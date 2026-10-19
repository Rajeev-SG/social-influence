#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:-final}"
QUALITY_ARGS=(--resolution 1080,1920 --fps 30 --video-codec libx264 --pixel-format yuv420p --encoder-option crf=18 --encoder-option preset=slow)
if [[ "$MODE" == "review" ]]; then
  QUALITY_ARGS=(--resolution 540,960 --fps 12 --video-codec libx264 --pixel-format yuv420p --encoder-option crf=24 --encoder-option preset=veryfast)
fi

mkdir -p .work
node scripts/narrate.cjs
uv run --no-project --python 3.13 --with numpy==2.3.4 python scripts/soundscape.py
/usr/bin/time -p uv run --no-project --python 3.13 --with manim==0.22.0 \
  manim render "${QUALITY_ARGS[@]}" \
  --media_dir .work/media --log_dir .work/logs --log_to_file --progress_bar none \
  --output_file "embeddings-${MODE}" src/embeddings_scene.py EmbeddingsScene \
  2>&1 | tee ".work/render-${MODE}.log"

PICTURE="$(find .work/media/videos -type f -name "embeddings-${MODE}.mp4" -print -quit)"
if [[ -z "$PICTURE" ]]; then
  echo "Rendered picture not found for mode: $MODE" >&2
  exit 1
fi

uv run --no-project --python 3.13 --with pillow==11.3.0 python scripts/deliver.py "$PICTURE" "$MODE"
mkdir -p audit
uv run --no-project --python 3.13 --with pillow==11.3.0 python scripts/verify.py "$MODE" | tee "audit/${MODE}-verification.json"
cp ".work/render-${MODE}.log" "audit/render-${MODE}.log"
if [[ "$MODE" == "final" ]]; then
  bash scripts/audit_frames.sh
fi
