#!/usr/bin/env python3
"""Validate committed Creative Engine v2 artifacts without regenerating media."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from social_influence.creative_engine_v2 import CreativeEngineV2

def main() -> int:
    engine = CreativeEngineV2.from_path(ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json')
    engine.validate()
    engine.run_stages()
    out = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
    expected_payload = json.loads(json.dumps(engine.static_review_payload(), sort_keys=True))
    expected_stage = json.loads(json.dumps(engine.run_stages(), sort_keys=True))
    if json.loads((out / 'review-payload.json').read_text()) != expected_payload:
        print('FAIL review-payload.json is not a generated projection of manifest.json', file=sys.stderr)
        return 1
    if json.loads((out / 'stage-output.json').read_text()) != expected_stage:
        print('FAIL stage-output.json is not a generated projection of manifest.json', file=sys.stderr)
        return 1
    for treatment in ('new-a', 'new-b', 'new-c'):
        for index in range(1, 11):
            if not (out / f'{treatment}-frame-{index:02d}.jpg').is_file():
                print(f'MISSING {treatment}-frame-{index:02d}.jpg', file=sys.stderr)
                return 1
        if not (out / f'{treatment}-preview.mp4').is_file():
            print(f'MISSING {treatment}-preview.mp4', file=sys.stderr)
            return 1
    page = (ROOT / 'reviews/gutkitchen-creative-v2/index.html').read_text()
    for phrase in ('OLD / BASELINE', 'NEW A', 'NEW B', 'NEW C', 'STORYBOARD', 'planned, not executed'):
        if phrase not in page:
            print(f'FAIL review page missing {phrase}', file=sys.stderr)
            return 1
    print('OK Creative Engine v2 artifacts and generated projections verified')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
