#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ffmpeg -y \
  -i "$ROOT/assets/diffusion/diffusion-master.mp4" \
  -loop 1 -framerate 30 \
  -i "$ROOT/assets/diffusion/title-plate.png" \
  -loop 1 -framerate 30 \
  -i "$ROOT/assets/diffusion/closing-plate.png" \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='between(t,0.55,5.25)'[title];[title][2:v]overlay=0:0:enable='between(t,81.15,86.65)'[video]" \
  -map "[video]" \
  -map 0:a:0 \
  -c:v libx264 \
  -crf 16 \
  -preset slow \
  -pix_fmt yuv420p \
  -c:a copy \
  -shortest \
  -movflags +faststart \
  "$ROOT/assets/diffusion/final-with-type.mp4"
