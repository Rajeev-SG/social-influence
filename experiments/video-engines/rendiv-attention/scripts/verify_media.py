"""Objective decode, spec, audio and timing checks for the rendered film."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "deliverables" / "final.mp4"
TIMING = json.loads((ROOT / "src" / "timing.json").read_text())


def run(*args, check=True):
    return subprocess.run(args, check=check, text=True, capture_output=True)


probe = json.loads(run(
    "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(FINAL)
).stdout)
streams = {stream["codec_type"]: stream for stream in probe["streams"]}
video = streams.get("video", {})
audio = streams.get("audio", {})
format_info = probe.get("format", {})
width = int(video.get("width", 0))
height = int(video.get("height", 0))
fps = video.get("r_frame_rate", "0/1")
duration = float(format_info.get("duration", 0))
checks = {
    "decode": run("ffmpeg", "-v", "error", "-i", str(FINAL), "-f", "null", "-").returncode == 0,
    "width_1080": width == 1080,
    "height_1920": height == 1920,
    "fps_30": fps == "30/1",
    "duration_15_25s": 15.0 <= duration <= 25.0,
    "h264": video.get("codec_name") == "h264",
    "yuv420p": video.get("pix_fmt") == "yuv420p",
    "aac_stereo": audio.get("codec_name") == "aac" and int(audio.get("channels", 0)) == 2,
    "audio_duration_matches": abs(duration - TIMING["duration"]) <= 0.25,
}
stats = run("ffmpeg", "-hide_banner", "-i", str(FINAL), "-af", "astats=metadata=1:reset=0", "-f", "null", "-", check=False)
silence = run("ffmpeg", "-hide_banner", "-i", str(FINAL), "-af", "silencedetect=n=-45dB:d=0.35", "-f", "null", "-", check=False)
report = {
    "file": str(FINAL),
    "format": format_info,
    "video": video,
    "audio": audio,
    "timing_duration": TIMING["duration"],
    "checks": checks,
    "audio_astats_tail": stats.stderr.splitlines()[-30:],
    "silencedetect_tail": silence.stderr.splitlines()[-12:],
}
print(json.dumps(report, indent=2))
if not all(checks.values()):
    sys.exit(1)
