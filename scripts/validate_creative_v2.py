#!/usr/bin/env python3
"""Validate committed Creative Engine v2 artifacts without regenerating media."""
from pathlib import Path
from datetime import date, datetime, timezone
import json
import os
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from hashlib import sha256
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from social_influence.creative_engine_v2 import CreativeEngineV2


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

class ReviewHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = 0
        self.video_sources = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'card' in attrs.get('class', '').split():
            self.cards += 1
        if tag == 'source' and attrs.get('src'):
            self.video_sources.append(attrs['src'])

def probe_video(path: Path) -> tuple[int, int, float, bool]:
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        raise RuntimeError('ffprobe is required for Creative Engine v2 media validation')
    env = os.environ.copy()
    env['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/homebrew/Cellar/x265/4.1/lib:' + env.get('DYLD_FALLBACK_LIBRARY_PATH', '')
    result = subprocess.run([ffprobe, '-v', 'error', '-show_entries', 'stream=codec_type,width,height', '-show_entries', 'format=duration', '-of', 'json', str(path)], check=True, capture_output=True, text=True, env=env)
    data = json.loads(result.stdout)
    video = next(item for item in data['streams'] if item['codec_type'] == 'video')
    has_audio = any(item['codec_type'] == 'audio' for item in data['streams'])
    return int(video['width']), int(video['height']), float(data['format']['duration']), has_audio


def motion_delta(path: Path) -> float:
    env = os.environ.copy()
    env['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/homebrew/Cellar/x265/4.1/lib:' + env.get('DYLD_FALLBACK_LIBRARY_PATH', '')
    with tempfile.TemporaryDirectory(prefix='creative-v2-motion-') as temp:
        first = Path(temp) / 'first.png'
        second = Path(temp) / 'second.png'
        for seek, output in ((0.25, first), (1.15, second)):
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(seek), '-i', str(path), '-frames:v', '1', str(output)], check=True, env=env)
        left = Image.open(first).convert('RGB')
        right = Image.open(second).convert('RGB')
        return sum(ImageStat.Stat(ImageChops.difference(left, right)).mean) / 3

def main() -> int:
    engine = CreativeEngineV2.from_path(ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json')
    engine.validate()
    engine.run_stages()
    out = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
    expected_payload = json.loads(json.dumps(engine.static_review_payload(), sort_keys=True))
    expected_stage = json.loads(json.dumps(engine.run_stages(), sort_keys=True))
    source_manifest = json.loads((ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json').read_text())
    projected_manifest = json.loads((out / 'manifest.json').read_text())
    projection = projected_manifest.pop('_projection', None)
    expected_projection = {
        'source': '../manifest.json',
        'status': 'generated-projection',
        'decisionScope': 'copy-and-structure-only',
        'visualQualityValidation': 'not-performed',
        'note': 'This file exists at the candidate projection path referenced by review tooling. It is generated from ../manifest.json and must never be edited independently.',
    }
    if projected_manifest != source_manifest or projection != expected_projection:
        print('FAIL candidates/manifest.json is not an exact generated projection of ../manifest.json', file=sys.stderr)
        return 1
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
    page_path = ROOT / 'reviews/gutkitchen-creative-v2/index.html'
    page = page_path.read_text()
    for phrase in ('OLD BASELINE', 'CURRENT V2 STORYBOARD', 'NEW A', 'NEW B', 'NEW C', 'FINAL MEDIA', 'Mark as winner', 'Local review notes'):
        if phrase not in page:
            print(f'FAIL review page missing {phrase}', file=sys.stderr)
            return 1
    parser = ReviewHTMLParser()
    parser.feed(page)
    if parser.cards != 5:
        print(f'FAIL expected 5 review cards, found {parser.cards}', file=sys.stderr)
        return 1
    expected_sources = {
        '../../brands/gutkitchen/media/pilot/scene-001.mp4',
        '../../brands/gutkitchen/creative-engine-v2/candidates/new-c-preview.mp4',
        '../../brands/gutkitchen/creative-engine-v2/candidates/final-media/new-a.mp4',
        '../../brands/gutkitchen/creative-engine-v2/candidates/final-media/new-b.mp4',
        '../../brands/gutkitchen/creative-engine-v2/candidates/final-media/new-c.mp4',
    }
    if set(parser.video_sources) != expected_sources:
        print(f'FAIL review page video sources do not match committed files: {parser.video_sources}', file=sys.stderr)
        return 1
    library = json.loads((ROOT / 'brands/gutkitchen/references/library.json').read_text())
    if any('capture' in item for item in library.get('references', []) + library.get('searchEvidence', [])):
        print('FAIL tracked reference library contains capture paths/filenames', file=sys.stderr)
        return 1
    if 'No committable creator frames are expected to exist' not in library.get('capturePolicy', ''):
        print('FAIL reference library lacks self-contained capture policy', file=sys.stderr)
        return 1
    generated_at = engine.manifest.provenance.get('generated_at')
    evidence_dir = ROOT / 'docs/evidence/2026-09-30/creative-engine-v2'
    evidence_date = evidence_dir.parent.name
    if generated_at != evidence_date:
        print(f'FAIL generated_at {generated_at} does not match evidence date {evidence_date}', file=sys.stderr)
        return 1
    if date.fromisoformat(generated_at) > datetime.now(timezone.utc).date():
        print(f'FAIL generated_at {generated_at} is in the future', file=sys.stderr)
        return 1
    verification = json.loads((evidence_dir / 'verification.json').read_text())
    if verification['generatedAtUtc'][:10] != evidence_date:
        print('FAIL verification timestamp does not match evidence date', file=sys.stderr)
        return 1
    for treatment in engine.manifest.treatments:
        path = out / f'{treatment.treatment_id}-preview.mp4'
        width, height, duration, _ = probe_video(path)
        if (width, height) != (1080, 1920) or abs(duration - treatment.duration_seconds) > 0.1:
            print(f'FAIL media mismatch for {path.name}: {width}x{height} {duration:.3f}s', file=sys.stderr)
            return 1
    final_manifest = json.loads((out / 'final-media/final-media-manifest.json').read_text())
    if final_manifest.get('openRouterOnly') is not True or final_manifest.get('plannedCriticalRoutes') != 0:
        print('FAIL final media manifest does not enforce OpenRouter-only zero-planned execution', file=sys.stderr)
        return 1
    if final_manifest.get('candidateCount') != 3 or len(final_manifest.get('candidates', [])) != 3:
        print('FAIL final media manifest must contain exactly three candidates', file=sys.stderr)
        return 1
    provenance = json.loads((ROOT / 'brands/gutkitchen/creative-engine-v2/openrouter-run/provenance/generations.json').read_text())
    provenance_by_route = {item['route']: item for item in provenance}
    for candidate in final_manifest['candidates']:
        path = out / 'final-media' / f"{candidate['id']}.mp4"
        width, height, duration, has_audio = probe_video(path)
        if (width, height) != (1080, 1920) or abs(duration - 8.1) > 0.1 or not has_audio:
            print(f'FAIL final media mismatch for {path.name}: {width}x{height} {duration:.3f}s audio={has_audio}', file=sys.stderr)
            return 1
        if motion_delta(path) < 2.0:
            print(f'FAIL final media lacks measurable action motion: {path.name}', file=sys.stderr)
            return 1
        for shot in candidate['shots']:
            if shot.get('executionStatus') != 'executed-provider' or not shot.get('model'):
                print(f"FAIL unfinished shot route {candidate['id']}/{shot['id']}", file=sys.stderr)
                return 1
            record = provenance_by_route.get(shot['recordRoute'])
            source = ROOT / shot['sourceFile']
            if not record or not source.is_file() or record.get('output_sha256') != sha256_file(source):
                print(f"FAIL provenance mismatch {candidate['id']}/{shot['id']}", file=sys.stderr)
                return 1
    run_summary = json.loads((ROOT / 'brands/gutkitchen/creative-engine-v2/openrouter-run/run-summary.json').read_text())
    if not run_summary.get('openRouterOnly') or run_summary.get('referenceFramesCommitted') is not False:
        print('FAIL run summary is not OpenRouter-only or commits third-party frames', file=sys.stderr)
        return 1
    print('OK Creative Engine v2 artifacts, projections, dates, HTML and finished OpenRouter media verified')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
