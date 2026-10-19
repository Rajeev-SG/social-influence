"""Original procedural stereo score and event sound design. No sampled assets."""

from array import array
from pathlib import Path
import json
import math
import random
import wave


ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src" / "timing.json").read_text())
SR = 48000
DURATION = TIMING["duration"]
N = round(DURATION * SR)
left = [0.0] * N
right = [0.0] * N


def add(start, samples, pan=0.5, gain=1.0):
    pos = round(start * SR)
    for i, value in enumerate(samples):
        j = pos + i
        if j >= N:
            break
        left[j] += value * (1.0 - pan) * gain
        right[j] += value * pan * gain


for freq, amp, phase in [
    (73.416, 0.010, 0.0),
    (110.0, 0.008, 0.7),
    (146.832, 0.006, 1.4),
    (220.0, 0.0035, 2.1),
    (293.665, 0.0022, 2.8),
]:
    for i in range(N):
        t = i / SR
        envelope = 0.72 + 0.28 * math.sin(2 * math.pi * 0.055 * t + phase)
        value = amp * envelope * math.sin(2 * math.pi * freq * t + 0.08 * math.sin(2 * math.pi * 0.09 * t))
        left[i] += value
        right[i] += value * 0.92


events = [(cue["start"], i) for i, cue in enumerate(TIMING["cues"])]
examples_start = next(c["start"] for c in TIMING["cues"] if c["id"] == "examples")
events.extend((examples_start + offset, i + 3) for i, offset in enumerate([0.52, 1.15, 1.78]))
for at, index in events:
    duration = 0.46
    n = round(duration * SR)
    samples = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 17.0) * (1.0 - math.exp(-t * 220.0))
        freq = 420.0 * (2.0 ** ([0, 7, 12, 14, 19][index % 5] / 12.0))
        tone = math.sin(2 * math.pi * freq * t) + 0.22 * math.sin(2 * math.pi * 2.01 * freq * t)
        samples.append(tone * env * 0.085)
    add(at, samples, 0.28 + 0.44 * ((index % 5) / 4.0), 1.0)
    add(at + 0.15, [x * 0.10 for x in samples], 0.72, 1.0)


def whoosh(start, duration=0.72):
    rng = random.Random(round(start * 1000))
    n = round(duration * SR)
    raw = [rng.uniform(-1.0, 1.0) for _ in range(n)]
    smooth = 0.0
    samples = []
    for i, value in enumerate(raw):
        smooth = smooth * 0.86 + value * 0.14
        envelope = math.sin(math.pi * i / n) ** 3
        samples.append((value - smooth) * envelope * 0.045)
    add(start - 0.18, samples, 0.46, 1.0)
    add(start - 0.13, samples, 0.58, 0.70)


for cue_id in ["course", "analogy", "settings", "specialist"]:
    whoosh(next(c["start"] for c in TIMING["cues"] if c["id"] == cue_id))


for cue_id, strength in [("examples", 0.052), ("adapt", 0.060), ("settings", 0.082)]:
    at = next(c["start"] for c in TIMING["cues"] if c["id"] == cue_id)
    n = round(0.58 * SR)
    samples = []
    for i in range(n):
        t = i / SR
        freq = 82.0 - 22.0 * t
        env = math.exp(-t * 10.5) * (1.0 - math.exp(-t * 150.0))
        samples.append(math.sin(2 * math.pi * freq * t) * env * strength)
    add(at, samples, 0.5, 1.0)


at = next(c["start"] for c in TIMING["cues"] if c["id"] == "specialist")
for offset, freq, amp in [(0.0, 146.832, 0.050), (0.38, 220.0, 0.034)]:
    n = min(round(1.35 * SR), N - round((at + offset) * SR))
    samples = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 1.35) * (1.0 - math.exp(-t * 12.0))
        samples.append(math.sin(2 * math.pi * freq * t) * env * amp)
    add(at + offset, samples, 0.5, 1.0)


fade_in = min(round(0.8 * SR), N)
fade_out = min(round(1.0 * SR), N)
for i in range(N):
    fade = min(1.0, i / fade_in, (N - 1 - i) / fade_out)
    left[i] *= fade
    right[i] *= fade

peak = max(max(abs(x) for x in left), max(abs(x) for x in right), 1e-9)
scale = min(1.0, 0.72 / peak)
frames = array("h")
for i in range(N):
    frames.append(round(max(-1.0, min(1.0, left[i] * scale)) * 32767))
    frames.append(round(max(-1.0, min(1.0, right[i] * scale)) * 32767))

out = ROOT / "assets" / "audio" / "soundscape.wav"
with wave.open(str(out), "wb") as handle:
    handle.setnchannels(2)
    handle.setsampwidth(2)
    handle.setframerate(SR)
    handle.writeframes(frames.tobytes())

print(f"wrote {out} ({DURATION:.3f}s, peak before scale={peak:.4f})")
