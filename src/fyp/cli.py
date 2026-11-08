"""fyp: one-word entry point for the eye-tracking copy-task rig.

Subcommands wrap the long invocations:

    fyp calibrate          # Gazepoint on-device calibration
    fyp gaze               # Gazepoint gaze stream (research tracker)
    fyp webcam             # webcam head-pose/gaze stream
    fyp both               # webcam head pose + Gazepoint gaze concurrently
    fyp smoke              # both sensors, 8 s, headless
    fyp test               # offline test suite

Aliases: cal, g, w, b, s, t.

Children run on the current interpreter (``python -m ...``) from the repo
root, so concurrent processes never race on uv's package reinstall and
relative data paths resolve consistently.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CALIBRATION = _ROOT / "data" / "calibration.json"
_ALIASES = {
    "cal": "calibrate",
    "g": "gaze",
    "w": "webcam",
    "b": "both",
    "s": "smoke",
    "t": "test",
}


def _abs(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(path if path.is_absolute() else Path.cwd() / path)


def _run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=_ROOT)


def _calibrate_cmd(args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        "-m",
        "fyp.gazepoint.cli",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--area",
        args.area,
        "--text-width",
        str(args.text_width),
        "--calibrate",
    ]


def _gazepoint_cmd(args: argparse.Namespace, *, with_stimulus: bool) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "fyp.gazepoint.cli",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--rate",
        str(args.rate),
        "--text-width",
        str(args.text_width),
    ]
    stimulus = _abs(args.stimulus) if with_stimulus else None
    if stimulus:
        cmd += ["--stimulus", stimulus]
    if args.duration:
        cmd += ["--duration", str(args.duration)]
    if args.headless:
        cmd += ["--headless"]
    return cmd


def _webcam_cmd(
    args: argparse.Namespace, *, headless: bool, with_stimulus: bool
) -> list[str]:
    cmd = [sys.executable, "-m", "fyp.webcam.cli"]
    calibration = _abs(args.calibration)
    if calibration is None and not args.no_calibration and _DEFAULT_CALIBRATION.exists():
        calibration = str(_DEFAULT_CALIBRATION)
    if calibration:
        cmd += ["--calibration", calibration]
    stimulus = _abs(args.stimulus) if with_stimulus else None
    if stimulus:
        cmd += ["--stimulus", stimulus]
    if args.duration:
        cmd += ["--duration", str(args.duration)]
    if headless:
        cmd += ["--headless"]
    if args.smooth is not None:
        cmd += ["--smooth", str(args.smooth)]
    return cmd


def _run_both(args: argparse.Namespace) -> int:
    webcam = _webcam_cmd(args, headless=True, with_stimulus=False)
    gaze = _gazepoint_cmd(args, with_stimulus=not args.headless)
    print("+", " ".join(webcam), flush=True)
    print("+", " ".join(gaze), flush=True)
    procs = [subprocess.Popen(webcam, cwd=_ROOT), subprocess.Popen(gaze, cwd=_ROOT)]
    try:
        while True:
            codes = [proc.poll() for proc in procs]
            if all(code is not None for code in codes):
                return max(code for code in codes if code is not None)
            time.sleep(0.2)
    except KeyboardInterrupt:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        deadline = time.monotonic() + 10.0
        for proc in procs:
            try:
                proc.wait(timeout=max(deadline - time.monotonic(), 0.1))
            except subprocess.TimeoutExpired:
                proc.kill()
        return 130


def _smoke_args() -> argparse.Namespace:
    return argparse.Namespace(
        duration=8.0,
        stimulus=None,
        headless=True,
        calibration=None,
        no_calibration=False,
        smooth=None,
        host="127.0.0.1",
        port=4242,
        rate=150.0,
        text_width=0,
    )


def _add_webcam_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--duration", type=float, default=0.0, help="seconds; 0 = until Ctrl-C")
    parser.add_argument("--stimulus", type=Path, default=None, help="paragraph text file")
    parser.add_argument("--headless", action="store_true", help="no preview windows")
    parser.add_argument("--calibration", type=Path, default=None, help="webcam calibration JSON")
    parser.add_argument("--no-calibration", action="store_true", help="ignore data/calibration.json")
    parser.add_argument("--smooth", type=float, default=None, help="webcam gaze EMA alpha (0..1)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fyp",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="action", required=True)

    cal = sub.add_parser("calibrate", aliases=["cal"], help="Gazepoint on-device calibration")
    cal.add_argument("--host", default="127.0.0.1")
    cal.add_argument("--port", type=int, default=4242)
    cal.add_argument(
        "--area", choices=("text", "full"), default="text", help="calibration grid area"
    )
    cal.add_argument(
        "--text-width", type=int, default=0, help="text column width px (0 = 47 percent of screen)"
    )

    gaze = sub.add_parser("gaze", aliases=["g"], help="Gazepoint gaze stream (research tracker)")
    gaze.add_argument("--duration", type=float, default=0.0, help="seconds; 0 = until Ctrl-C")
    gaze.add_argument("--stimulus", type=Path, default=None, help="paragraph text file")
    gaze.add_argument("--headless", action="store_true", help="no preview window")
    gaze.add_argument("--host", default="127.0.0.1")
    gaze.add_argument("--port", type=int, default=4242)
    gaze.add_argument("--rate", type=float, default=150.0, help="LSL nominal rate (GP3 HD = 150)")
    gaze.add_argument(
        "--text-width", type=int, default=0, help="text column width px (0 = 47 percent of screen)"
    )

    cam = sub.add_parser("webcam", aliases=["w"], help="webcam head-pose/gaze stream")
    _add_webcam_options(cam)

    both = sub.add_parser(
        "both", aliases=["b"], help="webcam head pose + Gazepoint gaze concurrently"
    )
    _add_webcam_options(both)
    both.add_argument("--host", default="127.0.0.1")
    both.add_argument("--port", type=int, default=4242)
    both.add_argument("--rate", type=float, default=150.0)
    both.add_argument(
        "--text-width", type=int, default=0, help="text column width px (0 = 47 percent of screen)"
    )

    sub.add_parser("smoke", aliases=["s"], help="both sensors, 8 s, headless")
    sub.add_parser("test", aliases=["t"], help="run the offline test suite")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    action = _ALIASES.get(args.action, args.action)
    if action == "calibrate":
        return _run(_calibrate_cmd(args))
    if action == "gaze":
        return _run(_gazepoint_cmd(args, with_stimulus=True))
    if action == "webcam":
        return _run(_webcam_cmd(args, headless=args.headless, with_stimulus=True))
    if action == "both":
        return _run_both(args)
    if action == "smoke":
        return _run_both(_smoke_args())
    return _run([sys.executable, "-m", "pytest", "-q"])


if __name__ == "__main__":
    raise SystemExit(main())
