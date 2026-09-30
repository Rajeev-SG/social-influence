# Acceptance: GutKitchen Creative Engine v2 finished media

Date: 2026-09-30
Issue: Rajeev-SG/social-influence#10

## Result

PASS. Creative Engine v2 now produces three finished 8.1-second candidates from the same pizza-bean bowl brief, using OpenRouter image and video generation rather than storyboard stills. The static review compares:

1. OLD BASELINE
2. CURRENT V2 STORYBOARD
3. NEW A — I2V
4. NEW B — T2V
5. NEW C — HYBRID

The strongest agent-reviewed candidate is **NEW C — HYBRID**. Its first-second cheese pull, bean drop, passata/spinach action, simmer/melt beats and final spoon payoff are a genuine visual improvement over the Issue #8 motion comps. It is a reasonable publish candidate after Rajeev confirms the label-based wording and watches the full motion.

## OpenRouter execution

- One `OPENROUTER_API_KEY` covers creative direction, image generation and video generation.
- No provider-specific API integration was added.
- Live image/video model discovery is retained under `brands/gutkitchen/creative-engine-v2/openrouter-run/discovery/`.
- `openai/gpt-5.6-sol` consumed nine real reference-frame captures for multimodal art direction.
- `openai/gpt-image-2.5-sunburst` generated five keyframes; `openai/gpt-image-2.5-flare` generated two alternatives.
- Video routes tested `bytedance/seedance-2.5`, `minimax/hailuo-3-max`, `minimax/hailuo-3` and `alibaba/wan-3.0`.
- Every final shot is `executed-provider`; `plannedCriticalRoutes` is zero.

## Reference integrity

Three TikTok sources were captured at first/middle/action positions and fed to the multimodal creative-direction stage. The frames are ephemeral and not committed. `reference-inputs.json` stores source URLs and hashes. No third-party reference frame is included in generated output.

## Media and deterministic design

- NEW A uses generated keyframes plus I2V food/action motion.
- NEW B is T2V-heavy with five direct T2V shots and one documented I2V bean-shot fallback after the OpenRouter credit limit.
- NEW C uses the best available I2V/T2V source per shot.
- Core beats are real generated action: bean drop, passata pour, spinach drop, simmer/bubble, cheese melt and spoon/cheese pull.
- All candidates are 1080x1920, 30fps, 8.1s and contain VO plus deterministic kitchen texture audio.
- Protein/fibre claims, captions, quantities, fibre progress and caveat remain deterministic and model-independent.

## Cost

- exact reported OpenRouter usage retained: **$0.498473**
- model-pricing estimate for recovered video responses: **$2.20**
- combined working estimate: **$2.70**

The first runner downloaded 13 of 16 planned video outputs before a `402 Insufficient credits` response. Completed bytes and hashes were preserved; the runner was changed to fail soft and resume. Some recovered clips retain model-level estimates rather than exact job IDs/costs.

## Review UX verification

Playwright at `https://gutkitchen-review.localhost:1355/reviews/gutkitchen-creative-v2/index.html` verified:

- five cards and five playable video sources at `readyState=4`;
- all final videos report 8.1s and 1080x1920;
- no current console errors and no horizontal overflow on desktop/mobile;
- NEW C winner selection and review notes persist through reload;
- restart-all resets final videos; play-all runs them muted to completion;
- first frames, filmstrips, reference links and per-shot model routes are visible.

Evidence captures: `review-desktop.png`, `review-mobile.png`.

## Known compromises

- Food continuity changes slightly across models.
- One T2V bean job fell back to I2V in NEW B.
- Exact job IDs and response costs for some recovered clips were lost when the runner stopped on the credit limit.
- The recipe remains label-estimated and was not physically tested.

## Publication

No candidate was published. Winner selection remains local to the reviewer.
