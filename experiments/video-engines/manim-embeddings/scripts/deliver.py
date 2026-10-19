"""Mix narration and sound design, encode deliverables, and build a contact sheet."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
PICTURE = Path(sys.argv[1]).resolve()
MODE = sys.argv[2] if len(sys.argv) > 2 else "final"


def run(*args: str):
    subprocess.run(args, check=True)


def font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audio = ROOT / "assets/audio"
    normalized = audio / "narration.wav"
    mixed = audio / "mix.wav"

    run(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(audio / "narration-raw.wav"),
        "-af", "highpass=f=75,lowpass=f=11000,acompressor=threshold=0.12:ratio=2:attack=15:release=180:makeup=1.15,loudnorm=I=-17:TP=-2:LRA=8",
        "-ar", "48000", "-ac", "2", str(normalized),
    )
    run(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(normalized), "-i", str(audio / "soundscape.wav"),
        "-filter_complex",
        "[0:a]volume=1.0[voice];[1:a]volume=0.48[sfx];[voice][sfx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.94,loudnorm=I=-16:TP=-1.5:LRA=8[out]",
        "-map", "[out]", "-ar", "48000", "-ac", "2", str(mixed),
    )

    if MODE == "final":
        final = OUT / "final.mp4"
        preview = OUT / "preview.mp4"
        run(
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(PICTURE), "-i", str(mixed),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(final),
        )
        run(
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(final), "-vf", "scale=540:960",
            "-c:v", "libx264", "-crf", "25", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
            "-movflags", "+faststart", str(preview),
        )
    else:
        final = OUT / "review.mp4"
        run(
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(PICTURE), "-i", str(mixed),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(final),
        )

    timing = json.loads((ROOT / "src/timing.json").read_text())
    frames = [
        ("Hook", timing["cues"][0]["start"] + 0.85),
        ("Coordinates", timing["cues"][1]["start"] + 2.25),
        ("Neighbourhood", timing["cues"][2]["start"] + 2.65),
        ("Distance", timing["cues"][3]["start"] + 1.85),
        ("Ending", timing["cues"][4]["start"] + 1.15),
    ]
    panel_w, panel_h, band = 320, 568, 38
    sheet = Image.new("RGB", (panel_w * 3, (panel_h + band) * 2), "#07111B")
    draw = ImageDraw.Draw(sheet)
    label_font = font(14)
    with tempfile.TemporaryDirectory() as temp:
        for index, (label, timestamp) in enumerate(frames):
            frame_path = Path(temp) / f"{index}.png"
            run(
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{timestamp:.3f}", "-i", str(final), "-frames:v", "1",
                "-vf", f"scale={panel_w}:{panel_h}", str(frame_path),
            )
            x = (index % 3) * panel_w
            y = (index // 3) * (panel_h + band)
            sheet.paste(Image.open(frame_path), (x, y + band))
            draw.text((x + 9, y + 10), f"{timestamp:05.2f}s  {label}", fill="#76F7D2", font=label_font)
            draw.rectangle((x, y + band, x + panel_w - 1, y + band + panel_h - 1), outline="#1D3442", width=1)
    sheet.save(OUT / "contact-sheet.jpg", quality=94, subsampling=0)

    print(json.dumps({"mode": MODE, "video": str(final), "mixed_audio": str(mixed), "contact_sheet": str(OUT / "contact-sheet.jpg")}))


if __name__ == "__main__":
    main()
