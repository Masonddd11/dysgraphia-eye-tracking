"""OpenGaze (Gazepoint) XML protocol: message builders + record parsers.

Pure functions (stdlib only) so the wire format is testable offline; the
socket I/O lives in ``client.py``.

Wire format (OpenGaze API v2.0): each record is a single XML element
delimited by CRLF. The client sends ``<SET ID="..." ... />`` or
``<GET ID="..." />``; the server replies ``<ACK ... />`` / ``<NACK ... />``
and streams ``<CAL ... />`` (calibration) and ``<REC ... />`` (data) records.
Point-of-gaze coordinates are fractions of the screen: (0,0) is top-left,
(0.5,0.5) centre, (1,1) bottom-right.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.etree import ElementTree

ACK = "ACK"
NACK = "NACK"
CAL = "CAL"
REC = "REC"


@dataclass(frozen=True)
class Record:
    tag: str  # ACK | NACK | CAL | REC
    cmd_id: str | None  # ID attribute (None for REC)
    attrs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GazePoint:
    x_px: float
    y_px: float
    valid: bool
    pupil_diameter_px: float  # mean of LPD/RPD; NaN when neither present
    time_s: float | None  # device TIME, if enabled


def format_command(action: str, cmd_id: str, **params) -> str:
    """Build a client -> server XML command, CRLF-terminated."""
    parts = [f'<{action.upper()} ID="{cmd_id.upper()}"']
    parts += [f'{key.upper()}="{value}"' for key, value in params.items()]
    return " ".join(parts) + " />\r\n"


def parse_record(xml: str) -> Record:
    """Parse one XML record element; tag, ID and attribute keys are upper-cased."""
    elem = ElementTree.fromstring(xml.strip())
    attrs = {key.upper(): value for key, value in elem.attrib.items()}
    raw_id = attrs.get("ID")
    cmd_id = raw_id.upper() if raw_id is not None else None
    return Record(tag=elem.tag.upper(), cmd_id=cmd_id, attrs=attrs)


def parse_gaze(rec: Record, screen_w: float, screen_h: float) -> GazePoint | None:
    """Best-eye POG (BPOGX/Y) -> pixel gaze; None if the fields are absent.

    Validity is BPOGV (1=valid). Pupil diameter is the mean of the available
    eye diameters (LPD/RPD), NaN when neither is present.
    """
    if rec.tag != REC:
        return None
    attrs = rec.attrs
    if "BPOGX" not in attrs or "BPOGY" not in attrs:
        return None
    x_px = float(attrs["BPOGX"]) * screen_w
    y_px = float(attrs["BPOGY"]) * screen_h
    valid = attrs.get("BPOGV", "1") == "1"
    pupil = _mean_pupil(attrs)
    time_s = float(attrs["TIME"]) if "TIME" in attrs else None
    return GazePoint(x_px=x_px, y_px=y_px, valid=valid, pupil_diameter_px=pupil, time_s=time_s)


def _mean_pupil(attrs: dict[str, str]) -> float:
    diameters = []
    for key in ("LPD", "RPD"):
        if key in attrs:
            try:
                diameters.append(float(attrs[key]))
            except ValueError:
                pass
    if not diameters:
        return float("nan")
    return sum(diameters) / len(diameters)


def calibration_summary(rec: Record) -> tuple[float, int] | None:
    """(AVE_ERROR, VALID_POINTS) from a CALIBRATE_RESULT_SUMMARY ACK, else None."""
    if rec.tag != ACK or rec.cmd_id != "CALIBRATE_RESULT_SUMMARY":
        return None
    if "AVE_ERROR" not in rec.attrs or "VALID_POINTS" not in rec.attrs:
        return None
    return float(rec.attrs["AVE_ERROR"]), int(float(rec.attrs["VALID_POINTS"]))


def screen_size(rec: Record) -> tuple[int, int] | None:
    """(WIDTH, HEIGHT) pixels from a SCREEN_SIZE ACK, else None."""
    if rec.tag != ACK or rec.cmd_id != "SCREEN_SIZE":
        return None
    if "WIDTH" not in rec.attrs or "HEIGHT" not in rec.attrs:
        return None
    return int(float(rec.attrs["WIDTH"])), int(float(rec.attrs["HEIGHT"]))
