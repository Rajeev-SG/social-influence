#!/usr/bin/env python3
"""Create a restrained original stereo sound bed and mix it under Kokoro narration."""

from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMING_PATH = ROOT / "src" / "timing.json"
NARRATION_PATH = ROOT / "assets" / "audio" / "narration.wav"
BED_PATH = ROOT / "assets" / "audio" / "soundtrack.wav"
MIX_PATH = ROOT / "assets" / "audio" / "mix.wav"


def read_pcm16(path: Path) -> tuple[int, list[list[float]]]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_rate = handle.getframerate()
        width = handle.getsampwidth()
        if width != 2:
            raise ValueError(f"expected 16-bit PCM, got {width * 8}-bit")
        frames = handle.readframes(handle.getnframes())
    values = struct.unpack("<" + "h" * (len(frames) // 2), frames)
    channel_data = [[0.0] * (len(values) // channels) for _ in range(channels)]
    for index, value in enumerate(values):
        channel_data[index % channels][index // channels] = value / 32768.0
    return sample_rate, channel_data


def write_pcm16(path: Path, sample_rate: int, channels: list[list[float]]) -> None:
    channel_count = len(channels)
    frame_count = len(channels[0])
    values = []
    for frame in range(frame_count):
        for channel in channels:
            clipped = max(-1.0, min(1.0, channel[frame]))
            values.append(int(round(clipped * 32767.0)))
    packed = struct.pack("<" + "h" * len(values), *values)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channel_count)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(packed)


def one_pole_lowpass(values: list[float], cutoff_hz: float, sample_rate: int) -> list[float]:
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff_hz / sample_rate)
    state = 0.0
    output = []
    for value in values:
        state += alpha * (value - state)
        output.append(state)
    return output


def add_tone(
    target: list[list[float]],
    sample_rate: int,
    start: float,
    duration: float,
    frequency: float,
    amplitude: float,
    decay: float = 7.0,
    pan: float = 0.0,
) -> None:
    start_index = int(start * sample_rate)
    count = int(duration * sample_rate)
    left_gain = math.sqrt(max(0.0, 0.5 - pan * 0.5))
    right_gain = math.sqrt(max(0.0, 0.5 + pan * 0.5))
    for offset in range(count):
        index = start_index + offset
        if index >= len(target[0]):
            break
        seconds = offset / sample_rate
        envelope = math.exp(-decay * seconds) * min(1.0, seconds / 0.008)
        sample = math.sin(2.0 * math.pi * frequency * seconds) * amplitude * envelope
        target[0][index] += sample * left_gain * 1.42
        target[1][index] += sample * right_gain * 1.42


def add_noise_swell(
    target: list[list[float]],
    sample_rate: int,
    start: float,
    duration: float,
    amplitude: float,
    seed: int,
) -> None:
    start_index = int(start * sample_rate)
    count = int(duration * sample_rate)
    state = seed & 0x7FFFFFFF
    noise = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        noise.append((state / 0x3FFFFFFF) - 1.0)
    noise = one_pole_lowpass(noise, 820.0, sample_rate)
    for offset, value in enumerate(noise):
        index = start_index + offset
        if index >= len(target[0]):
            break
        u = offset / max(1, count - 1)
        envelope = math.sin(math.pi * u) ** 2
        sample = value * amplitude * envelope
        target[0][index] += sample * 0.72
        target[1][index] += sample * 0.88


def main() -> None:
    timing = json.loads(TIMING_PATH.read_text())
    sample_rate, narration = read_pcm16(NARRATION_PATH)
    frame_count = int(round(float(timing["duration"]) * sample_rate))
    if narration and len(narration[0]) < frame_count:
        pad = frame_count - len(narration[0])
        narration = [channel + [0.0] * pad for channel in narration]
    narration = [channel[:frame_count] for channel in narration]

    bed = [[0.0] * frame_count for _ in range(2)]
    for index in range(frame_count):
        seconds = index / sample_rate
        slow = 0.55 + 0.45 * math.sin(2.0 * math.pi * 0.075 * seconds)
        drone = (
            math.sin(2.0 * math.pi * 55.0 * seconds) * 0.017
            + math.sin(2.0 * math.pi * 110.0 * seconds + 0.4) * 0.006
            + math.sin(2.0 * math.pi * 164.8 * seconds + 1.1) * 0.0035 * slow
        )
        bed[0][index] += drone * 0.92
        bed[1][index] += drone * 1.08

    scene_starts = [0.0] + [cue["start"] for cue in timing["cues"][1:]]
    frequencies = [520.0, 640.0, 720.0, 840.0, 1040.0]
    for index, start in enumerate(scene_starts):
        add_tone(bed, sample_rate, start, 0.32, frequencies[min(index, len(frequencies) - 1)], 0.028, 10.0, -0.22 + index * 0.1)
        add_tone(bed, sample_rate, start + 0.025, 0.22, frequencies[min(index, len(frequencies) - 1)] * 1.5, 0.012, 13.0, 0.3)
    for index, cue in enumerate(timing["cues"]):
        add_noise_swell(bed, sample_rate, max(0.0, cue["start"] - 0.11), 0.25, 0.012 + index * 0.001, 8123 + index * 97)

    mixed = [[0.0] * frame_count for _ in range(2)]
    for index in range(frame_count):
        seconds = index / sample_rate
        voice_gain = 1.0
        if seconds < 0.14:
            voice_gain = seconds / 0.14
        for channel in range(2):
            voice = narration[channel][index] * voice_gain
            value = voice * 1.02 + bed[channel][index]
            mixed[channel][index] = math.tanh(value * 1.08) / 1.08

    peak = max(abs(value) for channel in mixed for value in channel) or 1.0
    gain = 0.82 / peak
    mixed = [[value * gain for value in channel] for channel in mixed]
    bed = [[value * gain for value in channel] for channel in bed]

    BED_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_pcm16(BED_PATH, sample_rate, bed)
    write_pcm16(MIX_PATH, sample_rate, mixed)
    print(f"mix duration: {frame_count / sample_rate:.3f}s, peak after normalize: 0.820")


if __name__ == "__main__":
    main()
