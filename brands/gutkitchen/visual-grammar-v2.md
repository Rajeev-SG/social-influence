# GutKitchen visual grammar v2

This is the derived grammar from `brands/gutkitchen/references/library.json`. The grammar is an art-direction contract for Creative Engine v2, not a claim that any creator’s content was copied.

## Recurring patterns

1. **First-frame promise in under one second.** Show the finished meal and one hard number: `~40g PROTEIN` and `15g+ FIBRE`. The number is a hook, not a footnote.
2. **Food-first, ordinary kitchen evidence.** Use close 45-degree and top-down shots with normal bowls, packs, scales, hands, steam and imperfect edges. Avoid ad-like empty backgrounds.
3. **Fast build cadence.** Cut every 0.8–2.2 seconds while ingredients enter. Keep one thought per visual beat.
4. **Persistent numeric layer.** Keep a compact protein/fibre badge and a progressive fibre counter visible during the build. The counter should make the proposition obvious without requiring VO.
5. **Ingredient specificity.** Name weights and product roles (`235g drained cannellini`, `150g passata`, `50g spinach`, `100g lighter mozzarella`). Make the shopping basket feel reproducible.
6. **Mix of shot types.** Pair hero close-up, top-down ingredient laydown, action insert, pan/melt detail, label/data card and final save CTA. Do not repeat one still for multiple narrative beats.
7. **Native, slightly rough polish.** Use bright but natural light, short motion, texture, handheld energy and restrained graphic cards. Typography is bold, direct and readable in a safe region.
8. **Utility CTA.** End with `Save this for your next shop.` or `Save the 30g day.` Keep the CTA singular and content-led.

## Component map

- `HeroMeal` — finished bowl or pan close-up, tactile appetite appeal.
- `ProteinFibreBadge` — two numeric chips with `label estimate · check your pack`.
- `FibreCounter` — progressive 0–20g visual meter.
- `IngredientBuild` — sequential ingredient cards with active state.
- `BeforeAfterUpgrade` — ordinary meal before/after fibre upgrade.
- `ShoppingBasket` — supermarket list and save affordance.
- `EvidenceCard` — concise calculation/source note.
- `SaveCTA` — one content-specific call to action.

## Prohibited creative copy

Do not bake `AI-generated content`, `AIGC-assisted`, `AI food illustration` or implementation provenance into the creative/caption. Internal provenance remains in manifests and review metadata. The old baseline disclosure is preserved for historical comparison only.

## Reference use in generation

The manifest lists reference IDs per treatment. Each treatment intentionally borrows a different combination: A uses number + ingredient-build cadence; B uses calculator/counter + shopping utility; C uses tactile action inserts + editorial hierarchy. Reference screenshots/frames are retained under `brands/gutkitchen/references/frames/` for internal multimodal review and are not distributable candidate media.
