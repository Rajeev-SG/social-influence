#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def rms(samples: list[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


def main() -> None:
    timing = json.loads((ROOT / "assets" / "audio" / "timing.json").read_text())
    with wave.open(str(ROOT / "assets" / "audio" / "mix.wav"), "rb") as handle:
        sample_rate = handle.getframerate()
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        raw = handle.readframes(handle.getnframes())
    if sample_width != 2:
        raise ValueError("Audio analysis expects 16-bit PCM")
    values = [value / 32768.0 for (value,) in struct.iter_unpack("<h", raw)]
    mono = [
        sum(values[index : index + channels]) / channels
        for index in range(0, len(values), channels)
    ]
    duration = len(mono) / sample_rate
    overall_rms = rms(mono)
    peak = max(abs(sample) for sample in mono)
    clipped = sum(1 for sample in mono if abs(sample) >= 0.999)
    active = [abs(sample) > 0.015 for sample in mono]
    longest_silence = 0
    current_silence = 0
    for sample_active in active:
        if sample_active:
            current_silence = 0
        else:
            current_silence += 1
            longest_silence = max(longest_silence, current_silence)

    line_levels = []
    for line in timing["lines"]:
        start = int(float(line["start"]) * sample_rate)
        end = int(float(line["end"]) * sample_rate)
        line_rms = rms(mono[start:end])
        line_levels.append(
            {
                "id": line["id"],
                "start": line["start"],
                "end": line["end"],
                "rms": round(line_rms, 6),
                "dbfs": round(20 * math.log10(max(line_rms, 1e-9)), 2),
                "active": line_rms > 0.015,
            }
        )

    result = {
        "path": "assets/audio/mix.wav",
        "decoded": True,
        "sample_rate": sample_rate,
        "channels": channels,
        "duration": round(duration, 4),
        "expected_duration": timing["total_duration"],
        "rms": round(overall_rms, 6),
        "dbfs": round(20 * math.log10(max(overall_rms, 1e-9)), 2),
        "peak": round(peak, 6),
        "clipped_samples": clipped,
        "longest_silence_seconds": round(longest_silence / sample_rate, 4),
        "line_levels": line_levels,
        "all_narration_lines_active": all(item["active"] for item in line_levels),
        "duration_matches": abs(duration - float(timing["total_duration"])) < 0.01,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
