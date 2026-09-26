import json
import os
import subprocess

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def probe_dims(path):
    r = subprocess.run(
        [FFMPEG, "-i", path], capture_output=True, text=True, check=False
    )
    import re

    m = re.search(r"Video:.*?, (\d+)x(\d+)", r.stderr)
    if not m:
        raise RuntimeError(f"cannot probe dims: {path}")
    return int(m.group(1)), int(m.group(2))


def pick_layout(cfg, sw, sh):
    layout = (cfg.get("layout") or "auto").lower()
    if layout == "auto":
        if cfg.get("follow_speaker"):
            return "crop"
        ratio = sw / sh if sh else 1.0
        return "fit" if ratio >= float(cfg.get("fit_ratio", 2.0)) else "crop"
    return layout if layout in ("crop", "fit") else "crop"


def build_vf(cfg, sw, sh, W, H, source=None, start=None, end=None, settings=None):
    layout = pick_layout(cfg, sw, sh)
    if layout == "fit":
        if cfg.get("follow_speaker"):
            print("  follow_speaker ignored (layout=fit keeps the full frame)")
        sigma = cfg.get("fit_blur_sigma", 25)
        bright = cfg.get("fit_brightness", -0.18)
        return (
            f"[0:v]split=2[bg][fg];"
            f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},gblur=sigma={sigma},eq=brightness={bright}[bg2];"
            f"[fg]scale={W}:-2[fg2];"
            f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2"
        ), layout
    target_ratio = W / H
    src_ratio = sw / sh if sh else 1.0
    if src_ratio > target_ratio:
        cw, ch = int(sh * target_ratio), sh
    else:
        cw, ch = sw, int(sw / target_ratio)
    cx, cy = (sw - cw) // 2, (sh - ch) // 2
    x_expr = None
    if cfg.get("follow_speaker") and source and start is not None and end is not None:
        from .follow import build_x_expr, target_timeline

        shots = target_timeline(source, start, end, settings)
        x_expr = build_x_expr(shots, start, sw, cw)
        if x_expr:
            xs = " ".join(f"{s['x']:.2f}" for s in shots)
            print(f"  follow_speaker {len(shots)} cuts x=[{xs}]")
    if x_expr is not None:
        return f"crop={cw}:{ch}:'{x_expr}':{cy},scale={W}:{H}", layout
    if cfg.get("smart_crop", False) and source:
        from .smartcrop import smart_cx

        fx = smart_cx(source, start, end, settings)
        if fx is not None:
            cx = int(min(max(fx * sw - cw / 2, 0), sw - cw))
            print(f"  smart_crop x={fx:.2f} cx={cx}")
    return f"crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}", layout


def make_clip(source, start, end, out_path, settings=None, subtitles=None):
    cfg = (settings or {}).get("clips", {})
    W, H = cfg.get("width", 1080), cfg.get("height", 1920)
    crf = str(cfg.get("crf", 20))
    x264_preset = cfg.get("x264_preset", "fast")
    loudnorm = cfg.get("loudnorm", False)
    trim_silence = cfg.get("trim_silence", False)
    sw, sh = probe_dims(source)
    vf, layout = build_vf(cfg, sw, sh, W, H, source, start, end, settings)
    print(f"  layout={layout} ({sw}x{sh})")
    if subtitles:
        safe = subtitles.replace("'", "'\\''")
        vf += f",subtitles='{safe}'"
    af = []
    if trim_silence:
        af.append("silenceremove=start_periods=1:start_duration=0.3:start_threshold=-50dB")
    if loudnorm:
        af.append("loudnorm=I=-16:TP=-1.5:LRA=11")
    dur = end - start
    cmd = [
        FFMPEG,
        "-y",
        "-ss",
        str(start),
        "-i",
        source,
        "-t",
        str(dur),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        x264_preset,
        "-crf",
        crf,
        "-c:a",
        "aac",
        "-b:a",
        "128k",
    ]
    if af:
        cmd += ["-af", ",".join(af)]
    cmd += ["-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path


def cut_clips(
    source, ranked, out_dir, settings=None, style=None, max_clips=None, offset=0.0
):
    from .caption import write_ass, write_srt, write_vtt

    cfg = (settings or {}).get("clips", {})
    n = max_clips or cfg.get("max_clips", 3)
    style = style or cfg.get("default_style", "hormozi")
    sidecars = cfg.get("sidecars", ["ass", "srt", "vtt"])
    cap_ov = (settings or {}).get("_caption_overrides") or {}
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for i, c in enumerate(ranked[:n]):
        shifted = {**c, "start": c["start"] + offset, "end": c["end"] + offset}
        shifted["words"] = [
            {**w, "start": w["start"] + offset, "end": w["end"] + offset}
            for w in c.get("words", [])
        ]
        ass = os.path.join(out_dir, f"clip{i}.ass")
        write_ass(shifted, ass, style, base_offset=shifted["start"], overrides=cap_ov)
        extra = {}
        if "srt" in sidecars:
            extra["srt"] = os.path.join(out_dir, f"clip{i}.srt")
            write_srt(shifted, extra["srt"], style, base_offset=shifted["start"], overrides=cap_ov)
        if "vtt" in sidecars:
            extra["vtt"] = os.path.join(out_dir, f"clip{i}.vtt")
            write_vtt(shifted, extra["vtt"], style, base_offset=shifted["start"], overrides=cap_ov)
        mp4 = os.path.join(out_dir, f"clip{i}.mp4")
        make_clip(
            source, shifted["start"], shifted["end"], mp4, settings, subtitles=ass
        )
        dur = max(shifted["end"] - shifted["start"], 0.1)
        thumb_off = min(max(float(c.get("thumbnail_s", dur / 2)), 0), dur - 0.1)
        meta = {
            "title": c.get("title", ""),
            "description": c.get("description", ""),
            "hook": c.get("hook", ""),
            "score": c.get("score", 0),
            "start": shifted["start"],
            "end": shifted["end"],
            "thumbnail_s": round(thumb_off, 2),
        }
        meta_path = os.path.join(out_dir, f"clip{i}.meta.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=1, ensure_ascii=False)
        thumb_path = os.path.join(out_dir, f"clip{i}.thumb.jpg")
        try:
            subprocess.run(
                [
                    FFMPEG,
                    "-y",
                    "-v",
                    "error",
                    "-ss",
                    str(shifted["start"] + thumb_off),
                    "-i",
                    source,
                    "-frames:v",
                    "1",
                    "-q:v",
                    "3",
                    thumb_path,
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            thumb_path = None
        made.append(
            {
                "clip": mp4,
                "ass": ass,
                **extra,
                "meta": meta_path,
                "thumb": thumb_path,
                "score": c.get("score", 0),
                "start": shifted["start"],
                "end": shifted["end"],
            }
        )
    return made
