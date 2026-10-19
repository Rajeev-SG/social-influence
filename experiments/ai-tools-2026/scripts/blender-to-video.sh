#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER_DIR="$ROOT/assets/blender"

mkdir -p "$BLENDER_DIR/opening-frames" "$BLENDER_DIR/finale-frames"
blender --background "$ROOT/src/blender/ai-tools-2026.blend" --python "$ROOT/src/blender/render.py"

ffmpeg -y \
  -framerate 30 \
  -i "$BLENDER_DIR/opening-frames/frame-%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 16 -preset slow \
  "$BLENDER_DIR/opening.mp4"

ffmpeg -y \
  -framerate 30 \
  -start_number 301 \
  -i "$BLENDER_DIR/finale-frames/frame-%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 16 -preset slow \
  "$BLENDER_DIR/finale.mp4"
