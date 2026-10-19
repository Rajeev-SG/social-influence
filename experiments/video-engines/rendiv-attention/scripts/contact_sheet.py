"""Extract one representative frame from every scene into a labelled contact sheet."""
from pathlib import Path
import json
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
TIMING = json.loads((ROOT / "src" / "timing.json").read_text())
scenes = []
for cue in TIMING["cues"]:
    if not scenes or scenes[-1][0] != cue["scene"]:
        scenes.append([cue["scene"], cue["start"], cue["start"]])
    scenes[-1][2] = cue["end"]

frames = []
with tempfile.TemporaryDirectory(prefix="rendiv-contact-") as tmp:
    tmpdir = Path(tmp)
    for index, (name, start, end) in enumerate(scenes):
        at = start + (end - start) * 0.46
        frame_path = tmpdir / f"{index:02d}.png"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{at:.3f}", "-i", str(OUT / "final.mp4"), "-frames:v", "1",
            "-vf", "scale=270:480", str(frame_path),
        ], check=True)
        frames.append((name, at, Image.open(frame_path).convert("RGB")))

font_path = ROOT / "assets" / "fonts" / "Mono.ttf"
font = ImageFont.truetype(str(font_path), 18)
tile_w, tile_h, label_h = 270, 480, 42
sheet = Image.new("RGB", (tile_w * 4, (tile_h + label_h) * 2), "#0a1118")
draw = ImageDraw.Draw(sheet)
for index, (name, at, image) in enumerate(frames):
    x = (index % 4) * tile_w
    y = (index // 4) * (tile_h + label_h)
    draw.rectangle((x, y, x + tile_w, y + label_h), fill="#12232d")
    draw.text((x + 12, y + 11), f"{at:05.2f}s / {name}", fill="#72f0d2", font=font)
    sheet.paste(image, (x, y + label_h))
sheet.save(OUT / "contact-sheet.jpg", quality=94, subsampling=0)
print(OUT / "contact-sheet.jpg")
