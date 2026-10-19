# Asset provenance

- `narration.wav`: generated locally for this project with `kokoro-js@1.2.1`,
  Kokoro-82M-v1.0-ONNX q8 model weights already cached by the repository's
  `content-machine` tooling, and the local `bf_emma.bin` voice.
- `sound-design.wav`: synthesized locally by `scripts/generate-audio.mjs` using
  deterministic JavaScript waveform synthesis. No downloaded sound assets are
  used.

No model weights, package caches, or browser caches are retained in this
directory.
