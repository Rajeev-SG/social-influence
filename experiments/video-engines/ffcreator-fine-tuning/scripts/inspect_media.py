#!/usr/bin/env python3
"""Extract review frames and measure the delivered audio/video."""

from __future__ import annotations

import json
import math
import subprocess
import wave
from array import array
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "deliverables" / "final.mp4"
MIX = ROOT / "assets" / "audio" / "mix.wav"
TIMING = json.loads((ROOT / "src" / "timing.json").read_text())
OUT = ROOT / ".review"
FRAMES = OUT / "frames"


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def read_wav(path: Path) -> tuple[int, array]:
    with wave.open(str(path), "rb") as handle:
        rate = handle.getframerate()
        channels = handle.getnchannels()
        width = handle.getsampwidth()
        raw = handle.readframes(handle.getnframes())
    if width != 2:
        raise RuntimeError(f"{path}: expected 16-bit PCM, got {width * 8}-bit")
    values = array("h")
    values.frombytes(raw)
    if channels > 1:
        mono = array("f")
        for index in range(0, len(values), channels):
            mono.append(sum(values[index:index + channels]) / (channels * 32768.0))
        return rate, mono
    return rate, array("f", (value / 32768.0 for value in values))


def resample(data: array, source_rate: int, target_rate: int) -> array:
    if source_rate == target_rate:
        return data
    length = max(1, round(len(data) * target_rate / source_rate))
    result = array("f", bytes(4 * length))
    for index in range(length):
        source_pos = index * (len(data) - 1) / max(1, length - 1)
        left = int(source_pos)
        right = min(len(data) - 1, left + 1)
        weight = source_pos - left
        result[index] = data[left] * (1.0 - weight) + data[right] * weight
    return result


def correlation_offset(reference: array, mix: array, expected: float, rate: int) -> float:
    pad = round(0.42 * rate)
    expected_index = round(expected * rate)
    ref_mean = sum(reference) / len(reference)
    ref_centered = [value - ref_mean for value in reference]
    best_score = float("-inf")
    best_lag = 0
    for lag in range(-pad, pad + 1):
        start = expected_index + lag
        if start < 0 or start + len(reference) > len(mix):
            continue
        score = 0.0
        for index, value in enumerate(ref_centered):
            score += value * mix[start + index]
        if score > best_score:
            best_score = score
            best_lag = lag
    return best_lag / rate


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.jpg"):
        old.unlink()

    probe = json.loads(run(
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(VIDEO)
    ))
    decode = subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(VIDEO), "-f", "null", "-"],
        text=True,
        capture_output=True,
    )

    frame_times = [0.25, 1.6, 2.95, 5.6, 8.55, 11.8, 15.25, 17.35, 19.65, 22.55]
    for index, timestamp in enumerate(frame_times):
        run(
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{timestamp:.3f}", "-i", str(VIDEO), "-frames:v", "1",
            "-q:v", "2", str(FRAMES / f"{index + 1:02d}-{timestamp:05.2f}.jpg"),
        )

    mix_rate, mix = read_wav(MIX)
    corr_rate = 2000
    mix_corr = resample(mix, mix_rate, corr_rate)
    sync = []
    reference_pcm = OUT / "reference-pcm.wav"
    for cue in TIMING["cues"]:
        run(
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(ROOT / "assets" / cue["file"]),
            "-ar", str(corr_rate), "-ac", "1", "-c:a", "pcm_s16le",
            str(reference_pcm),
        )
        _, reference = read_wav(reference_pcm)
        offset = correlation_offset(reference, mix_corr, cue["start"], corr_rate)
        sync.append({
            "id": cue["id"],
            "expected_start": cue["start"],
            "measured_start": cue["start"] + offset,
            "offset_ms": round(offset * 1000, 1),
        })

    loudness = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(VIDEO),
         "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
        text=True,
        capture_output=True,
    ).stderr
    loudness_tail = "\n".join(loudness.strip().splitlines()[-18:])

    report = {
        "video": str(VIDEO),
        "probe": probe,
        "decode": {"returncode": decode.returncode, "stderr": decode.stderr},
        "frames": sorted(str(path.relative_to(ROOT)) for path in FRAMES.glob("*.jpg")),
        "audio_sync": sync,
        "max_abs_sync_ms": max(abs(item["offset_ms"]) for item in sync),
        "loudness_ebur128_tail": loudness_tail,
    }
    (OUT / "inspection.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
