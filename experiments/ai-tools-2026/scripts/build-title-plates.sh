#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FONT="$ROOT/assets/fonts/Manrope.ttf"
OUT="$ROOT/assets/diffusion"

mkdir -p "$OUT"

magick -size 1080x1920 xc:none \
  -font "$FONT" \
  -pointsize 112 \
  -fill '#EAF6FF' \
  -draw "text 100,330 'THE MOST USED'" \
  -draw "text 100,455 'AI TOOLS OF 2026'" \
  -fill '#FFB45C' \
  -pointsize 36 \
  -draw "text 235,760 'AND WHAT MAKES EACH DIFFERENT'" \
  -background '#071018' \
  -flatten \
  "$OUT/title-plate.png"

magick -size 1080x1920 xc:none \
  -font "$FONT" \
  -pointsize 118 \
  -fill '#EAF6FF' \
  -draw "text 160,760 'MATCH THE TOOL'" \
  -draw "text 160,890 'TO THE TASK.'" \
  -fill '#68E0FF' \
  -pointsize 34 \
  -draw "text 245,1160 'THE MOST USED AI TOOLS OF 2026'" \
  -background '#071018' \
  -flatten \
  "$OUT/closing-plate.png"
