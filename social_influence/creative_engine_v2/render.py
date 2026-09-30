"""Render deterministic SVG treatments and inspectable stills."""
from __future__ import annotations

from pathlib import Path
import json
from .components import *

def _base(bg: str, eyebrow: str, headline: str, detail: str) -> list[str]:
    return [svg_open(), rect(0, 0, W, H, bg), text(48, 78, eyebrow, 24, COLORS["tomato"], 800), text(48, 160, headline, 64, COLORS["ink"], 900), text(48, 216, detail, 28, COLORS["muted"], 600)]

def render_treatment(treatment_id: str, shot_index: int = 0) -> str:
    if treatment_id == "new-a":
        return render_a(shot_index)
    if treatment_id == "new-b":
        return render_b(shot_index)
    return render_c(shot_index)

def render_a(i: int) -> str:
    bg = COLORS["cream"]
    title = "THE 40g / 15g+ BOWL" if i == 0 else ["START WITH ONE TIN.", "ADD TOMATO + GREENS.", "THE PROTEIN FINISH.", "READ THE SMALL PRINT.", "SAVE THE SHOPPING LIST."][min(i-1,4)]
    out = _base(bg, "GUTKITCHEN  /  QUANTIFIED RECIPE BUILD", title, "normal supermarket ingredients · label estimate")
    out += [hero_meal(540, 760, 1.15, "bowl"), protein_fibre_badge(48, 330, "~40g", "15g+"), fibre_counter(48, 1230, [15.69, 15.04, 15.69, 15.69, 15.69, 15.69][min(i,5)]), ingredient_build(48, 1350, ["235g DRAINED CANNELLINI", "150g PASSATA + 50g SPINACH", "100g LIGHTER MOZZARELLA"], min(i-1,2) if i else -1), evidence_card(48, 1570, "THE MATH", "40.025g protein · 15.69g fibre lower bound"), common_footer("REAL NUMBERS. NORMAL INGREDIENTS."), '</svg>']
    return ''.join(out)

def render_b(i: int) -> str:
    bg = COLORS["sky"]
    title = "IF 30g FIBRE SOUNDS IMPOSSIBLE" if i == 0 else ["ONE TIN DOES THE HEAVY LIFTING.", "THE FIX IS NOT A SUPPLEMENT.", "A BOWL THAT COUNTS.", "THE LABEL DOES THE MATH.", "SAVE THE LIST."][min(i-1,4)]
    out = _base(bg, "GUTKITCHEN  /  FIBRE CALCULATOR", title, "watch the counter climb from ordinary food")
    out += [rect(48, 300, 984, 860, COLORS["ink"], 32), text(88, 385, "FIBRE COUNTER", 28, COLORS["cream"], 800), text(88, 565, ["15.69", "15.04", "15.69", "15.69", "15.69", "15.69"][min(i,5)] + "g", 150, COLORS["cheese"], 900), text(88, 630, "per bowl · lower bound", 26, COLORS["cream"], 600), fibre_counter(88, 720, [15.69, 15.04, 15.69, 15.69, 15.69, 15.69][min(i,5)], 820), before_after_upgrade(88, 850), shopping_basket(110, 1210), save_cta(160, 1570, "SAVE THE 30g DAY"), common_footer("THE NUMBER IS THE HOOK."), '</svg>']
    return ''.join(out)

def render_c(i: int) -> str:
    bg = COLORS["lavender"]
    title = "PIZZA FLAVOUR. BEAN MATHS." if i == 0 else ["CRUNCH THE LABEL.", "BUILD THE BOWL.", "MELT THE FINISH.", "THE NUMBERS HOLD.", "SHOP IT. SAVE IT."][min(i-1,4)]
    out = _base(bg, "GUTKITCHEN  /  EDITORIAL FOOD-BUILD", title, "tactile close-ups · fast cuts · saveable shopping logic")
    out += [rect(48, 300, 984, 820, COLORS["white"], 32), hero_meal(760, 675, 0.88, "pan" if i in (2,3) else "bowl"), protein_fibre_badge(88, 350, "~40g", "15g+", True), text(88, 945, ["40g PROTEIN", "235g CANNELLINI", "100g MOZZARELLA", "15.69g FIBRE", "4 ITEMS"][min(i,4)], 48, COLORS["ink"], 900), text(88, 1015, "close, tactile, ordinary, reproducible", 26, COLORS["muted"], 600), ingredient_build(88, 1180, ["BEANS", "PASSATA", "SPINACH", "LIGHTER MOZZARELLA"], min(i-1,3) if i else -1), evidence_card(88, 1570, "LABEL-BASED ESTIMATE", "check the pack you buy · no wellness promises"), common_footer("TACTILE. NUMERIC. SAVEABLE."), '</svg>']
    return ''.join(out)

def write_stills(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for treatment in ("new-a", "new-b", "new-c"):
        for i in range(6):
            p = out_dir / f"{treatment}-frame-{i+1:02d}.svg"
            p.write_text(render_treatment(treatment, i))
            paths.append(p)
    return paths

def write_manifest_payload(path: Path) -> None:
    payload = {"generated_at": "2026-09-30", "components": ["HeroMeal", "ProteinFibreBadge", "FibreCounter", "IngredientBuild", "BeforeAfterUpgrade", "ShoppingBasket", "EvidenceCard", "SaveCTA"], "shots_per_treatment": 6}
    path.write_text(json.dumps(payload, indent=2) + "\n")
