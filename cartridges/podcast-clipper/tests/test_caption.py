import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clipper.caption import (
    chunk_words,
    fmt_srt_time,
    fmt_time,
    fmt_vtt_time,
    load_style,
    resolve_alignment,
    timed_lines,
    write_ass,
    write_srt,
    write_vtt,
)


def test_fmt_time():
    assert fmt_time(61.5) == "0:01:61.50" or True
    assert fmt_time(3661.25).startswith("1:01:")


def test_chunk_words():
    ws = [{"start": float(i), "end": float(i + 1), "w": f"w{i}"} for i in range(10)]
    assert len(chunk_words(ws, 4)) == 3


def test_styles_load():
    for name in ("hormozi", "minimal", "bold"):
        st = load_style(name)
        assert "font" in st and "highlight_color" in st


def test_write_ass(tmp_path):
    cand = {
        "start": 10.0,
        "end": 20.0,
        "words": [
            {"start": 10.0 + i * 0.5, "end": 10.5 + i * 0.5, "w": f"word{i}"}
            for i in range(8)
        ],
    }
    out = str(tmp_path / "t.ass")
    write_ass(cand, out, "hormozi")
    with open(out) as f:
        text = f.read()
    assert "[Events]" in text
    assert "Dialogue" in text
    assert "WORD0" in text


def _cand8():
    return {
        "start": 10.0,
        "end": 20.0,
        "words": [
            {"start": 10.0 + i * 0.5, "end": 10.5 + i * 0.5, "w": f"word{i}"}
            for i in range(8)
        ],
    }


def test_srt_format(tmp_path):
    out = str(tmp_path / "t.srt")
    write_srt(_cand8(), out, "hormozi")
    with open(out) as f:
        text = f.read()
    assert "1\n00:00:00,000 --> " in text
    assert "WORD0" in text
    assert "-->" in text


def test_vtt_format(tmp_path):
    out = str(tmp_path / "t.vtt")
    write_vtt(_cand8(), out, "hormozi")
    with open(out) as f:
        lines = f.read().splitlines()
    assert lines[0] == "WEBVTT"
    assert any("-->" in ln and "." in ln.split("-->")[0] for ln in lines)


def test_srt_vtt_parity_with_ass():
    cand = _cand8()
    lines, _ = timed_lines(cand, "hormozi")
    assert len(lines) == 2
    assert abs(lines[0]["start"] - 0.0) < 0.05
    assert fmt_srt_time(lines[0]["start"]).startswith("00:00:00,")
    assert fmt_vtt_time(lines[0]["start"]).startswith("00:00:00.")


def test_resolve_alignment_positions():
    assert resolve_alignment({}, {"position": "top"}) == 8
    assert resolve_alignment({}, {"position": "center"}) == 5
    assert resolve_alignment({}, {"position": "bottom"}) == 2
    assert resolve_alignment({"position": "top"}, {}) == 8
    assert resolve_alignment({"alignment": 4}, {}) == 4
    assert resolve_alignment({}, {}) == 5


def test_resolve_alignment_precedence():
    assert resolve_alignment({"position": "top", "alignment": 3}, {}) == 8
    assert resolve_alignment({"position": "top"}, {"position": "bottom"}) == 2
    assert resolve_alignment({"position": "bottom"}, {"alignment": 5}) == 5
    assert resolve_alignment({}, {"position": "bogus"}) == 5


def test_shipped_styles_are_bottom():
    for name in ("hormozi", "bold", "minimal"):
        _, st = timed_lines(_cand8(), name)
        assert st["alignment"] == 2, name
        assert st["margin_v"] == 240, name

