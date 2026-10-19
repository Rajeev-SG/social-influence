"""Original procedural score and explanatory sound design. No sampled assets."""

from __future__ import annotations

import json
import math
import random
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src" / "timing.json").read_text())
SAMPLE_RATE = 48_000
DURATION = TIMING["duration"] + 1.25
COUNT = round(DURATION * SAMPLE_RATE)
left = [0.0] * COUNT
right = [0.0] * COUNT
rng = random.Random(184)


def add(start: float, samples: list[float], pan: float = 0.5, gain: float = 1.0) -> None:
    pos = round(start * SAMPLE_RATE)
    for i, value in enumerate(samples):
        at = pos + i
        if 0 <= at < COUNT:
            left[at] += value * (1.0 - pan) * gain
            right[at] += value * pan * gain


def envelope(index: int, attack: float, release: float) -> float:
    t = index / SAMPLE_RATE
    return min(1.0, t / attack) * math.exp(-t / release)


# Warm suspended bed: quiet enough to preserve a clean teaching voice.
for i in range(COUNT):
    t = i / SAMPLE_RATE
    drift = 0.78 + 0.22 * math.sin(2 * math.pi * 0.055 * t)
    bed = (
        0.0085 * math.sin(2 * math.pi * 73.416 * t)
        + 0.0055 * math.sin(2 * math.pi * 110.0 * t + 0.2)
        + 0.0032 * math.sin(2 * math.pi * 146.832 * t + 0.45)
        + 0.0018 * math.sin(2 * math.pi * 220.0 * t + 0.8)
    ) * drift
    left[i] += bed
    right[i] += bed * 0.92

# Paper ticks: one per spoken cue, tuned to the visible caption/card reveals.
for cue_index, cue in enumerate(TIMING["cues"]):
    length = round(0.24 * SAMPLE_RATE)
    tick = []
    for i in range(length):
        t = i / SAMPLE_RATE
        f = [420, 523.25, 659.25, 784, 587.33, 880][cue_index]
        value = (
            math.sin(2 * math.pi * f * t)
            + 0.22 * math.sin(2 * math.pi * f * 2.01 * t)
        ) * envelope(i, 0.002, 0.055) * 0.10
        tick.append(value)
    add(cue["start"] - 0.025, tick, pan=0.32 + 0.07 * cue_index, gain=0.82)

# A paper slide marks the desk analogy.
slide_start = TIMING["cues"][1]["start"] - 0.18
slide_len = round(0.62 * SAMPLE_RATE)
slide = []
previous = 0.0
for i in range(slide_len):
    t = i / slide_len
    noise = rng.uniform(-1, 1)
    previous = previous * 0.72 + noise * 0.28
    band = noise - previous
    slide.append(band * (math.sin(math.pi * t) ** 2.2) * 0.075)
add(slide_start, slide, pan=0.42, gain=1.0)
add(slide_start + 0.045, slide, pan=0.64, gain=0.48)

# Low physical arrival as the limited desk reaches capacity.
capacity_start = TIMING["cues"][2]["start"]
thump_len = round(0.52 * SAMPLE_RATE)
thump = []
for i in range(thump_len):
    t = i / SAMPLE_RATE
    f = 78 - 24 * t
    thump.append(math.sin(2 * math.pi * f * t) * envelope(i, 0.004, 0.105) * 0.12)
add(capacity_start, thump, pan=0.5, gain=1.0)

# Two restrained sorting chimes for trim/summarize.
for at, pitch in [
    (TIMING["cues"][3]["start"] + 0.18, 659.25),
    (TIMING["cues"][3]["start"] + 0.42, 783.99),
]:
    length = round(0.42 * SAMPLE_RATE)
    note = [
        (math.sin(2 * math.pi * pitch * i / SAMPLE_RATE) + 0.18 * math.sin(2 * math.pi * pitch * 3 * i / SAMPLE_RATE))
        * envelope(i, 0.004, 0.12)
        * 0.075
        for i in range(length)
    ]
    add(at, note, pan=0.58, gain=1.0)

# Closing resolve under the final limitation.
resolve_start = TIMING["cues"][-1]["start"]
resolve_len = round(2.6 * SAMPLE_RATE)
resolve = []
for i in range(resolve_len):
    t = i / SAMPLE_RATE
    value = (
        math.sin(2 * math.pi * 146.832 * t)
        + 0.32 * math.sin(2 * math.pi * 220.0 * t)
    ) * math.exp(-t * 1.15) * (1 - math.exp(-t * 16)) * 0.055
    resolve.append(value)
add(resolve_start, resolve, pan=0.5, gain=1.0)

# Fade both edges to avoid encoder-clicks.
fade_in = round(0.12 * SAMPLE_RATE)
fade_out = round(0.42 * SAMPLE_RATE)
for i in range(COUNT):
    if i < fade_in:
        gain = i / fade_in
        left[i] *= gain
        right[i] *= gain
    if i >= COUNT - fade_out:
        gain = (COUNT - i) / fade_out
        left[i] *= gain
        right[i] *= gain

peak = max(max(abs(v) for v in left), max(abs(v) for v in right))
scale = 0.72 / max(peak, 0.0001)
frames = bytearray()
for i in range(COUNT):
    frames.extend(round(max(-1, min(1, left[i] * scale)) * 32767).to_bytes(2, "little", signed=True))
    frames.extend(round(max(-1, min(1, right[i] * scale)) * 32767).to_bytes(2, "little", signed=True))

output = ROOT / "assets" / "audio" / "soundscape.wav"
with wave.open(str(output), "wb") as handle:
    handle.setnchannels(2)
    handle.setsampwidth(2)
    handle.setframerate(SAMPLE_RATE)
    handle.writeframes(bytes(frames))

print(f"Soundscape: {DURATION:.3f}s, peak before scale={peak:.4f}, output={output}")
