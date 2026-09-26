import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from clipper.settings_schema import (
    SETTABLE,
    apply_overrides,
    format_schema,
    parse_override,
    set_in,
    validate,
)


def test_validate_enum():
    assert validate("clips.layout", "fit")[0] is True
    assert validate("clips.layout", "FIT")[1] == "fit"
    ok, msg, _ = validate("clips.layout", "wide")
    assert ok is False and "auto|crop|fit" in msg


def test_validate_bool():
    for v in ("true", "1", "yes", "on"):
        assert validate("clips.smart_crop", v)[2] is True
    for v in ("false", "0", "no", "off"):
        assert validate("clips.loudnorm", v)[2] is False
    assert validate("clips.smart_crop", "maybe")[0] is False


def test_validate_int_range():
    assert validate("clips.crf", "18")[2] == 18
    assert validate("clips.crf", "99")[0] is False
    assert validate("clips.crf", "abc")[0] is False
    assert validate("download.max_duration_s", "59")[0] is False


def test_validate_float():
    assert validate("clips.fit_ratio", "2.5")[2] == 2.5
    assert validate("clips.fit_ratio", "9")[0] is False


def test_validate_sampling_keys():
    assert validate("nine_router.temperature", "0")[2] == 0.0
    assert validate("nine_router.temperature", "0.7")[2] == 0.7
    assert validate("nine_router.temperature", "1.5")[0] is False
    assert validate("nine_router.seed", "42")[2] == 42
    assert validate("nine_router.seed", "-1")[0] is False


def test_validate_follow_keys():
    assert validate("clips.follow_speaker", "yes")[2] is True
    assert validate("clips.scene_thresh", "0.2")[2] == 0.2
    assert validate("clips.scene_thresh", "0.9")[0] is False
    assert validate("clips.follow_fps", "2")[2] == 2.0
    assert validate("clips.follow_fps", "9")[0] is False


def test_validate_str():
    assert validate("nine_router.rank_model", "gpt-oss:120b")[2] == "gpt-oss:120b"
    assert validate("nine_router.rank_model", "")[0] is False


def test_read_only_keys_rejected():
    for key in ("paths.work_dir", "nine_router.base_url", "clips.default_style", "config_version"):
        ok, msg, _ = validate(key, "x")
        assert ok is False, key
        assert "not settable" in msg


def test_cross_field_min_max():
    st = {"prefilter": {"min_clip_s": 20, "max_clip_s": 70}}
    assert validate("prefilter.min_clip_s", "80", st)[0] is False
    assert validate("prefilter.min_clip_s", "30", st)[0] is True
    assert validate("prefilter.max_clip_s", "10", st)[0] is False
    assert validate("prefilter.max_clip_s", "90", st)[0] is True


def test_parse_override():
    assert parse_override("clips.layout=fit") == ("clips.layout", "fit")
    with pytest.raises(ValueError, match="expected section.key=value"):
        parse_override("clips.layout")
    with pytest.raises(ValueError):
        parse_override("clips.layout=wide")


def test_apply_overrides_and_set_in():
    d = {"clips": {"crf": 20}}
    set_in(d, "clips.layout", "fit")
    assert d["clips"] == {"crf": 20, "layout": "fit"}
    apply_overrides(d, {"clips.loudnorm": True, "prefilter.min_clip_s": 15})
    assert d["clips"]["loudnorm"] is True
    assert d["prefilter"]["min_clip_s"] == 15


def test_format_schema_lists_all():
    text = format_schema()
    for key in SETTABLE:
        assert key in text
