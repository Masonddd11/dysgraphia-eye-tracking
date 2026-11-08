"""Tests for the text-column calibration grid (pure math, no hardware)."""

from fyp.gazepoint.client import DEFAULT_TEXT_WIDTH_FRACTION, text_area_points


def test_text_area_grid_is_nine_points_inside_the_column():
    points = text_area_points(3440.0)
    assert len(points) == 9
    half = DEFAULT_TEXT_WIDTH_FRACTION / 2
    for x, y in points:
        assert 0.5 - half - 1e-9 <= x <= 0.5 + half + 1e-9
        assert 0.0 < y < 1.0


def test_text_area_grid_follows_explicit_width():
    points = text_area_points(3440.0, text_width_px=1600)
    xs = sorted({round(x, 4) for x, _ in points})
    assert xs[0] >= 0.27 and xs[-1] <= 0.73
    assert xs[1] == 0.5


def test_text_area_grid_clamps_absurd_width():
    points = text_area_points(1000.0, text_width_px=5000)
    assert all(0.05 <= x <= 0.95 for x, _ in points)

def test_text_area_grid_starts_at_centre():
    assert text_area_points(3440.0)[0] == (0.5, 0.5)
