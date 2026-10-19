#!/usr/bin/env python3
"""Create a labeled contact sheet from deterministic Lottie render frames."""

from __future__ import annotations

import json
import math
import argparse
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SELECTED_FRACTIONS = [
    (0.000, "Opening"),
    (0.040, "Hook"),
    (0.130, "Storyteller analogy"),
    (0.255, "Predict next piece"),
    (0.365, "Plausible candidates"),
    (0.465, "Confident claim"),
    (0.560, "Story / fact diverge"),
    (0.665, "Verified fact"),
    (0.755, "Pattern gets thin"),
    (0.815, "Plausible invention"),
    (0.905, "Plausible is not true"),
    (0.985, "Check important claims"),
]


def frame_path(frames_dir: Path, frame: int) -> Path:
    return frames_dir / f"frame-{frame:05d}.jpg"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default=str(ROOT / "deliverables" / "final.mp4"))
    parser.add_argument("--output", default=str(ROOT / "deliverables" / "contact-sheet.jpg"))
    args = parser.parse_args()
    video = Path(args.video).resolve()
    output = Path(args.output).resolve()
    summary = json.loads((ROOT / "src" / "lottie-summary.json").read_text())
    selected = [
        (
            min(summary["totalFrames"] - 1, round(fraction * summary["totalFrames"])),
            label,
        )
        for fraction, label in SELECTED_FRACTIONS
    ]
    selected = list(dict.fromkeys(selected))

    frames_dir = ROOT / ".render-tmp" / "final-contact-frames"
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    for frame, _ in selected:
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(video),
                "-vf",
                f"select=eq(n\\,{frame}),format=rgb24",
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(frame_path(frames_dir, frame)),
            ],
            check=True,
        )

    columns = 3
    rows = math.ceil(len(selected) / columns)
    thumb_w, thumb_h = 420, 747
    label_h = 54
    margin = 22
    header_h = 86
    cell_h = thumb_h + label_h
    width = margin * 2 + columns * thumb_w + (columns - 1) * margin
    height = header_h + margin + rows * cell_h + (rows - 1) * margin + margin
    sheet = Image.new("RGB", (width, height), "#08111F")
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(FONT_PATH, 38)
    label_font = ImageFont.truetype(FONT_PATH, 24)
    draw.text(
        (margin, 22),
        "Why does AI hallucinate?  |  Lottie-web scene review",
        font=title_font,
        fill="#F5F7FF",
    )

    for index, (frame, label) in enumerate(selected):
        row, column = divmod(index, columns)
        x = margin + column * (thumb_w + margin)
        y = header_h + margin + row * (cell_h + margin)
        image = Image.open(frame_path(frames_dir, frame)).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
        draw.rectangle(
            (x, y + thumb_h, x + thumb_w, y + thumb_h + label_h),
            fill="#10283C",
        )
        draw.text(
            (x + 14, y + thumb_h + 13),
            f"{frame / summary['fps']:.2f}s  {label}",
            font=label_font,
            fill="#F5F7FF",
        )
        draw.rectangle(
            (x, y, x + thumb_w - 1, y + thumb_h + label_h - 1),
            outline="#31506A",
            width=2,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92, optimize=True, subsampling=0)
    shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"Wrote {output} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
