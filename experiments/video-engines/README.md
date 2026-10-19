# Programmatic Video Engine Benchmark

This experiment contains fourteen complete 15–25 second educational videos,
each using a different programmatic video technology as its primary production
engine.

## Watch

Open [`index.html`](index.html) for the side-by-side gallery.

Each technology directory contains:

- `deliverables/final.mp4` — 1080 x 1920 H.264/AAC master
- `deliverables/preview.mp4` — reduced review copy
- `deliverables/contact-sheet.jpg` — representative scene frames
- editable source, scripts and required local assets
- `README.md` and `REPORT.md` — rebuild instructions and production evidence

## Benchmark documents

- [`COMPARISON.md`](COMPARISON.md) — measured evidence, skill usage and ranking
- [`RECOMMENDATIONS.md`](RECOMMENDATIONS.md) — recommended engines and combinations
- [`STATUS.md`](STATUS.md) — assignment/completion matrix
- [`WORKER-BRIEF.md`](WORKER-BRIEF.md) — shared production contract

All masters were generated with the installed Kokoro 82M q8 ONNX `bf_emma`
voice. No TTS model weights, dependency trees or temporary render frames are
committed.
