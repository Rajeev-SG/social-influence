#!/usr/bin/env python3
"""Verify immutable run evidence against its SHA-256 manifests."""
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT.glob('docs/evidence/**/manifest.sha256')


def main() -> int:
    checked = 0
    for manifest in MANIFESTS:
        for line in manifest.read_text().splitlines():
            expected, name = line.split('  ', 1)
            artifact = manifest.parent / name
            actual = sha256(artifact.read_bytes()).hexdigest()
            if actual != expected:
                print(f'FAIL {artifact.relative_to(ROOT)}: {actual} != {expected}', file=sys.stderr)
                return 1
            checked += 1
        print(f'OK {manifest.relative_to(ROOT)}')
    if not checked:
        print('No evidence manifests found', file=sys.stderr)
        return 1
    print(f'OK {checked} evidence artifacts verified')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
