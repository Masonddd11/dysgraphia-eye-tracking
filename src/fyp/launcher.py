"""Local, click-to-run control panel for the FYP copy-task rig.

The macOS ``FYP Launcher.app`` wrapper starts this small localhost server and
opens the browser.  It only listens on 127.0.0.1 and only exposes the four
session actions plus stop/shutdown, so it is a control surface rather than a
network service.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from fyp.launcher_commands import build_command

ROOT = Path(os.environ.get("FYP_ROOT", Path(__file__).resolve().parents[2])).resolve()
DATA = ROOT / "data"
CALIBRATION = DATA / "calibration.json"
ASSET = Path(__file__).resolve().parent / "launcher_assets" / "index.html"

LABELS = {
    "webcam_calibrate": "Webcam calibration",
    "webcam_read": "Webcam reading task",
    "gazepoint_calibrate": "Gazepoint calibration",
    "gazepoint_read": "Gazepoint reading task",
}


class Runner:
    """Run one calibration/session subprocess and collect its output."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._proc: subprocess.Popen[str] | None = None
        self._action = ""
        self._lines: deque[str] = deque(maxlen=240)
        self._returncode: int | None = None

    def _append(self, text: str) -> None:
        with self._lock:
            self._lines.append(text)

    def start(self, action: str, command: list[str]) -> None:
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                raise RuntimeError("a calibration or reading session is already running")
            self._action = action
            self._returncode = None
            self._lines.clear()
            self._lines.append("$ " + " ".join(command))

        kwargs: dict[str, object] = {
            "cwd": ROOT,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "bufsize": 1,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(
                subprocess, "CREATE_NEW_PROCESS_GROUP", 0
            )
        else:
            kwargs["start_new_session"] = True

        proc = subprocess.Popen(command, **kwargs)
        with self._lock:
            self._proc = proc
        threading.Thread(target=self._read, args=(proc,), daemon=True).start()

    def _read(self, proc: subprocess.Popen[str]) -> None:
        stream = proc.stdout
        if stream is not None:
            for line in stream:
                self._append(line.rstrip())
        code = proc.wait()
        with self._lock:
            self._returncode = code
            self._lines.append(f"[process exited with code {code}]")

    def stop(self) -> bool:
        with self._lock:
            proc = self._proc
        if proc is None or proc.poll() is not None:
            return False
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            proc.terminate()
        return True

    def status(self) -> dict[str, object]:
        with self._lock:
            proc = self._proc
            running = proc is not None and proc.poll() is None
            return {
                "app": "fyp-launcher",
                "running": running,
                "action": self._action,
                "label": LABELS.get(self._action, ""),
                "returncode": self._returncode,
                "log": list(self._lines),
                "calibration_exists": CALIBRATION.is_file(),
                "calibration_path": str(CALIBRATION),
            }


class LauncherServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], runner: Runner) -> None:
        super().__init__(address, LauncherHandler)
        self.runner = runner


class LauncherHandler(BaseHTTPRequestHandler):
    server_version = "FYPCopyTask/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        # A desktop launcher should not fill the system log with every poll.
        pass

    def _send(self, body: bytes, *, status: int = 200, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: object, status: int = 200) -> None:
        self._send(
            json.dumps(payload).encode("utf-8"),
            status=status,
            content_type="application/json; charset=utf-8",
        )

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            try:
                body = ASSET.read_bytes()
            except OSError as exc:
                self._send(
                    f"launcher asset missing: {ASSET}\n{exc}".encode("utf-8"),
                    status=500,
                    content_type="text/plain; charset=utf-8",
                )
                return
            self._send(body, content_type="text/html; charset=utf-8")
            return
        if path == "/api/config":
            files = (
                [p.name for p in sorted(DATA.glob("*.txt"))]
                if DATA.is_dir()
                else []
            )
            default = "sample_paragraph.txt" if "sample_paragraph.txt" in files else (
                files[0] if files else ""
            )
            self._json(
                {
                    "app": "fyp-launcher",
                    "root": str(ROOT),
                    "stimulus_files": files,
                    "default_stimulus": default,
                    "calibration_exists": CALIBRATION.is_file(),
                    "calibration_path": str(CALIBRATION),
                    "defaults": {
                        "font_scale": 0.0,
                        "line_spacing": 2.2,
                        "word_margin": 0.0,
                        "host": "127.0.0.1",
                    },
                }
            )
            return
        if path == "/api/status":
            self._json(self.server.runner.status())  # type: ignore[attr-defined]
            return
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self._json({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": f"invalid JSON: {exc}"}, status=400)
            return

        runner: Runner = self.server.runner  # type: ignore[attr-defined]

        if path == "/api/start":
            self._start(payload, runner)
            return
        if path == "/api/stop":
            stopped = runner.stop()
            self._json({"ok": True, "stopped": stopped})
            return
        if path == "/api/shutdown":
            runner.stop()
            self._json({"ok": True, "shutdown": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        self._json({"error": "not found"}, status=404)

    def _start(self, payload: dict[str, object], runner: Runner) -> None:
        action = str(payload.get("action", ""))
        if action not in LABELS:
            self._json({"error": f"unknown action: {action}"}, status=400)
            return

        stimulus_raw = str(payload.get("stimulus", "sample_paragraph.txt"))
        stimulus = Path(stimulus_raw)
        if not stimulus.is_absolute():
            # Accept both "sample_paragraph.txt" and "data/sample_paragraph.txt".
            candidate = (DATA / stimulus).resolve()
            if not candidate.exists():
                candidate = (ROOT / stimulus).resolve()
            stimulus = candidate
        else:
            stimulus = stimulus.resolve()
        if action.endswith("_read"):
            try:
                stimulus.relative_to(ROOT)
            except ValueError:
                self._json(
                    {"error": "stimulus must live inside the project folder"}, status=400
                )
                return
            if not stimulus.is_file() or stimulus.suffix.lower() not in (".txt", ".md"):
                self._json(
                    {"error": f"stimulus file not found: {stimulus}"}, status=400
                )
                return

        def number(name: str, default: float, low: float, high: float) -> float:
            try:
                value = float(payload.get(name, default))
            except (TypeError, ValueError):
                value = default
            return max(low, min(high, value))

        font_scale = number("font_scale", 0.0, 0.0, 4.0)
        line_spacing = number("line_spacing", 2.2, 1.0, 4.0)
        word_margin = number("word_margin", 0.0, 0.0, 200.0)
        host = str(payload.get("host", "127.0.0.1")).strip() or "127.0.0.1"

        try:
            command = build_command(
                action,
                stimulus=stimulus,
                font_scale=font_scale,
                line_spacing=line_spacing,
                word_margin=word_margin,
                host=host,
                calibration=CALIBRATION,
            )
            runner.start(action, command)
        except (OSError, RuntimeError, ValueError) as exc:
            self._json({"error": str(exc)}, status=409)
            return
        self._json({"ok": True, "action": action, "command": command})


def _existing_launcher(port: int) -> bool:
    import urllib.request

    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/status", timeout=0.4
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("app") == "fyp-launcher"
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fyp-launcher", description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    for port in range(args.port, args.port + 12):
        if _existing_launcher(port):
            url = f"http://127.0.0.1:{port}/"
            if not args.no_browser:
                webbrowser.open(url)
            print(f"Launcher already running at {url}")
            return 0

    runner = Runner()
    server: LauncherServer | None = None
    for port in range(args.port, args.port + 12):
        try:
            server = LauncherServer(("127.0.0.1", port), runner)
            break
        except OSError:
            continue
    if server is None:
        print("ERROR: could not find a free local port for the launcher.")
        return 2

    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"FYP launcher: {url}")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
