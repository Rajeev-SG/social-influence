#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p .render

echo "--- frame inspection timestamps ---"
.venv/bin/python - <<'PY'
import json
from pathlib import Path
timing = json.loads(Path("assets/audio/timing.json").read_text())
for scene in timing["scenes"]:
    print(f"{scene['id']:10s} {scene['start']:6.3f}s -> {scene['end']:6.3f}s")
PY

echo "--- actual audio analysis ---"
.venv/bin/python scripts/analyze_audio.py | tee .render/audio-analysis.json

echo "--- extracted frame contact sheet ---"
.venv/bin/python scripts/make_contact_sheet.py

echo "--- ffmpeg audio diagnostics ---"
ffmpeg -hide_banner -nostats -i assets/audio/mix.wav -af volumedetect -f null - 2>&1 | \
  rg "mean_volume|max_volume|Duration" || true

echo "Inspection complete: deliverables/contact-sheet.jpg and .render/audio-analysis.json"
