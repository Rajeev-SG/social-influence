from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "deliverables/final.mp4"
PREVIEW = ROOT / "deliverables/preview.mp4"
SHEET_JPG = ROOT / "deliverables/contact-sheet.jpg"
SKILL = ROOT / "skills/ffmpeg-skill/scripts"
CONTACT_TIMES = (0.70, 3.45, 6.15, 8.75, 11.25, 15.35, 18.90, 21.15)


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    review = ROOT / ".review"
    review.mkdir(exist_ok=True)
    run(sys.executable, str(SKILL / "probe.py"), str(FINAL), str(PREVIEW), "--json")
    run(
        sys.executable,
        str(SKILL / "check.py"),
        str(FINAL),
        "--platform",
        "custom",
        "--max-duration",
        "25",
        "--aspect",
        "9:16",
        "--lufs",
        "-16",
        "--tp",
        "-1.5",
        "--content",
        "--json",
    )
    frame_base = review / "contact-frame"
    args = [
        sys.executable,
        str(SKILL / "look.py"),
        str(FINAL),
        "--no-timecode",
    ]
    for at in CONTACT_TIMES:
        args.extend(("--at", f"{at:.2f}"))
    args.extend(("--output", str(frame_base), "--json"))
    run(*args)

    frame_paths = [review / f"contact-frame_{at:.3f}s.png" for at in CONTACT_TIMES]
    frames = [Image.open(path).convert("RGB") for path in frame_paths]
    tile_w, tile_h = 540, 960
    sheet = Image.new("RGB", (tile_w * 4, tile_h * 2), (17, 22, 26))
    label_font = ImageFont.truetype(str(ROOT / "assets/fonts/Mono.ttf"), 22)
    for i, (frame, at) in enumerate(zip(frames, CONTACT_TIMES)):
        frame.thumbnail((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (i % 4) * tile_w
        y = (i // 4) * tile_h
        sheet.paste(frame, (x, y))
        ImageDraw.Draw(sheet).rectangle((x + 10, y + 10, x + 135, y + 44), fill=(4, 10, 15))
        ImageDraw.Draw(sheet).text((x + 20, y + 16), f"{at:05.2f}s", font=label_font, fill=(242, 241, 234))
    sheet.save(SHEET_JPG, quality=92, optimize=True)
    for frame, path in zip(frames, frame_paths):
        frame.close()
        path.unlink()

    probe = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(FINAL)],
            cwd=ROOT,
            text=True,
        )
    )
    (review / "final-probe.json").write_text(json.dumps(probe, indent=2) + "\n")
    print(f"CONTACT_SHEET={SHEET_JPG}")


if __name__ == "__main__":
    main()
