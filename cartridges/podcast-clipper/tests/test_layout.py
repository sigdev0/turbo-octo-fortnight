import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clipper.clip import build_vf, pick_layout


def test_pick_layout_auto_wide_uses_fit():
    assert pick_layout({"layout": "auto"}, 1280, 534) == "fit"


def test_pick_layout_auto_normal_uses_crop():
    assert pick_layout({"layout": "auto"}, 1280, 720) == "crop"
    assert pick_layout({}, 1920, 1080) == "crop"


def test_pick_layout_explicit():
    assert pick_layout({"layout": "fit"}, 1280, 720) == "fit"
    assert pick_layout({"layout": "crop"}, 1280, 534) == "crop"
    assert pick_layout({"layout": "bogus"}, 1280, 534) == "crop"


def test_build_vf_fit_chain():
    vf, layout = build_vf({"layout": "fit"}, 1280, 534, 1080, 1920)
    assert layout == "fit"
    assert "split=2" in vf
    assert "gblur=sigma=25" in vf
    assert "overlay=(W-w)/2:(H-h)/2" in vf
    assert "crop=" not in vf or "crop=1080:1920" in vf


def test_build_vf_crop_center():
    vf, layout = build_vf({"layout": "crop"}, 1280, 720, 1080, 1920)
    assert layout == "crop"
    assert vf.startswith("crop=")
    assert vf.endswith("scale=1080:1920")


def test_custom_fit_threshold():
    assert pick_layout({"layout": "auto", "fit_ratio": 3.0}, 1280, 534) == "crop"
    assert pick_layout({"layout": "auto", "fit_ratio": 1.5}, 1280, 720) == "fit"


def test_follow_speaker_forces_crop_under_auto():
    assert pick_layout({"layout": "auto", "follow_speaker": True}, 1280, 534) == "crop"
    assert pick_layout({"follow_speaker": True}, 3840, 1600) == "crop"
    assert pick_layout({"layout": "fit", "follow_speaker": True}, 1280, 534) == "fit"
