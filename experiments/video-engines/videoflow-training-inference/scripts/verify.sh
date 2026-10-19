#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FINAL=deliverables/final.mp4
PREVIEW=deliverables/preview.mp4

python3 - <<'PY'
import json
import subprocess
from pathlib import Path

root = Path.cwd()
final = root / "deliverables/final.mp4"
preview = root / "deliverables/preview.mp4"
assert final.exists() and preview.exists()

def probe(path):
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ], text=True)
    return json.loads(raw)

data = probe(final)
streams = {stream["codec_type"]: stream for stream in data["streams"]}
video = streams["video"]
audio = streams["audio"]
duration = float(data["format"]["duration"])
checks = {
    "width": int(video["width"]) == 1080,
    "height": int(video["height"]) == 1920,
    "fps": video["r_frame_rate"] == "30/1",
    "duration_15_25s": 15.0 <= duration <= 25.0,
    "h264": video["codec_name"] == "h264",
    "yuv420p": video["pix_fmt"] == "yuv420p",
    "aac": audio["codec_name"] == "aac",
    "stereo": int(audio["channels"]) == 2,
    "audio_48k": int(audio["sample_rate"]) == 48000,
    "preview_smaller": preview.stat().st_size < final.stat().st_size,
}
assert all(checks.values()), checks
print(json.dumps({
    "final": {
        "width": video["width"],
        "height": video["height"],
        "fps": video["r_frame_rate"],
        "duration": duration,
        "video_codec": video["codec_name"],
        "pixel_format": video["pix_fmt"],
        "audio_codec": audio["codec_name"],
        "audio_channels": audio["channels"],
        "audio_sample_rate": audio["sample_rate"],
        "bytes": final.stat().st_size,
    },
    "preview_bytes": preview.stat().st_size,
    "checks": checks,
}, indent=2))
PY

echo "--- full decode check ---"
ffmpeg -hide_banner -loglevel error -i "$FINAL" -f null -
echo "decode=ok"

echo "--- decoded frame count ---"
ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "$FINAL"

echo "--- contact sheet dimensions ---"
python3 - <<'PY'
from PIL import Image
from pathlib import Path
path = Path("deliverables/contact-sheet.jpg")
with Image.open(path) as image:
    print(f"{image.width}x{image.height} {image.format}")
assert path.stat().st_size > 100_000
PY
