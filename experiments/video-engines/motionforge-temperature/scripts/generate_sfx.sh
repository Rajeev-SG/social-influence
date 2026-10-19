#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/assets/sfx"

ffmpeg -y -f lavfi -i "sine=frequency=110:duration=0.24" -af "afade=t=in:st=0:d=0.01,afade=t=out:st=0.1:d=0.14,lowpass=f=340,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo" "$ROOT/assets/sfx/lock.wav" </dev/null
ffmpeg -y -f lavfi -i "sine=frequency=880:duration=0.32" -af "afade=t=in:st=0:d=0.01,afade=t=out:st=0.1:d=0.22,tremolo=f=7:d=0.45,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo" "$ROOT/assets/sfx/sparkle.wav" </dev/null
ffmpeg -y -f lavfi -i "anoisesrc=color=white:duration=0.46" -af "afade=t=in:st=0:d=0.08,afade=t=out:st=0.22:d=0.24,lowpass=f=1800,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo" "$ROOT/assets/sfx/whoosh.wav" </dev/null
