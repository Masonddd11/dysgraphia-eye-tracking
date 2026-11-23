"""Tests for the pure command builder behind the clickable launcher."""

import pytest

from fyp.launcher_commands import build_command

PY = "/usr/bin/python3"


def _files(tmp_path):
    stimulus = tmp_path / "sample_paragraph.txt"
    stimulus.write_text("The patient was asked to copy this paragraph.")
    calibration = tmp_path / "calibration.json"
    calibration.write_text("{}")
    return stimulus, calibration


def test_webcam_calibration_command(tmp_path):
    stimulus, _ = _files(tmp_path)
    assert build_command(
        "webcam_calibrate", stimulus=stimulus, python_exe=PY
    ) == [PY, "-u", "-m", "fyp.webcam.cli", "--calibrate"]


def test_webcam_read_command_includes_calibration_and_layout(tmp_path):
    stimulus, calibration = _files(tmp_path)
    cmd = build_command(
        "webcam_read",
        stimulus=stimulus,
        calibration=calibration,
        font_scale=1.8,
        line_spacing=2.2,
        word_margin=18,
        python_exe=PY,
    )
    assert cmd[:4] == [PY, "-u", "-m", "fyp.webcam.cli"]
    assert "--stimulus" in cmd and str(stimulus) in cmd
    assert "--calibration" in cmd and str(calibration) in cmd
    assert cmd[cmd.index("--font-scale") + 1] == "1.8"
    assert cmd[cmd.index("--line-spacing") + 1] == "2.2"
    assert cmd[cmd.index("--word-margin") + 1] == "18"


def test_webcam_read_omits_missing_calibration_and_zero_margin(tmp_path):
    stimulus, missing = _files(tmp_path)
    cmd = build_command(
        "webcam_read",
        stimulus=stimulus,
        calibration=missing.with_name("does-not-exist.json"),
        word_margin=0,
        python_exe=PY,
    )
    assert "--calibration" not in cmd
    assert "--word-margin" not in cmd


def test_gazepoint_calibration_command_uses_host(tmp_path):
    stimulus, _ = _files(tmp_path)
    cmd = build_command(
        "gazepoint_calibrate",
        stimulus=stimulus,
        host="192.168.1.50",
        python_exe=PY,
    )
    assert cmd[:4] == [PY, "-u", "-m", "fyp.gazepoint.cli"]
    assert "--calibrate" in cmd
    assert cmd[cmd.index("--area") + 1] == "full"
    assert cmd[cmd.index("--host") + 1] == "192.168.1.50"


def test_gazepoint_read_command(tmp_path):
    stimulus, _ = _files(tmp_path)
    cmd = build_command(
        "gazepoint_read",
        stimulus=stimulus,
        host="192.168.1.50",
        font_scale=1.8,
        word_margin=20,
        python_exe=PY,
    )
    assert "--stimulus" in cmd
    assert cmd[cmd.index("--host") + 1] == "192.168.1.50"
    assert cmd[cmd.index("--font-scale") + 1] == "1.8"
    assert cmd[cmd.index("--word-margin") + 1] == "20"


def test_row_lock_can_be_disabled(tmp_path):
    stimulus, _ = _files(tmp_path)
    cmd = build_command(
        "webcam_read",
        stimulus=stimulus,
        row_lock=False,
        python_exe=PY,
    )
    assert "--no-row-lock" in cmd


def test_row_lock_is_on_by_default(tmp_path):
    stimulus, _ = _files(tmp_path)
    cmd = build_command("webcam_read", stimulus=stimulus, python_exe=PY)
    assert "--no-row-lock" not in cmd


def test_unknown_action_is_rejected(tmp_path):
    stimulus, _ = _files(tmp_path)
    with pytest.raises(ValueError):
        build_command("delete_everything", stimulus=stimulus, python_exe=PY)
