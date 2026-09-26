# Limitations

Known constraints of the current pipeline, sourced from code. Update this file when a limitation is fixed.

## Download (`src/clipper/download.py`)

- Single URL per `process()`; `cli.py batch` and `config/sources.yaml` run several sequentially.
- Hard cap `download.max_duration_s` (default 5400 s / 90 min). Longer videos raise `ValueError`, no auto-split.
- Fixed 720p format ladder. Higher resolutions are never fetched.
- No cookies / login / age-gate support. Members-only, private, or login-walled videos fail.
- No playlist support. One video per invocation.
- Stale-file reuse: if `<id>.source.mp4` / `<id>.audio.wav` exist in `work/<name>/`, they are reused silently even if the URL changed. Delete the dir to force re-download.
- Merge-leftover heuristic (`os.listdir` prefix match) can misfire if two videos share an ID prefix in the same dir.

## Transcribe (`src/clipper/transcribe.py`)

- Groq 24 MB single-call limit: files over ~24 MB are split into 5-min chunks (`CHUNK_DUR = 300`) and re-offset. Chunk boundaries can cut words mid-utterance; no overlap/reconciliation.
- Fragile duration probe: parses `ffmpeg -i` stderr text with `.split("Duration:")[1]...split(":")[0]` (keeps hours only on first try, falls back to a second parse). Unusual ffmpeg output breaks it.
- No speaker diarization. Multi-speaker podcasts get no speaker labels.
- Local CPU fallback is `faster-whisper` `small` + `int8` — works offline but takes ~40-60 min per episode and is less accurate than Groq `whisper-large-v3-turbo`.
- Broad `except Exception` on Groq failure: any error (bad key, rate limit, network) silently falls back to slow local instead of failing fast. A typo'd API key looks like "just slow".
- Chunk temp files use `tempfile.TemporaryDirectory`, cleaned up even on success — no cache for retry.

## Prefilter (`src/clipper/prefilter.py`)

- English + Indonesian hook-word lists only (`HOOK_WORDS_EN`, `HOOK_WORDS_ID`). Other languages score lower.
- Relies on Whisper punctuation: question `+2` / exclamation `+1.5` only fire if the transcriber emitted `?` / `!`. Flat transcripts lose these signals.
- Fixed ~45 s windows (segment-aligned, 50% overlap). Hooks near a window edge get split across two candidates and score worse.
- Clips outside 20-70 s (`min_clip_s`/`max_clip_s`) are penalized, never produced. No support for <20 s punchlines or 70-180 s Shorts.
- No audio cues (laughter, applause, volume spikes) and no visual cues (scene change, face on screen). Text-only scoring.
- Intro/outro penalty is positional only (`skip_intro_outro_s`, default 30 s). Sponsored mid-roll segments are not detected.
- Empty transcript (`segments == []`) yields zero candidates with no explicit error.

## Rank (`src/clipper/rank.py`, `prompts/rank_v1.txt`)

- Hard dependency on the 9router gateway (`nine_router.base_url`, default `http://127.0.0.1:20128/v1`) being up with a valid `NINE_ROUTER_API_KEY`. No offline fallback.
- Reasoning-token budget: default `max_tokens: 6000` must leave room for thinking tokens or replies come back empty (`rank failed: empty content`). Smaller limits break ranking silently after 4 retries.
- Fragile JSON contract: one-shot prompt asks for a bare JSON array; parsing relies on fence-stripping + longest-valid-`[...]`-prefix + loose `{...}` fallback. Model chatter can still break it (`rank parse failed`).
- Unknown candidate IDs in the model reply are silently dropped; if all are dropped, output is an empty list with no error.
- Overlap dedupe keeps highest score only — a second great moment inside the same window is lost.
- No score calibration across episodes. A "78" in one run is not comparable to "78" in another.
- Stdlib `urllib` client: no connection pooling, no request logging, 300 s default timeout blocks the whole run on a hung gateway.

## Clips & captions (`src/clipper/clip.py`, `src/clipper/caption.py`)

- Center-crop default; `clips.smart_crop` opt-in (YuNet, conservative). Single static crop per clip — multi-cut windows pick the dominant face position; PiP insets handled by area weighting but not perfectly.
- Clip start/end land on word timestamps (no scene snap), so a clip can begin or end mid-gesture.
- `clips.follow_speaker` (R-15/R-16) tracks the active speaker and switches on mouth-band motion (measured in a YuNet-landmark mouth box), but it is **visual-only** — no audio diarization (the reference podcast is near-mono, L/R corr 0.998). Non-speech mouth motion, head turns, or an off-screen speaker can still cause a wrong or missed cut; raise `clips.follow_min_dwell` to calm rapid switching. Shot detection needs a scene score above `clips.scene_thresh` (0.15); gradual cuts are missed. Motion/graphics sequences (intros, B-roll) can produce many false cuts.
- Loudness/silence are opt-in (`clips.loudnorm` / `clips.trim_silence`, default false). No per-clip auto-gain.
- Output is always 9:16 (platform presets cover `shorts`/`tiktok`/`reels`). No 1:1 or landscape output. Ultra-wide sources use `layout: fit` (blurred fill) instead of losing speakers to a crop.
- `layout: fit` is the right call for sources with **burned-in captions / slides / centre images** (crop cuts them off), but it shrinks the speakers to a ~1080×609 centred strip and disables `follow_speaker`. There is no automatic "this source has graphics" detection — set it per source in `config/sources.yaml` (`layout: fit`) or on the CLI/bot (`--layout fit`).
- Burned-in ASS requires ffmpeg with libass and system fonts (`Arial Black`, `Verdana`, `Arial` per style). Missing fonts silently fall back to something ugly.
- SRT/VTT sidecars written per `clips.sidecars`, but captions are still burned from ASS only — no platform-native caption upload.
- `write_ass` caps word duration at `max_word_dur_s` (1.5 s) and chunks at `max_words_per_line` (default 4) — mistimed words produce overlapping or zero-length events clamped to 0.1 s.
- `cut_clips` overwrites `clip0.mp4` / `clip0.ass` on re-run with no backup.
- Single `-ss` fast seek: frame-accurate at keyframes only, can drift ~0.5 s on long-GOP sources.

## Pipeline & UX (`src/clipper/pipeline.py`, `cli.py`)

- `print`, not logging. Bot captures per-job stdout to `work/<job>/job.log`, but the pipeline/CLI has no `--quiet`/`--verbose`, no global log file, no timestamps.
- Must run from repo root: `load_settings("config/settings.yaml")`, `prompts/rank_v1.txt`, and `config/styles/` are relative paths.
- Secrets via env vars only (`GROQ_API_KEY`, `NINE_ROUTER_API_KEY`); missing vars raise raw `KeyError` with no hint.
- Offline integration test covers process() with mocked download/transcribe/rank (R-09a). No live end-to-end test; Docker image deferred to ship (R-09b).

## Telegram bot (`bot/clipbot.py`)

- Digest theme matching is **keyword overlap only** — no embeddings (the 9router gateway exposes no embeddings endpoint). Synonyms/paraphrases that share no tokens are missed.
- The "trending" tier is a **view-sort / upload-date-sort search proxy**, not YouTube's official trending feed (`/feed/trending` no longer extracts with yt-dlp). Results are region/language dependent, and a theme with no recent on-topic long-form falls back to the newest match (possibly months old) rather than nothing.
- Trending adds extra YouTube scraping (search + per-video metadata); it fails open (empty section) on errors or bot-checks, so a blocked scrape silently drops the section.
- Digest state (`work/digest_state.json`) and the theme profile (`work/digest_profile.json`) live under `work/` (gitignored); deleting `work/` resets digest memory.
- "Already clipped" is derived from `done` jobs in `work/bot_queue.json`; a video clipped outside the bot won't be recognised as clipped.
