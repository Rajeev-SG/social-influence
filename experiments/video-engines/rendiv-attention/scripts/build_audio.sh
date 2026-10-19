#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/assets/audio"
node "$ROOT/scripts/narrate.cjs"
ffmpeg -hide_banner -loglevel error -y -i "$ROOT/assets/audio/narration-raw.wav" \
  -af "highpass=f=75,lowpass=f=11000,acompressor=threshold=0.12:ratio=2:attack=15:release=180:makeup=1.2,loudnorm=I=-17:TP=-2:LRA=8" \
  -ar 48000 -ac 2 "$ROOT/assets/audio/narration.wav"
python3 "$ROOT/scripts/soundscape.py"
rm -f "$ROOT/assets/audio/narration-raw.wav"
printf 'audio ready: %s\n' "$ROOT/assets/audio"
