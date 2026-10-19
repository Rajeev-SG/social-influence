#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p audit

extract() {
  local timestamp="$1"
  local output="$2"
  ffmpeg -hide_banner -loglevel error -y -ss "$timestamp" -i deliverables/final.mp4 \
    -frames:v 1 -vf "scale=540:960" -q:v 2 "audit/${output}"
}

extract "5.02" "coordinates-5.02-mobile.jpg"
extract "16.60" "ending-16.60-mobile.jpg"
extract "17.55" "ending-17.55-mobile.jpg"
extract "18.35" "ending-18.35-mobile.jpg"

ffmpeg -hide_banner -loglevel error -y \
  -i audit/ending-16.60-mobile.jpg \
  -i audit/ending-17.55-mobile.jpg \
  -i audit/ending-18.35-mobile.jpg \
  -filter_complex "[0:v][1:v][2:v]hstack=inputs=3" \
  -q:v 2 audit/ending-mobile-audit.jpg
