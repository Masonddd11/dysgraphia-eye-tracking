"""fyp-webcam CLI: capture -> FaceMesh -> gaze/head-pose/switch events -> LSL.

Modes:
- default: live session. Preview windows unless --headless; ESC or --duration ends.
- --calibrate: interactive 9-point screen-gaze calibration, saved to --out.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np

from fyp.webcam.gaze import Calibration, fit_calibration, gaze_error_px, map_gaze
from fyp.webcam.landmarks import FaceTracker
from fyp.webcam.lsl import WebcamOutlets
from fyp.webcam.stimulus import layout_paragraph, render_paragraph, word_at
from fyp.webcam.switching import MONITOR, SwitchConfig, SwitchDetector

_CAMERA_HELP = (
    "ERROR: camera did not open. On macOS grant Camera permission to the app "
    "running this command (System Settings -> Privacy & Security -> Camera, "
    "e.g. Terminal/iTerm), then rerun."
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="fyp-webcam", description=__doc__)
    p.add_argument("--index", type=int, default=0, help="camera index (default 0)")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--duration", type=float, default=0.0, help="seconds; 0 = until ESC/Ctrl-C")
    p.add_argument("--headless", action="store_true", help="no preview windows, stats to stdout")
    p.add_argument("--calibration", type=Path, default=None, help="calibration JSON to load")
    p.add_argument("--stimulus", type=Path, default=None, help="text file with the paragraph to display")
    p.add_argument("--smooth", type=float, default=0.35, help="gaze EMA alpha (0..1, higher=faster)")
    p.add_argument("--calibrate", action="store_true", help="run 9-point calibration and exit")
    p.add_argument(
        "--validate",
        action="store_true",
        help="measure held-out gaze accuracy on 5 points (needs --calibration)",
    )
    p.add_argument(
        "--calibration-seconds",
        type=float,
        default=4.5,
        help="seconds per calibration point (0.7s settle, rest collects samples)",
    )
    p.add_argument("--out", type=Path, default=Path("data/calibration.json"))
    p.add_argument("--screen-w", type=int, default=1440)
    p.add_argument("--screen-h", type=int, default=900)
    p.add_argument("--enter-deg", type=float, default=18.0)
    p.add_argument("--exit-deg", type=float, default=12.0)
    p.add_argument("--dwell-ms", type=float, default=200.0)
    return p.parse_args()


def open_camera(args: argparse.Namespace) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(args.index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    return cap


def run_session(args: argparse.Namespace) -> int:
    cap = open_camera(args)
    if not cap.isOpened():
        print(_CAMERA_HELP)
        return 2
    tracker, outlets = FaceTracker(), WebcamOutlets()
    detector = SwitchDetector(SwitchConfig(args.enter_deg, args.exit_deg, args.dwell_ms))
    cal: Calibration | None = None
    if args.calibration:
        cal = Calibration.from_json(args.calibration.read_text())
        print(f"loaded calibration screen={cal.screen} from {args.calibration}")

    screen = cal.screen if cal is not None else (float(args.screen_w), float(args.screen_h))
    layout, word_tol = None, 0.0
    font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.0, 2
    if args.stimulus is not None:
        font_scale = 0.9 * screen[1] / 900.0
        layout = layout_paragraph(
            args.stimulus.read_text(),
            font,
            font_scale,
            thickness,
            int(screen[0]),
            int(screen[0] * 0.08),
        )
        word_tol = layout.line_height * 0.75
        n_lines = 1 + (layout.boxes[-1].line if layout.boxes else 0)
        print(f"stimulus: {len(layout.boxes)} words / {n_lines} lines from {args.stimulus}")
        if not args.headless:
            cv2.namedWindow("stimulus", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("stimulus", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    frames = face_frames = blink_frames = 0
    pitches: list[float] = []
    lags: list[float] = []
    seen_events, read_fails = 0, 0
    gaze_ema: np.ndarray | None = None
    last_valid_ts, current_word = 0.0, -1
    t0, last_line = time.perf_counter(), 0.0

    print("streaming (Ctrl-C or ESC to stop)...")
    try:
        while True:
            ok, frame = cap.read()
            ts = time.perf_counter()
            if not ok:
                read_fails += 1
                if read_fails > 30:
                    print("ERROR: camera stopped delivering frames.")
                    break
                continue
            read_fails = 0
            frame = cv2.flip(frame, 1)
            r = tracker.process(frame, ts)
            frames += 1

            if r.ok:
                face_frames += 1
                blink_frames += int(r.blink)
                pitches.append(r.pitch_down_deg)
                outlets.push_head(r.pitch_down_deg, r.yaw_deg, r.roll_deg)
                if cal is not None and not r.blink:
                    raw = map_gaze(cal.coeffs, r.features, cal.screen)
                    if gaze_ema is None or ts - last_valid_ts > 0.5:
                        gaze_ema = raw.copy()
                    else:
                        gaze_ema = args.smooth * raw + (1.0 - args.smooth) * gaze_ema
                    last_valid_ts = ts
                    outlets.push_gaze(float(gaze_ema[0]), float(gaze_ema[1]), 1.0, 0.0)
                    if layout is not None:
                        widx = word_at(gaze_ema, layout.boxes, word_tol)
                        outlets.push_word(widx)
                        if widx != current_word and widx >= 0:
                            print(f"word {widx} '{layout.boxes[widx].text}' t={ts - t0:6.2f}s")
                        current_word = widx
                else:
                    outlets.push_gaze(-1.0, -1.0, 0.0, float(r.blink))
                    if layout is not None:
                        outlets.push_word(-1)
                detector.update(r.pitch_down_deg, (ts - t0) * 1000.0)
                for t_ms, state in detector.events[seen_events:]:
                    outlets.push_event(state)
                    name = "MONITOR" if state == MONITOR else "PAPER"
                    print(f"switch t={t_ms / 1000.0:6.2f}s -> {name}")
                seen_events = len(detector.events)
            else:
                outlets.push_gaze(-1.0, -1.0, 0.0, 0.0)
                if layout is not None:
                    outlets.push_word(-1)

            lags.append((time.perf_counter() - ts) * 1000.0)

            if not args.headless:
                state_name = "MONITOR" if detector.state == MONITOR else "PAPER"
                rx, ry, lx, ly = r.iris_px
                for cx, cy in ((rx, ry), (lx, ly)):
                    if r.ok:
                        cv2.circle(frame, (int(cx), int(cy)), 4, (0, 255, 0), -1)
                hud = [
                    f"face={'ok' if r.ok else 'LOST'} EAR={r.ear:.2f}"
                    f"{' BLINK' if r.blink else ''}",
                    f"pitch(down+)={r.pitch_down_deg:+6.1f} yaw={r.yaw_deg:+6.1f}"
                    f" roll={r.roll_deg:+6.1f}",
                    f"state={state_name}  hz={frames / max(ts - t0, 1e-9):.1f}  ESC quit",
                ]
                for i, line in enumerate(hud):
                    cv2.putText(frame, line, (10, 24 + 22 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
                if layout is not None:
                    canvas = render_paragraph(
                        (int(screen[0]), int(screen[1])), layout, font, font_scale, thickness,
                        highlight=current_word,
                    )
                    if gaze_ema is not None:
                        gx, gy = int(gaze_ema[0]), int(gaze_ema[1])
                        cv2.circle(canvas, (gx, gy), 12, (0, 0, 255), 2)
                        cv2.circle(canvas, (gx, gy), 2, (0, 0, 255), -1)
                    cv2.imshow("stimulus", canvas)
                elif cal is not None and r.ok and not r.blink:
                    g = map_gaze(cal.coeffs, r.features, cal.screen)
                    scale = 480.0 / cal.screen[0]
                    gx, gy = int(g[0] * scale), int(g[1] * scale)
                    canvas = np.zeros((int(cal.screen[1] * scale), 480, 3), dtype=np.uint8)
                    cv2.circle(canvas, (gx, gy), 8, (0, 255, 0), -1)
                    cv2.imshow("gaze (screen space)", canvas)
                cv2.imshow("fyp-webcam", frame)
                if (cv2.waitKey(1) & 0xFF) == 27:
                    break
            elif ts - last_line >= 1.0:
                last_line = ts
                pseg = pitches[-45:] or [0.0]
                print(
                    f"t={ts - t0:5.1f}s frames={frames} face={100 * face_frames / frames:.0f}%"
                    f" pitch[avg {np.mean(pseg):+.1f} min {np.min(pseg):+.1f} max {np.max(pseg):+.1f}]"
                    f" state={'MONITOR' if detector.state == MONITOR else 'PAPER'}"
                    + (f" word={current_word}" if layout is not None else "")
                    + f" lag={np.mean(lags[-45:]):.1f}ms"
                )

            if args.duration > 0 and (ts - t0) >= args.duration:
                break
    except KeyboardInterrupt:
        print("interrupted.")
    finally:
        tracker.close()
        cap.release()
        if not args.headless:
            cv2.destroyAllWindows()

    elapsed = max(time.perf_counter() - t0, 1e-9)
    print("=== webcam module summary ===")
    print(
        f"duration={elapsed:.1f}s frames={frames} ({frames / elapsed:.1f} Hz)"
        f" face={100 * face_frames / max(frames, 1):.0f}% blinks={blink_frames}"
    )
    if pitches:
        print(
            f"pitch_down_deg: mean {np.mean(pitches):+.1f} min {np.min(pitches):+.1f}"
            f" max {np.max(pitches):+.1f}"
        )
    print(f"switch events: {len(detector.events)}")
    for t_ms, state in detector.events:
        print(f"  t={t_ms / 1000.0:6.2f}s -> {'MONITOR' if state == MONITOR else 'PAPER'}")
    print(f"mean pipeline lag: {np.mean(lags):.1f} ms (capture->after-LSL-push)")
    if frames and face_frames == 0:
        print("WARNING: no face detected in any frame (lighting, no subject, or camera permission).")
    return 0


def camera_inset_rect(screen_wh: tuple[int, int]) -> tuple[int, int, int, int]:
    """Camera-inset rect on the calibration canvas, placed in the bottom-row
    gap between the left and centre dots (the widest dot-free rectangle)."""
    w, h = screen_wh
    inset_w = min(320, int(0.4 * w) - 80)
    inset_w = max(inset_w, 1)
    inset_h = inset_w * 9 // 16
    gap_mid = int(0.3 * w)
    x = max(0, gap_mid - inset_w // 2)
    y = max(0, h - inset_h - 10)
    return x, y, inset_w, inset_h


def run_calibration(args: argparse.Namespace) -> int:
    cap = open_camera(args)
    if not cap.isOpened():
        print(_CAMERA_HELP)
        return 2
    tracker = FaceTracker()
    screen = (float(args.screen_w), float(args.screen_h))
    fracs = (0.1, 0.5, 0.9)
    targets = [(fx * screen[0], fy * screen[1]) for fy in fracs for fx in fracs]
    samples: list[tuple[np.ndarray, np.ndarray]] = []
    print("9-point calibration: look at each dot. Do not move your head, only your eyes.")
    cv2.namedWindow("calibration", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    try:
        for idx, (tx, ty) in enumerate(targets):
            collected: list[np.ndarray] = []
            t_start = time.perf_counter()
            while (dwell := time.perf_counter() - t_start) < args.calibration_seconds:
                ok, frame = cap.read()
                if not ok:
                    continue
                frame = cv2.flip(frame, 1)
                r = tracker.process(frame, time.perf_counter())
                canvas = np.zeros((int(screen[1]), int(screen[0]), 3), dtype=np.uint8)
                cv2.circle(canvas, (int(tx), int(ty)), 18, (0, 255, 0), -1)
                ix, iy, iw, ih = camera_inset_rect((int(screen[0]), int(screen[1])))
                canvas[iy : iy + ih, ix : ix + iw] = cv2.resize(frame, (iw, ih))
                remaining = max(args.calibration_seconds - dwell, 0.0)
                cv2.putText(
                    canvas,
                    f"point {idx + 1}/9 - look at the dot - next in {remaining:.1f}s (SPACE to skip)",
                    (350, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
                cv2.imshow("calibration", canvas)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    return 2
                if key == 32 and dwell > 0.7:
                    break
                if dwell > 0.7 and r.ok and not r.blink:
                    collected.append(r.features)
            if len(collected) >= 4:
                mean_f = np.mean(collected, axis=0)
                samples.append((mean_f, np.array([tx, ty])))
                print(f"point {idx + 1}/9 ok ({len(collected)} samples)")
            else:
                print(f"point {idx + 1}/9 SKIPPED (face lost)")
    except KeyboardInterrupt:
        print("interrupted.")
        return 2
    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()

    if len(samples) < 7:
        print(f"ERROR: only {len(samples)} valid points; need >= 7. Retry in better light.")
        return 2
    coeffs = fit_calibration(samples)
    rmse = float(np.sqrt(np.mean([np.sum((map_gaze(coeffs, f, screen) - t) ** 2) for f, t in samples])))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(Calibration(coeffs, screen).to_json())
    print(f"calibration saved to {args.out} | fit RMSE {rmse:.0f} px over {len(samples)} points")
    return 0


def run_validation(args: argparse.Namespace) -> int:
    """5 held-out points (off the 3x3 calibration grid) -> error in px."""
    cal = Calibration.from_json(args.calibration.read_text())
    cap = open_camera(args)
    if not cap.isOpened():
        print(_CAMERA_HELP)
        return 2
    tracker = FaceTracker()
    w, h = int(cal.screen[0]), int(cal.screen[1])
    points = [(0.3, 0.3), (0.7, 0.3), (0.5, 0.5), (0.3, 0.7), (0.7, 0.7)]
    print(f"validating {args.calibration} on 5 held-out points; look at each dot")
    cv2.namedWindow("validation", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("validation", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    errors: list[float] = []
    try:
        for idx, (fx, fy) in enumerate(points):
            tx, ty = fx * w, fy * h
            gazes: list[np.ndarray] = []
            t_start = time.perf_counter()
            while (dwell := time.perf_counter() - t_start) < 3.0:
                ok, frame = cap.read()
                if not ok:
                    continue
                frame = cv2.flip(frame, 1)
                r = tracker.process(frame, time.perf_counter())
                canvas = np.zeros((h, w, 3), dtype=np.uint8)
                cv2.circle(canvas, (int(tx), int(ty)), 18, (0, 255, 0), -1)
                inset_w = min(240, int(0.15 * w))
                inset_h = inset_w * 9 // 16
                canvas[10 : 10 + inset_h, w - inset_w - 10 : w - 10] = cv2.resize(frame, (inset_w, inset_h))
                cv2.putText(
                    canvas,
                    f"point {idx + 1}/5 - next in {max(3.0 - dwell, 0.0):.1f}s",
                    (int(0.35 * w), 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
                if r.ok and not r.blink:
                    g = map_gaze(cal.coeffs, r.features, cal.screen)
                    if dwell > 0.7:
                        gazes.append(g)
                    cv2.circle(canvas, (int(g[0]), int(g[1])), 8, (0, 0, 255), 2)
                cv2.imshow("validation", canvas)
                if (cv2.waitKey(1) & 0xFF) == 27:
                    return 2
            if len(gazes) >= 4:
                mean_g = np.mean(gazes, axis=0)
                err = gaze_error_px(mean_g, np.array([tx, ty]))
                errors.append(err)
                print(
                    f"point {idx + 1}/5 target=({tx:.0f},{ty:.0f})"
                    f" gaze=({mean_g[0]:.0f},{mean_g[1]:.0f}) error={err:.0f}px"
                )
            else:
                print(f"point {idx + 1}/5 INVALID (face lost)")
    except KeyboardInterrupt:
        print("interrupted.")
        return 2
    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()

    if not errors:
        print("ERROR: no valid validation points; retry with better lighting/posture.")
        return 2
    errs = np.array(errors)
    print("=== webcam gaze accuracy (held-out) ===")
    print(f"mean {errs.mean():.0f}px | median {np.median(errs):.0f}px | max {errs.max():.0f}px")
    print(f"as % of screen width: mean {100 * errs.mean() / w:.1f}% | max {100 * errs.max() / w:.1f}%")
    return 0


def main() -> int:
    args = parse_args()
    if args.validate:
        if args.calibration is None:
            raise SystemExit("--validate requires --calibration <file>")
        if args.headless:
            raise SystemExit("--validate requires the preview window (drop --headless)")
        return run_validation(args)
    if args.calibrate:
        if args.headless:
            raise SystemExit("--calibrate requires the preview window (drop --headless)")
        return run_calibration(args)
    return run_session(args)


if __name__ == "__main__":
    raise SystemExit(main())
