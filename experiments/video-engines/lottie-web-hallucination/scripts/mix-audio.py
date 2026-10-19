#!/usr/bin/env python3
"""Concatenate Kokoro segments and synthesize a restrained sound bed."""

from __future__ import annotations

import array
import json
import math
import subprocess
import struct
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEGMENT_DIR = ROOT / ".render-tmp" / "tts-segments"
AUDIO_DIR = ROOT / "assets" / "audio"
NARRATION_PATH = ROOT / "src" / "narration.json"


def read_mono(path: Path) -> tuple[int, array.array]:
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=sample_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rate = int(probe.stdout.strip())
    decoded = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            str(rate),
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    )
    frames = decoded.stdout
    samples = array.array("h")
    samples.frombytes(frames)
    return rate, samples


def write_mono(path: Path, rate: int, samples: array.array) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(samples.tobytes())


def write_stereo(path: Path, rate: int, left: array.array, right: array.array) -> None:
    interleaved = array.array("h")
    for l_value, r_value in zip(left, right, strict=True):
        interleaved.append(l_value)
        interleaved.append(r_value)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(interleaved.tobytes())


def resample_linear(samples: array.array, source_rate: int, target_rate: int) -> array.array:
    if source_rate == target_rate:
        return array.array("h", samples)
    output = array.array("h", bytes(2 * round(len(samples) * target_rate / source_rate)))
    for index in range(len(output)):
        position = index * source_rate / target_rate
        left_index = min(len(samples) - 1, int(position))
        right_index = min(len(samples) - 1, left_index + 1)
        fraction = position - left_index
        value = samples[left_index] * (1 - fraction) + samples[right_index] * fraction
        output[index] = max(-32768, min(32767, int(value)))
    return output


def trim_silence(samples: array.array, rate: int, threshold: int = 220) -> array.array:
    """Remove Kokoro's leading/trailing silence while preserving a small breath."""
    if len(samples) < rate // 10:
        return samples
    window = max(1, round(rate * 0.01))
    energies = []
    for start in range(0, len(samples), window):
        chunk = samples[start : start + window]
        energies.append(math.sqrt(sum(value * value for value in chunk) / max(1, len(chunk))))
    active = [index for index, value in enumerate(energies) if value > threshold]
    if not active:
        return samples
    padding = round(rate * 0.035)
    first = max(0, active[0] * window - padding)
    last = min(len(samples), (active[-1] + 1) * window + padding)
    return samples[first:last]


def synth_effects(timings: list[dict], total_seconds: float, rate: int = 48_000) -> tuple[array.array, array.array]:
    count = round(total_seconds * rate)
    left = array.array("h", bytes(2 * count))
    right = array.array("h", bytes(2 * count))

    def add_tone(start: float, duration: float, frequency: float, gain: float, pan: float = 0.0, sweep: float = 0.0) -> None:
        start_index = max(0, round(start * rate))
        length = min(count - start_index, round(duration * rate))
        for offset in range(length):
            t = offset / rate
            progress = offset / max(1, length)
            envelope = min(1.0, progress * 12) * (1 - progress) ** 1.7
            phase = 2 * math.pi * (frequency * t + 0.5 * sweep * t * t)
            sample = int(32767 * gain * envelope * math.sin(phase))
            left[start_index + offset] = max(-32768, min(32767, left[start_index + offset] + int(sample * (1 - max(0, pan)))))
            right[start_index + offset] = max(-32768, min(32767, right[start_index + offset] + int(sample * (1 + min(0, pan)))))

    def add_noise_swoop(start: float, duration: float, gain: float) -> None:
        start_index = max(0, round(start * rate))
        length = min(count - start_index, round(duration * rate))
        phase = 0.0
        for offset in range(length):
            progress = offset / max(1, length)
            envelope = math.sin(math.pi * progress) ** 2
            phase += 2 * math.pi * (120 + 850 * progress) / rate
            deterministic = math.sin(phase * 3.17) * 0.55 + math.sin(phase * 7.41) * 0.25
            sample = int(32767 * gain * envelope * deterministic)
            pan = -0.25 + 0.5 * progress
            left[start_index + offset] = max(-32768, min(32767, left[start_index + offset] + int(sample * (1 - max(0, pan)))))
            right[start_index + offset] = max(-32768, min(32767, right[start_index + offset] + int(sample * (1 + min(0, pan)))))

    add_noise_swoop(0.0, 1.35, 0.055)
    for index, timing in enumerate(timings):
        if index in {1, 2, 3, 5, 6}:
            add_tone(timing["startSeconds"] - 0.08, 0.16, 310 + index * 18, 0.045, pan=(index % 3 - 1) * 0.18)

    wrong_time = timings[3]["startSeconds"] + 1.25
    add_tone(wrong_time, 0.42, 128, 0.085, sweep=-32)
    verify_time = timings[4]["startSeconds"] + 1.15
    add_tone(verify_time, 0.42, 523.25, 0.065, pan=-0.18)
    add_tone(verify_time + 0.11, 0.5, 783.99, 0.055, pan=0.18)
    add_tone(timings[6]["startSeconds"], 0.75, 392.0, 0.055, pan=-0.12)
    add_tone(timings[6]["startSeconds"] + 0.16, 0.9, 587.33, 0.045, pan=0.12)
    return left, right


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    narration = json.loads(NARRATION_PATH.read_text())
    segment_paths = sorted(SEGMENT_DIR.glob("*.wav"))
    if len(segment_paths) != len(narration["lines"]):
        raise RuntimeError(f"Expected {len(narration['lines'])} segments, found {len(segment_paths)}")

    target_rate = 48_000
    narration_samples = array.array("h")
    timings = []
    gap_rate = round(narration["gapSeconds"] * target_rate)
    for line, segment_path in zip(narration["lines"], segment_paths, strict=True):
        source_rate, samples = read_mono(segment_path)
        samples = trim_silence(samples, source_rate)
        resampled = resample_linear(samples, source_rate, target_rate)
        start_seconds = len(narration_samples) / target_rate
        end_seconds = (len(narration_samples) + len(resampled)) / target_rate
        timings.append(
            {
                "id": line["id"],
                "text": line["text"],
                "caption": line["caption"],
                "startSeconds": round(start_seconds, 4),
                "endSeconds": round(end_seconds, 4),
                "durationSeconds": round((end_seconds - start_seconds), 4),
            }
        )
        narration_samples.extend(resampled)
        narration_samples.extend(array.array("h", bytes(2 * gap_rate)))

    total_seconds = len(narration_samples) / target_rate
    write_mono(AUDIO_DIR / "narration.wav", target_rate, narration_samples)

    peak = max(1, max(abs(value) for value in narration_samples))
    normalization = 0.82 * 32767 / peak
    normalized = array.array("h", (int(value * normalization) for value in narration_samples))
    effects_left, effects_right = synth_effects(timings, total_seconds, target_rate)
    left = array.array("h", bytes(2 * len(normalized)))
    right = array.array("h", bytes(2 * len(normalized)))
    for index, speech in enumerate(normalized):
        left[index] = max(-32768, min(32767, speech + effects_left[index]))
        right[index] = max(-32768, min(32767, speech + effects_right[index]))
    write_stereo(AUDIO_DIR / "effects.wav", target_rate, effects_left, effects_right)
    write_stereo(AUDIO_DIR / "mix.wav", target_rate, left, right)

    scene_starts = [
        timings[0]["startSeconds"],
        timings[2]["startSeconds"],
        timings[3]["startSeconds"],
        timings[5]["startSeconds"],
        timings[6]["startSeconds"],
    ]
    payload = {
        "voice": narration["voice"],
        "speed": narration["speed"],
        "sampleRate": target_rate,
        "durationSeconds": round(total_seconds, 4),
        "lines": timings,
        "sceneStartsSeconds": scene_starts,
    }
    (AUDIO_DIR / "narration-timing.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Narration duration: {total_seconds:.3f}s")
    for timing in timings:
        print(f"{timing['startSeconds']:6.2f}-{timing['endSeconds']:6.2f}  {timing['id']}")


if __name__ == "__main__":
    main()
