#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FINAL="$ROOT/deliverables/final.mp4"
PREVIEW="$ROOT/deliverables/preview.mp4"
CONTACT="$ROOT/deliverables/contact-sheet.jpg"

for file in "$FINAL" "$PREVIEW" "$CONTACT"; do
  test -s "$file" || { echo "missing or empty: $file" >&2; exit 1; }
done

ffmpeg -hide_banner -loglevel error -i "$FINAL" -f null -
ffmpeg -hide_banner -loglevel error -i "$PREVIEW" -f null -

python3 - "$FINAL" "$PREVIEW" "$CONTACT" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

final, preview, contact = map(Path, sys.argv[1:])

def probe(path: Path) -> dict:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ])
    return json.loads(raw)

def assert_media(path: Path, width: int, height: int) -> dict:
    data = probe(path)
    streams = {stream["codec_type"]: stream for stream in data["streams"]}
    video, audio = streams.get("video", {}), streams.get("audio", {})
    assert video.get("codec_name") == "h264", (path, video)
    assert video.get("pix_fmt") == "yuv420p", (path, video)
    assert (video.get("width"), video.get("height")) == (width, height), (path, video)
    assert video.get("r_frame_rate") == "30/1", (path, video)
    assert audio.get("codec_name") == "aac", (path, audio)
    assert audio.get("channels") == 2, (path, audio)
    duration = float(data["format"]["duration"])
    assert 15 <= duration <= 25, (path, duration)
    return {
        "durationSeconds": round(duration, 3),
        "video": {
            "codec": video["codec_name"],
            "pixelFormat": video["pix_fmt"],
            "width": video["width"],
            "height": video["height"],
            "frameRate": video["r_frame_rate"],
        },
        "audio": {
            "codec": audio["codec_name"],
            "channels": audio["channels"],
            "sampleRate": int(audio["sample_rate"]),
        },
        "sizeBytes": path.stat().st_size,
    }

final_data = assert_media(final, 1080, 1920)
preview_data = assert_media(preview, 540, 960)
assert preview_data["sizeBytes"] < final_data["sizeBytes"]

from PIL import Image
with Image.open(contact) as image:
    assert image.format == "JPEG", image.format
    assert image.width >= 1200 and image.height >= 2500, image.size
    contact_data = {"width": image.width, "height": image.height, "sizeBytes": contact.stat().st_size}

print(json.dumps({"final": final_data, "preview": preview_data, "contactSheet": contact_data}, indent=2))
PY
