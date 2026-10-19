#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_BIN="${NODE_BIN:-/opt/homebrew/opt/node@22/bin/node}"
if [[ ! -x "$NODE_BIN" ]]; then
  NODE_BIN="$(command -v node)"
fi

"$NODE_BIN" "$ROOT/scripts/narrate.cjs"
ffmpeg -hide_banner -loglevel error -y \
  -i "$ROOT/assets/audio/narration-raw.wav" \
  -af "highpass=f=75,lowpass=f=11500,acompressor=threshold=0.12:ratio=2:attack=15:release=180:makeup=1.15,loudnorm=I=-17:TP=-2:LRA=8" \
  -ac 2 -ar 48000 "$ROOT/assets/audio/narration.wav"
python3 "$ROOT/scripts/soundscape.py"

find "$ROOT/assets/audio/.tts-tmp" -type f -delete 2>/dev/null || true
find "$ROOT/assets/audio/.tts-tmp" -depth -type d -empty -delete 2>/dev/null || true
if [[ -f "$ROOT/assets/audio/narration-raw.wav" ]]; then
  unlink "$ROOT/assets/audio/narration-raw.wav"
fi

