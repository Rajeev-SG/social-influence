#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p .review deliverables
rm -f .review/rendiv-master.mp4 .review/rendiv-render.log .review/render-timing.txt
if [[ ! -x node_modules/ffmpeg-static/ffmpeg ]]; then
  mkdir -p node_modules/ffmpeg-static
  ln -sf "$(command -v ffmpeg)" node_modules/ffmpeg-static/ffmpeg
fi

START="$(python3 - <<'PY'
import time
print(time.time())
PY
)"
set +e
npm exec -- rendiv render src/index.tsx Attention .review/rendiv-master.mp4 \
  --concurrency 4 --image-format png --preset slow --crf 17 --profiling \
  2>&1 | tee .review/rendiv-render.log
RENDER_STATUS=${PIPESTATUS[0]}
set -e
END="$(python3 - <<'PY'
import time
print(time.time())
PY
)"
python3 - "$START" "$END" "$RENDER_STATUS" > .review/render-timing.txt <<'PY'
import sys
start, end, status = map(float, sys.argv[1:])
print(f"rendiv_render_seconds={end-start:.3f}")
print(f"rendiv_render_exit={int(status)}")
PY
if [[ "$RENDER_STATUS" -ne 0 ]]; then
  exit "$RENDER_STATUS"
fi

HAS_AUDIO="$(ffprobe -v error -select_streams a:0 -show_entries stream=index -of csv=p=0 .review/rendiv-master.mp4 || true)"
if [[ -n "$HAS_AUDIO" ]]; then
  ffmpeg -hide_banner -loglevel error -y -i .review/rendiv-master.mp4 \
    -c:v copy -af "loudnorm=I=-16:TP=-1.5:LRA=8" -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart deliverables/final.mp4
else
  ffmpeg -hide_banner -loglevel error -y -i .review/rendiv-master.mp4 \
    -i assets/audio/narration.wav -i assets/audio/soundscape.wav \
    -filter_complex "[1:a][2:a]amix=inputs=2:duration=longest:weights='1 0.34'[mix];[mix]loudnorm=I=-16:TP=-1.5:LRA=8[out]" \
    -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart deliverables/final.mp4
fi
ffmpeg -hide_banner -loglevel error -y -i deliverables/final.mp4 \
  -vf scale=270:480 -c:v libx264 -preset medium -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 96k -movflags +faststart deliverables/preview.mp4
python3 scripts/contact_sheet.py
python3 scripts/verify_media.py
cat .review/render-timing.txt
