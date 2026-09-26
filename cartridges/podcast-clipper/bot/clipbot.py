import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.parse
from itertools import pairwise

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.error import NetworkError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

ROOT = os.path.join(os.path.dirname(__file__), "..")
ROOT = os.path.normpath(ROOT)
QUEUE_PATH = os.path.join(ROOT, "work", "bot_queue.json")
CONFIG_PATH = os.path.join(ROOT, "work", "bot_config.json")
SOURCES_PATH = os.path.join(ROOT, "config", "sources.yaml")
STYLES_DIR = os.path.join(ROOT, "config", "styles")
PRESETS_DIR = os.path.join(ROOT, "config", "presets")
SETTINGS_PATH = os.path.join(ROOT, "config", "settings.yaml")
DIGEST_STATE_PATH = os.path.join(ROOT, "work", "digest_state.json")
DIGEST_PROFILE_PATH = os.path.join(ROOT, "work", "digest_profile.json")
TRENDING_SEARCH_URL = (
    "https://www.youtube.com/results?search_query={query}&sp=CAI%3D"
)

URL_RE = re.compile(r"(https?://[^\s]+)")
YOUTUBE_RE = re.compile(r"(https?://(?:www\.|m\.)?(?:youtube\.com|youtu\.be)[^\s]*)")

STAGE_RE = re.compile(r"\[(\d)/5\] ([a-z]+)(?: \((cached)\))?")
DOWNLOAD_PCT_RE = re.compile(r"\[download\]\s+([\d.]+)%")
TITLE_RE = re.compile(r"^\s{2}.+\((\d+)s\)\s*$")
TRANSCRIBE_RE = re.compile(r"backend=(\w+) segments=(\d+)")
CANDIDATES_RE = re.compile(r"^\s{2}(\d+) candidates\s*$")
RANK_LINE_RE = re.compile(r"^\s{2}\[(\d+)\] score=(\d+)")
CLIP_LINE_RE = re.compile(r"^\s{2}(\S+\.mp4) \(([\d.]+)-([\d.]+)s score=(\d+)\)")

DEFAULT_CONFIG = {
    "style": None,
    "preset": None,
    "max_clips": 3,
    "digest_time": "07:00",
    "digest_cooldown_days": 14,
    "digest_per_channel_limit": 15,
    "digest_top_n": 5,
    "digest_theme_weight": 1.0,
    "digest_trending_enabled": True,
    "digest_trending_window_days": 30,
    "digest_trending_seeds": 3,
    "digest_trending_per_seed": 10,
    "digest_trending_min_duration_s": 300,
    "digest_trending_top_n": 2,
}

FAILURE_HINTS = [
    (
        r"YouTube blocked|Sign in to confirm|403|Forbidden|cookies|bot",
        "YouTube blocked the download (bot check). Retry, or add cookies to the source.",
    ),
    (
        (
            r"video unavailable|Private video|This video is unavailable|"
            r"Video unavailable|removed"
        ),
        "Video is unavailable or private.",
    ),
    (
        r"exceeds|capprobe",
        "Video is longer than the duration cap.",
    ),
    (
        (
            r"rank failed|503|502|Service Unavailable|fetch connect timeout|"
            r"Connection refused"
        ),
        "All rank models failed (gateway upstream down). Retry in a few minutes.",
    ),
    (
        r"rank parse failed",
        "Rank model returned unparseable output. Retry or change rank_models.",
    ),
    (
        r"no candidates|0 candidates",
        "No clip candidates found in this episode.",
    ),
    (
        r"CalledProcessError|ffmpeg|libass|subtitles",
        "ffmpeg/transcode error (check fonts, libass, source media).",
    ),
    (
        r"cannot probe dims|cannot probe duration",
        "Could not read the source media (corrupt or unsupported file).",
    ),
    (
        r"429|Rate limit|rate limit|Too Many Requests",
        "Rate limited by an upstream API. Retry shortly.",
    ),
    (
        r"DownloadError|unable to download video data",
        "Download failed.",
    ),
]


def classify_failure(lines):
    text = "\n".join(lines)
    for pat, msg in FAILURE_HINTS:
        if re.search(pat, text, re.IGNORECASE):
            return msg
    for ln in reversed(lines):
        if ln.strip():
            return ln.strip()[:300]
    return "unknown error"


def summarize_tail(lines, n=4):
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith(("Traceback", "File \"", "self.", "raise ", "return ", "during handling")):
            continue
        if re.match(r"^\w+Error:", s) or "ERROR:" in s or "Error:" in s:
            out.append(s)
    if not out:
        out = [ln.strip() for ln in lines if ln.strip()][-n:]
    seen = []
    for ln in out:
        if ln not in seen:
            seen.append(ln)
    return "\n".join(seen[-n:])


def progress_detail(line, detail):
    if DOWNLOAD_PCT_RE.search(line):
        pct = DOWNLOAD_PCT_RE.search(line).group(1)
        return f"downloading {pct}%"
    m = TRANSCRIBE_RE.search(line)
    if m:
        return f"transcribed via {m.group(1)} — {m.group(2)} segments"
    m = CANDIDATES_RE.match(line)
    if m:
        return f"{m.group(1)} candidates found"
    m = RANK_LINE_RE.match(line)
    if m:
        return f"scoring… best so far {m.group(2)}"
    m = CLIP_LINE_RE.match(line)
    if m:
        return f"rendered {m.group(1)} (score {m.group(4)})"
    return detail


def _env(name, default=""):
    v = os.environ.get(name, default)
    if not v and name == "TELEGRAM_TOKEN":
        v = os.environ.get("TELEGRAM_BOT_TOKEN", default)
    return v


ALLOWED_USER = int(_env("TELEGRAM_ALLOWED_USER_ID", "0") or 0)


def load_queue():
    try:
        with open(QUEUE_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"jobs": []}


def save_queue(q):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w") as f:
        json.dump(q, f, indent=1)


def load_bot_config():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError):
        cfg = {}
    return {**DEFAULT_CONFIG, **cfg}


def save_bot_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=1)


def check_user(update: Update):
    return not (
        ALLOWED_USER
        and update.effective_user
        and update.effective_user.id != ALLOWED_USER
    )


async def guard(update: Update):
    if not check_user(update):
        if update.message:
            await update.message.reply_text("Not authorized.")
        return False
    return True


def parse_clip_args(text):
    args = {
        "url": None,
        "style": None,
        "preset": None,
        "max_clips": None,
        "overrides": {},
        "fresh": False,
    }
    m = YOUTUBE_RE.search(text or "")
    if not m:
        return args
    args["url"] = m.group(1)
    if "--fresh" in text:
        args["fresh"] = True
    for flag in ("--style", "--preset", "--max-clips", "--max"):
        pm = re.search(rf"{flag}\s+(\S+)", text)
        if pm:
            key = "max_clips" if flag.startswith("--max") else flag[2:]
            args[key] = int(pm.group(1)) if key == "max_clips" else pm.group(1)
    lay = re.search(r"--layout\s+(\S+)", text)
    if lay:
        args["overrides"]["clips.layout"] = lay.group(1).lower()
    if "--smart-crop" in text:
        args["overrides"]["clips.smart_crop"] = "true"
    if "--no-smart-crop" in text:
        args["overrides"]["clips.smart_crop"] = "false"
    if "--loudnorm" in text:
        args["overrides"]["clips.loudnorm"] = "true"
    if "--no-loudnorm" in text:
        args["overrides"]["clips.loudnorm"] = "false"
    if "--follow" in text:
        args["overrides"]["clips.follow_speaker"] = "true"
    if "--no-follow" in text:
        args["overrides"]["clips.follow_speaker"] = "false"
    return args


def enqueue(url, cfg, overrides=None):
    from clipper.pipeline import _slug

    overrides = overrides or {}
    q = load_queue()
    existing = [j for j in q["jobs"] if j.get("url") == url and j["status"] in ("done", "failed", "cancelled")]
    n = len(existing)
    base = _slug(url, 0)
    job_id = base if n == 0 else f"{base}-{n + 1}"
    fresh = bool(overrides.get("fresh"))
    reuse_from = None
    if not fresh:
        for prev in reversed(existing):
            if os.path.exists(os.path.join(ROOT, "work", prev["id"], "ranked.json")):
                reuse_from = prev["id"]
                break
    job = {
        "id": job_id,
        "url": url,
        "style": overrides.get("style") or cfg.get("style"),
        "preset": overrides.get("preset") or cfg.get("preset"),
        "max_clips": overrides.get("max_clips") or cfg.get("max_clips", 3),
        "overrides": overrides.get("overrides") or {},
        "fresh": fresh,
        "reuse_from": reuse_from,
        "status": "queued",
        "stage": "-",
        "detail": "queued",
        "reason": "",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    q["jobs"].append(job)
    save_queue(q)
    return job


def find_job(job_id):
    for j in load_queue()["jobs"]:
        if j["id"] == job_id:
            return j
    return None


def set_job(job_id, **kw):
    q = load_queue()
    for j in q["jobs"]:
        if j["id"] == job_id:
            j.update(kw)
    save_queue(q)


def _append_lines(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.writelines(ln + "\n" for ln in lines)


REUSE_ARTIFACTS = ("transcript.json", "candidates.json", "ranked.json", "rank_meta.json")


def reuse_artifacts(job_id, from_id):
    import shutil

    src_dir = os.path.join(ROOT, "work", from_id)
    dst_dir = os.path.join(ROOT, "work", job_id)
    os.makedirs(dst_dir, exist_ok=True)
    copied = []
    for name in REUSE_ARTIFACTS:
        src = os.path.join(src_dir, name)
        dst = os.path.join(dst_dir, name)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            copied.append(name)
    return copied


def job_log_path(job_id):
    return os.path.join(ROOT, "work", job_id, "job.log")


def read_job_log(job_id, tail=30):
    try:
        with open(job_log_path(job_id)) as f:
            return f.read().splitlines()[-tail:]
    except OSError:
        return []


def _fmt_dur(sec):
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m{sec % 60:02d}s"
    return f"{sec // 3600}h{(sec % 3600) // 60:02d}m"


def last_cost(job_id):
    path = os.path.join(ROOT, "work", "costs.jsonl")
    entry = None
    try:
        with open(path) as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("name") == job_id:
                    entry = e
    except OSError:
        return None
    return entry


def format_status(job):
    lines = [f"[{job['id']}] {job['status'].upper()}"]
    lines.append(f"stage: {job.get('stage', '-')} — {job.get('detail', '-')}")
    if job.get("started"):
        lines.append(f"elapsed: {_fmt_dur(time.time() - job['started'])}")
    if job.get("reason"):
        lines.append(f"reason: {job['reason']}")
    lines.append(job.get("url", ""))
    return "\n".join(lines)


def format_summary(job_id, wall=None):
    out_dir = os.path.join(ROOT, "output", job_id)
    clips = []
    if os.path.isdir(out_dir):
        clips = sorted(f for f in os.listdir(out_dir) if f.endswith(".mp4"))
    entry = last_cost(job_id) or {}
    stage_s = entry.get("stage_s") or {}
    rank = entry.get("rank") or {}
    parts = [f"[{job_id}] DONE — {len(clips)} clip(s)"]
    if stage_s:
        total = sum(stage_s.values())
        parts.append(
            "pipeline: " + _fmt_dur(total) + " ("
            + ", ".join(f"{k} {_fmt_dur(v)}" for k, v in stage_s.items() if v)
            + ")"
        )
    if wall:
        parts.append(f"wall: {_fmt_dur(wall)} (incl. startup/imports)")
    if rank.get("total_tokens"):
        parts.append(f"rank: {rank.get('model', '?')} {rank['total_tokens']} tokens")
        tried = rank.get("models_tried") or []
        if tried and rank.get("model") and rank["model"] != tried[0]:
            parts.append(f"note: fell back to {rank['model']}")
    meta = _read_json(os.path.join(ROOT, "work", job_id, "rank_meta.json"), {})
    if meta.get("model") and not rank.get("model"):
        parts.append(f"rank: {meta['model']} ({meta.get('total_tokens', 0)} tokens)")
    parts.append(f"files: output/{job_id}/")
    return "\n".join(parts)


def _pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def recover_orphans():
    q = load_queue()
    changed = False
    for j in q["jobs"]:
        if j["status"] == "running" and not _pid_alive(j.get("pid")):
            j["status"] = "failed"
            j["stage"] = "error"
            j["detail"] = "interrupted"
            j["reason"] = "orphaned (bot restarted mid-job) — retry to resume from cache"
            changed = True
    if changed:
        save_queue(q)
    return [j["id"] for j in q["jobs"] if j["status"] == "queued"]


WORKER_RUNNING = False


async def worker_loop(app):
    global WORKER_RUNNING
    if WORKER_RUNNING:
        return
    WORKER_RUNNING = True
    try:
        while True:
            q = load_queue()
            nxt = next((j for j in q["jobs"] if j["status"] == "queued"), None)
            if not nxt:
                break
            await run_job(app, nxt)
    finally:
        WORKER_RUNNING = False


async def run_job(app, job):
    job_id = job["id"]
    chat_id = job.get("chat_id")
    msg_id = job.get("msg_id")
    log_path = job_log_path(job_id)
    cmd = [
        sys.executable,
        "cli.py",
        "process",
        job["url"],
        "--name",
        job_id,
        "--max-clips",
        str(job.get("max_clips") or 3),
        "--resume",
    ]
    if job.get("style"):
        cmd += ["--style", job["style"]]
    if job.get("preset"):
        cmd += ["--preset", job["preset"]]
    for key, val in (job.get("overrides") or {}).items():
        cmd += ["--set", f"{key}={val}"]
    env = dict(os.environ)

    state = {
        "stage": "download",
        "detail": "starting",
        "started": time.time(),
        "last_edit": 0.0,
        "last_text": "",
    }

    async def flush_log(lines):
        if lines:
            await asyncio.to_thread(_append_lines, log_path, lines)

    async def edit(force=False):
        nonlocal state
        now = time.time()
        text = format_status({**job, **state, "status": "running"})
        if not force and (now - state["last_edit"] < 3 or text == state["last_text"]):
            return
        state["last_edit"] = now
        state["last_text"] = text
        if chat_id and msg_id:
            try:
                await app.bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id)
            except Exception as e:  # noqa: BLE001 - status edit is best-effort
                print(f"status edit failed: {e}")

    set_job(
        job_id,
        status="running",
        stage="download",
        detail="starting",
        started=state["started"],
        reason="",
        preset=job.get("preset"),
    )
    await flush_log([f"=== job {job_id} started {time.strftime('%Y-%m-%dT%H:%M:%S')} ==="])
    if job.get("reuse_from") and not job.get("fresh"):
        copied = await asyncio.to_thread(reuse_artifacts, job_id, job["reuse_from"])
        if copied:
            await flush_log([f"reused {', '.join(copied)} from {job['reuse_from']}"])
    await edit(force=True)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=ROOT,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        set_job(job_id, pid=proc.pid)
        tail = []
        batch = []
        seen_pct = None
        assert proc.stdout is not None
        async for raw in proc.stdout:
            chunk = raw.decode(errors="replace").replace("\r", "\n")
            for line in chunk.splitlines():
                line = line.strip()
                if not line:
                    continue
                m = DOWNLOAD_PCT_RE.search(line)
                if m:
                    pct = int(float(m.group(1)))
                    if pct != seen_pct:
                        seen_pct = pct
                        state["detail"] = f"downloading {pct}%"
                        batch.append(f"download {pct}%")
                        await edit()
                    continue
                tail.append(line)
                tail = tail[-40:]
                batch.append(line)
                st = STAGE_RE.search(line)
                if st:
                    state["stage"] = st.group(2) + (" (cached)" if st.group(3) else "")
                    state["detail"] = st.group(2)
                    set_job(job_id, stage=state["stage"], detail=state["detail"])
                    await flush_log(batch)
                    batch = []
                    await edit(force=True)
                    continue
                new_detail = progress_detail(line, state["detail"])
                if new_detail != state["detail"]:
                    state["detail"] = new_detail
                    set_job(job_id, detail=new_detail)
                    await edit()
                if len(batch) >= 20:
                    await flush_log(batch)
                    batch = []
            if batch:
                await flush_log(batch)
                batch = []
        await proc.wait()
        await flush_log(batch)
        if proc.returncode == 0:
            set_job(job_id, status="done", stage="clips", detail="complete")
            await edit(force=True)
            summary = format_summary(job_id, wall=time.time() - state["started"])
            await flush_log([summary])
            if chat_id:
                try:
                    await app.bot.send_message(chat_id, summary)
                except Exception as e:  # noqa: BLE001 - summary is best-effort
                    print(f"summary send failed: {e}")
            await deliver_clips(app, chat_id, job)
        else:
            reason = classify_failure(tail)
            set_job(job_id, status="failed", stage=state["stage"], detail="failed", reason=reason)
            await flush_log([f"FAILED: {reason}"])
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Retry", callback_data=f"retry:{job_id}")]]
            )
            tail_txt = summarize_tail(tail)[:1200]
            text = f"[{job_id}] FAILED\n{reason}\n\n{tail_txt}"
            if chat_id and msg_id:
                try:
                    await app.bot.edit_message_text(
                        text, chat_id=chat_id, message_id=msg_id, reply_markup=kb
                    )
                except Exception:  # noqa: BLE001 - status edit is best-effort
                    await app.bot.send_message(chat_id, text, reply_markup=kb)
    except asyncio.CancelledError:
        set_job(job_id, status="cancelled", detail="cancelled")
        await flush_log(["CANCELLED by user"])
        await edit(force=True)
    except Exception as e:  # noqa: BLE001 - worker must report, never crash
        set_job(job_id, status="failed", detail="error", reason=str(e))
        await flush_log([f"WORKER ERROR: {e}"])
        await edit(force=True)


def _read_json(path, default):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return default


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _read_yaml(path):
    try:
        with open(path) as fh:
            return yaml.safe_load(fh) or {}
    except OSError:
        return {}


def _write_yaml(path, data):
    with open(path, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)


def list_styles():
    out = {}
    try:
        for f in sorted(os.listdir(STYLES_DIR)):
            if f.endswith(".json"):
                out[f[:-5]] = _read_json(os.path.join(STYLES_DIR, f), {})
    except OSError:
        pass
    return out


def list_preset_info():
    out = {}
    try:
        from clipper.pipeline import list_presets

        for name in list_presets(PRESETS_DIR):
            out[name] = _read_yaml(os.path.join(PRESETS_DIR, f"{name}.yaml"))
    except Exception as e:  # noqa: BLE001 - listing is best-effort
        print(f"list_presets failed: {e}")
    return out


def read_pipeline_settings():
    return _read_yaml(SETTINGS_PATH)


def write_pipeline_settings(data):
    with open(SETTINGS_PATH, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)


def format_schema_list():
    from clipper.settings_schema import format_schema

    return format_schema()


def config_dump():
    from clipper.settings_schema import SETTABLE

    cfg = load_bot_config()
    st = read_pipeline_settings()
    lines = ["Bot defaults (writable: /config <key> <value>):"]
    for k, v in cfg.items():
        lines.append(f"  {k} = {v}")
    lines.append("")
    lines.append("Pipeline settings (read-only; /settings section[.key]):")
    for section, vals in st.items():
        if isinstance(vals, dict):
            lines.append(f"  [{section}]")
            for k, v in vals.items():
                lines.append(f"    {k} = {v}")
        else:
            lines.append(f"  {section} = {vals}")
    lines.append("")
    lines.append("Settable via /set <key> <value> (writes settings.yaml):")
    for line in format_schema_list().splitlines():
        lines.append(f"  {line}")
    lines.append("")
    lines.append("Styles: " + ", ".join(list_styles()))
    lines.append("Presets: " + ", ".join(list_preset_info()))
    lines.append(f"({len(SETTABLE)} settable keys)")
    return "\n".join(lines)


def chunk_message(text, limit=3800):
    parts, cur = [], ""
    for line in text.splitlines():
        if len(cur) + len(line) + 1 > limit:
            parts.append(cur)
            cur = ""
        cur += line + "\n"
    if cur:
        parts.append(cur)
    return parts


async def reply_chunks(message, text, **kw):
    for part in chunk_message(text):
        await message.reply_text(part, **kw)


def job_overrides(job):
    return {k: v for k, v in (job.get("overrides") or {}).items()}
async def deliver_clips(app, chat_id, job):
    if not chat_id:
        return
    out_dir = os.path.join(ROOT, "output", job["id"])
    if not os.path.isdir(out_dir):
        await app.bot.send_message(chat_id, f"[{job['id']}] done, no output dir found.")
        return
    mp4s = sorted(f for f in os.listdir(out_dir) if f.endswith(".mp4"))
    if not mp4s:
        await app.bot.send_message(chat_id, f"[{job['id']}] done, no clips produced.")
        return
    meta = {}
    for f in os.listdir(out_dir):
        if f.endswith(".meta.json"):
            meta[f.replace(".meta.json", "")] = await asyncio.to_thread(
                _read_json, os.path.join(out_dir, f), {}
            )
    ranked = await asyncio.to_thread(
        _read_json, os.path.join(ROOT, "work", job["id"], "ranked.json"), []
    )
    for i, mp4 in enumerate(mp4s):
        base = mp4.replace(".mp4", "")
        path = os.path.join(out_dir, mp4)
        r = ranked[i] if i < len(ranked) else {}
        m = meta.get(base, {})
        hook = m.get("hook") or r.get("hook", "")
        score = m.get("score", r.get("score", "?"))
        caption = f"{base} score={score} {hook}"[:900]
        data = await asyncio.to_thread(_read_bytes, path)
        try:
            await app.bot.send_video(
                chat_id, InputFile(data, filename=mp4), caption=caption
            )
        except Exception as e:  # noqa: BLE001 - fall back to document
            print(f"send_video failed ({e}), trying document")
            await app.bot.send_document(
                chat_id, InputFile(data, filename=mp4), caption=caption
            )


def score_title(title, weight=1.0):
    from clipper.prefilter import HOOK_WORDS_EN, HOOK_WORDS_ID

    score = 0.0
    reasons = []
    hooks = set()
    hooks |= {h.lower() for h in HOOK_WORDS_EN.findall(title)}
    hooks |= {h.lower() for h in HOOK_WORDS_ID.findall(title)}
    if hooks:
        score += min(len(hooks), 4)
        reasons.append("hooks:" + ",".join(sorted(hooks)[:3]))
    if "?" in title:
        score += 1.0
        reasons.append("question")
    if "!" in title:
        score += 0.5
        reasons.append("exclaim")
    score *= weight
    return round(score, 2), reasons


def _ytdlp_bin():
    bundled = os.path.join(ROOT, ".venv", "bin", "yt-dlp")
    return bundled if os.path.exists(bundled) else "yt-dlp"


async def _run_ytdlp(args, timeout=120):
    """Run yt-dlp and return stdout text; empty string on any failure (fail-open)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            _ytdlp_bin(),
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except (asyncio.TimeoutError, FileNotFoundError, OSError):
        return ""
    return out.decode(errors="replace")


def _parse_flat_line(line):
    parts = line.split("\t")
    vid = parts[0].strip() if parts else ""
    if len(parts) < 2 or len(vid) != 11:  # skip playlists/channels in search results
        return None
    duration = None
    if len(parts) > 2 and parts[2].strip().isdigit():
        duration = int(parts[2].strip())
    return {"id": vid, "title": parts[1].strip(), "duration": duration}


async def fetch_channel_videos(channel_url, limit=5, with_desc=False):
    if with_desc:
        # --dump-json (NDJSON) loads per-video metadata, so descriptions survive.
        out = await _run_ytdlp(
            ["--dump-json", "--playlist-end", str(limit), channel_url], timeout=180
        )
        vids = []
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            vids.append(
                {
                    "id": d.get("id"),
                    "title": d.get("title") or "",
                    "duration": d.get("duration"),
                    "description": (d.get("description") or "")[:500],
                }
            )
        return vids
    out = await _run_ytdlp(
        [
            "--flat-playlist",
            "--print",
            "%(id)s\t%(title)s\t%(duration)s",
            "--playlist-end",
            str(limit),
            channel_url,
        ],
        timeout=120,
    )
    return [v for v in (_parse_flat_line(ln) for ln in out.splitlines()) if v]


# --- daily digest: memory, theme profile, trending -------------------------

_VIDEO_ID_RE = re.compile(r"(?:youtu\.be/|v=|/shorts/|/embed/)([\w-]{11})")
_WORD_RE = re.compile(r"[a-z0-9]+")

_STOPWORD_TEXT = """
    a an the and or but if then than that this these those of to in on at by for with from
    is are was were be been being do does did doing have has had having i you he she it we
    they me him her us them my your his its our their as so not no yes will would can could
    should may might must about into over after before up down out off again more most some
    such only own same too very just also there here what which who when where why how all
    any both each few other
    yang dan di ke dari untuk dengan pada adalah ini itu tidak akan atau juga sebagai karena
    bila jika agar saya kamu dia kami kita mereka anda nya pun saja sudah telah belum bisa
    dapat harus mau ingin ada apa siapa kapan dimana mengapa bagaimana
"""
_STOPWORDS = set(_STOPWORD_TEXT.split())


def _video_id(url):
    m = _VIDEO_ID_RE.search(url or "")
    return m.group(1) if m else None


def _tokens(text):
    return [
        w
        for w in _WORD_RE.findall((text or "").lower())
        if len(w) > 2 and w not in _STOPWORDS
    ]


def _tokens_with_bigrams(text):
    toks = _tokens(text)
    return toks + [f"{a} {b}" for a, b in pairwise(toks)]


def load_digest_state():
    st = _read_json(DIGEST_STATE_PATH, {})
    if not isinstance(st, dict):
        st = {}
    st.setdefault("version", 1)
    st.setdefault("shown", {})
    return st


def save_digest_state(st):
    os.makedirs(os.path.dirname(DIGEST_STATE_PATH), exist_ok=True)
    with open(DIGEST_STATE_PATH, "w") as fh:
        json.dump(st, fh, indent=1)


def clipped_video_ids():
    ids = set()
    for j in load_queue().get("jobs", []):
        if j.get("status") == "done":
            vid = _video_id(j.get("url"))
            if vid:
                ids.add(vid)
    return ids


def _on_cooldown(rec, cooldown_days):
    if not rec or cooldown_days <= 0:
        return False
    last = rec.get("last")
    if not last:
        return False
    try:
        last_t = time.mktime(time.strptime(last, "%Y-%m-%d"))
    except ValueError:
        return False
    return (time.time() - last_t) < cooldown_days * 86400


def mark_shown(picks):
    st = load_digest_state()
    today = time.strftime("%Y-%m-%d")
    for p in picks:
        vid = p.get("id")
        if not vid:
            continue
        rec = st["shown"].get(vid)
        if rec:
            rec["last"] = today
            rec["times"] = int(rec.get("times", 0)) + 1
        else:
            st["shown"][vid] = {"first": today, "last": today, "times": 1}
    save_digest_state(st)


def _profile_items():
    items, seen = [], set()
    for j in load_queue().get("jobs", []):
        if j.get("status") != "done":
            continue
        vid = _video_id(j.get("url"))
        if vid and vid in seen:
            continue
        ranked = _read_json(
            os.path.join(ROOT, "work", j.get("id", ""), "ranked.json"), []
        )
        if not isinstance(ranked, list) or not ranked:
            continue
        chunks = []
        for c in ranked[:5]:
            for key in ("title", "hook", "reason", "description"):
                val = c.get(key)
                if val:
                    chunks.append(str(val))
        items.append((j.get("id"), "\n".join(chunks)))
        if vid:
            seen.add(vid)
    return items


_PROFILE_VERSION = 2


def build_theme_profile(force=False):
    items = _profile_items()
    digest_input = "|".join(f"{rid}\x00{text}" for rid, text in items)
    input_hash = hashlib.sha1(digest_input.encode()).hexdigest()
    cached = _read_json(DIGEST_PROFILE_PATH, {})
    if (
        not force
        and isinstance(cached, dict)
        and cached.get("version") == _PROFILE_VERSION
        and cached.get("input_hash") == input_hash
    ):
        return cached
    per_video = [_tokens_with_bigrams(text) for _rid, text in items]
    tf, df = {}, {}
    for toks in per_video:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
    n = max(len(per_video), 1)
    weights = {t: round(tf[t] * (math.log(n / df[t]) + 1.0), 3) for t in tf}
    top = sorted(weights.items(), key=lambda kv: (-kv[1], kv[0]))[:40]
    # Seeds favour phrases (more meaningful) then high-frequency single words,
    # which search YouTube better than the rare, high-IDF terms.
    phrases = [t for t, _ in top if " " in t][:2]
    frequent = sorted(
        (t for t in tf if " " not in t), key=lambda t: (-tf[t], t)
    )[:6]
    seeds = list(dict.fromkeys(phrases + frequent))[:6]
    profile = {
        "version": _PROFILE_VERSION,
        "input_hash": input_hash,
        "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "videos": len(per_video),
        "keywords": dict(top),
        "labels": [t for t, _ in top if " " not in t][:8],
        "seeds": seeds,
    }
    os.makedirs(os.path.dirname(DIGEST_PROFILE_PATH), exist_ok=True)
    with open(DIGEST_PROFILE_PATH, "w") as fh:
        json.dump(profile, fh, indent=1, ensure_ascii=False)
    return profile


def theme_affinity(text, profile, weight=1.0):
    keywords = (profile or {}).get("keywords") or {}
    toks = _tokens_with_bigrams(text)
    hits = sorted({t for t in toks if t in keywords}, key=lambda t: -keywords[t])
    if not hits:
        return 0.0, []
    score = sum(keywords[t] for t in hits[:6])
    return round(score * weight, 3), hits[:3]


def _within_days(upload_date, days):
    if not upload_date:
        return True
    try:
        ts = time.mktime(time.strptime(str(upload_date), "%Y%m%d"))
    except ValueError:
        return True
    return (time.time() - ts) <= days * 86400


async def _load_trending_meta(ids):
    if not ids:
        return {}
    out = await _run_ytdlp(
        ["--dump-json", "--no-playlist"] + [f"https://youtu.be/{i}" for i in ids],
        timeout=240,
    )
    meta = {}
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        meta[d.get("id")] = {
            "upload_date": d.get("upload_date"),
            "view_count": d.get("view_count"),
            "channel": d.get("channel"),
        }
    return meta


async def trending_candidates(profile, cfg, exclude):
    if not cfg.get("digest_trending_enabled", True):
        return []
    seed_pool = profile.get("seeds") or profile.get("labels") or []
    seeds = list(seed_pool)[: int(cfg.get("digest_trending_seeds", 3))] or ["podcast"]
    per_seed = int(cfg.get("digest_trending_per_seed", 10))
    min_dur = int(cfg.get("digest_trending_min_duration_s", 300))
    window_days = int(cfg.get("digest_trending_window_days", 30))
    weight = float(cfg.get("digest_theme_weight", 1.0))

    found = {}
    for seed in seeds:
        url = TRENDING_SEARCH_URL.format(query=urllib.parse.quote(seed))
        out = await _run_ytdlp(
            [
                "--flat-playlist",
                "--print",
                "%(id)s\t%(title)s\t%(duration)s",
                "--playlist-end",
                str(per_seed),
                url,
            ],
            timeout=120,
        )
        hits = [
            v
            for v in (_parse_flat_line(ln) for ln in out.splitlines())
            if v and v["id"] not in exclude
        ]
        hits = [h for h in hits if h.get("duration") is None or h["duration"] >= min_dur]
        for h in hits:
            h["affinity"], h["theme_hits"] = theme_affinity(h["title"], profile, weight)
        hits.sort(key=lambda h: (-h["affinity"], h["id"]))
        for h in hits:
            found.setdefault(h["id"], h)

    ids = [v for v in found if v not in exclude][: max(per_seed * len(seeds), 1)]
    meta = await _load_trending_meta(ids)
    scored = []
    for vid in ids:
        m = meta.get(vid, {})
        c = found[vid]
        views = m.get("view_count") or 0
        c["view_count"] = m.get("view_count")
        c["upload_date"] = m.get("upload_date")
        c["channel"] = m.get("channel")
        c["score"] = round(c.get("affinity", 0.0) + math.log10(views + 1) * 0.5, 3)
        c["recent"] = _within_days(m.get("upload_date"), window_days)
        scored.append(c)

    limit = int(cfg.get("digest_trending_top_n", 2))
    recent = sorted((c for c in scored if c["recent"]), key=lambda c: (-c["score"], c["id"]))
    if len(recent) >= limit:
        return recent[:limit]
    # Fall back to the newest on-theme uploads when nothing is inside the window.
    older = sorted(
        (c for c in scored if not c["recent"]),
        key=lambda c: (c.get("upload_date") or "", c["id"]),
        reverse=True,
    )
    return (recent + older)[:limit]


def group_by_theme(picks):
    groups = {}
    for p in picks:
        hits = p.get("theme_hits") or []
        groups.setdefault(hits[0] if hits else None, []).append(p)
    out, others = [], []
    for label, items in groups.items():
        if label and len(items) >= 2:
            out.append((label, items))
        else:
            others.extend(items)
    if others:
        others.sort(key=lambda p: (-p["score"], p["id"]))
        out.append(("Other picks", others))
    return out


def _fmt_pick(p):
    dur = f" {p['duration'] // 60}m" if p.get("duration") else ""
    return f"★ {p['score']}{dur} — {p['title']}\nhttps://youtu.be/{p['id']}"


def render_digest(res):
    lines = ["🌅 Daily digest"]
    for label, items in group_by_theme(res.get("channel", [])):
        lines.append("")
        lines.append(f"— {label} —")
        lines.extend(_fmt_pick(p) for p in items)
    trending = res.get("trending") or []
    if trending:
        lines.append("")
        lines.append("— Trending on your themes —")
        lines.extend(_fmt_pick(p) for p in trending)
    return "\n\n".join(lines)


def digest_score(v, weight=1.0):
    s, reasons = score_title(v.get("title", ""), 1.0)
    dur = v.get("duration")
    if dur and 600 <= dur <= 1800:
        s += 2.0
        reasons.append("good-length")
    elif dur and dur > 1800:
        s -= 1.0
        reasons.append("too-long")
    return round(s * weight, 2), reasons


async def cmd_clip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    await clip_from_text(
        update, ctx.application, " ".join(ctx.args or []), update.effective_chat.id
    )


async def clip_from_text(update, app, text, chat_id):
    from clipper.settings_schema import validate

    cfg = load_bot_config()
    parsed = parse_clip_args(text)
    if not parsed["url"]:
        await update.message.reply_text(
        "Usage: /clip <url> [--style X] [--preset Y] [--max N] "
        "[--layout auto|crop|fit] [--smart-crop] [--follow] [--loudnorm] [--fresh]"
        )
        return
    for key, raw in (parsed.get("overrides") or {}).items():
        ok, msg, _ = validate(key, raw, read_pipeline_settings())
        if not ok:
            await update.message.reply_text(f"bad flag {key}: {msg}")
            return
    job = enqueue(parsed["url"], cfg, overrides=parsed)
    set_job(job["id"], chat_id=chat_id)
    msg = await update.message.reply_text(f"[{job['id']}] queued: {parsed['url']}")
    set_job(job["id"], msg_id=msg.message_id)
    asyncio.create_task(worker_loop(app))


async def cmd_url_shorthand(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    text = update.message.text or ""
    if not YOUTUBE_RE.search(text):
        return
    await clip_from_text(update, ctx.application, text, update.effective_chat.id)


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    q = load_queue()
    if ctx.args:
        j = find_job(ctx.args[0])
        if not j:
            await update.message.reply_text("Job not found.")
            return
        await update.message.reply_text(format_status(j))
        return
    running = [j for j in q["jobs"] if j["status"] in ("queued", "running")]
    if not running:
        await update.message.reply_text("No active jobs.")
        return
    lines = [format_status(j) for j in running[-5:]]
    await update.message.reply_text("\n\n".join(lines))


async def cmd_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /logs <job>")
        return
    job_id = ctx.args[0]
    lines = await asyncio.to_thread(read_job_log, job_id, 40)
    if not lines:
        await update.message.reply_text(f"No log for {job_id}.")
        return
    await update.message.reply_text(("\n".join(lines))[-3500:])


async def requeue(update, app, job_id):
    if not find_job(job_id):
        return False
    set_job(job_id, status="queued", stage="-", detail="requeued", reason="", started=None)
    await update.message.reply_text(f"[{job_id}] requeued — resuming from cache.")
    asyncio.create_task(worker_loop(app))
    return True


async def cmd_retry(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /retry <job>")
        return
    if not await requeue(update, ctx.application, ctx.args[0]):
        await update.message.reply_text("Job not found.")


async def cmd_queue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    q = load_queue()
    jobs = q["jobs"][-15:]
    if not jobs:
        await update.message.reply_text("Queue empty.")
        return
    lines = []
    for j in jobs:
        line = f"[{j['id']}] {j['status']} {j.get('detail') or j.get('stage', '-')}"
        if j.get("reason"):
            line += f"\n    reason: {j['reason']}"
        lines.append(line)
    await update.message.reply_text("\n".join(lines))


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /cancel <job>")
        return
    j = find_job(ctx.args[0])
    if not j:
        await update.message.reply_text("Job not found.")
        return
    if j.get("pid"):
        try:
            os.kill(j["pid"], 15)
        except (OSError, ProcessLookupError):
            pass
    set_job(j["id"], status="cancelled")
    await update.message.reply_text(f"[{j['id']}] cancelled.")


async def cmd_costs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "cli.py",
        "costs",
        *(["--month", ctx.args[0]] if ctx.args else []),
        cwd=ROOT,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    await update.message.reply_text(out.decode(errors="replace").strip() or "No data.")


def validate_bot_value(key, val):
    if key == "max_clips":
        try:
            return True, int(val)
        except (TypeError, ValueError):
            return False, "expected an integer 1..10"
    if key == "style":
        if val not in list_styles():
            return False, "unknown style; valid: " + ", ".join(list_styles())
        return True, val
    if key == "preset":
        if val not in list_preset_info():
            return False, "unknown preset; valid: " + ", ".join(list_preset_info())
        return True, val
    if key == "digest_time":
        if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", str(val)):
            return False, "expected HH:MM (24h)"
        return True, val
    int_ranges = {
        "digest_cooldown_days": (0, 365),
        "digest_per_channel_limit": (1, 50),
        "digest_top_n": (1, 20),
        "digest_trending_window_days": (1, 365),
        "digest_trending_seeds": (1, 10),
        "digest_trending_per_seed": (1, 50),
        "digest_trending_min_duration_s": (0, 7200),
        "digest_trending_top_n": (0, 20),
    }
    if key in int_ranges:
        lo, hi = int_ranges[key]
        try:
            num = int(val)
        except (TypeError, ValueError):
            return False, f"expected an integer {lo}..{hi}"
        if not lo <= num <= hi:
            return False, f"expected an integer {lo}..{hi}"
        return True, num
    if key == "digest_theme_weight":
        try:
            num = float(val)
        except (TypeError, ValueError):
            return False, "expected a number 0..5"
        if not 0 <= num <= 5:
            return False, "expected a number 0..5"
        return True, round(num, 3)
    if key == "digest_trending_enabled":
        raw = str(val).strip().lower()
        if raw in ("1", "true", "yes", "on"):
            return True, True
        if raw in ("0", "false", "no", "off"):
            return True, False
        return False, "expected true/false"
    return True, val


async def cmd_config(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    cfg = load_bot_config()
    args = ctx.args or []
    if not args:
        await reply_chunks(update.message, config_dump())
        return
    key = args[0]
    if key not in DEFAULT_CONFIG:
        await update.message.reply_text(
            f"Unknown key. Valid: {', '.join(DEFAULT_CONFIG)}\n"
            "Use /config (no args) to see all configuration."
        )
        return
    if len(args) == 1:
        await update.message.reply_text(f"{key} = {cfg.get(key)}")
        return
    raw = " ".join(args[1:])
    ok, res = validate_bot_value(key, raw)
    if not ok:
        await update.message.reply_text(f"{key}: {res}")
        return
    cfg[key] = res
    save_bot_config(cfg)
    await update.message.reply_text(f"{key} = {res}")


async def cmd_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    st = read_pipeline_settings()
    if not ctx.args:
        sel = st
    else:
        sel = st
        for part in ctx.args[0].split("."):
            if isinstance(sel, dict) and part in sel:
                sel = sel[part]
            else:
                await update.message.reply_text(f"not found: {ctx.args[0]}")
                return
    if isinstance(sel, dict):
        text = "\n".join(f"{k} = {v}" for k, v in sel.items())
    else:
        text = str(sel)
    await reply_chunks(update.message, text)


async def cmd_set(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from clipper.settings_schema import set_in, validate

    if not await guard(update):
        return
    args = ctx.args or []
    if len(args) != 2:
        await update.message.reply_text(
            "Usage: /set <section.key> <value>\nSee /config for the settable keys."
        )
        return
    key, raw = args[0], args[1]
    st = read_pipeline_settings()
    ok, msg, val = validate(key, raw, st)
    if not ok:
        await update.message.reply_text(f"{key}: {msg}")
        return
    set_in(st, key, val)
    await asyncio.to_thread(write_pipeline_settings, st)
    await update.message.reply_text(f"{key} = {val}  (applies to the next job)")


async def cmd_style(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    styles = list_styles()
    if not ctx.args:
        lines = []
        for n, s in styles.items():
            lines.append(
                f"{n}: {s.get('font')} {s.get('size')} "
                f"{s.get('position', s.get('alignment', '?'))} mv={s.get('margin_v')}"
            )
        await reply_chunks(update.message, "\n".join(lines))
        return
    name = ctx.args[0]
    if name not in styles:
        await update.message.reply_text("unknown; valid: " + ", ".join(styles))
        return
    await reply_chunks(update.message, json.dumps(styles[name], indent=1, ensure_ascii=False))


async def cmd_preset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    presets = list_preset_info()
    if not ctx.args:
        lines = [f"{n}: {p.get('description', '')}" for n, p in presets.items()]
        await reply_chunks(update.message, "\n".join(lines))
        return
    name = ctx.args[0]
    if name not in presets:
        await update.message.reply_text("unknown; valid: " + ", ".join(presets))
        return
    await reply_chunks(update.message, json.dumps(presets[name], indent=1, ensure_ascii=False))


async def cmd_sources(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    args = ctx.args or []
    data = await asyncio.to_thread(_read_yaml, SOURCES_PATH)
    sources = data.get("sources", [])
    if not args or args[0] == "list":
        if not sources:
            await update.message.reply_text("No sources.")
            return
        lines = [
            f"{i}. {s.get('url')} lang={s.get('lang', '?')} w={s.get('weight', 1.0)}"
            for i, s in enumerate(sources)
        ]
        await update.message.reply_text("\n".join(lines))
        return
    if args[0] == "add" and len(args) >= 2:
        sources.append({"url": args[1], "lang": "en", "max_clips": 3, "weight": 1.0})
        data["sources"] = sources
        await asyncio.to_thread(_write_yaml, SOURCES_PATH, data)
        await update.message.reply_text(f"Added. {len(sources)} sources total.")
        return
    if args[0] == "rm" and len(args) >= 2:
        try:
            idx = int(args[1])
            sources.pop(idx)
            data["sources"] = sources
            await asyncio.to_thread(_write_yaml, SOURCES_PATH, data)
            await update.message.reply_text(f"Removed. {len(sources)} sources total.")
        except (ValueError, IndexError):
            await update.message.reply_text("Usage: /sources rm <index>")
        return
    await update.message.reply_text("Usage: /sources [list|add <url>|rm <index>]")


async def build_digest(cfg=None, limit_per_channel=None, top_n=None):
    cfg = cfg or load_bot_config()
    top_n = int(top_n if top_n is not None else cfg.get("digest_top_n", 5))
    per_ch = int(
        limit_per_channel
        if limit_per_channel is not None
        else cfg.get("digest_per_channel_limit", 15)
    )
    cooldown = int(cfg.get("digest_cooldown_days", 14))
    weight = float(cfg.get("digest_theme_weight", 1.0))

    profile = build_theme_profile()
    clipped = clipped_video_ids()
    shown = load_digest_state().get("shown", {})

    data = await asyncio.to_thread(_read_yaml, SOURCES_PATH)
    channel_picks = []
    for s in data.get("sources", []):
        url = s.get("url", "")
        src_weight = float(s.get("weight", 1.0))
        vids = await fetch_channel_videos(url, per_ch, with_desc=True)
        for v in vids:
            vid = v.get("id")
            if not vid or vid in clipped or _on_cooldown(shown.get(vid), cooldown):
                continue
            base, _reasons = digest_score(v, src_weight)
            affinity, theme_hits = theme_affinity(
                (v.get("title") or "") + " " + (v.get("description") or ""),
                profile,
                weight,
            )
            channel_picks.append(
                {
                    **v,
                    "score": round(base + affinity, 3),
                    "base_score": base,
                    "theme_hits": theme_hits,
                    "channel": url,
                    "tier": "channel",
                }
            )
    channel_picks.sort(key=lambda p: (-p["score"], p["id"]))
    picks = channel_picks[:top_n]

    exclude = set(clipped) | {p["id"] for p in picks}
    trending = await trending_candidates(profile, cfg, exclude)
    for t in trending:
        t["tier"] = "trending"

    return {
        "channel": picks,
        "trending": trending,
        "profile": {
            "videos": profile.get("videos", 0),
            "labels": profile.get("labels", []),
        },
    }


async def cmd_digest(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    await update.message.reply_text("Scoring latest uploads + trending…")
    res = await build_digest()
    picks = res["channel"] + res["trending"]
    if not picks:
        await update.message.reply_text("No picks (check /sources).")
        return
    await reply_chunks(update.message, render_digest(res))
    for p in picks:
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Clip this", callback_data=f"clip:{p['id']}")]]
        )
        await update.message.reply_text(_fmt_pick(p), reply_markup=kb)
    mark_shown(picks)


async def on_clip_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not check_user(update):
        return
    vid = query.data.split(":", 1)[1]
    cfg = load_bot_config()
    job = enqueue(f"https://youtu.be/{vid}", cfg)
    set_job(job["id"], chat_id=query.message.chat_id)
    msg = await query.message.reply_text(f"[{job['id']}] queued: https://youtu.be/{vid}")
    set_job(job["id"], msg_id=msg.message_id, chat_id=query.message.chat_id)
    asyncio.create_task(worker_loop(ctx.application))


async def on_retry_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not check_user(update):
        return
    job_id = query.data.split(":", 1)[1]
    if not find_job(job_id):
        await query.message.reply_text("Job not found.")
        return
    set_job(job_id, status="queued", stage="-", detail="requeued", reason="", started=None)
    await query.message.reply_text(f"[{job_id}] requeued — resuming from cache.")
    asyncio.create_task(worker_loop(ctx.application))


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    await update.message.reply_text(
        "Jobs\n"
        "/clip <url> [--style X] [--preset Y] [--max N] [--layout auto|crop|fit] "
        "[--smart-crop] [--follow] [--loudnorm] [--fresh] — queue a clip\n"
        "  --follow cuts to the active speaker per source shot (forces crop)\n"
        "  repeats reuse the previous run's transcript/ranking; --fresh re-ranks\n"
        "/status [job] — stage, elapsed, failure reason\n"
        "/logs <job> — last 40 log lines\n"
        "/retry <job> — requeue a failed job from cache\n"
        "/queue — recent jobs\n"
        "/cancel <job> — kill a job\n"
        "/digest — theme-grouped picks + trending (deduped)\n"
        "/costs [YYYY-MM] — spend summary\n"
        "\nConfig\n"
        "/config — show ALL configuration (bot + pipeline + styles + presets)\n"
        "/config <key> [value] — bot defaults: style, preset, max_clips, digest_time\n"
        "/settings [section[.key]] — view pipeline settings (read-only)\n"
        "/set <section.key> <value> — curated override, writes settings.yaml\n"
        "/style [name] — list/show caption styles\n"
        "/preset [name] — list/show platform presets\n"
        "/sources [list|add|rm] — manage channels\n"
        "\nOr just paste a YouTube URL."
    )


async def digest_job(app):
    if not ALLOWED_USER:
        return
    res = await build_digest()
    picks = res["channel"] + res["trending"]
    if not picks:
        return
    try:
        await app.bot.send_message(ALLOWED_USER, render_digest(res))
        mark_shown(picks)
    except Exception as e:  # noqa: BLE001 - digest is best-effort
        print(f"digest send failed: {e}")


async def post_init(app):
    cfg = load_bot_config()
    hh, mm = (cfg.get("digest_time", "07:00") + ":00").split(":")[:2]
    now = time.localtime()
    target = time.mktime(
        (now.tm_year, now.tm_mon, now.tm_mday, int(hh), int(mm), 0, 0, 0, -1)
    )
    delay = max(target - time.time(), 60)
    asyncio.get_event_loop().call_later(delay, lambda: asyncio.create_task(digest_loop(app)))
    orphans = recover_orphans()
    if orphans:
        print(f"recovered {len(orphans)} orphaned running job(s)")
    queued = [j for j in load_queue()["jobs"] if j["status"] == "queued"]
    if queued:
        print(f"resuming {len(queued)} queued job(s)")
        asyncio.create_task(worker_loop(app))


async def digest_loop(app):
    while True:
        await digest_job(app)
        await asyncio.sleep(86400)


def build_app(token):
    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler("clip", cmd_clip))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("retry", cmd_retry))
    app.add_handler(CommandHandler("queue", cmd_queue))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("costs", cmd_costs))
    app.add_handler(CommandHandler("config", cmd_config))
    app.add_handler(CommandHandler("settings", cmd_settings))
    app.add_handler(CommandHandler("set", cmd_set))
    app.add_handler(CommandHandler("style", cmd_style))
    app.add_handler(CommandHandler("preset", cmd_preset))
    app.add_handler(CommandHandler("sources", cmd_sources))
    app.add_handler(CommandHandler("digest", cmd_digest))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_clip_button, pattern=r"^clip:"))
    app.add_handler(CallbackQueryHandler(on_retry_button, pattern=r"^retry:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_url_shorthand))
    return app


def main():
    token = _env("TELEGRAM_TOKEN")
    if not token:
        print("Set TELEGRAM_TOKEN (or TELEGRAM_BOT_TOKEN).")
        raise SystemExit(2)
    backoff = 5
    while True:
        app = build_app(token)
        print("clipbot polling…")
        try:
            app.run_polling(drop_pending_updates=True)
            break
        except NetworkError as e:
            print(f"polling network error: {e} — restarting in {backoff}s")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--once-digest", action="store_true", help="print digest and exit")
    a = ap.parse_args()
    if a.once_digest:
        print(json.dumps(asyncio.run(build_digest()), indent=1, ensure_ascii=False))
    else:
        main()
