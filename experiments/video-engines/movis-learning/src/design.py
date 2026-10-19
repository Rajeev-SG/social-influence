from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets/fonts"
FONT_TITLE = FONT_DIR / "Manrope.ttf"
FONT_MONO = FONT_DIR / "Mono.ttf"

W, H = 1080, 1920

BG = (7, 16, 25)
BG_TOP = (11, 27, 38)
INK = (242, 241, 234)
MUTED = (151, 170, 178)
CYAN = (71, 226, 201)
CYAN_DARK = (18, 81, 82)
BLUE = (83, 133, 255)
CORAL = (255, 116, 102)
AMBER = (248, 183, 83)
LINE = (54, 78, 91)
SURFACE = (14, 31, 43)


def font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_MONO if mono else FONT_TITLE), size=size)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease(value: float, start: float, end: float, power: int = 3) -> float:
    t = clamp((value - start) / max(end - start, 1e-6))
    return 1.0 - (1.0 - t) ** power


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(lerp(a[i], b[i], t)) for i in range(3))


def bezier(p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], t: float) -> tuple[float, float]:
    u = 1.0 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
    )


def dashed_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    width: int = 4,
    dash: float = 16.0,
    gap: float = 11.0,
    alpha: int = 255,
) -> None:
    remaining = dash
    drawing = True
    for a, b in zip(points, points[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length <= 0:
            continue
        travelled = 0.0
        while travelled < length:
            step = min(remaining, length - travelled)
            t0 = travelled / length
            t1 = (travelled + step) / length
            if drawing:
                draw.line(
                    (
                        lerp(a[0], b[0], t0),
                        lerp(a[1], b[1], t0),
                        lerp(a[0], b[0], t1),
                        lerp(a[1], b[1], t1),
                    ),
                    fill=(*color, alpha),
                    width=width,
                )
            travelled += step
            remaining -= step
            if remaining <= 1e-5:
                drawing = not drawing
                remaining = dash if drawing else gap


def draw_tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: float = 0.0,
) -> None:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=fnt, fill=fill)
        x += draw.textlength(char, font=fnt) + tracking


def rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int] = SURFACE,
    outline: tuple[int, int, int] = LINE,
    radius: int = 32,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=(*fill, 235), outline=(*outline, 190), width=width)


def draw_ball(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    radius: float = 24.0,
    color: tuple[int, int, int] = CYAN,
    alpha: int = 255,
) -> None:
    draw.ellipse((x - radius * 1.15, y + radius * 0.55, x + radius * 1.15, y + radius * 1.3), fill=(0, 0, 0, 55))
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
    draw.ellipse(
        (x - radius * 0.52, y - radius * 0.58, x - radius * 0.10, y - radius * 0.16),
        fill=(*mix(color, (255, 255, 255), 0.65), alpha),
    )


def draw_bucket(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    scale: float = 1.0,
    color: tuple[int, int, int] = CYAN,
    target: bool = True,
) -> None:
    rx, ry = 112 * scale, 38 * scale
    depth = 165 * scale
    if target:
        draw.ellipse((cx - rx * 1.35, cy - ry * 1.45, cx + rx * 1.35, cy + ry * 1.45), outline=(*color, 80), width=max(2, round(3 * scale)))
    draw.polygon(
        [
            (cx - rx, cy),
            (cx + rx, cy),
            (cx + rx * 0.72, cy + depth),
            (cx - rx * 0.72, cy + depth),
        ],
        fill=(15, 52, 62, 245),
        outline=(*color, 225),
    )
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(7, 24, 33, 255), outline=(*color, 235), width=max(2, round(4 * scale)))
    draw.arc((cx - rx * 1.22, cy - ry * 1.55, cx + rx * 1.22, cy + ry * 1.55), 185, 355, fill=(*color, 155), width=max(2, round(3 * scale)))
    draw.ellipse((cx - rx * 0.76, cy - ry * 0.56, cx + rx * 0.76, cy + ry * 0.56), outline=(*color, 110), width=max(2, round(2 * scale)))


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    a: tuple[float, float],
    b: tuple[float, float],
    color: tuple[int, int, int],
    width: int = 5,
    head: float = 18.0,
    alpha: int = 255,
) -> None:
    draw.line((*a, *b), fill=(*color, alpha), width=width)
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    p1 = (b[0] - head * math.cos(angle - math.pi / 5), b[1] - head * math.sin(angle - math.pi / 5))
    p2 = (b[0] - head * math.cos(angle + math.pi / 5), b[1] - head * math.sin(angle + math.pi / 5))
    draw.polygon([b, p1, p2], fill=(*color, alpha))


def draw_knob(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    value: float,
    color: tuple[int, int, int] = CYAN,
    radius: float = 34.0,
    alpha: int = 255,
) -> None:
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(8, 24, 34, alpha), outline=(*color, alpha), width=3)
    draw.arc((x - radius * 0.78, y - radius * 0.78, x + radius * 0.78, y + radius * 0.78), 145, 395, fill=(*color, int(alpha * 0.32)), width=5)
    angle = math.radians(lerp(135, 405, clamp(value)))
    draw.line((x, y, x + math.cos(angle) * radius * 0.67, y + math.sin(angle) * radius * 0.67), fill=(*color, alpha), width=5)
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(*color, alpha))


def make_background() -> Image.Image:
    base = Image.new("RGB", (W, H), BG)
    pixels = base.load()
    for y in range(H):
        blend = clamp((y - 160) / 1250)
        color = mix(BG_TOP, BG, blend)
        for x in range(W):
            pixels[x, y] = color
    img = base.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(70, W, 120):
        draw.line((x, 0, x, H), fill=(*LINE, 18), width=1)
    for y in range(160, H, 120):
        draw.line((0, y, W, y), fill=(*LINE, 15), width=1)

    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((-420, 280, 760, 1420), fill=(*CYAN_DARK, 68))
    glow = glow.filter(ImageFilter.GaussianBlur(155))
    img = Image.alpha_composite(img, glow)
    img = Image.alpha_composite(img, overlay)
    return img


BACKGROUND = make_background()
