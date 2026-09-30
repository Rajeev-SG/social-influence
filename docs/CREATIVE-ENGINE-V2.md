# Creative Engine v2 — finished OpenRouter media milestone

Creative Engine v2 is now an executed media experiment, not only a storyboard system. This milestone does not automate discovery, publishing, selling, measurement or decisioning. Nothing is published automatically.

## Review artifact

Open `reviews/gutkitchen-creative-v2/index.html` locally, or use the Portless URL `https://gutkitchen-review.localhost:1355/reviews/gutkitchen-creative-v2/index.html` while the static server is running.

The page compares five artifacts from the same pizza-bean bowl brief:

| Artifact | Role | Duration | Status |
|---|---|---:|---|
| OLD BASELINE | Issue #2 pilot | 31.15s | reference |
| CURRENT V2 STORYBOARD | best Issue #8 motion comp | 32.5s | reference, storyboard only |
| NEW A — I2V | generated keyframes to image-to-video action | 8.1s | final media |
| NEW B — T2V | mostly direct text-to-video cooking action | 8.1s | final media |
| NEW C — HYBRID | best available source route per shot | 8.1s | final media |

Each final candidate has a playable 9:16 preview, poster/first frame, six-shot filmstrip, model IDs, route per shot, reference inputs, selected-source cost, QA state, known weaknesses, winner control and local notes. Winner selection and notes persist in `localStorage`.

## What was executed

The reusable client is `social_influence/openrouter_media.py`. It uses only `OPENROUTER_API_KEY` and the dedicated OpenRouter APIs:

- image discovery: `GET /api/v1/images/models`
- image generation/editing: `POST /api/v1/images`
- video discovery: `GET /api/v1/videos/models`
- video generation: `POST /api/v1/videos`
- video polling: `GET /api/v1/videos/{jobId}`
- video download: `GET /api/v1/videos/{jobId}/content`
- multimodal creative direction: `POST /api/v1/chat/completions`

The configuration is `brands/gutkitchen/creative-engine-v2/openrouter-media-plan.json`; model IDs are not hard-coded in GutKitchen-specific logic. The run ledger is `brands/gutkitchen/creative-engine-v2/openrouter-run/provenance/generations.json` and records prompt, redacted input-reference hashes, request parameters, output hash, job ID where recovered, elapsed time, usage/cost where available and failures/recovery notes.

### Exact models used

- creative direction: `openai/gpt-5.6-sol`
- image generation: `openai/gpt-image-2.5-sunburst`
- image iteration: `openai/gpt-image-2.5-flare`
- image-to-video: `bytedance/seedance-2.5`, `minimax/hailuo-3-max`, `alibaba/wan-3.0`
- text-to-video: `alibaba/wan-3.0`, `bytedance/seedance-2.5`, `minimax/hailuo-3`

`anthropic/claude-fable-5.1` was discovered and configured as an optional review model but was not needed for the executed core media routes.

## Reference conditioning

Nine real frames were captured from three strongest TikTok references at first/middle/action positions. The frames were passed to `openai/gpt-5.6-sol` for framing, information density, shot rhythm, food placement, typography hierarchy, overlay positioning, camera-style and transition analysis.

The captures are ephemeral and not committed. `openrouter-run/reference-inputs.json` retains source URLs, frame hashes and an explicit `ephemeral-not-committed` retention policy. No creator-owned frame is shipped with generated output or stored in `brands/gutkitchen/references/`.

## Candidate routes

- **NEW A — I2V:** generated food keyframes were animated with OpenRouter image-to-video models. The selected shots contain spoon/cheese pull, bean drop, passata/spinach action, simmer, melt and final spoon payoff.
- **NEW B — T2V:** five selected shots are direct OpenRouter text-to-video actions. `t2v/beans-pan` hit the account credit limit before its response was recovered, so this T2V-heavy candidate documents one I2V bean-drop fallback.
- **NEW C — HYBRID:** the strongest available source is selected per shot. It mixes I2V and T2V without using zoompan stills for an acceptance-critical action shot.

Every acceptance-critical final shot is `executed-provider`; `plannedCriticalRoutes` is zero in `candidates/final-media/final-media-manifest.json`.

## Deterministic layer

`scripts/render_creative_v2_media.py` assembles the final 8.1-second cuts with local deterministic tooling:

- 1080x1920, 30fps output
- six action cuts around 1.2–1.5 seconds each
- crisp protein/fibre hook, captions, ingredient quantities, caveat and animated fibre progress bar
- concise local VO and restrained kitchen texture audio
- first frame and shot filmstrip per candidate

Typography and factual overlays are not generated inside image/video models.

## Cost and recovery

- exact OpenRouter usage reported in retained records: **$0.498473**
- model-pricing estimate for recovered video responses: **$2.20**
- combined working estimate: **$2.70**

The first runner downloaded 13 of 16 planned video outputs before OpenRouter returned `402 Insufficient credits`. The runner was changed to preserve existing output hashes and fail soft. Some recovered clips retain model/route/hash and model-level cost estimates but not their original job IDs or exact response costs. This limitation is recorded in the run summary and each affected candidate.

## Creative assessment

**Best-performing candidate: NEW C — HYBRID.** It has the strongest first-second cheese pull, clear bean drop and sauce/spinach action, fast simmer/melt beats and a convincing final spoon payoff. It is the candidate Rajeev could reasonably choose to publish after confirming the label-based protein wording and checking the final food continuity in motion.

Remaining weaknesses:

- model-to-model food continuity changes slightly across cuts;
- one T2V bean job was replaced by an I2V fallback in NEW B;
- exact job IDs/costs for some recovered clips are unavailable after the credit-limit exception;
- the recipe remains label-estimated and is not documentation of a physically tested cook.

## Rerun with different models

1. Source the approved key: `source ~/.config/claude-openrouter/env.sh`.
2. Edit model IDs and shot prompts in `brands/gutkitchen/creative-engine-v2/openrouter-media-plan.json`.
3. Capture first/middle/action frames into a temporary directory such as `/tmp/gutkitchen-ref-captures`. Do not commit third-party frames.
4. Run `python3 scripts/generate_creative_v2_media.py --reference-dir /tmp/gutkitchen-ref-captures --workers 4`.
5. Run `python3 scripts/render_creative_v2_media.py`.
6. Run `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_creative_v2.py`.

The generation runner discovers current capabilities before requests and resumes completed output hashes instead of re-billing them.

## Verification

The current evidence bundle is `docs/evidence/2026-09-30/creative-engine-v2/`. It includes full-page desktop/mobile review captures, commands, timing and hash manifests. Validation covers:

- factual basis and existing Creative Engine projections
- actual video dimensions, duration, audio and measured motion delta
- per-shot OpenRouter provenance hashes
- zero planned critical routes
- five-card HTML comparison and real media sources
- winner/note persistence and no horizontal overflow through Playwright

Do not publish candidates automatically. A future candidate set requires a new dated evidence directory and a new model/prompt run ledger.
