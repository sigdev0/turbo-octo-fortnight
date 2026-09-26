import asyncio
from pathlib import Path
from typing import Optional
from core.config import VOICE_PROFILES, DEFAULT_BEDTIME_VOICE

class VoiceSynthesizer:
    def __init__(self, profile_name: str = DEFAULT_BEDTIME_VOICE):
        self.profile = VOICE_PROFILES.get(profile_name, VOICE_PROFILES[DEFAULT_BEDTIME_VOICE])

    async def synthesize(self, text: str, output_path: str, profile_name: Optional[str] = None) -> str:
        """
        Synthesizes text into high-quality speech using Edge-TTS.
        """
        import edge_tts

        prof = VOICE_PROFILES.get(profile_name, self.profile) if profile_name else self.profile
        
        voice = prof["voice"]
        rate = prof["rate"]
        pitch = prof.get("pitch", "+0Hz")
        volume = prof.get("volume", "+0%")

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        await communicate.save(str(out_file))
        return str(out_file)

    def synthesize_sync(self, text: str, output_path: str, profile_name: Optional[str] = None) -> str:
        return asyncio.run(self.synthesize(text, output_path, profile_name))
