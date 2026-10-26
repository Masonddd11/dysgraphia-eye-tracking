# Dysgraphia Eye-Tracking Copy-Task Rig

Research prototype for a science-first dysgraphia screening study: an eye-tracking
copy-task rig that streams gaze, head pose, and attention-switch events over LSL.

Two gaze sources:

- **Webcam** (macOS / Linux / Windows): MediaPipe FaceMesh + 9-point calibration.
  Working prototype, region-level accuracy (~2-4 deg visual angle).
- **Gazepoint GP3 HD** (Windows host): 150 Hz research tracker via the OpenGaze
  API. Fixation-grade (~0.5-1.0 deg). Gazepoint Control, which hosts the
  OpenGaze server, is **Windows-only**; on macOS the adapter acts as a client
  to a Windows machine via `--host <ip>`.

## Quick start

### Windows (data collection with the GP3 HD)

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Prerequisite: install **Gazepoint Control**, connect the GP3 HD to a USB 3.0
port, and confirm the OpenGaze API port is `4242` in Gazepoint Control.

### macOS / Linux (webcam + analysis)

```bash
bash install.sh
```

Both scripts install `uv` if needed, install Python 3.12, run `uv sync`, and
execute the offline test suite.

Manual equivalent:

```bash
uv sync
uv run fyp test
```

## Commands

`uv run fyp ...` is the entry point (or just `fyp ...` if the venv is active):

| Command | Purpose |
|---|---|
| `fyp calibrate` | Gazepoint on-device calibration (Windows host) |
| `fyp gaze --stimulus data/sample_paragraph.txt` | Gazepoint gaze + word overlay |
| `fyp webcam --stimulus data/sample_paragraph.txt` | webcam head pose + gaze |
| `fyp both --stimulus data/sample_paragraph.txt` | webcam head pose + Gazepoint gaze |
| `fyp smoke` | both sensors, 8 s, headless |
| `fyp test` | offline test suite |

Aliases: `cal`, `g`, `w`, `b`, `s`, `t`.

The Gazepoint server can run on another machine:

```bash
uv run fyp calibrate --host 192.168.1.50
uv run fyp gaze --host 192.168.1.50 --stimulus data/sample_paragraph.txt
```

For valid word-level gaze, the stimulus display must be the display Gazepoint
Control calibrates against (i.e. the Windows-driven screen).

## LSL streams

| Stream | Channels | Rate |
|---|---|---|
| `FYP_WebcamGaze` | x_px, y_px, confidence, blink | 60 Hz nominal |
| `FYP_WebcamHeadPose` | pitch_down_deg, yaw_deg, roll_deg | 60 Hz nominal |
| `FYP_WordIndex` | word index (-1 = off/eligible) | 60 Hz nominal |
| `FYP_SwitchEvents` | 0 = MONITOR, 1 = PAPER | irregular |
| `FYP_GazePoint` | x_px, y_px, valid, pupil_diameter_px | 150 Hz nominal |

## Layout

```
src/fyp/webcam/      webcam pipeline (FaceMesh, calibration, switching, stimulus)
src/fyp/gazepoint/   Gazepoint OpenGaze client + LSL + CLI
src/fyp/cli.py       unified `fyp` entry point
tests/               offline tests (36)
docs/                concept, proposal, paper chapters
install.sh           macOS/Linux setup
install.ps1          Windows setup
```

## Calibration and data

- Webcam calibration: `data/calibration.json` (personal; git-ignored).
- Gazepoint calibration lives in Gazepoint Control on the Windows host.
- `data/` is git-ignored except `data/sample_paragraph.txt`.

## Scope

Research prototype, not a diagnostic device. The study protocol and its
limitations are in `docs/ideas/eye-tracking-dysgraphia-copy-task.md`.
