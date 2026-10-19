# How AI Learns From Mistakes

A bespoke 21.633-second beginner video in 1080 × 1920 at 30 fps. The teaching
analogy is a ball toss into a bucket: miss, measure the feedback, adjust the
aim, and repeat. The same loop becomes the AI explanation: guess, compare with
the right answer, measure error, nudge internal settings, and repeat.

## Watch

- [Final master](deliverables/final.mp4)
- [Small review copy](deliverables/preview.mp4)
- [Contact sheet](deliverables/contact-sheet.jpg)

## Production technology

Movis is the primary renderer. `src/render_video.py` creates a
`movis.layer.Composition`, evaluates a custom RGBA `FilmLayer` at every time
sample, mixes the narration and procedural soundscape as Movis audio layers,
and calls `Composition.write_video()` for the H.264/AAC master. Movis package:
`0.7.1`; Python: `3.11.15`.

FFmpeg is used only for local narration conditioning, proxy generation,
contact-frame extraction and delivery checks.

## Rebuild

The included audio is sufficient to re-render without downloading TTS weights.
To regenerate it, this machine must retain the already-installed Kokoro setup
named in `REPORT.md`; `scripts/narrate.cjs` is explicitly local-only.

```sh
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
./scripts/build.sh
.venv/bin/python scripts/inspect_media.py
```

Use `./scripts/build.sh --skip-audio` to reuse the checked-in audio and
`src/timing.json`. The build writes `deliverables/final.mp4` and
`deliverables/preview.mp4`; the inspection script writes
`deliverables/contact-sheet.jpg`.

## Editable files

- `script.json`: original six-line narration.
- `src/timing.json`: measured Kokoro cue timing and exact 649-frame duration.
- `src/design.py`: palette, typography, geometry and reusable drawing helpers.
- `src/render_video.py`: all four animated scenes, captions and Movis composition.
- `scripts/narrate.cjs`: local Kokoro 82M q8 ONNX synthesis and cue measurement.
- `scripts/soundscape.py`: original procedural music/effects synthesis.
- `scripts/build.sh`: narration, mix, Movis render and preview build.
- `scripts/inspect_media.py`: FFmpeg-skill checks and exact-scene contact sheet.
- `assets/audio/`: narration and sound-design WAV files.
- `assets/fonts/`: Manrope and IBM Plex Mono files with their OFL notices.

## Skill provenance

No Movis-specific agent skill was present in the local skill index or the
public `SKILL.md` searches performed for this task. A maintained relevant
FFmpeg skill was found and vendored at `skills/ffmpeg-skill/`:

- repository: <https://github.com/kajisho5/ffmpeg-skill>
- release/tag: `v2.10.4`, published 2026-10-17
- pinned commit: `11a70aa680c0916581164dc49957a1b64ec57a79`
- license: MIT

Its `probe.py`, `check.py`, `look.py`, `audio.py` and `proxy.py` workflows were
used for media verification and review. The installed `transcribe` skill at
`/Users/rajeev/.codex/skills/transcribe/SKILL.md` was consulted, but its
OpenAI-backed CLI could not run because `OPENAI_API_KEY` was unset.

## Factual scope

The video teaches the feedback-and-adjustment intuition, not the full
mathematics of gradient descent or every kind of model training. The numeric
guess/error values and decreasing-error curve are illustrative. Captions are
burned into the picture and synchronized to measured generated audio; the
master has no separate subtitle track.
