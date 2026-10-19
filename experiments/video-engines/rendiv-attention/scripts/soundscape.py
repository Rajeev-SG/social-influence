"""Original restrained stereo sound design using only Python's standard library."""
import json
import math
import random
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src" / "timing.json").read_text())
SR = 48000
DURATION = float(TIMING["duration"])
N = int(DURATION * SR)
left = [0.0] * N
right = [0.0] * N
rng = random.Random(82)


def add_tone(start, duration, frequency, amp, pan=0.5, decay=1.0, phase=0.0):
    start_i = max(0, int(start * SR))
    count = min(int(duration * SR), N - start_i)
    for i in range(count):
        t = i / SR
        env = math.exp(-t * decay) * (1 - math.exp(-t * 180))
        value = math.sin(2 * math.pi * frequency * t + phase) * amp * env
        left[start_i + i] += value * (1 - pan)
        right[start_i + i] += value * pan


def add_noise(start, duration, amp, pan=0.5):
    start_i = max(0, int(start * SR))
    count = min(int(duration * SR), N - start_i)
    smooth = 0.0
    for i in range(count):
        raw = rng.uniform(-1, 1)
        smooth += (raw - smooth) * 0.18
        env = math.sin(math.pi * i / max(1, count)) ** 3
        value = (raw - smooth) * amp * env
        left[start_i + i] += value * (1 - pan)
        right[start_i + i] += value * pan


# A quiet suspended harmonic bed, deliberately underneath the speech.
for frequency, amplitude in [(73.416, 0.0038), (110.0, 0.0028), (146.832, 0.0018), (220.0, 0.0012)]:
    for i in range(N):
        t = i / SR
        env = 0.72 + 0.28 * math.sin(2 * math.pi * 0.035 * t + frequency)
        value = math.sin(2 * math.pi * frequency * t + 0.10 * math.sin(2 * math.pi * 0.09 * t)) * amplitude * env
        left[i] += value * 0.92
        right[i] += value * 1.08

# Short glassy markers at scene handoffs and the relationship reveal.
for cue_index, cue in enumerate(TIMING["cues"]):
    add_tone(cue["start"] + 0.02, 0.42, 440 * (2 ** ((cue_index % 5) * 7 / 12)), 0.040, 0.32 + 0.36 * (cue_index % 4) / 3, 8.0)
    if cue_index in (1, 2, 3, 4, 7):
        add_noise(cue["start"] - 0.16, 0.52, 0.022, 0.42 + 0.16 * (cue_index % 3))

for start in (6.15, 9.85, 13.30, 18.45):
    add_tone(start, 0.58, 76, 0.055, 0.5, 10.0)

for start in (2.65, 15.55, 20.35):
    add_tone(start, 0.65, 293.665, 0.032, 0.65, 3.0)
    add_tone(start + 0.11, 0.52, 440.0, 0.022, 0.35, 3.6)

# Fade the edges and write signed 16-bit stereo.
for i in range(N):
    t = i / SR
    fade = min(1.0, t / 0.55) * min(1.0, (DURATION - t) / 0.65)
    left[i] *= fade
    right[i] *= fade

peak = max(max(abs(v) for v in left), max(abs(v) for v in right), 1e-9)
scale = min(1.0, 0.72 / peak)
with wave.open(str(ROOT / "assets" / "audio" / "soundscape.wav"), "wb") as handle:
    handle.setnchannels(2)
    handle.setsampwidth(2)
    handle.setframerate(SR)
    frames = bytearray()
    for i in range(N):
        frames += struct.pack("<hh", int(max(-1, min(1, left[i] * scale)) * 32767), int(max(-1, min(1, right[i] * scale)) * 32767))
    handle.writeframes(frames)
print(f"sound design: {DURATION:.3f}s peak before scale {peak:.4f}")
