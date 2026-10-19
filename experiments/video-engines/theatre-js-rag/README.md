# What is RAG?

A complete 21.6-second, 1080x1920, 30fps beginner explainer produced with
Theatre.js, local Kokoro TTS, deterministic browser capture, and FFmpeg.

The teaching analogy is a notebook library: a question retrieves useful pages,
those pages become context, and the model generates an answer.

## Deliverables

- `deliverables/final.mp4` - 1080x1920 H.264/yuv420p, 30fps, stereo AAC.
- `deliverables/preview.mp4` - 540x960 quick-review copy.
- `deliverables/contact-sheet.jpg` - one representative frame from each major
  scene.
- `REPORT.md` - provenance, render timing, review loop, QA evidence, and
  limitations.

## How Theatre.js produces the video

`src/theatre-state.json` is a Theatre.js project state with one `Scene` sheet,
one `VisualSystem` object, and 17 `BasicKeyframedTrack` animations. The
`@theatre/core` sequence is the timing authority. `scripts/render.mjs` seeks
`sheet.sequence.position` to one frame at a time, Theatre updates the
`VisualSystem` values, and `src/scene.js` applies those values to the HTML/SVG
composition. Chrome screenshots are streamed directly to FFmpeg.

The timeline is generated from the editable `tracks` table in
`scripts/build.mjs`; `src/script.json` owns narration, caption text, and scene
windows.

## Layout

```text
src/                         Theatre.js scene, HTML/CSS, captions, saved state
scripts/                     install, audio, build, render, inspect, cleanup
assets/                      retained narration/effect WAVs and provenance
deliverables/                final.mp4, preview.mp4, contact-sheet.jpg
package.json                 pinned Theatre.js/build/capture dependencies
package-lock.json            reproducible temporary dependency resolution
```

No model weights, `node_modules`, package caches, browser caches, or temporary
frames are retained.

## Reproduce

Tested with Node 26.7.0, npm 11.19.0, FFmpeg/FFprobe 9.0.2, and Google Chrome
155.0.8059.84 on macOS.

```sh
sh scripts/install-temp.sh
node scripts/generate-audio.mjs
node scripts/render.mjs
node scripts/inspect.mjs
node scripts/clean.mjs
```

`generate-audio.mjs` expects the brief's existing local files:

- Kokoro model:
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- `bf_emma` voice:
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`

It does not download TTS weights. The render script uses the macOS Chrome path
shown above; change `chromePath` in `scripts/render.mjs` for another local
browser installation.

## Editing

- `src/script.json`: narration, captions, and caption/visual timing.
- `scripts/build.mjs`: Theatre.js keyframes and generated project state.
- `src/scene.js`: Theatre-to-DOM binding and frame seeking.
- `src/index.html` / `src/styles.css`: scene structure and visual design.
- `scripts/generate-audio.mjs`: Kokoro synthesis and local sound design.

Run `npm run build` to regenerate `src/theatre-state.json` and the temporary
browser bundle after changing the timeline or scene source.
