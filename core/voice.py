import asyncio
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
from core.config import VOICE_PROFILES, DEFAULT_BEDTIME_VOICE

class VoiceSynthesizer:
    def __init__(self, profile_name: str = DEFAULT_BEDTIME_VOICE):
        self.profile = VOICE_PROFILES.get(profile_name, VOICE_PROFILES[DEFAULT_BEDTIME_VOICE])
        self.ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    def _normalize_hush_tokens(self, text: str) -> str:
        """Edge-TTS spells 'Shhh' as S-H-H-H; replace with a breathable exhale cue."""
        return re.sub(r"\b[Ss][Hh]{2,}[Hh]*\b", "syuh", text)

    async def _synthesize_single_chunk(self, text: str, output_path: str, prof: dict) -> str:
        text = self._normalize_hush_tokens(text)
        if prof.get("engine") == "elevenlabs":
            from core.config import ELEVENLABS_API_KEY
            if ELEVENLABS_API_KEY:
                try:
                    import httpx
                    voice_id = prof.get("voice_id", "EXAVITQu4vr4xnSDxMaL")
                    model_id = prof.get("model_id", "eleven_multilingual_v2")
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                    headers = {
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "text": text,
                        "model_id": model_id,
                        "voice_settings": {
                            "stability": prof.get("stability", 0.45),
                            "similarity_boost": prof.get("similarity_boost", 0.85),
                            "style": prof.get("style", 0.20),
                            "use_speaker_boost": True
                        }
                    }
                    async with httpx.AsyncClient(timeout=45.0) as client:
                        resp = await client.post(url, json=payload, headers=headers)
                        if resp.status_code == 200:
                            Path(output_path).write_bytes(resp.content)
                            return output_path
                except Exception:
                    pass

            # Graceful fallback to Edge-TTS on quota exhaustion or network error
            fallback_name = prof.get("fallback", "indonesian_female")
            fallback_prof = VOICE_PROFILES.get(fallback_name, VOICE_PROFILES[DEFAULT_BEDTIME_VOICE])
            return await self._synthesize_single_chunk(text, output_path, fallback_prof)

        # Standard Edge-TTS synthesizer ($0 unmetered)
        import edge_tts
        communicate = edge_tts.Communicate(
            text=text,
            voice=prof.get("voice", "id-ID-ArdiNeural"),
            rate=prof.get("rate", "-10%"),
            pitch=prof.get("pitch", "+0Hz"),
            volume=prof.get("volume", "+0%")
        )
        await communicate.save(output_path)
        return output_path

    def _segment_text(self, text: str, target_words: int = 45) -> List[str]:
        """
        Splits text into narrative movements or paragraph chunks.
        Honors explicit double newlines if present, otherwise groups sentences
        into ~40-55 word movements for natural sleep wind-down pacing.
        """
        clean_text = text.strip()
        if "\n\n" in clean_text:
            return [p.strip() for p in re.split(r"\n\s*\n", clean_text) if p.strip()]

        # Split by sentence boundaries (. or ... or ! or ? followed by space)
        sentences = re.split(r"(?<=[.!?…])\s+(?=[A-Z\d\"'“‘])", clean_text)
        movements: List[str] = []
        current_chunk: List[str] = []
        current_word_count = 0

        for s in sentences:
            s = s.strip()
            if not s:
                continue
            words = len(s.split())
            current_chunk.append(s)
            current_word_count += words
            if current_word_count >= target_words:
                movements.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0

        if current_chunk:
            if movements and len(" ".join(current_chunk).split()) < 20:
                movements[-1] += " " + " ".join(current_chunk)
            else:
                movements.append(" ".join(current_chunk))

        return movements or [clean_text]

    async def synthesize(
        self,
        text: str,
        output_path: str,
        profile_name: Optional[str] = None,
        enable_pacing: bool = True,
        pause_duration_sec: float = 1.2
    ) -> str:
        """
        Synthesizes text into high-quality speech using Edge-TTS with narrative breath pacing.
        Inserts calibrated silence breath breaks between movements for calming rhythm.
        """
        prof = VOICE_PROFILES.get(profile_name, self.profile) if profile_name else self.profile
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        clean_text = text.strip()
        movements = self._segment_text(clean_text)

        if not enable_pacing or len(movements) <= 1:
            return await self._synthesize_single_chunk(clean_text, str(out_file), prof)

        tmpdir = tempfile.mkdtemp(prefix="omniforge_tts_")
        try:
            chunk_files: List[Path] = []
            for idx, movement in enumerate(movements):
                chunk_path = Path(tmpdir) / f"m_{idx:03d}.mp3"
                await self._synthesize_single_chunk(movement, str(chunk_path), prof)
                chunk_files.append(chunk_path)

            # Generate calibrated silence segment
            silence_path = Path(tmpdir) / "pause.mp3"
            silence_cmd = [
                self.ffmpeg, "-y",
                "-f", "lavfi",
                "-i", "anullsrc=r=24000:cl=mono",
                "-t", f"{pause_duration_sec:.2f}",
                "-c:a", "libmp3lame",
                "-b:a", "64k",
                str(silence_path)
            ]
            subprocess.run(silence_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            # Build ffmpeg concat manifest
            concat_manifest = Path(tmpdir) / "concat.txt"
            with open(concat_manifest, "w", encoding="utf-8") as f:
                for idx, chunk_file in enumerate(chunk_files):
                    f.write(f"file '{chunk_file.resolve().as_posix()}'\n")
                    if idx < len(chunk_files) - 1:
                        f.write(f"file '{silence_path.resolve().as_posix()}'\n")

            # Stitch chunks with zero-reencode copy
            concat_cmd = [
                self.ffmpeg, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_manifest),
                "-c", "copy",
                str(out_file)
            ]
            subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return str(out_file)

        except Exception:
            # Fallback to single-chunk synthesis if concat fails
            return await self._synthesize_single_chunk(clean_text, str(out_file), prof)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def synthesize_sync(self, text: str, output_path: str, profile_name: Optional[str] = None) -> str:
        return asyncio.run(self.synthesize(text, output_path, profile_name))
