"""Display-side smoothing for noisy point streams.

Pure Python (math only): the live previews use these, LSL streams stay raw.
The One Euro filter (Casiez et al., 2012) adapts its cutoff to speed: heavy
smoothing while the eye is still, light smoothing during saccades so the dot
does not trail behind the gaze.
"""

from __future__ import annotations

import math
from collections import deque
from statistics import median


def _alpha(cutoff_hz: float, dt_s: float) -> float:
    tau = 1.0 / (2.0 * math.pi * cutoff_hz)
    return 1.0 / (1.0 + tau / dt_s)


class OneEuroFilter:
    """1-D adaptive low-pass filter; lower ``min_cutoff`` = smoother at rest."""

    def __init__(
        self,
        min_cutoff: float = 0.7,
        beta: float = 5.0,
        d_cutoff: float = 1.0,
    ) -> None:
        self._min_cutoff = min_cutoff
        self._beta = beta
        self._d_cutoff = d_cutoff
        self._x_prev: float | None = None
        self._x_hat: float | None = None
        self._edx = 0.0
        self._t_prev: float | None = None

    def __call__(self, x: float, t: float) -> float:
        if self._x_prev is None or self._x_hat is None or self._t_prev is None:
            self._x_prev = self._x_hat = float(x)
            self._t_prev = t
            return self._x_hat
        dt = max(t - self._t_prev, 1e-4)
        dx = (x - self._x_prev) / dt
        self._edx += _alpha(self._d_cutoff, dt) * (dx - self._edx)
        cutoff = self._min_cutoff + self._beta * abs(self._edx)
        self._x_hat += _alpha(cutoff, dt) * (x - self._x_hat)
        self._x_prev = float(x)
        self._t_prev = t
        return self._x_hat

    def reset(self) -> None:
        self._x_prev = self._x_hat = self._t_prev = None
        self._edx = 0.0


class OneEuroPoint:
    """2-D One Euro filter with a 3-sample median prefilter for spike rejection."""

    def __init__(
        self,
        min_cutoff: float = 0.7,
        beta: float = 5.0,
        d_cutoff: float = 1.0,
    ) -> None:
        self._x = OneEuroFilter(min_cutoff, beta, d_cutoff)
        self._y = OneEuroFilter(min_cutoff, beta, d_cutoff)
        self._recent_x: deque[float] = deque(maxlen=3)
        self._recent_y: deque[float] = deque(maxlen=3)

    def __call__(self, x: float, y: float, t: float) -> tuple[float, float]:
        self._recent_x.append(float(x))
        self._recent_y.append(float(y))
        return (
            self._x(median(self._recent_x), t),
            self._y(median(self._recent_y), t),
        )

    def reset(self) -> None:
        self._x.reset()
        self._y.reset()
        self._recent_x.clear()
        self._recent_y.clear()


class WordDwell:
    """Commit a word index only after it has been stable for ``dwell_s``."""

    def __init__(self, dwell_s: float = 0.12) -> None:
        self._dwell_s = dwell_s
        self._candidate = -1
        self._committed = -1
        self._since: float | None = None

    def update(self, word: int, t: float) -> int:
        if word != self._candidate:
            self._candidate = word
            self._since = t
        elif (
            word != self._committed
            and self._since is not None
            and t - self._since >= self._dwell_s
        ):
            self._committed = word
        return self._committed

    def reset(self) -> None:
        self._candidate = self._committed = -1
        self._since = None
