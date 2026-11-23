"""Tests for the optional reading row lock (pure state machine)."""

from fyp.webcam.rowlock import RowLock, rows_from_boxes
from fyp.webcam.stimulus import WordBox

BOXES = [
    WordBox("top", 0, 100, 100, 50, 30, line=0),
    WordBox("middle", 1, 100, 180, 60, 30, line=1),
    WordBox("bottom", 2, 100, 260, 55, 30, line=2),
]


def lock() -> RowLock:
    return RowLock(release_px=30.0, release_s=0.12, switch_margin_px=4.0)


def test_rows_collapse_word_boxes():
    rows = rows_from_boxes(BOXES)
    assert [row.line for row in rows] == [0, 1, 2]
    assert rows[1].top == 180
    assert rows[1].bottom == 210
    assert rows[1].center == 195


def test_lock_starts_on_nearest_row():
    row_lock = lock()
    assert row_lock.update(188.0, BOXES, 0.0) == 1
    assert row_lock.update(250.0, BOXES, 1.0) == 1  # still current until release


def test_lock_holds_through_gap_and_jitter():
    row_lock = lock()
    assert row_lock.update(195.0, BOXES, 0.0) == 1
    assert row_lock.update(150.0, BOXES, 0.1) == 1  # just outside, not long enough
    assert row_lock.update(145.0, BOXES, 0.2) == 1  # starts release timer
    assert row_lock.update(145.0, BOXES, 0.4) == 0  # clear move to the top row


def test_lock_switches_only_after_clear_vertical_move():
    row_lock = lock()
    assert row_lock.update(195.0, BOXES, 0.0) == 1
    assert row_lock.update(275.0, BOXES, 0.1) == 1
    assert row_lock.update(275.0, BOXES, 0.2) == 1
    assert row_lock.update(275.0, BOXES, 0.3) == 2


def test_reset_and_empty_layout():
    row_lock = lock()
    assert row_lock.update(195.0, BOXES, 0.0) == 1
    row_lock.reset()
    assert row_lock.update(275.0, BOXES, 0.0) == 2
    assert row_lock.update(275.0, [], 0.1) is None
