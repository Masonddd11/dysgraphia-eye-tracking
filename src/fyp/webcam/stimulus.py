"""Copy-task stimulus: paragraph layout with word bounding boxes + gaze->word resolution.

Renders the prompt the subject copies from. Layout math is pure (numpy/cv2
only) so word positions are known exactly; the gaze overlay highlights the
word the (calibrated, smoothed) gaze estimate falls in.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

_FONT = cv2.FONT_HERSHEY_SIMPLEX


@dataclass
class WordBox:
    text: str
    index: int
    x: float  # top-left px
    y: float
    w: float
    h: float
    line: int


@dataclass
class LayoutResult:
    boxes: list[WordBox]
    line_height: float


def layout_paragraph(
    text: str,
    font: int = _FONT,
    font_scale: float = 1.0,
    thickness: int = 2,
    max_width_px: int = 1280,
    margin_px: int = 100,
    line_spacing: float = 1.8,
) -> LayoutResult:
    """Greedy word-wrap layout; every word gets a screen-space bounding box."""
    words = text.split()
    (_, sample_h), _ = cv2.getTextSize("Ag", font, font_scale, thickness)
    line_height = sample_h * line_spacing
    usable_right = max_width_px - margin_px

    boxes: list[WordBox] = []
    space_w = cv2.getTextSize("x x", font, font_scale, thickness)[0][0] - 2 * cv2.getTextSize(
        "x", font, font_scale, thickness
    )[0][0]
    x, line = float(margin_px), 0
    for i, word in enumerate(words):
        (w, h), _ = cv2.getTextSize(word, font, font_scale, thickness)
        if x > margin_px and x + w > usable_right:
            x = float(margin_px)
            line += 1
        boxes.append(WordBox(word, i, x, margin_px + line * line_height, float(w), float(h), line))
        x += w + space_w
    return LayoutResult(boxes, line_height)


def word_at(gaze_xy: np.ndarray, boxes: list[WordBox], tolerance_px: float) -> int:
    """Index of the first word whose (tolerance-expanded) bbox contains the point, else -1."""
    gx, gy = float(gaze_xy[0]), float(gaze_xy[1])
    for b in boxes:
        if (b.x - tolerance_px <= gx <= b.x + b.w + tolerance_px) and (
            b.y - tolerance_px <= gy <= b.y + b.h + tolerance_px
        ):
            return b.index
    return -1


def render_paragraph(
    canvas_wh: tuple[int, int],
    layout: LayoutResult,
    font: int = _FONT,
    font_scale: float = 1.0,
    thickness: int = 2,
    highlight: int = -1,
) -> np.ndarray:
    """Draw the paragraph; the highlighted word gets an inverted box."""
    canvas = np.zeros((canvas_wh[1], canvas_wh[0], 3), dtype=np.uint8)
    for b in layout.boxes:
        origin = (int(b.x), int(b.y + b.h))
        if b.index == highlight:
            cv2.rectangle(
                canvas,
                (int(b.x) - 6, int(b.y) - 6),
                (int(b.x + b.w) + 6, int(b.y + b.h) + 6),
                (80, 80, 80),
                -1,
            )
            cv2.putText(canvas, b.text, origin, font, font_scale, (0, 255, 255), thickness)
        else:
            cv2.putText(canvas, b.text, origin, font, font_scale, (200, 200, 200), thickness)
    return canvas
