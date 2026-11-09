"""Tests for preview smoothing (adaptive One Euro + word dwell), no hardware."""

import numpy as np

from fyp.smoothing import OneEuroPoint, WordDwell


def test_one_euro_reduces_fixation_jitter():
    rng = np.random.default_rng(0)
    raw = 0.5 + rng.normal(0.0, 0.002, 3000)
    smoother = OneEuroPoint(min_cutoff=0.7, beta=5.0)
    out = np.array([smoother(x, 0.5, i / 150.0)[0] for i, x in enumerate(raw)])
    assert np.std(out[300:]) < 0.35 * np.std(raw[300:])


def test_one_euro_settles_after_saccade():
    smoother = OneEuroPoint(min_cutoff=0.7, beta=5.0)
    out = []
    for i in range(300):
        t = i / 150.0
        out.append(smoother(0.0 if t < 0.5 else 0.3, 0.5, t)[0])
    assert abs(out[-1] - 0.3) < 0.005
    assert out[74] < 0.05  # still at the old position before the saccade


def test_one_euro_median_rejects_single_sample_spike():
    smoother = OneEuroPoint(min_cutoff=0.7, beta=5.0)
    for i in range(200):
        smoother(0.5, 0.5, i / 150.0)
    assert smoother(0.9, 0.5, 200 / 150.0)[0] < 0.55


def test_word_dwell_ignores_short_flicker():
    dwell = WordDwell(dwell_s=0.12)
    assert dwell.update(3, 0.00) == -1
    assert dwell.update(3, 0.13) == 3
    # jump to 4 for less than the dwell, then back: committed word holds
    assert dwell.update(4, 0.14) == 3
    assert dwell.update(4, 0.20) == 3
    assert dwell.update(3, 0.21) == 3


def test_word_dwell_commits_stable_word_and_clears():
    dwell = WordDwell(dwell_s=0.12)
    assert dwell.update(3, 0.00) == -1
    assert dwell.update(3, 0.13) == 3
    assert dwell.update(4, 0.14) == 3
    assert dwell.update(4, 0.27) == 4
    assert dwell.update(-1, 0.28) == 4
    assert dwell.update(-1, 0.41) == -1


def test_word_dwell_reset_clears_immediately():
    dwell = WordDwell(dwell_s=0.12)
    dwell.update(3, 0.0)
    assert dwell.update(3, 0.2) == 3
    dwell.reset()
    assert dwell.update(3, 0.3) == -1
