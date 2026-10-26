"""LSL outlet for the Gazepoint-derived gaze stream.

Stream published:

- ``FYP_GazePoint`` (Gaze, 4ch float32, ~150Hz): x_px, y_px, valid,
  pupil_diameter_px. Invalid samples carry (-1, -1, 0, pupil) so consumers
  can treat them exactly like the webcam stream's no-face frames.
"""

from __future__ import annotations

import pylsl

_NAME = "FYP_GazePoint"


class GazePointOutlet:
    def __init__(self, nominal_rate: float = 150.0) -> None:
        self.gaze = pylsl.StreamOutlet(
            pylsl.StreamInfo(_NAME, "Gaze", 4, nominal_rate, pylsl.cf_float32, "fyp-gazepoint-gaze")
        )

    def push(
        self,
        x_px: float,
        y_px: float,
        valid: bool,
        pupil_diameter_px: float,
        timestamp: float | None = None,
    ) -> None:
        self.gaze.push_sample(
            [x_px, y_px, float(valid), pupil_diameter_px],
            pylsl.local_clock() if timestamp is None else timestamp,
        )
