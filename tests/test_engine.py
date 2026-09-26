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

if __name__ == "__main__":
    unittest.main()
