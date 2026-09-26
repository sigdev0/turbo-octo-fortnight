import json
import os


def load_style(name):
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "config", "styles", f"{name}.json"
    )
    path = os.path.normpath(path)
    if not os.path.exists(path):
        path = os.path.join("config", "styles", f"{name}.json")
    with open(path) as f:
        return json.load(f)


def fmt_time(s):
    h, s = int(s // 3600), s % 3600
    m, s = int(s // 60), s % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def fmt_srt_time(s):
    h, rem = int(s // 3600), s % 3600
    m, sec = int(rem // 60), rem % 60
    ms = round((sec - int(sec)) * 1000)
    sec_i = int(sec)
    if ms == 1000:
        sec_i, ms = sec_i + 1, 0
    return f"{h:02d}:{m:02d}:{sec_i:02d},{ms:03d}"


def fmt_vtt_time(s):
    return fmt_srt_time(s).replace(",", ".")


def chunk_words(words, max_words, gap_threshold=5.0):
    if not words:
        return []
    chunk = [words[0]]
    out = []
    for w in words[1:]:
        if len(chunk) >= max_words or (w["start"] - chunk[-1]["end"]) > gap_threshold:
            out.append(chunk)
            chunk = [w]
        else:
            chunk.append(w)
    if chunk:
        out.append(chunk)
    return out


def fix_words(words, max_word_dur=1.5):
    fixed = []
    for i, w in enumerate(words):
        ws, we = w["start"], w["end"]
        if i + 1 < len(words):
            nxt = words[i + 1]["start"]
            we = min(we, nxt, ws + max_word_dur)
        else:
            we = min(we, ws + max_word_dur)
        if we <= ws:
            we = ws + 0.1
        fixed.append({**w, "start": ws, "end": we})
    return fixed


POSITION_ALIGN = {"top": 8, "center": 5, "bottom": 2}


def resolve_alignment(style, overrides):
    if "alignment" in overrides:
        return overrides["alignment"]
    if "position" in overrides:
        return POSITION_ALIGN.get(overrides["position"], 5)
    if "position" in style:
        return POSITION_ALIGN.get(style["position"], 5)
    return style.get("alignment", 5)


def timed_lines(candidate, style_name="hormozi", base_offset=None, overrides=None):
    overrides = overrides or {}
    st = load_style(style_name)
    align = resolve_alignment(st, overrides)
    st = {**st, **overrides}
    st["alignment"] = align
    if "size_scale" in overrides:
        st["size"] = round(st["size"] * overrides["size_scale"])
    words = candidate.get("words", [])
    start_off = base_offset if base_offset is not None else candidate["start"]
    maxw = st.get("max_words_per_line", 4)
    upper = st.get("uppercase", False)
    max_word_dur = st.get("max_word_dur_s", 1.5)
    out = []
    for chunk in chunk_words(fix_words(words, max_word_dur), maxw):
        t0 = max(chunk[0]["start"] - start_off, 0)
        t1 = max(chunk[-1]["end"] - start_off, t0 + 0.2)
        text = " ".join(w["w"].strip().upper() if upper else w["w"].strip() for w in chunk)
        out.append({"start": t0, "end": t1, "text": text})
    return out, st


def style_line(st):
    return (
        f"Style: Clip,{st['font']},{st['size']},{st['primary_color']},"
        f"{st['highlight_color']},{st['outline_color']},&H000000FF,"
        f"-1,0,0,0,100,100,0,0,1,{st['outline']},{st['shadow']},"
        f"{st['alignment']},40,40,{st['margin_v']},1"
    )


def write_ass(candidate, out_path, style_name="hormozi", base_offset=None, overrides=None):
    lines, st = timed_lines(candidate, style_name, base_offset, overrides)
    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        ),
        style_line(st),
        "",
        "[Events]",
        (
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
            "Effect, Text"
        ),
    ]
    for ln in lines:
        parts = [
            f"{{\\1c{st['highlight_color']}}}{w}{{\\1c{st['primary_color']}}}"
            for w in ln["text"].split()
        ]
        header.append(
            f"Dialogue: 0,{fmt_time(ln['start'])},{fmt_time(ln['end'])},Clip,,0,0,0,,"
            + " ".join(parts)
        )
    with open(out_path, "w") as f:
        f.write("\n".join(header) + "\n")
    return out_path


def write_srt(candidate, out_path, style_name="hormozi", base_offset=None, overrides=None):
    lines, _ = timed_lines(candidate, style_name, base_offset, overrides)
    out = []
    for i, ln in enumerate(lines, 1):
        out.append(str(i))
        out.append(f"{fmt_srt_time(ln['start'])} --> {fmt_srt_time(ln['end'])}")
        out.append(ln["text"])
        out.append("")
    with open(out_path, "w") as f:
        f.write("\n".join(out))
    return out_path


def write_vtt(candidate, out_path, style_name="hormozi", base_offset=None, overrides=None):
    lines, _ = timed_lines(candidate, style_name, base_offset, overrides)
    out = ["WEBVTT", ""]
    for ln in lines:
        out.append(f"{fmt_vtt_time(ln['start'])} --> {fmt_vtt_time(ln['end'])}")
        out.append(ln["text"])
        out.append("")
    with open(out_path, "w") as f:
        f.write("\n".join(out))
    return out_path
