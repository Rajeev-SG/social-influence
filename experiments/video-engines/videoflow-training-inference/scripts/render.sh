#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/videoflow ]]; then
  echo "Missing .venv; run scripts/setup.sh first." >&2
  exit 1
fi
if [[ ! -f assets/audio/mix.wav || ! -f assets/audio/timing.json ]]; then
  echo "Missing generated audio; run scripts/generate_audio.mjs and scripts/build_audio.py first." >&2
  exit 1
fi

read -r TOTAL_FRAMES TOTAL_DURATION < <(.venv/bin/python - <<'PY'
import json
from pathlib import Path
timing = json.loads(Path("assets/audio/timing.json").read_text())
print(timing["total_frames"], timing["total_duration"])
PY
)

rm -rf .render/frames .render/frame-events.jsonl .render/frame-manifest.json
mkdir -p .render/frames deliverables

NATS_CONTAINER="vf-training-inference-nats"
cleanup() {
  docker rm -f "$NATS_CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup
docker run -d --name "$NATS_CONTAINER" -p 4222:4222 nats:2.12-alpine -js >/dev/null
.venv/bin/python - <<'PY'
import socket
import time
for attempt in range(40):
    try:
        with socket.create_connection(("127.0.0.1", 4222), timeout=0.5) as connection:
            if connection.recv(64).startswith(b"INFO"):
                raise SystemExit(0)
    except OSError:
        pass
    time.sleep(0.25)
raise SystemExit("NATS did not become ready on 127.0.0.1:4222")
PY

echo "VideoFlow graph render: ${TOTAL_FRAMES} frames / ${TOTAL_DURATION}s"
VF_START="$(python3 - <<'PY'
import time
print(time.time())
PY
)"
VF_TOTAL_FRAMES="$TOTAL_FRAMES" \
VF_OUTPUT_DIR="$ROOT/.render/frames" \
VF_MANIFEST_PATH="$ROOT/.render/frame-manifest.json" \
VF_TIMING_PATH="$ROOT/assets/audio/timing.json" \
  .venv/bin/videoflow run-local --non-interactive --no-prepare --no-restart --no-redis \
    --no-infra --nats nats://127.0.0.1:4222 src/render_flow.py
VF_END="$(python3 - <<'PY'
import time
print(time.time())
PY
)"
VF_SECONDS="$(python3 - "$VF_START" "$VF_END" <<'PY'
import sys
print(f"{float(sys.argv[2]) - float(sys.argv[1]):.3f}"
)
PY
)"
echo "VideoFlow graph render completed in ${VF_SECONDS}s"

FFMPEG_START="$(python3 - <<'PY'
import time
print(time.time())
PY
)"
ffmpeg -hide_banner -loglevel error -y \
  -framerate 30 -i .render/frames/frame_%05d.jpg \
  -i assets/audio/mix.wav \
  -map 0:v:0 -map 1:a:0 \
  -t "$TOTAL_DURATION" \
  -vf "scale=in_range=full:out_range=tv,format=yuv420p" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -color_range tv \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  deliverables/final.mp4
FFMPEG_END="$(python3 - <<'PY'
import time
print(time.time())
PY
)"
FFMPEG_SECONDS="$(python3 - "$FFMPEG_START" "$FFMPEG_END" <<'PY'
import sys
print(f"{float(sys.argv[2]) - float(sys.argv[1]):.3f}")
PY
)"
echo "FFmpeg encode completed in ${FFMPEG_SECONDS}s"

ffmpeg -hide_banner -loglevel error -y \
  -i deliverables/final.mp4 \
  -vf "scale=540:960:flags=lanczos:in_range=full:out_range=tv,format=yuv420p" \
  -r 30 \
  -c:v libx264 -preset veryfast -crf 28 -pix_fmt yuv420p \
  -color_range tv \
  -c:a aac -b:a 128k -ar 48000 -ac 2 \
  -movflags +faststart \
  deliverables/preview.mp4

echo "RENDER_TIMING videoflow_seconds=$VF_SECONDS ffmpeg_seconds=$FFMPEG_SECONDS total_seconds=$(python3 - "$VF_SECONDS" "$FFMPEG_SECONDS" <<'PY'
import sys
print(f"{float(sys.argv[1]) + float(sys.argv[2]):.3f}"
)
PY
)"
