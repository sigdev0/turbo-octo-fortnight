import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from clipper.caption import timed_lines
from clipper.pipeline import apply_preset, list_presets


def _settings():
    return {"clips": {"width": 1080, "height": 1920, "crf": 20, "default_style": "hormozi"}}


def test_list_presets():
    names = list_presets()
    assert {"shorts", "tiktok", "reels"} <= set(names)


def test_apply_preset_unknown():
    with pytest.raises(ValueError, match="unknown preset"):
        apply_preset(_settings(), "bogus")


def test_apply_preset_tiktok_overrides():
    s = apply_preset(_settings(), "tiktok")
    assert s["clips"]["crf"] == 18
    assert s["_caption_overrides"]["margin_v"] == 520
    assert s["_caption_overrides"]["position"] == "bottom"
    assert s["_preset"] == "tiktok"


def test_apply_preset_none_passthrough():
    s = _settings()
    assert apply_preset(s, None) is s


def _cand():
    return {
        "start": 0.0,
        "end": 10.0,
        "words": [
            {"start": i * 0.5, "end": i * 0.5 + 0.4, "w": f"w{i}"} for i in range(6)
        ],
    }


def test_caption_overrides_margin_and_size():
    _, st_plain = timed_lines(_cand(), "hormozi")
    _, st_ov = timed_lines(_cand(), "hormozi", overrides={"margin_v": 650, "size_scale": 0.9})
    assert st_ov["margin_v"] == 650
    assert st_ov["size"] == round(st_plain["size"] * 0.9)


def test_preset_resolves_bottom_alignment():
    for name, margin in (("shorts", 200), ("reels", 380), ("tiktok", 520)):
        s = apply_preset(_settings(), name)
        _, st = timed_lines(_cand(), "hormozi", overrides=s["_caption_overrides"])
        assert st["alignment"] == 2
        assert st["margin_v"] == margin

