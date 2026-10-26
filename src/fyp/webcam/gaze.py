"""9-point linear calibration: eye/iris feature vectors -> screen pixel gaze.

Pure functions (numpy only) so the mapping math is testable offline. The
feature vector is produced by ``landmarks.FaceTracker``:

    f = [iris_offset_x_right, iris_offset_y_right,
         iris_offset_x_left,  iris_offset_y_left,
         head_pitch_down_deg, head_yaw_deg]

A per-axis affine map (least squares with intercept) is fit from calibration
samples. This yields region-level accuracy on a webcam (~2-4 deg visual
angle); fixation-grade metrics remain the research tracker's job.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

FEATURE_DIM = 6


@dataclass
class Calibration:
    coeffs: np.ndarray  # (FEATURE_DIM + 1, 2) affine coefficients
    screen: tuple[float, float]  # (width_px, height_px)

    def to_json(self) -> str:
        return json.dumps(
            {"screen": list(self.screen), "coeffs": self.coeffs.tolist()}, indent=2
        )

    @classmethod
    def from_json(cls, text: str) -> "Calibration":
        data = json.loads(text)
        return cls(
            coeffs=np.asarray(data["coeffs"], dtype=np.float64),
            screen=(float(data["screen"][0]), float(data["screen"][1])),
        )


def _design_row(features: np.ndarray) -> np.ndarray:
    features = np.asarray(features, dtype=np.float64)
    if features.shape != (FEATURE_DIM,):
        raise ValueError(f"expected feature vector of shape ({FEATURE_DIM},)")
    return np.concatenate([features, [1.0]])


def fit_calibration(samples: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    """Fit [features -> screen px] via least squares. Returns (7, 2) coeffs."""
    if len(samples) < FEATURE_DIM + 1:
        raise ValueError("need at least 7 calibration samples")
    x = np.array([_design_row(f) for f, _ in samples])
    y = np.array([np.asarray(t, dtype=np.float64) for _, t in samples])
    coeffs, *_ = np.linalg.lstsq(x, y, rcond=None)
    return coeffs


def map_gaze(
    coeffs: np.ndarray, features: np.ndarray, screen: tuple[float, float]
) -> np.ndarray:
    """Map a feature vector to screen pixels, clipped to the screen bounds."""
    xy = _design_row(features) @ np.asarray(coeffs, dtype=np.float64)
    upper = np.array([screen[0] - 1.0, screen[1] - 1.0])
    return np.clip(xy, [0.0, 0.0], upper)


def gaze_error_px(gaze_xy: np.ndarray, target_xy: np.ndarray) -> float:
    """Euclidean distance between a gaze estimate and its target, in pixels."""
    diff = np.asarray(gaze_xy, dtype=np.float64) - np.asarray(target_xy, dtype=np.float64)
    return float(np.linalg.norm(diff))


def calibration_rmse(
    coeffs: np.ndarray,
    samples: list[tuple[np.ndarray, np.ndarray]],
    screen: tuple[float, float],
) -> float:
    """Root-mean-square pixel error of the fit over the given samples."""
    if not samples:
        raise ValueError("no samples")
    err2 = [
        float(np.sum((map_gaze(coeffs, f, screen) - np.asarray(t)) ** 2))
        for f, t in samples
    ]
    return float(np.sqrt(np.mean(err2)))
