#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f assets/narration.wav ]]; then
  node scripts/generate_audio.mjs
fi

bash scripts/generate_sfx.sh
node scripts/render.mjs

ffmpeg -y \
  -i assets/picture.mp4 \
  -i assets/narration.wav \
  -i assets/sfx/lock.wav \
  -i assets/sfx/sparkle.wav \
  -i assets/sfx/whoosh.wav \
  -filter_complex "[0:v]fps=30,format=yuv420p[v];[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=1.0[voice];[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.28,adelay=7140|7140[lock];[3:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.18,adelay=12610|12610[sparkle];[4:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.16,adelay=15880|15880[whoosh];[voice][lock][sparkle][whoosh]amix=inputs=4:duration=first:normalize=0,alimiter=limit=0.95[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart \
  deliverables/final.mp4

ffmpeg -y -i deliverables/final.mp4 -vf "scale=540:960:flags=lanczos" -c:v libx264 -preset veryfast -crf 28 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 48000 -ac 2 -movflags +faststart deliverables/preview.mp4

ffmpeg -y -i deliverables/final.mp4 -vf "select='eq(n\,20)+eq(n\,120)+eq(n\,260)+eq(n\,420)+eq(n\,540)+eq(n\,700)',scale=270:480,tile=3x2:margin=16:padding=16:color=#07101f" -frames:v 1 -q:v 2 deliverables/contact-sheet.jpg

bash scripts/verify.sh
