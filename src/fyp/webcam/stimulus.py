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

# Reading text is intentionally large: bigger glyphs and generous line spacing
# give the word-level gaze classifier larger, cleaner hit regions.
DEFAULT_FONT_HEIGHT_RATIO = 1.5
DEFAULT_LINE_SPACING = 2.2


def auto_font_scale(screen_height: float) -> float:
    """Font scale that keeps the passage large on the current display."""
    return max(1.0, DEFAULT_FONT_HEIGHT_RATIO * screen_height / 900.0)


def auto_thickness(font_scale: float) -> int:
    """Stroke width that stays proportional to the enlarged font."""
    return max(2, int(round(font_scale * 1.5)))


def auto_word_margins(font_scale: float, line_height: float) -> tuple[float, float]:
    """Automatic gaze-to-word hit margins (x, y) in pixels.

    Word spacing controls horizontal ambiguity; line spacing controls vertical
    ambiguity.  These values reach into the gaps without erasing the nearest-
    word decision.
    """
    return max(4.0, font_scale * 5.0), max(6.0, line_height * 0.23)


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
    top_px: int | None = None,
) -> LayoutResult:
    """Greedy word-wrap layout; every word gets a screen-space bounding box.

    ``margin_px`` is the left/right margin; ``top_px`` overrides the vertical
    origin (defaults to ``margin_px``) so a centred column can start higher
    than its horizontal margin.
    """
    words = text.split()
    (_, sample_h), _ = cv2.getTextSize("Ag", font, font_scale, thickness)
    line_height = sample_h * line_spacing
    usable_right = max_width_px - margin_px
    top = margin_px if top_px is None else top_px

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
        boxes.append(WordBox(word, i, x, top + line * line_height, float(w), float(h), line))
        x += w + space_w
    return LayoutResult(boxes, line_height)


def word_at(
    gaze_xy: np.ndarray,
    boxes: list[WordBox],
    tolerance_px: float = 0.0,
    *,
    x_tolerance_px: float | None = None,
    y_tolerance_px: float | None = None,
) -> int:
    """Index of the nearest word within the hit margin, else -1.

    Horizontal and vertical margins can differ: horizontal error mostly causes
    a word to be confused with its neighbour, while vertical error is larger
    during reading.  Taking the nearest expanded box (rather than the first
    match in reading order) avoids biasing every ambiguous gaze point towards
    the earlier word.
    """
    gx, gy = float(gaze_xy[0]), float(gaze_xy[1])
    x_tol = tolerance_px if x_tolerance_px is None else x_tolerance_px
    y_tol = tolerance_px if y_tolerance_px is None else y_tolerance_px

    best_index = -1
    best_distance = float("inf")
    for b in boxes:
        left = b.x - x_tol
        right = b.x + b.w + x_tol
        top = b.y - y_tol
        bottom = b.y + b.h + y_tol
        if not (left <= gx <= right and top <= gy <= bottom):
            continue

        # Squared distance to the unexpanded word rectangle; 0 when inside.
        dx = max(b.x - gx, 0.0, gx - (b.x + b.w))
        dy = max(b.y - gy, 0.0, gy - (b.y + b.h))
        distance = dx * dx + dy * dy
        if distance < best_distance:
            best_distance = distance
            best_index = b.index
    return best_index


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
