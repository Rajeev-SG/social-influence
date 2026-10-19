# Lottie-web: Why does AI hallucinate?

This directory contains a complete 19.29-second educational motion-graphics
video for intelligent beginners. It explains that language models generate
plausible next pieces from learned patterns rather than checking a fact
database, so fluent answers can still be wrong.

## Deliverables

- `deliverables/final.mp4` - 1080x1920, 30 fps, H.264/yuv420p, stereo AAC
- `deliverables/preview.mp4` - 540x960 quick-review copy
- `deliverables/contact-sheet.jpg` - MP4-derived frames covering all five scenes

## How the video is produced

1. `src/build-lottie.mjs` generates `src/lottie.json` and
   `src/lottie-summary.json`.
2. `src/render/index.html` loads the vendored `lottie-web` 5.13.0 SVG renderer.
3. `scripts/render-video.mjs` drives `goToAndStop(frame, true)` in headless
   Chrome, captures every Lottie frame, and encodes the result with FFmpeg.
4. `assets/audio/mix.wav` contains locally generated Kokoro narration and
   synthesized sound design.

Lottie-web is the primary motion renderer: all typography entrances, panels,
cards, path drawing, probability bars, scene transitions, markers and other
graphics come from the generated Lottie JSON.

## Reproduction

The scripts assume the existing local toolchain documented in `REPORT.md`.
They do not install packages or download TTS weights.

```bash
npm run narration
npm run mix
npm run assets
npm run build
npm run render -- deliverables/final.mp4 deliverables/preview.mp4 /tmp/lottie-web-hallucination-frames
python3 scripts/make-contact-sheet.py \
  --video deliverables/final.mp4 \
  --output deliverables/contact-sheet.jpg
npm run verify
```

`scripts/render-video.mjs` removes its frame directory after atomic output
replacement and records the measured timing in `assets/render-timing.json`.
No `node_modules`, model weights, caches or temporary frames are retained here.

## Source map

- `src/narration.json` - original script and caption text
- `src/text-spec.json` - editable typography/color specification
- `src/build-lottie.mjs` - Lottie composition generator
- `src/render/index.html` - minimal Lottie-web rendering page
- `scripts/generate-assets.py` - deterministic typography/background assets
- `scripts/generate-narration.mjs` - local Kokoro 82M q8 ONNX synthesis
- `scripts/mix-audio.py` - silence trimming, timing and sound-design mix
- `scripts/render-video.mjs` - browser frame capture and FFmpeg encoding
- `scripts/make-contact-sheet.py` - final scene review sheet
- `scripts/inspect-audio.py` - narration timing/level inspection
- `scripts/verify-media.sh` - strict decode/spec assertions
- `assets/vendor/` - vendored `lottie-web` runtime and MIT license

See `REPORT.md` for provenance, measured render timing, review findings and
limitations.
