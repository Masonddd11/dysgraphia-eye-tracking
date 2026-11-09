"""fyp-gazepoint CLI: OpenGaze stream -> FYP_GazePoint LSL (research-grade).

Modes:
- default: live session streaming ``FYP_GazePoint``; optional stimulus overlay
  with word-level gaze highlight.
- --calibrate: run the GP3 HD's own 5/9-point calibration, report the summary.

Requires Gazepoint Control (OpenGaze server) on 127.0.0.1:4242 with the
tracker connected. Screen size is queried from the server so POG fractions
map to pixels (override with --screen-w/--screen-h).

LSL carries raw (device-native) best-eye POG: x_px, y_px, valid, pupil_diameter.
Samples are buffered and drained every loop iteration, so a slow renderer does
not drop the 150 Hz stream. LSL timestamps come from the device TIME field
(offset to the LSL clock), preserving the tracker's sample spacing.
``--smooth`` drives an adaptive One Euro filter for the on-screen preview dot
and word highlight; LSL is never smoothed. ``--word-dwell-ms`` debounces the
highlight so it cannot flicker between words at 150 Hz.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import pylsl

from fyp.gazepoint.client import (
    DEFAULT_TEXT_WIDTH_FRACTION,
    OpenGazeClient,
    OpenGazeError,
    text_area_points,
)
from fyp.gazepoint.lsl import GazePointOutlet
from fyp.smoothing import OneEuroPoint, WordDwell
from fyp.webcam.stimulus import layout_paragraph, render_paragraph, word_at

_CONNECT_HELP = (
    "ERROR: OpenGaze server not reachable on {host}:{port}. Gazepoint Control "
    "(the OpenGaze server) is Windows-only: run it on a Windows PC/VM with the "
    "GP3 HD USB-attached, confirm its API port is 4242, then pass --host <windows-ip>. "
    "Native macOS Gazepoint Control does not exist."
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="fyp-gazepoint", description=__doc__)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=4242)
    p.add_argument("--rate", type=float, default=150.0, help="LSL nominal rate (GP3 HD = 150 Hz)")
    p.add_argument("--screen-w", type=int, default=0, help="override screen width px (0 = query server)")
    p.add_argument("--screen-h", type=int, default=0, help="override screen height px (0 = query server)")
    p.add_argument("--duration", type=float, default=0.0, help="seconds; 0 = until Ctrl-C")
    p.add_argument("--calibrate", action="store_true", help="run device calibration and exit")
    p.add_argument(
        "--area",
        choices=("text", "full"),
        default="text",
        help="calibration grid: centred text column (default) or full screen",
    )
    p.add_argument(
        "--text-width",
        type=int,
        default=0,
        help="stimulus column width px (0 = 47 percent of screen); matched by --area text",
    )
    p.add_argument("--stimulus", type=Path, default=None, help="text file with the paragraph to display")
    p.add_argument(
        "--smooth",
        type=float,
        default=0.4,
        help="preview smoothing 0..1 (lower = smoother); LSL stays raw",
    )
    p.add_argument(
        "--word-dwell-ms",
        type=float,
        default=120.0,
        help="word highlight must be stable this long before it changes",
    )
    p.add_argument("--headless", action="store_true", help="no preview window, stats to stdout")
    return p.parse_args()


def _connect(args: argparse.Namespace) -> tuple[OpenGazeClient | None, int]:
    client = OpenGazeClient(args.host, args.port)
    try:
        client.connect()
    except OpenGazeError as exc:
        print(_CONNECT_HELP.format(host=args.host, port=args.port))
        print(str(exc))
        return None, 2
    return client, 0


def _resolve_screen(client: OpenGazeClient, args: argparse.Namespace) -> tuple[float, float] | None:
    if args.screen_w and args.screen_h:
        return float(args.screen_w), float(args.screen_h)
    ss = client.query_screen_size()
    if ss is None:
        return None
    return float(ss[0]), float(ss[1])


def run_calibration(args: argparse.Namespace) -> int:
    client, rc = _connect(args)
    if client is None:
        return rc
    try:
        pid = client.product_id()
        print(f"tracker: {pid or 'unknown'}")
        points = None
        if args.area == "text":
            resolved = _resolve_screen(client, args)
            if resolved is None:
                print("ERROR: no screen size; pass --screen-w/--screen-h.")
                return 2
            points = text_area_points(resolved[0], args.text_width)
            print(f"calibration area: centred text column, {len(points)} points")
        print("calibration: fixate each on-screen point; sit at the normal reading distance.")
        ave_error, valid_points = client.calibrate(points=points)
        print(
            f"calibration done: {valid_points} valid points, "
            f"average error {ave_error} (device-reported)"
        )
        if valid_points == 0:
            print("WARNING: no valid calibration points - recalibrate.")
            return 2
        return 0
    except OpenGazeError as exc:
        print(f"ERROR: {exc}")
        return 2
    finally:
        client.close()


def run_session(args: argparse.Namespace) -> int:
    client, rc = _connect(args)
    if client is None:
        return rc
    try:
        pid = client.product_id()
        resolved = _resolve_screen(client, args)
        if resolved is None or resolved[0] <= 0 or resolved[1] <= 0:
            print("ERROR: no screen size; pass --screen-w/--screen-h.")
            return 2
        sw, sh = resolved
        client.set_screen(sw, sh)
        for cmd in (
            "ENABLE_SEND_TIME",
            "ENABLE_SEND_POG_BEST",
            "ENABLE_SEND_PUPIL_LEFT",
            "ENABLE_SEND_PUPIL_RIGHT",
        ):
            client.enable(cmd, True)
        client.enable("ENABLE_SEND_DATA", True)
    except OpenGazeError as exc:
        print(f"ERROR: {exc}")
        client.close()
        return 2

    print(
        f"tracker: {pid or 'unknown'} | screen: {sw:.0f}x{sh:.0f} px | "
        f"stream FYP_GazePoint @ {args.rate:.0f} Hz nominal"
    )

    outlet = GazePointOutlet(args.rate)
    layout = None
    word_tol = 0.0
    font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.0, 2
    if args.stimulus is not None:
        font_scale = 0.9 * sh / 900.0
        column = args.text_width if args.text_width > 0 else int(sw * DEFAULT_TEXT_WIDTH_FRACTION)
        column = max(200, min(int(sw), column))
        margin_x = (int(sw) - column) // 2
        layout = layout_paragraph(
            args.stimulus.read_text(),
            font,
            font_scale,
            thickness,
            int(sw),
            margin_x,
            top_px=0,
        )
        if layout.boxes:
            block_top = min(b.y for b in layout.boxes)
            block_bottom = max(b.y + b.h for b in layout.boxes)
            offset = int((sh - (block_bottom - block_top)) / 2 - block_top)
            for box in layout.boxes:
                box.y += offset
        word_tol = layout.line_height * 0.75
        n_lines = 1 + (layout.boxes[-1].line if layout.boxes else 0)
        print(
            f"stimulus: {len(layout.boxes)} words / {n_lines} lines from {args.stimulus} "
            f"(column {column:.0f}px)"
        )
        if not args.headless:
            cv2.namedWindow("stimulus", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("stimulus", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    samples = valid_samples = 0
    smooth = min(max(args.smooth, 0.0), 1.0)
    smoother = OneEuroPoint(min_cutoff=0.3 + 2.7 * smooth)
    dwell = WordDwell(max(args.word_dwell_ms, 0.0) / 1000.0)
    smoothed: np.ndarray | None = None
    current_word = -1
    time_offset: float | None = None
    last_draw = 0.0
    t0 = time.perf_counter()
    last_line = 0.0
    t_end = t0

    print("streaming (Ctrl-C to stop)...")
    try:
        while True:
            ts = time.perf_counter()
            drained = client.drain_samples()
            for gp in drained:
                samples += 1
                if time_offset is None and gp.time_s is not None:
                    time_offset = pylsl.local_clock() - gp.time_s
                stamp = (
                    time_offset + gp.time_s
                    if time_offset is not None and gp.time_s is not None
                    else None
                )
                if gp.valid:
                    valid_samples += 1
                    outlet.push(gp.x_px, gp.y_px, True, gp.pupil_diameter_px, timestamp=stamp)
                    sample_t = gp.time_s if gp.time_s is not None else ts
                    nx, ny = smoother(gp.x_px / sw, gp.y_px / sh, sample_t)
                    smoothed = np.array([nx * sw, ny * sh])
                    if layout is not None:
                        widx = word_at(smoothed, layout.boxes, word_tol)
                        widx = dwell.update(widx, sample_t)
                        if widx != current_word and widx >= 0:
                            print(f"word {widx} '{layout.boxes[widx].text}' t={ts - t0:6.2f}s")
                        current_word = widx
                else:
                    outlet.push(-1.0, -1.0, False, gp.pupil_diameter_px, timestamp=stamp)
                    smoother.reset()
                    dwell.reset()
                    smoothed = None
                    current_word = -1

            if not args.headless and layout is not None and ts - last_draw >= 0.033:
                canvas = render_paragraph(
                    (int(sw), int(sh)), layout, font, font_scale, thickness, highlight=current_word
                )
                if smoothed is not None:
                    gx, gy = int(smoothed[0]), int(smoothed[1])
                    cv2.circle(canvas, (gx, gy), 12, (0, 0, 255), 2)
                    cv2.circle(canvas, (gx, gy), 2, (0, 0, 255), -1)
                cv2.imshow("stimulus", canvas)
                last_draw = ts
                if (cv2.waitKey(1) & 0xFF) == 27:
                    break
            elif ts - last_line >= 1.0:
                last_line = ts
                print(
                    f"t={ts - t0:5.1f}s samples={samples} ({samples / max(ts - t0, 1e-9):.0f} Hz)"
                    f" valid={100 * valid_samples / max(samples, 1):.0f}%"
                    + (f" word={current_word}" if layout is not None else "")
                )

            if args.duration > 0 and (ts - t0) >= args.duration:
                break
            if not drained:
                time.sleep(0.001)
    except KeyboardInterrupt:
        print("interrupted.")
    finally:
        t_end = time.perf_counter()
        client.close()
        if not args.headless:
            cv2.destroyAllWindows()

    elapsed = max(t_end - t0, 1e-9)
    print("=== gazepoint module summary ===")
    print(f"duration={elapsed:.1f}s samples={samples} ({samples / elapsed:.1f} Hz)")
    print(f"valid gaze: {100 * valid_samples / max(samples, 1):.1f}%")
    return 0


def main() -> int:
    args = parse_args()
    if args.calibrate:
        return run_calibration(args)
    return run_session(args)


if __name__ == "__main__":
    raise SystemExit(main())
