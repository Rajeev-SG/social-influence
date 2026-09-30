# Creative Engine v2 — reference-led GutKitchen quality milestone

This milestone improves content quality only. It does not automate discovery, publishing, selling, measurement or decisioning.

## Review artifact

Open `reviews/gutkitchen-creative-v2/index.html` locally in a browser. It shows the existing GutKitchen pilot beside three materially different Creative Engine v2 treatments from the same pizza-bean bowl brief:

- **NEW A** — Quantified Recipe Build
- **NEW B** — Fibre Calculator / Counter
- **NEW C** — Tactile Editorial Food-Build

The page includes playable baseline preview, first frames, treatment rationale, reference inputs, asset/design stacks, duration, QA status and known compromises.

## Pipeline

`social_influence/creative_engine_v2` separates:

1. **Stage A — creative direction:** 15 angles, hook tournament, ranking and selected lanes.
2. **Stage B — reference interpretation:** `brands/gutkitchen/references/library.json` plus `brands/gutkitchen/visual-grammar-v2.md`; reference IDs are attached to each treatment and analysis frames are retained separately.
3. **Stage C — asset routing:** each shot has a provider slot and route (`stock`, `image-to-video`, `text-to-video` or `code-generated`). Brand logic does not hard-code one provider.
4. **Stage D — deterministic design:** reusable SVG/HTML-style components: `HeroMeal`, `ProteinFibreBadge`, `FibreCounter`, `IngredientBuild`, `BeforeAfterUpgrade`, `ShoppingBasket`, `EvidenceCard`, `SaveCTA`.
5. **Stage E — candidate generation:** explicit manifests, ten approved-plate storyboard stills and playable storyboard motion comps for each treatment.
6. **Stage F — QA:** existing fact/evidence/technical checks remain separate from creative selection.

## Regenerate another candidate set

1. Keep the same `brief_id` for a fair comparison, or add a new brief and source record.
2. Update `brands/gutkitchen/creative-engine-v2/manifest.json`: angles, selected treatments, storyboard shots, asset routes and QA basis.
3. Update `brands/gutkitchen/references/library.json` and `visual-grammar-v2.md` when the reference territory changes.
4. Run `python3 scripts/render-creative-v2.py
python3 scripts/render_creative_v2_video.py  # local FFmpeg; review comps are committed`.
5. Open `reviews/gutkitchen-creative-v2/index.html` and compare the storyboard comps, first frames and treatment stills. Do not treat the comparison as final visual-quality validation.
6. Do not publish candidates. Keep provider/model/prompt provenance in manifests, never as redundant on-frame AI branding.

## Verification

Run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_packs.py
python3 scripts/validate_evidence.py
python3 scripts/render-creative-v2.py
python3 scripts/render_creative_v2_video.py  # local FFmpeg; review comps are committed
```

The current run passes the factual basis from the existing pilot: 40.025g protein and a 15.69g fibre lower bound per bowl. The approved-plate storyboard candidates and silent storyboard motion comps are review artifacts, not published media. The comps use deterministic camera motion and no VO/music mix; provider slots can replace each shot with native/generated footage later. Real/native footage remains preferable before public publishing where appetite realism is the objective.

## Regeneration date rule

A new candidate set requires a new dated evidence directory such as `docs/evidence/<YYYY-MM-DD>/creative-engine-v2/`. Keep the previous dated directory and hash manifest intact. `manifest.json`’s `generated_at` and the evidence directory date must match and must not be in the future.
