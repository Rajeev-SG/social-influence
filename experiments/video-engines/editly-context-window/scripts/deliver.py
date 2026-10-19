#!/usr/bin/env python3
"""Create the review-sized preview and a six-frame contact sheet from final.mp4."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "deliverables" / "final.mp4"
PREVIEW = ROOT / "deliverables" / "preview.mp4"
CONTACT = ROOT / "deliverables" / "contact-sheet.jpg"
FONT = ROOT / "assets" / "fonts" / "Mono.ttf"


def run(args: list[str]) -> None:
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


run([
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-i", str(FINAL),
    "-vf", "scale=540:960:flags=lanczos",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
    "-movflags", "+faststart", str(PREVIEW),
])

frames = [
    ("0.90", "OPEN"),
    ("3.60", "DESK"),
    ("8.10", "FILLS"),
    ("10.70", "TRIM"),
    ("15.50", "NOW"),
    ("19.70", "LIMIT"),
]

with tempfile.TemporaryDirectory(prefix="editly-contact-", dir=str(ROOT / "src")) as temp:
    temp_dir = Path(temp)
    frame_paths = []
    for index, (timestamp, label) in enumerate(frames):
        frame_path = temp_dir / f"{index}-{label}.jpg"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", timestamp, "-i", str(FINAL),
            "-frames:v", "1", "-q:v", "2", str(frame_path),
        ])
        frame_paths.append(frame_path)

    subprocess.run([
        "montage", *map(str, frame_paths),
        "-thumbnail", "360x640",
        "-tile", "3x2",
        "-geometry", "+8+28",
        "-background", "#18232b",
        "-fill", "white",
        "-font", str(FONT),
        "-pointsize", "28",
        "-set", "label", "%t",
        str(CONTACT),
    ], check=True)

print(f"Created {PREVIEW}")
print(f"Created {CONTACT}")

