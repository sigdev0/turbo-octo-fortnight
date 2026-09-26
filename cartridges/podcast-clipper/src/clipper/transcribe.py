import json
import os
import re
import subprocess
import tempfile

import imageio_ffmpeg
from groq import Groq

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

CHUNK_DUR = 300  # 5 min per Groq call (well under 25MB)


def _probe_duration(audio_path):
    stderr = subprocess.run(
        [FFMPEG, "-i", audio_path], capture_output=True, text=True, check=False
    ).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if not m:
        raise RuntimeError(f"cannot probe duration: {audio_path}")
    h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mnt * 60 + s


def _split_audio(audio_path, work_dir, chunk_sec=CHUNK_DUR):
    duration = _probe_duration(audio_path)
    chunks = []
    offset = 0.0
    while offset < duration:
        end = min(offset + chunk_sec, duration)
        out = os.path.join(work_dir, f"_chunk_{offset:.0f}.wav")
        subprocess.run(
            [
                FFMPEG,
                "-y",
                "-i",
                audio_path,
                "-ss",
                str(offset),
                "-t",
                str(end - offset),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                out,
            ],
            check=True,
            capture_output=True,
        )
        chunks.append({"path": out, "offset": offset})
        offset = end
    return chunks


def transcribe_groq(audio_path, settings):
    fsize = os.path.getsize(audio_path)
    if fsize > 24_000_000:
        return transcribe_groq_chunked(audio_path, settings)
    client = Groq(api_key=os.environ[settings["groq"]["api_key_env"]])
    with open(audio_path, "rb") as f:
        out = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f.read()),
            model=settings["groq"]["model"],
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
        )
    segs = []
    for s in out.segments:
        words = [
            {"start": w["start"], "end": w["end"], "w": w["word"]}
            for w in out.words
            if w["start"] >= s["start"] and w["end"] <= s["end"]
        ]
        segs.append(
            {
                "start": s["start"],
                "end": s["end"],
                "text": s["text"].strip(),
                "words": words,
            }
        )
    return {"segments": segs, "lang": getattr(out, "language", "en")}


def transcribe_groq_chunked(audio_path, settings):
    with tempfile.TemporaryDirectory() as tmp:
        chunks = _split_audio(audio_path, tmp)
        client = Groq(api_key=os.environ[settings["groq"]["api_key_env"]])
        all_segs = []
        lang = "en"
        for c in chunks:
            with open(c["path"], "rb") as f:
                out = client.audio.transcriptions.create(
                    file=(os.path.basename(c["path"]), f.read()),
                    model=settings["groq"]["model"],
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"],
                )
            lang = getattr(out, "language", lang)
            offset = c["offset"]
            for s in out.segments:
                words = [
                    {
                        "start": w["start"] + offset,
                        "end": w["end"] + offset,
                        "w": w["word"],
                    }
                    for w in out.words
                    if w["start"] >= s["start"] and w["end"] <= s["end"]
                ]
                all_segs.append(
                    {
                        "start": s["start"] + offset,
                        "end": s["end"] + offset,
                        "text": s["text"].strip(),
                        "words": words,
                    }
                )
    all_segs.sort(key=lambda s: s["start"])
    return {"segments": all_segs, "lang": lang}


def transcribe_local(audio_path, settings):
    from faster_whisper import WhisperModel

    model = WhisperModel(
        settings["transcribe"]["local_model"],
        compute_type=settings["transcribe"]["local_compute"],
    )
    segments, info = model.transcribe(audio_path, word_timestamps=True)
    segs = [
        {
            "start": s.start,
            "end": s.end,
            "text": s.text.strip(),
            "words": [
                {"start": w.start, "end": w.end, "w": w.word} for w in (s.words or [])
            ],
        }
        for s in segments
    ]
    return {"segments": segs, "lang": info.language}


def transcribe(audio_path, settings, out_path=None):
    try:
        t = transcribe_groq(audio_path, settings)
        t["backend"] = "groq"
    except Exception as e:  # noqa: BLE001
        print(f"groq failed ({e}), falling back to local CPU")
        t = transcribe_local(audio_path, settings)
        t["backend"] = "local"
    if out_path:
        with open(out_path, "w") as f:
            json.dump(t, f, indent=1)
    return t
