#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ffmpeg -y -hide_banner -loglevel error \
  -i "$ROOT/deliverables/final.mp4" \
  -vf "scale=540:960:flags=lanczos:in_range=full:out_range=tv,format=yuv420p" \
  -c:v libx264 -preset medium -crf 26 \
  -pix_fmt yuv420p -r 30 \
  -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 96k -ar 48000 -ac 2 \
  -movflags +faststart \
  "$ROOT/deliverables/preview.mp4"
echo "Wrote deliverables/preview.mp4"
