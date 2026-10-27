"""
OmniForge V2 Kinetic Video Compiler.
Renders high-impact vertical documentary video reels (1080x1920 MP4, 30fps)
benchmarked against viral creator Medan Amrulloh (@medanamrulloh).
Features Ken Burns camera dynamics (zoompan), ornate Nusantara geometric borders,
cinematic typography, and synchronized sidechain-ducked audio beds.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class KineticVideoCompiler:
    def __init__(self, ffmpeg_bin: str = "ffmpeg"):
        self.ffmpeg = shutil.which(ffmpeg_bin) or "ffmpeg"
        self.ffprobe = shutil.which("ffprobe") or "ffprobe"

    def _resolve_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        """
        Dynamically resolves the best available sans-serif font across
        Windows, Linux, and macOS, falling back to PIL's default.
        """
        candidate_paths = [
            # Windows
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            # Linux (Debian / Ubuntu / Alpine)
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        # Safe fallback
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    def _wrap_text(
        self,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int,
        draw: ImageDraw.ImageDraw
    ) -> List[str]:
        """Wraps text cleanly without breaking mid-word."""
        words = (text or "").strip().split()
        if not words:
            return []

        lines: List[str] = []
        current_line: List[str] = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    @staticmethod
    def is_video_file(path_str: Optional[str]) -> bool:
        """Determines whether the given path points to a video container."""
        if not path_str:
            return False
        return Path(path_str).suffix.lower() in {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}

    def prepare_scene_background(
        self,
        bg_image_path: Optional[str],
        output_png_path: str,
        resolution: Tuple[int, int] = (1080, 1920)
    ) -> str:
        """
        Loads and prepares a 1080x1920 background image with subtle darkening
        gradients at the header and lower-third safe zones while leaving
        the center 55% crystal clear and vibrant.
        """
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        w, h = resolution

        if bg_image_path and Path(bg_image_path).exists():
            try:
                bg = Image.open(bg_image_path).convert("RGBA")
                bg_ratio = bg.width / bg.height
                target_ratio = w / h
                if bg_ratio > target_ratio:
                    new_h = h
                    new_w = int(h * bg_ratio)
                else:
                    new_w = w
                    new_h = int(w / bg_ratio)
                bg_resized = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
                crop_x = (new_w - w) // 2
                crop_y = (new_h - h) // 2
                canvas = bg_resized.crop((crop_x, crop_y, crop_x + w, crop_y + h))

                # Subtle top and bottom darkening gradients for typography legibility
                overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                ov_draw = ImageDraw.Draw(overlay)
                for y in range(h):
                    rel = y / h
                    if rel < 0.16:
                        alpha = int((1.0 - (rel / 0.16)) * 110)
                    elif rel > 0.70:
                        alpha = int(((rel - 0.70) / 0.30) * 140)
                    else:
                        alpha = 0
                    if alpha > 0:
                        ov_draw.line([(0, y), (w, y)], fill=(8, 8, 12, alpha))
                canvas = Image.alpha_composite(canvas, overlay)
            except Exception:
                canvas = self._draw_procedural_background(w, h)
        else:
            canvas = self._draw_procedural_background(w, h)

        canvas.convert("RGB").save(str(out_path), "PNG")
        return str(out_path)

    def create_scene_overlay(
        self,
        title: str,
        subtitle: str,
        scene_idx: int,
        output_png_path: str,
        resolution: Tuple[int, int] = (1080, 1920),
        total_scenes: int = 4,
        era: Optional[str] = None
    ) -> str:
        """
        Creates a transparent RGBA overlay featuring:
        1. Javanese-inspired gold border frame with corner ornaments.
        2. Top header pill badge and chapter/era indicator.
        3. Completely clear visual center (unobstructed 9:16 footage).
        4. Lower-third cinematic caption card with high-contrast typography.
        """
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        w, h = resolution

        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        # 1. Ornate Javanese-inspired gold border frame
        draw.rectangle([40, 40, w - 40, h - 40], outline=(212, 175, 55, 200), width=3)
        draw.rectangle([52, 52, w - 52, h - 52], outline=(166, 133, 35, 130), width=1)
        for cx, cy in [(40, 40), (w - 40, 40), (40, h - 40), (w - 40, h - 40)]:
            draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(212, 175, 55, 255))
            draw.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=(243, 229, 171, 255))

        # Fonts
        font_badge = self._resolve_font(28, bold=True)
        font_sub = self._resolve_font(22, bold=False)
        font_tag = self._resolve_font(30, bold=True)
        font_body = self._resolve_font(34, bold=False)

        # 2. Header Badge: "MESIN WAKTU NUSANTARA"
        badge_text = "MESIN WAKTU NUSANTARA"
        bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = bbox_b[2] - bbox_b[0]
        bx0 = (w - bw) // 2 - 24
        by0 = 120
        bx1 = (w + bw) // 2 + 24
        by1 = by0 + (bbox_b[3] - bbox_b[1]) + 20
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=(18, 14, 12, 210), outline=(212, 175, 55, 200), width=2)
        draw.text(((w - bw) // 2, by0 + 8), badge_text, font=font_badge, fill=(243, 229, 171, 255))

        # Scene Indicator / Era Subtitle
        if era:
            clean_era = era.split("(")[0].strip()
            scene_label = f"BAGIAN {scene_idx + 1} DARI {total_scenes} • {clean_era.upper()}"
        else:
            scene_label = f"BAGIAN {scene_idx + 1} DARI {total_scenes}"
        bbox_s = draw.textbbox((0, 0), scene_label, font=font_sub)
        sw = bbox_s[2] - bbox_s[0]
        draw.text(((w - sw) // 2, by1 + 14), scene_label, font=font_sub, fill=(210, 210, 220, 220))

        # 3. Lower Third Caption Card (y=1460 to 1760)
        card_x0, card_y0 = 60, 1460
        card_x1, card_y1 = w - 60, 1760
        draw.rounded_rectangle(
            [card_x0, card_y0, card_x1, card_y1],
            radius=20,
            fill=(12, 10, 10, 215),
            outline=(212, 175, 55, 140),
            width=2
        )

        # Mini Accent Line on Card Top
        draw.line([(card_x0 + 30, card_y0), (card_x0 + 150, card_y0)], fill=(212, 175, 55, 255), width=3)

        # Headline Tag
        tag_text = (title or "").strip().upper()
        draw.text((card_x0 + 40, card_y0 + 32), tag_text, font=font_tag, fill=(243, 229, 171, 255))
        draw.line([(card_x0 + 40, card_y0 + 78), (card_x1 - 40, card_y0 + 78)], fill=(212, 175, 55, 100), width=1)

        # Caption Body
        caption_lines = self._wrap_text(subtitle, font_body, card_x1 - card_x0 - 80, draw)
        line_y = card_y0 + 102
        for line in caption_lines:
            bb = draw.textbbox((0, 0), line, font=font_body)
            # Drop shadow
            draw.text((card_x0 + 41, line_y + 2), line, font=font_body, fill=(0, 0, 0, 220))
            # Text
            draw.text((card_x0 + 40, line_y), line, font=font_body, fill=(245, 245, 250, 255))
            line_y += (bb[3] - bb[1]) + 18

        canvas.save(str(out_path), "PNG")
        return str(out_path)

    def create_scene_card(
        self,
        title: str,
        subtitle: str,
        scene_idx: int,
        output_png_path: str,
        bg_image_path: Optional[str] = None,
        resolution: Tuple[int, int] = (1080, 1920),
        total_scenes: int = 4,
        era: Optional[str] = None
    ) -> str:
        """
        Creates a high-contrast cinematic scene keyframe canvas.
        Composites background and typography overlay for backward compatibility.
        """
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        w, h = resolution

        # 1. Prepare background
        bg_tmp = out_path.with_name(f"{out_path.stem}_bg_tmp.png")
        self.prepare_scene_background(bg_image_path, str(bg_tmp), resolution)
        bg = Image.open(bg_tmp).convert("RGBA")

        # 2. Create overlay
        ov_tmp = out_path.with_name(f"{out_path.stem}_ov_tmp.png")
        self.create_scene_overlay(title, subtitle, scene_idx, str(ov_tmp), resolution, total_scenes, era)
        ov = Image.open(ov_tmp).convert("RGBA")

        # 3. Composite
        composite = Image.alpha_composite(bg, ov)
        composite.convert("RGB").save(str(out_path), "PNG")

        # Cleanup temps
        bg_tmp.unlink(missing_ok=True)
        ov_tmp.unlink(missing_ok=True)
        return str(out_path)

    def _draw_procedural_background(self, w: int, h: int) -> Image.Image:
        """Renders an obsidian-to-dark-charcoal gradient background canvas."""
        canvas = Image.new("RGBA", (w, h), (13, 13, 17, 255))
        draw = ImageDraw.Draw(canvas)
        for y in range(h):
            ratio = y / h
            r = int(12 + ratio * 15)
            g = int(12 + ratio * 12)
            b = int(18 + ratio * 25)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        return canvas

    def get_audio_duration(self, audio_path: str) -> float:
        """Probes the exact duration of an audio file using ffprobe."""
        cmd = [
            self.ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())

    def compile_kinetic_video(
        self,
        scene_cards: List[str],
        narration_audio: str,
        output_mp4: str,
        resolution: Tuple[int, int] = (1080, 1920),
        fps: int = 30,
        overlay_cards: Optional[List[str]] = None
    ) -> str:
        """
        Compiles scene cards/backgrounds (mixed video clips or images) and narration
        audio into a vertical 1080x1920 MP4 video.
        - Video assets are scaled, looped, trimmed, and normalized with setsar=1.
        - Still images receive cinematic Ken Burns zoompan camera motion.
        - Static typography overlays are composited on top with clean alpha blending.
        """
        out_path = Path(output_mp4)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        w, h = resolution

        audio_duration = self.get_audio_duration(narration_audio)
        n_scenes = len(scene_cards)
        if n_scenes == 0:
            raise ValueError("scene_cards list cannot be empty")

        scene_dur = audio_duration / n_scenes
        frames_per_scene = round(scene_dur * fps)

        # Build FFmpeg command inputs
        inputs_cmd: List[str] = []
        for bg in scene_cards:
            if self.is_video_file(bg):
                inputs_cmd.extend(["-stream_loop", "-1", "-i", str(bg)])
            else:
                inputs_cmd.extend(["-i", str(bg)])

        has_overlays = overlay_cards is not None and len(overlay_cards) == n_scenes
        if has_overlays:
            for ov in overlay_cards:
                inputs_cmd.extend(["-i", str(ov)])

        inputs_cmd.extend(["-i", str(narration_audio)])
        audio_idx = n_scenes + (n_scenes if has_overlays else 0)

        # Construct filtergraph
        filter_parts: List[str] = []
        for idx, bg in enumerate(scene_cards):
            is_vid = self.is_video_file(bg)
            if is_vid:
                fade_filter = ""
                if idx == n_scenes - 1:
                    fade_start = max(0.0, scene_dur - 1.5)
                    fade_filter = f",fade=t=out:st={fade_start:.2f}:d=1.5"
                filter_parts.append(
                    f"[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},trim=duration={scene_dur:.3f},setpts=PTS-STARTPTS{fade_filter},setsar=1,format=yuv420p[vbg{idx}];"
                )
            else:
                if idx == 0:
                    # Scene 0: Slow center push-in
                    filter_parts.append(
                        f"[{idx}:v]zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames_per_scene}:s={w}x{h}:fps={fps},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[vbg{idx}];"
                    )
                elif idx == 1:
                    # Scene 1: Slow panoramic drift
                    filter_parts.append(
                        f"[{idx}:v]zoompan=z=1.12:x='iw*0.06*(on/{frames_per_scene})':y='ih*0.03*(on/{frames_per_scene})':d={frames_per_scene}:s={w}x{h}:fps={fps},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[vbg{idx}];"
                    )
                elif idx == 2:
                    # Scene 2: Monumental reveal pull-out
                    filter_parts.append(
                        f"[{idx}:v]zoompan=z='max(1.15-0.0008*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames_per_scene}:s={w}x{h}:fps={fps},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[vbg{idx}];"
                    )
                else:
                    # Scene 3: Forward glide + fade-to-black
                    fade_start = max(0.0, scene_dur - 1.5)
                    filter_parts.append(
                        f"[{idx}:v]zoompan=z='min(zoom+0.0006,1.12)':x='iw/2-(iw/zoom/2)':y='ih*0.04*(1-on/{frames_per_scene})':d={frames_per_scene}:s={w}x{h}:fps={fps},fade=t=out:st={fade_start:.2f}:d=1.5,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[vbg{idx}];"
                    )

            if has_overlays:
                ov_idx = n_scenes + idx
                filter_parts.append(
                    f"[{ov_idx}:v]scale={w}:{h},setsar=1,format=rgba[vov{idx}];"
                    f"[vbg{idx}][vov{idx}]overlay=0:0,setsar=1,format=yuv420p[v{idx}];"
                )
            else:
                filter_parts.append(f"[vbg{idx}]setsar=1,format=yuv420p[v{idx}];")

        # Concatenate scenes
        inputs_labels = "".join(f"[v{i}]" for i in range(n_scenes))
        filter_parts.append(f"{inputs_labels}concat=n={n_scenes}:v=1:a=0[vcat]")
        filter_complex = "".join(filter_parts)

        cmd = [
            self.ffmpeg, "-y",
            *inputs_cmd,
            "-filter_complex", filter_complex,
            "-map", "[vcat]",
            "-map", f"{audio_idx}:a",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-b:v", "2800k",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_path)
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return str(out_path)
