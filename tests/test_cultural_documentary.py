"""
OmniForge V2 Cultural Documentary Video Engine Unit Test Suite.
Tests library calibration (240-340 words, 4 movements, 4 scenes),
media bed synthesis, kinetic video compiler (1080x1920),
cartridge orchestration, and Telegram bot integration.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from cartridges.cultural_library import (
    ARCHETYPES_METADATA,
    ARCHETYPE_ALIASES,
    select_cultural_archetype,
    get_documentary_story,
)
from core.media import MediaMixer
from core.video import KineticVideoCompiler
from cartridges.cultural_documentary import CulturalDocumentaryCartridge
from core.bot import OmniForgeBot


class TestCulturalLibrary(unittest.TestCase):
    def test_archetype_keys_and_count(self):
        """Verifies exactly 5 canonical Nusantara archetypes are defined."""
        expected = {
            "majapahit_trowulan",
            "sriwijaya_maritim",
            "padjajaran_siliwangi",
            "borobudur_syailendra",
            "singasari_kenarok"
        }
        self.assertEqual(set(ARCHETYPES_METADATA.keys()), expected)

    def test_narration_calibration_word_count(self):
        """
        Verifies spoken narrative scripts are strictly calibrated to 240–340 words
        (~60–90 seconds spoken at 130–140 WPM) for both ID and EN versions.
        """
        for key, data in ARCHETYPES_METADATA.items():
            id_words = len(data["narration"].split())
            self.assertGreaterEqual(
                id_words, 240,
                f"[{key}] Indonesian narration word count {id_words} < 240 words"
            )
            self.assertLessEqual(
                id_words, 340,
                f"[{key}] Indonesian narration word count {id_words} > 340 words"
            )

            en_words = len(data["narration_en"].split())
            self.assertGreaterEqual(
                en_words, 240,
                f"[{key}] English narration word count {en_words} < 240 words"
            )
            self.assertLessEqual(
                en_words, 340,
                f"[{key}] English narration word count {en_words} > 340 words"
            )

    def test_scene_descriptors_and_fields(self):
        """Verifies each archetype contains exactly 4 Ken Burns scene descriptors."""
        required_fields = {"visual_prompt", "camera_motion", "caption_title", "caption_body"}
        valid_motions = {"zoom_in_center", "pan_horizontal_reveal", "zoom_out_monumental", "dramatic_tilt_up"}

        for key, data in ARCHETYPES_METADATA.items():
            scenes = data["scenes"]
            self.assertEqual(len(scenes), 4, f"[{key}] must have exactly 4 scenes")
            for idx, scene in enumerate(scenes):
                self.assertTrue(
                    required_fields.issubset(scene.keys()),
                    f"[{key}] scene {idx} missing required fields"
                )
                self.assertIn(
                    scene["camera_motion"], valid_motions,
                    f"[{key}] scene {idx} has invalid camera motion: {scene['camera_motion']}"
                )
                self.assertTrue(len(scene["caption_title"]) > 0)
                self.assertTrue(len(scene["caption_body"]) > 0)
                self.assertTrue(len(scene["visual_prompt"]) > 20)

    def test_alias_normalization(self):
        """Verifies historical keywords and figures correctly resolve to canonical archetypes."""
        self.assertEqual(select_cultural_archetype("gajah mada"), "majapahit_trowulan")
        self.assertEqual(select_cultural_archetype("hayam wuruk"), "majapahit_trowulan")
        self.assertEqual(select_cultural_archetype("wilwatikta"), "majapahit_trowulan")
        self.assertEqual(select_cultural_archetype("sriwijaya"), "sriwijaya_maritim")
        self.assertEqual(select_cultural_archetype("palembang"), "sriwijaya_maritim")
        self.assertEqual(select_cultural_archetype("siliwangi"), "padjajaran_siliwangi")
        self.assertEqual(select_cultural_archetype("kujang"), "padjajaran_siliwangi")
        self.assertEqual(select_cultural_archetype("borobudur"), "borobudur_syailendra")
        self.assertEqual(select_cultural_archetype("syailendra"), "borobudur_syailendra")
        self.assertEqual(select_cultural_archetype("singasari"), "singasari_kenarok")
        self.assertEqual(select_cultural_archetype("ken arok"), "singasari_kenarok")
        self.assertEqual(select_cultural_archetype("mpu gandring"), "singasari_kenarok")

        # Empty or unknown fallback
        self.assertEqual(select_cultural_archetype(""), "majapahit_trowulan")

    def test_get_documentary_story(self):
        """Verifies structured retrieval returns complete story dictionaries."""
        story_id = get_documentary_story("majapahit_trowulan", is_id=True)
        self.assertIn("Bhinneka Tunggal Ika", story_id["narration"])
        self.assertEqual(story_id["era"], "1350 Masehi (Era Hayam Wuruk & Gajah Mada)")
        self.assertEqual(len(story_id["scenes"]), 4)

        story_en = get_documentary_story("majapahit_trowulan", is_id=False)
        self.assertIn("Unity in Diversity", story_en["narration"])


class TestMediaMixerDocumentary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix="test_media_doc_")
        cls.mixer = MediaMixer()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_generate_documentary_bed(self):
        """Verifies Gamelan Slendro & Foley bed synthesis outputs valid stereo 44.1kHz MP3."""
        out_mp3 = Path(self.tmpdir) / "test_gamelan_bed.mp3"
        res = self.mixer.generate_documentary_bed(duration_sec=4, output_path=str(out_mp3))
        self.assertEqual(res, str(out_mp3))
        self.assertTrue(out_mp3.exists())
        self.assertGreater(out_mp3.stat().st_size, 50000)

        # Probe with ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=channels,sample_rate",
            "-of", "csv=p=0",
            str(out_mp3)
        ]
        proc = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        lines = [line.strip() for line in proc.stdout.strip().splitlines() if line.strip()]
        # Stream line: channels,sample_rate (e.g. 44100,2)
        # Format line: duration (e.g. 4.000000)
        self.assertTrue(any("44100" in l for l in lines))
        self.assertTrue(any("2" in l for l in lines))


class TestKineticVideoCompiler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix="test_video_comp_")
        cls.compiler = KineticVideoCompiler()
        cls.mixer = MediaMixer()
        # Generate a short 4s test audio bed
        cls.test_audio = Path(cls.tmpdir) / "test_narration.mp3"
        cls.mixer.generate_documentary_bed(duration_sec=4, output_path=str(cls.test_audio))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_create_scene_card(self):
        """Verifies programmatic 1080x1920 scene card generation with gold borders and typography."""
        card_png = Path(self.tmpdir) / "test_card.png"
        res = self.compiler.create_scene_card(
            title="Gapura Bajang Ratu",
            subtitle="Gapura terakota bata merah abad ke-14 berdiri kokoh tanpa spesi semen.",
            scene_idx=0,
            output_png_path=str(card_png),
            total_scenes=4
        )
        self.assertEqual(res, str(card_png))
        self.assertTrue(card_png.exists())

        # Check image dimensions
        from PIL import Image
        with Image.open(card_png) as img:
            self.assertEqual(img.size, (1080, 1920))

    def test_prepare_scene_background_and_overlay(self):
        """Verifies decoupled background preparation and transparent overlay creation."""
        from PIL import Image
        bg_path = Path(self.tmpdir) / "test_decoupled_bg.png"
        ov_path = Path(self.tmpdir) / "test_decoupled_ov.png"

        res_bg = self.compiler.prepare_scene_background(
            bg_image_path=None,
            output_png_path=str(bg_path),
            resolution=(1080, 1920)
        )
        self.assertEqual(res_bg, str(bg_path))
        self.assertTrue(bg_path.exists())
        with Image.open(bg_path) as img:
            self.assertEqual(img.size, (1080, 1920))

        res_ov = self.compiler.create_scene_overlay(
            title="Patih Gajah Mada",
            subtitle="Sumpah Palapa menggetarkan jagat peradaban Nusantara.",
            scene_idx=2,
            output_png_path=str(ov_path),
            resolution=(1080, 1920),
            total_scenes=4
        )
        self.assertEqual(res_ov, str(ov_path))
        self.assertTrue(ov_path.exists())
        with Image.open(ov_path) as img:
            self.assertEqual(img.size, (1080, 1920))
            self.assertEqual(img.mode, "RGBA")

    def test_compile_kinetic_video_smoke(self):
        """Verifies 4 scene cards compile with audio into a valid 1080x1920 MP4 video."""
        cards = []
        for i in range(4):
            card_path = Path(self.tmpdir) / f"smoke_card_{i}.png"
            self.compiler.create_scene_card(
                title=f"Scene {i+1}",
                subtitle=f"Historical description fact number {i+1}.",
                scene_idx=i,
                output_png_path=str(card_path),
                total_scenes=4
            )
            cards.append(str(card_path))

        out_mp4 = Path(self.tmpdir) / "smoke_kinetic.mp4"
        res = self.compiler.compile_kinetic_video(
            scene_cards=cards,
            narration_audio=str(self.test_audio),
            output_mp4=str(out_mp4),
            fps=30
        )
        self.assertEqual(res, str(out_mp4))
        self.assertTrue(out_mp4.exists())
        self.assertGreater(out_mp4.stat().st_size, 500000)

        # Probe video dimensions and codec
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,codec_name",
            "-of", "csv=p=0",
            str(out_mp4)
        ]
        proc = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        self.assertIn("1080", proc.stdout)
        self.assertIn("1920", proc.stdout)
        self.assertIn("h264", proc.stdout)

    def test_compile_kinetic_video_with_overlays(self):
        """Verifies layered compilation: background Ken Burns with static overlay HUD."""
        bgs = []
        ovs = []
        for i in range(4):
            bg_path = Path(self.tmpdir) / f"layered_bg_{i}.png"
            ov_path = Path(self.tmpdir) / f"layered_ov_{i}.png"
            self.compiler.prepare_scene_background(
                bg_image_path=None,
                output_png_path=str(bg_path),
                resolution=(1080, 1920)
            )
            self.compiler.create_scene_overlay(
                title=f"Layered Scene {i+1}",
                subtitle=f"Layered caption body {i+1}.",
                scene_idx=i,
                output_png_path=str(ov_path),
                total_scenes=4
            )
            bgs.append(str(bg_path))
            ovs.append(str(ov_path))

        out_mp4 = Path(self.tmpdir) / "layered_kinetic.mp4"
        res = self.compiler.compile_kinetic_video(
            scene_cards=bgs,
            narration_audio=str(self.test_audio),
            output_mp4=str(out_mp4),
            fps=30,
            overlay_cards=ovs
        )
        self.assertEqual(res, str(out_mp4))
        self.assertTrue(out_mp4.exists())
        self.assertGreater(out_mp4.stat().st_size, 100000)

    def test_compile_kinetic_video_mixed_media(self):
        """Verifies mixed media compilation: moving video hero scene + still image Ken Burns scenes."""
        # 1. Create a lightweight 2s test video clip
        test_clip = Path(self.tmpdir) / "test_hero_clip.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=navy:s=1080x1920:d=2:r=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(test_clip)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 2. Prepare 3 still image scenes
        bgs = [str(test_clip)]
        ovs = []
        for i in range(4):
            ov_path = Path(self.tmpdir) / f"mixed_ov_{i}.png"
            self.compiler.create_scene_overlay(
                title=f"Mixed Scene {i+1}",
                subtitle=f"Historical description fact {i+1}.",
                scene_idx=i,
                output_png_path=str(ov_path),
                total_scenes=4,
                era="1350 Masehi"
            )
            ovs.append(str(ov_path))
            if i > 0:
                bg_path = Path(self.tmpdir) / f"mixed_bg_{i}.png"
                self.compiler.prepare_scene_background(
                    bg_image_path=None,
                    output_png_path=str(bg_path),
                    resolution=(1080, 1920)
                )
                bgs.append(str(bg_path))

        out_mp4 = Path(self.tmpdir) / "mixed_kinetic.mp4"
        res = self.compiler.compile_kinetic_video(
            scene_cards=bgs,
            narration_audio=str(self.test_audio),
            output_mp4=str(out_mp4),
            fps=30,
            overlay_cards=ovs
        )
        self.assertEqual(res, str(out_mp4))
        self.assertTrue(out_mp4.exists())
        self.assertGreater(out_mp4.stat().st_size, 100000)


class TestCulturalDocumentaryCartridge(unittest.TestCase):
    def setUp(self):
        self.cartridge = CulturalDocumentaryCartridge()

    def test_cartridge_properties(self):
        """Verifies BaseCartridge interface implementation."""
        self.assertEqual(self.cartridge.name, "cultural_documentary")
        self.assertEqual(self.cartridge.command, "culture")
        self.assertIn("Medan Amrulloh", self.cartridge.description)

    def test_resolve_lang(self):
        """Verifies language resolution logic."""
        self.assertEqual(self.cartridge._resolve_lang({"lang": "en"}), "en")
        self.assertEqual(self.cartridge._resolve_lang({"language": "English"}), "en")
        self.assertEqual(self.cartridge._resolve_lang({"lang": "id"}), "id")
        self.assertEqual(self.cartridge._resolve_lang({}), "id")

    def test_find_scene_background_prioritizes_video(self):
        """Verifies that _find_scene_background detects hero_scene_0.mp4 for majapahit_trowulan."""
        bg = self.cartridge._find_scene_background("majapahit_trowulan", 0)
        self.assertIsNotNone(bg)
        self.assertTrue(bg.endswith(".mp4") or bg.endswith(".jpg"))
        if Path("assets/culture/majapahit_trowulan/hero_scene_0.mp4").exists():
            self.assertTrue(bg.endswith(".mp4"))


class TestBotCultureIntegration(unittest.TestCase):
    def setUp(self):
        self.bot = OmniForgeBot()

    def test_cartridge_discovered(self):
        """Verifies /culture is registered in bot.cartridges."""
        self.assertIn("culture", self.bot.cartridges)
        cart = self.bot.cartridges["culture"]
        self.assertEqual(cart.name, "cultural_documentary")

    def test_culture_keyboard_buttons(self):
        """Verifies inline keyboard presents all 5 historical civilizations."""
        kb_id = self.bot._get_culture_keyboard("id")
        buttons_id = [b.text for row in kb_id.inline_keyboard for b in row]
        self.assertTrue(any("Majapahit" in b for b in buttons_id))
        self.assertTrue(any("Sriwijaya" in b for b in buttons_id))
        self.assertTrue(any("Pajajaran" in b for b in buttons_id))
        self.assertTrue(any("Borobudur" in b for b in buttons_id))
        self.assertTrue(any("Singasari" in b for b in buttons_id))

        kb_en = self.bot._get_culture_keyboard("en")
        buttons_en = [b.text for row in kb_en.inline_keyboard for b in row]
        self.assertTrue(any("Majapahit" in b for b in buttons_en))
        self.assertTrue(any("Sriwijaya" in b for b in buttons_en))

    def test_simulate_system_with_culture(self):
        """Verifies simulate_command handles /status and reports active culture cartridge."""
        res = asyncio.run(self.bot.simulate_command("/status"))
        self.assertEqual(res["status"], "success")
        self.assertIn("culture", res["active_cartridges"])


if __name__ == "__main__":
    unittest.main()
