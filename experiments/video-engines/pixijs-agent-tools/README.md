# PixiJS — How do AI agents use tools?

A 22.2-second, 1080x1920, 30 fps educational benchmark video for intelligent
beginners. It explains the tool loop as a control-room workflow:

1. choose a tool,
2. supply an action,
3. read the result,
4. continue with the new information.

PixiJS is the substantive visual renderer. Every frame is a PixiJS v8 scene
graph (`Application`, `Container`, `Graphics`, and `Text`) rendered to a
1080x1920 WebGL canvas. Playwright captures the canvas as a deterministic PNG
sequence; FFmpeg only encodes that sequence, mixes audio, and builds the
preview/contact sheet.

## Deliverables

```text
deliverables/
  final.mp4          1080x1920 H.264 + stereo AAC master
  preview.mp4        540x960 quick-review version
  contact-sheet.jpg  six representative frames from every major scene
```

`final.mp4` is 22.2 seconds, 30 fps, H.264 High-compatible yuv420p, with 48 kHz
stereo AAC. `preview.mp4` keeps the same timing and audio while reducing the
picture to 540x960.

## Source map

```text
src/
  index.html       minimal PixiJS host page
  scene.js         complete control-room animation and captions
  script.json      narration text, caption copy, and beat timings
scripts/
  generate-audio.mjs  local Kokoro narration + synthesized sound design
  mix-audio.sh        timed narration/effects mix
  render-frames.mjs   deterministic PixiJS/WebGL frame capture
  build.sh            final, preview, contact sheet, and stream probe
  verify.sh           full decode and required-spec assertions
assets/
  pixi.min.js         vendored PixiJS 8.22.0 browser bundle
  audio/              generated narration clips, effects, timing, and mix
```

The scripts reference the already-installed Playwright and Kokoro/Transformers
runtime in `/Users/rajeev/Code/content-machine/node_modules`. They intentionally
do not install packages or retain `node_modules`.

## Rebuild

Run from this directory:

```bash
node scripts/generate-audio.mjs
./scripts/mix-audio.sh
node scripts/render-frames.mjs final
./scripts/build.sh final
./scripts/verify.sh
```

The render script uses the installed Google Chrome with SwiftShader so the
1080x1920 WebGL output is deterministic. Temporary frame and browser-profile
directories live under `.work/`; the delivered project removes them after QA.

See `REPORT.md` for provenance, measured timings, the mandatory first-cut review,
creative refinements, verification evidence, and limitations.
