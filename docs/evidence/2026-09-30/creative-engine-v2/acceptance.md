# Acceptance: GutKitchen Creative Engine v2 quality milestone

Date: 2026-09-30
Issue: Rajeev-SG/social-influence#8

## Result

PASS for the requested review-only creative-quality milestone. The reviewer can open one static page and compare the existing GutKitchen pilot with three materially different Creative Engine v2 treatments from the same pizza-bean bowl brief.

Review page: `reviews/gutkitchen-creative-v2/index.html`

## Baseline diagnosis

The existing pilot is technically and factually clean, but creatively weak because:

- six source clips become repeated hero/ingredient/pan stills rather than varied narrative shots;
- several beats hold the same composition for too long;
- the overlay/card system dominates the food and feels closer to a presentation than native short-form content;
- pacing, camera movement and tactile action do not visibly improve after the first second;
- technical QA success is not evidence of appetite appeal or creative quality.

The old content remains in the comparison as the baseline.

## Reference-led work

- `brands/gutkitchen/references/library.json` records 12 reference patterns and exact high-performing public examples where counts were available.
- `brands/gutkitchen/visual-grammar-v2.md` derives the recurring first-frame, pacing, typography, ingredient, motion, caption and CTA grammar.
- Internal analysis frames are kept under `brands/gutkitchen/references/frames/`, separate from candidate media.
- Local SearXNG searches timed out; Brave Search was used as the documented escalation route.

## Creative Engine v2

`social_influence/creative_engine_v2` implements explicit stages:

1. creative direction with 15 angles and a hook tournament;
2. reference-led art direction;
3. per-shot asset routing with replaceable provider slots;
4. deterministic composition components;
5. three materially different candidate treatments;
6. factual/evidence/technical QA separate from creative selection.

Candidates:

- NEW A — Quantified Recipe Build, 31.2s, 10 cuts.
- NEW B — Fibre Calculator / Counter, 29.8s, 10 cuts.
- NEW C — Tactile Editorial Food-Build, 32.5s, 10 cuts.

All preserve the existing factual basis: 40.025g protein and a 15.69g fibre lower bound per bowl from validated product-label calculations. No candidate is published.

## Verification performed

- `python3 -m unittest discover -s tests -v` — 31 tests pass.
- `python3 scripts/validate_packs.py` — both production packs and tracked source/media inputs pass.
- `python3 scripts/validate_evidence.py` — prior evidence manifests pass; this run's artifact manifest is included.
- `python3 scripts/render-creative-v2.py` — regenerates 30 photo-led stills and review payloads.
- `python3 scripts/render_creative_v2_video.py` — regenerates three review MP4s at 1080x1920, 30fps.
- Playwright at `https://gutkitchen-review.localhost:1355/reviews/gutkitchen-creative-v2/index.html`:
  - OLD and NEW A/B/C video elements reach `readyState=4`;
  - durations are 9.0s, 31.2s, 29.8s and 32.5s;
  - desktop 1440px and mobile 390px layouts have no horizontal overflow;
  - browser console is clean;
  - all page-relative media and documentation links resolve.
- Rendered screenshots: `review-desktop.png`, `review-mobile.png`.

## Known compromises

- The review comps use the existing approved GutKitchen food plates with deterministic camera motion and per-shot provider slots. Native/generated footage can replace individual shots without changing brand logic.
- The comps are silent review renders; VO, music and caption-sync timing are not part of these candidate previews.
- The recipe remains label-estimated and was not physically cooked or tested. The review page preserves that claim boundary.
- Human creative selection is intentionally still open: the milestone proves the comparison and system, not which treatment wins.

## Reviewer decision

Choose which treatment should become the new GutKitchen baseline by judging first-second impact, appetite realism, shot diversity, pacing, information hierarchy, brand consistency and saveability.
