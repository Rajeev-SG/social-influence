#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FINAL="$ROOT/deliverables/final.mp4"
TIMING="$ROOT/src/timing.json"
[[ -f "$FINAL" ]] || { echo "missing $FINAL" >&2; exit 1; }
[[ -f "$TIMING" ]] || { echo "missing $TIMING" >&2; exit 1; }

CREATED_TMP=0
if [[ -n "${OUT_DIR:-}" ]]; then
  QA="$OUT_DIR"
  mkdir -p "$QA"
else
  QA="$(mktemp -d "${TMPDIR:-/tmp}/mediabunny-qa.XXXXXX")"
  CREATED_TMP=1
fi

cleanup() {
  if [[ "$CREATED_TMP" -eq 1 && -z "${KEEP:-}" ]]; then
    find "$QA" -type f -delete
    find "$QA" -depth -type d -empty -delete
  fi
}
trap cleanup EXIT

ffprobe -v error -show_streams -show_format -of json "$FINAL" > "$QA/ffprobe.json"
ffmpeg -v error -i "$FINAL" -f null - > "$QA/decode.log" 2>&1

node - "$TIMING" "$QA/times.tsv" <<'NODE'
const fs = require("node:fs");
const [timingPath, outputPath] = process.argv.slice(2);
const timing = JSON.parse(fs.readFileSync(timingPath, "utf8"));
const starts = timing.cues.map((cue) => cue.start);
const bounds = [
  ["opening", 0, Math.max(2.8, starts[1] - 0.2)],
  ["image", Math.max(2.8, starts[1] - 0.2), starts[2] - 0.15],
  ["handoff-image-audio", starts[2] - 0.15, starts[2] + 0.15],
  ["audio", starts[2] - 0.15, starts[3] - 0.15],
  ["text", starts[3] - 0.15, starts[4] - 0.15],
  ["handoff-text-converge", starts[4] - 0.15, starts[4] + 0.15],
  ["converge", starts[4] - 0.15, starts[5] - 0.15],
  ["answer", starts[5] - 0.15, timing.duration + 0.2],
  ["ending", Math.max(0, timing.duration - 0.18), timing.duration + 0.2],
];
const rows = bounds.map(([label, start, end]) => {
  const midpoint = Math.min(timing.duration - 0.02, start + (end - start) * 0.58);
  return `${label}\t${midpoint.toFixed(3)}`;
});
fs.writeFileSync(outputPath, `${rows.join("\n")}\n`);
NODE

while IFS=$'\t' read -r label time; do
  [[ -n "$label" ]] || continue
  ffmpeg -hide_banner -loglevel error -y -ss "$time" -i "$FINAL" -frames:v 1 "$QA/$label.jpg"
done < "$QA/times.tsv"

ffmpeg -hide_banner -loglevel error -y -i "$FINAL" -vn -acodec pcm_s16le "$QA/muxed-audio.wav"
ffmpeg -hide_banner -i "$FINAL" -af ebur128=peak=true -f null - > "$QA/ebur128.txt" 2>&1
ffmpeg -hide_banner -i "$QA/muxed-audio.wav" -af astats=metadata=1:reset=0 -f null - > "$QA/astats.txt" 2>&1

echo "--- streams ---"
jq '{format: .format, streams: [.streams[] | {codec_name,codec_type,profile,width,height,pix_fmt,color_range,color_space,r_frame_rate,avg_frame_rate,duration,bit_rate,sample_rate,channels,channel_layout}]}' "$QA/ffprobe.json"
echo "--- decode log ---"
cat "$QA/decode.log"
echo "--- loudness ---"
grep -E 'Integrated loudness|I:|LRA:|True peak|Peak:' "$QA/ebur128.txt" | tail -12
echo "--- audio stats ---"
grep -E 'Peak level|RMS level|Flat factor|Peak count|Dynamic range|Number of samples' "$QA/astats.txt" | tail -18
echo "--- QA files: $QA ---"
find "$QA" -maxdepth 1 -type f -print | sort
