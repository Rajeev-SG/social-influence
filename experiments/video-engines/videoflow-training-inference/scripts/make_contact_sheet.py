#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default=str(ROOT / "deliverables" / "final.mp4"))
    parser.add_argument("--timing", default=str(ROOT / "assets" / "audio" / "timing.json"))
    parser.add_argument("--work-dir", default=str(ROOT / ".render" / "inspection"))
    parser.add_argument(
        "--output",
        default=str(ROOT / "deliverables" / "contact-sheet.jpg"),
    )
    args = parser.parse_args()

    timing = json.loads(Path(args.timing).read_text(encoding="utf-8"))
    total = float(timing["total_duration"])
    scenes = {scene["id"]: scene for scene in timing["scenes"]}
    samples = [
        ("Opening", 0.18),
        ("Training examples", scenes["training"]["start"] + 0.65),
        ("Training adjust", scenes["training"]["start"] + 2.65),
        ("Recipe fixed", scenes["transition"]["start"] + 1.15),
        ("Inference input", scenes["inference"]["start"] + 0.75),
        ("Inference output", scenes["inference"]["start"] + 2.65),
        ("Takeaway", scenes["outro"]["start"] + 0.65),
        ("Ending", max(0.0, total - 0.18)),
    ]

    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    frame_paths: list[tuple[str, Path]] = []
    for index, (label, timestamp) in enumerate(samples, start=1):
        frame_path = work_dir / f"inspect-{index:02d}.jpg"
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-ss",
                f"{timestamp:.4f}",
                "-i",
                args.video,
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(frame_path),
            ],
            check=True,
        )
        frame_paths.append((f"{index:02d}  {label}", frame_path))

    tile_w, tile_h = 270, 480
    label_h = 58
    sheet = Image.new("RGB", (tile_w * 4, (tile_h + label_h) * 2), (7, 15, 28))
    draw = ImageDraw.Draw(sheet)
    for index, (label, frame_path) in enumerate(frame_paths):
        frame = Image.open(frame_path).convert("RGB").resize(
            (tile_w, tile_h), Image.Resampling.LANCZOS
        )
        x = (index % 4) * tile_w
        y = (index // 4) * (tile_h + label_h)
        sheet.paste(frame, (x, y))
        draw.rectangle((x, y + tile_h, x + tile_w, y + tile_h + label_h), fill=(12, 28, 46))
        draw.text((x + 14, y + tile_h + 14), label, font=font(19), fill=(238, 245, 251))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92, subsampling=1)
    print(output)


if __name__ == "__main__":
    main()
