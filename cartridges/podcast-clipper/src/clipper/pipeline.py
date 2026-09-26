import json
import os
import re
import time

import yaml

from .clip import cut_clips
from .download import download
from .prefilter import prefilter
from .rank import rank
from .settings_schema import apply_overrides

COSTS_LOG = os.path.join("work", "costs.jsonl")

GROQ_STT_USD_PER_MIN = 0.0  # free tier default; override via settings
ROUTER_USD_PER_1K = 0.0  # unknown gateway pricing; tokens still logged


def _log_cost(entry):
    os.makedirs(os.path.dirname(COSTS_LOG), exist_ok=True)
    with open(COSTS_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def list_presets(presets_dir="config/presets"):
    if not os.path.exists(presets_dir):
        alt = os.path.join(ROOT_DIR, presets_dir)
        if os.path.exists(alt):
            presets_dir = alt
    try:
        return sorted(f[:-5] for f in os.listdir(presets_dir) if f.endswith(".yaml"))
    except OSError:
        return []


def apply_preset(settings, preset=None):
    if not preset:
        return settings
    path = os.path.join("config", "presets", f"{preset}.yaml")
    if not os.path.exists(path):
        alt = os.path.join(ROOT_DIR, path)
        if os.path.exists(alt):
            path = alt
        else:
            valid = list_presets()
            raise ValueError(f"unknown preset '{preset}'. Valid: {valid}")
    with open(path) as f:
        p = yaml.safe_load(f) or {}
    import copy

    settings = copy.deepcopy(settings)
    for k, v in (p.get("clips") or {}).items():
        settings.setdefault("clips", {})[k] = v
    settings["_caption_overrides"] = p.get("caption") or {}
    settings["_preset"] = preset
    return settings


def process(
    url,
    settings,
    name="job",
    style=None,
    max_clips=None,
    skip_transcribe=False,
    skip_rank=False,
    preset=None,
    overrides=None,
):
    settings = apply_preset(settings, preset)
    settings = apply_overrides(settings, overrides)
    paths = settings["paths"]
    work_dir = os.path.join(paths["work_dir"], name)
    out_dir = os.path.join(paths["output_dir"], name)
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    print("[1/5] download")
    t0 = time.monotonic()
    stage_s = {}
    dl = download(url, work_dir, settings)
    stage_s["download"] = max(0.0, round(time.monotonic() - t0, 1))
    print(f"  {dl['title']} ({dl['duration']}s)")

    t_path = os.path.join(work_dir, "transcript.json")
    if skip_transcribe and os.path.exists(t_path):
        print("[2/5] transcribe (cached)")
        with open(t_path) as f:
            t = json.load(f)
        stage_s["transcribe"] = 0.0
    else:
        print("[2/5] transcribe")
        from .transcribe import transcribe

        t0 = time.monotonic()
        t = transcribe(dl["audio"], settings, out_path=t_path)
        stage_s["transcribe"] = max(0.0, round(time.monotonic() - t0, 1))
        print(f"  backend={t['backend']} segments={len(t['segments'])}")

    print("[3/5] prefilter")
    t0 = time.monotonic()
    c_path = os.path.join(work_dir, "candidates.json")
    cands = prefilter(t, settings, out_path=c_path)
    stage_s["prefilter"] = max(0.0, round(time.monotonic() - t0, 1))
    print(f"  {len(cands)} candidates")

    r_path = os.path.join(work_dir, "ranked.json")
    rank_meta = {
        "model": "",
        "temperature": None,
        "seed": None,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }
    if skip_rank and os.path.exists(r_path):
        print("[4/5] rank (cached)")
        with open(r_path) as f:
            ranked = json.load(f)
        stage_s["rank"] = 0.0
        meta_path = os.path.join(work_dir, "rank_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path) as f:
                    rank_meta = json.load(f)
            except (OSError, json.JSONDecodeError):
                pass
    else:
        print("[4/5] rank")
        t0 = time.monotonic()
        ranked, rank_meta = rank(cands, settings, out_path=r_path)
        stage_s["rank"] = max(0.0, round(time.monotonic() - t0, 1))
        for r in ranked[:5]:
            print(f"  [{r['id']}] score={r['score']} {r['hook'][:70]}")

    print("[5/5] clips")
    t0 = time.monotonic()
    made = cut_clips(
        dl["source"], ranked, out_dir, settings, style=style, max_clips=max_clips
    )
    stage_s["clips"] = max(0.0, round(time.monotonic() - t0, 1))
    for m in made:
        print(f"  {m['clip']} ({m['start']:.0f}-{m['end']:.0f}s score={m['score']})")
    audio_min = round((dl.get("duration") or 0) / 60.0, 2)
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "name": name,
        "url": url,
        "stage_s": stage_s,
        "groq": {"audio_min": audio_min, "usd": round(audio_min * GROQ_STT_USD_PER_MIN, 4)},
        "rank": rank_meta,
        "router_usd": round(rank_meta["total_tokens"] / 1000.0 * ROUTER_USD_PER_1K, 4),
        "clips": len(made),
    }
    try:
        _log_cost(entry)
    except OSError as e:
        print(f"  cost log skipped: {e}")
    return {"download": dl, "transcript": t_path, "ranked": r_path, "clips": made}


def _slug(url, i):
    slug = re.sub(r"\W+", "-", url.rstrip("/").split("/")[-1].split("?")[0])
    return slug.strip("-").lower() or f"src{i}"


def batch(
    settings,
    sources_path="config/sources.yaml",
    style=None,
    max_clips=None,
    skip_transcribe=False,
    skip_rank=False,
    preset=None,
    overrides=None,
):
    with open(sources_path) as f:
        entries = (yaml.safe_load(f) or {}).get("sources", [])
    ok, failed = [], []
    for i, e in enumerate(entries):
        name = e.get("name") or _slug(e["url"], i)
        print(f"=== [{i + 1}/{len(entries)}] {name} ===")
        src_over = dict(overrides or {})
        if e.get("layout"):
            src_over["clips.layout"] = e["layout"]
        if "follow_speaker" in e:
            src_over["clips.follow_speaker"] = bool(e["follow_speaker"])
        src_over.update(e.get("overrides") or {})
        try:
            res = process(
                e["url"],
                settings,
                name=name,
                style=style or e.get("style"),
                max_clips=max_clips or e.get("max_clips"),
                skip_transcribe=skip_transcribe,
                skip_rank=skip_rank,
                preset=preset or e.get("preset"),
                overrides=src_over,
            )
            ok.append({"name": name, "url": e["url"], "clips": len(res["clips"])})
        except Exception as ex:  # noqa: BLE001 - continue-on-error by design
            print(f"  FAILED {name}: {ex}")
            failed.append({"name": name, "url": e["url"], "error": str(ex)})
    print(f"batch done: {len(ok)} ok, {len(failed)} failed")
    for f in failed:
        print(f"  FAIL {f['name']}: {f['error'][:120]}")
    return {"ok": ok, "failed": failed}
