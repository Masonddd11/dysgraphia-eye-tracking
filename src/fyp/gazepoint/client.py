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

from fyp.gazepoint.protocol import (
    ACK,
    CAL,
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


class OpenGazeError(RuntimeError):
    """Raised on connection/acknowledgement failures."""


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

    def _wait_for(self, tag: str, cmd_id: str, timeout_s: float) -> Record | None:
        key = (tag, cmd_id.upper())
        deadline = time.monotonic() + timeout_s
        with self._cond:
            while time.monotonic() < deadline:
                if key in self._records:
                    return self._records[key]
                self._cond.wait(timeout=0.1)
        return None

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
    def calibrate(self, timeout_s: float = 60.0) -> tuple[float, int]:
        """Run the tracker's own calibration; returns (ave_error, valid_points).

        Drives CALIBRATE_CLEAR -> CALIBRATE_SHOW -> CALIBRATE_START, waits for
        the CALIB_RESULT record, hides the window, then reads the summary.
        """
        self.set("CALIBRATE_CLEAR")
        with self._cond:
            self._records.pop((CAL, "CALIB_RESULT"), None)
        self.set("CALIBRATE_SHOW", STATE="1")
        self.set("CALIBRATE_START", STATE="1")
        if self._wait_for(CAL, "CALIB_RESULT", timeout_s) is None:
            self.set("CALIBRATE_SHOW", STATE="0")
            raise OpenGazeError("calibration did not finish before timeout")
        self.set("CALIBRATE_SHOW", STATE="0")
        summary = calibration_summary(self.get("CALIBRATE_RESULT_SUMMARY"))
        if summary is None:
            raise OpenGazeError("CALIBRATE_RESULT_SUMMARY missing AVE_ERROR/VALID_POINTS")
        return summary
