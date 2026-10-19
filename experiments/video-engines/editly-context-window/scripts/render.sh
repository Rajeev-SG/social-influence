#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_BIN="${NODE_BIN:-/opt/homebrew/opt/node@22/bin/node}"
if [[ ! -x "$NODE_BIN" ]]; then
  NODE_BIN="$(command -v node)"
fi

"$NODE_BIN" "$ROOT/src/render.mjs" --out "$ROOT/deliverables/final.mp4"
python3 "$ROOT/scripts/deliver.py"

