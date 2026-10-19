import json
import math
import struct
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIMING_PATH = ROOT / "narration" / "timing.json"
OUTPUT_PATH = ROOT / "assets" / "audio" / "soundtrack.wav"
SAMPLE_RATE = 48000
DURATION = 88.8


def add_tone(samples, start, duration, frequency, amplitude, decay=1.0, pan=0.0):
    start_index = int(start * SAMPLE_RATE)
    count = int(duration * SAMPLE_RATE)
    for offset in range(count):
        index = start_index + offset
        if index >= len(samples[0]):
            break
        t = offset / SAMPLE_RATE
        envelope = math.exp(-decay * t)
        value = amplitude * envelope * math.sin(2 * math.pi * frequency * t)
        left_gain = math.sqrt((1.0 - pan) / 2.0)
        right_gain = math.sqrt((1.0 + pan) / 2.0)
        samples[0][index] += value * left_gain
        samples[1][index] += value * right_gain


def add_whoosh(samples, start, duration, amplitude):
    start_index = int(start * SAMPLE_RATE)
    count = int(duration * SAMPLE_RATE)
    previous = [0.0, 0.0]
    seed = 0x2026 + int(start * 1000)
    for offset in range(count):
        index = start_index + offset
        if index >= len(samples[0]):
            break
        t = offset / count
        envelope = math.sin(math.pi * t) ** 2
        seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
        noise = ((seed / 0xFFFFFFFF) * 2.0 - 1.0)
        for channel in range(2):
            high_passed = noise - previous[channel] * 0.82
            previous[channel] = noise
            pan = -0.55 + 1.1 * t if channel == 0 else 0.55 - 1.1 * t
            samples[channel][index] += amplitude * envelope * high_passed * (0.65 + 0.35 * abs(pan))


def build():
    timing = json.loads(TIMING_PATH.read_text())
    frame_count = int(DURATION * SAMPLE_RATE)
    samples = [[0.0] * frame_count, [0.0] * frame_count]

    chord_progression = [
        (55.00, 82.41, 110.00),
        (61.74, 92.50, 123.47),
        (49.00, 73.42, 98.00),
        (55.00, 82.41, 130.81),
    ]
    chord_seconds = 8.0
    for chord_index in range(math.ceil(DURATION / chord_seconds)):
        start = chord_index * chord_seconds
        frequencies = chord_progression[chord_index % len(chord_progression)]
        for tone_index, frequency in enumerate(frequencies):
            add_tone(
                samples,
                start,
                chord_seconds + 1.4,
                frequency,
                0.018 if tone_index else 0.026,
                decay=0.055,
                pan=-0.4 + tone_index * 0.4,
            )
            add_tone(
                samples,
                start,
                chord_seconds + 1.4,
                frequency * 2.003,
                0.005,
                decay=0.09,
                pan=0.5 - tone_index * 0.35,
            )

    for pulse_start in [x * 2.0 for x in range(int(DURATION / 2.0))]:
        add_tone(samples, pulse_start, 1.1, 72.0, 0.045, decay=4.2)

    for cue in timing["cues"]:
        add_tone(samples, cue["start"], 0.18, 820.0, 0.012, decay=13.0, pan=0.35)
        add_tone(samples, cue["start"] + 0.025, 0.12, 1230.0, 0.007, decay=18.0, pan=-0.25)

    for boundary in [6.5, 16.1, 25.15, 34.2, 43.55, 53.45, 64.9, 79.8]:
        add_whoosh(samples, boundary - 0.75, 1.25, 0.042)

    add_tone(samples, 0.0, 2.8, 110.0, 0.07, decay=1.15)
    add_tone(samples, 80.0, 5.4, 55.0, 0.065, decay=0.42)
    add_tone(samples, 80.0, 5.4, 82.41, 0.032, decay=0.48)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT_PATH), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for index in range(frame_count):
            for channel in range(2):
                value = max(-1.0, min(1.0, samples[channel][index]))
                frames.extend(struct.pack("<h", int(value * 32767)))
        output.writeframes(frames)

    print(f"Wrote {OUTPUT_PATH} ({DURATION:.3f}s)")


if __name__ == "__main__":
    build()
