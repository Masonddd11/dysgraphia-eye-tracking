"""MediaPipe FaceMesh landmark extraction: iris features, head pose, blinks.

Produces the per-frame feature vector consumed by ``gaze``/``switching``:

- Iris offsets: each iris centre offset from the eye-corner midpoint,
  normalised by eye width (robust to distance/head motion).
- Head pose: solvePnP against a generic 3D face model. The pitch contract
  is ``pitch_down_deg`` — POSITIVE means nose-down (looking toward the
  desk), which is the signal the paper-switch detector thresholds on.
"""

from __future__ import annotations

import os

os.environ.setdefault("GLOG_minloglevel", "3")  # silence absl logging before import

from dataclasses import dataclass  # noqa: E402

import cv2  # noqa: E402
import mediapipe as mp  # noqa: E402
import numpy as np  # noqa: E402

# Landmark IDs (468-point mesh + 10 iris points with refine_landmarks=True).
_IRIS_R, _IRIS_L = 468, 473
_R_OUT, _R_IN = 33, 133
_L_IN, _L_OUT = 362, 263
_R_LID_TOP, _R_LID_BOT = 159, 145
_L_LID_TOP, _L_LID_BOT = 386, 374

# Generic 3D face model (classic solvePnP approximation), paired with
# landmark IDs (1, 152, 33, 263, 61, 291). Only Y/Z geometry affects the
# pitch contract, which is invariant to the horizontal mirroring we apply.
_MODEL_POINTS = np.array(
    [
        (0.0, 0.0, 0.0),  # nose tip
        (0.0, -330.0, -65.0),  # chin
        (-225.0, 170.0, -135.0),  # eye outer 33
        (225.0, 170.0, -135.0),  # eye outer 263
        (-150.0, -150.0, -125.0),  # mouth corner 61
        (150.0, -150.0, -125.0),  # mouth corner 291
    ],
    dtype=np.float64,
)
_POSE_IDS = (1, 152, 33, 263, 61, 291)
# No plausible writing posture exceeds this; larger solvePnP outputs are landmark glitches.
_MAX_PLAUSIBLE_POSE_DEG = 60.0


@dataclass
class FrameResult:
    ok: bool
    ts: float  # perf_counter seconds at frame grab
    features: np.ndarray | None  # (6,) gaze feature vector, None if no face
    pitch_down_deg: float  # positive = nose down (toward desk)
    yaw_deg: float
    roll_deg: float
    ear: float  # mean eye aspect ratio
    blink: bool
    iris_px: tuple[float, float, float, float]  # r_x, r_y, l_x, l_y in frame px


def _wrap_deg(angle: float) -> float:
    return (angle + 180.0) % 360.0 - 180.0


def _head_pose(image_points: np.ndarray, w: int, h: int) -> tuple[float, float, float]:
    focal = float(w)
    k = np.array(
        [[focal, 0.0, w / 2.0], [0.0, focal, h / 2.0], [0.0, 0.0, 1.0]], dtype=np.float64
    )
    ok, rvec, _ = cv2.solvePnP(
        _MODEL_POINTS, image_points, k, None, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not ok:
        return 0.0, 0.0, 0.0
    rot, _ = cv2.Rodrigues(rvec)
    alpha = np.degrees(np.arctan2(rot[2, 1], rot[2, 2]))
    # Neutral head pose sits at alpha ~= +/-180 (model Y/Z flip vs camera);
    # shifting by 180 maps nose-down rotations to positive degrees.
    pitch_down = _wrap_deg(180.0 + alpha)
    yaw = np.degrees(np.arctan2(-rot[2, 0], np.hypot(rot[2, 1], rot[2, 2])))
    roll = np.degrees(np.arctan2(rot[1, 0], rot[0, 0]))
    return float(pitch_down), float(yaw), float(roll)


class FaceTracker:
    """Wraps legacy FaceMesh; expects a horizontally mirrored BGR frame."""

    def __init__(self) -> None:
        self._mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, bgr: np.ndarray, ts: float) -> FrameResult:
        h, w = bgr.shape[:2]
        res = self._mesh.process(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        empty = FrameResult(False, ts, None, 0.0, 0.0, 0.0, 0.0, False, (0.0, 0.0, 0.0, 0.0))
        if not res.multi_face_landmarks:
            return empty
        lm = res.multi_face_landmarks[0].landmark

        def px(i: int) -> np.ndarray:
            return np.array([lm[i].x * w, lm[i].y * h])

        # Iris offsets normalised by eye width.
        r_out, r_in, l_in, l_out = px(_R_OUT), px(_R_IN), px(_L_IN), px(_L_OUT)
        r_w = float(np.linalg.norm(r_in - r_out))
        l_w = float(np.linalg.norm(l_out - l_in))
        if r_w < 1e-6 or l_w < 1e-6:
            return empty
        r_c, l_c = (r_out + r_in) / 2.0, (l_in + l_out) / 2.0
        r_off, l_off = (px(_IRIS_R) - r_c) / r_w, (px(_IRIS_L) - l_c) / l_w

        # Eye aspect ratio (mean of both eyes).
        ear_r = float(np.linalg.norm(px(_R_LID_TOP) - px(_R_LID_BOT))) / r_w
        ear_l = float(np.linalg.norm(px(_L_LID_TOP) - px(_L_LID_BOT))) / l_w
        ear = (ear_r + ear_l) / 2.0

        pitch, yaw, roll = _head_pose(np.array([px(i) for i in _POSE_IDS], dtype=np.float64), w, h)
        if max(abs(pitch), abs(yaw), abs(roll)) > _MAX_PLAUSIBLE_POSE_DEG:
            return empty
        features = np.array([r_off[0], r_off[1], l_off[0], l_off[1], pitch, yaw])
        iris_px = (float(px(_IRIS_R)[0]), float(px(_IRIS_R)[1]), float(px(_IRIS_L)[0]), float(px(_IRIS_L)[1]))
        return FrameResult(True, ts, features, pitch, yaw, roll, ear, ear < 0.18, iris_px)

    def close(self) -> None:
        self._mesh.close()
