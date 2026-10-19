# MotionForge — What is temperature in AI?

This directory contains a complete 24.5-second beginner explainer rendered at
1080x1920, 30 fps. The film uses one continuous “choice machine” analogy:
low temperature locks a focused route, while high temperature opens more
possible routes. It explains that temperature changes variety, not intelligence.

## Deliverables

- `deliverables/final.mp4` — 1080x1920, 30 fps, H.264/yuv420p, stereo AAC
- `deliverables/preview.mp4` — 540x960 quick review copy
- `deliverables/contact-sheet.jpg` — six representative scene frames

## Editable source

- `src/scene.tsx` — MotionForge React composition, diagrams, typography and cues
- `src/main.tsx` — deterministic `PlayerComposition` capture entry point
- `src/styles.css` — visual system and mobile typography
- `src/timeline.json` — measured narration timings and scene metadata
- `scripts/` — local Kokoro synthesis, SFX generation, frame capture, encoding and QA
- `assets/` — generated narration/SFX and timing/QA records; no model weights or caches

## Reproduce

From this directory:

```sh
npm install
node scripts/generate_audio.mjs
bash scripts/build.sh
```

`generate_audio.mjs` reuses the six local Kokoro segment WAVs when they already
exist. If a segment is missing, it loads the already-installed q8 ONNX Kokoro
model from the cache at
`/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
with `allowRemoteModels=false`. The required local voice is
`/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`.

`build.sh` synthesizes the three local effects (`lock`, `sparkle`, `whoosh`),
captures every MotionForge frame in headless Chromium, mixes the narration and
effects with FFmpeg, writes the final/preview/contact-sheet deliverables, and
runs `scripts/verify.mjs`.

## Technology

MotionForge is the primary visual technology. `src/scene.tsx` uses its
`PlayerComposition`, `AbsoluteFill`, `KineticTypography`, `useCurrentFrame`,
`spring`, `interpolate` and `Easing` primitives. MotionForge produces every
visual frame; Playwright captures those deterministic frames and FFmpeg encodes
and muxes the final media.

See `REPORT.md` for source provenance, render timings, full-render inspection
findings, the creative refinement pass, and exact QA evidence.
