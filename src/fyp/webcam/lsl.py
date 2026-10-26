"""LSL outlets for the webcam-derived streams (V1 stream-quality baseline).

Streams published:

- ``FYP_WebcamGaze``   (Gaze, 4ch float32, ~60Hz): x_px, y_px, confidence, blink.
  Uncalibrated/no-face frames carry (-1, -1, confidence=0, blink).
- ``FYP_WebcamHeadPose`` (HeadPose, 3ch float32, ~60Hz): pitch_down_deg, yaw_deg, roll_deg.
- ``FYP_WordIndex`` (GazeWord, 1ch float32, ~60Hz): index of the word the
  smoothed gaze estimate falls in; -1 when gaze is invalid or off-paragraph.
- ``FYP_SwitchEvents``  (Markers, 1ch float32, irregular): committed attention
  state transitions (0=MONITOR, 1=PAPER).
"""

from __future__ import annotations

import pylsl

_GAZE_NAME = "FYP_WebcamGaze"
_HEAD_NAME = "FYP_WebcamHeadPose"
_WORD_NAME = "FYP_WordIndex"
_EVENT_NAME = "FYP_SwitchEvents"


class WebcamOutlets:
    def __init__(self) -> None:
        self.gaze = pylsl.StreamOutlet(
            pylsl.StreamInfo(_GAZE_NAME, "Gaze", 4, 60, pylsl.cf_float32, "fyp-webcam-gaze")
        )
        self.head = pylsl.StreamOutlet(
            pylsl.StreamInfo(_HEAD_NAME, "HeadPose", 3, 60, pylsl.cf_float32, "fyp-webcam-head")
        )
        self.word = pylsl.StreamOutlet(
            pylsl.StreamInfo(_WORD_NAME, "GazeWord", 1, 60, pylsl.cf_float32, "fyp-webcam-word")
        )
        self.events = pylsl.StreamOutlet(
            pylsl.StreamInfo(_EVENT_NAME, "Markers", 1, pylsl.IRREGULAR_RATE, pylsl.cf_float32, "fyp-webcam-switch")
        )

    def push_gaze(self, x_px: float, y_px: float, confidence: float, blink: float) -> None:
        self.gaze.push_sample([x_px, y_px, confidence, blink], pylsl.local_clock())

    def push_head(self, pitch_down_deg: float, yaw_deg: float, roll_deg: float) -> None:
        self.head.push_sample([pitch_down_deg, yaw_deg, roll_deg], pylsl.local_clock())

    def push_word(self, word_index: int) -> None:
        self.word.push_sample([float(word_index)], pylsl.local_clock())

    def push_event(self, state: int) -> None:
        self.events.push_sample([float(state)], pylsl.local_clock())
