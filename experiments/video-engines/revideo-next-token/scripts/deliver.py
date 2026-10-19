"""Create the final master, small review copy, and representative contact sheet."""

from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".review" / "revideo-master.mp4"
OUT = ROOT / "deliverables"
OUT.mkdir(parents=True, exist_ok=True)


def run(*args):
    subprocess.run(args, check=True)


run(
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-i", str(SOURCE),
    "-i", str(ROOT / "assets" / "audio" / "narration.wav"),
    "-i", str(ROOT / "assets" / "audio" / "soundscape.wav"),
    "-filter_complex",
    "[1:a]volume=1.0,aformat=channel_layouts=stereo[voice];"
    "[2:a]volume=0.32,aformat=channel_layouts=stereo[bed];"
    "[voice][bed]amix=inputs=2:duration=longest:normalize=0,"
    "loudnorm=I=-16:TP=-1.5:LRA=8[mix]",
    "-map", "0:v:0", "-map", "[mix]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    "-movflags", "+faststart",
    str(OUT / "final.mp4"),
)
run(
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-i", str(OUT / "final.mp4"),
    "-vf", "scale=540:960",
    "-c:v", "libx264", "-crf", "24", "-preset", "medium", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "96k",
    "-movflags", "+faststart",
    str(OUT / "preview.mp4"),
)

shots = [
    ("Hook", 1.2),
    ("Context", 4.8),
    ("Scoring", 7.8),
    ("Weighted ballot", 11.0),
    ("Choose", 13.8),
    ("Append", 16.0),
    ("Repeat", 18.2),
    ("Likely ≠ truth", 19.6),
]
tile_w, tile_h, band = 270, 480, 42
sheet = Image.new("RGB", (tile_w * 4, (tile_h + band) * 2), "#071117")
draw = ImageDraw.Draw(sheet)
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
font = ImageFont.truetype(font_path, 18)
for index, (label, timestamp) in enumerate(shots):
    frame = ROOT / ".review" / f"contact-{index:02d}.png"
    run(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(timestamp), "-i", str(OUT / "final.mp4"),
        "-frames:v", "1", "-vf", f"scale={tile_w}:{tile_h}", str(frame)
    )
    x = (index % 4) * tile_w
    y = (index // 4) * (tile_h + band)
    sheet.paste(Image.open(frame), (x, y + band))
    draw.text((x + 10, y + 10), f"{timestamp:04.1f}s  {label}", fill="#78E8D8", font=font)
sheet.save(OUT / "contact-sheet.jpg", quality=94, subsampling=0)
print(OUT / "final.mp4")
print(OUT / "preview.mp4")
print(OUT / "contact-sheet.jpg")
