# Roadmap

Next-development items. Each entry: problem, proposal, acceptance criteria, priority, effort.

Priority: **P0** = blocks correctness/scale, **P1** = high value, **P2** = nice-to-have.
Effort: **S** = <1 day, **M** = 1-3 days, **L** = 3+ days.

## R-01 Batch runner from `sources.yaml` — P0 / M ✅ DONE

- **Status:** implemented. `cli.py batch [--sources] [--style] [--max-clips] [--resume]` runs `process()` per entry with per-source name/style/max_clips overrides, continue-on-error, exit 1 listing failures. Verified live: 1 ok (cached channel) + 1 failed (invalid URL) → exit 1.

- **Problem:** `process()` takes one URL; `config/sources.yaml` is dead config. Multi-source workflow means manual per-URL runs.
- **Proposal:** `cli.py batch` subcommand: read `sources.yaml`, run `process()` per entry (URL + name + style + max_clips overrides), continue-on-error with per-source summary.
- **Acceptance:** `cli.py batch --sources config/sources.yaml` processes 2+ URLs in one invocation; one failed URL doesn't kill the rest; exit code non-zero with failed-source list.

## R-02 `--skip-*` / `--resume` CLI flags — P0 / S ✅ DONE

- **Status:** implemented. `cli.py process` accepts `--skip-transcribe --skip-rank --resume`. Verified: `--resume` on cached `work/channel` skips transcribe+rank, goes straight to clipping.

- **Problem:** `skip_transcribe` / `skip_rank` exist in `process()` but unreachable from CLI. Re-runs after a rank failure redo the slow transcribe.
- **Proposal:** Add `--skip-transcribe --skip-rank --resume` to `cli.py process`. `--resume` implies both skips when cached `transcript.json` / `ranked.json` exist.
- **Acceptance:** `process URL --name ep1 --resume` reuses cached JSON and goes straight to clipping; flags documented in README Usage.

## R-03 Face-tracking / smart crop — P1 / L ✅ DONE (conservative)

- **Status:** `src/clipper/smartcrop.py` — YuNet (OpenCV DNN, CPU, auto-download ~230KB to `work/.yunet.onnx` gitignored) samples 8 frames per clip, area-weighted median of all face detections. Conservative: stays center unless detections agree off-center (margin 0.12, 70% agreement). Falls back to center on any failure. Opt-in via `clips.smart_crop` (default false).
- **Verified live:** on channel episode, detector found speaker center (area 1.5%) + PiP inset (0.6%) — area weighting correctly stayed center (x=0.50, cx=437), frame confirmed speaker framed. First naive median version cropped to the inset and was fixed.
- **Known limit:** single static crop per clip — multi-cut windows with the speaker in different positions pick the dominant one. Per-segment tracking deferred.

## R-04 Loudness normalization + silence trim — P1 / M ✅ DONE

- **Status:** `make_clip` applies `-af silenceremove + loudnorm=I=-16:TP=-1.5:LRA=11` when `clips.loudnorm` / `clips.trim_silence` are true (both default false). Verified live: source -19.6 LUFS → output -16.4 LUFS.
- **Acceptance:** output measures ≈-16 LUFS ±1; flags independently toggleable in `settings.yaml`.

## R-05 Titles, thumbnails, hashtags — P1 / M ✅ DONE

- **Status:** prompt extended (no extra LLM cost), `rank()` passes title(≤60)/description/thumbnail_s through, `cut_clips` writes `clipN.meta.json` + `clipN.thumb.jpg`. Verified: meta+thumb live on channel source; rank new-fields contract verified via direct model call + 32 tests. **Live rank re-verified (2026-09-24):** `cli.py rank work/channel/transcript.json` → 20 candidates scored, valid JSON, model `ollama/gpt-oss:120b`, 8745 tokens. Dead `bai-auto/glm-5.3-flash` (now `403 Deposit required`) replaced by `bai-auto/deepseek-v4-flash` in the fallback chain.
- **Also fixed:** `rank_meta` sidecar clobbered any custom `--out` name (same content replaced ranked output). Now writes `<out>.meta.json` unless name contains `ranked.json`.

## R-06 SRT/VTT export alongside ASS — P1 / S ✅ DONE

- **Status:** `write_srt` / `write_vtt` in `caption.py` share `timed_lines()` with ASS so timings match exactly. `cut_clips` writes all sidecars per `clips.sidecars` (default all three). Verified live on `output/channel/`.
- **Acceptance:** `clipN.srt` + `clipN.vtt` next to every ASS; timings identical by construction (single source).

## R-07 TikTok / Reels presets — P2 / M ✅ DONE

- **Status:** `config/presets/{shorts,tiktok,reels}.yaml` + `--preset` on `process`/`clip`/`batch` (+ per-source `preset:` key). Overrides `clips.width/height/crf/x264_preset` and caption `margin_v`/`size_scale`. Verified live: all three render 1080x1920; tiktok margin 650 + size 76 (0.9x) vs default 420/84; `--preset bogus` errors with valid names.
- **Acceptance:** default output geometry unchanged; TikTok captions clear of UI zone; unknown preset fails with hint.

## R-11 Wide-source fit layout — P1 / S ✅ DONE

- **Problem:** Ultra-wide multi-person sources (e.g. 1280x534, two speakers side by side) lost faces to the 9:16 center crop — a rendered clip had **0 faces** and elsewhere the speaker was jammed at the frame edge.
- **Proposal:** `clips.layout: auto|crop|fit`. `fit` scales the full frame to width over a blurred, darkened fill (never crops content); `auto` picks `fit` when source aspect ≥ `clips.fit_ratio` (default 2.0), else `crop`. `fit_blur_sigma` / `fit_brightness` tunable. `smart_crop` applies to `crop` only.
- **Verified live:** 1280x534 source auto-selected `fit`; rendered clip shows both speakers (faces at x=0.22 and 0.67, y≈0.44) where the old crop showed none; sharpness mid-band 647 vs blurred bands 0.4/2.3; captions still burn.

## R-12 Caption position (bottom default) — P1 / S ✅ DONE

- **Problem:** `hormozi`/`bold` sat `alignment: 5` (center) with `margin_v 420`; only the raw ASS alignment number was configurable, no readable position.
- **Proposal:** `position: top|center|bottom` → alignment `8|5|2`, precedence `override.alignment > override.position > style.position > style.alignment > 5`. All styles default `bottom`, `margin_v 240`; presets bottom with `shorts 200 / reels 380 / tiktok 520`.
- **Verified live:** rendered captions at y 1526–1676 (240 px from bottom), clear of the centered `fit` video band (y 735–1185).

## R-13 Full config surfacing — P1 / M ✅ DONE

- **Problem:** `/config` handled only 4 bot keys, unvalidated; `/help` listed no config; ~90% of knobs (pipeline settings, styles, presets) were invisible from Telegram.
- **Proposal:** shared `settings_schema.py` (17 curated settable keys, typed/range/enum + cross-field validation); CLI `--set section.key=value`; bot `/config` (grouped dump incl. schema + styles + presets), `/settings` (read-only), `/set` (writes settings.yaml), `/style`, `/preset`, and per-job `--layout/--smart-crop/--loudnorm`. Bot defaults stay in `work/bot_config.json`; pipeline settings read-only except the curated set.
- **Verified:** fake-bot run of all commands; invalid/read-only keys rejected; writes to an isolated settings copy left the real file untouched; 72 tests pass.

## R-14 Deterministic ranking + repeat-URL reuse — P1 / M ✅ DONE

- **Problem:** re-running the same video produced falling scores (92/88/85 → 82/78 → 72/72 on identical transcript+candidates, same model). `rank.py` sent no `temperature`/`seed`, so the LLM sampled differently every call; each repeat also used a fresh work dir, so `--resume` had no cache to reuse.
- **Proposal:** pin `nine_router.temperature: 0.0` + `seed: 42` (sent when set, recorded in `rank_meta.json`, exposed in SETTABLE → 19 keys). Re-queuing a URL now copies the prior `transcript/candidates/ranked/rank_meta` into the new work dir (bot `reuse_artifacts`); `/clip ... --fresh` forces a re-rank. Also wrapped `run_polling` in a NetworkError backoff-restart loop (was killing the bot on a transient `httpx.ReadError`).
- **Verified:** live dirs confirmed identical inputs but differing completion tokens (the nondeterminism); unit tests assert the request body carries temperature/seed and reuse/enqueue/`--fresh` behavior; 80 tests pass, ruff clean.

## R-15 Speaker-following crop (shot-aware) — P1 / M ✅ DONE

- **Problem:** For multi-person podcasts the hand-made clips jump the camera between speakers to catch reactions; our `crop`/`smart_crop` held one static x for the whole clip. On the reference episode (Pandji Pragiwaksono, 3840×1600 / 2.4:1) the audio is near-mono (L/R corr 0.998), so who-is-talking can't be read from panning; the source is a multicam edit alternating a centered closeup and a two-shot.
- **Proposal:** new `clipper/follow.py` — detect the source's cuts (`select='gt(scene,θ)'`, default 0.15), split the clip into shots, sample frames (`clips.follow_fps`, 2), track faces (reuse YuNet) and pick the largest / most mouth-active face per shot, then emit a **step-function crop-x** (`crop=…:'if(lt(t,…),x,…)':…`) so the render hard-jumps per shot. `clips.follow_speaker` forces `crop`; `--follow` on the bot; schema grows to 22 settable keys.
- **Verified:** on the source's 08:34–09:56 window the rendered clip's scene cuts land exactly on the detected shot boundaries (515/524/526.5/545.5/556.5/575.5/577 s), framing the active face near center. Sample at `output/_sample_follow/clip0.mp4`. 95 tests pass, ruff clean.

## R-16 Reaction-cut speaker switching within shots — P1 / M ✅ DONE

- **Problem:** R-15 only cut on the source's own camera changes, so during a long two-shot it held one speaker and could not cut to the listener on a reaction/laugh — the exact "catch the expression" move of the reference clips.
- **Proposal:** per source shot, cluster faces into 1–2 columns (1-D k-means) and build a per-sample mouth-activity timeline; pick the displayed track with hysteresis — switch only if the challenger beats the current track by **1.25× + floor** (`plan_switches`) and `clips.follow_min_dwell` (1.5 s) has elapsed, merging sub-0.6 s pieces. The first sample of each shot is dropped (its frame-diff spans the camera cut), and `plan_to_shots` snaps the first/last emitted shot to the true shot bounds. Activity is measured in a **landmark-centred mouth box** (YuNet mouth corners), not the whole lower face, so hand gestures don't read as speech.
- **Verified:** Pandji episode → 9 cuts; the first two-shot (rel 1.0–10.0 s) frames x=0.67, the speaker the mouth metric ranks 13.3 vs 3.8. Two bugs fixed after review: (a) the shot tail (523.5–524.0) used to fall to the *next* shot's crop, framing between the faces at t≈9.5 s and t≈42 s — now a face is centred there (x≈0.47); (b) the old lower-face ROI counted hand gestures. Volka English 16:9 two-shot → 9 cuts alternating x≈0.32/0.67, faces 0.41–0.61. Samples `output/_sample_follow/`, `output/_sample_follow_volka/`. 102 tests pass, ruff clean. SETTABLE now 23 keys.

## R-17 Per-source layout for caption/graphic-heavy video — P2 / S ✅ DONE

- **Problem:** Some sources carry their own burned-in captions/slides/centre images (Volka English: bottom-edge density ≈36 on every frame). A speaker crop cuts that content off, so the same policy can't suit every source.
- **Proposal:** `config/sources.yaml` entries accept `layout`, `follow_speaker`, and an `overrides` map; `batch()` merges them (source value wins) into the per-run overrides. Fit keeps the whole frame in a centred strip and prints that `follow_speaker` is ignored.
- **Verified:** Volka rendered with `layout: fit` keeps the full 16:9 frame as a centred 1080×609 strip (rows 655–1264) over the blurred fill, so its captions/graphics survive; sample `output/_sample_fit_volka/`. 103 tests pass, ruff clean.

## R-08 Cost / time tracking log — P1 / S ✅ DONE


- **Status:** implemented. `process()` appends one JSON line per run to `work/costs.jsonl` (ts, stage_s timings, groq audio_min, rank model+tokens via `rank_meta.json` sidecar so cached resumes keep tokens). `cli.py costs [--month YYYY-MM]` summarizes. USD rates default 0.0 (free tier / unknown gateway pricing) — tokens always logged.
- **Acceptance:** every full run appends exactly one line; `cli.py costs` reports runs/tokens/usd; zero extra API calls (usage parsed from existing rank response).

## R-09a Offline integration test — P1 / S ✅ DONE

- **Status:** `tests/test_pipeline.py` + `tests/fixtures/sample.mp4` (synthetic 70s AV). `test_process_offline_full` mocks download/transcribe/rank and asserts transcript → ranked → MP4+ASS+SRT+VTT+meta+thumb artifacts exist; `test_process_offline_prefilter_rank_path` covers the real prefilter→rank scoring path. Runs offline in ~6s.
- **Acceptance:** full suite green without network/gateway; fixture 1.3MB committed.

## R-09b Docker image — DEFERRED to ship/sell-ready

- **Problem:** Setup is manual (venv, env vars, gateway, system fonts). No reproducible deploy unit.
- **Proposal:** `Dockerfile` (python 3.12, ffmpeg+libass, deps, fonts) — the deploy unit from the ship-prep checklist. Keep system deps declared there, not in host setup notes.
- **Acceptance:** `docker build` succeeds; container runs `cli.py batch --resume` against a mounted `work/`.

## R-10 Telegram bot control + daily digest — P1 / L ✅ DONE (v1.1)

- **Status:** `bot/clipbot.py` implemented. Single-worker async queue around `cli.py process --resume`, live status edits. `/clip` (+bare-URL shorthand), `/status`, `/logs <job>`, `/retry <job>`, `/queue`, `/cancel`, `/sources list|add|rm`, `/digest` (metadata-only scoring), `/costs`, `/config`, `/help`, Retry inline button. Allowlist `TELEGRAM_ALLOWED_USER_ID`. Daily digest via asyncio 24h loop at `digest_time`.
- **v1.1 diagnostics:** every job writes full stdout+errors to `work/<job>/job.log`; failures are classified into human reasons (YouTube blocked, all rank models down, video unavailable, no candidates, transcode error, …); progress shows sub-stage detail (download %, segments, candidates, best score, clip N); completion posts a summary (pipeline vs wall time, rank model/tokens, fallback note, output path); `/logs` tails the log; `/retry` + button requeue from cache; orphaned running jobs marked failed on restart; queued jobs auto-resume on startup.
- **Deferred to v2:** preview-frame photo before video, MP4-vs-document size split, approval-before-delivery, YouTube auto-upload.

## R-18 Theme-aware + trending daily digest — P1 / M ✅ DONE

- **Problem:** the daily digest was stateless and title-only — it re-scored a channel's latest uploads every day with no memory and no awareness of what had already been clipped, so with no new uploads it repeated the same video. It also ignored the themes of the content that was actually clipped.
- **Proposal:** a two-tier, keyword-overlap recommender. A cached **theme profile** is built from every done job's top-ranked clips (`work/<job>/ranked.json`: title/hook/reason/description → unigrams+bigrams, EN+ID stopwords, TF·IDF). **Tier 1** scores each channel's latest uploads (title+description) by `digest_score` + theme affinity, excluding already-*clipped* videos and anything shown within `digest_cooldown_days`, then groups picks by the shared theme. **Tier 2** is an always-on **trending** section: a YouTube **upload-date-sorted search** (`&sp=CAI%3D`) seeded by the profile's phrases/high-frequency words surfaces recent long-form on-theme uploads, ranked by affinity + log(view_count), with a fallback to the newest match when nothing lands inside `digest_trending_window_days`. Shown picks are recorded in `work/digest_state.json`; the profile caches in `work/digest_profile.json`. 11 new bot-config keys, all validated via `/config`.
- **Verified live (2026-09-24):** profile from 3 clipped videos (labels `romawi/hidayah/quran/islam/ekonomi`); channel tier ranked `Ekonomi Islam - Part 2 | PUTBAL` #1 on theme affinity (`islam`/`ekonomi`/`ekonomi islam`) and grouped picks as `islam`/`live`; trending surfaced recent long-form matches (`ROMAWI VS YUNANI`, 20260827; `FTV Hidayah`, 20260825). Playlists filtered out of search. 116 tests pass, ruff clean.
- **Known limits:** keyword overlap only (no embeddings — the 9router gateway exposes none); trending is a view-sort/relevance proxy, not YouTube's official feed (its `/feed/trending` no longer extracts); results are region-dependent and scrape risk is real (the tier fails open).

## Deferred: web UI

Web queue UI is **deferred until ship/sell-ready**. R-10 covers phone control for personal use. A browser UI only makes sense with multi-user auth, billing, and hosted workers — see ship-prep checklist below.

## Ship-prep alignment

Principles to keep every R-item sell-compatible, so a future web UI / SaaS doesn't require a rewrite:

- [ ] **Stable core contract:** `process(url, settings, ...) -> dict{download, transcript, ranked, clips}` stays the single entry point. New frontends (CLI, bot, web) call it, never duplicate stage logic.
- [ ] **Versioned config:** add `config_version: 1` to `settings.yaml`; loader warns on mismatch. Preset/style schemas frozen per version.
- [ ] **Queue behind an interface:** bot queue (`enqueue/job_id/status` in `work/bot_queue.json`) designed so a web worker can share the same job records later.
- [ ] **Structured logging:** replace `print` with stage-timestamped logs (needed for R-08 billing + future per-user usage metering).
- [ ] **Cost ledger from day one:** R-08 `costs.jsonl` is the future billing source — keep per-run token/audio-second fields exact.
- [ ] **Auth boundary:** single-user allowlist (`TELEGRAM_ALLOWED_USER_ID`) now; keep user identity threaded through job records so multi-user auth slots in.
- [ ] **Docker as ship artifact:** R-09b Dockerfile is the deploy unit — keep system deps (ffmpeg, fonts, libass) declared there, not in host setup notes.
- [ ] **No secrets in repo:** env-var-only keys (`GROQ_API_KEY`, `NINE_ROUTER_API_KEY`) — already true, keep enforcing.

## Suggested order

1. ✅ R-02 + R-08 — done.
2. ✅ R-01 — done.
3. ✅ R-10 — done (v1).
4. ✅ R-06 + R-04 + R-07 — done.
5. ✅ R-05 — done (live rank re-verified 2026-09-24 after gateway recovery).
6. ✅ R-03 — done (conservative). R-09b Docker at ship time.
7. ✅ R-18 — theme-aware + trending daily digest (2026-09-24).
