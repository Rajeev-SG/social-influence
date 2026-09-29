#!/usr/bin/env python3
"""Render disclosed image-led shot cards with deliberate quick cuts.

This is an operator preproduction helper for generated stills. JSON controls all
copy and nutrient values. The bottom 672px is reserved for burned captions so the
Content Machine OCR sync gate sees captions rather than decorative text.
"""
import argparse
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


CAPTION_TOP = 1248


def font(size, bold=False):
    candidates = [
        Path('/System/Library/Fonts/Supplemental') / ('Arial Bold.ttf' if bold else 'Arial.ttf'),
        Path('/usr/share/fonts/truetype/dejavu') / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),
    ]
    return ImageFont.truetype(str(next(path for path in candidates if path.exists())), size)


def shot_frame(source, data, shot, t):
    """Build one frame; crop jumps every 1.35s to match the research pacing."""
    canvas = Image.new('RGB', (1080, 1920), '#FAF5EA')
    crop_height = 840
    crop_width = 875
    offset = (int(t / 1.35) + shot.get('phase', 0)) % 4
    zooms = (1.00, 1.14, 1.06, 1.20)
    pans = ((0, 0), (-35, 15), (35, -15), (0, 25))
    zoom = zooms[offset]
    pan_x, pan_y = pans[offset]
    source_width = int(source.width / zoom)
    source_height = int(source.height / zoom)
    left = max(0, min(source.width - source_width, source_width // 12 + pan_x))
    top = max(0, min(source.height - source_height, source_height // 12 + pan_y))
    view = source.crop((left, top, left + source_width, top + source_height))
    if offset % 2:
        view = view.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        view = ImageEnhance.Brightness(view).enhance(0.55)
        view = ImageEnhance.Color(view).enhance(0.25)
    view = ImageOps.fit(view, (crop_width, crop_height))
    canvas.paste(view, ((1080 - crop_width) // 2, 365))

    draw = ImageDraw.Draw(canvas)
    draw.text((64, 52), data['brand'], font=font(33, True), fill='#2D543B')
    draw.text((64, 108), shot['headline'] if offset % 2 == 0 else shot['detail'],
              font=font(52 if offset % 2 == 0 else 43, True), fill='#203A2A')
    for x, value, label, color in (
        (64, data['protein'], 'PROTEIN', '#DCECBE'),
        (555, data['fibre'], 'FIBRE', '#F6CF75'),
    ):
        draw.rounded_rectangle((x, 195, x + 460, 338), radius=24, fill=color)
        draw.text((x + 27, 205), value, font=font(64, True), fill='#203A2A')
        draw.text((x + 28, 285), label, font=font(23, True), fill='#203A2A')

    draw.text((66, 338), 'AI food illustration | label-based estimate', font=font(22), fill='#526656')
    draw.rounded_rectangle((52, 1082, 1028, 1186), radius=20, fill='#FAF5EA')
    draw.text((78, 1102), shot['detail'], font=font(35, True), fill='#203A2A')
    draw.text((78, 1148), shot['subdetail'], font=font(24), fill='#203A2A')

    previous = shot.get('counter_from', shot['counter'])
    value = previous + (shot['counter'] - previous) * min(t / 1.1, 1)
    draw.rounded_rectangle((52, 1192, 525, 1242), radius=16, fill='#264A35')
    draw.text((74, 1203), f'FIBRE  {value:.1f}g+', font=font(31, True), fill='white')
    if t >= 1.4 and 0.0 <= (t % 1.35) < 0.035:
        draw.rectangle((0, 0, 1080, 1920), fill='#F6CF75')
    draw.rectangle((0, CAPTION_TOP, 1080, 1920), fill='#203A2A')
    return canvas


def render(spec_path, force=False):
    spec_path = Path(spec_path).resolve()
    data = json.loads(spec_path.read_text())
    root = spec_path.parent
    for shot in data['shots']:
        dest = root / shot['output']
        if dest.exists() and not force:
            continue
        source = Image.open(root / shot['image']).convert('RGB')
        source = source.crop((0, int(source.height * .13), source.width, source.height))
        seconds, fps = shot.get('seconds', 9), 30
        command = [
            'ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
            '-s', '1080x1920', '-r', str(fps), '-i', '-', '-an', '-c:v', 'libx264',
            '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart', str(dest),
        ]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as proc:
            for frame in range(int(seconds * fps)):
                proc.stdin.write(shot_frame(source, data, shot, frame / fps).tobytes())
            proc.stdin.close()
            if proc.wait():
                raise RuntimeError(f'FFmpeg failed: {dest}')
        print(dest, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('spec')
    parser.add_argument('--force', action='store_true')
    render(parser.parse_args().spec, force=parser.parse_args().force)
