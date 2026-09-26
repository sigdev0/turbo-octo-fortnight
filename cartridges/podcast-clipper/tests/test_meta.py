import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipper.clip as C


def _ranked():
    return [
        {
            "id": 0,
            "start": 10.0,
            "end": 50.0,
            "score": 85,
            "hook": "Hook here",
            "reason": "r",
            "title": "Why Money Secrets Matter More Than You Think Ever",
            "description": "A practical take. #shorts #money #podcast",
            "thumbnail_s": 5.0,
            "words": [{"start": 10.0 + i, "end": 10.5 + i, "w": f"w{i}"} for i in range(6)],
        }
    ]


def test_meta_json_written(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "make_clip", lambda *a, **k: a[3])
    called = {}

    class FakeRun:
        def __call__(self, *a, **k):
            called["cmd"] = a[0]
            with open(os.path.join(str(tmp_path), "t.jpg"), "wb") as f:
                f.write(b"x")
            return type("R", (), {})()

    monkeypatch.setattr(C.subprocess, "run", FakeRun())
    out = str(tmp_path)
    made = C.cut_clips("src.mp4", _ranked(), out, {"clips": {}}, style="minimal", max_clips=1)
    assert len(made) == 1
    m = made[0]
    assert m["thumb"] is not None and m["thumb"].endswith(".thumb.jpg")
    with open(m["meta"]) as f:
        meta = json.load(f)
    assert len(meta["title"]) <= 60
    assert meta["thumbnail_s"] == 5.0
    assert "#shorts" in meta["description"]
    assert os.path.exists(m["srt"]) and os.path.exists(m["vtt"])


def test_thumb_none_on_ffmpeg_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "make_clip", lambda *a, **k: a[3])

    def boom(*a, **k):
        raise C.subprocess.CalledProcessError(1, "ffmpeg")

    monkeypatch.setattr(C.subprocess, "run", boom)
    made = C.cut_clips("src.mp4", _ranked(), str(tmp_path), {"clips": {}}, max_clips=1)
    assert made[0]["thumb"] is None
    assert os.path.exists(made[0]["meta"])
