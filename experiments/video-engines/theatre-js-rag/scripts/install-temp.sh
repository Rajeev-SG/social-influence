#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

# Temporary dependency installation is intentionally confined to this project.
# Remove node_modules and .npm-cache with scripts/clean.mjs before delivery.
npm install --cache .npm-cache --no-audit --no-fund
