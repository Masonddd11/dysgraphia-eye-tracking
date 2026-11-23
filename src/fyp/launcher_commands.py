"""Pure command construction for the clickable launcher.

Kept separate from the HTTP/Tk layer so the exact subprocess arguments can be
unit-tested without a display or camera.
"""

from __future__ import annotations

import sys
from pathlib import Path

ACTIONS = {
    "webcam_calibrate",
    "webcam_read",
    "gazepoint_calibrate",
    "gazepoint_read",
}


def build_command(
    action: str,
    *,
    stimulus: Path,
    font_scale: float = 0.0,
    line_spacing: float = 2.2,
    word_margin: float = 0.0,
    host: str = "127.0.0.1",
    calibration: Path | None = None,
    python_exe: str | None = None,
) -> list[str]:
    """Return the argv used by the launcher for one action.

    ``stimulus`` is ignored for calibration actions.  The webcam reading path
    only loads ``calibration`` when that file exists; otherwise the session can
    still display the passage, just without word-level gaze mapping.
    """
    if action not in ACTIONS:
        raise ValueError(f"unknown launcher action: {action}")

    py = python_exe or sys.executable
    prefix = [py, "-u", "-m"]

    if action == "webcam_calibrate":
        return prefix + ["fyp.webcam.cli", "--calibrate"]

    if action == "gazepoint_calibrate":
        return prefix + [
            "fyp.gazepoint.cli",
            "--calibrate",
            "--area",
            "full",
            "--host",
            host,
        ]

    if action == "webcam_read":
        cmd = prefix + ["fyp.webcam.cli", "--stimulus", str(stimulus)]
        if calibration is not None and calibration.exists():
            cmd += ["--calibration", str(calibration)]
        if font_scale > 0:
            cmd += ["--font-scale", str(font_scale)]
        cmd += ["--line-spacing", str(line_spacing)]
        if word_margin > 0:
            cmd += ["--word-margin", str(word_margin)]
        return cmd

    # gazepoint_read
    cmd = prefix + ["fyp.gazepoint.cli", "--stimulus", str(stimulus), "--host", host]
    if font_scale > 0:
        cmd += ["--font-scale", str(font_scale)]
    cmd += ["--line-spacing", str(line_spacing)]
    if word_margin > 0:
        cmd += ["--word-margin", str(word_margin)]
    return cmd
