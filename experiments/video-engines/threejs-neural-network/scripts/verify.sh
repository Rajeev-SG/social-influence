#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="${1:-$ROOT/deliverables/final.mp4}"

echo "FILE=$FILE"
ffprobe -v error -show_entries format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels -of json "$FILE"
ffmpeg -v error -i "$FILE" -map 0:v:0 -f null -
ffmpeg -hide_banner -i "$FILE" -map 0:a:0 -af volumedetect -f null - 2>&1 | grep -E 'mean_volume|max_volume'
echo "DECODE_OK"
