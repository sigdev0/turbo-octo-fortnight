import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR, DEFAULT_LANGUAGE
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
        return "Generates screen-free personalized bedtime audio adventures for kids in English or Bahasa Indonesia."

    def _is_indonesian(self, lang: Optional[str], theme: str, lesson: str) -> bool:
        if lang:
            return lang.lower().strip() in ("id", "id-id", "indonesia", "indo", "bahasa")
        
        # Check environment default
        if DEFAULT_LANGUAGE.lower() in ("id", "indonesia"):
            # Check if user didn't explicitly request english words
            en_keywords = {"space", "forest", "castle", "courage", "kindness", "gentleness", "patience"}
            words = set((theme + " " + lesson).lower().split())
            if words & en_keywords and not (words & {"dan", "ke", "di", "yang", "anak", "sabar"}):
                return False
            return True

        # Check keywords
        id_keywords = {"hutan", "awan", "bintang", "bulan", "hewan", "kebaikan", "kesabaran", "keberanian", "tidur", "mimpi", "sahabat"}
        words = set((theme + " " + lesson).lower().split())
        return bool(words & id_keywords)

    def _generate_fallback_script(self, name: str, age: int, theme: str, lesson: str, is_id: bool = True) -> str:
        """
        High-quality handcrafted story template when testing without an active LLM router.
        """
        if is_id:
            if age <= 3:
                return (
                    f"Pada suatu malam yang tenang di negeri yang indah, si kecil {name} memandang ke langit malam yang bertabur bintang. "
                    f"Bulan tersenyum ramah, bulat dan bersinar lembut. "
                    f"Awan-awan berarak pelan, selembut bantal yang hangat. "
                    f"Di dunia {theme}, semua makhluk kecil mulai bersiap untuk tidur. "
                    f"Kelinci-kelinci kecil memejamkan mata mereka dengan damai. Shhh... hening dan tenang sekarang. "
                    f"Si kecil {name} menarik napas perlahan... lalu menghembuskannya dengan lega. "
                    f"Kamu aman, kamu sangat disayangi, dan kamu anak yang hebat serta penuh kebaikan. "
                    f"Pejamkan matamu, manis. Saatnya bermimpi indah. Selamat tidur, penjelajah kecil. Selamat malam."
                )
            else:
                return (
                    f"Bintang-bintang malam mulai berkelip lembut di langit biru pekat. "
                    f"{name} yang berusia {age} tahun berbaring nyaman di bawah selimut hangat, siap menjelajahi keajaiban {theme}. "
                    f"Malam ini, semilir angin membawa bisikan rahasia dari pucuk pepohonan: bahwa kekuatan sejati selalu bermula dari {lesson}. "
                    f"Ketika melintasi jembatan perak yang bercahaya, sahabat peri hutan melangkah mendekat dengan senyum hangat. "
                    f"'Selamat datang, {name},' bisiknya lembut. 'Kami telah menanti seorang pahlawan dengan hati yang sabar dan penuh kebaikan sepertimu.' "
                    f"Bersama-sama, mereka menyusuri lembah sunyi di mana cahaya bintang menari riang di atas aliran sungai yang tenang. "
                    f"Saat sebuah rintangan kecil muncul di perjalanan, {name} ingat bahwa ketenangan hati dan {lesson} mampu menerangi jalan yang paling gelap sekalipun. "
                    f"Dengan senyuman manis, {name} berhasil menyelesaikan teka-teki itu, membawa kedamaian dan kehangatan ke seluruh penjuru alam. "
                    f"Burung hantu perak bersenandung merdu dari dahan pohon kuno. "
                    f"Kelopak mata terasa semakin berat. Napas menjadi semakin perlahan, tenang, dan damai. "
                    f"Petualangan malam ini telah usai, dan esok akan membawa keajaiban baru. "
                    f"Tidurlah dengan nyenyak, {name}. Bintang-bintang selalu menjagamu. Selamat malam."
                )
        else:
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
                    f"{age}-year-old {name} lay comfortably beneath the blankets, ready for an adventure into {theme}. "
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

    async def _generate_llm_script(self, name: str, age: int, theme: str, lesson: str, is_id: bool = True) -> str:
        """
        Generates an original, sleep-calibrated story via the LLM Router.
        """
        router = LLMRouter()
        if not router.is_configured:
            return self._generate_fallback_script(name, age, theme, lesson, is_id=is_id)

        if is_id:
            system_prompt = (
                "Anda adalah master penulis cerita pengantar tidur anak dan spesialis audio relaksasi tidur. "
                "Tuliskan naskah audio cerita pengantar tidur yang SANGAT menenangkan dan lembut dalam Bahasa Indonesia yang indah. "
                "Panduan penulisan: "
                "- Ritme cerita santai, menenangkan, dan semakin melambat menjelang akhir. "
                "- Panjang maksimal 220 kata. "
                "- Berikan afirmasi rasa aman, disayangi orang tua, dan relaksasi napas perlahan. "
                "- Akhiri dengan ucapan selamat tidur dan doa mimpi indah yang damai. "
                "- HANYA keluarkan teks narasi yang diucapkan. Jangan sertakan petunjuk panggung atau catatan suara efek."
            )
            user_prompt = (
                f"Tuliskan cerita tidur untuk anak usia {age} tahun bernama {name}. "
                f"Tema dunia imajinasi: {theme}. Pesan moral / karakter: {lesson}."
            )
        else:
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
            return self._generate_fallback_script(name, age, theme, lesson, is_id=is_id)

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        on_progress: Optional[Callable[[str], Any]] = payload.get("on_progress")

        child_name = payload.get("name", "Little Explorer").capitalize()
        age = int(payload.get("age", 8))
        theme = payload.get("theme", "negeri bintang" if DEFAULT_LANGUAGE == "id" else "the Starlight Forest")
        lesson = payload.get("lesson", "kesabaran dan kebaikan" if DEFAULT_LANGUAGE == "id" else "patience and kindness")
        lang = payload.get("lang")

        is_id = self._is_indonesian(lang, theme, lesson)

        # Voice selection based on language and age
        if is_id:
            default_voice = "indonesian_female" if age <= 3 else "indonesian_male"
        else:
            default_voice = "bedtime_female" if age <= 3 else "bedtime_british"
            
        voice_profile = payload.get("voice_profile", default_voice)

        # 1. Script Generation
        if on_progress:
            await on_progress("📖 Merangkai cerita pengantar tidur yang menenangkan..." if is_id else "📖 Weaving personalized bedtime story...")

        script_text = payload.get("script")
        if not script_text:
            script_text = await self._generate_llm_script(
                name=child_name,
                age=age,
                theme=theme,
                lesson=lesson,
                is_id=is_id
            )

        # 2. File Naming
        safe_name = child_name.lower().replace(" ", "_")
        lang_tag = "id" if is_id else "en"
        raw_voice_file = OUTPUT_DIR / f"voice_{safe_name}_{age}yo_{lang_tag}.mp3"
        final_mixed_file = OUTPUT_DIR / f"bedtime_story_{safe_name}_{age}yo_{lang_tag}.mp3"

        # 3. Voice Synthesis (Edge-TTS)
        if on_progress:
            await on_progress(f"🎙️ Merekam suara narator ('{voice_profile}')..." if is_id else "🎙️ Synthesizing soothing neural voiceover...")

        voice_engine = VoiceSynthesizer(profile_name=voice_profile)
        await voice_engine.synthesize(
            text=script_text,
            output_path=str(raw_voice_file),
            profile_name=voice_profile
        )

        # 4. Media Mixing (ffmpeg with smart audio ducking)
        if on_progress:
            await on_progress("🎵 Menggabungkan musik tidur ambient & audio ducking..." if is_id else "🎵 Mixing harmonic sleep soundtrack & audio ducking...")

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
            await on_progress("✨ Audio selesai dirender!" if is_id else "✨ Audio rendering complete!")

        title = f"Petualangan {child_name} ke {theme.title()}" if is_id else f"{child_name}'s Journey into {theme.title()}"

        return {
            "status": "success",
            "title": title,
            "output_file": str(final_mixed_file),
            "script": script_text,
            "metadata": {
                "child_name": child_name,
                "age": age,
                "theme": theme,
                "lesson": lesson,
                "language": "id" if is_id else "en",
                "voice_profile": voice_profile
            }
        }
