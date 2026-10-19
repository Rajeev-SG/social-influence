#!/usr/bin/env python3
"""Measure speech level, silence, and narration timing without extra packages."""

from __future__ import annotations

import array
import json
import math
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "assets" / "audio"


def read_audio(path: Path) -> tuple[int, int, array.array]:
    with wave.open(str(path), "rb") as handle:
        rate = handle.getframerate()
        channels = handle.getnchannels()
        raw = handle.readframes(handle.getnframes())
    samples = array.array("h")
    samples.frombytes(raw)
    if channels == 2:
        samples = array.array("h", (samples[index] for index in range(0, len(samples), 2)))
    return rate, channels, samples


def dbfs(value: float) -> float:
    return 20 * math.log10(max(value, 1e-9) / 32768)


def rms_at(samples: array.array, rate: int, start: float, duration: float = 0.08) -> float:
    first = max(0, round(start * rate))
    last = min(len(samples), first + round(duration * rate))
    if first >= last:
        return 0.0
    return math.sqrt(sum(value * value for value in samples[first:last]) / (last - first))


def main() -> None:
    timing = json.loads((AUDIO_DIR / "narration-timing.json").read_text())
    narration_rate, narration_channels, narration = read_audio(AUDIO_DIR / "narration.wav")
    mix_rate, mix_channels, mix = read_audio(AUDIO_DIR / "mix.wav")
    window_rate = 50
    window_size = narration_rate // window_rate
    energy = []
    for start in range(0, len(narration), window_size):
        chunk = narration[start : start + window_size]
        energy.append(math.sqrt(sum(value * value for value in chunk) / max(1, len(chunk))))
    active = sum(value > 350 for value in energy) / window_rate
    quiet = sum(value < 80 for value in energy) / window_rate

    line_checks = []
    for line in timing["lines"]:
        start = line["startSeconds"]
        before = rms_at(narration, narration_rate, max(0, start - 0.12))
        after = rms_at(narration, narration_rate, start + 0.04)
        line_checks.append(
            {
                "id": line["id"],
                "startSeconds": start,
                "rmsBeforeDbfs": round(dbfs(before), 2),
                "rmsAtStartDbfs": round(dbfs(after), 2),
                "onsetRiseDb": round(dbfs(after) - dbfs(before), 2),
            }
        )

    result = {
        "narration": {
            "sampleRate": narration_rate,
            "channels": narration_channels,
            "durationSeconds": round(len(narration) / narration_rate, 3),
            "peakDbfs": round(dbfs(max(abs(value) for value in narration)), 2),
            "rmsDbfs": round(dbfs(math.sqrt(sum(value * value for value in narration) / len(narration))), 2),
            "activeSeconds": round(active, 3),
            "quietSeconds": round(quiet, 3),
        },
        "mix": {
            "sampleRate": mix_rate,
            "channels": mix_channels,
            "durationSeconds": round(len(mix) / mix_rate, 3),
            "peakDbfs": round(dbfs(max(abs(value) for value in mix)), 2),
            "rmsDbfs": round(dbfs(math.sqrt(sum(value * value for value in mix) / len(mix))), 2),
        },
        "lineChecks": line_checks,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
