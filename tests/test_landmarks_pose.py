"""Offline tests for solvePnP head-pose extraction (no camera needed).

Projects the generic 3D face model with known rotations and asserts the
extracted angles. The physical sign contract (positive pitch = nose down)
is validated up to the model's axis conventions here; live confirmation
happens via the preview HUD.
"""

import cv2
import numpy as np

from fyp.webcam.landmarks import _MODEL_POINTS, _head_pose

W, H = 1280, 720
K = np.array([[float(W), 0.0, W / 2.0], [0.0, float(W), H / 2.0], [0.0, 0.0, 1.0]])
TVEC = np.array([[0.0], [0.0], [1000.0]])


def _projected_points(rvec: np.ndarray) -> np.ndarray:
    pts, _ = cv2.projectPoints(_MODEL_POINTS, rvec, TVEC, K, None)
    return pts.reshape(-1, 2).astype(np.float64)


def test_neutral_head_pose_reads_near_zero():
    rvec = np.array([np.pi, 0.0, 0.0])  # real neutral: RotX(pi) vs camera axes
    pitch, yaw, roll = _head_pose(_projected_points(rvec), W, H)
    assert abs(pitch) < 0.5
    assert abs(yaw) < 0.5
    assert abs(roll) < 0.5


def test_pitch_symmetric_and_wraps_cleanly():
    for theta_deg, expected in ((10.0, 10.0), (-10.0, -10.0), (45.0, 45.0)):
        rvec = np.array([np.pi + np.radians(theta_deg), 0.0, 0.0])
        pitch, _, _ = _head_pose(_projected_points(rvec), W, H)
        assert abs(pitch - expected) < 0.5, f"theta={theta_deg} got {pitch}"


def test_yaw_and_roll_extracted():
    def rot(rvec: list[float]) -> np.ndarray:
        matrix, _ = cv2.Rodrigues(np.asarray(rvec, dtype=np.float64))
        return matrix

    composed = rot([0.0, 0.0, np.radians(15.0)]) @ rot([np.pi, 0.0, 0.0])
    rvec, _ = cv2.Rodrigues(composed)
    _, _, roll = _head_pose(_projected_points(rvec), W, H)
    assert abs(roll - 15.0) < 0.5
