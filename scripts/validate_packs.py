#!/usr/bin/env python3
"""Validate committed production packs against their source/media hashes."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from social_influence.cli import production_pack


def main() -> int:
    checked = 0
    for pack_path in sorted(ROOT.glob('brands/*/posts/*.json')):
        brand_dir = pack_path.parent.parent
        pack = json.loads(pack_path.read_text())
        production_pack(brand_dir, pack['topic'], (brand_dir / 'profile.md').read_text())
        print(f'OK {pack_path.relative_to(ROOT)}')
        checked += 1
    if not checked:
        print('No production packs found', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
