"""Original restrained sound design and final stereo mix for the token explainer."""
from pathlib import Path
import json
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
cues = json.loads((ROOT / "assets/audio/narration-cues.json").read_text())["cues"]
duration = max(24.0, cues[-1]["end"] + 1.0)
t = np.arange(round(duration * SR)) / SR
rng = np.random.default_rng(42)
left = np.zeros(len(t), dtype=np.float64)
right = np.zeros(len(t), dtype=np.float64)

# Suspended low bed: a quiet, spacious floor beneath the speech.
for freq, amp in [(55.0, 0.010), (82.41, 0.006), (110.0, 0.004), (164.81, 0.0024)]:
    lfo = 0.82 + 0.18 * np.sin(2 * np.pi * 0.045 * t + freq / 20)
    left += amp * lfo * np.sin(2 * np.pi * freq * t)
    right += amp * lfo * np.sin(2 * np.pi * (freq + 0.08) * t)

def place(signal, start, pan=0.5):
    p = int(max(0, start) * SR)
    e = min(len(left), p + len(signal))
    if e <= p:
        return
    left[p:e] += signal[:e-p] * (1 - pan)
    right[p:e] += signal[:e-p] * pan

def tick(start, index):
    n = int(0.42 * SR)
    u = np.arange(n) / SR
    env = np.exp(-u * 17) * (1 - np.exp(-u * 180))
    f = 520 * 2 ** ((index % 5) / 12)
    tone = (np.sin(2 * np.pi * f * u) + 0.18 * np.sin(2 * np.pi * 2.01 * f * u)) * env * 0.075
    place(tone, start, 0.25 + 0.12 * (index % 5))
    place(tone * 0.13, start + 0.17, 0.72)

def whoosh(start):
    n = int(0.62 * SR)
    u = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    smooth = np.convolve(noise, np.ones(23) / 23, mode="same")
    fine = np.convolve(noise, np.ones(5) / 5, mode="same")
    env = np.sin(np.pi * u / 0.62) ** 3
    signal = (fine - smooth) * env * 0.045
    place(signal, start - 0.22, 0.34)
    place(signal * 0.82, start - 0.15, 0.66)

# Cue-linked details: one small click per caption and a soft air move at chapter shifts.
for i, cue in enumerate(cues):
    tick(cue["start"] + 0.02, i)
    if i in (1, 3, 4, 5, 6):
        whoosh(cue["start"])

# Token reveal ticks inside the first split phase.
for i in range(5):
    tick(cues[1]["end"] + 0.32 + i * 0.19, i + 2)

# Closing resolve.
p = int(21.65 * SR)
u = t[:len(t)-p]
resolve = np.sin(2 * np.pi * 110 * u) * np.exp(-u * 1.1) * (1 - np.exp(-u * 10)) * 0.07
left[p:] += resolve
right[p:] += resolve

fade = np.minimum(t / 0.55, 1.0) * np.minimum((duration - t) / 1.15, 1.0)
stereo = np.stack([left * fade, right * fade], axis=1)
stereo = np.clip(stereo, -0.96, 0.96)

def write_wav(path, data, channels=2):
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes((data * 32767).astype("<i2").tobytes())

write_wav(ROOT / "assets/audio/soundscape.wav", stereo)

narration_path = ROOT / "assets/audio/narration.wav"
with wave.open(str(narration_path), "rb") as handle:
    narr_sr = handle.getframerate()
    narr_channels = handle.getnchannels()
    narr = np.frombuffer(handle.readframes(handle.getnframes()), dtype="<i2").astype(np.float64) / 32767
    narr = narr.reshape(-1, narr_channels)
if narr_sr != SR:
    raise SystemExit(f"unexpected narration sample rate: {narr_sr}")
if narr_channels == 1:
    narr = np.repeat(narr, 2, axis=1)
mix = np.zeros_like(stereo)
mix[:len(narr)] += narr[:len(mix)] * 1.0
mix += stereo * 0.72
mix = np.clip(mix, -0.98, 0.98)
write_wav(ROOT / "assets/audio/mix.wav", mix)
for temporary in ("narration-raw.wav", "narration-cues.json"):
    (ROOT / "assets/audio" / temporary).unlink(missing_ok=True)
print(f"soundscape duration={duration:.3f}s peak={np.max(np.abs(stereo)):.3f} mix_peak={np.max(np.abs(mix)):.3f}")
