"""Curated, validated overrides for pipeline settings.

Shared by the CLI (`--set section.key=value`) and the Telegram bot (`/set`).
Only keys in SETTABLE may be changed; everything else in settings.yaml is
read-only. Validation returns a typed value or a human error message.
"""

SETTABLE = {
    "clips.layout": {"type": "enum", "values": ["auto", "crop", "fit"]},
    "clips.smart_crop": {"type": "bool"},
    "clips.follow_speaker": {"type": "bool"},
    "clips.scene_thresh": {"type": "float", "min": 0.05, "max": 0.6},
    "clips.follow_fps": {"type": "float", "min": 0.5, "max": 5.0},
    "clips.follow_min_dwell": {"type": "float", "min": 0.4, "max": 3.0},
    "clips.loudnorm": {"type": "bool"},
    "clips.trim_silence": {"type": "bool"},
    "clips.crf": {"type": "int", "min": 14, "max": 28},
    "clips.fit_ratio": {"type": "float", "min": 1.0, "max": 4.0},
    "clips.max_clips": {"type": "int", "min": 1, "max": 10},
    "clips.smart_crop_samples": {"type": "int", "min": 2, "max": 30},
    "prefilter.min_clip_s": {"type": "int", "min": 5, "max": 120},
    "prefilter.max_clip_s": {"type": "int", "min": 15, "max": 180},
    "prefilter.max_candidates": {"type": "int", "min": 1, "max": 50},
    "prefilter.skip_intro_outro_s": {"type": "int", "min": 0, "max": 300},
    "download.max_duration_s": {"type": "int", "min": 60, "max": 7200},
    "transcribe.local_model": {
        "type": "enum",
        "values": ["tiny", "base", "small", "medium", "large-v3"],
    },
    "transcribe.local_compute": {
        "type": "enum",
        "values": ["int8", "int8_float16", "float16", "float32"],
    },
    "nine_router.rank_model": {"type": "str", "min_len": 1},
    "nine_router.temperature": {"type": "float", "min": 0.0, "max": 1.0},
    "nine_router.seed": {"type": "int", "min": 0, "max": 1000000},
    "nine_router.max_tokens": {"type": "int", "min": 512, "max": 32000},
}

_TRUE = {"true", "1", "yes", "on"}
_FALSE = {"false", "0", "no", "off"}
_NOT_SET = object()


def split_key(key):
    section, _, leaf = key.partition(".")
    return section, leaf


def validate(key, raw, settings=None):
    spec = SETTABLE.get(key)
    if not spec:
        return False, f"'{key}' is not settable (read-only or unknown)", None
    t = spec["type"]
    if t == "bool":
        v = str(raw).strip().lower()
        if v not in _TRUE | _FALSE:
            return False, "expected true/false", None
        val = v in _TRUE
    elif t == "int":
        try:
            val = int(str(raw).strip())
        except ValueError:
            return False, "expected an integer", None
        if not (spec["min"] <= val <= spec["max"]):
            return False, f"must be {spec['min']}..{spec['max']}", None
    elif t == "float":
        try:
            val = float(str(raw).strip())
        except ValueError:
            return False, "expected a number", None
        if not (spec["min"] <= val <= spec["max"]):
            return False, f"must be {spec['min']}..{spec['max']}", None
    elif t == "enum":
        val = str(raw).strip().lower()
        if val not in spec["values"]:
            return False, "must be one of " + "|".join(spec["values"]), None
    else:
        val = str(raw).strip()
        if len(val) < spec.get("min_len", 1):
            return False, "cannot be empty", None
    if settings is not None:
        err = _cross_check(key, val, settings)
        if err:
            return False, err, None
    return True, val, val


def _cross_check(key, val, settings):
    if key == "prefilter.min_clip_s":
        max_s = settings.get("prefilter", {}).get("max_clip_s")
        if max_s is not None and val >= max_s:
            return f"min_clip_s ({val}) must be < max_clip_s ({max_s})"
    if key == "prefilter.max_clip_s":
        min_s = settings.get("prefilter", {}).get("min_clip_s")
        if min_s is not None and val <= min_s:
            return f"max_clip_s ({val}) must be > min_clip_s ({min_s})"
    return None


def set_in(settings, key, val):
    section, leaf = split_key(key)
    settings.setdefault(section, {})[leaf] = val
    return settings


def parse_override(token, settings=None):
    """Parse 'section.key=value'. Returns (settings_key, value) or raises ValueError."""
    if "=" not in token:
        raise ValueError(f"expected section.key=value, got '{token}'")
    key, raw = token.split("=", 1)
    key = key.strip()
    ok, msg, val = validate(key, raw, settings)
    if not ok:
        raise ValueError(f"{key}: {msg}")
    return key, val


def apply_overrides(settings, overrides):
    for key, val in (overrides or {}).items():
        set_in(settings, key, val)
    return settings


def format_schema():
    lines = []
    for key, spec in SETTABLE.items():
        t = spec["type"]
        if t == "enum":
            rule = "|".join(spec["values"])
        elif t == "bool":
            rule = "true|false"
        elif t == "str":
            rule = "text"
        else:
            rule = f"{spec.get('min')}..{spec.get('max')}"
        lines.append(f"{key} = {rule}")
    return "\n".join(lines)
