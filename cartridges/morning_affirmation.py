import asyncio
from pathlib import Path
from typing import Dict, Any
from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR, DEFAULT_LANGUAGE
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
        return "Generates empowering morning affirmations for kids and adults in English or Bahasa Indonesia."

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_name = payload.get("name", "Sahabat" if DEFAULT_LANGUAGE == "id" else "Friend").capitalize()
        theme = payload.get("theme", "keberanian dan kebaikan" if DEFAULT_LANGUAGE == "id" else "courage and strength")
        lang = payload.get("lang")

        is_id = False
        if lang:
            is_id = lang.lower().strip() in ("id", "id-id", "indonesia", "indo")
        elif DEFAULT_LANGUAGE.lower() in ("id", "indonesia"):
            is_id = True

        if is_id:
            voice_profile = payload.get("voice_profile", "indonesian_affirmation")
            script_text = (
                f"Selamat pagi, {target_name}! Hari ini adalah hari baru yang penuh dengan kebaikan dan peluang hebat. "
                f"Ingatlah bahwa keberanianmu selalu lebih besar dari tantangan apa pun, dan kebaikan hatimu adalah kekuatan supermu. "
                f"Tarik napas yang dalam, percaya pada dirimu sendiri, dan pancarkan senyum terbaikmu hari ini. Kamu pasti bisa!"
            )
            title = f"Afirmasi Pagi {target_name}"
        else:
            voice_profile = payload.get("voice_profile", "energetic_affirmation")
            script_text = (
                f"Good morning, {target_name}! Today is a brand new day full of opportunity. "
                f"Remember that your courage is bigger than any challenge, and your kindness is your superpower. "
                f"Take a deep breath, believe in yourself, and let your light shine bright today. You've got this!"
            )
            title = f"{target_name}'s Daily Boost"

        safe_name = target_name.lower().replace(" ", "_")
        lang_tag = "id" if is_id else "en"
        raw_voice_file = OUTPUT_DIR / f"voice_{safe_name}_{self.name}_{lang_tag}.mp3"
        final_file = OUTPUT_DIR / f"{self.name}_{safe_name}_{lang_tag}.mp3"

        on_progress = payload.get("on_progress")
        if on_progress:
            await on_progress("🎙️ Merekam naskah afirmasi positif..." if is_id else "🎙️ Recording positive affirmation voiceover...")

        voice_engine = VoiceSynthesizer(profile_name=voice_profile)
        await voice_engine.synthesize(
            text=script_text,
            output_path=str(raw_voice_file),
            profile_name=voice_profile
        )

        if on_progress:
            await on_progress("🎵 Menggabungkan musik pengiring ceria..." if is_id else "🎵 Mixing uplifting morning soundtrack...")

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
            "title": title,
            "output_file": str(final_file),
            "script": script_text,
            "metadata": {
                "target_name": target_name,
                "theme": theme,
                "language": "id" if is_id else "en",
                "cartridge": self.name
            }
        }
