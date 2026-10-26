"""Tests for stimulus paragraph layout and gaze->word resolution (no hardware)."""

import cv2

from fyp.webcam.stimulus import WordBox, layout_paragraph, render_paragraph, word_at

FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT = "the quick brown fox jumps over the lazy dog " * 3


def test_layout_preserves_words_and_indices():
    layout = layout_paragraph(TEXT, FONT, font_scale=1.0, thickness=2, max_width_px=400, margin_px=20)
    assert [b.text for b in layout.boxes] == TEXT.split()
    assert [b.index for b in layout.boxes] == list(range(len(TEXT.split())))


def test_layout_wraps_within_usable_width():
    margin, width = 20, 400
    layout = layout_paragraph(TEXT, FONT, 1.0, 2, width, margin)
    assert len({b.line for b in layout.boxes}) > 1  # wrapping actually happened
    for b in layout.boxes:
        assert b.x >= margin - 0.5
        assert b.x + b.w <= width - margin + 0.5
    # no horizontal overlap between consecutive words on the same line
    for a, b in zip(layout.boxes, layout.boxes[1:]):
        if a.line == b.line:
            assert b.x >= a.x + a.w - 0.5
    assert layout.line_height > 0


def test_layout_lines_advance_downward():
    layout = layout_paragraph(TEXT, FONT, 1.0, 2, 400, 20)
    lines = sorted({b.line for b in layout.boxes})
    for prev, nxt in zip(lines, lines[1:]):
        y_prev = max(b.y + b.h for b in layout.boxes if b.line == prev)
        y_next = min(b.y for b in layout.boxes if b.line == nxt)
        assert y_next >= y_prev  # next line starts below previous line's extent


def test_word_at_containment_tolerance_and_miss():
    boxes = [
        WordBox("aa", 0, 100, 100, 60, 30, line=0),
        WordBox("bb", 1, 200, 100, 60, 30, line=0),
    ]
    assert word_at((115.0, 110.0), boxes, tolerance_px=0.0) == 0
    assert word_at((215.0, 125.0), boxes, tolerance_px=0.0) == 1
    assert word_at((165.0, 115.0), boxes, tolerance_px=0.0) == -1  # gap between boxes
    assert word_at((165.0, 115.0), boxes, tolerance_px=30.0) in (0, 1)  # expanded boxes reach the gap
    assert word_at((900.0, 900.0), boxes, tolerance_px=30.0) == -1  # far away
    assert word_at((115.0, 110.0), [], tolerance_px=10.0) == -1


def test_render_paragraph_draws_words_and_highlight():
    layout = layout_paragraph(TEXT, FONT, 1.0, 2, 400, 20)
    plain = render_paragraph((500, 2000), layout, FONT, 1.0, 2, highlight=-1)
    highlighted = render_paragraph((500, 2000), layout, FONT, 1.0, 2, highlight=0)
    assert plain.shape == highlighted.shape == (2000, 500, 3)
    import numpy as np

    assert not np.array_equal(plain, highlighted)  # highlight visibly changes pixels
    assert plain.sum() > 0  # words were drawn
