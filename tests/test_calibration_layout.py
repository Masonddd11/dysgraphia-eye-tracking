"""Tests for calibration-canvas layout: the camera inset must never cover a dot."""

import pytest

from fyp.webcam.cli import camera_inset_rect

RESOLUTIONS = [(1024, 768), (1280, 800), (1440, 900), (1512, 982), (1920, 1080)]
FRACS = (0.1, 0.5, 0.9)
DOT_RADIUS = 18
PAD = 12


@pytest.mark.parametrize("w,h", RESOLUTIONS)
def test_inset_never_overlaps_any_calibration_dot(w, h):
    x, y, iw, ih = camera_inset_rect((w, h))
    assert iw > 0 and ih > 0
    assert 0 <= x and x + iw <= w and 0 <= y and y + ih <= h
    for fy in FRACS:
        for fx in FRACS:
            dx, dy = fx * w, fy * h
            pad = DOT_RADIUS + PAD
            disjoint = (
                x + iw < dx - pad
                or x > dx + pad
                or y + ih < dy - pad
                or y > dy + pad
            )
            assert disjoint, f"inset {(x, y, iw, ih)} overlaps dot ({dx:.0f},{dy:.0f}) at {w}x{h}"


def test_inset_fits_smallest_gap():
    x, y, iw, ih = camera_inset_rect((900, 700))
    assert 0 <= x and x + iw <= 900
    assert ih == iw * 9 // 16
