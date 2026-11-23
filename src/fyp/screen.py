"""Cross-platform display-size detection for full-screen OpenCV views.

The calibration canvas and the reading stimulus are rendered at native display
resolution.  If that size is wrong, OpenCV either letterboxes a 16:10 canvas on
a 16:9 laptop or the calibration dots do not reach the screen edges.  This
module keeps the layout tied to the actual display.

``--screen-w``/``--screen-h`` still override the detected values for lab
setups with an external display or a virtual desktop.
"""

from __future__ import annotations

import ctypes
import os
import sys
from collections.abc import Callable

FALLBACK_SCREEN = (1920, 1080)


def _macos_screen_size() -> tuple[int, int] | None:
    """Native pixels of the main display via CoreGraphics (no extra deps)."""
    if sys.platform != "darwin":
        return None
    try:
        cg = ctypes.CDLL(
            "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
        )
        cg.CGMainDisplayID.restype = ctypes.c_uint32
        cg.CGDisplayPixelsWide.argtypes = [ctypes.c_uint32]
        cg.CGDisplayPixelsWide.restype = ctypes.c_size_t
        cg.CGDisplayPixelsHigh.argtypes = [ctypes.c_uint32]
        cg.CGDisplayPixelsHigh.restype = ctypes.c_size_t
        display = cg.CGMainDisplayID()
        width = int(cg.CGDisplayPixelsWide(display))
        height = int(cg.CGDisplayPixelsHigh(display))
        if width > 0 and height > 0:
            return width, height
    except Exception:
        pass
    return None


def _windows_screen_size() -> tuple[int, int] | None:
    if os.name != "nt":
        return None
    try:
        user32 = ctypes.windll.user32
        # Per-monitor DPI-aware so GetSystemMetrics returns physical pixels.
        try:
            user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except Exception:
            pass
        width = int(user32.GetSystemMetrics(0))
        height = int(user32.GetSystemMetrics(1))
        if width > 0 and height > 0:
            return width, height
    except Exception:
        pass
    return None


def _linux_screen_size() -> tuple[int, int] | None:
    try:
        from screeninfo import get_monitors  # optional dependency

        monitors = get_monitors()
        if monitors:
            return int(monitors[0].width), int(monitors[0].height)
    except Exception:
        pass
    return None


def detect_screen_size() -> tuple[int, int]:
    """Return the main display size in pixels, with a 1920x1080 fallback."""
    for detector in (
        _macos_screen_size,
        _windows_screen_size,
        _linux_screen_size,
    ):
        size = detector()
        if size is not None:
            return size
    return FALLBACK_SCREEN


def resolve_screen_size(
    width: int,
    height: int,
    *,
    detector: Callable[[], tuple[int, int]] = detect_screen_size,
) -> tuple[float, float]:
    """Resolve CLI overrides, falling back to the detected display size.

    ``detector`` is injectable so the override/fallback logic can be tested
    without a display server.
    """
    if width > 0 and height > 0:
        return float(width), float(height)
    detected = detector()
    return float(detected[0]), float(detected[1])
