import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

import clipper.transcribe as T


class _Result:
    def __init__(self, stderr):
        self.stderr = stderr


def test_probe_duration_over_an_hour(monkeypatch):
    monkeypatch.setattr(
        T.subprocess, "run", lambda *a, **k: _Result("  Duration: 01:32:15.12, start: 0")
    )
    assert T._probe_duration("x") == 1 * 3600 + 32 * 60 + 15.12


def test_probe_duration_under_an_hour(monkeypatch):
    monkeypatch.setattr(
        T.subprocess, "run", lambda *a, **k: _Result("Duration: 00:39:25.00, bitrate: 1")
    )
    assert T._probe_duration("x") == 39 * 60 + 25.0


def test_probe_duration_missing(monkeypatch):
    monkeypatch.setattr(T.subprocess, "run", lambda *a, **k: _Result("no duration here"))
    with pytest.raises(RuntimeError):
        T._probe_duration("x")


def test_split_audio_chunks_a_90_minute_file(monkeypatch, tmp_path):
    def fake_run(cmd, *a, **k):
        return _Result("Duration: 01:32:15.00, start: 0")

    monkeypatch.setattr(T.subprocess, "run", fake_run)
    chunks = T._split_audio("in.wav", str(tmp_path), chunk_sec=300)
    assert len(chunks) == 19
    assert chunks[0]["offset"] == 0.0
    assert chunks[-1]["offset"] == 18 * 300
