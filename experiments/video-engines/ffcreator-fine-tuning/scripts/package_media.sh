#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RENDER="$ROOT/.review"
OUT="$ROOT/deliverables"
mkdir -p "$OUT"

ffmpeg -hide_banner -loglevel error -y \
  -i "$OUT/final.mp4" \
  -vf "scale=540:960" \
  -c:v libx264 -preset veryfast -crf 28 \
  -pix_fmt yuv420p \
  -c:a aac -b:a 96k \
  -movflags +faststart \
  "$OUT/preview.mp4"

ffmpeg -hide_banner -loglevel error -y \
  -i "$RENDER/frames/02-01.60.jpg" \
  -i "$RENDER/frames/04-05.60.jpg" \
  -i "$RENDER/frames/06-11.80.jpg" \
  -i "$RENDER/frames/08-17.35.jpg" \
  -i "$RENDER/frames/10-22.55.jpg" \
  -filter_complex "[0:v]scale=320:568[a0];[1:v]scale=320:568[a1];[2:v]scale=320:568[a2];[3:v]scale=320:568[a3];[4:v]scale=320:568[a4];[a0][a1][a2][a3][a4]concat=n=5:v=1:a=0,tile=3x2:padding=10:margin=10:color=0x07151B[out]" \
  -map "[out]" -frames:v 1 -q:v 2 \
  "$OUT/contact-sheet.jpg"

echo "wrote $OUT/preview.mp4 and $OUT/contact-sheet.jpg"
