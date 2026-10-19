from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 1080
H = 1920

BG_TOP = (5, 13, 27)
BG_BOTTOM = (12, 31, 52)
PANEL = (17, 36, 59)
PANEL_LIGHT = (25, 50, 77)
INK = (245, 248, 252)
MUTED = (151, 174, 199)
CYAN = (69, 214, 255)
CYAN_DARK = (20, 111, 144)
CORAL = (255, 111, 98)
CORAL_DARK = (151, 57, 57)
YELLOW = (255, 210, 94)
GREEN = (91, 224, 163)
BLUE = (89, 132, 255)
BLACK = (3, 8, 16)

FONT_REGULAR_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttf",
]
FONT_BOLD_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
]

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
_BG_CACHE: Image.Image | None = None


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease_out_cubic(value: float) -> float:
    value = clamp(value)
    return 1 - (1 - value) ** 3


def ease_in_out_cubic(value: float) -> float:
    value = clamp(value)
    return 4 * value**3 if value < 0.5 else 1 - (-2 * value + 2) ** 3 / 2


def ease_out_back(value: float) -> float:
    value = clamp(value)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (value - 1) ** 3 + c1 * (value - 1) ** 2


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = ("bold" if bold else "regular", size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    paths = FONT_BOLD_PATHS if bold else FONT_REGULAR_PATHS
    for path in paths:
        if Path(path).exists():
            font = ImageFont.truetype(path, size=size)
            _FONT_CACHE[key] = font
            return font
    font = ImageFont.load_default(size=size)
    _FONT_CACHE[key] = font
    return font


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> float:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and text_width(draw, candidate, font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def rounded_shadow(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    shadow: int = 22,
    outline: tuple[int, int, int] | None = None,
    width: int = 2,
) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(
        (x1 + 6, y1 + shadow, x2 + 6, y2 + shadow),
        radius=radius,
        fill=(0, 0, 0, 105),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(15))
    canvas.alpha_composite(overlay)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    width: int = 8,
    head: int = 20,
) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    left = (
        x2 - head * math.cos(angle - math.pi / 5),
        y2 - head * math.sin(angle - math.pi / 5),
    )
    right = (
        x2 - head * math.cos(angle + math.pi / 5),
        y2 - head * math.sin(angle + math.pi / 5),
    )
    draw.polygon([(x2, y2), left, right], fill=color)


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
) -> None:
    draw.text((center_x, y), text, font=font, fill=fill, anchor="ma")


def draw_kicker(
    draw: ImageDraw.ImageDraw,
    scene_number: str,
    left_label: str,
    accent: tuple[int, int, int],
) -> None:
    draw.line((84, 112, 140, 112), fill=accent, width=6)
    draw.text((158, 91), f"VIDEOFLOW / {left_label}", font=load_font(27, True), fill=MUTED)
    draw.text((996, 87), scene_number, font=load_font(30, True), fill=accent, anchor="ra")


def make_background() -> Image.Image:
    global _BG_CACHE
    if _BG_CACHE is not None:
        return _BG_CACHE.copy()
    image = Image.new("RGBA", (W, H), BG_TOP + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(H):
        p = y / (H - 1)
        color = tuple(
            int(BG_TOP[i] * (1 - p) + BG_BOTTOM[i] * p) for i in range(3)
        )
        draw.line((0, y, W, y), fill=color + (255,))

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-360, -240, 520, 560), fill=(34, 111, 160, 110))
    gd.ellipse((690, 1170, 1380, 1880), fill=(28, 88, 132, 115))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    image.alpha_composite(glow)

    for x in range(84, W - 40, 128):
        draw.line((x, 160, x, H - 250), fill=(92, 134, 171, 16), width=1)
    for y in range(160, H - 240, 128):
        draw.line((84, y, W - 84, y), fill=(92, 134, 171, 16), width=1)
    _BG_CACHE = image
    return image.copy()


def draw_caption(
    canvas: Image.Image,
    text: str,
    progress: float,
    accent: tuple[int, int, int],
) -> None:
    if not text:
        return
    draw = ImageDraw.Draw(canvas)
    font = load_font(43, True)
    lines = wrap_text(draw, text, font, 820)
    if len(lines) > 3:
        font = load_font(37, True)
        lines = wrap_text(draw, text, font, 830)
    line_height = 54 if font.size >= 42 else 48
    card_height = 96 + line_height * len(lines)
    y1 = H - 236 - card_height
    rounded_shadow(canvas, (70, y1, 1010, y1 + card_height), 32, (5, 12, 22, 236), shadow=14)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (70, y1, 1010, y1 + card_height),
        radius=32,
        outline=(92, 132, 164, 150),
        width=2,
    )
    y = y1 + 42
    for line in lines:
        draw.text((112, y), line, font=font, fill=INK)
        y += line_height
    progress_width = int((940 - 112) * clamp(progress))
    if progress_width > 0:
        draw.rounded_rectangle(
            (112, y1 + card_height - 30, 112 + progress_width, y1 + card_height - 24),
            radius=3,
            fill=accent,
        )


def draw_input_chip(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    label: str,
    value: str,
    accent: tuple[int, int, int],
    active: float = 1.0,
) -> None:
    draw = ImageDraw.Draw(canvas)
    rounded_shadow(canvas, box, 26, PANEL_LIGHT + (255,), shadow=12)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(
        (x1, y1, x1 + 10, y2),
        radius=5,
        fill=accent if active > 0.02 else MUTED,
    )
    draw.text((x1 + 34, y1 + 24), label, font=load_font(24, True), fill=MUTED)
    draw.text((x1 + 34, y1 + 62), value, font=load_font(42, True), fill=INK)


def draw_model_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    accent: tuple[int, int, int],
    progress: float,
    locked: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    rounded_shadow(canvas, box, 36, PANEL + (255,), shadow=24, outline=accent, width=3)
    draw = ImageDraw.Draw(canvas)
    draw.text((x1 + 38, y1 + 34), title, font=load_font(31, True), fill=accent)
    draw.text((x1 + 38, y1 + 78), subtitle, font=load_font(23), fill=MUTED)
    cx = (x1 + x2) // 2
    cy = y1 + 205
    for idx, radius in enumerate((112, 82, 52)):
        alpha = 150 + idx * 30
        ring_color = tuple(min(255, int(accent[i] * (0.55 + idx * 0.15))) for i in range(3))
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=ring_color + (alpha,),
            width=5,
        )
    sweep = math.pi * (1.5 * clamp(progress) - 0.25)
    draw.line(
        (
            cx,
            cy,
            cx + int(112 * math.cos(sweep)),
            cy + int(112 * math.sin(sweep)),
        ),
        fill=accent,
        width=8,
    )
    if locked:
        draw.rounded_rectangle((cx - 38, cy - 18, cx + 38, cy + 42), radius=12, fill=accent)
        draw.arc((cx - 26, cy - 62, cx + 26, cy - 2), 180, 360, fill=accent, width=12)
        draw.ellipse((cx - 8, cy + 1, cx + 8, cy + 17), fill=PANEL)
    else:
        draw.text((cx, cy - 20), "ADJUST", font=load_font(28, True), fill=INK, anchor="mm")
        draw.text((cx, cy + 18), "LEARN", font=load_font(24, True), fill=MUTED, anchor="mm")
    draw.line((x1 + 38, y2 - 78, x2 - 38, y2 - 78), fill=(73, 107, 137), width=2)
    draw.text(
        (x1 + 38, y2 - 54),
        "PATTERN" if locked else "PATTERN + ERRORS",
        font=load_font(23, True),
        fill=INK,
    )


def render_intro(canvas: Image.Image, p: float, caption: str, caption_progress: float) -> None:
    draw = ImageDraw.Draw(canvas)
    draw_kicker(draw, "01 / 05", "MODEL BASICS", CYAN)
    reveal = ease_out_cubic(p / 0.24)
    title_y = int(192 - 50 * (1 - reveal))
    draw_centered_text(draw, W // 2, title_y, "TRAINING", load_font(112, True), CORAL)
    draw_centered_text(draw, W // 2, title_y + 112, "VERSUS", load_font(38, True), MUTED)
    draw_centered_text(draw, W // 2, title_y + 164, "INFERENCE", load_font(112, True), CYAN)

    rounded_shadow(canvas, (72, 574, 1008, 1372), 42, PANEL + (255,), shadow=28)
    draw = ImageDraw.Draw(canvas)
    draw.line((540, 630, 540, 1310), fill=(85, 126, 158), width=3)
    draw.text((118, 636), "LEARN", font=load_font(27, True), fill=CORAL)
    draw.text((588, 636), "USE", font=load_font(27, True), fill=CYAN)
    draw.text((118, 688), "many examples", font=load_font(46, True), fill=INK)
    draw.text((588, 688), "one new input", font=load_font(46, True), fill=INK)

    for row in range(3):
        for col in range(2):
            idx = row * 2 + col
            appear = ease_out_back((p - 0.05 - idx * 0.045) / 0.18)
            if appear <= 0:
                continue
            x = 118 + col * 184
            y = 804 + row * 126
            w = int(154 * appear)
            h = int(82 * appear)
            rounded_shadow(canvas, (x, y, x + w, y + h), 18, CORAL_DARK + (255,), shadow=7)
            draw = ImageDraw.Draw(canvas)
            draw.text((x + 18, y + 18), f"EX {idx + 1:02d}", font=load_font(25, True), fill=INK)
            draw.line((x + 18, y + 57, x + max(28, w - 18), y + 57), fill=CORAL, width=4)

    train_arrow = ease_in_out_cubic((p - 0.18) / 0.38)
    if train_arrow > 0:
        draw_arrow(draw, (314, 1218), (458, 1218), CORAL, width=8)
        draw.text((382, 1140), "study", font=load_font(24, True), fill=MUTED, anchor="mm")

    infer_start = ease_out_cubic((p - 0.36) / 0.22)
    if infer_start > 0:
        y = int(842 + 34 * (1 - infer_start))
        rounded_shadow(canvas, (612, y, 922, y + 112), 22, CYAN_DARK + (255,), shadow=10)
        draw = ImageDraw.Draw(canvas)
        draw.text((638, y + 18), "NEW INPUT", font=load_font(23, True), fill=CYAN)
        draw.text((638, y + 56), "fresh question", font=load_font(30, True), fill=INK)
        draw_arrow(draw, (766, y + 138), (766, y + 210), CYAN, width=8)
        output_p = ease_out_back((p - 0.53) / 0.25)
        if output_p > 0:
            oy = int(y + 242 - 18 * (1 - output_p))
            rounded_shadow(canvas, (612, oy, 922, oy + 112), 22, PANEL_LIGHT + (255,), shadow=10)
            draw = ImageDraw.Draw(canvas)
            draw.text((638, oy + 18), "ONE ANSWER", font=load_font(23, True), fill=CYAN)
            draw.text((638, oy + 56), "prediction", font=load_font(30, True), fill=INK)

    draw.text(
        (118, 1262),
        "repeated adjustment",
        font=load_font(26, True),
        fill=CORAL,
    )
    draw.text(
        (588, 1262),
        "fixed learned pattern",
        font=load_font(26, True),
        fill=CYAN,
    )
    draw_caption(canvas, caption, caption_progress, CYAN)


def render_training(canvas: Image.Image, p: float, caption: str, caption_progress: float) -> None:
    draw = ImageDraw.Draw(canvas)
    draw_kicker(draw, "02 / 05", "TRAINING", CORAL)
    draw.text((84, 184), "Learn the pattern", font=load_font(82, True), fill=INK)
    draw.text((84, 292), "Examples in. Errors measured. Weights adjusted.", font=load_font(34), fill=MUTED)

    for idx in range(4):
        appear = ease_out_back((p - idx * 0.075) / 0.22)
        if appear <= 0:
            continue
        y = 502 + idx * 130
        x = 84 + int(18 * (1 - appear))
        rounded_shadow(canvas, (x, y, x + 242, y + 92), 20, CORAL_DARK + (255,), shadow=8)
        draw = ImageDraw.Draw(canvas)
        draw.text((x + 22, y + 16), f"EXAMPLE {idx + 1:02d}", font=load_font(23, True), fill=CORAL)
        draw.text((x + 22, y + 50), ["sweet", "salty", "soft", "crisp"][idx], font=load_font(28, True), fill=INK)
        draw_arrow(draw, (x + 254, y + 46), (372, y + 46), CORAL, width=5, head=14)

    draw_model_card(
        canvas,
        (390, 486, 770, 972),
        "MODEL",
        "learning the recipe",
        CORAL,
        p,
        locked=False,
    )
    draw = ImageDraw.Draw(canvas)
    draw_arrow(draw, (788, 670), (862, 670), CORAL, width=7, head=18)
    draw_input_chip(canvas, (842, 570, 996, 736), "GUESS", "tangy", CORAL, 1.0)
    draw_input_chip(canvas, (842, 768, 996, 934), "ANSWER", "sweet", GREEN, 1.0)
    draw_arrow(draw, (918, 754), (918, 742), YELLOW, width=5, head=12)

    # Feedback loop: the visible adjustment is the key explanatory motion.
    loop_p = ease_in_out_cubic((p % 0.34) / 0.34)
    draw_arrow(draw, (876, 966), (876, 1046), YELLOW, width=8)
    draw_arrow(draw, (876, 1046), (734, 1046), YELLOW, width=8)
    draw_arrow(draw, (734, 1046), (734, 982), YELLOW, width=8)
    draw.text((802, 1068), "ADJUST", font=load_font(25, True), fill=YELLOW, anchor="mm")
    if loop_p > 0:
        x = int(876 - 142 * loop_p)
        y = 1046 if loop_p < 0.65 else int(1046 - 64 * ((loop_p - 0.65) / 0.35))
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=YELLOW)

    rounded_shadow(canvas, (84, 1110, 996, 1292), 28, PANEL + (255,), shadow=14)
    draw = ImageDraw.Draw(canvas)
    draw.text((116, 1142), "CHEF'S NOTEBOOK", font=load_font(25, True), fill=YELLOW)
    steps = [
        ("TASTE", 0.10, 118),
        ("COMPARE", 0.42, 342),
        ("ADJUST", 0.76, 566),
    ]
    for label, start, step_x in steps:
        active = ease_out_cubic((p - start) / 0.17)
        color = CORAL if active > 0 else (81, 111, 137)
        draw.ellipse((step_x, 1204, step_x + 32, 1236), outline=color, width=6)
        if active > 0.2:
            draw.ellipse((step_x + 9, 1213, step_x + 23, 1227), fill=color)
        draw.text(
            (step_x + 46, 1198),
            label,
            font=load_font(25, True),
            fill=INK if active > 0 else MUTED,
        )
    draw.line((302, 1220, 330, 1220), fill=(78, 111, 139), width=4)
    draw.line((526, 1220, 554, 1220), fill=(78, 111, 139), width=4)
    draw.text((876, 1188), "error", font=load_font(24, True), fill=MUTED, anchor="ma")
    error_p = ease_out_cubic(p)
    draw.rounded_rectangle((710, 1230, 930, 1254), radius=12, fill=(53, 77, 101))
    draw.rounded_rectangle(
        (710, 1230, int(930 - 160 * error_p), 1254),
        radius=12,
        fill=GREEN,
    )
    draw_caption(canvas, caption, caption_progress, CORAL)


def render_transition(canvas: Image.Image, p: float, caption: str, caption_progress: float) -> None:
    draw = ImageDraw.Draw(canvas)
    wipe = ease_in_out_cubic(p)
    split_x = int(W * (0.30 + 0.48 * wipe))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, split_x, H), fill=(76, 25, 33, 95))
    od.rectangle((split_x, 0, W, H), fill=(9, 61, 82, 118))
    canvas.alpha_composite(overlay)
    draw = ImageDraw.Draw(canvas)
    draw_kicker(draw, "03 / 05", "THE HANDOFF", YELLOW)
    draw_centered_text(draw, W // 2, 284, "LEARNING", load_font(82, True), CORAL)
    draw_centered_text(draw, W // 2, 382, "BECOMES", load_font(34, True), MUTED)
    draw_centered_text(draw, W // 2, 446, "USING", load_font(94, True), CYAN)

    draw.line((split_x, 612, split_x, 1288), fill=YELLOW, width=7)
    draw.ellipse((split_x - 38, 850, split_x + 38, 926), fill=YELLOW)
    draw.text((split_x, 870), "=", font=load_font(48, True), fill=BLACK, anchor="mm")

    left_x = int(94 + 120 * (1 - wipe))
    rounded_shadow(canvas, (left_x, 664, left_x + 350, 1138), 32, CORAL_DARK + (255,), shadow=18)
    draw = ImageDraw.Draw(canvas)
    draw.text((left_x + 32, 704), "NOTEBOOK", font=load_font(27, True), fill=CORAL)
    draw.text((left_x + 32, 756), "many pages", font=load_font(40, True), fill=INK)
    for row in range(5):
        y = 840 + row * 54
        draw.line((left_x + 32, y, left_x + 310, y), fill=(255, 148, 127), width=7)
        draw.line((left_x + 32, y + 18, left_x + 240, y + 18), fill=(156, 72, 71), width=5)

    right_x = int(636 - 110 * (1 - wipe))
    rounded_shadow(canvas, (right_x, 664, right_x + 350, 1138), 32, CYAN_DARK + (255,), shadow=18)
    draw = ImageDraw.Draw(canvas)
    draw.text((right_x + 32, 704), "RECIPE CARD", font=load_font(27, True), fill=CYAN)
    draw.text((right_x + 32, 756), "one fixed set", font=load_font(40, True), fill=INK)
    draw.rounded_rectangle((right_x + 50, 840, right_x + 300, 988), radius=22, fill=(12, 58, 78), outline=CYAN, width=3)
    draw.text((right_x + 74, 872), "LOCKED", font=load_font(34, True), fill=CYAN)
    draw.text((right_x + 74, 920), "no more edits", font=load_font(25, True), fill=INK)
    draw.line((right_x + 54, 1036, right_x + 298, 1036), fill=CYAN, width=8)
    draw.text((right_x + 176, 1066), "ready to use", font=load_font(24, True), fill=MUTED, anchor="ma")

    # A compact analogy strip keeps the teaching through-line visible during
    # the state change instead of leaving the lower frame unresolved.
    rounded_shadow(canvas, (112, 1192, 968, 1350), 28, (13, 31, 50, 246), shadow=12)
    draw = ImageDraw.Draw(canvas)
    draw.text((150, 1220), "THE THROUGH-LINE", font=load_font(23, True), fill=YELLOW)
    flow_items = [
        (260, "MANY DISHES", CORAL),
        (508, "ONE RECIPE", YELLOW),
        (820, "NEW DISH", CYAN),
    ]
    for center_x, label, color in flow_items:
        draw.rounded_rectangle(
            (center_x - 110, 1272, center_x + 110, 1322),
            radius=20,
            fill=(27, 48, 69),
            outline=color,
            width=3,
        )
        draw.text((center_x, 1284), label, font=load_font(23, True), fill=INK, anchor="ma")
    draw_arrow(draw, (382, 1297), (414, 1297), MUTED, width=5, head=14)
    draw_arrow(draw, (630, 1297), (694, 1297), MUTED, width=5, head=14)

    draw_caption(canvas, caption, caption_progress, YELLOW)


def render_inference(canvas: Image.Image, p: float, caption: str, caption_progress: float) -> None:
    draw = ImageDraw.Draw(canvas)
    draw_kicker(draw, "04 / 05", "INFERENCE", CYAN)
    draw.text((84, 184), "Use the pattern", font=load_font(82, True), fill=INK)
    draw.text((84, 292), "One fresh input. One forward pass. One prediction.", font=load_font(34), fill=MUTED)

    draw_model_card(
        canvas,
        (250, 438, 830, 872),
        "TRAINED MODEL",
        "fixed recipe",
        CYAN,
        p,
        locked=True,
    )
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((414, 840, 666, 888), radius=22, fill=CYAN)
    draw.text((540, 851), "LOCKED", font=load_font(25, True), fill=BLACK, anchor="mm")

    input_p = ease_out_back((p - 0.12) / 0.22)
    if input_p > 0:
        y = int(560 + 38 * (1 - input_p))
        rounded_shadow(canvas, (92, y, 238, y + 134), 24, PANEL_LIGHT + (255,), shadow=12)
        draw = ImageDraw.Draw(canvas)
        draw.text((118, y + 22), "NEW", font=load_font(23, True), fill=CYAN)
        draw.text((118, y + 58), "DISH", font=load_font(37, True), fill=INK)
        draw_arrow(draw, (254, y + 68), (332, 652), CYAN, width=7, head=18)

    forward_p = ease_in_out_cubic((p - 0.24) / 0.30)
    if forward_p > 0:
        x = int(540 + 0)
        y = int(892 + 182 * forward_p)
        draw_arrow(draw, (540, 900), (540, y), CYAN, width=8)
        draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=CYAN)

    output_p = ease_out_back((p - 0.50) / 0.25)
    if output_p > 0:
        oy = int(1100 + 30 * (1 - output_p))
        rounded_shadow(canvas, (252, oy, 828, oy + 188), 32, PANEL_LIGHT + (255,), shadow=18, outline=CYAN, width=3)
        draw = ImageDraw.Draw(canvas)
        draw.text((290, oy + 28), "ONE PREDICTION", font=load_font(26, True), fill=CYAN)
        draw.text((290, oy + 76), "fresh dish → likely sweet", font=load_font(43, True), fill=INK)
        draw.text((290, oy + 132), "the learned recipe does the work", font=load_font(23), fill=MUTED)

    draw.rounded_rectangle((282, 1378, 798, 1450), radius=22, outline=(105, 139, 166), width=3)
    draw.text((540, 1400), "NO WEIGHT UPDATE", font=load_font(29, True), fill=YELLOW, anchor="mm")
    draw.text((540, 1464), "using is not learning", font=load_font(24), fill=MUTED, anchor="ma")
    draw_caption(canvas, caption, caption_progress, CYAN)


def render_outro(canvas: Image.Image, p: float, caption: str, caption_progress: float) -> None:
    draw = ImageDraw.Draw(canvas)
    draw_kicker(draw, "05 / 05", "TAKEAWAY", GREEN)
    reveal = ease_out_cubic(p / 0.25)
    draw_centered_text(draw, W // 2, 252, "LEARN ONCE", load_font(96, True), CORAL)
    draw_centered_text(draw, W // 2, 376, "USE MANY TIMES", load_font(82, True), CYAN)
    draw_centered_text(
        draw,
        W // 2,
        510,
        "Training updates the pattern. Inference applies it.",
        load_font(34),
        MUTED,
    )

    rounded_shadow(canvas, (82, 672, 998, 1258), 38, PANEL + (255,), shadow=24)
    draw = ImageDraw.Draw(canvas)
    draw.text((126, 724), "TRAINING", font=load_font(31, True), fill=CORAL)
    draw.text((670, 724), "INFERENCE", font=load_font(31, True), fill=CYAN)
    draw.rounded_rectangle((126, 812, 452, 1042), radius=30, fill=CORAL_DARK, outline=CORAL, width=3)
    draw.text((289, 862), "LEARN", font=load_font(50, True), fill=INK, anchor="mm")
    draw.text((289, 932), "many → one", font=load_font(30, True), fill=MUTED, anchor="mm")
    draw.text((289, 982), "recipe", font=load_font(33, True), fill=YELLOW, anchor="mm")
    draw_arrow(draw, (478, 926), (612, 926), GREEN, width=10, head=25)
    draw.text((545, 858), "fixed", font=load_font(24, True), fill=GREEN, anchor="mm")
    draw.rounded_rectangle((638, 812, 950, 1042), radius=30, fill=CYAN_DARK, outline=CYAN, width=3)
    draw.text((794, 862), "USE", font=load_font(50, True), fill=INK, anchor="mm")
    draw.text((794, 932), "one → one", font=load_font(30, True), fill=MUTED, anchor="mm")
    draw.text((794, 982), "prediction", font=load_font(33, True), fill=YELLOW, anchor="mm")

    timeline_y = 1128
    draw.line((154, timeline_y, 926, timeline_y), fill=(89, 125, 152), width=5)
    for idx in range(7):
        x = 154 + idx * 129
        color = CORAL if idx == 0 else CYAN
        draw.ellipse((x - 12, timeline_y - 12, x + 12, timeline_y + 12), fill=color)
        draw.text((x, timeline_y + 36), "01" if idx == 0 else f"{idx + 1:02d}", font=load_font(21, True), fill=MUTED, anchor="ma")
    draw.text((540, 1214), "the learning happens once; the pattern can be used repeatedly", font=load_font(23), fill=MUTED, anchor="ma")

    fade = ease_out_cubic((p - 0.28) / 0.32)
    if fade > 0:
        draw.rounded_rectangle((250, 1340, 830, 1440), radius=30, fill=(30, 55, 75), outline=GREEN, width=3)
        draw.text((540, 1376), "TRAINING ≠ INFERENCE", font=load_font(37, True), fill=INK, anchor="mm")
    draw_caption(canvas, caption, caption_progress, GREEN)


def render_frame(
    state: dict[str, Any],
    project_path: str,
    assets_dir: str,
    output_path: Path,
) -> None:
    # The source/asset paths are accepted for future asset-driven scenes and kept
    # in the worker API so the render graph remains explicit and reproducible.
    _ = (project_path, assets_dir)
    canvas = make_background()
    scene = state["scene"]
    p = float(state["scene_progress"])
    caption = str(state.get("caption", ""))
    caption_progress = float(state.get("caption_progress", 0.0))
    if scene == "intro":
        render_intro(canvas, p, caption, caption_progress)
    elif scene == "training":
        render_training(canvas, p, caption, caption_progress)
    elif scene == "transition":
        render_transition(canvas, p, caption, caption_progress)
    elif scene == "inference":
        render_inference(canvas, p, caption, caption_progress)
    else:
        render_outro(canvas, p, caption, caption_progress)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, quality=94, subsampling=1)


if __name__ == "__main__":
    # Lightweight local smoke render for one frame when debugging visual code.
    timing = {
        "fps": 30,
        "scenes": [{"id": "intro", "start": 0, "end": 1}],
        "lines": [{"text": "Training versus inference.", "start": 0, "end": 1, "duration": 1}],
    }
    render_frame(
        {
            "frame": 0,
            "timestamp": 0,
            "scene": "intro",
            "scene_progress": 0.5,
            "caption": timing["lines"][0]["text"],
            "caption_progress": 0.5,
        },
        "",
        "",
        Path("/tmp/videoflow-smoke.jpg"),
    )
