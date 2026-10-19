"""Original restrained sound design: no sampled or licensed media assets."""
from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src/timing.json").read_text())
SR = 48_000
DURATION = TIMING["duration"]
N = round(DURATION * SR)
t = np.arange(N, dtype=np.float64) / SR
left = np.zeros(N, dtype=np.float64)
right = np.zeros(N, dtype=np.float64)
rng = np.random.default_rng(20261019)


def place(signal: np.ndarray, at: float, gain: float = 1.0, pan: float = 0.5) -> None:
    start = max(0, round(at * SR))
    end = min(N, start + len(signal))
    if end <= start:
        return
    body = signal[: end - start] * gain
    left[start:end] += body * (1.0 - pan)
    right[start:end] += body * pan


def envelope(n: int, attack: float, release: float) -> np.ndarray:
    u = np.arange(n, dtype=np.float64) / SR
    return (1.0 - np.exp(-u / max(attack, 1e-4))) * np.exp(-u / max(release, 1e-4))


# A quiet suspended bed keeps the film tactile without competing with narration.
for freq, amp, detune in (
    (73.416, 0.0032, 0.00),
    (110.0, 0.0024, 0.05),
    (146.832, 0.0017, -0.04),
    (220.0, 0.0011, 0.07),
):
    motion = 0.82 + 0.18 * np.sin(2 * np.pi * 0.045 * t + freq)
    left += amp * motion * np.sin(2 * np.pi * freq * t)
    right += amp * motion * np.sin(2 * np.pi * (freq + detune) * t)


def whoosh(duration: float = 0.46, reverse: bool = False) -> np.ndarray:
    n = round(duration * SR)
    u = np.arange(n, dtype=np.float64) / SR
    noise = rng.normal(0.0, 1.0, n)
    smooth = np.convolve(noise, np.ones(23) / 23, mode="same")
    band = noise - smooth
    env = np.sin(np.pi * u / duration) ** 2
    if reverse:
        band = band[::-1]
        env = env[::-1]
    return band * env * 0.055


def click(freq: float = 520.0, duration: float = 0.18) -> np.ndarray:
    n = round(duration * SR)
    u = np.arange(n, dtype=np.float64) / SR
    env = envelope(n, 0.002, 0.035)
    return (
        np.sin(2 * np.pi * freq * u)
        + 0.28 * np.sin(2 * np.pi * freq * 2.01 * u)
    ) * env * 0.075


def thunk() -> np.ndarray:
    n = round(0.32 * SR)
    u = np.arange(n, dtype=np.float64) / SR
    sweep = 84.0 - 32.0 * u
    return np.sin(2 * np.pi * sweep * u) * envelope(n, 0.001, 0.07) * 0.10


def chime(step: int) -> np.ndarray:
    n = round(0.58 * SR)
    u = np.arange(n, dtype=np.float64) / SR
    freq = 392.0 * 2 ** ([0, 7, 12, 16][step % 4] / 12.0)
    env = envelope(n, 0.003, 0.16)
    return (
        np.sin(2 * np.pi * freq * u)
        + 0.22 * np.sin(2 * np.pi * freq * 2.0 * u)
        + 0.08 * np.sin(2 * np.pi * freq * 3.0 * u)
    ) * env * 0.065


cues = TIMING["cues"]
c0, c1, c2, c3, c4, c5 = cues

# The bucket-toss analogy gets physical cues exactly on its action beats.
place(whoosh(0.52), c1["start"] + 0.34, 1.0, 0.35)
place(thunk(), c1["end"] - 0.12, 1.0, 0.28)
place(chime(1), c2["start"] + 0.18, 1.0, 0.62)
place(click(430.0), c3["start"] + 0.78, 0.75, 0.42)
place(click(560.0), c3["start"] + 1.12, 0.75, 0.58)
place(whoosh(0.48), c3["end"] - 0.35, 0.82, 0.68)
place(chime(3), c3["end"] - 0.05, 0.75, 0.62)

# Four restrained feedback ticks map to guess, compare, nudge and repeat.
for i, offset in enumerate((0.35, 2.45, 5.05, 7.25)):
    place(click((360.0, 440.0, 520.0, 660.0)[i]), c4["start"] + offset, 0.55, 0.3 + i * 0.13)

place(whoosh(0.58, reverse=True), c5["start"] - 0.18, 0.75, 0.50)
place(chime(2), c5["start"] + 0.52, 0.85, 0.50)

# Closing resolve.
start = round(c5["start"] * SR)
u = t[: N - start]
resolve = (
    np.sin(2 * np.pi * 146.832 * u)
    + 0.34 * np.sin(2 * np.pi * 220.0 * u)
    + 0.12 * np.sin(2 * np.pi * 293.665 * u)
) * np.exp(-u * 1.2) * (1.0 - np.exp(-u * 12.0)) * 0.045
left[start:] += resolve
right[start:] += resolve

fade_in = np.clip(t / 0.7, 0.0, 1.0)
fade_out = np.clip((DURATION - t) / 0.9, 0.0, 1.0)
stereo = np.stack((left, right), axis=1) * (fade_in * fade_out)[:, None]
peak = float(np.max(np.abs(stereo)))
if peak > 0.92:
    stereo *= 0.92 / peak

with wave.open(str(ROOT / "assets/audio/soundscape.wav"), "wb") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(SR)
    wav.writeframes((np.clip(stereo, -1.0, 1.0) * 32767).astype("<i2").tobytes())

print(f"Soundscape: {DURATION:.3f}s, {N} samples, peak {peak:.4f}")
