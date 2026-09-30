# Pizza-bean bowl — source snapshots (verified 2026-09-29)

Recipe target: one serving, around 40g protein and at least 15g fibre, normal UK supermarket ingredients.
Status: source verification + arithmetic only. The recipe was **not physically cooked or timed** in this task.

## Chosen grams (one serving)

| Ingredient | Chosen amount | Basis |
|---|---|---|
| Sainsbury's Cannellini Beans In Water | 235g drained (one 400g can, declared 235g drained weight) | as drained |
| Sainsbury's Lighter Mozzarella Cheese | 100g drained | as drained |
| Sainsbury's Passata | 150g | as sold |
| Sainsbury's Baby Leaf Spinach | 50g | as sold |

## Verified nutrient figures (per 100g, official Sainsbury's product tables)

**Sainsbury's Cannellini Beans In Water 400g (235g*)**
URL: https://www.sainsburys.co.uk/groceries/product/sainsburys-cannellini-beans-in-water-400g-235g
Accessed: 2026-09-29. Table heading: *Typical Values as Drained, 100g contains*.
- Fibre 6.4g per 100g drained
- Protein 7.5g per 100g drained
- No raw/dry-bean figure is used; all bean maths is on drained weight.

**Sainsbury's Lighter Mozzarella Cheese 125g**
URL: https://www.sainsburys.co.uk/groceries/product/sainsburys-lighter-mozzarella-cheese-125g
Accessed: 2026-09-29. Table heading: *Typical Values as drained, per 100g*.
- Fibre <0.5g per 100g
- Protein 18.9g per 100g

**Sainsbury's Passata 500g**
URL: https://www.sainsburys.co.uk/groceries/product/sainsburys-passata-500g
Accessed: 2026-09-29. Table heading: *Typical values, Per 100g* (as sold).
- Fibre <0.5g per 100g
- Protein 1.5g per 100g

**Sainsbury's Baby Leaf Spinach 200g**
URL: https://www.sainsburys.co.uk/groceries/product/sainsburys-baby-leaf-spinach-200g
Accessed: 2026-09-29. Table heading: *Typical values, 100g contains* (as sold).
- Fibre 1.3g per 100g
- Protein 2.5g per 100g

## Tesco candidate check

Tesco Cannellini Beans Water 400G, product 262489348:
https://www.tesco.com/shop/en-GB/products/262489348
Attempted 2026-09-29 via SearXNG google cse + mojeek, `web_url_read`, and a Chrome-UA `curl`. Tesco UK returned HTTP 403 (bot detection); the Tesco IE equivalent also returned HTTP 403. The starting values (5.8g fibre, 5.9g protein per 100g drained) therefore could **not** be verified from Tesco's official table and are not used. The verified Sainsbury's own-brand table above is the calculation basis.

## Arithmetic (Decimal, one serving)

| Ingredient | Protein | Fibre (upper) |
|---|---|---|
| 235g beans | 17.625 | 15.040 |
| 100g lighter mozzarella | 18.900 | 0.500 (<0.5) |
| 150g passata | 2.250 | 0.750 (<0.5) |
| 50g spinach | 1.250 | 0.650 |
| **Total** | **40.025g** | **16.940g** |

- Protein: 40.025g exact (no "less than" values in the protein column).
- Fibre upper bound: 16.94g (each "<0.5g per 100g" counted as 0.5g).
- Fibre lower bound: 15.69g (each "<0.5g per 100g" counted as 0g).
- Conservative claim: "around 40g protein and at least 15g fibre per serving."

## Suggested method (untested)

1. Drain and rinse one 400g can of cannellini beans; about 235g beans.
2. Warm 150g passata in a pan, add the beans and 50g baby spinach, stir until the spinach wilts.
3. Tear or grate 100g lighter mozzarella over the top, cover briefly or grill until melted.
4. Season and serve as one portion.

No measured cooking time is claimed. The only time references are the retailer's own pack/can guidance; this method is a reasonable suggestion and was not cooked or tasted during this task.

## QA notes

- Health claims: none. No gut/microbiome/detox/IBS/IBD/disease claims. Jurisdiction: United Kingdom (England).
- Physical cooking test: not applicable — this task is source verification and arithmetic, so no sensory, timing or yield result is claimed.
- Label currency: product nutrient tables can change; always read the pack bought. Figures captured 2026-09-29.
