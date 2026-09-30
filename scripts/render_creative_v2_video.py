#!/usr/bin/env python3
"""Encode review-only Creative Engine v2 motion comps from the rendered shot stills."""
from __future__ import annotations

from pathlib import Path
import json
import math
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
MANIFEST = ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json'

def motion_filter(motion: str, frames: int) -> str:
    text = motion.lower()
    if 'left' in text:
        x = f'(iw-iw/zoom)*(1-on/{frames})'
        y = 'ih/2-(ih/zoom/2)'
        z = '1.08'
    elif 'right' in text or 'pan' in text or 'handheld' in text:
        x = f'(iw-iw/zoom)*on/{frames}'
        y = 'ih/2-(ih/zoom/2)'
        z = '1.08'
    elif 'orbit' in text or 'down' in text:
        x = 'iw/2-(iw/zoom/2)'
        y = f'(ih-ih/zoom)*on/{frames}'
        z = '1.08'
    elif 'out' in text or 'split' in text:
        x = 'iw/2-(iw/zoom/2)'
        y = 'ih/2-(ih/zoom/2)'
        z = f'1.08-0.08*on/{frames}'
    else:
        x = 'iw/2-(iw/zoom/2)'
        y = 'ih/2-(ih/zoom/2)'
        z = f'1.0+0.08*on/{frames}'
    return f"scale=2160:3840,zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s=1080x1920:fps=30,format=yuv420p"

def run_ffmpeg(args: list[str]) -> None:
    env = os.environ.copy()
    env['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/homebrew/Cellar/x265/4.1/lib:' + env.get('DYLD_FALLBACK_LIBRARY_PATH','')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*args], check=True, env=env)

def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    with tempfile.TemporaryDirectory(prefix='gutkitchen-v2-') as temp:
        temp_path = Path(temp)
        for treatment in manifest['treatments']:
            tid = treatment['treatment_id']
            clips = []
            for index, shot in enumerate(treatment['storyboard']['shots'], 1):
                frames = max(1, round(float(shot['duration']) * 30))
                src = CANDIDATES / f'{tid}-frame-{index:02d}.jpg'
                clip = temp_path / f'{tid}-{index:02d}.mp4'
                vf = motion_filter(shot['motion'], frames)
                run_ffmpeg(['-framerate','30','-i',str(src),'-vf',vf,'-frames:v',str(frames),'-c:v','libx264','-preset','medium','-crf','19','-an',str(clip)])
                clips.append(clip)
            listing = temp_path / f'{tid}.txt'
            listing.write_text(''.join(f"file '{clip.as_posix()}'\n" for clip in clips))
            output = CANDIDATES / f'{tid}-preview.mp4'
            run_ffmpeg(['-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(output)])
            print(f'OK {output.relative_to(ROOT)} {treatment["duration_seconds"]:.1f}s')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
