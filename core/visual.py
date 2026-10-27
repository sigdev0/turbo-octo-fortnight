"""
Visual Asset Manager for Cultural Documentary Video Reels.
Resolves, fetches, caches, and procedurally synthesizes 1080x1920 cinematic
historical backdrops for Nusantara civilizations.
"""

import hashlib
import logging
import math
import os
import random
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple

import httpx
from PIL import Image, ImageDraw, ImageFilter

from core.config import BASE_DIR

logger = logging.getLogger(__name__)

CULTURE_TEMPLATES_DIR = BASE_DIR / "assets" / "templates" / "culture"

# Palette definitions for high-contrast procedural architectural fallback
ARCHETYPE_PALETTES = {
    "majapahit_trowulan": {
        "bg_top": (18, 10, 8),
        "bg_mid": (74, 25, 18),       # Terracotta red brick
        "bg_bottom": (35, 12, 10),
        "accent": (212, 175, 55),     # Royal Wilwatikta gold
        "glow": (245, 158, 11),       # Torchlight ember
    },
    "sriwijaya_maritim": {
        "bg_top": (8, 18, 32),
        "bg_mid": (14, 52, 85),       # Musi river / maritime ocean
        "bg_bottom": (6, 26, 46),
        "accent": (234, 179, 8),      # Golden spice tribute
        "glow": (56, 189, 248),       # River dawn reflection
    },
    "padjajaran_siliwangi": {
        "bg_top": (10, 22, 14),
        "bg_mid": (25, 60, 35),       # Gunung Salak rainforest mist
        "bg_bottom": (12, 30, 18),
        "accent": (250, 204, 21),     # Sacred Kujang brass
        "glow": (134, 239, 172),      # Forest morning canopy mist
    },
    "borobudur_syailendra": {
        "bg_top": (22, 20, 28),
        "bg_mid": (48, 44, 58),       # Volcanic andesite stone
        "bg_bottom": (24, 22, 32),
        "accent": (224, 170, 62),     # Syailendra enlightenment gold
        "glow": (253, 230, 138),      # Lembah Kedu morning dawn
    },
    "singasari_kenarok": {
        "bg_top": (24, 6, 12),
        "bg_mid": (80, 16, 28),       # Tumapel blood & iron forge
        "bg_bottom": (32, 8, 16),
        "accent": (245, 158, 11),     # Mpu Gandring keris fire
        "glow": (239, 68, 68),        # Volcanic lava dusk
    },
}

DEFAULT_PALETTE = {
    "bg_top": (13, 13, 17),
    "bg_mid": (35, 32, 50),
    "bg_bottom": (15, 14, 25),
    "accent": (212, 175, 55),
    "glow": (245, 158, 11),
}


class VisualAssetManager:
    """
    Manages loading, online synthesis, caching, and offline procedural generation
    of 1080x1920 cinematic vertical backgrounds.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or CULTURE_TEMPLATES_DIR
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def get_or_generate_scene_image(
        self,
        archetype: str,
        scene_idx: int,
        visual_prompt: str,
        width: int = 1080,
        height: int = 1920,
        force_regenerate: bool = False,
    ) -> str:
        """
        Retrieves a cached background image, attempts online AI synthesis,
        or creates a procedural cinematic backdrop.
        """
        arch_dir = self.templates_dir / archetype
        arch_dir.mkdir(parents=True, exist_ok=True)

        cached_png = arch_dir / f"scene_{scene_idx}.png"
        cached_jpg = arch_dir / f"scene_{scene_idx}.jpg"

        if not force_regenerate:
            if cached_png.exists() and cached_png.stat().st_size > 10000:
                logger.info(f"Using cached scene visual: {cached_png}")
                return str(cached_png)
            if cached_jpg.exists() and cached_jpg.stat().st_size > 10000:
                logger.info(f"Using cached scene visual: {cached_jpg}")
                return str(cached_jpg)

        # 1. Attempt AI synthesis via Pollinations FLUX API
        try:
            downloaded = self._fetch_ai_image(
                visual_prompt=visual_prompt,
                output_path=cached_png,
                width=width,
                height=height,
            )
            if downloaded and cached_png.exists() and cached_png.stat().st_size > 10000:
                logger.info(f"Successfully synthesized AI scene visual: {cached_png}")
                return str(cached_png)
        except Exception as e:
            logger.warning(f"Online AI image generation failed: {e}. Falling back to procedural synthesis.")

        # 2. Fallback to procedural high-contrast cinematic canvas
        self._generate_procedural_backdrop(
            archetype=archetype,
            scene_idx=scene_idx,
            output_path=cached_png,
            width=width,
            height=height,
        )
        return str(cached_png)

    def _fetch_ai_image(
        self,
        visual_prompt: str,
        output_path: Path,
        width: int,
        height: int,
        timeout_sec: float = 18.0,
    ) -> bool:
        """
        Calls Pollinations.ai FLUX endpoint to synthesize high-res 9:16 imagery.
        """
        clean_prompt = visual_prompt.strip()
        enhanced_prompt = (
            f"{clean_prompt}, authentic ancient Indonesian Nusantara history, "
            f"cinematic lighting, national geographic 8k photography, vertical 9:16 composition, "
            f"photorealistic masterpiece, highly detailed relief, atmospheric mist, golden hour"
        )
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        # Deterministic seed from prompt hash for consistency
        seed = int(hashlib.md5(clean_prompt.encode("utf-8")).hexdigest()[:6], 16)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}&model=flux&nologo=true&seed={seed}"
        )

        logger.info(f"Requesting AI scene image from Pollinations ({width}x{height})...")
        with httpx.Client(timeout=timeout_sec, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200 and len(resp.content) > 10000:
                output_path.write_bytes(resp.content)
                # Verify PIL can open it
                with Image.open(output_path) as img:
                    img.verify()
                return True
        return False

    def _generate_procedural_backdrop(
        self,
        archetype: str,
        scene_idx: int,
        output_path: Path,
        width: int = 1080,
        height: int = 1920,
    ) -> None:
        """
        Synthesizes a rich, multi-layered atmospheric cinematic background
        tailored to the historical archetype's aesthetic.
        """
        palette = ARCHETYPE_PALETTES.get(archetype, DEFAULT_PALETTE)
        top = palette["bg_top"]
        mid = palette["bg_mid"]
        bottom = palette["bg_bottom"]
        accent = palette["accent"]
        glow = palette["glow"]

        img = Image.new("RGB", (width, height), top)
        draw = ImageDraw.Draw(img)

        # 1. Base 3-point vertical gradient
        for y in range(height):
            ratio = y / height
            if ratio < 0.5:
                sub = ratio / 0.5
                r = int(top[0] + (mid[0] - top[0]) * sub)
                g = int(top[1] + (mid[1] - top[1]) * sub)
                b = int(top[2] + (mid[2] - top[2]) * sub)
            else:
                sub = (ratio - 0.5) / 0.5
                r = int(mid[0] + (bottom[0] - mid[0]) * sub)
                g = int(mid[1] + (bottom[1] - mid[1]) * sub)
                b = int(mid[2] + (bottom[2] - mid[2]) * sub)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 2. Atmospheric volumetric lighting disc (golden hour sun or sacred torch glow)
        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        # Center glow varies slightly by scene index to give camera movement dynamism
        glow_x = int(width * (0.45 + 0.1 * (scene_idx % 3)))
        glow_y = int(height * (0.35 + 0.08 * (scene_idx % 2)))
        glow_radius = int(width * 0.45)

        for radius in range(glow_radius, 10, -15):
            alpha = int(45 * (1.0 - (radius / glow_radius)) ** 1.8)
            glow_draw.ellipse(
                [
                    (glow_x - radius, glow_y - radius),
                    (glow_x + radius, glow_y + radius),
                ],
                fill=(glow[0], glow[1], glow[2], alpha),
            )

        # 3. Architectural silhouette / temple geometry layer
        geo_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        geo_draw = ImageDraw.Draw(geo_layer)

        # Draw classical Nusantara temple roofline / stupa / gapura stepped silhouettes
        horizon_y = int(height * 0.62)
        base_points = []
        center_x = width // 2

        # Symmetrical stepped temple gate (Gapura / Meru / Candi)
        steps = [
            (width * 0.08, height * 0.16),
            (width * 0.16, height * 0.12),
            (width * 0.25, height * 0.08),
            (width * 0.35, height * 0.04),
        ]
        # Left side
        for w_offset, h_offset in steps:
            x_left = center_x - int(w_offset)
            x_right = center_x + int(w_offset)
            y_top = horizon_y - int(h_offset)
            geo_draw.rectangle(
                [(x_left, y_top), (x_right, horizon_y)],
                fill=(10, 8, 12, 160),
                outline=(accent[0], accent[1], accent[2], 50),
                width=2,
            )

        # Stupa pinnacle or crowning spire
        geo_draw.polygon(
            [
                (center_x, horizon_y - int(height * 0.22)),
                (center_x - 30, horizon_y - int(height * 0.16)),
                (center_x + 30, horizon_y - int(height * 0.16)),
            ],
            fill=(accent[0], accent[1], accent[2], 180),
        )

        # Ground silhouette
        geo_draw.rectangle(
            [(0, horizon_y), (width, height)],
            fill=(8, 6, 10, 220),
        )

        # 4. Subtle ancient stone texture noise
        random.seed(42 + scene_idx * 17)
        for _ in range(3500):
            nx = random.randint(0, width - 1)
            ny = random.randint(0, height - 1)
            lum = random.randint(15, 60)
            draw.point((nx, ny), fill=(lum, lum, lum))

        # Composite layers
        img.paste(Image.alpha_composite(Image.new("RGBA", (width, height), (0, 0, 0, 0)), glow_layer).convert("RGB"), (0, 0), glow_layer)
        img.paste(geo_layer, (0, 0), geo_layer)

        # 5. Cinematic vignette border (dark edges)
        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        v_draw = ImageDraw.Draw(vignette)
        margin = 120
        v_draw.rectangle([(0, 0), (width, height)], outline=(0, 0, 0, 190), width=margin)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=60))
        img.paste(vignette, (0, 0), vignette)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG", quality=95)
        logger.info(f"Synthesized procedural scene backdrop: {output_path}")
