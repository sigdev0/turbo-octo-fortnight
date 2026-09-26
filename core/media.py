import subprocess
import shutil
from pathlib import Path
from typing import Optional
from core.config import MUSIC_DIR

class MediaMixer:
    def __init__(self, ffmpeg_bin: str = "ffmpeg"):
        self.ffmpeg = shutil.which(ffmpeg_bin) or "ffmpeg"

    def generate_ambient_bed(self, duration_sec: int, output_path: str) -> str:
        """
        Generates a peaceful, soothing ambient chord drone using ffmpeg audio synthesis.
        Perfect as an automatic fallback background bed.
        """
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Harmonic C-major / F-major soft ambient frequencies (warm, sleepy meditation drone)
        filter_str = (
            "aevalsrc=sin(261.63*2*PI*t)*0.03 + sin(329.63*2*PI*t)*0.025 + "
            "sin(392.00*2*PI*t)*0.02 + sin(130.81*2*PI*t)*0.04:s=44100:d={d},"
            "lowpass=f=800,afade=t=in:ss=0:d=2,afade=t=out:st={out_start}:d=3"
        ).format(d=duration_sec, out_start=max(0, duration_sec - 3))

        cmd = [
            self.ffmpeg, "-y",
            "-f", "lavfi",
            "-i", filter_str,
            "-c:a", "libmp3lame",
            "-q:a", "4",
            str(out_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return str(out_path)

    def mix_voice_and_music(
        self,
        voice_path: str,
        output_path: str,
        music_path: Optional[str] = None,
        music_volume: float = 0.12,
        voice_volume: float = 1.0,
        fade_out_sec: float = 3.0
    ) -> str:
        """
        Mixes voiceover with background music using ffmpeg.
        Loops the music if necessary and ends exactly when the voiceover finishes.
        """
        voice = Path(voice_path)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if not voice.exists():
            raise FileNotFoundError(f"Voice file not found: {voice_path}")

        # If no music specified, use default or generate an ambient bed
        if not music_path or not Path(music_path).exists():
            default_music = MUSIC_DIR / "ambient_sleep_bed.mp3"
            if not default_music.exists():
                self.generate_ambient_bed(duration_sec=300, output_path=str(default_music))
            music_path = str(default_music)

        # Complex filter:
        # 1. Loop background music indefinitely
        # 2. Adjust volumes (voice = 1.0, music = ~0.12 / -22dB)
        # 3. amix duration=first (cut off when voice finishes)
        filter_complex = (
            f"[1:a]volume={music_volume}[bg];"
            f"[0:a]volume={voice_volume}[voice];"
            f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=3[mixed];"
            f"[mixed]afade=t=out:st=0:d={fade_out_sec}:curve=exp[final]"
        )

        # Get voice duration for fade out
        duration_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(voice)
        ]
        try:
            res = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            voice_duration = float(res.stdout.strip())
            fade_start = max(0.0, voice_duration - fade_out_sec)
            filter_complex = (
                f"[1:a]volume={music_volume}[bg];"
                f"[0:a]volume={voice_volume}[voice];"
                f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=3[mixed];"
                f"[mixed]afade=t=out:st={fade_start:.2f}:d={fade_out_sec}[final]"
            )
        except Exception:
            # Fallback if ffprobe isn't available
            filter_complex = (
                f"[1:a]volume={music_volume}[bg];"
                f"[0:a]volume={voice_volume}[voice];"
                f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=3[final]"
            )

        cmd = [
            self.ffmpeg, "-y",
            "-i", str(voice),
            "-stream_loop", "-1",
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[final]",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            str(out)
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return str(out)
