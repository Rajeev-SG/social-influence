"""Deterministic GutKitchen SVG components used by every candidate treatment."""
from __future__ import annotations

from html import escape
from typing import Any

W, H = 1080, 1920
COLORS = {
    "ink": "#1c2a21",
    "cream": "#fff7e9",
    "tomato": "#d84b36",
    "spinach": "#315c3b",
    "cheese": "#ffd166",
    "bean": "#f4e3b2",
    "sky": "#cbe8e7",
    "lavender": "#ddd8ff",
    "white": "#fffdf8",
    "muted": "#5e695f",
}


def svg_open() -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'


def text(x: int, y: int, value: str, size: int = 38, fill: str = COLORS["ink"], weight: int = 700, anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>'


def rect(x: int, y: int, w: int, h: int, fill: str, rx: int = 0, opacity: float = 1) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" opacity="{opacity}"/>'


def circle(cx: int, cy: int, r: int, fill: str, stroke: str = "none", sw: int = 0) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def path(d: str, fill: str = "none", stroke: str = COLORS["ink"], sw: int = 8, opacity: float = 1) -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'


def hero_meal(x: int, y: int, scale: float = 1.0, variant: str = "bowl") -> str:
    if variant == "pan":
        body = rect(x - 310 * scale, y - 90 * scale, 620 * scale, 300 * scale, "#262626", int(34 * scale))
        handle = rect(x + 250 * scale, y - 25 * scale, 240 * scale, 48 * scale, "#353535", int(22 * scale))
        food = circle(x, y + 45 * scale, 260 * scale, COLORS["tomato"], "#8f2e27", int(12 * scale))
        cheese = path(f"M {x-150*scale} {y-5*scale} C {x-80*scale} {y-100*scale} {x+70*scale} {y-100*scale} {x+145*scale} {y-10*scale} L {x+80*scale} {y+85*scale} C {x+20*scale} {y+120*scale} {x-70*scale} {y+90*scale} {x-150*scale} {y-5*scale} Z", COLORS["cheese"], "#b67b1d", int(8 * scale))
        greens = ''.join(circle(x+dx*scale, y+dy*scale, int(25*scale), COLORS["spinach"]) for dx,dy in [(-110,25),(-30,85),(80,20),(145,70)])
        return body+handle+food+cheese+greens
    body = circle(x, y + 60 * scale, 310 * scale, COLORS["white"], "#d8c9ad", int(12 * scale))
    rim = circle(x, y + 60 * scale, 270 * scale, COLORS["tomato"], "#8f2e27", int(10 * scale))
    beans = ''.join(circle(x+dx*scale, y+dy*scale, int(28*scale), COLORS["bean"], "#b88b52", int(3*scale)) for dx,dy in [(-150,-25),(-80,45),(0,-20),(95,38),(170,-20),(-170,95),(20,105),(145,115),(-45,-105),(80,-95)])
    cheese = path(f"M {x-145*scale} {y-20*scale} C {x-65*scale} {y-125*scale} {x+75*scale} {y-115*scale} {x+155*scale} {y-5*scale} L {x+95*scale} {y+95*scale} C {x+15*scale} {y+135*scale} {x-85*scale} {y+105*scale} {x-145*scale} {y-20*scale} Z", COLORS["cheese"], "#b67b1d", int(8 * scale))
    greens = ''.join(circle(x+dx*scale, y+dy*scale, int(28*scale), COLORS["spinach"]) for dx,dy in [(-110,25),(-30,85),(80,20),(145,70)])
    return body+rim+beans+cheese+greens


def protein_fibre_badge(x: int, y: int, protein: str, fibre: str, dark: bool = False) -> str:
    bg = COLORS["ink"] if dark else COLORS["cream"]
    fg = COLORS["cream"] if dark else COLORS["ink"]
    return ''.join([
        rect(x, y, 410, 122, bg, 22, 0.96),
        rect(x + 16, y + 16, 178, 90, COLORS["cheese"], 16),
        rect(x + 216, y + 16, 178, 90, COLORS["bean"], 16),
        text(x + 105, y + 60, protein, 34, COLORS["ink"], 800, "middle"),
        text(x + 105, y + 88, "PROTEIN", 18, COLORS["ink"], 700, "middle"),
        text(x + 305, y + 60, fibre, 34, COLORS["ink"], 800, "middle"),
        text(x + 305, y + 88, "FIBRE", 18, COLORS["ink"], 700, "middle"),
        text(x + 205, y + 116, "label estimate · check your pack", 15, fg, 500, "middle"),
    ])


def fibre_counter(x: int, y: int, value: float, width: int = 720) -> str:
    pct = max(0.04, min(value / 20.0, 1.0))
    return ''.join([
        text(x, y - 18, f"TRACK THE NUMBER MOST PEOPLE IGNORE  ·  {value:.2g}g FIBRE", 24, COLORS["cream"], 800),
        rect(x, y, width, 22, "#ffffff33", 11),
        rect(x, y, int(width * pct), 22, COLORS["cheese"], 11),
        text(x + width, y + 48, "0g", 18, COLORS["cream"], 700, "end"),
        text(x + width, y + 48, "20g", 18, COLORS["cream"], 700, "start"),
    ])


def ingredient_build(x: int, y: int, items: list[str], active: int = -1) -> str:
    out = [text(x, y, "BUILD IT", 24, COLORS["cream"], 800)]
    for i, item in enumerate(items):
        yy = y + 70 + i * 76
        fill = COLORS["cheese"] if i == active else "#ffffff22"
        out += [rect(x, yy - 42, 620, 58, fill, 18), circle(x + 28, yy - 13, 16, COLORS["tomato"] if i == active else COLORS["bean"]), text(x + 64, yy - 3, item, 27, COLORS["cream"] if i != active else COLORS["ink"], 700)]
    return ''.join(out)


def before_after_upgrade(x: int, y: int) -> str:
    return ''.join([
        rect(x, y, 420, 420, COLORS["cream"], 28),
        rect(x + 500, y, 420, 420, COLORS["cheese"], 28),
        text(x + 210, y + 55, "BEFORE", 24, COLORS["muted"], 800, "middle"),
        text(x + 710, y + 55, "AFTER", 24, COLORS["ink"], 800, "middle"),
        hero_meal(x + 210, y + 185, 0.45, "bowl"),
        hero_meal(x + 710, y + 185, 0.45, "pan"),
        text(x + 210, y + 370, "plain pasta", 24, COLORS["muted"], 700, "middle"),
        text(x + 710, y + 370, "beans + greens", 24, COLORS["ink"], 800, "middle"),
    ])


def shopping_basket(x: int, y: int) -> str:
    return ''.join([rect(x, y, 860, 250, COLORS["cream"], 28), text(x + 32, y + 54, "SUPERMARKET BASKET", 24, COLORS["tomato"], 800), text(x + 32, y + 112, "cannellini beans  ·  passata  ·  spinach  ·  lighter mozzarella", 30, COLORS["ink"], 700), text(x + 32, y + 172, "ordinary ingredients. numbers first.", 24, COLORS["muted"], 600), text(x + 820, y + 218, "SAVE", 28, COLORS["spinach"], 800, "end")])


def evidence_card(x: int, y: int, title: str, body: str) -> str:
    return ''.join([rect(x, y, 820, 180, COLORS["sky"], 24), text(x + 28, y + 55, title, 25, COLORS["ink"], 800), text(x + 28, y + 105, body, 23, COLORS["ink"], 600)])


def save_cta(x: int, y: int, cta: str) -> str:
    return ''.join([rect(x, y, 760, 112, COLORS["tomato"], 28), text(x + 380, y + 71, cta, 34, COLORS["cream"], 800, "middle")])


def common_footer(label: str) -> str:
    return ''.join([rect(0, 1760, W, 160, COLORS["ink"]), text(48, 1810, label, 22, COLORS["cream"], 700), text(48, 1852, "GUTKITCHEN  ·  real numbers. normal ingredients.", 30, COLORS["cheese"], 800), text(W - 48, 1852, "SAVE THIS FOR YOUR NEXT SHOP", 22, COLORS["cream"], 700, "end")])
