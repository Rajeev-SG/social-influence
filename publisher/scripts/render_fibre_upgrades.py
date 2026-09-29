#!/usr/bin/env python3
"""Render the GutKitchen fibre-upgrades short (1080x1920 vertical MP4).

Content: queue item 'Five ways to add 5g fibre to breakfast' from
brands/gutkitchen/queue.md — quantified, evidence-led per the brand profile.
Numbers from standard UK composition data (NHS/BNF-aligned): chia ~34g
fibre/100g, milled flaxseed ~27g, oats ~10g, raspberries ~6.5g, oat bran ~17g.

Output: posts/gutkitchen-001/ (bundle.json + fibre-upgrades.mp4)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "posts" / "gutkitchen-001"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
FPS = 30
CREAM = (247, 243, 232)
INK = (26, 26, 26)
GREEN = (46, 94, 62)
MUTED = (120, 116, 106)

FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
FONT_REG = "/System/Library/Fonts/Helvetica.ttc"


def font(size: int, index: int = 1) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size, index=index)


def text_center(d: ImageDraw.ImageDraw, y: int, text: str, size: int, fill, index=1, tracking=0):
    f = font(size, index)
    bbox = d.textbbox((0, 0), text, font=f)
    w = bbox[2] - bbox[0]
    d.text(((W - w) / 2, y), text, font=f, fill=fill)
    return f


def card_hook() -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    text_center(d, 620, "You're tracking protein.", 78, INK)
    text_center(d, 740, "Now look at the number", 78, INK)
    text_center(d, 860, "most people ignore.", 78, GREEN)
    text_center(d, 1050, "fibre", 64, MUTED, index=1)
    return img


def card_title() -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    text_center(d, 660, "Five breakfast upgrades", 84, INK)
    text_center(d, 790, "each adds ~5g fibre", 84, GREEN)
    text_center(d, 980, "real numbers, no supplements", 48, MUTED)
    return img


def card_item(n: int, item: str, dose: str, grams: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    text_center(d, 520, f"{n}/5", 60, MUTED)
    text_center(d, 680, item, 72, INK)
    text_center(d, 800, dose, 72, INK)
    text_center(d, 1000, f"+{grams}g fibre", 110, GREEN)
    text_center(d, 1180, f"running total  {total}g", 52, MUTED)
    return img


def card_total() -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    text_center(d, 640, "24g added", 120, GREEN)
    text_center(d, 800, "before you've cooked anything.", 64, INK)
    return img


def card_close() -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    text_center(d, 560, "Most adults should average", 58, INK)
    text_center(d, 660, "30g fibre a day (NHS)", 58, INK)
    text_center(d, 830, "Start with breakfast.", 84, GREEN)
    text_center(d, 1500, "Save this for your next shop.", 56, MUTED)
    return img


def fade(img: Image.Image, t: float, total: float) -> Image.Image:
    """fade in first 0.4s of each scene"""
    if t > 0.4:
        return img
    a = int(255 * (t / 0.4))
    black = Image.new("RGB", (W, H), CREAM)
    return Image.blend(black, img, t / 0.4)


SCENES = [
    (card_hook(), 5.0),
    (card_title(), 4.0),
    (card_item(1, "1 tbsp chia seeds", "stirred into yoghurt", 4, 4), 4.5),
    (card_item(2, "2 tbsp milled flaxseed", "into overnight oats", 4, 8), 4.5),
    (card_item(3, "50g jumbo oats", "instead of cereal flakes", 5, 13), 4.5),
    (card_item(4, "100g raspberries", "fresh or frozen", 6, 19), 4.5),
    (card_item(5, "30g oat bran", "into the pan", 5, 24), 4.5),
    (card_total(), 4.0),
    (card_close(), 5.0),
]

frames_dir = OUT / "_frames"
frames_dir.mkdir(exist_ok=True)

i = 0
for img, dur in SCENES:
    n = int(dur * FPS)
    for f_idx in range(n):
        t = f_idx / FPS
        fade(img, t, dur).save(frames_dir / f"{i:05d}.png")
        i += 1

total_dur = i / FPS
print(f"frames: {i}, duration: {total_dur:.1f}s")