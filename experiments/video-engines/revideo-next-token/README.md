# How does next-token prediction work?

A complete 20.1-second beginner explainer rendered with Revideo 0.11.0. The film follows one sentence tape from context, through a weighted next-piece ballot, into the selected piece, then back into the next prediction.

## Watch

- `deliverables/final.mp4` — 1080 × 1920, 30 fps, H.264/yuv420p, stereo AAC
- `deliverables/preview.mp4` — 540 × 960 review copy
- `deliverables/contact-sheet.jpg` — eight representative frames covering every major beat

## Rerender

Requirements: Node.js, FFmpeg/FFprobe on `PATH`, Python 3, Pillow, and Google Chrome or Chromium. No TTS model download is needed on the recorded machine.

```sh
cd /Users/rajeev/Code/social-influence/experiments/video-engines/revideo-next-token
PUPPETEER_SKIP_DOWNLOAD=1 npm ci
node scripts/narrate.cjs
python3 scripts/soundscape.py
./scripts/render.sh
python3 scripts/deliver.py
```

`scripts/render.sh` renders four finite Revideo ranges in isolated processes, verifies the assembled 603-frame master, and writes `.review/render-timing.json`. `scripts/deliver.py` mixes the measured Kokoro narration with the procedural sound bed and creates all three deliverables.

## Edit map

- `assets/script.json` — original narration and caption text
- `src/timing.json` — measured sample-derived cue timing
- `src/scene.tsx` — all Revideo animation and visual explanation
- `src/data.ts` — illustrative candidate probabilities and caption mapping
- `src/theme.ts` — palette and font tokens
- `src/project.ts` / `src/render.ts` — Revideo project and Wasm MP4 render entry point
- `scripts/narrate.cjs` — local Kokoro 82M q8 narration using the existing cache
- `scripts/soundscape.py` — original procedural score, ticks, whooshes, impacts, and resolve
- `scripts/render.sh` — gated segmented Revideo render and FFmpeg concatenation
- `scripts/inspect_media.py` — decode/spec/frame/audio inspection
- `scripts/deliver.py` — final mix, preview encode, and contact sheet
- `assets/skills/revideo-video/` — locally installed Revideo production skill with provenance

The probability values are illustrative. Tokens may be words, fragments, or punctuation; this short example uses word-sized pieces for clarity. Sampling does not necessarily select the largest probability, and likely wording is not a truth guarantee.
