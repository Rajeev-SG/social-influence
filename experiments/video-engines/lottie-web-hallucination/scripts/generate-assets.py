#!/usr/bin/env python3
"""Generate transparent typography and a restrained gradient background."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TEXT_DIR = ASSETS / "text"
SPEC_PATH = ROOT / "src" / "text-spec.json"
NARRATION_PATH = ROOT / "src" / "narration.json"

FONT_PATHS = {
    "sans": "/System/Library/Fonts/SFNS.ttf",
    "bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "black": "/System/Library/Fonts/Supplemental/Arial Black.ttf",
}


def font_for(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATHS[name], size=size)


def tracked_text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, tracking: int) -> int:
    if not text:
        return 0
    widths = [draw.textbbox((0, 0), ch, font=font)[2] for ch in text]
    return sum(widths) + max(0, len(text) - 1) * tracking


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    tracking: int,
    stroke_fill: str | None = None,
    stroke_width: int = 0,
) -> None:
    x, y = xy
    for ch in text:
        draw.text(
            (x, y),
            ch,
            font=font,
            fill=fill,
            stroke_fill=stroke_fill,
            stroke_width=stroke_width,
        )
        x += draw.textbbox((0, 0), ch, font=font)[2] + tracking


def render_text_item(item: dict, index: int) -> dict:
    size = int(item["size"])
    tracking = int(item.get("tracking", 0))
    font = font_for(item.get("font", "sans"), size)
    scratch = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(scratch)
    text = item["text"]
    width = tracked_text_width(draw, text, font, tracking)
    ascent, descent = font.getmetrics()
    height = ascent + descent
    pad_x = max(18, size // 5)
    pad_y = max(14, size // 6)
    canvas_w = width + pad_x * 2
    canvas_h = height + pad_y * 2

    shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    draw_tracked(
        shadow_draw,
        (pad_x, pad_y + max(3, size // 22)),
        text,
        font,
        "#020711",
        tracking,
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(4, size // 18)))
    shadow.putalpha(shadow.getchannel("A").point(lambda a: int(a * 0.52)))

    image = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    image.alpha_composite(shadow)
    draw = ImageDraw.Draw(image)
    stroke_width = max(1, size // 48) if item.get("font") == "black" else 0
    draw_tracked(
        draw,
        (pad_x, pad_y),
        text,
        font,
        item["color"],
        tracking,
        stroke_fill="#08111F",
        stroke_width=stroke_width,
    )

    path = TEXT_DIR / f"{index:02d}-{item['id']}.png"
    image.save(path, optimize=True)
    return {
        "id": item["id"],
        "path": f"text/{path.name}",
        "width": canvas_w,
        "height": canvas_h,
        "text": text,
    }


def render_background() -> None:
    width, height = 1080, 1920
    bg = Image.new("RGB", (width, height))
    pixels = bg.load()
    top = (7, 16, 31)
    bottom = (17, 39, 60)
    for y in range(height):
        t = y / (height - 1)
        eased = t * t * (3 - 2 * t)
        for x in range(width):
            side = 0.94 + 0.06 * math.sin(math.pi * x / width)
            pixels[x, y] = tuple(
                max(0, min(255, int((top[i] * (1 - eased) + bottom[i] * eased) * side)))
                for i in range(3)
            )

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(60, width, 120):
        od.line((x, 0, x, height), fill=(99, 213, 255, 11), width=1)
    for y in range(80, height, 120):
        od.line((0, y, width, y), fill=(99, 213, 255, 9), width=1)

    vignette = Image.new("L", (width, height), 0)
    vd = ImageDraw.Draw(vignette)
    for i in range(80):
        alpha = int(2.2 * i)
        vd.rectangle(
            (i, i, width - 1 - i, height - 1 - i),
            outline=alpha,
            width=3,
        )
    vignette = vignette.filter(ImageFilter.GaussianBlur(80))
    dark = Image.new("RGBA", (width, height), (0, 5, 12, 255))
    dark.putalpha(vignette.point(lambda a: min(135, a)))
    bg = bg.convert("RGBA")
    bg.alpha_composite(overlay)
    bg.alpha_composite(dark)
    bg.convert("RGB").save(ASSETS / "background.jpg", quality=92, optimize=True)


def main() -> None:
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC_PATH.read_text())
    narration = json.loads(NARRATION_PATH.read_text())
    items = list(spec["items"])
    for index, line in enumerate(narration["lines"], start=1):
        items.append(
            {
                "id": f"caption_{index:02d}",
                "text": line["caption"],
                "size": 42,
                "font": "bold",
                "color": "#F5F7FF",
            }
        )

    manifest = {
        "colors": spec["colors"],
        "items": [render_text_item(item, index) for index, item in enumerate(items, start=1)],
    }
    (ASSETS / "text-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    render_background()
    print(f"Generated {len(manifest['items'])} text assets and background.jpg")


if __name__ == "__main__":
    main()
