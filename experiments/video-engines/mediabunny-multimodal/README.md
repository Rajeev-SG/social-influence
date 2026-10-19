# Mediabunny — How does multimodal AI work?

A complete 23-second educational reel for intelligent beginners, rendered at
1080 × 1920, 30 fps with H.264 video and stereo AAC audio.

## Watch

- `deliverables/final.mp4` — full-quality master
- `deliverables/preview.mp4` — 540 × 960 review copy
- `deliverables/contact-sheet.jpg` — one representative frame from each scene

The contact-sheet grid reads left-to-right, then top-to-bottom: hook, image,
audio, text, shared representations, combined answer.

## Teaching idea

Images, audio, and text are converted into compatible representations that the
model can combine before producing one answer. The film’s analogy is:
**different senses become shared notes**.

Animated image, audio, and text fragments travel into a shared workspace, where
their visual, acoustic, and semantic notes become comparable. The final scene
joins those notes into one answer.

## How Mediabunny renders the video

Mediabunny 1.56.1 is the actual media writer, not an incidental dependency:

1. `src/scene.js` draws every animation frame to a 1080 × 1920 Canvas.
2. `scripts/render.mjs` converts each Canvas frame to explicit limited-range
   BT.709 I420 pixels and adds it through Mediabunny’s `VideoSampleSource`.
3. The mixed Kokoro/sound-design `AudioBuffer` is added through
   `AudioBufferSource` and transformed to 48 kHz stereo.
4. Mediabunny’s `Output`, `Mp4OutputFormat`, and `BufferTarget` encode H.264 and
   AAC with WebCodecs and mux the final MP4.

FFmpeg is used only to create the smaller review copy/contact sheet and to
decode and inspect the Mediabunny output.

## Rebuild

Requirements: Node.js, Python 3, FFmpeg, Playwright, and the existing
`content-machine` packages containing `mediabunny`, `kokoro-js`, and
`@huggingface/transformers`. No `node_modules` is included in this directory.

```sh
# 1. Generate local Kokoro speech. It uses local_files_only and cannot download.
node scripts/generate-narration.cjs

# 2. Kokoro writes mono float WAV; normalize it for the stereo PCM mixer.
ffmpeg -i assets/audio/narration.wav -ac 2 -acodec pcm_s16le assets/audio/narration-pcm16.wav
mv assets/audio/narration-pcm16.wav assets/audio/narration.wav

# 3. Synthesize the restrained sound bed and final stereo mix.
python3 scripts/generate-soundtrack.py

# 4. Draw, encode, and mux with Mediabunny.
node scripts/render.mjs --out deliverables/final.mp4 --label final

# 5. Make review derivatives and run media QA.
scripts/build-review.sh
scripts/qa-inspect.sh
```

`scripts/qa-inspect.sh` extracts evidence into a temporary directory and removes
it on exit. Set `OUT_DIR=/some/path` to choose the location, or `KEEP=1` with the
default temporary directory to retain a manual inspection set.

## Source map

- `src/script.json` — original narration and caption copy
- `src/timing.json` — measured Kokoro cue timings (generated)
- `src/scene.js` — deterministic Canvas animation and caption renderer
- `src/index.html` — 1080 × 1920 stage
- `scripts/render.mjs` — I420 conversion, Mediabunny encoding/muxing
- `scripts/generate-narration.cjs` — local Kokoro 82M q8 generation
- `scripts/generate-soundtrack.py` — original procedural sound design/mix
- `scripts/build-review.sh` — preview and contact sheet
- `scripts/qa-inspect.sh` — decode, spec, frame, and audio checks
- `assets/audio/` — generated narration, sound bed, and final mix

## Provenance

- [Mediabunny quick start](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/quick-start.md)
- [Mediabunny media sources](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/media-sources.md)
- [Mediabunny writing media files](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/writing-media-files.md)
- [Mediabunny repository](https://github.com/Vanilagy/mediabunny)
- [Kokoro voices](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)

Exact skill usage, version evidence, render measurements, QA findings, and
limitations are in `REPORT.md`.
