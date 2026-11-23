"""Tests for screen-size override/fallback logic (no display required)."""

from fyp.screen import resolve_screen_size


def test_explicit_screen_size_wins():
    assert resolve_screen_size(1920, 1080) == (1920.0, 1080.0)
    assert resolve_screen_size(1440, 900) == (1440.0, 900.0)


def test_zero_uses_detected_size():
    got = resolve_screen_size(0, 0, detector=lambda: (1920, 1080))
    assert got == (1920.0, 1080.0)


def test_one_missing_dimension_uses_detected_size():
    got = resolve_screen_size(1920, 0, detector=lambda: (2560, 1440))
    assert got == (2560.0, 1440.0)
