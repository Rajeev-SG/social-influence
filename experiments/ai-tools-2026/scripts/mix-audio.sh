#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/build-soundtrack.py"

ffmpeg -y \
  -i "$ROOT/narration/narration.wav" \
  -i "$ROOT/assets/audio/soundtrack.wav" \
  -filter_complex "[1:a]volume=0.34[music];[music][0:a]sidechaincompress=threshold=0.012:ratio=10:attack=18:release=380[ducked];[0:a][ducked]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11,apad=whole_dur=88.8[out]" \
  -map "[out]" \
  -ar 48000 \
  -ac 2 \
  -c:a pcm_s16le \
  "$ROOT/assets/audio/mix.wav"
