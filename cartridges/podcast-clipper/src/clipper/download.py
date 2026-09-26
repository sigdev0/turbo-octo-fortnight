import os
import subprocess

import imageio_ffmpeg
import yaml
from yt_dlp import YoutubeDL

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXPECTED_CONFIG_VERSION = 1


def load_settings(path="config/settings.yaml"):
    if not os.path.exists(path):
        alt_path = os.path.join(ROOT_DIR, path)
        if os.path.exists(alt_path):
            path = alt_path
    with open(path) as f:
        settings = yaml.safe_load(f)
    ver = settings.get("config_version")
    if ver != EXPECTED_CONFIG_VERSION:
        print(
            f"warning: config_version={ver} != expected {EXPECTED_CONFIG_VERSION} "
            f"({path}) — schemas may have changed"
        )
    return settings


def _ydl_opts(settings, fmt, source, tmpdir, player_client=None):
    opts = {
        "format": fmt,
        "outtmpl": source,
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": tmpdir,
    }
    clients = player_client or (settings.get("download", {}).get("player_clients") or [])
    if clients:
        opts["extractor_args"] = {"youtube": {"player_client": clients}}
    return opts


def download(url, work_dir, settings=None):
    settings = settings or load_settings()
    max_dur = settings["download"]["max_duration_s"]
    fmt = settings["download"]["format"]
    os.makedirs(work_dir, exist_ok=True)
    with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    duration = info.get("duration") or 0
    if duration > max_dur:
        raise ValueError(f"video {duration}s exceeds {max_dur}s cap")
    vid = info.get("id", "video")
    source = os.path.join(work_dir, f"{vid}.source.mp4")
    audio = os.path.join(work_dir, f"{vid}.audio.wav")
    if not os.path.exists(source):
        tmpdir = os.path.join(work_dir, "bin")
        os.makedirs(tmpdir, exist_ok=True)
        link = os.path.join(tmpdir, "ffmpeg")
        try:
            if not os.path.exists(link):
                os.symlink(FFMPEG, link)
        except OSError:
            pass
        env = dict(os.environ)
        env["PATH"] = tmpdir + os.pathsep + env.get("PATH", "")
        with YoutubeDL(_ydl_opts(settings, fmt, source, tmpdir)) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                if os.path.exists(source) and os.path.getsize(source) > 0:
                    pass
                else:
                    err = str(e)
                    if "403" in err or "Forbidden" in err:
                        with YoutubeDL(
                            _ydl_opts(settings, "18/best", source, tmpdir, ["android"])
                        ) as y2:
                            y2.download([url])
                    else:
                        raise
        merged = [
            f
            for f in os.listdir(work_dir)
            if f.startswith(os.path.basename(source)) and f != os.path.basename(source)
        ]
        for m in merged:
            mp = os.path.join(work_dir, m)
            if mp != source and os.path.getsize(mp) > 0:
                if not os.path.exists(source) or os.path.getsize(source) == 0:
                    os.replace(mp, source)
                else:
                    os.remove(mp)
    if not os.path.exists(audio):
        if not os.path.exists(source) or os.path.getsize(source) == 0:
            raise RuntimeError(f"download failed, no usable file for {url}")
        subprocess.run(
            [FFMPEG, "-y", "-i", source, "-vn", "-ac", "1", "-ar", "16000", audio],
            check=True,
            capture_output=True,
        )
    return {
        "id": vid,
        "title": info.get("title", ""),
        "duration": duration,
        "source": source,
        "audio": audio,
    }
