# podcast-clipper

Download → transcribe → rank → clip pipeline that turns podcast episodes into
captioned 9:16 YouTube Shorts.

> Next steps: [Limitations](docs/LIMITATIONS.md) · [Roadmap](docs/ROADMAP.md)
>
> Interface decision: CLI + Telegram bot (R-10) for personal use. Web UI is
> deferred until ship/sell-ready — see roadmap "Ship-prep alignment".

## How it works

Five stages, orchestrated by `clipper/pipeline.py:process`:

| # | Stage | Module | What happens |
|---|-------|--------|--------------|
| 1 | Download | `clipper/download.py` | yt-dlp fetches ≤720p video + extracts 16 kHz mono WAV |
| 2 | Transcribe | `clipper/transcribe.py` | Groq `whisper-large-v3-turbo` with word timestamps; CPU fallback on failure |
| 3 | Prefilter | `clipper/prefilter.py` | Heuristic scan builds ~45 s candidate windows, keeps top 20 |
| 4 | Rank | `clipper/rank.py` | LLM scores candidates 0–100 for Shorts virality, dedupes overlaps |
| 5 | Clips | `clipper/clip.py` + `clipper/caption.py` | Crop to 1080×1920, optionally follow speakers per shot, burn in captions, H.264 MP4 |

Per-episode artifacts live in `work/<name>/`, finished clips in `output/<name>/`:

```text
work/<name>/…vid.source.mp4  # downloaded video (reused on re-run)
work/<name>/…vid.audio.wav   # extracted audio
work/<name>/transcript.json  # segments + word timestamps + lang
work/<name>/candidates.json  # prefilter windows with heuristic scores
work/<name>/ranked.json      # LLM-scored, deduped, best first
output/<name>/clip0.mp4 + clip0.ass  # finished clip + its subtitle file
```

## Setup

```bash
uv venv .venv && uv pip install -r requirements.txt
export GROQ_API_KEY=gsk_...
export NINE_ROUTER_API_KEY=sk_...
```

`uv` manages the venv; `ffmpeg` comes bundled via `imageio-ffmpeg` (no sudo
needed — `download.py` symlinks it into `work/<name>/bin/` so yt-dlp finds it).
The rank step calls a local 9router gateway (`nine_router.base_url`, default
`http://127.0.0.1:20128/v1`) — it must be running and the API key valid.
Ranking is pinned deterministic by default (`nine_router.temperature: 0.0`,
`seed: 42`), so the same transcript yields the same scores; the earlier drift
(92 → 82 → 72 across repeat runs) came from unpinned sampling.

## Usage

```bash
# full pipeline: URL -> captioned 9:16 clips in output/<name>/
.venv/bin/python cli.py process "https://youtu.be/..." --name ep1

# same, with caption style, platform preset and clip-count overrides
.venv/bin/python cli.py process "https://youtu.be/..." --name ep1 --style bold --preset tiktok --max-clips 5

# resume after failure: reuse cached transcript.json / ranked.json
.venv/bin/python cli.py process "https://youtu.be/..." --name ep1 --resume

# batch: process every source in config/sources.yaml (continue-on-error)
.venv/bin/python cli.py batch
.venv/bin/python cli.py batch --sources config/sources.yaml --resume

# costs: summarize per-run time/token log
.venv/bin/python cli.py costs
.venv/bin/python cli.py costs --month 2026-09

# subcommands for debugging / re-running single stages
.venv/bin/python cli.py transcribe work/ep1/xxx.audio.wav --out t.json
.venv/bin/python cli.py rank t.json --out ranked.json
.venv/bin/python cli.py clip source.mp4 ranked.json --out-dir output/x --style hormozi --max-clips 3
```

Re-runs are cheap: existing `source.mp4` / `audio.wav` files are reused, and
`--resume` reuses cached `transcript.json` / `ranked.json`.

## Telegram bot

```bash
export TELEGRAM_TOKEN=... TELEGRAM_ALLOWED_USER_ID=...
export GROQ_API_KEY=... NINE_ROUTER_API_KEY=...
.venv/bin/python bot/clipbot.py
```

Send `/help`, paste a YouTube URL, or use
`/clip <url> [--style X] [--preset Y] [--max N] [--layout auto|crop|fit] [--smart-crop] [--follow] [--loudnorm] [--fresh]`.
Re-queuing the same URL reuses the previous run's transcript + ranking directly
(pipeline stays `--resume`); add `--fresh` to force a re-rank.
Per job: live stage edits, full log at `work/<job>/job.log`, classified failure reason
with a Retry button, `/logs <job>` to inspect, `/retry <job>` to resume from cache.
`/digest` builds a **theme-aware** digest: recent channel uploads grouped by the
themes of your already-clipped videos, plus a "Trending on your themes" section.
Already-clipped and recently-shown videos are never repeated. `/costs [YYYY-MM]`
summarizes spend.

Config from Telegram:
- `/config` — show **all** configuration (bot defaults + pipeline + settable keys + styles + presets)
- `/config <key> <value>` — bot defaults: `style`, `preset`, `max_clips`, `digest_time`,
  plus digest tuning (`digest_cooldown_days`, `digest_top_n`, `digest_theme_weight`,
  `digest_trending_enabled`, `digest_trending_window_days`, `digest_trending_seeds`,
  `digest_trending_per_seed`, `digest_trending_min_duration_s`, `digest_trending_top_n`) — all validated
- `/settings [section[.key]]` — read-only view of `config/settings.yaml`
- `/set <section.key> <value>` — curated override (writes `settings.yaml`, applies to the next job)
- `/style [name]`, `/preset [name]` — list or show parameters

The 19 settable keys are listed by `/config`; everything else in `settings.yaml`
(`base_url`, `*_env`, `paths.*`, `groq.model`, `clips.default_style`, `config_version`)
is read-only.

### Daily digest

`/digest` and the daily job (24h after `digest_time`) are stateful:

- **Theme profile** — the top clips of every done job (`work/<job>/ranked.json`)
  are tokenized (EN+ID stopwords, unigrams + bigrams) into weighted keywords,
  cached in `work/digest_profile.json` and rebuilt only when clips change.
- **Tier 1 (channels)** — latest uploads per `sources.yaml` channel, scored by
  `digest_score` + keyword theme affinity (title + description), filtered against
  already-*clipped* videos and anything shown within `digest_cooldown_days`, then
  grouped by the shared theme.
- **Tier 2 (trending, always shown)** — YouTube upload-date search seeded by the
  theme phrases/keywords surfaces recent long-form, on-theme uploads, ranked by
  affinity + view count; if nothing lands inside `digest_trending_window_days` it
  falls back to the newest on-theme match rather than show an empty section.
- Emitted picks are recorded in `work/digest_state.json` so the digest does not
  repeat itself.

## Stage details

### Download

- Rejects videos over `download.max_duration_s` (default 5400 s / 90 min).
- Format ladder `bv*[height<=720]+ba/b[height<=720]/b` keeps files small.
- Audio is extracted once as mono 16 kHz WAV, the format the transcribers want.

### Transcribe

- Primary: Groq `whisper-large-v3-turbo` with `verbose_json` + word and segment
  timestamps. Files over ~24 MB are split into 5-minute chunks, transcribed
  separately, and re-offset into one timeline.
- Fallback: any Groq failure prints a warning and retries locally with
  `faster-whisper` (`transcribe.local_model`, default `small`, `int8` compute).
- Output records which backend was used (`"backend": "groq" | "local"`).

### Prefilter

Slides ~45 s windows (segment-aligned, 50 % overlap) over the transcript and
scores each one:

- question mark `+2`, exclamation `+1.5`
- hook words `+1` each (max `+4`), English + Indonesian lists
- numbers `+0.5` each (max `+2`), 120–200 wpm pace `+1`
- intro/outro proximity (`skip_intro_outro_s`, default 30 s) `−3`
- duration outside `min_clip_s`–`max_clip_s` (default 20–70 s) `−2`

Top `max_candidates` (default 20) windows go to the rank step.

### Rank

Sends the candidates to `nine_router.rank_model` (default
`ollama/gpt-oss:120b`) with `prompts/rank_v1.txt`, which asks for a bare
JSON array of `{id, score, hook, reason}`. Behavior notes:

- The model is a reasoning model — `max_tokens` (default 6000) must leave room
  for thinking tokens or replies come back empty.
- Fallback chain `nine_router.rank_models` (default `ollama/gpt-oss:120b` →
  `bai-auto/deepseek-v4-flash` → `opencode/muse-spark-1.3-contributor-free`)
  rotates across models on failure.
- 4 attempts with linear backoff; tolerant JSON parsing (fences stripped,
  longest valid `[...]` prefix, else loose `{...}` objects).
- Results are sorted by score and overlapping windows are deduped (highest
  score wins), so clips never cover the same moment twice.

### Clips & captions

- Layout is chosen by `clips.layout` (`auto|crop|fit`, default `auto`):
  - `crop` — center-crop to the 9:16 frame (or smart-crop if `clips.smart_crop`).
  - `fit` — full frame scaled to width over a blurred, darkened fill. Use for
    ultra-wide / single-subject sources (`auto` picks it when aspect ≥
    `clips.fit_ratio`, default 2.0).
  - `follow_speaker` forces `crop` and makes the window **jump between speakers**:
    the clip is split on the source's camera cuts (`clips.scene_thresh`, 0.15),
    and inside each shot the window follows whoever is most mouth-active,
    switching with hysteresis (`clips.follow_min_dwell`, 1.5 s) so laughter and
    reactions pull the camera without jitter. Per-shot crop-x is emitted as a
    step expression so the edit hard-cuts like a hand-made clip. Use for
    multi-person podcasts (`--follow` on the bot).
- Output is scaled to 1080×1920 and encoded `libx264 preset fast crf 20` +
  `aac 128k` with `+faststart` for streaming.
- Captions are generated as ASS subtitles (`clipper/caption.py:write_ass`):
  word-level timestamps chunked into short lines; the phrase is colored in the
  style's highlight color. (Per-word karaoke emphasis is not implemented yet.)
- Three presets in `config/styles/`: `hormozi` (Arial Black, yellow, uppercase,
  centered), `minimal` (plain Arial, bottom), `bold` (Verdana, orange). Any JSON
  with the same keys works as a custom style.

## Config

`config/settings.yaml` — all tunables in one place:

| Section | Key keys |
|---------|----------|
| `nine_router` | `base_url`, `api_key_env`, `rank_model`, `rank_models`, `max_tokens`, `timeout_s`, `temperature`, `seed` |
| `groq` | `api_key_env`, `model` |
| `transcribe` | `primary`, `fallback`, `local_model`, `local_compute` |
| `download` | `max_duration_s`, `format` |
| `prefilter` | `min_clip_s`, `max_clip_s`, `max_candidates`, `skip_intro_outro_s` |
| `clips` | `default_style`, `max_clips`, `width`, `height`, `crf`, `x264_preset`, `sidecars`, `layout`, `fit_ratio`, `fit_blur_sigma`, `fit_brightness`, `loudnorm`, `trim_silence`, `smart_crop`, `smart_crop_samples`, `smart_crop_thresh`, `follow_speaker`, `scene_thresh`, `follow_fps`, `follow_min_dwell` |
| `paths` | `work_dir`, `output_dir` |

Per-run overrides from the CLI: `cli.py process <url> --set clips.layout=fit --set clips.crf=18`
(repeatable; only keys in `<src>/clipper/settings_schema.py:SETTABLE` are allowed, and
values are validated). The bot wraps the same mechanism via `/set` and the
`--layout/--smart-crop/--follow/--loudnorm` clip flags.

`config/sources.yaml` holds a podcast source list for `cli.py batch` (per-source
`name`, `style`, `preset`, `max_clips`, `weight`, plus `layout` / `follow_speaker`
and an `overrides` map of any settable key). Secrets are never stored here,
only env-var names via `*_env` keys.

Pick the layout per source style:
- **talking-head / multi-person, no burned-in graphics** → `layout: crop` (or
  `follow_speaker: true`) for a face-filling vertical.
- **sources with their own captions, slides, or centre images** (e.g. language
  lessons) → `layout: fit`, which keeps the whole frame in a centred strip over
  a blurred fill so the source's text/graphics are not cut off. `fit` disables
  `follow_speaker`.

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/ruff check src/ cli.py tests/
```

Covers prefilter heuristics, caption timing/position, presets, layout selection,
batch, costs, settings validation, and the bot (config, failure classification).

## Troubleshooting

- `401 Missing API key` on rank → 9router gateway needs a valid key in
  `NINE_ROUTER_API_KEY` and must be reachable at `nine_router.base_url`.
- `groq failed (...), falling back to local CPU` → check `GROQ_API_KEY`; local
  fallback works offline but is much slower.
- `video Ns exceeds Ms cap` → episode too long for `download.max_duration_s`.
- `rank failed: empty content` → reasoning model ran out of tokens; raise
  `nine_router.max_tokens`.
- `rank parse failed` → model returned non-JSON; retry (automatic ×4) or try a
  different `rank_model`.
- Clips with no burned-in captions → check the `.ass` file exists next to the
  MP4; the `subtitles` filter path must be readable by ffmpeg.
