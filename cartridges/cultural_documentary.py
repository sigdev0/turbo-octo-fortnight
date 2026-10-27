"""
OmniForge V2 Cultural Documentary Video Cartridge — "Mesin Waktu Nusantara".
Generates viral, cinematic vertical video reels (1080x1920 MP4, 60-90s)
transporting the audience through ancient Nusantara civilizations.
Benchmarked to Medan Amrulloh (@medanamrulloh):
- Ken Burns dynamic camera movements
- Gamelan Slendro & foley soundscapes with sidechain ducking
- Authoritative solemn voiceover (Ardi baritone)
- Relief-researched architectural scene cards
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from cartridges.base import BaseCartridge
from cartridges.cultural_library import (
    ARCHETYPES_METADATA,
    select_cultural_archetype,
    get_documentary_story,
)
from core.config import OUTPUT_DIR, MUSIC_DIR, TEMPLATES_DIR, DEFAULT_LANGUAGE, BASE_DIR
from core.media import MediaMixer
from core.video import KineticVideoCompiler
from core.voice import VoiceSynthesizer


class CulturalDocumentaryCartridge(BaseCartridge):
    def __init__(self):
        self.mixer = MediaMixer()
        self.compiler = KineticVideoCompiler()

    @property
    def name(self) -> str:
        return "cultural_documentary"

    @property
    def command(self) -> str:
        return "culture"

    @property
    def description(self) -> str:
        return (
            "Generates cinematic historical documentary video reels (1080x1920 MP4) "
            "on ancient Nusantara civilizations benchmarked to Medan Amrulloh."
        )

    def _resolve_lang(self, payload: Dict[str, Any]) -> str:
        lang = payload.get("lang") or payload.get("language")
        if lang:
            clean = str(lang).strip().lower()
            if clean in ("en", "english", "inggris"):
                return "en"
            return "id"
        return "id" if DEFAULT_LANGUAGE.lower() in ("id", "indonesia") else "en"

    def _find_scene_background(self, archetype: str, scene_idx: int) -> Optional[str]:
        """
        Checks if curated heritage assets or template media exist.
        Prioritizes moving hero video clips (.mp4) over still images.
        """
        search_dirs = [
            BASE_DIR / "assets" / "culture" / archetype,
            BASE_DIR / "assets" / "templates" / "culture" / archetype,
            TEMPLATES_DIR
        ]

        # 1. Priority 1: High-impact moving video clips (e.g. Veo / Kling generations)
        video_exts = [".mp4", ".mov", ".webm", ".mkv"]
        for sdir in search_dirs:
            if not sdir.exists():
                continue
            for ext in video_exts:
                candidate = sdir / f"hero_scene_{scene_idx}{ext}"
                if candidate.exists() and candidate.stat().st_size > 1000:
                    return str(candidate)
                candidate = sdir / f"scene_{scene_idx}{ext}"
                if candidate.exists() and candidate.stat().st_size > 1000:
                    return str(candidate)
                candidate = sdir / f"{archetype}_{scene_idx}{ext}"
                if candidate.exists() and candidate.stat().st_size > 1000:
                    return str(candidate)

        # 2. Priority 2: High-resolution historical still images
        image_exts = [".jpg", ".png", ".jpeg", ".webp"]
        for sdir in search_dirs:
            if not sdir.exists():
                continue
            for ext in image_exts:
                candidate = sdir / f"scene_{scene_idx}{ext}"
                if candidate.exists() and candidate.stat().st_size > 1000:
                    return str(candidate)
                candidate = sdir / f"{archetype}_{scene_idx}{ext}"
                if candidate.exists() and candidate.stat().st_size > 1000:
                    return str(candidate)
        return None

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the end-to-end documentary video generation pipeline:
        1. Script retrieval & calibration
        2. Solemn documentary voice synthesis
        3. Gamelan Slendro sidechain ducked audio mixing
        4. Ornate scene keyframe card rendering
        5. Kinetic 1080x1920 MP4 video compilation
        """
        try:
            # 1. Parse payload and resolve archetype
            query = payload.get("topic") or payload.get("theme") or payload.get("query") or ""
            lang = self._resolve_lang(payload)
            archetype = select_cultural_archetype(query)
            story = get_documentary_story(archetype, is_id=(lang == "id"))

            timestamp = int(time.time() * 1000)
            voice_profile = payload.get("voice_profile") or (
                "indonesian_male" if lang == "id" else "bedtime_american"
            )

            # 2. Synthesize solemn documentary voiceover
            synthesizer = VoiceSynthesizer(profile_name=voice_profile)
            voice_path = OUTPUT_DIR / f"doc_voice_{archetype}_{timestamp}.mp3"
            await synthesizer.synthesize(
                text=story["narration"],
                output_path=str(voice_path),
                profile_name=voice_profile,
                enable_pacing=True,
                pause_duration_sec=0.65  # Pacing for solemn historical authority
            )

            # 3. Ensure Gamelan Slendro & Foley bed exists
            epic_bed = MUSIC_DIR / "majapahit_epic_bed.mp3"
            if not epic_bed.exists():
                self.mixer.generate_documentary_bed(duration_sec=120, output_path=str(epic_bed))

            # 4. Mix narration with documentary sidechain ducking
            mixed_audio_path = OUTPUT_DIR / f"doc_mixed_{archetype}_{timestamp}.mp3"
            self.mixer.mix_voice_and_music(
                voice_path=str(voice_path),
                output_path=str(mixed_audio_path),
                music_path=str(epic_bed),
                music_volume=0.32,
                voice_volume=1.0,
                fade_out_sec=2.0,
                outro_padding_sec=2.0,
                ducking_threshold=0.10,  # -20dB speech threshold
                ducking_ratio=4.5,
                ducking_attack_ms=120.0,
                ducking_release_ms=550.0
            )

            # 5. Generate scene backgrounds and transparent overlays
            bg_paths: List[str] = []
            ov_paths: List[str] = []
            scenes = story["scenes"]
            for idx, scene in enumerate(scenes):
                ov_path = OUTPUT_DIR / f"doc_ov_{archetype}_{timestamp}_{idx}.png"
                bg_asset = self._find_scene_background(archetype, idx)

                if bg_asset and KineticVideoCompiler.is_video_file(bg_asset):
                    # Direct moving video background (Veo hero clip)
                    bg_paths.append(bg_asset)
                else:
                    # Still image background with darkening safe zones
                    bg_path = OUTPUT_DIR / f"doc_bg_{archetype}_{timestamp}_{idx}.png"
                    self.compiler.prepare_scene_background(
                        bg_image_path=bg_asset,
                        output_png_path=str(bg_path),
                        resolution=(1080, 1920)
                    )
                    bg_paths.append(str(bg_path))

                self.compiler.create_scene_overlay(
                    title=scene["caption_title"],
                    subtitle=scene["caption_body"],
                    scene_idx=idx,
                    output_png_path=str(ov_path),
                    resolution=(1080, 1920),
                    total_scenes=len(scenes),
                    era=story.get("era")
                )
                ov_paths.append(str(ov_path))

            # 6. Compile 1080x1920 kinetic video with Ken Burns dynamics & overlays
            final_mp4 = OUTPUT_DIR / f"culture_{archetype}_{timestamp}.mp4"
            self.compiler.compile_kinetic_video(
                scene_cards=bg_paths,
                narration_audio=str(mixed_audio_path),
                output_mp4=str(final_mp4),
                resolution=(1080, 1920),
                fps=30,
                overlay_cards=ov_paths
            )

            # 7. Clean up intermediate generated artifacts safely
            for p in bg_paths + ov_paths:
                try:
                    p_path = Path(p)
                    # Protect permanent assets by checking parent directory
                    if str(OUTPUT_DIR.resolve()) in str(p_path.resolve()):
                        p_path.unlink(missing_ok=True)
                except Exception:
                    pass
            try:
                voice_path.unlink(missing_ok=True)
                mixed_audio_path.unlink(missing_ok=True)
            except Exception:
                pass

            return {
                "status": "success",
                "title": story["title"],
                "output_file": str(final_mp4),
                "script": story["narration"],
                "metadata": {
                    "archetype": archetype,
                    "era": story["era"],
                    "scenes": len(scenes),
                    "lang": lang,
                    "word_count": story["word_count"],
                    "scene_prompts": [s["visual_prompt"] for s in scenes]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate cultural documentary video: {str(e)}"
            }
