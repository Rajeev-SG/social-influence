# Creation-engine benchmark (Issue #2 sidecar)

Scope: compare creation-engine candidates for social-influence Issue #2 using the
same first brief, and record what was actually executed versus what was blocked.
This document does not select a final engine; it produces an actionable shortlist
for the parent's orchestration work.

## Test brief (identical for every candidate)

GutKitchen first queue item: **"40g protein + 15g fibre pizza-bean bowl using
supermarket ingredients."** Required output contract:

1. Exact meal shown, not generic food b-roll.
2. Validated nutrient arithmetic (protein, fibre) that the visuals agree with.
3. Real food footage (ordinary supermarket ingredients, non-advertising aesthetic).
4. Moving nutrient badges driven by that arithmetic.
5. Native 9:16, 20–45 seconds, voiceover + burned captions.
6. Fail-closed QA (no render accepted without validation passing).
7. Export metadata and asset rights recorded.
8. **No publishing.**

Secondary fit check: a real desktop screen-recording demo for the
AIForAccountants brand (`INPUT → AI STEP → HUMAN CHECK` overlay, no avatar).

## Pinned revisions

Benchmarked 2026-09-29 by shallow clone into `/tmp/si-benchmark`.

| Candidate | Repo | Pinned SHA | License | Stack |
|---|---|---|---|---|
| MoneyPrinterTurbo | `harry0703/MoneyPrinterTurbo` | `d47783266cfad72663c8bf84b59694a9034450b0` | MIT | Python 3.11, FastAPI 0.136.3, moviepy 2.2.1, litellm/openai, edge-tts |
| short-video-maker | `gyoridavid/short-video-maker` | `9bb9a212ced86caa7e09099c382da1a44d638760` (v1.3.4) | MIT | Node/TS, Remotion 4.0.286, kokoro-js, whisper.cpp, Pexels |
| OpenNolan | `het8802/OpenNolan` | `4457349c386ea1a89c01547f9a76fa650970c131` (v1.0.2) | **AGPL-3.0** | Python + FastAPI, Remotion composer, Node, FFmpeg, optional Claude Agent SDK |
| OpenShorts | `mutonby/openshorts` | `29c54fa04c42621310f768adf40c81a1f3436bf2` | MIT | Python + FastAPI, torch/ultralytics/mediapipe, faster-whisper, google-genai, Docker |
| Content Machine (parent-owned) | local `CONTENT_MACHINE_DIR` checkout | `46cfe459d9ffbf40f847399e3f88c7c380074e7b` | MIT | `@45ck/content-machine` 0.2.2, `generate-short` skill |

Repo-resolution notes:

- The issue's "MoneyPrinterTurbo" has no owner given; `harvesthq/MoneyPrinterTurbo`
  does not exist (`remote: Repository not found`). The canonical repo is
  `harry0703/MoneyPrinterTurbo`.
- "OpenShorts" has several namesakes. `mutonby/openshorts` (5,794 stars, topics
  include `mcp-server`, `ugc-platform`, `clip-generator`) is the one matching the
  issue description ("AI UGC actors + clipping + MCP/API + direct publishing").
  Rejected matches: `gameplayxx111/openshorts` (10 stars), `faris-sait/openshorts`
  (clip-only), `jnMetaCode/openshorts` (local-first pipeline, unrelated lineage).

## Environment observed

- `python3` 3.14.7, `node` v26.7.0, `uv`, `pnpm`, `npm`, `docker` present.
- `ffmpeg` 8.1 and `ffprobe` at `/opt/homebrew/bin` fail on the default library
  path (`dyld: Library not loaded: /opt/homebrew/opt/x265/lib/libx265.215.dylib`)
  but work with a **process-local, non-modifying** fallback:
  ```bash
  export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/Cellar/x265/4.1/lib
  ffmpeg -version   # ffmpeg version 8.1
  ffprobe -version  # ffprobe version 8.1
  ```
  No `brew` change, symlink, or system modification was made. Both binaries are
  usable, so FFmpeg is **not** a blocker.
- System Python lacks `fastapi`, `moviepy`, `loguru`.

Consequence: FFmpeg-dependent work is viable. One real assembly was run (see
below); other render claims remain capability inspection and are marked as such.

## Commands actually run and observed results

### 1. Static integrity (all four)

```bash
cd /tmp/si-benchmark/<repo> && python3 -m compileall -q .
```

| Repo | Result |
|---|---|
| MoneyPrinterTurbo | exit 0, no output |
| OpenNolan | exit 0, no output |
| OpenShorts | exit 0, two `SyntaxWarning: 'return' in a 'finally' block` at `app.py:1634` and `app.py:1641` |

### 2. Executable CLI surfaces (no credentials, no downloads)

```bash
python3 OpenShorts/cli/openshorts_cli.py --help
python3 OpenNolan/render_demo.py --help
python3 OpenNolan/render_demo.py --list
python3 MoneyPrinterTurbo/cli.py --help
```

| Command | Observed |
|---|---|
| OpenShorts CLI `--help` | Works. Subcommands: `process`, `status`, `clips`, `quota`, `publish`. `publish` calls `POST /api/social/post` (Upload-Post) — must stay unwired for the no-publishing rule. |
| OpenNolan `render_demo.py --help` | Works. "Render zero-key OpenNolan demo videos from checked-in Remotion props." |
| OpenNolan `render_demo.py --list` | Fails: `Error: No demo prop files were found in .../remotion-composer/public/demo-props`. Zero-key demo path is not actually populated at this SHA. |
| MPT `cli.py --help` | First run failed with `ModuleNotFoundError: No module named 'loguru'`. After `python3 -m venv` + `pip install loguru pydantic-settings` only, help ran and exposed `--video-source {pexels,pixabay,coverr,wavespeed,volcengine_seedance,ofox,metaso_minimax,muapi,openai_image,local}`, `--video-aspect {9:16,16:9,1:1}`, `--video-fit-mode {cover,contain}`, `--stop-at {script,terms,audio,subtitle,materials,video}`, and `--confirm-wavespeed-charge` / `--confirm-seedance-charge` / `--confirm-ofox-charge` / `--confirm-metaso-minimax-charge` / `--confirm-muapi-charge`. |

The `--confirm-*-charge` flags are the strongest safety signal in the whole
benchmark: MPT makes paid/generative providers opt-in per run. No paid provider
was invoked.

### 3. Integration surfaces (source inspection)

- **MoneyPrinterTurbo** — FastAPI `POST /api/v1/videos` (task response),
  `POST /api/v1/subtitle`; `app/services/video.py:generate_video`; schema exposes
  `video_aspect` (default portrait), `video_clip_duration` (1–15 s),
  `paragraph_number` (1–10), `video_fit_mode`, transition modes.
  `app/services/llm.py` has `generate_script`, `generate_terms`,
  `generate_social_metadata`.
- **short-video-maker** — REST `POST /api/short-video`,
  `GET /api/short-video/:videoId/status`, `GET /api/short-videos`, `GET /voices`,
  `DELETE`/listing routes; MCP tools `create-short-video` and `get-video-status`;
  MCP over SSE at `/sse` + `/messages`. `rest.http` example uses port 3123.
  `types/shorts.ts` has `orientation: landscape | portrait` (default portrait);
  tests use 1080×1920.
- **OpenNolan** — FastAPI backend (`:8000`) + React/Vite (`:5173`) via `./run-dev`;
  `lib/media_profiles.py` defines `PORTRAIT_9_16` at 1080×1920; `config.yaml`
  `default_resolution` is `1920x1080`, so portrait must be selected explicitly.
  Pipelines include `instagram-reels-studio.yaml`, `screen-demo.yaml`,
  `talking-head-screen-demo-reel.yaml`, `product-demo.yaml`, `clip-factory.yaml`.
  In-app chat panel needs the Claude Agent SDK (`CLAUDE_CODE_OAUTH_TOKEN` or
  `ANTHROPIC_API_KEY`); pipelines/editor/render do not.
- **OpenShorts** — FastAPI + `/mcp` (also stdio `mcp_stdio.py`); tools
  `process_video`, `create_upload`, `get_job_status`, `list_clips`, `get_quota`,
  `add_subtitles`, `recut_clip`, `publish_clip`. `clip_selection.py` bounds clips
  to 15–60 s. Layout modes include `SCREENCAST_LAYOUT` (`app.py:2643`), so a
  desktop recording could be clipped. AI Shorts is avatar/UGC-driven and paid
  (~$0.65 low-cost, ~$2 premium per the README) — not run.

### 4. Real assembly smoke test — MoneyPrinterTurbo, local materials

This is a **technical-only** smoke test of the assembly path. It is not a
GutKitchen post, and its output is **not** an acceptable brand deliverable: no real
food, no validated nutrient arithmetic, no nutrient badges, no voice. It exists
only to prove the render path works end to end.

Fixture (synthetic test pattern, no third-party media, made in scratch):

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/Cellar/x265/4.1/lib
ffmpeg -v error -y -f lavfi -i "testsrc=size=1080x1920:rate=30:duration=6" \
  -f lavfi -i "sine=frequency=440:duration=6" \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest fixture.mp4
# -> h264, 1080x1920, aac, duration 6.000000, 176K
```

Run (no API keys, no LLM, no model download, no paid provider):

```bash
cd /tmp/si-benchmark/MoneyPrinterTurbo
/tmp/si-benchmark/venv-mpt/bin/python cli.py \
  --video-script "Technical smoke test footage assembly only." \
  --video-source local --video-materials /tmp/si-benchmark/fixture.mp4 \
  --video-language en-US --video-aspect 9:16 --video-count 2 \
  --video-clip-duration 5 --voice-name no-voice --subtitle-enabled \
  --bgm-type none --n-threads 2 --stop-at video
```

Observed result: **exit 0**, MPT v1.3.7, task
`dfc4f6e0-464e-4bd2-8f27-e910f86a8f49` in `storage/tasks/`, generating 2 videos
plus SRT and combined clips (~9 s wall clock in this environment). ffprobe on the
outputs:

- `final-1.mp4` and `final-2.mp4`: h264 + aac, **1080×1920**, 44.1 kHz audio,
  **3.03 s**, 108,207 bytes each.
- `subtitle.srt` written and burned in
  (`00:00:00,000 --> 00:00:03,000`).

Notes: the SRT text came from the supplied script, so **no Whisper model was
downloaded**. `pip` installed `moviepy`, `edge_tts`, `pydub`, `openai` and small
support deps into a scratch venv only; nothing was installed system-wide and no
`config.toml` outside the scratch clone was touched. Two output videos for one
different request were identical because with a single source material MPT
reused it (`warnings: batch_materials_reused`) — a real limitation to note, not a
defect of the smoke test. A 3.03 s output also shows MPT derives length from the
audio track, so it did not satisfy the 20–45 s contract here; that was not the
goal of this test.

## Fit against the GutKitchen contract

| Requirement | MPT | SVM | OpenNolan | OpenShorts |
|---|---|---|---|---|
| Exact meal (not generic b-roll) | ✗ generic stock search | ✗ generic Pexels | ✗ stock/generated footage | ✗ clips an existing source video |
| Validated nutrient arithmetic | ✗ | ✗ | ✗ | ✗ |
| Real food footage | △ stock (Pexels/Pixabay/Coverr) or `local` materials | △ Pexels | △ stock/generated | △ only if you supply real footage |
| Moving nutrient badges from arithmetic | △ subtitles/text only | △ captions only | ✓ motion graphics/overlay engine | △ hook text overlays |
| Native 9:16 | ✓ 1080×1920 | ✓ 1080×1920 portrait default | ✓ portrait profile (explicit) | ✓ vertical crop |
| 20–45 s | △ length from `paragraph_number`, clip 1–15 s | △ scene-count driven | △ pipeline driven | △ clip bounds 15–60 s; 20–45 s is inside that range, but a 20 s floor must be enforced |
| Voice + burned captions | ✓ edge-tts + subtitles | ✓ Kokoro + Whisper | ✓ TTS + word-level captions | ✓ ElevenLabs + faster-whisper |
| Fail-closed QA | ✗ | ✗ | △ multi-point self-review (README claim) | ✗ |
| Export metadata/rights | △ `generate_social_metadata` | ✗ | △ render artifacts | △ YouTube Studio metadata |
| No publishing (Postiz-only) | ✓ no publish path | ✓ no publish path | ✓ no publish path | △ ships `publish_clip`/Upload-Post, but publishing is opt-in: not calling the endpoint keeps the no-publishing rule |
| Licence risk | MIT | MIT | **AGPL-3.0** | MIT |
| Maintenance signal | active 2026 | last commit 2025-06-21 (stale) | active 2026 | active 2026 |

Key finding: **none of the four candidates satisfies the GutKitchen contract on
its own.** Every one of them assumes the script and facts arrive from an LLM and
none of them computes or verifies nutrient arithmetic. Requirements 1, 2 and 4
(exact meal, validated arithmetic, badges bound to that arithmetic) must be
satisfied upstream — by Content Machine plus a deterministic nutrition
calculator that emits a machine-readable nutrient manifest — and then passed
into the chosen renderer as authoritative values the renderer may not recompute.

## Fit for the accountant desktop demo

| Candidate | Fit |
|---|---|
| OpenNolan | Strongest structural match. `screen-demo.yaml` and `talking-head-screen-demo-reel.yaml` are purpose-built for screen recordings + overlays, and the overlay engine has the primitives for `INPUT → AI STEP → HUMAN CHECK` and `REVIEW REQUIRED` callouts. Not render-verified here. |
| OpenShorts | Plausible. `SCREENCAST_LAYOUT` exists and clipping long screen recordings is its core job, but the AI Shorts lane is avatar-led, which the brand profile forbids ("fake AI accountant/CPA persona"). |
| MoneyPrinterTurbo | Weak. `--video-materials ... --video-source local` can ingest a supplied recording, but there is no screen-focus or cursor/highlight treatment. |
| short-video-maker | Poor. No local-material ingestion path found; designed around stock background video. |

## Actionable shortlist

1. **Keep Content Machine `generate-short` as the orchestrator** (parent-owned,
   pinned `46cfe459`). It is the only candidate that already ties script, audio,
   timestamps, visuals, render metadata and validation into one artifact set
   (`visuals/visual-quality.json`, platform metadata + upload checklist).
2. **Add a deterministic nutrient-calculation step before rendering** and make
   the badges read from its output. No engine in this benchmark closes that gap.
3. **OpenNolan (AGPL-3.0) has the best-documented overlay/motion capability** for GutKitchen
   badge/motion-graphics scenes and for the accountant screen demo — subject to
   an explicit licence decision, because AGPL obligations attach if it is
   exposed as a network service. Do not adopt it before that decision.
4. **MoneyPrinterTurbo is the simplest MIT fallback for volume faceless b-roll**
   (`9:16` native, FastAPI task API, CLI, per-provider charge confirmation) but
   cannot show the exact GutKitchen meal or move arithmetic-driven badges.
5. **short-video-maker is the cleanest MCP/REST integration surface** (two MCP
   tools, MIT) but is the weakest on the food brief and its last commit is
   2025-06-21. Use only if a minimal MCP render endpoint is the priority.
6. **OpenShorts is a clip-repurposing tool, not a creator**, for this program.
   Revisit only once real long-form footage exists, and keep `publish_clip` /
   Upload-Post unwired so Postiz remains the single publishing path.

## Not run / blocked (do not read as failures)

- MPT LLM/script generation: needs an LLM key; not run. Provider-backed footage
  (Pexels etc.) was not run either — the smoke test used `--video-source local`.
- SVM generation: needs `PEXELS_API_KEY`; first run also downloads Whisper/Kokoro models (deliberately not done).
- OpenNolan render: zero-key demo props absent at this SHA; web app not booted. FFmpeg itself is now usable.
- OpenShorts generation: paid Gemini/ElevenLabs/fal.ai path and multi-GB torch/YOLO model downloads deliberately not run.
- Content Machine: **read only**. It was not run, installed, or modified, per the task constraint.
- No candidate run other than MPT was render-verified, and the one MPT run above
  was a technical assembly check, **not** brand-acceptable output. No quality
  ranking between engines is asserted; differences noted are structural.
