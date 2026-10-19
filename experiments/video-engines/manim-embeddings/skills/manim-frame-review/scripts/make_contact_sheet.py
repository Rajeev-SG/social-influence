#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a 4x4 PNG contact sheet from Manim frames."
    )
    parser.add_argument(
        "image_dir",
        help="Directory containing PNG frames (e.g., media/images/foo).",
    )
    parser.add_argument(
        "--scene-name",
        default=None,
        help="Scene name (used for output filename if --output not specified).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output PNG filename (default: <scene_name>_sheet.png or contact_sheet.png).",
    )
    parser.add_argument(
        "--grid",
        default="4x4",
        help="Grid size as COLSxROWS (default: 4x4).",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=320,
        help="Max width per cell (default: 320).",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=None,
        help="Frames per second (for timing info).",
    )
    parser.add_argument(
        "--grid-color",
        default="808080",
        help="Grid line color as hex (default: 808080 for mid-gray).",
    )
    parser.add_argument(
        "--label-size",
        type=int,
        default=12,
        help="Font size for frame labels and timing (default: 12).",
    )
    return parser.parse_args()


def parse_grid(grid: str) -> tuple[int, int]:
    try:
        cols_str, rows_str = grid.lower().split("x")
        cols = int(cols_str)
        rows = int(rows_str)
    except ValueError as exc:
        raise ValueError("Grid must be in COLSxROWS format, e.g., 4x4.") from exc
    if cols <= 0 or rows <= 0:
        raise ValueError("Grid dimensions must be positive.")
    return cols, rows


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def main() -> int:
    args = parse_args()
    cols, rows = parse_grid(args.grid)
    image_dir = Path(args.image_dir)
    if not image_dir.is_dir():
        raise SystemExit(f"Image directory not found: {image_dir}")

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ModuleNotFoundError:
        Image = None

    frames = sorted(image_dir.glob("*.png"))
    if not frames:
        raise SystemExit(f"No PNG frames found in {image_dir}")

    total = cols * rows
    if len(frames) < total:
        indices = list(range(len(frames)))
    else:
        step = (len(frames) - 1) / (total - 1) if total > 1 else 1
        indices = [int(round(i * step)) for i in range(total)]

    selected = [frames[i] for i in indices]
    selected_indices = indices

    # Determine output filename
    if args.output:
        output_filename = args.output
    elif args.scene_name:
        output_filename = f"{args.scene_name}_sheet.png"
    else:
        output_filename = "contact_sheet.png"

    output_path = image_dir / output_filename

    if Image is None:
        magick = shutil.which("magick")
        montage = shutil.which("montage")
        if magick:
            cmd = [magick, "montage"]
        elif montage:
            cmd = [montage]
        else:
            raise SystemExit(
                "Pillow not installed and ImageMagick not found (magick/montage)."
            )
        print("Warning: Pillow not available, using ImageMagick fallback (no gridlines or labels).", file=sys.stderr)
        geometry = f"{args.max_width}x{args.max_width}+0+0"
        cmd.extend(str(path) for path in selected)
        cmd.extend(["-tile", f"{cols}x{rows}", "-geometry", geometry, str(output_path)])
        subprocess.run(cmd, check=True)
        print(f"Wrote contact sheet: {output_path.resolve()}")
        return 0

    images = [Image.open(path).convert("RGB") for path in selected]
    cell_w = min(args.max_width, max(im.width for im in images))
    scale_factors = [cell_w / im.width for im in images]
    resized = []
    for im, scale in zip(images, scale_factors):
        new_w = max(1, int(im.width * scale))
        new_h = max(1, int(im.height * scale))
        resized.append(im.resize((new_w, new_h), Image.LANCZOS))

    cell_h = max(im.height for im in resized)
    label_height = args.label_size + 8  # Space for filename and timing
    grid_line_width = 1

    sheet_w = cols * cell_w + (cols + 1) * grid_line_width
    sheet_h = rows * (cell_h + label_height) + (rows + 1) * grid_line_width

    sheet = Image.new("RGB", (sheet_w, sheet_h), color=(16, 16, 16))
    draw = ImageDraw.Draw(sheet)

    # Try to load a decent font, fall back to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", args.label_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", args.label_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    grid_color = hex_to_rgb(args.grid_color)

    # Draw grid lines and paste images
    for idx, im in enumerate(resized):
        row = idx // cols
        col = idx % cols

        # Calculate cell position
        cell_x = col * cell_w + (col + 1) * grid_line_width
        cell_y = row * (cell_h + label_height) + (row + 1) * grid_line_width

        # Center image in cell
        x = cell_x + (cell_w - im.width) // 2
        y = cell_y + (cell_h - im.height) // 2
        sheet.paste(im, (x, y))

        # Draw filename and timing below image
        frame_idx = selected_indices[idx]
        frame_name = selected[idx].name
        label_y = cell_y + cell_h + 2

        # Build label text
        label_text = frame_name
        if args.fps:
            time_sec = frame_idx / args.fps
            label_text += f" ({time_sec:.2f}s)"

        # Draw filename with optional timing (in white)
        draw.text((cell_x + 2, label_y), label_text, font=font, fill=(255, 255, 255))

    # Draw vertical grid lines
    for col in range(cols + 1):
        x = col * cell_w + col * grid_line_width
        draw.rectangle([(x, 0), (x + grid_line_width - 1, sheet_h)], fill=grid_color)

    # Draw horizontal grid lines
    for row in range(rows + 1):
        y = row * (cell_h + label_height) + row * grid_line_width
        draw.rectangle([(0, y), (sheet_w, y + grid_line_width - 1)], fill=grid_color)

    sheet.save(output_path)
    print(f"Wrote contact sheet: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
