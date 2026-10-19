#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h}"
PYTHON="$ROOT/.venv/bin/python"

mkdir -p "$ROOT/assets/audio" "$ROOT/deliverables" "$ROOT/.review"

if [[ "${1:-}" != "--skip-audio" ]]; then
  node "$ROOT/scripts/narrate.cjs"
  "$PYTHON" "$ROOT/scripts/soundscape.py"
  "$PYTHON" - "$ROOT/assets/audio/narration-raw.wav" "$ROOT/assets/audio/narration.wav" <<'PY'
import subprocess
import sys

subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", sys.argv[1],
    "-af", "highpass=f=72,lowpass=f=11500,acompressor=threshold=0.14:ratio=2.1:attack=14:release=170:makeup=1.25,loudnorm=I=-17:TP=-2:LRA=8",
    "-ar", "48000", "-ac", "2", sys.argv[2],
], check=True)
PY
fi

"$PYTHON" "$ROOT/src/render_video.py" \
  --output "$ROOT/deliverables/final.mp4" \
  --fps 30 \
  --crf 18

python3 "$ROOT/skills/ffmpeg-skill/scripts/proxy.py" \
  "$ROOT/deliverables/final.mp4" \
  --width 540 \
  --quality 29 \
  --output "$ROOT/deliverables/preview.mp4" \
  --overwrite

python3 "$ROOT/skills/ffmpeg-skill/scripts/probe.py" \
  "$ROOT/deliverables/final.mp4" "$ROOT/deliverables/preview.mp4" \
  --compact
