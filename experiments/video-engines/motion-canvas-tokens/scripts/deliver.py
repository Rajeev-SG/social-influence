"""Encode Motion Canvas PNG frames with the mixed audio and build review artifacts."""
from pathlib import Path
import json
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
OUT.mkdir(exist_ok=True)

def run(*args):
    subprocess.run([str(a) for a in args], check=True)

frame_files = sorted((ROOT / "output").glob("**/*.png"))
if not frame_files:
    raise SystemExit("no Motion Canvas PNG frames found under output/")
frame_dir = frame_files[0].parent
first = frame_files[0].name
if not first.rsplit('.', 1)[0].isdigit():
    raise SystemExit(f"unexpected frame name: {first}")
width = len(first.rsplit('.', 1)[0])
pattern = f"%0{width}d.png"

final = OUT / "final.mp4"
run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30", "-i", frame_dir / pattern,
    "-i", ROOT / "assets/audio/mix.wav", "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", final)

preview = OUT / "preview.mp4"
run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", final,
    "-vf", "scale=540:960", "-c:v", "libx264", "-preset", "medium", "-crf", "24",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", preview)

times = [0.65, 3.45, 5.55, 8.25, 10.55, 13.35, 15.65, 18.15, 20.85, 23.05]
labels = [
    "Hook: sentence ribbon", "Tokenizer gate", "Split: reusable pieces", "Examples: word fragments",
    "Examples: punctuation", "IDs: model-ready values", "IDs: mapping", "Bridge: text to chunks",
    "Bridge: chunks to IDs", "Takeaway: the handoff",
]
w, h, band = 300, 533, 42
sheet = Image.new("RGB", (w * 5, (h + band) * 2), "#0a0f14")
draw = ImageDraw.Draw(sheet)
font_path = ROOT / "assets/fonts/Manrope.ttf"
font = ImageFont.truetype(str(font_path), 16)
with tempfile.TemporaryDirectory() as tmp:
    for i, (label, time) in enumerate(zip(labels, times)):
        png = Path(tmp) / f"{i}.png"
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(time), "-i", final,
            "-frames:v", "1", "-vf", f"scale={w}:{h}", png)
        x = (i % 5) * w
        y = (i // 5) * (h + band)
        sheet.paste(Image.open(png), (x, y + band))
        draw.text((x + 10, y + 11), f"{time:05.2f}s / {label}", fill="#75e4cd", font=font)
sheet.save(OUT / "contact-sheet.jpg", quality=94, subsampling=0)

subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration,size,bit_rate",
    "-show_entries", "stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels",
    "-of", "json", str(final),
], check=True)
print(f"wrote {final}\nwrote {preview}\nwrote {OUT / 'contact-sheet.jpg'}")
