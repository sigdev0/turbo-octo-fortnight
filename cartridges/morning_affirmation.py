import asyncio
from pathlib import Path
from typing import Dict, Any
from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR
from core.voice import VoiceSynthesizer
from core.media import MediaMixer

class MorningAffirmationCartridge(BaseCartridge):
    @property
    def name(self) -> str:
        return "morning_affirmation"

    @property
    def command(self) -> str:
        return "morning"

    @property
    def description(self) -> str:
        return "Autonomous cartridge generated for: User Idea: 3-minute morning courage affirmations for kids  Generate the complete"

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_name = payload.get("name", "Friend").capitalize()
        theme = payload.get("theme", "courage and strength")
        voice_profile = payload.get("voice_profile", "energetic_affirmation")

        # Craft message script
        script_text = (
            f"Good morning, {target_name}! Today is a brand new day full of opportunity. "
            f"Remember that your courage is bigger than any challenge, and your kindness is your superpower. "
            f"Take a deep breath, believe in yourself, and let your light shine bright today. You've got this!"
        )

        safe_name = target_name.lower().replace(" ", "_")
        raw_voice_file = OUTPUT_DIR / f"voice_{safe_name}_{self.name}.mp3"
        final_file = OUTPUT_DIR / f"{self.name}_{safe_name}.mp3"

        voice_engine = VoiceSynthesizer(profile_name=voice_profile)
        await voice_engine.synthesize(
            text=script_text,
            output_path=str(raw_voice_file),
            profile_name=voice_profile
        )

        mixer = MediaMixer()
        mixer.mix_voice_and_music(
            voice_path=str(raw_voice_file),
            output_path=str(final_file),
            music_volume=0.15,
            voice_volume=1.0,
            fade_out_sec=2.0
        )

        if raw_voice_file.exists():
            raw_voice_file.unlink()

        return {
            "status": "success",
            "title": f"{target_name}'s Daily Boost",
            "output_file": str(final_file),
            "script": script_text,
            "metadata": {
                "target_name": target_name,
                "theme": theme,
                "cartridge": self.name
            }
        }
