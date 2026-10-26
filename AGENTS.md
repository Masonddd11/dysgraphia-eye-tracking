# AGENTS.md

Instructions for OpenCode agents working in this repo.

## Project

Final-year project (FYP): science-first dysgraphia screening study on an eye-tracking copy-task rig (concept doc: `docs/ideas/eye-tracking-dysgraphia-copy-task.md`). The Python sensor/analysis package is the priority; treat any future frontend work as secondary.

Real structure landed 2026-09-08 (V1 webcam module); Gazepoint GP3 HD adapter landed 2026-10-26. Commands:

- Sync env: `uv sync`
- Tests: `uv run pytest -q` (36 offline tests: gaze calibration math, switch detector, head-pose extraction, stimulus layout + word lookup, OpenGaze protocol codec)
- Webcam smoke (stats only): `uv run fyp-webcam --headless --duration 8`
- Webcam live preview (HUD + gaze dot): `uv run fyp-webcam --calibration data/calibration.json`
- Copy-task stimulus + word-level gaze overlay: `uv run fyp-webcam --calibration data/calibration.json --stimulus data/sample_paragraph.txt`
- 9-point gaze calibration: `uv run fyp-webcam --calibrate --screen-w <W> --screen-h <H> --out data/calibration.json`
- Gazepoint calibration (GP3 HD, requires Gazepoint Control): `uv run fyp-gazepoint --calibrate`
- Gazepoint gaze smoke to LSL (150 Hz): `uv run fyp-gazepoint --headless --duration 8`
- Gazepoint copy-task overlay: `uv run fyp-gazepoint --stimulus data/sample_paragraph.txt`
- Shortcuts (console script `fyp`, after `uv sync`): `uv run fyp calibrate` / `gaze` / `webcam` / `both` / `smoke` / `test` (aliases `cal g w b s t`). `fyp both --stimulus <FILE>` shows the Gazepoint overlay while the webcam records head pose; children run on the current interpreter, so no uv reinstall race.

Module boundaries: `src/fyp/webcam/` — `landmarks.py` (FaceMesh + solvePnP head pose), `gaze.py` (calibration math, pure), `switching.py` (hysteresis/dwell state machine, pure), `stimulus.py` (paragraph word-wrap layout + gaze→word resolution, pure), `lsl.py` (four outlets: FYP_WebcamGaze / FYP_WebcamHeadPose / FYP_WordIndex / FYP_SwitchEvents), `cli.py` (run loop + fullscreen stimulus overlay). Pure modules must stay numpy-only and unit-tested; hardware paths are verified by live smoke runs. `src/fyp/gazepoint/` — `protocol.py` (OpenGaze XML codec + POG fraction→px, pure), `client.py` (TCP client + on-device calibration), `lsl.py` (FYP_GazePoint: x_px, y_px, valid, pupil), `cli.py` (run loop + overlay). The Gazepoint supplies gaze only; monitor↔paper switching stays on the webcam head-pose stream.

Quirks:

- `mediapipe` is pinned `>=0.10.14,<0.10.15` — 0.10.15+ removed the legacy `mp.solutions` API this module uses.
- Two concurrent `uv run` processes can race on the per-run package reinstall and corrupt imports; use `uv run --no-sync` for the second concurrent process (e.g. an LSL consumer alongside the producer).
- Head-pitch contract: `pitch_down_deg` is POSITIVE when nose goes down; switch thresholds `--enter-deg/--exit-deg/--dwell-ms` operate on it.
- macOS: first camera use needs Camera permission granted to the terminal app.
- Gazepoint: Gazepoint Control (the OpenGaze server) is Windows-only ("Mac and Linux are not supported at this time" per Gazepoint). On macOS the adapter must point at a server on a Windows PC/VM via `--host <ip>`; the GP3 HD must be USB-attached to that Windows host, and the stimulus/calibration display must be the display that host drives. POG coordinates are screen fractions (0..1); the device's calibration is separate from the webcam `data/calibration.json`.

## Toolchain (owner-locked)

- Python: always use `uv` (`uv run`, `uv add`, `uv sync`). Never pip / venv / requirements.txt workflows.
- JavaScript/TypeScript: always use `bun` (`bun install`, `bun add`, `bun run`). Never npm / yarn / pnpm.
