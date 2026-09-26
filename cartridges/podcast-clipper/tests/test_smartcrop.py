import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipper.smartcrop as S


def test_smooth_x_median():
    assert S.smooth_x([0.2, 0.2, 0.2]) == 0.2
    assert S.smooth_x([]) == 0.5


def test_smooth_x_conservative():
    assert S.smooth_x([0.51, 0.49, 0.5]) == 0.5
    assert S.smooth_x([0.62, 0.64, 0.63, 0.65, 0.61]) == 0.63
    assert S.smooth_x([0.88, 0.9, 0.89, 0.87]) > 0.8


def test_smooth_x_area_weighted_pip():
    weighted = [
        (0.51, 0.015), (0.45, 0.003), (0.55, 0.003), (0.50, 0.015),
        (0.13, 0.006), (0.13, 0.006), (0.12, 0.006),
        (0.13, 0.006), (0.12, 0.006), (0.11, 0.006),
    ]
    assert S.smooth_x(weighted) == 0.5


def test_smart_cx_off_by_default():
    assert S.smart_cx("nope.mp4", 0, 10, {"clips": {}}) is None
    assert S.smart_cx("nope.mp4", 0, 10, {}) is None


def test_smart_cx_failure_falls_back(monkeypatch):
    monkeypatch.setattr(S, "sample_frames", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    assert S.smart_cx("s.mp4", 0, 10, {"clips": {"smart_crop": True}}) is None
