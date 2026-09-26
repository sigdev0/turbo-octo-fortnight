import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import clipbot


def test_parse_clip_args_full():
    p = clipbot.parse_clip_args("/clip https://youtu.be/abc123 --style bold --max 5")
    assert p["url"] == "https://youtu.be/abc123"
    assert p["style"] == "bold"
    assert p["max_clips"] == 5


def test_parse_clip_args_bare_url():
    p = clipbot.parse_clip_args("check this https://www.youtube.com/watch?v=xyz out")
    assert p["url"] == "https://www.youtube.com/watch?v=xyz"
    assert p["style"] is None


def test_parse_clip_args_no_url():
    p = clipbot.parse_clip_args("hello world")
    assert p["url"] is None


def test_parse_clip_args_per_job_flags():
    p = clipbot.parse_clip_args(
        "/clip https://youtu.be/abc --layout fit --smart-crop --loudnorm"
    )
    assert p["overrides"]["clips.layout"] == "fit"
    assert p["overrides"]["clips.smart_crop"] == "true"
    assert p["overrides"]["clips.loudnorm"] == "true"
    p2 = clipbot.parse_clip_args("https://youtu.be/abc --no-smart-crop")
    assert p2["overrides"]["clips.smart_crop"] == "false"


def test_validate_bot_value():
    ok, val = clipbot.validate_bot_value("max_clips", "5")
    assert ok and val == 5
    assert clipbot.validate_bot_value("max_clips", "x")[0] is False
    assert clipbot.validate_bot_value("style", "hormozi")[0] is True
    assert clipbot.validate_bot_value("style", "nope")[0] is False
    assert clipbot.validate_bot_value("preset", "tiktok")[0] is True
    assert clipbot.validate_bot_value("preset", "nope")[0] is False
    assert clipbot.validate_bot_value("digest_time", "07:30")[0] is True
    assert clipbot.validate_bot_value("digest_time", "25:00")[0] is False


def test_list_styles_and_presets():
    styles = clipbot.list_styles()
    assert {"hormozi", "bold", "minimal"} <= set(styles)
    assert styles["hormozi"]["position"] == "bottom"
    presets = clipbot.list_preset_info()
    assert {"shorts", "tiktok", "reels"} <= set(presets)
    assert presets["tiktok"]["caption"]["position"] == "bottom"


def test_config_dump_covers_all():
    dump = clipbot.config_dump()
    assert "Bot defaults" in dump
    assert "[clips]" in dump
    assert "clips.layout = auto|crop|fit" in dump
    assert "Styles:" in dump and "Presets:" in dump


def test_chunk_message_splits_long_text():
    parts = clipbot.chunk_message("\n".join(f"line {i}" for i in range(2000)))
    assert len(parts) > 1
    assert all(len(p) <= 3800 for p in parts)



def test_digest_score_hooks_and_length():
    v = {"title": "Why is money the biggest secret? Never miss this!", "duration": 900}
    s, reasons = clipbot.digest_score(v, 1.0)
    assert s >= 4.0
    assert "good-length" in reasons


def test_digest_score_too_long_penalty():
    v = {"title": "plain talk", "duration": 3600}
    _score, reasons = clipbot.digest_score(v, 1.0)
    assert "too-long" in reasons


def test_digest_score_weight_scales():
    v = {"title": "Why secret money?", "duration": 900}
    s1, _reasons = clipbot.digest_score(v, 1.0)
    s2, _reasons2 = clipbot.digest_score(v, 2.0)
    assert s2 == round(s1 * 2, 2)


def test_check_user_allowlist():
    class U:
        id = 126259585

    class Upd:
        effective_user = U()

    clipbot.ALLOWED_USER = 126259585
    assert clipbot.check_user(Upd()) is True
    U.id = 999
    assert clipbot.check_user(Upd()) is False
    clipbot.ALLOWED_USER = 0
    assert clipbot.check_user(Upd()) is True


def test_enqueue_reuses_slug(tmp_path, monkeypatch):
    monkeypatch.setattr(clipbot, "QUEUE_PATH", str(tmp_path / "q.json"))
    j1 = clipbot.enqueue("https://youtu.be/abc123", {})
    assert j1["id"] == "abc123"
    clipbot.set_job(j1["id"], status="done")
    j2 = clipbot.enqueue("https://youtu.be/abc123", {})
    assert j2["id"] == "abc123-2"
    assert clipbot.find_job("abc123")["status"] == "done"
    assert clipbot.find_job("nope") is None


def test_classify_failure_youtube_block():
    lines = ["[download] 12.0%", "ERROR: unable to download video data: HTTP Error 403: Forbidden"]
    assert "YouTube blocked" in clipbot.classify_failure(lines)


def test_classify_failure_rank_down():
    lines = ["[4/5] rank", "rank failed: request failed (attempt 4): HTTP Error 503"]
    assert "rank models failed" in clipbot.classify_failure(lines)


def test_classify_failure_unavailable():
    lines = ["ERROR: [youtube] INVALID1234: This video is unavailable"]
    assert "unavailable" in clipbot.classify_failure(lines)


def test_classify_failure_fallback_last_line():
    lines = ["some noise", "", "final weird error"]
    assert clipbot.classify_failure(lines) == "final weird error"
    assert clipbot.classify_failure([]) == "unknown error"


def test_summarize_tail_strips_traceback():
    lines = [
        "Traceback (most recent call last):",
        '  File "/x/yt_dlp/YoutubeDL.py", line 1103, in trouble',
        "    raise DownloadError(message, exc_info)",
        "yt_dlp.utils.DownloadError: ERROR: [youtube] AB: This video is unavailable",
    ]
    out = clipbot.summarize_tail(lines)
    assert "Traceback" not in out
    assert "File \"" not in out
    assert "This video is unavailable" in out


def test_progress_detail_parsing():
    assert clipbot.progress_detail("[download]  45.2% of 33MiB", "-") == "downloading 45.2%"
    assert "groq" in clipbot.progress_detail("  backend=groq segments=493", "-")
    assert "20 candidates" in clipbot.progress_detail("  20 candidates", "-")
    assert "best so far 92" in clipbot.progress_detail("  [13] score=92 Hook", "-")
    assert "clip0.mp4" in clipbot.progress_detail(
        "  output/x/clip0.mp4 (287-335s score=92)", "-"
    )
    assert clipbot.progress_detail("random line", "keep") == "keep"


def test_format_status_has_stage_and_reason():
    job = {
        "id": "j1",
        "status": "failed",
        "stage": "rank",
        "detail": "failed",
        "started": clipbot.time.time() - 65,
        "reason": "all rank models down",
        "url": "https://youtu.be/x",
    }
    text = clipbot.format_status(job)
    assert "FAILED" in text
    assert "rank" in text
    assert "elapsed: 1m" in text
    assert "all rank models down" in text


def test_recover_orphans_marks_dead_running(tmp_path, monkeypatch):
    monkeypatch.setattr(clipbot, "QUEUE_PATH", str(tmp_path / "q.json"))
    clipbot.save_queue(
        {
            "jobs": [
                {"id": "dead", "status": "running", "pid": 999999999},
                {"id": "alive", "status": "running", "pid": os.getpid()},
                {"id": "waiting", "status": "queued"},
            ]
        }
    )
    queued = clipbot.recover_orphans()
    assert clipbot.find_job("dead")["status"] == "failed"
    assert "orphaned" in clipbot.find_job("dead")["reason"]
    assert clipbot.find_job("alive")["status"] == "running"
    assert queued == ["waiting"]


def test_parse_clip_args_fresh():
    assert clipbot.parse_clip_args("/clip https://youtu.be/abc --fresh")["fresh"] is True
    assert clipbot.parse_clip_args("https://youtu.be/abc")["fresh"] is False


def test_reuse_artifacts_copies_once(tmp_path, monkeypatch):
    monkeypatch.setattr(clipbot, "ROOT", str(tmp_path))
    src = tmp_path / "work" / "old"
    src.mkdir(parents=True)
    (src / "ranked.json").write_text("[1]")
    (src / "transcript.json").write_text("{}")
    copied = clipbot.reuse_artifacts("new", "old")
    assert "ranked.json" in copied and "transcript.json" in copied
    assert (tmp_path / "work" / "new" / "ranked.json").read_text() == "[1]"
    assert clipbot.reuse_artifacts("new", "old") == []


def test_enqueue_sets_reuse_from(tmp_path, monkeypatch):
    monkeypatch.setattr(clipbot, "QUEUE_PATH", str(tmp_path / "q.json"))
    monkeypatch.setattr(clipbot, "ROOT", str(tmp_path))
    j1 = clipbot.enqueue("https://youtu.be/abc123", {})
    clipbot.set_job(j1["id"], status="done")
    work = tmp_path / "work" / "abc123"
    work.mkdir(parents=True)
    (work / "ranked.json").write_text("[]")
    j2 = clipbot.enqueue("https://youtu.be/abc123", {})
    assert j2["reuse_from"] == "abc123"
    assert j2["fresh"] is False
    clipbot.set_job(j2["id"], status="done")
    j3 = clipbot.enqueue("https://youtu.be/abc123", {}, {"fresh": True})
    assert j3["reuse_from"] is None
    assert j3["fresh"] is True


def test_deliver_clips_names_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(clipbot, "ROOT", str(tmp_path))
    out = tmp_path / "output" / "j1"
    out.mkdir(parents=True)
    (out / "clip0.mp4").write_bytes(b"x")
    (out / "clip0.meta.json").write_text('{"hook": "h", "score": 90}')
    work = tmp_path / "work" / "j1"
    work.mkdir(parents=True)
    (work / "ranked.json").write_text("[]")

    sent = []

    class FakeBot:
        async def send_video(self, chat_id, video, caption=None):
            sent.append((video.filename, video.mimetype))

        async def send_document(self, chat_id, document, caption=None):
            sent.append((document.filename, document.mimetype))

        async def send_message(self, chat_id, text):
            sent.append(("message", text))

    class FakeApp:
        bot = FakeBot()

    asyncio.run(clipbot.deliver_clips(FakeApp(), 123, {"id": "j1"}))
    assert sent == [("clip0.mp4", "video/mp4")]


def test_main_restarts_on_network_error(monkeypatch):
    calls = {"n": 0}

    class FakeApp:
        def run_polling(self, **kw):
            calls["n"] += 1
            if calls["n"] == 1:
                raise clipbot.NetworkError("boom")

    monkeypatch.setattr(clipbot, "build_app", lambda token: FakeApp())
    monkeypatch.setattr(clipbot, "_env", lambda name: "tok")
    monkeypatch.setattr(clipbot.time, "sleep", lambda s: None)
    clipbot.main()
    assert calls["n"] == 2
