# Benchmark Report

## Teaching goal

Three.js — What is a neural network? explains to intelligent beginners that a neural network is a layered team of small units which combine weighted clues, apply an activation, and learn connection strengths that turn raw clues into patterns.

## Technology and provenance

- Three.js: `0.180.0`, MIT, vendored from `/Users/rajeev/Code/web-automation-microbench/bench-ext/work/sitegeist/node_modules/three/build/three.module.js` and `three.core.js`. npm metadata was checked with `npm view three@0.180.0`; the exact package source is `https://registry.npmjs.org/three/-/three-0.180.0.tgz` and the project repository is `https://github.com/mrdoob/three.js`.
- Current official Three.js documentation consulted:
  - `https://threejs.org/docs/pages/WebGLRenderer.html` — WebGL2 renderer and render loop behavior.
  - `https://threejs.org/docs/pages/PerspectiveCamera.html` — perspective projection and camera parameters.
  - `https://threejs.org/docs/pages/TubeGeometry.html` — tubular geometry for weighted connection paths.
  - `https://threejs.org/docs/pages/MeshStandardMaterial.html` — physically based node surfaces and emissive response.
  - `https://threejs.org/manual/en/` — current Three.js manual/examples guidance.
- Current community/official automation guidance consulted:
  - `https://playwright.dev/docs/screenshots` and `https://playwright.dev/docs/api/class-page#page-screenshot` for deterministic browser frame capture.
- Installed skill discovery used `python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py`. No Three.js-specific skill was present. The matching installed skills were `speech` (`/Users/rajeev/.codex/skills/speech/SKILL.md`) and `playwright` (`/Users/rajeev/.codex/skills/playwright/SKILL.md`). The speech skill informed narration validation structure; its remote OpenAI path was not used because the brief required the installed local Kokoro setup. The Playwright skill informed the browser-capture workflow; the implementation uses the already-installed `playwright` package and does not retain a browser cache.

## Technology role

Three.js is the primary visual technology. `src/scene.js` builds a four-layer network with 30 weighted `TubeGeometry` connections, emissive node meshes, additive travelling signal spheres, fog and a perspective camera whose position and network rotation change every frame to create depth/parallax. The same deterministic `window.__SEEK__(time)` state drives the HTML title, formula, output card and captions. Playwright Chromium captures the 1080x1920 canvas/overlay state frame by frame; FFmpeg encodes the PNG stream to H.264/yuv420p and muxes audio.

## Local TTS and sound

`scripts/generate-narration.cjs` uses `kokoro-js 1.2.1` with the installed q8 `Kokoro-82M-v1.0-ONNX` cache and the `bf_emma` British voice. It generates each sentence locally with `local_files_only: true`, trims silent model padding while retaining breathing margins, merges the measured sample windows, writes `assets/audio/timing.json`, and does not download weights or create an environment. `scripts/generate-soundtrack.py` synthesizes an original low-level stereo bed, cue-aligned glass ticks and transition swells in Python's standard library. FFmpeg applies a light speech EQ/compressor/loudness pass and mixes narration above the bed.

Captions are synchronized to the exact measured Kokoro cue start/end times in `assets/audio/timing.json`. They are sentence/cue captions rather than word-level karaoke.

## Render commands and timings

- First complete cut: `node scripts/render.mjs --label first --force-audio --keep-temp --output .render-tmp/first/first-cut.mp4`; measured render time `57.913s`, `625` frames at the then-current `20.817s` narration duration.
- Final render: `node scripts/render.mjs --label final --force-audio --deliver --output deliverables/final.mp4`; measured render time `82.540s`, `700` frames at `23.319s` scene/narration duration.
- FFmpeg/Playwright versions on the machine: Node `26.7.0`, Playwright `1.63.0`, FFmpeg/ffprobe `9.0.2`.

## Full-render inspection findings and refinement

The first cut was inspected through its actual MP4, contact sheet and representative opening/middle/transition/ending frames. Strengths: the perspective camera and tubular paths gave the network tangible depth; the signal travel and node pulses explained information flow; typography remained readable at 1080x1920; and the formula/output overlays clarified the activation and prediction stages. The first cut exposed two weaknesses: the last sample repeated the training caption instead of resolving the idea, and the closing headline sat over too many active network lines.

Creative refinement changed `script.json` by shortening the training line and adding a sixth spoken conclusion, “Those learned patterns become the network's answer.” `src/scene.js` now derives every scene window from the measured cue times, keeps the output card alive through the closing beat, and dims connection tubes by 38% and signals by 32% while the final headline resolves. `src/styles.css` adds a stronger closing text shadow. The final contact sheet shows distinct opening, clue, weighted-path, activation, training and output/closing frames, including the new closing caption.

Audio review evidence: the first and final mixes were checked with waveform/segment RMS output, FFmpeg `volumedetect`, and EBU R128 measurement. The final narration has a clean head, sustained speech energy through all six cue windows, and a quiet tail. Final loudness is `-16.1 LUFS` integrated, `1.2 LU` LRA, and `-4.5 dBFS` true peak. No local ASR runtime/model was installed, so independent speech-to-text transcription was unavailable; audio intelligibility was therefore checked through deterministic Kokoro text generation, measured cue timing, waveform/energy inspection and loudness/decode checks rather than a second recognizer.

## Final media verification

`scripts/verify.sh deliverables/final.mp4` passed a full video decode to null and reported:

- `deliverables/final.mp4`: duration `23.333333s`, size `8,291,190` bytes, `700` decoded frames, H.264 `1080x1920`, `30/1` fps, `yuv420p`; AAC stereo, `48,000 Hz`.
- audio: mean volume `-19.6 dB`, max volume `-4.5 dB`; EBU R128 integrated loudness `-16.1 LUFS`, true peak `-4.5 dBFS`.
- `deliverables/preview.mp4`: duration `23.333333s`, `540x960`, H.264/yuv420p at `30/1`, AAC stereo `48,000 Hz`, size `1,046,938` bytes.
- `deliverables/contact-sheet.jpg`: `1080x1280` MJPEG contact sheet. OCR/text inspection found the opening title, all six caption lines, the activation formula, `CURVE FOUND`, and the closing `LAYERS FIND PATTERNS`/output beat.

## Limitations

- The network is an illustrative compact architecture, not a trained production model. The displayed weights and “training” motion are explanatory visual state, not a claim about a specific trained system.
- Captions are cue-synchronized sentence captions, not word-level karaoke.
- The renderer is a deterministic browser-capture workflow, not a real-time Three.js video exporter.
- No TTS weights, `node_modules`, model caches, temporary frame directories or raw intermediate narration are retained in the project. The generated `narration.wav`, `soundscape.wav` and `timing.json` are retained so the source can be rerendered without model downloads.
