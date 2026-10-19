#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FINAL="$ROOT/deliverables/final.mp4"

ffprobe -v error -show_entries \
  format=format_name,duration,size,bit_rate:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels,channel_layout \
  -of json "$FINAL"
ffmpeg -hide_banner -v error -xerror -i "$FINAL" -f null -
echo "FULL_DECODE_OK"
ffmpeg -hide_banner -i "$FINAL" -map 0:a -af ebur128=peak=true -f null - 2>&1 | tail -22

