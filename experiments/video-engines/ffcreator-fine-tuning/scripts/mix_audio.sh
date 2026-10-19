#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ffmpeg -hide_banner -loglevel error -y \
  -i "$ROOT/assets/audio/narration.wav" \
  -i "$ROOT/assets/audio/soundscape.wav" \
  -filter_complex "[0:a]aformat=channel_layouts=stereo,volume=1.0[voice];[1:a]aformat=channel_layouts=stereo,volume=0.34[bed];[voice][bed]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89,loudnorm=I=-16:TP=-2:LRA=9[mix]" \
  -map "[mix]" -ar 48000 -ac 2 -c:a pcm_s16le \
  "$ROOT/assets/audio/mix.wav"

echo "wrote $ROOT/assets/audio/mix.wav"
