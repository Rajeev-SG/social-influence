#!/bin/zsh
set -euo pipefail
ROOT="${0:A:h:h}"
A="$ROOT/assets/audio"
N=$(python3 - <<'PY'
import json
print(len(json.load(open('/Users/rajeev/Code/social-influence/experiments/video-engines/pixijs-agent-tools/assets/audio/timing.json'))['timing']))
PY
)
ARGS=()
for f in "$A"/control-desk.wav "$A"/choose-tool.wav "$A"/supply-action.wav "$A"/read-result.wav "$A"/continue.wav "$A"/effects.wav; do ARGS+=(-i "$f"); done
for i in {0..4}; do
  START=$(python3 - "$i" <<'PY'
import json,sys
i=int(sys.argv[1]); print(json.load(open('/Users/rajeev/Code/social-influence/experiments/video-engines/pixijs-agent-tools/assets/audio/timing.json'))['timing'][i]['start']*1000)
PY
)
  FILTER+="[$i:a]aresample=48000,adelay=${START}|${START},volume=1.0[v$i];"
done
FILTER+="[5:a]volume=0.72[fx];[v0][v1][v2][v3][v4][fx]amix=inputs=6:normalize=0[mix];[mix]apad=whole_dur=22.2,alimiter=limit=0.92,loudnorm=I=-18:TP=-2:LRA=9[out]"
ffmpeg -hide_banner -loglevel error -y "${ARGS[@]}" -filter_complex "$FILTER" -map "[out]" -ac 2 -ar 48000 "$A/mix.wav"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_name,channels,sample_rate -of json "$A/mix.wav" > "$A/mix-probe.json"
echo "mixed $N narration clips into $A/mix.wav"
