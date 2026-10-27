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
        Generates a peaceful, soothing stereo ambient soundscape:
        warm sub-harmonic meditation drone + gentle pink noise surf swells.
        Renders high-quality stereo 44.1kHz 192kbps MP3.
        """
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        fade_out_start = max(0, duration_sec - 5)
        filter_str = (
            f"anoisesrc=d={duration_sec}:c=pink:r=44100:a=0.035,lowpass=f=550[surf];"
            f"aevalsrc='0.022*sin(2*PI*55*t) + 0.018*sin(2*PI*110*t) + 0.012*sin(2*PI*164.81*t)':"
            f"d={duration_sec}:s=44100,lowpass=f=350,afade=t=in:ss=0:d=4,afade=t=out:st={fade_out_start}:d=5[drone];"
            f"[surf][drone]amix=inputs=2:duration=first,"
            f"stereotools=mlev=0.75:slev=1.2,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[out]"
        )

        cmd = [
            self.ffmpeg, "-y",
            "-filter_complex", filter_str,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(out_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return str(out_path)
    def generate_documentary_bed(self, duration_sec: int, output_path: str) -> str:
        """
        Generates an ancient Nusantara epic documentary soundscape:
        - Gamelan Slendro bronze resonance synthesis (130.81Hz C3 gong ageng, 196Hz G3 kempul, 261.63Hz C4 saron, 329.63Hz E4 bonang)
        - Periodic metallic decay envelope simulating bronze gong and saron strikes
        - Atmospheric foley layer: low-frequency torch crackle/wind + sacred river waters
        - Mastered in high-fidelity stereo 44.1kHz 192kbps MP3 normalized to -24.0 LUFS.
        """
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        fade_out_start = max(0, duration_sec - 4)
        gamelan_expr = (
            "0.045*sin(2*PI*130.81*t)*exp(-0.8*mod(t,5)) + "
            "0.035*sin(2*PI*196.00*t)*exp(-1.2*mod(t+2.5,5)) + "
            "0.025*sin(2*PI*261.63*t)*exp(-1.8*mod(t+1.25,2.5)) + "
            "0.020*sin(2*PI*329.63*t)*exp(-2.2*mod(t+0.6,2.5)) + "
            "0.010*sin(2*PI*523.25*t)*exp(-3.0*mod(t+1.25,2.5))"
        )

        filter_str = (
            f"aevalsrc='{gamelan_expr}':d={duration_sec}:s=44100[gamelan];"
            f"anoisesrc=d={duration_sec}:c=brown:r=44100:a=0.03,highpass=f=120,lowpass=f=900[foley_wind];"
            f"anoisesrc=d={duration_sec}:c=pink:r=44100:a=0.015,bandpass=f=600:width_type=h:w=300[foley_water];"
            f"[gamelan][foley_wind][foley_water]amix=inputs=3:duration=first,"
            f"afade=t=in:ss=0:d=2,afade=t=out:st={fade_out_start}:d=3,"
            f"loudnorm=I=-24.0:LRA=7.0:TP=-2.0,"
            f"stereotools=mlev=0.8:slev=1.2,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[out]"
        )

        cmd = [
            self.ffmpeg, "-y",
            "-filter_complex", filter_str,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(out_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return str(out_path)

    def mix_voice_and_music(
        self,
        voice_path: str,
        output_path: str,
        music_path: Optional[str] = None,
        music_volume: float = 0.35,
        voice_volume: float = 1.0,
        fade_out_sec: float = 4.0,
        outro_padding_sec: float = 14.0,
        ducking_threshold: float = 0.04,
        ducking_ratio: float = 2.5,
        ducking_attack_ms: float = 200.0,
        ducking_release_ms: float = 900.0
    ) -> str:
        """
        Mixes voiceover with background music using professional sidechain ducking.
        - Applies warm vocal EQ (sub-bass cleanup, chest resonance, sibilance taming).
        - Ducks background bed when voice speaks; smoothly swells during pauses.
        - Mastered in high-fidelity 44.1kHz stereo at 192 kbps.
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
                self.generate_ambient_bed(duration_sec=600, output_path=str(default_music))
            music_path = str(default_music)

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
            total_duration = voice_duration + outro_padding_sec
            fade_start = max(0.0, total_duration - fade_out_sec)

            filter_complex = (
                f"[0:a]volume={voice_volume},aformat=sample_rates=44100:channel_layouts=stereo,"
                f"highpass=f=80,lowshelf=f=250:g=1.5,highshelf=f=5500:g=-2.5[voice_warmed];"
                f"[voice_warmed]apad=pad_dur={outro_padding_sec}[voice_padded];"
                f"[voice_padded]asplit[voice_out][voice_trigger];"
                f"[1:a]volume={music_volume},apad=pad_dur={outro_padding_sec}[bg_scaled];"
                f"[bg_scaled][voice_trigger]sidechaincompress=threshold={ducking_threshold}:ratio={ducking_ratio}:attack={ducking_attack_ms}:release={ducking_release_ms}[ducked_bg];"
                f"[voice_out][ducked_bg]amix=inputs=2:duration=longest:dropout_transition=0[mixed];"
                f"[mixed]atrim=duration={total_duration:.2f},afade=t=out:st={fade_start:.2f}:d={fade_out_sec:.2f}[final]"
            )
        except Exception:
            # Resilient fallback if ffprobe or sidechain fails
            filter_complex = (
                f"[0:a]volume={voice_volume},aformat=sample_rates=44100:channel_layouts=stereo,"
                f"apad=pad_dur={outro_padding_sec}[voice];"
                f"[1:a]volume={music_volume}[bg];"
                f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=4[final]"
            )

        cmd = [
            self.ffmpeg, "-y",
            "-i", str(voice),
            "-stream_loop", "-1",
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[final]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(out)
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError:
            # Secondary fallback with basic mix if advanced filter fails
            fallback_complex = (
                f"[0:a]volume={voice_volume},apad=pad_dur={outro_padding_sec}[v];"
                f"[1:a]volume={music_volume * 0.5}[b];"
                f"[v][b]amix=inputs=2:duration=first[f]"
            )
            fallback_cmd = [
                self.ffmpeg, "-y",
                "-i", str(voice),
                "-stream_loop", "-1",
                "-i", str(music_path),
                "-filter_complex", fallback_complex,
                "-map", "[f]",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(out)
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        return str(out)
