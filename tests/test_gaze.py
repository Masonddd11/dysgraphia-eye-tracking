"""Tests for the 9-point gaze calibration math (pure functions, no hardware)."""

import numpy as np
import pytest

from fyp.webcam.gaze import calibration_rmse, fit_calibration, gaze_error_px, map_gaze

SCREEN = (1440.0, 900.0)


def _synthetic_samples(rng: np.random.Generator, n: int, true_coeffs: np.ndarray):
    samples = []
    for _ in range(n):
        features = rng.normal(size=6)
        target = np.concatenate([features, [1.0]]) @ true_coeffs
        samples.append((features, target))
    return samples


def _in_bounds_coeffs(seed: int, scale: float) -> np.ndarray:
    """Affine map whose outputs stay inside the screen for N(0,1) features."""
    coeffs = np.random.default_rng(seed).normal(scale=scale, size=(7, 2))
    coeffs[6] = [720.0, 450.0]  # bias targets to screen centre
    return coeffs


def test_fit_recovers_known_affine_map():
    rng = np.random.default_rng(7)
    true_coeffs = np.random.default_rng(1).normal(scale=50.0, size=(7, 2))
    coeffs = fit_calibration(_synthetic_samples(rng, 30, true_coeffs))
    assert np.allclose(coeffs, true_coeffs, atol=1e-6)


def test_fit_with_9_points_exactly_determined_shape():
    rng = np.random.default_rng(3)
    true_coeffs = _in_bounds_coeffs(2, 20.0)
    coeffs = fit_calibration(_synthetic_samples(rng, 9, true_coeffs))
    assert coeffs.shape == (7, 2)
    assert calibration_rmse(coeffs, _synthetic_samples(rng, 40, true_coeffs), SCREEN) < 1e-3


def test_map_gaze_clips_to_screen_bounds():
    coeffs = np.zeros((7, 2))
    coeffs[6] = [500.0, 400.0]  # constant gaze at screen centre-ish
    got = map_gaze(coeffs, np.zeros(6), SCREEN)
    assert np.allclose(got, [500.0, 400.0])

    coeffs[0, 0] = 1e5  # huge x sensitivity drives the estimate far out
    got = map_gaze(coeffs, np.ones(6), SCREEN)
    assert got[0] == SCREEN[0] - 1.0
    coeffs[1, 1] = -1e5
    got = map_gaze(coeffs, np.ones(6), SCREEN)
    assert got[1] == 0.0


def test_gaze_error_px_is_euclidean_distance():
    assert gaze_error_px(np.array([100.0, 100.0]), np.array([130.0, 140.0])) == pytest.approx(50.0)
    assert gaze_error_px(np.array([720.0, 450.0]), np.array([720.0, 450.0])) == 0.0


def test_rmse_zero_for_consistent_system():
    rng = np.random.default_rng(11)
    true_coeffs = _in_bounds_coeffs(5, 15.0)
    coeffs = fit_calibration(_synthetic_samples(rng, 12, true_coeffs))
    rmse = calibration_rmse(coeffs, _synthetic_samples(rng, 12, true_coeffs), SCREEN)
    assert rmse < 1e-3
