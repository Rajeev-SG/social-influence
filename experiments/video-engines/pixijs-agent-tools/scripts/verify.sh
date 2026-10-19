#!/bin/zsh
set -euo pipefail
ROOT="${0:A:h:h}"
OUT="$ROOT/deliverables"
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels -of json "$OUT/final.mp4"
ffmpeg -hide_banner -v error -xerror -i "$OUT/final.mp4" -map 0:v:0 -map 0:a:0 -f null -
ffmpeg -hide_banner -v error -xerror -i "$OUT/preview.mp4" -map 0:v:0 -map 0:a:0 -f null -
test "$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,pix_fmt -of csv=p=0 "$OUT/final.mp4")" = "1080,1920,yuv420p,30/1"
test -s "$OUT/contact-sheet.jpg"
echo "verified"
