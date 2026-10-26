"""Tests for the OpenGaze protocol codec (pure, no hardware)."""

from fyp.gazepoint.protocol import (
    ACK,
    REC,
    calibration_summary,
    format_command,
    parse_gaze,
    parse_record,
    screen_size,
)


def test_format_set_command():
    assert format_command("SET", "ENABLE_SEND_POG_BEST", STATE="1") == (
        '<SET ID="ENABLE_SEND_POG_BEST" STATE="1" />\r\n'
    )


def test_format_get_command_without_params():
    assert format_command("GET", "CALIBRATE_RESULT_SUMMARY") == (
        '<GET ID="CALIBRATE_RESULT_SUMMARY" />\r\n'
    )


def test_format_command_uppercases_action_and_id():
    assert format_command("set", "calibrate_show", STATE=0) == (
        '<SET ID="CALIBRATE_SHOW" STATE="0" />\r\n'
    )


def test_parse_ack_record():
    rec = parse_record('<ACK ID="SCREEN_SIZE" X="0" Y="0" WIDTH="1920" HEIGHT="1080" />')
    assert rec.tag == ACK
    assert rec.cmd_id == "SCREEN_SIZE"
    assert rec.attrs["WIDTH"] == "1920"


def test_parse_rec_record_has_no_id():
    rec = parse_record('<REC BPOGX="0.47175" BPOGY="0.43360" BPOGV="1" />')
    assert rec.tag == REC
    assert rec.cmd_id is None
    assert rec.attrs["BPOGX"] == "0.47175"


def test_parse_record_normalises_case():
    rec = parse_record('<ack id="product_id" value="GP3" />')
    assert rec.tag == ACK
    assert rec.cmd_id == "PRODUCT_ID"
    assert rec.attrs["VALUE"] == "GP3"


def test_parse_gaze_fraction_to_pixels():
    rec = parse_record('<REC BPOGX="0.5" BPOGY="0.25" BPOGV="1" LPD="14.0" RPD="10.0" />')
    gp = parse_gaze(rec, 1920.0, 1080.0)
    assert gp.x_px == 960.0
    assert gp.y_px == 270.0
    assert gp.valid is True
    assert gp.pupil_diameter_px == 12.0


def test_parse_gaze_invalid_flag():
    rec = parse_record('<REC BPOGX="0.5" BPOGY="0.5" BPOGV="0" />')
    gp = parse_gaze(rec, 100.0, 100.0)
    assert gp.valid is False
    assert gp.pupil_diameter_px != gp.pupil_diameter_px  # NaN


def test_parse_gaze_missing_pog_is_none():
    assert parse_gaze(parse_record('<REC CNT="42" />'), 100.0, 100.0) is None


def test_calibration_summary():
    rec = parse_record('<ACK ID="CALIBRATE_RESULT_SUMMARY" AVE_ERROR="19.43" VALID_POINTS="5" />')
    assert calibration_summary(rec) == (19.43, 5)


def test_calibration_summary_wrong_record_is_none():
    assert calibration_summary(parse_record('<ACK ID="PRODUCT_ID" VALUE="GP3" />')) is None


def test_screen_size_ack():
    rec = parse_record('<ACK ID="SCREEN_SIZE" X="0" Y="0" WIDTH="1920" HEIGHT="1080" />')
    assert screen_size(rec) == (1920, 1080)
