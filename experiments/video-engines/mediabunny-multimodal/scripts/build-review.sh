#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FINAL="$ROOT/deliverables/final.mp4"
PREVIEW="$ROOT/deliverables/preview.mp4"
CONTACT="$ROOT/deliverables/contact-sheet.jpg"
TIMING="$ROOT/src/timing.json"

[[ -f "$FINAL" ]] || { echo "missing $FINAL" >&2; exit 1; }
[[ -f "$TIMING" ]] || { echo "missing $TIMING" >&2; exit 1; }
mkdir -p "$ROOT/deliverables"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/mediabunny-review.XXXXXX")"
cleanup() {
  find "$TMP" -type f -delete
  find "$TMP" -depth -type d -empty -delete
}
trap cleanup EXIT

ffmpeg -hide_banner -loglevel error -y \
  -i "$FINAL" \
  -map 0:v:0 -map 0:a:0 \
  -vf "scale=540:960:flags=lanczos" \
  -r 30 -c:v libx264 -preset medium -crf 25 -pix_fmt yuv420p \
  -c:a aac -b:a 96k -movflags +faststart -shortest \
  "$PREVIEW"

node - "$TIMING" "$TMP/times.tsv" <<'NODE'
const fs = require("node:fs");
const [timingPath, outputPath] = process.argv.slice(2);
const timing = JSON.parse(fs.readFileSync(timingPath, "utf8"));
const starts = timing.cues.map((cue) => cue.start);
const bounds = [
  ["hook", 0, Math.max(2.8, starts[1] - 0.2)],
  ["image", Math.max(2.8, starts[1] - 0.2), starts[2] - 0.15],
  ["audio", starts[2] - 0.15, starts[3] - 0.15],
  ["text", starts[3] - 0.15, starts[4] - 0.15],
  ["converge", starts[4] - 0.15, starts[5] - 0.15],
  ["answer", starts[5] - 0.15, timing.duration + 0.2],
];
const rows = bounds.map(([label, start, end]) => {
  const midpoint = Math.min(timing.duration - 0.02, start + (end - start) * 0.58);
  return `${label}\t${midpoint.toFixed(3)}`;
});
fs.writeFileSync(outputPath, `${rows.join("\n")}\n`);
NODE

index=0
while IFS=$'\t' read -r label time; do
  [[ -n "$label" ]] || continue
  ffmpeg -hide_banner -loglevel error -y -ss "$time" -i "$FINAL" -frames:v 1 "$TMP/$index.png"
  index=$((index + 1))
done < "$TMP/times.tsv"

filter=""
for i in 0 1 2 3 4 5; do
  filter+="[${i}:v]scale=360:640[v${i}];"
done
filter+="[v0][v1][v2]hstack=inputs=3[row0];[v3][v4][v5]hstack=inputs=3[row1];[row0][row1]vstack=inputs=2[out]"

ffmpeg -hide_banner -loglevel error -y \
  -i "$TMP/0.png" -i "$TMP/1.png" -i "$TMP/2.png" \
  -i "$TMP/3.png" -i "$TMP/4.png" -i "$TMP/5.png" \
  -filter_complex "$filter" -map "[out]" -frames:v 1 -q:v 3 "$CONTACT"

echo "wrote $PREVIEW"
echo "wrote $CONTACT"
