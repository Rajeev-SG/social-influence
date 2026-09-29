#!/usr/bin/env python3
"""Validate committed production packs against their source/media hashes."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def assert_tracked(relative: str) -> None:
    subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", relative],
                   check=True, stdout=subprocess.DEVNULL)


from social_influence.cli import production_pack


def main() -> int:
    checked = 0
    for pack_path in sorted(ROOT.glob('brands/*/posts/*.json')):
        brand_dir = pack_path.parent.parent
        pack = json.loads(pack_path.read_text())
        production_pack(brand_dir, pack['topic'], (brand_dir / 'profile.md').read_text())
        for item in pack.get('sources', []) + pack.get('media', []):
            assert_tracked(str((brand_dir.relative_to(ROOT) / item['file']).as_posix()))
        print(f'OK {pack_path.relative_to(ROOT)} (tracked inputs verified)')
        checked += 1
    if not checked:
        print('No production packs found', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
