#!/bin/zsh
set -euo pipefail
ROOT="${0:A:h:h}"
VARIANT="${1:-final}"
FRAMES="$ROOT/.work/frames-$VARIANT"
OUT="$ROOT/deliverables"
mkdir -p "$OUT"

ffmpeg -hide_banner -loglevel error -y \
  -framerate 30 -i "$FRAMES/frame-%05d.png" \
  -i "$ROOT/assets/audio/mix.wav" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ac 2 -ar 48000 -movflags +faststart \
  -shortest "$OUT/final.mp4"

ffmpeg -hide_banner -loglevel error -y -i "$OUT/final.mp4" \
  -vf "scale=540:960" -c:v libx264 -preset medium -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ac 2 -movflags +faststart "$OUT/preview.mp4"

ffmpeg -hide_banner -loglevel error -y \
  -i "$OUT/final.mp4" \
  -vf "select='eq(n\,15)+eq(n\,125)+eq(n\,245)+eq(n\,385)+eq(n\,515)+eq(n\,645)',scale=270:480,tile=3x2:padding=12:margin=12:color=0x071015" \
  -frames:v 1 -q:v 2 "$OUT/contact-sheet.jpg"

ffprobe -v error -show_entries format=duration,size -show_entries stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels -of json "$OUT/final.mp4" > "$ROOT/.work/final-probe.json"
echo "built $OUT/final.mp4"
