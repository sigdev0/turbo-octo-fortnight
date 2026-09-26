import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipper.pipeline as P

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.mp4")


def _words(start, n, step=0.5):
    return [{"start": start + i * step, "end": start + i * step + 0.4, "w": f"w{i}"} for i in range(n)]


def _transcript():
    segs = []
    for i in range(12):
        s = float(i * 5)
        segs.append({
            "start": s,
            "end": s + 5.0,
            "text": f"Why is money the biggest secret? Segment {i} never miss this!",
            "words": _words(s, 6),
        })
    return {"segments": segs, "lang": "en", "backend": "mock"}


def _ranked():
    return [
        {
            "id": 0,
            "start": 5.0,
            "end": 50.0,
            "dur": 45.0,
            "text": "Why is money the biggest secret?",
            "words": _words(5.0, 20),
            "prefilter_score": 9.0,
            "signals": ["question"],
            "score": 90,
            "hook": "Why is money the biggest secret?",
            "reason": "question + hooks",
            "title": "Why Money Secrets Matter",
            "description": "A practical take. #shorts #money",
            "thumbnail_s": 3.0,
        }
    ]


def _settings(tmp_path):
    return {
        "paths": {"work_dir": str(tmp_path / "work"), "output_dir": str(tmp_path / "out")},
        "prefilter": {"min_clip_s": 20, "max_clip_s": 70, "max_candidates": 5, "skip_intro_outro_s": 0},
        "clips": {
            "default_style": "minimal",
            "max_clips": 1,
            "width": 360,
            "height": 640,
            "sidecars": ["ass", "srt", "vtt"],
        },
        "nine_router": {"rank_model": "mock", "max_tokens": 100},
    }


def test_process_offline_full(tmp_path, monkeypatch):
    import shutil

    import clipper.rank as RK

    settings = _settings(tmp_path)
    work = tmp_path / "work" / "job"
    work.mkdir(parents=True)
    shutil.copy(FIXTURE, work / "vid.source.mp4")

    monkeypatch.setattr(
        P, "download",
        lambda url, wd, s: {
            "id": "vid", "title": "t", "duration": 60,
            "source": str(work / "vid.source.mp4"),
            "audio": str(work / "vid.audio.wav"),
        },
    )
    import clipper.transcribe as TR

    monkeypatch.setattr(TR, "transcribe_groq", lambda a, s: _transcript())
    monkeypatch.setattr(
        RK, "call_9router",
        lambda msgs, s, model=None: {
            "choices": [{"message": {"content": '[{"id": 0, "score": 90, "hook": "h", "reason": "r", "title": "Why Money Secrets Matter", "description": "d #a", "thumbnail_s": 3.0}]'}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
    )
    monkeypatch.setattr(P, "COSTS_LOG", str(tmp_path / "costs.jsonl"))

    res = P.process("https://youtu.be/mock", settings, name="job", max_clips=1)
    assert len(res["clips"]) == 1
    m = res["clips"][0]
    for key in ("clip", "ass", "srt", "vtt", "meta", "thumb"):
        assert m.get(key) and os.path.exists(m[key]), key
    assert os.path.getsize(m["clip"]) > 100_000
    with open(m["meta"]) as f:
        meta = json.load(f)
    assert meta["title"] == "Why Money Secrets Matter"
    with open(m["srt"]) as f:
        assert len(f.read()) > 50
    with open(m["vtt"]) as f:
        assert f.read().startswith("WEBVTT")
    assert os.path.exists(tmp_path / "work" / "job" / "transcript.json")
    assert os.path.exists(tmp_path / "work" / "job" / "ranked.json")


def test_process_offline_prefilter_rank_path(tmp_path, monkeypatch):
    import clipper.rank as RK

    settings = _settings(tmp_path)
    t = _transcript()
    from clipper.prefilter import prefilter

    cands = prefilter(t, settings)
    assert 1 <= len(cands) <= 5
    monkeypatch.setattr(
        RK, "call_9router",
        lambda msgs, s, model=None: {
            "choices": [{"message": {"content": json.dumps([
                {"id": c["id"], "score": 80, "hook": "h", "reason": "r",
                 "title": "T", "description": "d", "thumbnail_s": 1.0}
                for c in cands
            ])}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
    )
    ranked, rmeta = RK.rank(cands, settings)
    assert len(ranked) >= 1
    assert rmeta["total_tokens"] == 2
    assert ranked[0]["title"] == "T"
