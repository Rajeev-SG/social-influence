#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r src/requirements.txt

echo "VideoFlow environment ready:"
.venv/bin/python - <<'PY'
import importlib.metadata as metadata
for package in ("videoflow", "pillow"):
    print(f"{package}=={metadata.version(package)}")
PY
