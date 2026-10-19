"""Decode, inspect video specs, extract review frames, and measure audio."""

import argparse
import json
from pathlib import Path
import subprocess


def run(args, capture=False):
    result = subprocess.run(args, check=True, text=True, capture_output=capture)
    return (result.stdout + result.stderr) if capture else ""


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--outdir", required=True)
parser.add_argument("--times", default="1.4,4.6,8.2,11.8,15.0,18.2,21.2")
args = parser.parse_args()

media = Path(args.input).resolve()
outdir = Path(args.outdir).resolve()
outdir.mkdir(parents=True, exist_ok=True)

probe = json.loads(run([
    "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(media)
], capture=True))
decode_log = run([
    "ffmpeg", "-v", "error", "-xerror", "-i", str(media), "-map", "0", "-f", "null", "-"
], capture=True)

audio = run([
    "ffmpeg", "-hide_banner", "-nostats", "-i", str(media), "-map", "0:a:0",
    "-af", "ebur128=peak=true,volumedetect", "-f", "null", "-"
], capture=True)

times = [float(value) for value in args.times.split(",")]
frames = []
for index, timestamp in enumerate(times):
    target = outdir / f"frame-{index:02d}-{timestamp:05.2f}.png"
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(timestamp),
        "-i", str(media), "-frames:v", "1", str(target)
    ])
    frames.append(str(target))

report = {
    "media": str(media),
    "probe": probe,
    "decode_errors": decode_log.strip(),
    "audio_measurement": audio.strip(),
    "frames": frames,
}
(outdir / "inspection.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
