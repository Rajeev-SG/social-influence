#!/usr/bin/env python3
"""Verify the final deliverables decode and match the requested media contract."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def probe(path: Path) -> dict:
    return json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)))


def decode(path: Path) -> dict:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"],
        text=True,
        capture_output=True,
    )
    return {"returncode": result.returncode, "stderr": result.stderr}


def stream(probe_result: dict, codec_type: str) -> dict:
    return next(stream for stream in probe_result["streams"] if stream["codec_type"] == codec_type)


def main() -> None:
    final = OUT / "final.mp4"
    preview = OUT / "preview.mp4"
    contact = OUT / "contact-sheet.jpg"
    final_probe = probe(final)
    preview_probe = probe(preview)
    contact_probe = probe(contact)
    final_video = stream(final_probe, "video")
    final_audio = stream(final_probe, "audio")
    preview_video = stream(preview_probe, "video")
    preview_audio = stream(preview_probe, "audio")
    contact_video = stream(contact_probe, "video")
    checks = {
        "final_exists": final.exists(),
        "preview_exists": preview.exists(),
        "contact_sheet_exists": contact.exists(),
        "final_decode": decode(final),
        "preview_decode": decode(preview),
        "contact_decode": decode(contact),
        "final_video": {
            "codec": final_video.get("codec_name"),
            "width": final_video.get("width"),
            "height": final_video.get("height"),
            "pix_fmt": final_video.get("pix_fmt"),
            "avg_frame_rate": final_video.get("avg_frame_rate"),
            "r_frame_rate": final_video.get("r_frame_rate"),
            "frames": final_video.get("nb_frames"),
            "duration": final_video.get("duration"),
        },
        "final_audio": {
            "codec": final_audio.get("codec_name"),
            "sample_rate": final_audio.get("sample_rate"),
            "channels": final_audio.get("channels"),
            "duration": final_audio.get("duration"),
        },
        "preview_video": {
            "codec": preview_video.get("codec_name"),
            "width": preview_video.get("width"),
            "height": preview_video.get("height"),
            "pix_fmt": preview_video.get("pix_fmt"),
            "avg_frame_rate": preview_video.get("avg_frame_rate"),
            "frames": preview_video.get("nb_frames"),
        },
        "preview_audio": {
            "codec": preview_audio.get("codec_name"),
            "sample_rate": preview_audio.get("sample_rate"),
            "channels": preview_audio.get("channels"),
        },
        "contact_sheet": {
            "codec": contact_video.get("codec_name"),
            "width": contact_video.get("width"),
            "height": contact_video.get("height"),
        },
    }
    expected = (
        checks["final_exists"]
        and checks["preview_exists"]
        and checks["contact_sheet_exists"]
        and checks["final_decode"]["returncode"] == 0
        and checks["preview_decode"]["returncode"] == 0
        and checks["contact_decode"]["returncode"] == 0
        and checks["final_video"]["codec"] == "h264"
        and checks["final_video"]["width"] == 1080
        and checks["final_video"]["height"] == 1920
        and checks["final_video"]["pix_fmt"] == "yuv420p"
        and checks["final_video"]["avg_frame_rate"] == "30/1"
        and checks["final_audio"]["codec"] == "aac"
        and checks["final_audio"]["sample_rate"] == "48000"
        and checks["final_audio"]["channels"] == 2
    )
    checks["contract_pass"] = bool(expected)
    print(json.dumps(checks, indent=2))
    if not expected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
