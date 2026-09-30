#!/usr/bin/env python3
"""Regenerate Creative Engine v2 SVG treatment stills and the review payload."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from social_influence.creative_engine_v2 import CreativeEngineV2
from social_influence.creative_engine_v2.render import write_manifest_payload
from social_influence.creative_engine_v2.photographic import main as render_photo_stills

def main() -> int:
    out = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
    out.mkdir(parents=True, exist_ok=True)
    render_photo_stills()
    write_manifest_payload(out / 'component-render.json')
    engine = CreativeEngineV2.from_path(ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json')
    (out / 'review-payload.json').write_text(json.dumps(engine.static_review_payload(), indent=2) + '\n')
    (out / 'stage-output.json').write_text(json.dumps(engine.run_stages(), indent=2) + '\n')
    print('OK 30 photo-led candidate stills + review payload')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
