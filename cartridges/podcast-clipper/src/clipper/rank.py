import json
import os
import re
import time
import urllib.request


def call_9router(messages, settings, model=None):
    cfg = settings["nine_router"]
    key = os.environ[cfg["api_key_env"]]
    body = {
        "model": model or cfg["rank_model"],
        "messages": messages,
        "max_tokens": cfg.get("max_tokens", 2000),
        "stream": False,
    }
    if cfg.get("temperature") is not None:
        body["temperature"] = cfg["temperature"]
    if cfg.get("seed") is not None:
        body["seed"] = cfg["seed"]
    body = json.dumps(body).encode()
    req = urllib.request.Request(
        cfg["base_url"] + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
    )
    with urllib.request.urlopen(req, timeout=cfg.get("timeout_s", 120)) as r:
        return json.load(r)


def rank_models(settings):
    cfg = settings["nine_router"]
    models = list(cfg.get("rank_models") or [])
    primary = cfg.get("rank_model")
    if primary and primary not in models:
        models.insert(0, primary)
    return models


def parse_json_array(text):
    text = text.strip()
    text = re.sub(r"^```\w*\n?", "", text).strip()
    text = re.sub(r"\n?```\s*$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("[")
    if start != -1:
        frag = text[start:]
        for end in range(len(frag), 0, -1):
            try:
                obj = json.loads(frag[:end])
                if isinstance(obj, list):
                    return obj
            except json.JSONDecodeError:
                continue
        m = re.findall(r"\{[^{}]*\}", frag)
        if m:
            return [json.loads(x) for x in m]
    raise json.JSONDecodeError("no JSON array found", text, 0)


ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def rank(candidates, settings, prompt_path="prompts/rank_v1.txt", out_path=None):
    if not os.path.exists(prompt_path):
        alt = os.path.join(ROOT_DIR, prompt_path)
        if os.path.exists(alt):
            prompt_path = alt
    with open(prompt_path) as f:
        template = f.read()
    cand_text = "\n\n".join(
        f"[{c['id']}] ({c['start']:.0f}s-{c['end']:.0f}s): {c['text']}"
        for c in candidates
    )
    prompt = template.replace("{candidates}", cand_text)
    content = ""
    resp = {}
    used_model = ""
    last_err = None
    models = rank_models(settings)
    attempts = max(3, len(models) * 2)
    for attempt in range(attempts):
        model = models[attempt % len(models)]
        try:
            resp = call_9router([{"role": "user", "content": prompt}], settings, model)
        except Exception as e:  # noqa: BLE001 - retry/fallback on transient failure
            last_err = f"{model} request failed (attempt {attempt + 1}): {e}"
            time.sleep(min(2 * (attempt + 1), 8))
            continue
        content = (resp["choices"][0]["message"].get("content") or "").strip()
        if content:
            used_model = model
            break
        last_err = f"{model} empty content (attempt {attempt + 1})"
        time.sleep(min(2 * (attempt + 1), 8))
    if not content:
        raise RuntimeError(
            f"rank failed after {attempts} attempts: {last_err}\n"
            f"models tried: {models}\nraw resp: {json.dumps(resp)[:500]}"
        )
    try:
        scores = parse_json_array(content)
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"rank parse failed: {e}\nraw: {content[:500]}")
    by_id = {c["id"]: c for c in candidates}
    ranked = []
    for s in scores:
        c = by_id.get(s["id"])
        if not c:
            continue
        ranked.append(
            {
                **c,
                "score": s.get("score", 0),
                "hook": s.get("hook", ""),
                "reason": s.get("reason", ""),
                "title": (s.get("title", "") or "")[:60],
                "description": s.get("description", ""),
                "thumbnail_s": float(s.get("thumbnail_s", (c["end"] - c["start"]) / 2)),
            }
        )
    ranked.sort(key=lambda c: -c["score"])
    deduped, used = [], []
    for c in ranked:
        if all(c["start"] >= e or c["end"] <= s for s, e in used):
            deduped.append(c)
            used.append((c["start"], c["end"]))
    usage = (resp.get("usage") or {}) if isinstance(resp, dict) else {}
    nr = settings["nine_router"]
    meta = {
        "model": used_model or settings["nine_router"]["rank_model"],
        "models_tried": models,
        "temperature": nr.get("temperature"),
        "seed": nr.get("seed"),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }
    if out_path:
        with open(out_path, "w") as f:
            json.dump(deduped, f, indent=1)
        meta_path = (
            out_path.replace("ranked.json", "rank_meta.json")
            if "ranked.json" in out_path
            else out_path + ".meta.json"
        )
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=1)
    return deduped, meta
