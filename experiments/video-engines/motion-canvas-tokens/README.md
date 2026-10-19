# What Are Tokens?

A complete 24.78-second Motion Canvas educational short for mobile: a sentence
ribbon enters a tokenizer gate, becomes reusable text pieces, receives example
IDs, and resolves into the `text -> chunks -> IDs` handoff. The visual analogy is
a sorting line: the ribbon is cut once, and the same pieces carry through every
later step.

## Watch

- [Final master](deliverables/final.mp4) — 1080 x 1920, 30 fps
- [Review copy](deliverables/preview.mp4) — 540 x 960
- [Contact sheet](deliverables/contact-sheet.jpg) — ten frames covering every major beat
- [Production evidence](REPORT.md)

## Production

Motion Canvas 3.17.2 is the primary production technology. It renders every
frame from TypeScript/TSX to a PNG sequence; FFmpeg only muxes that sequence
with the locally produced audio and makes the review copy/contact sheet.

To rerun from this directory:

```sh
npm install
npx playwright install chromium   # only if Chromium is not already available

# Reuse the already-installed Kokoro cache; no TTS download occurs.
KOKORO_PACKAGE=/Users/rajeev/Code/content-machine/package.json node scripts/narrate.cjs
/Users/rajeev/Code/mlx-vlm/.venv/bin/python scripts/soundscape.py

npm run build
npm run render
python3 scripts/deliver.py
```

`scripts/render.mjs` starts the official Motion Canvas editor, drives its
render button with Playwright, waits for the image sequence to stabilize, and
closes the browser. `scripts/deliver.py` encodes the master, creates the
smaller review MP4, and regenerates the contact sheet from the master.

## Edit

- `src/scenes.tsx` — complete narrative, scene choreography, token diagrams,
  ID mapping, tokenizer-boundary comparison, bridge recap, and captions.
- `src/design.tsx` — palette, typography, safe-area rules, token tiles, and
  reusable motion helpers.
- `src/project.ts` / `src/project.meta` — Motion Canvas scene registration,
  audio track, 1080 x 1920 size, 30 fps, and PNG-sequence exporter settings.
- `scripts/narration-script.json` — original seven-line narration.
- `scripts/narrate.cjs` — local Kokoro synthesis with measured per-line timing.
- `scripts/soundscape.py` — original pad, token ticks, transition air moves,
  closing resolve, and final stereo mix.
- `assets/skills/VideoZero-skills-670ff96/` — project-local skill provenance.

No model weights, caches, `node_modules`, render frames, or temporary review
files are retained.
