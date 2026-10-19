# What Is a Context Window?

A 23.08-second Editly educational short for mobile. It uses a desk metaphor:
the model can consider a limited amount of text in one go, older material may be
trimmed or summarised, and context is what the model can use now rather than
permanent memory.

## Watch

- [Final master](deliverables/final.mp4) — 1080 x 1920, 30 fps
- [Review copy](deliverables/preview.mp4) — 540 x 960
- [Contact sheet](deliverables/contact-sheet.jpg) — representative frames
- [Production evidence](REPORT.md)

## Production

Editly 0.15.0-rc.1 with `canvas` 2.11.2 is the primary production technology.
The editable scene functions draw the animated desk, capacity fills, trims,
context diagram, typography and captions. Editly supplies the timeline,
transitions, audio tracks and MP4 encode.

From this directory:

```sh
cd src
npm install
cd ..
scripts/build.sh
scripts/render.sh
```

The build reuses the installed local Kokoro cache and voice, synthesises
narration and the soundscape, then renders the final master. `scripts/deliver.py`
creates the smaller review MP4 and contact sheet.

## Edit

- `src/scenes.mjs` — animated scene drawing and caption choreography.
- `src/design.mjs` — palette, typography, layout and motion helpers.
- `src/render.mjs` — Editly clip construction, transitions and audio mix.
- `src/script.json` and `src/timing.json` — narration text and cue timing.
- `scripts/` — narration, soundscape, render and delivery automation.
- `assets/skills/video-editing-skill/` — pinned skill provenance.

No TTS weights or model caches are included.
