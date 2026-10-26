"""Tests for the head-pitch monitor<->paper switch detector (pure state machine)."""

from fyp.webcam.switching import MONITOR, PAPER, SwitchConfig, SwitchDetector

CFG = SwitchConfig(enter_deg=18.0, exit_deg=12.0, dwell_ms=200.0)


def _detector() -> SwitchDetector:
    return SwitchDetector(CFG)


def test_starts_in_monitor_and_high_reading_alone_does_not_flip():
    d = _detector()
    assert d.update(down_deg=25.0, t_ms=0) == MONITOR
    assert d.events == []  # dwell not yet elapsed


def test_flip_to_paper_after_dwell():
    d = _detector()
    d.update(5.0, 0)
    for t_ms in (33, 66, 99, 132, 165, 198, 231, 264):
        state = d.update(25.0, t_ms)
    # pending armed at t=33; commit requires t - 33 >= 200 -> first at t=231? 198 < 200, 231 >= 198+? (231-33=198 <200), 264-33=231 >= 200
    assert state == PAPER
    assert d.events == [(264, PAPER)]


def test_hysteresis_band_holds_state():
    d = _detector()
    for t_ms in (33, 66, 99, 132, 165, 198, 231, 264):
        d.update(25.0, t_ms)
    assert d.state == PAPER
    # 12 < reading < 18 is the hold band: no flip either way
    for t_ms in range(300, 600, 33):
        assert d.update(15.0, t_ms) == PAPER
    assert d.events == [(264, PAPER)]


def test_excursion_shorter_than_dwell_is_ignored():
    d = _detector()
    d.update(5.0, 0)
    d.update(25.0, 33)  # single high frame
    for t_ms in (66, 99, 132):
        d.update(5.0, t_ms)  # back to monitor well before dwell elapses
    assert d.state == MONITOR
    assert d.events == []


def test_exit_threshold_flips_back_to_monitor():
    d = _detector()
    for t_ms in (33, 66, 99, 132, 165, 198, 231, 264):
        d.update(25.0, t_ms)
    for t_ms in range(300, 900, 33):
        state = d.update(8.0, t_ms)  # below exit threshold
    assert state == MONITOR
    assert d.events == [(264, PAPER), (531, MONITOR)]  # armed at 300, 531-300=231 >= 200
