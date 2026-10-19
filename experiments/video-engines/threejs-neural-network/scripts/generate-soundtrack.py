#!/usr/bin/env python3
"""Synthesize an original restrained stereo bed and cue-aligned effects."""

import json
import math
import random
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMING = ROOT / "assets" / "audio" / "timing.json"
OUTPUT = ROOT / "assets" / "audio" / "soundscape.wav"
SAMPLE_RATE = 48000


def write_stereo(path: Path, left: list[float], right: list[float]) -> None:
    frames = bytearray()
    for sample_left, sample_right in zip(left, right):
        frames += struct.pack(
            "<hh",
            max(-32767, min(32767, round(sample_left * 32767))),
            max(-32767, min(32767, round(sample_right * 32767))),
        )
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(frames)


def main() -> None:
    timing = json.loads(TIMING.read_text())
    duration = timing["duration"]
    count = round(duration * SAMPLE_RATE)
    left = [0.0] * count
    right = [0.0] * count
    randomizer = random.Random(180)

    for index in range(count):
        t = index / SAMPLE_RATE
        breath = 0.72 + 0.28 * math.sin(2 * math.pi * 0.055 * t)
        left[index] += 0.0062 * breath * math.sin(2 * math.pi * 73.416 * t)
        right[index] += 0.0058 * breath * math.sin(2 * math.pi * 73.49 * t)
        left[index] += 0.0034 * math.sin(2 * math.pi * 146.832 * t + 0.2)
        right[index] += 0.0031 * math.sin(2 * math.pi * 220.1 * t - 0.15)

    cue_starts = [cue["start"] for cue in timing["cues"]]
    for cue_index, start in enumerate(cue_starts):
        note = [392.0, 440.0, 493.883, 587.33, 659.255][cue_index % 5]
        effect_length = round(0.34 * SAMPLE_RATE)
        effect_start = round(start * SAMPLE_RATE)
        for step in range(effect_length):
            if effect_start + step >= count:
                break
            u = step / SAMPLE_RATE
            envelope = math.exp(-u * 13.5) * (1 - math.exp(-u * 170))
            tone = (math.sin(2 * math.pi * note * u) + 0.22 * math.sin(2 * math.pi * note * 2.01 * u)) * envelope
            pan = 0.28 + cue_index * 0.1
            left[effect_start + step] += tone * 0.032 * (1 - pan)
            right[effect_start + step] += tone * 0.032 * pan

    for transition_index, start in enumerate(cue_starts[1:-1], start=1):
        length = round(0.72 * SAMPLE_RATE)
        effect_start = max(0, round((start - 0.22) * SAMPLE_RATE))
        previous = 0.0
        for step in range(length):
            if effect_start + step >= count:
                break
            u = step / SAMPLE_RATE
            white = randomizer.uniform(-1.0, 1.0)
            smooth = previous * 0.91 + white * 0.09
            previous = smooth
            whoosh = (white - smooth) * math.sin(math.pi * u / 0.72) ** 3
            gain = 0.015 if transition_index % 2 else 0.011
            left[effect_start + step] += whoosh * gain
            right[effect_start + step] += whoosh * gain * 0.78

    if cue_starts:
        resolve_start = round(cue_starts[-1] * SAMPLE_RATE)
        for index in range(resolve_start, count):
            u = (index - resolve_start) / SAMPLE_RATE
            envelope = math.exp(-u * 1.1) * (1 - math.exp(-u * 10))
            tone = math.sin(2 * math.pi * 146.832 * u) * envelope * 0.016
            left[index] += tone
            right[index] += tone

    for index in range(count):
        t = index / SAMPLE_RATE
        fade = min(1.0, t / 0.8) * min(1.0, max(0.0, duration - t) / 0.65)
        left[index] *= fade
        right[index] *= fade

    peak = max(max(abs(value) for value in left), max(abs(value) for value in right))
    write_stereo(OUTPUT, left, right)
    print(f"soundtrack duration={duration:.3f}s peak={peak:.4f}")


if __name__ == "__main__":
    main()
