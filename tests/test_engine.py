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
        """Verifies script fallback generation for both age tiers."""
        cartridge = BedtimeStoryCartridge()
        script_2yo = cartridge._generate_fallback_script("Maya", 2, "clouds", "gentleness")
        self.assertIn("Maya", script_2yo)
        self.assertIn("clouds", script_2yo)

        script_8yo = cartridge._generate_fallback_script("Leo", 8, "space", "courage")
        self.assertIn("Leo", script_8yo)
        self.assertIn("space", script_8yo)

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
