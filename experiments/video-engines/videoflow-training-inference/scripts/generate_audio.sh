#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_BIN="${KOKORO_NODE_BIN:-/opt/homebrew/opt/node@22/bin/node}"
cd "$ROOT"

if [[ ! -x "$NODE_BIN" ]]; then
  echo "Missing supported Node runtime: $NODE_BIN" >&2
  exit 1
fi

HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 "$NODE_BIN" scripts/generate_audio.mjs
.venv/bin/python scripts/build_audio.py
