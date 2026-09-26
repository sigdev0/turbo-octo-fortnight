import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipper.pipeline as P


def _settings():
    return {"paths": {"work_dir": "work", "output_dir": "output"}}


def test_batch_continues_on_error(tmp_path, monkeypatch):
    src = tmp_path / "sources.yaml"
    src.write_text(
        "sources:\n"
        "  - url: https://youtu.be/ok1\n    name: ep1\n"
        "  - url: https://youtu.be/bad\n    name: ep2\n"
        "  - url: https://youtu.be/ok2\n    name: ep3\n"
    )
    calls = []

    def fake_process(url, settings, **kw):
        calls.append(url)
        if "bad" in url:
            raise RuntimeError("boom")
        return {"clips": [{"clip": "x.mp4"}]}

    monkeypatch.setattr(P, "process", fake_process)
    res = P.batch(_settings(), sources_path=str(src))
    assert [o["name"] for o in res["ok"]] == ["ep1", "ep3"]
    assert [f["name"] for f in res["failed"]] == ["ep2"]
    assert len(calls) == 3


def test_batch_empty_sources(tmp_path):
    src = tmp_path / "sources.yaml"
    src.write_text("sources: []\n")
    res = P.batch(_settings(), sources_path=str(src))
    assert res == {"ok": [], "failed": []}


def test_batch_applies_per_source_layout(tmp_path, monkeypatch):
    src = tmp_path / "sources.yaml"
    src.write_text(
        "sources:\n"
        "  - url: https://youtu.be/a\n    layout: fit\n"
        "  - url: https://youtu.be/b\n    follow_speaker: true\n"
        "  - url: https://youtu.be/c\n    overrides:\n      clips.crf: 18\n"
    )
    seen = {}

    def fake_process(url, settings, **kw):
        seen[url] = kw.get("overrides")
        return {"clips": []}

    monkeypatch.setattr(P, "process", fake_process)
    P.batch(_settings(), sources_path=str(src), overrides={"clips.max_clips": 2})
    assert seen["https://youtu.be/a"]["clips.layout"] == "fit"
    assert seen["https://youtu.be/a"]["clips.max_clips"] == 2
    assert seen["https://youtu.be/b"]["clips.follow_speaker"] is True
    assert seen["https://youtu.be/c"]["clips.crf"] == 18
    assert seen["https://youtu.be/c"]["clips.max_clips"] == 2
