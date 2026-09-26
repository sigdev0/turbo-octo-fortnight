import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipper.pipeline as P
import clipper.rank as R


def test_parse_usage_meta():
    resp = {"usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}
    usage = resp.get("usage") or {}
    assert usage["total_tokens"] == 15


def test_log_cost_appends_jsonl(tmp_path, monkeypatch):
    log = tmp_path / "costs.jsonl"
    monkeypatch.setattr(P, "COSTS_LOG", str(log))
    P._log_cost({"ts": "2026-09-01T00:00:00", "name": "ep1"})
    P._log_cost({"ts": "2026-09-01T00:01:00", "name": "ep2"})
    lines = log.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["name"] == "ep1"


def test_rank_returns_meta(monkeypatch):
    settings = {"nine_router": {"rank_model": "m", "max_tokens": 100}}
    monkeypatch.setattr(R, "call_9router", lambda msgs, s, model=None: {
        "choices": [{"message": {"content": '[{"id": 0, "score": 90, "hook": "h", "reason": "r"}]'}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    })
    cands = [{"id": 0, "start": 0.0, "end": 30.0, "text": "t", "words": []}]
    ranked, meta = R.rank(cands, settings)
    assert ranked[0]["score"] == 90
    assert meta["total_tokens"] == 15
    assert meta["model"] == "m"


def test_rank_custom_out_writes_both(tmp_path, monkeypatch):
    settings = {"nine_router": {"rank_model": "m", "max_tokens": 100}}
    monkeypatch.setattr(R, "call_9router", lambda msgs, s, model=None: {
        "choices": [{"message": {"content": '[{"id": 0, "score": 90, "hook": "h", "reason": "r"}]'}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    })
    cands = [{"id": 0, "start": 0.0, "end": 30.0, "text": "t", "words": []}]
    out = str(tmp_path / "custom.json")
    ranked, _ = R.rank(cands, settings, out_path=out)
    assert len(ranked) == 1
    assert ranked[0]["score"] == 90
    with open(out + ".meta.json") as f:
        assert json.load(f)["total_tokens"] == 2


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._payload


def _capture_body(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode())
        return _FakeResp(b'{"choices": []}')

    monkeypatch.setattr(R.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setenv("NR_KEY", "k")
    return captured


def _router_settings(**extra):
    cfg = {"base_url": "http://x", "api_key_env": "NR_KEY", "rank_model": "m"}
    cfg.update(extra)
    return {"nine_router": cfg}


def test_call_9router_sends_sampling(monkeypatch):
    captured = _capture_body(monkeypatch)
    R.call_9router([{"role": "user", "content": "x"}], _router_settings(temperature=0.0, seed=42))
    assert captured["body"]["temperature"] == 0.0
    assert captured["body"]["seed"] == 42
    assert captured["body"]["stream"] is False


def test_call_9router_omits_unset_sampling(monkeypatch):
    captured = _capture_body(monkeypatch)
    R.call_9router([{"role": "user", "content": "x"}], _router_settings())
    assert "temperature" not in captured["body"]
    assert "seed" not in captured["body"]


def test_rank_meta_records_sampling(monkeypatch):
    settings = _router_settings(temperature=0.0, seed=7)
    monkeypatch.setattr(R, "call_9router", lambda msgs, s, model=None: {
        "choices": [{"message": {"content": '[{"id": 0, "score": 90}]'}}],
        "usage": {},
    })
    cands = [{"id": 0, "start": 0.0, "end": 30.0, "text": "t", "words": []}]
    _, meta = R.rank(cands, settings)
    assert meta["temperature"] == 0.0
    assert meta["seed"] == 7
