# What Is Attention?

A 24.5-second Rendiv educational short for mobile. It starts with a sentence as
a room of clues, then shows how nearby words change the meaning of “bank” and
how relevant clues exert stronger influence. The through-line is simple:
attention is the model measuring which context matters.

## Watch

- [Final master](deliverables/final.mp4) — 1080 x 1920, 30 fps
- [Review copy](deliverables/preview.mp4) — 270 x 480
- [Contact sheet](deliverables/contact-sheet.jpg) — representative frames
- [Production evidence](REPORT.md)

## Production

Rendiv 0.2.6 is the primary production technology. React/TypeScript scene
components are evaluated as a function of frame number; the Rendiv CLI renders
the composition to MP4. The retained `scripts/render.sh` handles bundling,
rendering, audio muxing, preview creation, contact-sheet generation and media
verification.

From this directory:

```sh
npm install
scripts/build_audio.sh
scripts/render.sh
```

The narration and sound bed use the installed local Kokoro cache and `bf_emma`
voice. No TTS weights are bundled.

## Edit

- `src/Attention.tsx` — scene composition, relationship diagrams, animated bars.
- `src/design.tsx` — typography, palette and reusable motion primitives.
- `src/index.tsx` and `src/timing.json` — composition registration and cue timing.
- `scripts/` — narration, soundscape, rendering, contact sheet and verification.
- `skills/rendiv-video/` and `skills/PROVENANCE.txt` — pinned skill reference.

No model weights, caches, node_modules or temporary render files are intended
for retention.
