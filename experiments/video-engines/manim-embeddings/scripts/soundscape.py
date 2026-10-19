"""Synthesize an original restrained score and event-synchronized effects."""

from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src/timing.json").read_text())
SAMPLE_RATE = 48_000
DURATION = TIMING["duration"]


def add_tone(left, right, start, frequency, duration, amplitude, pan=0.5):
    count = int(duration * SAMPLE_RATE)
    time = np.arange(count) / SAMPLE_RATE
    envelope = (1 - np.exp(-time * 180)) * np.exp(-time * 8.5)
    tone = (
        np.sin(2 * np.pi * frequency * time)
        + 0.22 * np.sin(2 * np.pi * frequency * 2.004 * time)
        + 0.08 * np.sin(2 * np.pi * frequency * 3.01 * time)
    ) * envelope * amplitude
    pos = int(start * SAMPLE_RATE)
    end = min(pos + count, len(left))
    if end > pos:
        left[pos:end] += tone[: end - pos] * (1 - pan)
        right[pos:end] += tone[: end - pos] * pan


def add_whoosh(left, right, start, duration=0.62, amplitude=0.055):
    count = int(duration * SAMPLE_RATE)
    time = np.arange(count) / SAMPLE_RATE
    rng = np.random.default_rng(round(start * 1000))
    noise = rng.normal(0, 1, count)
    low = np.convolve(noise, np.ones(18) / 18, mode="same")
    high = noise - low
    envelope = np.sin(np.pi * time / duration) ** 3
    whoosh = high * envelope * amplitude
    pos = max(0, int((start - duration * 0.48) * SAMPLE_RATE))
    end = min(pos + count, len(left))
    if end > pos:
        width = end - pos
        left[pos:end] += whoosh[:width]
        right[pos:end] += whoosh[:width] * 0.82


def main():
    count = int(round(DURATION * SAMPLE_RATE))
    time = np.arange(count) / SAMPLE_RATE
    left = np.zeros(count)
    right = np.zeros(count)

    # Quiet suspended A-minor bed. It sits beneath speech rather than driving it.
    for frequency, amplitude in [(55.0, 0.0040), (110.0, 0.0032), (164.81, 0.0021), (220.0, 0.0014)]:
        drift = 0.82 + 0.18 * np.sin(2 * np.pi * 0.045 * time + frequency)
        left += amplitude * drift * np.sin(2 * np.pi * frequency * time)
        right += amplitude * drift * np.sin(2 * np.pi * (frequency + 0.06) * time)

    cue_starts = [cue["start"] for cue in TIMING["cues"]]
    for index, start in enumerate(cue_starts):
        add_tone(left, right, max(0, start - 0.08), [220.0, 246.94, 293.66, 329.63, 392.0][index], 0.42, 0.022, 0.28 + index * 0.11)

    # Spatial relationship events, matched to the map actions.
    events = [
        (cue_starts[1] + 1.55, 329.63, 0.032, 0.30),
        (cue_starts[2] + 0.75, 392.00, 0.038, 0.38),
        (cue_starts[2] + 1.55, 440.00, 0.038, 0.52),
        (cue_starts[2] + 2.45, 493.88, 0.038, 0.66),
        (cue_starts[2] + 3.75, 220.00, 0.030, 0.82),
        (cue_starts[3] + 1.10, 523.25, 0.035, 0.42),
        (cue_starts[3] + 2.35, 587.33, 0.035, 0.62),
    ]
    for start, frequency, amplitude, pan in events:
        add_tone(left, right, start, frequency, 0.48, amplitude, pan)

    for index, start in enumerate(cue_starts[1:], start=1):
        add_whoosh(left, right, start, 0.58 + 0.04 * index, 0.042)

    # Final resolve: a low tone and a small bright harmonic.
    add_tone(left, right, cue_starts[-1], 110.0, 1.5, 0.032, 0.5)
    add_tone(left, right, cue_starts[-1] + 0.12, 440.0, 1.15, 0.018, 0.5)

    fade_in = np.minimum(time / 0.35, 1)
    fade_out = np.minimum((DURATION - time) / 0.72, 1)
    fade = np.maximum(fade_in * fade_out, 0)
    stereo = np.stack([left * fade, right * fade], axis=-1)
    stereo = np.tanh(stereo * 1.18) * 0.72

    output = ROOT / "assets/audio/soundscape.wav"
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())

    peak = float(np.max(np.abs(stereo)))
    rms = float(np.sqrt(np.mean(stereo**2)))
    print(f"synthesized {output} duration={DURATION:.3f}s peak={peak:.4f} rms={rms:.4f}")


if __name__ == "__main__":
    main()
