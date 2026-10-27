import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR, DEFAULT_LANGUAGE
from core.voice import VoiceSynthesizer
from core.media import MediaMixer
from core.router import LLMRouter
from cartridges.story_library import get_story_fallback

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
            en_keywords = {"space", "forest", "castle", "courage", "kindness", "gentleness", "patience"}
            words = set((theme + " " + lesson).lower().split())
            if words & en_keywords and not (words & {"dan", "ke", "di", "yang", "anak", "sabar", "awan", "hutan"}):
                return False
            return True

        # Check keywords
        id_keywords = {
            "hutan", "awan", "bintang", "bulan", "hewan", "kebaikan",
            "kesabaran", "keberanian", "tidur", "mimpi", "sahabat",
            "perahu", "laut", "pantai", "sungai", "kunang", "kejora",
            "candi", "borobudur", "danau", "toba", "bromo", "sabana", "kereta", "rimba"
        }
        words = set((theme + " " + lesson).lower().split())
        return bool(words & id_keywords)

    def _select_archetype(self, theme: str, name: str = "") -> str:
        """
        Selects an authentic storytelling archetype based on theme keywords or deterministic variety.
        """
        th = theme.lower()
        if any(k in th for k in ["candi", "borobudur", "stupa", "menoreh", "relief", "temple"]):
            return "candi_borobudur"
        if any(k in th for k in ["danau", "toba", "samosir", "ikan mas", "kaldera", "lake", "crater"]):
            return "danau_toba"
        if any(k in th for k in ["bromo", "sabana", "savana", "pasir berbisik", "tengger", "whispering sand", "kuda", "horse"]):
            return "sabana_bromo"
        if any(k in th for k in ["kereta", "uap", "rel", "masinis", "kondektur", "gerbong", "train", "railway", "locomotive", "express"]):
            return "kereta_rimba"
        if any(k in th for k in ["laut", "pantai", "ombak", "perahu", "pinisi", "pulau", "sea", "ocean", "boat", "sail", "island", "beach", "waves"]):
            return "perahu_pinisi"
        if any(k in th for k in ["hutan", "rimba", "pohon", "hewan", "kancil", "rusa", "cendrawasih", "taman", "burung", "forest", "jungle", "tree", "animals", "creatures", "woods", "garden"]):
            return "hutan_kalpataru"
        if any(k in th for k in ["awan", "langit", "gunung", "kabut", "teh", "melati", "angin", "sejuk", "cloud", "sky", "mountain", "mist", "wind", "breeze", "tea", "jasmine"]):
            return "negeri_atas_awan"
        if any(k in th for k in ["sungai", "kunang", "lentera", "cahaya", "rawa", "river", "firefly", "lantern", "glow", "stream", "swamp"]):
            return "lentera_kunang_kunang"
        if any(k in th for k in ["bintang", "bulan", "angkasa", "antariksa", "kejora", "ruang", "star", "moon", "space", "galaxy", "starlight", "cosmic"]):
            return "bintang_kejora"

        # Deterministic variation across different names and themes
        archetypes = [
            "perahu_pinisi", "hutan_kalpataru", "negeri_atas_awan",
            "lentera_kunang_kunang", "bintang_kejora", "candi_borobudur",
            "danau_toba", "sabana_bromo", "kereta_rimba"
        ]
        return archetypes[abs(hash(name + theme)) % len(archetypes)]

    def _generate_fallback_script(self, name: str, age: int, theme: str, lesson: str, is_id: bool = True, archetype: str = "negeri_atas_awan") -> str:
        """
        High-fidelity, calibrated multi-movement sleep scripts (380-450 words for toddlers, 650-750 words for older kids)
        incorporating Indonesian folklore, nature wonders, and somatic relaxation cues.
        """
        return get_story_fallback(
            archetype=archetype,
            age=age,
            is_id=is_id,
            name=name,
            theme=theme,
            lesson=lesson
        )

    async def _generate_llm_script(self, name: str, age: int, theme: str, lesson: str, archetype: str, is_id: bool = True) -> str:
        """
        Generates an original, multi-movement sleep journey (380-850 words) via the LLM Router.
        """
        router = LLMRouter()
        if not router.is_configured:
            return self._generate_fallback_script(name, age, theme, lesson, is_id=is_id, archetype=archetype)

        if is_id:
            word_target = "450 hingga 600 kata" if age <= 3 else "750 hingga 950 kata"
            system_prompt = (
                "Anda adalah master penulis cerita pengantar tidur anak (pediatric bedtime sleep storyteller) kelas dunia, "
                "setara dengan standar emas Moshi Sleep dan Riri Cerita Anak. "
                "Tuliskan naskah audio pengantar tidur yang SANGAT menenangkan, puitis, dan menghanyutkan jiwa dalam tutur tutur ibu/ayah Indonesia yang luwes.\n"
                f"TARGET PANJANG NASKAH: {word_target}. JANGAN membuat rangkuman pendek di bawah 400 kata!\n\n"
                "ARSITEKTUR 5 GERAKAN PENURUNAN TIDUR (SLEEP DESCENT):\n"
                "1. Gerakan 1 (Grounding Kamar & Napas): Mengajak anak menarik selimut hangat menyelimuti pundak dan dada, "
                "menyelaraskan napas pelan (tarik napas lembut... hembuskan perlahan), dan menegaskan bahwa waktu bermain hari ini sudah selesai dengan indah.\n"
                "2. Gerakan 2 (Memasuki Alam Cerita yang Tenang): Melukiskan suasana malam yang hangat dan aman. "
                "Gunakan detail sensoris fisik (desir ombak, wangi melati, bantal sutra empuk). JANGAN gunakan istilah siang hari seperti 'teduh' untuk malam hari.\n"
                "3. Gerakan 3 (Sahabat Satwa Mengantuk / Mirror-Neuron Mimicry): Fokus pada SATU sahabat satwa yang sangat mengantuk. "
                "Gambarkan gestur fisiknya secara detail: merapatkan tubuh ke sarang/perahu, menguap pelan, dan membiarkan kelopak matanya yang berat menutup perlahan.\n"
                "4. Gerakan 4 (Somatic Body Wind-Down): Relaksasi fisik progresif dari ujung jemari kaki, merambat naik ke betis, punggung, "
                "pundak turun bersandar bebas, dan kedua kelopak mata terasa sangat berat dan mengantuk.\n"
                "5. Gerakan 5 (Bisikan Kasih & Nina Bobo): Afirmasi tulus bahwa anak senantiasa aman dan disayangi ayah-ibu selamanya, "
                "diakhiri bisikan selamat tidur yang lembut memudar ke dalam musik.\n\n"
                "PANDUAN GAYA BAHASA & FONETIK (STANDAR EMAS):\n"
                "- Gunakan kata-kata berfonetik lembut: semilir, lembut, hening, lelap, empuk, damai, desir, hangat, pelan.\n"
                "- JANGAN gunakan terjemahan kaku seperti 'pundakmu yang santai' (gunakan 'sampai menyelimuti pundak dan dadamu').\n"
                "- JANGAN ada konflik eksternal, musuh, bahaya, atau kejutan apa pun.\n"
                "- Sisipkan tanda '...' pada jeda napas yang menenangkan.\n"
                "- Pisahkan setiap gerakan dengan jeda baris ganda (\\n\\n) agar pembacaan memiliki jeda napas santai.\n"
                "- HANYA keluarkan teks narasi yang diucapkan. Jangan sertakan judul, bab, catatan panggung, atau tanda kurung efek suara."
            )
            user_prompt = (
                f"Tuliskan naskah cerita tidur tidur lengkap ({word_target}) untuk anak usia {age} tahun bernama {name}.\n"
                f"Tema dunia: {theme} (Archetype inspirasi: {archetype}).\n"
                f"Nilai karakter / pesan moral: {lesson}."
            )
        else:
            word_target = "450 to 600 words" if age <= 3 else "750 to 950 words"
            system_prompt = (
                "You are a master pediatric sleep storyteller and bedtime audio specialist, "
                "benchmarking against the gold standard of Moshi Sleep and Calm Kids. "
                "Write an immersive, deeply calming, hypnotic bedtime sleep journey for a child.\n"
                f"TARGET WORD COUNT: {word_target}. DO NOT write short summaries under 400 words!\n\n"
                "5-MOVEMENT PROGRESSIVE SLEEP DESCENT ARCHITECTURE:\n"
                "1. Movement 1 (Sensory Grounding & Breath): Pulling warm blankets up over shoulders and chest, "
                "synchronizing slow rhythmic breathing (deep breath in... and long gentle exhale), declaring playtime complete.\n"
                "2. Movement 2 (Gentle World Entrance): Painting a warm, serene nocturnal realm. "
                "Focus on tactile textures (whispering sea swells, jasmine aromas, plush velvet cushions). No daytime terms.\n"
                "3. Movement 3 (The Drowsy Companion / Mirror-Neuron Mimicry): Focus on ONE gentle sleepy creature. "
                "Depict its drowsiness in slow detail: curling up snugly, taking a sleepy yawn, and letting heavy eyelids close completely.\n"
                "4. Movement 4 (Somatic Body Wind-Down): Progressive muscular relaxation from toes up through calves, back sinking into bed, "
                "shoulders dropping completely, eyelids too delightfully heavy to open.\n"
                "5. Movement 5 (Whisper Blessing & Drift): Reassurances of unconditional parental love and safety, "
                "fading into quiet dreamland.\n\n"
                "LINGUISTIC & PHONETIC GUIDELINES:\n"
                "- Favor soft, liquid consonants and soothing words: drift, cradle, velvet, amber, whisper, shimmer, uncurl, settle, soft, glow.\n"
                "- ZERO external conflict, villains, alarms, or hurry.\n"
                "- Insert '...' at natural calming breath pauses.\n"
                "- Separate each movement with double line breaks (\\n\\n) to create narrative breathing room.\n"
                "- Output ONLY spoken narrative text. Do NOT include titles, stage directions, scene headers, or sound effect brackets."
            )
            user_prompt = (
                f"Write a full-length sleep adventure ({word_target}) for a {age}-year-old child named {name}.\n"
                f"Theme / setting: {theme} (Inspirational archetype: {archetype}).\n"
                f"Core character virtue: {lesson}."
            )
        try:
            script = await router.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.7)
            
            # Verify script isn't unexpectedly truncated
            if len(script.split()) < 250:
                return self._generate_fallback_script(name, age, theme, lesson, is_id=is_id, archetype=archetype)
            return script
        except Exception:
            return self._generate_fallback_script(name, age, theme, lesson, is_id=is_id, archetype=archetype)

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        on_progress: Optional[Callable[[str], Any]] = payload.get("on_progress")

        child_name = payload.get("name", "Little Explorer").capitalize()
        age = int(payload.get("age", 8))
        theme = payload.get("theme", "negeri bintang" if DEFAULT_LANGUAGE == "id" else "the Starlight Forest")
        lesson = payload.get("lesson", "kesabaran dan kebaikan" if DEFAULT_LANGUAGE == "id" else "patience and kindness")
        lang = payload.get("lang")

        is_id = self._is_indonesian(lang, theme, lesson)
        archetype = self._select_archetype(theme, child_name)

        # Voice selection: Prefer ElevenLabs when API key is active, with seamless Edge-TTS fallback
        from core.config import ELEVENLABS_API_KEY
        if is_id:
            default_voice = "indonesian_female" if age <= 4 else "indonesian_male"
        else:
            if ELEVENLABS_API_KEY:
                default_voice = "elevenlabs_maternal" if age <= 4 else "elevenlabs_storyteller"
            else:
                default_voice = "bedtime_female" if age <= 3 else "bedtime_british"
        voice_profile = payload.get("voice_profile", default_voice)

        # 1. Script Generation (V2 Multi-Movement Sleep Arc)
        if on_progress:
            step_msg = (
                f"📖 Merangkai dongeng tidur Nusantara ({archetype.replace('_', ' ').title()})..."
                if is_id else
                f"📖 Weaving deep sleep adventure ({archetype.replace('_', ' ').title()})..."
            )
            await on_progress(step_msg)

        script_text = payload.get("script")
        if not script_text:
            script_text = await self._generate_llm_script(
                name=child_name,
                age=age,
                theme=theme,
                lesson=lesson,
                archetype=archetype,
                is_id=is_id
            )

        # 2. File Naming
        safe_name = child_name.lower().replace(" ", "_")
        lang_tag = "id" if is_id else "en"
        raw_voice_file = OUTPUT_DIR / f"voice_{safe_name}_{age}yo_{lang_tag}.mp3"
        final_mixed_file = OUTPUT_DIR / f"bedtime_story_{safe_name}_{age}yo_{lang_tag}.mp3"

        # 3. Voice Synthesis (Edge-TTS)
        if on_progress:
            step_msg = (
                f"🎙️ Merekam suara narator relaksasi tidur ('{voice_profile}')..."
                if is_id else
                f"🎙️ Recording soothing sleep narration ('{voice_profile}')..."
            )
            await on_progress(step_msg)

        voice_engine = VoiceSynthesizer(profile_name=voice_profile)
        await voice_engine.synthesize(
            text=script_text,
            output_path=str(raw_voice_file),
            profile_name=voice_profile
        )

        # 4. Media Mixing (ffmpeg with smart ducking and 18s sleep outro padding)
        if on_progress:
            step_msg = (
                "🎵 Menggabungkan musik tidur ambient & outro relaksasi..."
                if is_id else
                "🎵 Mixing harmonic ambient sleep bed & outro relaxation..."
            )
            await on_progress(step_msg)
        from core.config import MUSIC_DIR
        music_map = {
            "perahu_pinisi": MUSIC_DIR / "ocean_stars_ambient.mp3",
            "danau_toba": MUSIC_DIR / "ocean_stars_ambient.mp3",
            "hutan_kalpataru": MUSIC_DIR / "nature_night_crickets_rain.mp3",
            "lentera_kunang_kunang": MUSIC_DIR / "nature_night_crickets_rain.mp3",
            "sabana_bromo": MUSIC_DIR / "nature_night_crickets_rain.mp3",
            "negeri_atas_awan": MUSIC_DIR / "lullaby_piano_gymnopedie.mp3",
            "bintang_kejora": MUSIC_DIR / "lullaby_piano_gymnopedie.mp3",
            "candi_borobudur": MUSIC_DIR / "lullaby_piano_gymnopedie.mp3",
            "kereta_rimba": MUSIC_DIR / "lullaby_piano_gymnopedie.mp3"
        }
        selected_music = music_map.get(archetype, MUSIC_DIR / "nature_night_crickets_rain.mp3")
        music_path = str(selected_music) if selected_music.exists() else None

        mixer = MediaMixer()
        mixer.mix_voice_and_music(
            voice_path=str(raw_voice_file),
            output_path=str(final_mixed_file),
            music_path=music_path,
            music_volume=0.22 if "piano" in str(music_path) else 0.35,
            voice_volume=1.0,
            fade_out_sec=4.0,
            outro_padding_sec=16.0
        )
        # Clean up temporary raw voice
        if raw_voice_file.exists():
            raw_voice_file.unlink()

        if on_progress:
            await on_progress("✨ Audio pengantar tidur selesai!" if is_id else "✨ Bedtime sleep audio complete!")

        # Dynamic title based on archetype and language
        if is_id:
            title_map = {
                "perahu_pinisi": f"Pelayaran Pinisi Bintang {child_name}",
                "hutan_kalpataru": f"Misteri Damai Hutan Kalpataru {child_name}",
                "negeri_atas_awan": f"Petualangan {child_name} di Negeri Atas Awan",
                "lentera_kunang_kunang": f"Cahaya Kunang-Kunang Rawa Tenang {child_name}",
                "bintang_kejora": f"Nyanyian Bintang Kejora {child_name}"
            }
            title = title_map.get(archetype, f"Petualangan {child_name} ke {theme.title()}")
        else:
            title_map = {
                "perahu_pinisi": f"{child_name}'s Starlight Canoe Voyage",
                "hutan_kalpataru": f"{child_name} & the Whispering Sanctuary",
                "negeri_atas_awan": f"{child_name}'s Cloud Kingdom Journey",
                "lentera_kunang_kunang": f"{child_name} & the River of Fireflies",
                "bintang_kejora": f"{child_name} & the Sleepy Constellations"
            }
            title = title_map.get(archetype, f"{child_name}'s Journey into {theme.title()}")

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
                "archetype": archetype,
                "language": "id" if is_id else "en",
                "voice_profile": voice_profile,
                "word_count": len(script_text.split())
            }
        }
