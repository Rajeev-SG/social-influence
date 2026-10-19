# Why does AI hallucinate? (Lottie-web benchmark)

This directory contains a complete 19.29-second educational motion graphic for
intelligent beginners. The visual explanation is generated as a Lottie JSON
composition and rendered by lottie-web 5.13.0's SVG renderer. Local Kokoro
narration and synthesized sound design are mixed into the final MP4.

## Deliverables

- `deliverables/final.mp4` - 1080x1920, 30 fps, H.264, yuv420p, stereo AAC.
- `deliverables/preview.mp4` - 540x960 quick-review encode.
- `deliverables/contact-sheet.jpg` - 12 representative frames covering every
  major scene and both sides of the plausible/verified example.

## Source map

- `src/narration.json` - narration and caption copy.
- `src/text-spec.json` - editable typography source.
- `src/build-lottie.mjs` - generates the complete Lottie composition and scene
  markers from measured narration timing.
- `src/lottie.json` - generated Lottie-web input (91 layers, 579 frames).
- `src/render/index.html` - minimal lottie-web player/capture surface.
- `assets/vendor/lottie.min.js` - vendored lottie-web 5.13.0 runtime.
- `assets/text/` and `assets/background.jpg` - generated local visual assets.
- `assets/audio/` - Kokoro narration, effects, final mix and line timing.
- `scripts/` - asset, TTS, render, contact-sheet and verification workflows.

## Rebuild

The scripts use the already-installed shared runtime under
`/Users/rajeev/Code/content-machine/node_modules`; they do not download TTS
weights or install dependencies.

```bash
python3 scripts/generate-assets.py
node scripts/generate-narration.mjs
python3 scripts/mix-audio.py
node src/build-lottie.mjs
node scripts/render-video.mjs deliverables/final.mp4 deliverables/preview.mp4
python3 scripts/make-contact-sheet.py \
  --video deliverables/final.mp4 \
  --output deliverables/contact-sheet.jpg
bash scripts/verify-media.sh
```

`scripts/render-video.mjs` captures Lottie in 120-frame Chromium batches,
asserts every source frame exists, encodes with FFmpeg, atomically replaces the
deliverables and removes temporary frame files. `assets/render-timing.json`
records the measured capture and encode time for the current output.

## Teaching structure

1. Hook and analogy: a confident storyteller without a fact-checker.
2. Mechanism: the model predicts plausible next pieces rather than querying a
   fact database.
3. Example: a fluent Eiffel Tower claim (`1927`) diverges from the verified fact
   (`1889`).
4. Failure mode: thin patterns leave a gap that is filled by a plausible
   invention.
5. Close: important claims need checking because plausible is not true.

See `REPORT.md` for research provenance, render timings, inspection findings,
creative refinement and limitations.
