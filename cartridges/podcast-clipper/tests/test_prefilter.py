import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clipper.prefilter import prefilter, score_window


def _t(words=30, dur=30.0):
    text = "What is the biggest mistake people make with money? "
    return text * 3, ["w"] * words, dur


def test_hook_words_boost():
    text, words, dur = _t()
    s, reasons = score_window(text, words, dur, 100, 1000, 30)
    assert s > 2
    assert any("hooks" in r for r in reasons)


def test_question_boost():
    s, _ = score_window("Why is this true? " * 5, ["w"] * 20, 25.0, 100, 1000, 30)
    assert s >= 2.0


def test_edge_penalty():
    s_edge, _ = score_window(
        "plain statement here. " * 8, ["w"] * 30, 30.0, 5, 1000, 30
    )
    s_mid, _ = score_window(
        "plain statement here. " * 8, ["w"] * 30, 30.0, 500, 1000, 30
    )
    assert s_edge < s_mid


def test_prefilter_windows():
    segs = [
        {
            "start": float(i * 5),
            "end": float(i * 5 + 5),
            "text": f"Segment number {i} talking about money secrets.",
            "words": [{"start": float(i * 5), "end": float(i * 5 + 1), "w": "hi"}],
        }
        for i in range(20)
    ]
    out = prefilter(
        {"segments": segs},
        {
            "prefilter": {
                "min_clip_s": 20,
                "max_clip_s": 70,
                "max_candidates": 5,
                "skip_intro_outro_s": 0,
            }
        },
    )
    assert 1 <= len(out) <= 5
    assert all(o["dur"] >= 20 for o in out)
    assert all("words" in o and o["words"] for o in out)
