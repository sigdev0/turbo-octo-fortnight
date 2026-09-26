import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipbot


def _run(coro):
    return asyncio.run(coro)


def test_video_id_parsing():
    assert clipbot._video_id("https://youtu.be/9kpO8JWJRyg?si=x") == "9kpO8JWJRyg"
    assert (
        clipbot._video_id("https://www.youtube.com/watch?v=G1p4SnUH0bc")
        == "G1p4SnUH0bc"
    )
    assert clipbot._video_id("https://www.youtube.com/channel/UCabc") is None


def test_tokens_drop_stopwords():
    toks = clipbot._tokens("The podcast and the CLIPPING workflow")
    assert "podcast" in toks and "clipping" in toks
    assert "the" not in toks and "and" not in toks


def test_theme_affinity_hits_profile():
    profile = {"keywords": {"clipping": 3.0, "podcast": 2.0}}
    score, hits = clipbot.theme_affinity("How to make podcast clips", profile)
    assert score > 0
    assert "podcast" in hits
    assert clipbot.theme_affinity("unrelated cooking recipe", profile)[0] == 0.0


def test_validate_digest_keys():
    assert clipbot.validate_bot_value("digest_cooldown_days", "14") == (True, 14)
    assert clipbot.validate_bot_value("digest_cooldown_days", "-1")[0] is False
    assert clipbot.validate_bot_value("digest_theme_weight", "1.5") == (True, 1.5)
    assert clipbot.validate_bot_value("digest_theme_weight", "9")[0] is False
    assert clipbot.validate_bot_value("digest_trending_enabled", "false") == (
        True,
        False,
    )
    assert clipbot.validate_bot_value("digest_trending_enabled", "maybe")[0] is False
    assert clipbot.validate_bot_value("digest_top_n", "999")[0] is False


def test_build_theme_profile_and_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(clipbot, "DIGEST_PROFILE_PATH", str(tmp_path / "p.json"))
    monkeypatch.setattr(
        clipbot,
        "_profile_items",
        lambda: [
            ("a", "viral clipping workflow podcast"),
            ("b", "clipping workflow tips podcast"),
        ],
    )
    p1 = clipbot.build_theme_profile()
    assert p1["videos"] == 2
    assert "clipping" in p1["keywords"]
    assert "clipping" in p1["labels"]
    assert os.path.exists(str(tmp_path / "p.json"))
    p2 = clipbot.build_theme_profile()
    assert p2["input_hash"] == p1["input_hash"]


def test_mark_shown_persists(monkeypatch, tmp_path):
    monkeypatch.setattr(clipbot, "DIGEST_STATE_PATH", str(tmp_path / "s.json"))
    clipbot.mark_shown([{"id": "AAA00000001"}])
    assert clipbot.load_digest_state()["shown"]["AAA00000001"]["times"] == 1
    clipbot.mark_shown([{"id": "AAA00000001"}])
    assert clipbot.load_digest_state()["shown"]["AAA00000001"]["times"] == 2


def test_on_cooldown():
    today = time.strftime("%Y-%m-%d")
    assert clipbot._on_cooldown({"last": today}, 14) is True
    assert clipbot._on_cooldown({"last": "2000-01-01"}, 14) is False
    assert clipbot._on_cooldown(None, 14) is False


def test_parse_flat_line_skips_playlists():
    assert clipbot._parse_flat_line("PLWtKFLQLtcLWPFBwVLkyOg39ppmvpzi_-\tPlaylist\t") is None
    assert clipbot._parse_flat_line("UCabcdefghijklmnop\tChannel\t") is None
    v = clipbot._parse_flat_line("LONG0000001\tEp\t1200")
    assert v == {"id": "LONG0000001", "title": "Ep", "duration": 1200}


def test_fetch_channel_videos_ndjson(monkeypatch):
    payload = (
        '{"id":"AAA00000001","title":"Ep 1","duration":900,'
        '"description":"line one\\nline two"}\n'
        '{"id":"BBB00000002","title":"Ep 2","duration":1200,"description":""}\n'
    )

    async def fake_run(args, timeout=120):
        assert "--dump-json" in args
        return payload

    monkeypatch.setattr(clipbot, "_run_ytdlp", fake_run)
    vids = _run(clipbot.fetch_channel_videos("https://x", 5, with_desc=True))
    assert [v["id"] for v in vids] == ["AAA00000001", "BBB00000002"]
    assert "line one" in vids[0]["description"]


def test_group_by_theme():
    picks = [
        {"id": "A", "score": 9.0, "theme_hits": ["clipping"]},
        {"id": "B", "score": 8.0, "theme_hits": ["clipping"]},
        {"id": "C", "score": 7.0, "theme_hits": ["podcast"]},
        {"id": "D", "score": 6.0, "theme_hits": []},
    ]
    groups = dict(clipbot.group_by_theme(picks))
    assert [p["id"] for p in groups["clipping"]] == ["A", "B"]
    assert {p["id"] for p in groups["Other picks"]} == {"C", "D"}


def test_trending_filters_and_recency(monkeypatch):
    search_out = "SHORT000001\tquick short\t30\nLONG0000001\tpodcast clipping tips\t1200"

    async def fake_run(args, timeout=120):
        return search_out

    async def fake_meta(ids):
        return {
            "LONG0000001": {
                "upload_date": time.strftime("%Y%m%d"),
                "view_count": 10000,
            }
        }

    monkeypatch.setattr(clipbot, "_run_ytdlp", fake_run)
    monkeypatch.setattr(clipbot, "_load_trending_meta", fake_meta)
    profile = {"labels": ["clipping"], "keywords": {"clipping": 3.0, "podcast": 2.0}}
    cfg = {
        **clipbot.DEFAULT_CONFIG,
        "digest_trending_seeds": 1,
        "digest_trending_per_seed": 5,
        "digest_trending_top_n": 2,
        "digest_trending_min_duration_s": 300,
    }
    picks = _run(clipbot.trending_candidates(profile, cfg, exclude=set()))
    ids = [p["id"] for p in picks]
    assert "LONG0000001" in ids
    assert "SHORT000001" not in ids


def test_trending_prefers_seeds_and_falls_back(monkeypatch):
    captured = {}

    async def fake_run(args, timeout=120):
        captured["args"] = args
        return "OLD00000001\tpodcast ekonomi islam\t3600"

    async def fake_meta(ids):
        return {"OLD00000001": {"upload_date": "20100101", "view_count": 5000}}

    monkeypatch.setattr(clipbot, "_run_ytdlp", fake_run)
    monkeypatch.setattr(clipbot, "_load_trending_meta", fake_meta)
    profile = {
        "seeds": ["ekonomi islam"],
        "labels": ["islam"],
        "keywords": {"ekonomi islam": 5.0},
    }
    cfg = {**clipbot.DEFAULT_CONFIG, "digest_trending_seeds": 1, "digest_trending_per_seed": 5}
    picks = _run(clipbot.trending_candidates(profile, cfg, exclude=set()))
    assert "ekonomi%20islam" in captured["args"][-1]
    # Nothing inside the recency window -> newest on-theme upload still surfaces.
    assert [p["id"] for p in picks] == ["OLD00000001"]


def test_build_digest_dedup(monkeypatch):
    monkeypatch.setattr(
        clipbot,
        "build_theme_profile",
        lambda force=False: {"keywords": {}, "labels": [], "videos": 0},
    )
    monkeypatch.setattr(clipbot, "clipped_video_ids", lambda: {"CLIPPED0001"})
    today = time.strftime("%Y-%m-%d")
    monkeypatch.setattr(
        clipbot,
        "load_digest_state",
        lambda: {
            "shown": {
                "SHOWN000001": {"last": today, "times": 1},
                "OLD00000001": {"last": "2000-01-01", "times": 1},
            }
        },
    )
    monkeypatch.setattr(
        clipbot, "_read_yaml", lambda path: {"sources": [{"url": "x", "weight": 1.0}]}
    )

    async def fake_fetch(url, limit=5, with_desc=False):
        return [
            {"id": "CLIPPED0001", "title": "clipped", "duration": 900, "description": ""},
            {"id": "SHOWN000001", "title": "shown recently", "duration": 900, "description": ""},
            {"id": "OLD00000001", "title": "shown long ago", "duration": 900, "description": ""},
            {"id": "FRESH000001", "title": "fresh episode ?", "duration": 900, "description": ""},
        ]

    async def fake_trending(profile, cfg, exclude):
        return []

    monkeypatch.setattr(clipbot, "fetch_channel_videos", fake_fetch)
    monkeypatch.setattr(clipbot, "trending_candidates", fake_trending)
    cfg = {**clipbot.DEFAULT_CONFIG, "digest_trending_enabled": False}
    res = _run(clipbot.build_digest(cfg=cfg))
    ids = [p["id"] for p in res["channel"]]
    assert "CLIPPED0001" not in ids
    assert "SHOWN000001" not in ids
    assert "OLD00000001" in ids
    assert "FRESH000001" in ids
    assert res["trending"] == []
