import json
import os
import subprocess
from typing import Optional, Dict, Any, List

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def resolve_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    font_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in font_candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def render_banner_overlay(
    out_png_path: str,
    text: str,
    banner_cfg: Optional[Dict[str, Any]] = None,
    logo_path: Optional[str] = None,
    logo_cfg: Optional[Dict[str, Any]] = None,
    width: int = 1080,
    height: int = 1920,
) -> Optional[str]:
    """
    Renders a modular top hook banner and/or campaign logo watermark
    onto a transparent 1080x1920 PNG overlay.
    Only renders components that are explicitly enabled by the campaign profile.
    """
    banner_cfg = banner_cfg or {}
    logo_cfg = logo_cfg or {}
    banner_enabled = bool(banner_cfg.get("enabled", False) and text)
    logo_enabled = bool(logo_cfg.get("enabled", False) and logo_path and os.path.exists(logo_path))

    if not banner_enabled and not logo_enabled:
        return None

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    if banner_enabled:
        font_size = int(banner_cfg.get("font_size", 44))
        font = resolve_font(font_size, bold=True)
        max_line_w = int(banner_cfg.get("max_width", 880))
        y_top = int(banner_cfg.get("y", 160))
        text_color = banner_cfg.get("text_color", "#FFEB3B")
        bg_raw = banner_cfg.get("bg_color", [18, 18, 22, 225])
        bg_color = tuple(bg_raw) if isinstance(bg_raw, list) else (18, 18, 22, 225)
        border_raw = banner_cfg.get("border_color", [255, 235, 59, 180])
        border_color = tuple(border_raw) if isinstance(border_raw, list) else None
        border_width = int(banner_cfg.get("border_width", 3))
        corner_radius = int(banner_cfg.get("radius", 26))

        # Multi-line word wrap
        words = text.strip().split()
        lines: List[str] = []
        curr: List[str] = []
        for w in words:
            test = " ".join(curr + [w])
            bbox = draw.textbbox((0, 0), test, font=font)
            if (bbox[2] - bbox[0]) <= max_line_w:
                curr.append(w)
            else:
                if curr:
                    lines.append(" ".join(curr))
                curr = [w]
        if curr:
            lines.append(" ".join(curr))

        line_height = int(font_size * 1.25)
        total_text_h = len(lines) * line_height
        max_w = 0
        for line in lines:
            bb = draw.textbbox((0, 0), line, font=font)
            max_w = max(max_w, bb[2] - bb[0])

        pad_x = 42
        pad_y = 20
        box_w = max_w + (pad_x * 2)
        box_h = total_text_h + (pad_y * 2)
        box_x = (width - box_w) // 2
        box_y = y_top

        # Draw rounded rectangle pill box
        draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=corner_radius,
            fill=bg_color,
            outline=border_color if border_width > 0 else None,
            width=border_width,
        )

        # Draw centered text lines with drop shadow
        for idx, line in enumerate(lines):
            line_bb = draw.textbbox((0, 0), line, font=font)
            lw = line_bb[2] - line_bb[0]
            lx = (width - lw) // 2
            ly = box_y + pad_y + (idx * line_height)
            draw.text((lx + 2, ly + 2), line, font=font, fill=(0, 0, 0, 220))
            draw.text((lx, ly), line, font=font, fill=text_color)

    if logo_enabled and logo_path:
        try:
            with Image.open(logo_path) as logo:
                logo_rgba = logo.convert("RGBA")
                max_w = int(logo_cfg.get("max_width", 160))
                max_h = int(logo_cfg.get("max_height", 80))
                logo_rgba.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

                pos = logo_cfg.get("position", "top-right")
                if pos == "top-left":
                    lx, ly = 40, 40
                else:  # top-right
                    lx, ly = width - logo_rgba.width - 40, 40
                canvas.alpha_composite(logo_rgba, (lx, ly))
        except Exception as e:
            print(f"  [warn] failed to composite logo {logo_path}: {e}")

    os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
    canvas.save(out_png_path, "PNG")
    return out_png_path


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


def make_clip(
    source,
    start,
    end,
    out_path,
    settings=None,
    subtitles=None,
    overlay_path=None,
    ambience_path=None,
    ambience_volume=0.12,
):
    cfg = (settings or {}).get("clips", {})
    W, H = cfg.get("width", 1080), cfg.get("height", 1920)
    crf = str(cfg.get("crf", 20))
    x264_preset = cfg.get("x264_preset", "fast")
    loudnorm = cfg.get("loudnorm", False)
    trim_silence = cfg.get("trim_silence", False)
    sw, sh = probe_dims(source)
    dur = end - start

    base_vf, layout = build_vf(cfg, sw, sh, W, H, source, start, end, settings)
    print(f"  layout={layout} ({sw}x{sh})")

    has_overlay = bool(overlay_path and os.path.exists(overlay_path))
    has_ambience = bool(ambience_path and os.path.exists(ambience_path))

    cmd = [FFMPEG, "-y", "-ss", str(start), "-i", source, "-t", str(dur)]
    input_idx = 1
    overlay_idx = None
    ambience_idx = None

    if has_overlay:
        cmd += ["-i", overlay_path]
        overlay_idx = input_idx
        input_idx += 1

    if has_ambience:
        cmd += ["-stream_loop", "-1", "-i", ambience_path]
        ambience_idx = input_idx
        input_idx += 1

    sub_filter = ""
    if subtitles:
        safe_subs = subtitles.replace("'", "'\\''")
        sub_filter = f",subtitles='{safe_subs}'"

    filter_chains = []
    # Video branch
    if has_overlay:
        v_chain = f"[0:v]{base_vf}[base];[base][{overlay_idx}:v]overlay=0:0{sub_filter}[v]"
    else:
        v_chain = f"[0:v]{base_vf}{sub_filter}[v]"
    filter_chains.append(v_chain)

    # Audio branch
    voice_af = []
    if trim_silence:
        voice_af.append("silenceremove=start_periods=1:start_duration=0.3:start_threshold=-50dB")

    if has_ambience:
        m_vol = max(0.01, min(float(ambience_volume), 0.5))
        a_chain = (
            f"[{ambience_idx}:a]volume={m_vol}[bgm];"
            f"[bgm][0:a]sidechaincompress=threshold=0.08:ratio=4:attack=50:release=300[duck_bgm];"
            f"[0:a][duck_bgm]amix=inputs=2:duration=first:dropout_transition=2[a_mix]"
        )
        if loudnorm:
            a_chain += ";[a_mix]loudnorm=I=-16:TP=-1.5:LRA=11[a]"
        else:
            a_chain += ";[a_mix]anull[a]"
        filter_chains.append(a_chain)
    else:
        if loudnorm:
            voice_af.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        if voice_af:
            filter_chains.append(f"[0:a]{','.join(voice_af)}[a]")
        else:
            filter_chains.append("[0:a]anull[a]")

    cmd += [
        "-filter_complex",
        ";".join(filter_chains),
        "-map",
        "[v]",
        "-map",
        "[a]",
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
        "-movflags",
        "+faststart",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path


def cut_clips(
    source,
    ranked,
    out_dir,
    settings=None,
    style=None,
    max_clips=None,
    offset=0.0,
    campaign_profile=None,
):
    from .caption import write_ass, write_srt, write_vtt

    cfg = (settings or {}).get("clips", {})
    n = max_clips or cfg.get("max_clips", 3)
    style = style or cfg.get("default_style", "hormozi")
    sidecars = cfg.get("sidecars", ["ass", "srt", "vtt"])
    cap_ov = (settings or {}).get("_caption_overrides") or {}
    camp_prof = campaign_profile or (settings or {}).get("_campaign_profile") or {}
    banner_cfg = camp_prof.get("banner", {})
    logo_cfg = camp_prof.get("logo", {})
    ambience_cfg = camp_prof.get("ambience", {})

    os.makedirs(out_dir, exist_ok=True)
    made = []
    W, H = cfg.get("width", 1080), cfg.get("height", 1920)

    # Resolve ambience music track if requested
    ambience_path = None
    ambience_vol = float(ambience_cfg.get("volume", 0.12))
    if ambience_cfg.get("enabled", False):
        raw_track = ambience_cfg.get("track")
        if raw_track:
            candidate_paths = [
                raw_track,
                os.path.join(ROOT_DIR, raw_track),
                os.path.join(ROOT_DIR, "assets", "music", raw_track),
                os.path.join(ROOT_DIR, "..", "..", "assets", "music", raw_track),
                os.path.join(ROOT_DIR, "..", "..", "assets", "music", "ambient_sleep_bed.mp3"),
            ]
            for cp in candidate_paths:
                if os.path.exists(cp):
                    ambience_path = cp
                    break

    # Resolve logo path if requested
    logo_path = None
    if logo_cfg.get("enabled", False):
        raw_logo = logo_cfg.get("path")
        if raw_logo:
            for lp in [raw_logo, os.path.join(ROOT_DIR, raw_logo), os.path.join(ROOT_DIR, "..", "..", raw_logo)]:
                if os.path.exists(lp):
                    logo_path = lp
                    break

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

        # Generate overlay only if winner/campaign has banner or logo enabled
        overlay_path = None
        banner_text = c.get("banner_hook") or c.get("title", "")
        if banner_cfg.get("enabled", False) or (logo_cfg.get("enabled", False) and logo_path):
            ov_out = os.path.join(out_dir, f"clip{i}_overlay.png")
            overlay_path = render_banner_overlay(
                out_png_path=ov_out,
                text=banner_text,
                banner_cfg=banner_cfg,
                logo_path=logo_path,
                logo_cfg=logo_cfg,
                width=W,
                height=H,
            )

        mp4 = os.path.join(out_dir, f"clip{i}.mp4")
        make_clip(
            source=source,
            start=shifted["start"],
            end=shifted["end"],
            out_path=mp4,
            settings=settings,
            subtitles=ass,
            overlay_path=overlay_path,
            ambience_path=ambience_path,
            ambience_volume=ambience_vol,
        )

        dur = max(shifted["end"] - shifted["start"], 0.1)
        thumb_off = min(max(float(c.get("thumbnail_s", dur / 2)), 0), dur - 0.1)

        tags = c.get("hashtags", [])
        if not tags and c.get("description"):
            tags = [t.strip() for t in c.get("description", "").split() if t.startswith("#")]

        meta = {
            "title": c.get("title", ""),
            "banner_hook": c.get("banner_hook", ""),
            "description": c.get("description", ""),
            "hashtags": tags,
            "hook": c.get("hook", ""),
            "score": c.get("score", 0),
            "start": shifted["start"],
            "end": shifted["end"],
            "thumbnail_s": round(thumb_off, 2),
            "campaign": camp_prof.get("name") or camp_prof.get("campaign"),
            "submission_ready": {
                "platform_title": f"{c.get('title', '')} {' '.join(tags)}".strip(),
                "full_description": f"{c.get('description', '')}\n\n{' '.join(tags)}".strip(),
                "timestamp_proof": f"{shifted['start']:.0f}s - {shifted['end']:.0f}s",
            },
        }
        meta_path = os.path.join(out_dir, f"clip{i}.meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

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
                "submission_ready": meta["submission_ready"],
            }
        )
    return made
