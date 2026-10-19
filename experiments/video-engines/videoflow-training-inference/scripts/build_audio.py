#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "assets" / "audio"
SFX = ROOT / "assets" / "sfx"
TIMING_PATH = AUDIO / "timing.json"


def write_wav(
    path: Path,
    samples: list[float] | list[tuple[float, float]],
    sample_rate: int,
    channels: int = 1,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = bytearray()
    for sample in samples:
        values = sample if isinstance(sample, tuple) else (sample,)
        for value in values:
            value = max(-1.0, min(1.0, value))
            frames.extend(struct.pack("<h", int(value * 32767)))
    block_align = channels * 2
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + len(frames),
        b"WAVE",
        b"fmt ",
        16,
        1,
        channels,
        sample_rate,
        sample_rate * block_align,
        block_align,
        16,
        b"data",
        len(frames),
    )
    path.write_bytes(header + frames)


def read_mono_wav(path: Path) -> tuple[int, list[float]]:
    data = path.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError(f"Not a RIFF/WAVE file: {path}")
    offset = 12
    fmt = None
    raw = b""
    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        chunk_size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = data[offset + 8 : offset + 8 + chunk_size]
        if chunk_id == b"fmt ":
            fmt = struct.unpack_from("<HHIIHH", payload, 0)
        elif chunk_id == b"data":
            raw = payload
        offset += 8 + chunk_size + (chunk_size % 2)
    if fmt is None:
        raise ValueError(f"Missing fmt chunk: {path}")
    format_tag, channels, sample_rate, _, _, bits = fmt
    if channels != 1:
        raise ValueError(f"Expected mono WAV: {path}")
    samples: list[float] = []
    if format_tag == 1 and bits == 16:
        samples = [value / 32768.0 for (value,) in struct.iter_unpack("<h", raw)]
    elif format_tag == 3 and bits == 32:
        samples = [value for (value,) in struct.iter_unpack("<f", raw)]
    else:
        raise ValueError(f"Unsupported WAV format {format_tag}/{bits}: {path}")
    return sample_rate, samples


def synthesize_sfx() -> dict[str, Path]:
    random.seed(17)
    sr = 24000

    ticks: list[float] = [0.0] * int(sr * 0.08)
    for index in range(6):
        frequency = 520 + index * 72
        duration = 0.075
        start = len(ticks)
        ticks.extend([0.0] * int(sr * 0.105))
        for sample_index in range(int(sr * duration)):
            t = sample_index / sr
            envelope = math.exp(-32 * t) * (0.55 + index * 0.045)
            tone = math.sin(2 * math.pi * frequency * t)
            click = math.sin(2 * math.pi * frequency * 2.7 * t) * 0.22
            ticks[start + sample_index] = envelope * (tone + click) * 0.55
    ticks_path = SFX / "training-ticks.wav"
    write_wav(ticks_path, ticks, sr)

    lock = [0.0] * int(sr * 0.30)
    for index in range(int(sr * 0.18)):
        t = index / sr
        click_env = math.exp(-70 * t)
        noise = random.uniform(-1, 1) * 0.32
        thump = math.sin(2 * math.pi * 118 * t) * 0.82
        tick = math.sin(2 * math.pi * 1450 * t) * 0.34
        lock[index] = (noise * click_env + thump * math.exp(-24 * t) + tick * click_env) * 0.58
    lock_path = SFX / "lock-click.wav"
    write_wav(lock_path, lock, sr)

    chime = [0.0] * int(sr * 1.35)
    notes = [(392.0, 0.0), (523.25, 0.16), (659.25, 0.33)]
    for frequency, offset in notes:
        start = int(sr * offset)
        for index in range(int(sr * 0.95)):
            t = index / sr
            envelope = math.exp(-4.2 * t) * (1 - math.exp(-55 * t))
            tone = (
                math.sin(2 * math.pi * frequency * t)
                + 0.24 * math.sin(2 * math.pi * frequency * 2 * t)
            )
            chime[start + index] += envelope * tone * 0.20
    chime_path = SFX / "resolve-chime.wav"
    write_wav(chime_path, chime, sr)
    return {
        "training-ticks": ticks_path,
        "lock-click": lock_path,
        "resolve-chime": chime_path,
    }


def build_narration(timing: dict, sample_rate: int) -> Path:
    total_frames = int(round(float(timing["total_duration"]) * sample_rate))
    output = [0.0] * total_frames
    for line in timing["lines"]:
        line_rate, samples = read_mono_wav(ROOT / line["path"])
        if line_rate != sample_rate:
            raise ValueError(f"Unexpected sample rate for {line['path']}: {line_rate}")
        offset = int(round(float(line["start"]) * sample_rate))
        for index, sample in enumerate(samples):
            target = offset + index
            if target < total_frames:
                output[target] = sample
    narration_path = AUDIO / "narration.wav"
    write_wav(narration_path, output, sample_rate)
    return narration_path


def mix_audio(timing: dict, narration: Path, sfx: dict[str, Path]) -> None:
    total_duration = float(timing["total_duration"])
    sample_rate = 48000
    total_samples = int(round(total_duration * sample_rate))
    mixed = [0.0] * total_samples

    _, narration_samples = read_mono_wav(narration)
    source_rate = int(timing["sample_rate"])
    ratio = source_rate / sample_rate
    for target_index in range(total_samples):
        source_index = target_index * ratio
        left = int(source_index)
        right = min(left + 1, len(narration_samples) - 1)
        fraction = source_index - left
        if left < len(narration_samples):
            value = narration_samples[left] * (1 - fraction) + narration_samples[right] * fraction
            mixed[target_index] += value * 0.88

    events = {event["id"]: event for event in timing["sound_events"]}
    for event_id, path in sfx.items():
        event = events[event_id]
        _, effect_samples = read_mono_wav(path)
        offset = int(round(float(event["at"]) * sample_rate))
        gain = float(event["gain"])
        for index, value in enumerate(effect_samples):
            target = offset + index
            if target < total_samples:
                mixed[target] += value * gain

    current_rms = math.sqrt(sum(value * value for value in mixed) / len(mixed))
    rms_scale = 0.128 / max(current_rms, 1e-9)
    stereo = []
    for value in mixed:
        scaled = value * rms_scale
        limited = 0.84 * math.tanh(scaled / 0.84)
        stereo.append((limited, limited))

    output = AUDIO / "mix.wav"
    write_wav(output, stereo, sample_rate, channels=2)
    print(
        json.dumps(
            {
                "narration": str(narration.relative_to(ROOT)),
                "mix": str(output.relative_to(ROOT)),
                "duration": total_duration,
                "sample_rate": sample_rate,
                "samples": total_samples,
                "rms_scale": round(rms_scale, 6),
                "limiter_peak": 0.84,
                "sound_events": timing["sound_events"],
            },
            indent=2,
        )
    )


def main() -> None:
    timing = json.loads(TIMING_PATH.read_text(encoding="utf-8"))
    sample_rate = int(timing["sample_rate"])
    sfx = synthesize_sfx()
    narration = build_narration(timing, sample_rate)
    mix_audio(timing, narration, sfx)


if __name__ == "__main__":
    main()
