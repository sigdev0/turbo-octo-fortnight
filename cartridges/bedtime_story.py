import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR
from core.voice import VoiceSynthesizer
from core.media import MediaMixer
from core.router import LLMRouter

class BedtimeStoryCartridge(BaseCartridge):
    @property
    def name(self) -> str:
        return "bedtime_story"

    @property
    def command(self) -> str:
        return "story"

    @property
    def description(self) -> str:
        return "Generates screen-free personalized bedtime audio adventures for kids (Ages 2-8)."

    def _generate_fallback_script(self, name: str, age: int, theme: str, lesson: str) -> str:
        """
        High-quality handcrafted story template when testing without an active LLM router.
        """
        if age <= 3:
            return (
                f"Once upon a time, in a cozy little world, little {name} looked up at the quiet night sky. "
                f"The moon was smiling down, round and silver. "
                f"Soft clouds drifted by, like warm fluffy pillows. "
                f"In the land of {theme}, every little creature was getting ready to sleep. "
                f"The tiny bunnies closed their eyes. Shhh... quiet now. "
                f"Little {name} took a slow, deep breath in... and let it out. "
                f"You are safe, you are loved, and you are so very kind. "
                f"Close your eyes, sweet {name}. It is time to dream. Goodnight, little explorer. Goodnight."
            )
        else:
            return (
                f"The evening stars were just beginning to flicker across the deep indigo sky. "
                f"Eight-year-old {name} lay comfortably beneath the blankets, ready for an adventure into {theme}. "
                f"Tonight, the gentle wind carried a secret across the whispering treetops: true strength always begins with {lesson}. "
                f"As {name} ventured past the glowing silver bridge, a friendly guide with glowing emerald wings stepped forward. "
                f"'Welcome, {name},' the guide whispered warmly. 'We have been waiting for someone with a heart as patient as yours.' "
                f"Together, they journeyed through the quiet valleys where the starlight danced upon the quiet river. "
                f"When a small challenge arose along the path, {name} remembered that quiet courage and {lesson} could light up even the darkest forest. "
                f"With a soft smile, {name} solved the puzzle, bringing warmth and peace to the entire realm. "
                f"The silver owl hooted a gentle song from high above in the ancient branches. "
                f"The eyelids grew heavy. The breathing became slow, deep, and peaceful. "
                f"The adventure was complete, and tomorrow would bring new wonders. "
                f"Sleep peacefully now, {name}. The stars are watching over you. Goodnight."
            )

    async def _generate_llm_script(self, name: str, age: int, theme: str, lesson: str) -> str:
        """
        Generates an original, sleep-calibrated story via the LLM Router.
        """
        router = LLMRouter()
        if not router.is_configured:
            return self._generate_fallback_script(name, age, theme, lesson)

        system_prompt = (
            "You are a master children's bedtime story author and pediatric sleep audio specialist. "
            "Write a calming, imaginative bedtime audio story script designed to ease a child to sleep. "
            "Guidelines: "
            "- Calming, poetic rhythm that progressively slows down towards the end. "
            "- Under 250 words total. "
            "- Emphasize slow breathing, physical relaxation, feeling safe and loved. "
            "- Conclude with a whispery goodnight blessing. "
            "- Output ONLY the spoken story narrative text. No stage directions or sound effect notes."
        )
        user_prompt = (
            f"Write a bedtime story for a {age}-year-old child named {name}. "
            f"Theme / setting: {theme}. Core moral / lesson: {lesson}."
        )
        try:
            return await router.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.7)
        except Exception:
            return self._generate_fallback_script(name, age, theme, lesson)

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        on_progress: Optional[Callable[[str], Any]] = payload.get("on_progress")

        child_name = payload.get("name", "Little Explorer").capitalize()
        age = int(payload.get("age", 8))
        theme = payload.get("theme", "the Starlight Forest")
        lesson = payload.get("lesson", "patience and kindness")
        
        # Default voice based on age if not specified
        default_voice = "bedtime_female" if age <= 3 else "bedtime_british"
        voice_profile = payload.get("voice_profile", default_voice)

        # 1. Script Generation
        if on_progress:
            await on_progress("📖 Weaving personalized bedtime story...")

        script_text = payload.get("script")
        if not script_text:
            script_text = await self._generate_llm_script(
                name=child_name,
                age=age,
                theme=theme,
                lesson=lesson
            )

        # 2. File Naming
        safe_name = child_name.lower().replace(" ", "_")
        raw_voice_file = OUTPUT_DIR / f"voice_{safe_name}_{age}yo.mp3"
        final_mixed_file = OUTPUT_DIR / f"bedtime_story_{safe_name}_{age}yo.mp3"

        # 3. Voice Synthesis (Edge-TTS)
        if on_progress:
            await on_progress("🎙️ Synthesizing soothing neural voiceover...")

        voice_engine = VoiceSynthesizer(profile_name=voice_profile)
        await voice_engine.synthesize(
            text=script_text,
            output_path=str(raw_voice_file),
            profile_name=voice_profile
        )

        # 4. Media Mixing (ffmpeg with smart audio ducking)
        if on_progress:
            await on_progress("🎵 Mixing harmonic sleep soundtrack & audio ducking...")

        mixer = MediaMixer()
        mixer.mix_voice_and_music(
            voice_path=str(raw_voice_file),
            output_path=str(final_mixed_file),
            music_volume=0.10,
            voice_volume=1.0,
            fade_out_sec=3.0
        )

        # Clean up temporary raw voice
        if raw_voice_file.exists():
            raw_voice_file.unlink()

        if on_progress:
            await on_progress("✨ Audio rendering complete!")

        return {
            "status": "success",
            "title": f"{child_name}'s Journey into {theme.title()}",
            "output_file": str(final_mixed_file),
            "script": script_text,
            "metadata": {
                "child_name": child_name,
                "age": age,
                "theme": theme,
                "lesson": lesson,
                "voice_profile": voice_profile
            }
        }
