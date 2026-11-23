"""Optional line/row lock for gaze-to-word assignment.

Without a lock, a gaze point halfway between two lines can fall into either
line's expanded word boxes.  The line lock keeps the current reading row until
the gaze clearly leaves it for another row, which makes word-level output more
stable during normal reading saccades.
"""

from __future__ import annotations

from dataclasses import dataclass

from fyp.webcam.stimulus import WordBox


@dataclass(frozen=True)
class RowGeometry:
    line: int
    top: float
    bottom: float
    center: float


def rows_from_boxes(boxes: list[WordBox]) -> list[RowGeometry]:
    """Collapse word boxes into one vertical band per text line."""
    grouped: dict[int, list[WordBox]] = {}
    for box in boxes:
        grouped.setdefault(box.line, []).append(box)
    rows: list[RowGeometry] = []
    for line in sorted(grouped):
        group = grouped[line]
        top = min(box.y for box in group)
        bottom = max(box.y + box.h for box in group)
        rows.append(RowGeometry(line, top, bottom, (top + bottom) * 0.5))
    return rows


class RowLock:
    """Hysteresis-based row lock.

    ``release_px`` is how far outside the current row the gaze must go before
    a switch is considered.  ``release_s`` is how long it must stay outside,
    and ``switch_margin_px`` requires the other row to be meaningfully closer.
    """

    def __init__(
        self,
        *,
        release_px: float = 24.0,
        release_s: float = 0.12,
        switch_margin_px: float = 4.0,
    ) -> None:
        self.release_px = max(0.0, release_px)
        self.release_s = max(0.0, release_s)
        self.switch_margin_px = max(0.0, switch_margin_px)
        self.line: int | None = None
        self._outside_since: float | None = None

    def reset(self) -> None:
        self.line = None
        self._outside_since = None

    def update(
        self, gaze_y: float, boxes: list[WordBox], now_s: float
    ) -> int | None:
        rows = rows_from_boxes(boxes)
        if not rows:
            self.reset()
            return None

        by_line = {row.line: row for row in rows}
        if self.line not in by_line:
            nearest = min(rows, key=lambda row: abs(gaze_y - row.center))
            self.line = nearest.line
            self._outside_since = None
            return self.line

        current = by_line[self.line]
        nearest = min(rows, key=lambda row: abs(gaze_y - row.center))
        if nearest.line == current.line:
            self._outside_since = None
            return current.line

        outside = (
            gaze_y < current.top - self.release_px
            or gaze_y > current.bottom + self.release_px
        )
        other_is_closer = (
            abs(gaze_y - nearest.center) + self.switch_margin_px
            < abs(gaze_y - current.center)
        )
        if not outside or not other_is_closer:
            self._outside_since = None
            return current.line

        if self._outside_since is None:
            self._outside_since = now_s
        elif now_s - self._outside_since >= self.release_s:
            self.line = nearest.line
            self._outside_since = None
        return self.line
