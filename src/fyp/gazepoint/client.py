"""OpenGaze TCP client: connect, stream records, drive on-device calibration.

Hardware I/O (socket + reader thread); the pure wire format lives in
``protocol.py``. Gazepoint Control (the OpenGaze server, port 4242) must be
running with the tracker connected. Screen size is queried from the server so
POG fractions map to pixels; override locally with ``set_screen``.
"""

from __future__ import annotations

import socket
import threading
import time
from collections import deque
from collections.abc import Sequence

from fyp.gazepoint.protocol import (
    ACK,
    REC,
    GazePoint,
    Record,
    calibration_summary,
    format_command,
    parse_gaze,
    parse_record,
    screen_size,
)

_ACK_TIMEOUT_S = 5.0
_SAMPLE_BUFFER = 6000  # ~40 s at 150 Hz

DEFAULT_TEXT_WIDTH_FRACTION = 0.47  # centred stimulus column vs screen width
_CALIBRATION_ROWS = (0.30, 0.50, 0.70)
_CALIBRATION_INSET = 0.10


class OpenGazeError(RuntimeError):
    """Raised on connection/acknowledgement failures."""


def text_area_points(
    screen_w: float, text_width_px: float | None = None
) -> list[tuple[float, float]]:
    """3x3 calibration grid confined to the centred text column (screen fractions).

    Gazepoint's stock grid spans x=0.1..0.9, which on an ultrawide places the
    outer points ~30 deg off-axis where the tracker is least accurate.
    Calibrating only the column the stimulus uses keeps the fit where the words
    are; gaze outside that column will be less accurate by design.
    """
    width = float(text_width_px) if text_width_px else float(screen_w) * DEFAULT_TEXT_WIDTH_FRACTION
    width = min(max(width, 200.0), float(screen_w))
    column = width / float(screen_w)
    xs = (
        0.5 - column / 2 + _CALIBRATION_INSET * column,
        0.5,
        0.5 + column / 2 - _CALIBRATION_INSET * column,
    )
    ys = _CALIBRATION_ROWS
    # Gazepoint's default order is centre first, then clockwise from top-right;
    # match it so the UI and the fitted samples stay index-aligned.
    order = ((1, 1), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1), (0, 0), (1, 0))
    return [(min(max(xs[c], 0.05), 0.95), ys[r]) for c, r in order]


class OpenGazeClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 4242) -> None:
        self._host = host
        self._port = port
        self._sock: socket.socket | None = None
        self._cond = threading.Condition()
        self._records: dict[tuple[str, str | None], Record] = {}
        self._send_lock = threading.Lock()
        self._reader: threading.Thread | None = None
        self._closed = threading.Event()
        self._screen_wh: tuple[float, float] | None = None
        self._pending: deque[Record] = deque(maxlen=_SAMPLE_BUFFER)
        self.malformed = 0

    # -- lifecycle -----------------------------------------------------
    def connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        try:
            sock.connect((self._host, self._port))
        except OSError as exc:
            sock.close()
            raise OpenGazeError(
                f"cannot reach OpenGaze server at {self._host}:{self._port}"
            ) from exc
        sock.settimeout(1.0)
        self._sock = sock
        self._closed.clear()
        self._reader = threading.Thread(
            target=self._read_loop, name="gazepoint-reader", daemon=True
        )
        self._reader.start()

    def close(self) -> None:
        self._closed.set()
        if self._sock is not None:
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._sock.close()
            self._sock = None
        if self._reader is not None:
            self._reader.join(timeout=2.0)
            self._reader = None

    # -- reader --------------------------------------------------------
    def _read_loop(self) -> None:
        assert self._sock is not None
        buf = b""
        while not self._closed.is_set():
            try:
                chunk = self._sock.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            while b"\r\n" in buf:
                raw, buf = buf.split(b"\r\n", 1)
                if not raw.strip():
                    continue
                try:
                    rec = parse_record(raw.decode("utf-8", "replace"))
                except Exception:
                    self.malformed += 1
                    continue
                with self._cond:
                    self._records[(rec.tag, rec.cmd_id)] = rec
                    if rec.tag == REC:
                        self._pending.append(rec)
                    self._cond.notify_all()

    # -- request / response -------------------------------------------
    def _send(self, action: str, cmd_id: str, **params) -> Record:
        if self._sock is None:
            raise OpenGazeError("not connected")
        key = (ACK, cmd_id.upper())
        with self._cond:
            self._records.pop(key, None)  # discard stale ACK of a prior same-ID command
        msg = format_command(action, cmd_id, **params)
        with self._send_lock:
            self._sock.sendall(msg.encode("utf-8"))
        deadline = time.monotonic() + _ACK_TIMEOUT_S
        with self._cond:
            while time.monotonic() < deadline:
                if key in self._records:
                    return self._records[key]
                self._cond.wait(timeout=0.05)
        raise OpenGazeError(f"no ACK for {cmd_id} within {_ACK_TIMEOUT_S:.0f}s")

    def get(self, cmd_id: str) -> Record:
        return self._send("GET", cmd_id)

    def set(self, cmd_id: str, **params) -> Record:
        return self._send("SET", cmd_id, **params)

    def enable(self, cmd_id: str, state: bool = True) -> None:
        self.set(cmd_id, STATE="1" if state else "0")

    # -- device queries ------------------------------------------------
    def product_id(self) -> str | None:
        rec = self.get("PRODUCT_ID")
        return rec.attrs.get("VALUE")

    def query_screen_size(self) -> tuple[int, int] | None:
        return screen_size(self.get("SCREEN_SIZE"))

    def set_screen(self, width_px: float, height_px: float) -> None:
        self._screen_wh = (float(width_px), float(height_px))

    # -- data ----------------------------------------------------------
    def drain_samples(self) -> list[GazePoint]:
        """All REC samples received since the last drain, converted to pixels.

        Buffered in a bounded deque so a slow renderer (e.g. the stimulus
        overlay) cannot drop the 150 Hz LSL stream.
        """
        with self._cond:
            recs = list(self._pending)
            self._pending.clear()
            screen = self._screen_wh
        if screen is None:
            return []
        points = (parse_gaze(rec, *screen) for rec in recs)
        return [gp for gp in points if gp is not None]

    # -- calibration ---------------------------------------------------
    def calibrate(
        self,
        timeout_s: float = 60.0,
        points: Sequence[tuple[float, float]] | None = None,
        point_timeout_s: float = 2.5,
        point_delay_s: float = 1.0,
    ) -> tuple[float, int]:
        """Run the tracker's own calibration; returns (ave_error, valid_points).

        ``points`` are ``(x, y)`` screen fractions for a custom grid (None uses
        the device defaults). ``point_timeout_s`` is how long each point is
        sampled and ``point_delay_s`` the animation lead-in; the defaults are
        longer than Gazepoint's 1.5/0.5 to collect more samples per point.

        Keeps the calibration window open while polling
        CALIBRATE_RESULT_SUMMARY. The server emits an empty ``CALIB_RESULT``
        about a second after start (plus one ``CALIB_RESULT_PT`` per point),
        so that record is *not* a completion signal; the summary only becomes
        non-zero once the device accepts at least one point.
        """
        self.set("CALIBRATE_TIMEOUT", VALUE=f"{point_timeout_s:g}")
        self.set("CALIBRATE_DELAY", VALUE=f"{point_delay_s:g}")
        if points:
            self.set("CALIBRATE_CLEAR")
            for x, y in points:
                self.set("CALIBRATE_ADDPOINT", X=f"{x:.5f}", Y=f"{y:.5f}")
            accepted = int(float(self.get("CALIBRATE_ADDPOINT").attrs.get("PTS", "0")))
            if accepted != len(points):
                raise OpenGazeError(
                    f"device accepted {accepted}/{len(points)} calibration points"
                )
        else:
            self.set("CALIBRATE_RESET")
            self.set("CALIBRATE_CLEAR")
        time.sleep(0.5)  # let the clear land before the first summary read
        self.set("CALIBRATE_SHOW", STATE="1")
        time.sleep(1.5)  # let the fullscreen calibration window appear
        self.set("CALIBRATE_START", STATE="1")

        deadline = time.monotonic() + timeout_s
        summary: tuple[float, int] | None = None
        last: tuple[float, int] | None = None
        stable = 0
        try:
            while time.monotonic() < deadline:
                try:
                    rec = self.get("CALIBRATE_RESULT_SUMMARY")
                except OpenGazeError:
                    rec = None
                current = calibration_summary(rec) if rec is not None else None
                if current is not None and current[1] > 0:
                    stable = stable + 1 if current == last else 0
                    last = current
                    if stable >= 2:  # unchanged over ~1 s -> device finished
                        summary = current
                        break
                time.sleep(0.5)
        finally:
            self.set("CALIBRATE_SHOW", STATE="0")

        if summary is None:
            summary = calibration_summary(self.get("CALIBRATE_RESULT_SUMMARY"))
        if summary is None:
            raise OpenGazeError("CALIBRATE_RESULT_SUMMARY missing AVE_ERROR/VALID_POINTS")
        return summary
