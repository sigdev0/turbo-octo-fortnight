import asyncio
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.bot import OmniForgeBot
from core.autoforge import AutoForge
from cartridges.bedtime_story import BedtimeStoryCartridge

class TestOmniForgeEngine(unittest.TestCase):
    def setUp(self):
        self.bot = OmniForgeBot()
        self.autoforge = AutoForge()

    def test_cartridge_registry(self):
        """Verifies cartridges are discovered dynamically and registered."""
        self.assertIn("story", self.bot.cartridges)
        story_cartridge = self.bot.cartridges["story"]
        self.assertEqual(story_cartridge.name, "bedtime_story")
        self.assertEqual(story_cartridge.command, "story")

        self.assertIn("clip", self.bot.cartridges)
        clip_cartridge = self.bot.cartridges["clip"]
        self.assertEqual(clip_cartridge.name, "podcast_clipper")
        self.assertEqual(clip_cartridge.command, "clip")

    def test_autoforge_ast_validation(self):
        """Verifies AST safety checks prohibit dangerous calls."""
        valid_code = "def test():\n    return 42\n"
        self.autoforge._validate_ast(valid_code)

        invalid_code = "def test():\n    return eval('2+2')\n"
        with self.assertRaises(ValueError):
            self.autoforge._validate_ast(invalid_code)

    def test_bot_simulation_system_commands(self):
        """Verifies system commands execute cleanly in simulation mode."""
        res_start = asyncio.run(self.bot.simulate_command("/start"))
        self.assertEqual(res_start["status"], "success")

        res_status = asyncio.run(self.bot.simulate_command("/status"))
        self.assertEqual(res_status["status"], "success")

    def test_bedtime_story_fallback(self):
        """Verifies script fallback generation for both age tiers and languages."""
        cartridge = BedtimeStoryCartridge()
        # Toddler test
        script_2yo = cartridge._generate_fallback_script("Maya", 2, "awan", "kelembutan", is_id=True, archetype="negeri_atas_awan")
        self.assertIn("Maya", script_2yo)
        self.assertIn("awan", script_2yo)
        self.assertGreaterEqual(len(script_2yo.split()), 380)

        # Older kids test
        script_8yo = cartridge._generate_fallback_script("Leo", 8, "space", "courage", is_id=False, archetype="bintang_kejora")
        self.assertIn("Leo", script_8yo)
        self.assertIn("space", script_8yo)
        self.assertGreaterEqual(len(script_8yo.split()), 650)

    def test_v2_archetype_selection(self):
        """Verifies Indonesian storytelling archetypes map accurately to themes."""
        cartridge = BedtimeStoryCartridge()
        # Pinisi boat / sea
        self.assertEqual(cartridge._select_archetype("perahu pinisi"), "perahu_pinisi")
        self.assertEqual(cartridge._select_archetype("starlight boat"), "perahu_pinisi")

        # Kalpataru / forest
        self.assertEqual(cartridge._select_archetype("hutan rimba"), "hutan_kalpataru")
        self.assertEqual(cartridge._select_archetype("sacred tree"), "hutan_kalpataru")

        # Negeri di atas awan
        self.assertEqual(cartridge._select_archetype("negeri awan"), "negeri_atas_awan")
        self.assertEqual(cartridge._select_archetype("misty mountains"), "negeri_atas_awan")

        # Lentera kunang-kunang
        self.assertEqual(cartridge._select_archetype("lentera kunang"), "lentera_kunang_kunang")
        self.assertEqual(cartridge._select_archetype("river firefly"), "lentera_kunang_kunang")

        # Bintang kejora
        self.assertEqual(cartridge._select_archetype("bintang kejora"), "bintang_kejora")
        self.assertEqual(cartridge._select_archetype("cosmic stars"), "bintang_kejora")

    def test_v2_all_archetypes_word_counts_and_somatic_cues(self):
        """Verifies all 20 archetypes satisfy word budget and somatic breathing cues."""
        from cartridges.story_library import TEMPLATES, get_story_fallback

        for (lang, tier, arch), fn in TEMPLATES.items():
            age = 2 if tier == "toddler" else 8
            is_id = (lang == "id")
            script = get_story_fallback(arch, age, is_id, "Maya", "bintang", "kebaikan")
            wc = len(script.split())

            # Word count bounds: Toddler (380-460), Older (650-760)
            min_wc = 380 if tier == "toddler" else 650
            max_wc = 460 if tier == "toddler" else 760
            self.assertGreaterEqual(
                wc, min_wc,
                f"{lang}_{tier}_{arch} too short: {wc} words (expected >= {min_wc})"
            )
            self.assertLessEqual(
                wc, max_wc,
                f"{lang}_{tier}_{arch} too long: {wc} words (expected <= {max_wc})"
            )

            # Breathing pauses check
            self.assertIn("...", script, f"{lang}_{tier}_{arch} missing breathing pauses")

            # Somatic relaxation cues check
            if is_id:
                has_somatic = any(k in script.lower() for k in ["napas", "kelopak mata", "empuk", "pejamkan", "tidur"])
            else:
                has_somatic = any(k in script.lower() for k in ["breath", "eyelids", "cozy", "close your eyes", "sleep"])
            self.assertTrue(has_somatic, f"{lang}_{tier}_{arch} missing somatic cues")

    def test_bot_interactive_keyboards(self):
        """Verifies all interactive keyboards generate valid Telegram buttons under 64 bytes."""
        kb_lang = self.bot._get_story_lang_keyboard()
        for row in kb_lang.inline_keyboard:
            for btn in row:
                self.assertIsNotNone(btn.callback_data)
                self.assertLessEqual(len(btn.callback_data.encode("utf-8")), 64)

        for lang in ("id", "en"):
            kb_child = self.bot._get_child_keyboard(lang)
            for row in kb_child.inline_keyboard:
                for btn in row:
                    self.assertIsNotNone(btn.callback_data)
                    self.assertLessEqual(len(btn.callback_data.encode("utf-8")), 64)

            for name, age in [("Maya", 2), ("Leo", 8)]:
                kb_theme = self.bot._get_theme_keyboard(lang, name, age)
                for row in kb_theme.inline_keyboard:
                    for btn in row:
                        self.assertIsNotNone(btn.callback_data)
                        self.assertLessEqual(
                            len(btn.callback_data.encode("utf-8")),
                            64,
                            f"Callback data too long: {btn.callback_data}"
                        )

        kb_morning = self.bot._get_morning_keyboard()
        for row in kb_morning.inline_keyboard:
            for btn in row:
                self.assertIsNotNone(btn.callback_data)
                self.assertLessEqual(len(btn.callback_data.encode("utf-8")), 64)

    def test_session_storage(self):
        """Verifies session store assigns IDs and preserves cartridge payload."""
        sess_id = self.bot._store_session({"cmd": "story", "payload": {"name": "Maya", "age": 2}})
        self.assertTrue(sess_id.startswith("s_"))
        self.assertIn(sess_id, self.bot.sessions)
        self.assertEqual(self.bot.sessions[sess_id]["cmd"], "story")
        self.assertEqual(self.bot.sessions[sess_id]["payload"]["name"], "Maya")

    def test_indonesian_language_detection(self):
        """Verifies language identification logic for Indonesian stories."""
        cartridge = BedtimeStoryCartridge()
        self.assertTrue(cartridge._is_indonesian("id", "awan", "kelembutan"))
        self.assertTrue(cartridge._is_indonesian(None, "hutan ajaib", "kebaikan"))
        self.assertFalse(cartridge._is_indonesian("en", "forest", "kindness"))

    def test_i18n_translation(self):
        """Verifies string resolution for both Global English and Indonesian."""
        from core.i18n import t
        # Test English
        en_title = t("start_title", "en")
        self.assertIn("Welcome", en_title)
        # Test Indonesian
        id_title = t("start_title", "id")
        self.assertIn("Selamat Datang", id_title)
        # Test interpolation
        interpolated = t("story_lang_prompt", "en", name="Leo", age=8, theme="space", lesson="courage")
        self.assertIn("Leo", interpolated)
        self.assertIn("space", interpolated)

    def test_user_language_resolution(self):
        """Verifies user language resolution hierarchy."""
        # 1. Explicit request flag takes precedence
        self.assertEqual(self.bot.resolve_user_language(explicit_lang="id"), "id")
        self.assertEqual(self.bot.resolve_user_language(explicit_lang="en"), "en")

        # 2. Saved preference
        self.bot._set_user_language("test_user_123", "en")
        class MockUser:
            id = "test_user_123"
            language_code = "id"
        class MockUpdate:
            effective_user = MockUser()

        # Even though client is 'id', saved preference is 'en'
        self.assertEqual(self.bot.resolve_user_language(MockUpdate()), "en")

        # 3. New user without saved preference -> follows client language_code
        class NewUser:
            id = "new_user_456"
            language_code = "id-ID"
        class NewUpdate:
            effective_user = NewUser()
        self.assertEqual(self.bot.resolve_user_language(NewUpdate()), "id")

        class GlobalUser:
            id = "global_user_789"
            language_code = "en-US"
        class GlobalUpdate:
            effective_user = GlobalUser()
        self.assertEqual(self.bot.resolve_user_language(GlobalUpdate()), "en")

if __name__ == "__main__":
    unittest.main()
