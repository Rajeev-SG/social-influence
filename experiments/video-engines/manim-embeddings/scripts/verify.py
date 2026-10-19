"""Decode and verify the delivered media with FFmpeg/FFprobe."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODE = sys.argv[1] if len(sys.argv) > 1 else "final"
OUT = ROOT / "deliverables"


def probe(path: Path):
    raw = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels",
            "-of", "json", str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def decode(path: Path):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
        check=True,
    )


def audio_metrics(path: Path):
    raw = subprocess.check_output(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
            "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-",
        ],
        stderr=subprocess.STDOUT,
        text=True,
    )
    keep = [line.strip() for line in raw.splitlines() if any(key in line for key in ("Integrated loudness", "True peak", "LRA:", "Peak:"))]
    return keep[-12:]


def main():
    files = [OUT / "review.mp4"] if MODE == "review" else [OUT / "final.mp4", OUT / "preview.mp4"]
    results = {}
    for path in files:
        decode(path)
        results[path.name] = {
            "probe": probe(path),
            "audio_metrics": audio_metrics(path),
        }
    if MODE == "final":
        contact = OUT / "contact-sheet.jpg"
        with contact.open("rb") as handle:
            if handle.read(2) != b"\xff\xd8":
                raise RuntimeError("contact-sheet.jpg is not a JPEG")
        results[contact.name] = {"bytes": contact.stat().st_size}
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
