# Three.js: What Is a Neural Network?

One complete 1080x1920, 30fps educational benchmark video about neural networks for intelligent beginners. The teaching analogy is a team of tiny decision helpers: simple clues enter the first layer, weighted connections combine them, each node sums a bias and applies an activation, and training tunes the connection strengths until useful patterns emerge.

## Deliverables

- `deliverables/final.mp4`: 23.333s H.264 master with stereo AAC
- `deliverables/preview.mp4`: 540x960 H.264/AAC review copy
- `deliverables/contact-sheet.jpg`: six representative frames from the major scenes

## Reproduce

The project intentionally has no `node_modules` and downloads no TTS weights. The renderer uses the installed `playwright` package from `/Users/rajeev/Code/content-machine/node_modules` and a vendored Three.js module in `assets/vendor/`.

```sh
cd /Users/rajeev/Code/social-influence/experiments/video-engines/threejs-neural-network
node scripts/render.mjs --label final --force-audio --deliver --output deliverables/final.mp4
./scripts/verify.sh deliverables/final.mp4
```

The `--force-audio` flag regenerates the local Kokoro narration and soundscape, then removes the raw intermediate WAV. The narration command requires the installed cache at `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX` and the `bf_emma` voice at `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`.

## Editable source

- `src/index.html`: accessible title, captions, formula and output overlays
- `src/styles.css`: mobile-scale typography, scene hierarchy and transitions
- `src/scene.js`: deterministic Three.js scene, four layers, 30 weighted tube paths, animated signals, camera parallax and cue-driven overlays
- `script.json`: original narration and captions
- `assets/audio/timing.json`: measured Kokoro cue timings used by the scene and renderer
- `scripts/generate-narration.cjs`: local q8 Kokoro synthesis and cue timing
- `scripts/generate-soundtrack.py`: original restrained stereo bed and cue-aligned effects
- `scripts/render.mjs`: Playwright capture, FFmpeg encoding, mix, preview and contact sheet
- `scripts/verify.sh`: decode/spec/audio smoke check

The video uses Three.js as the substantive visual engine. It creates a real WebGL scene with `WebGLRenderer`, `PerspectiveCamera`, `MeshStandardMaterial`, `TubeGeometry`, additive signal sprites and fog; Playwright screenshots only the deterministic canvas/overlay state and FFmpeg encodes the result.
