# Production Report

## Topic and teaching goal

**Rendiv — “What is attention?”** teaches that a model uses surrounding words
as context and gives more influence to clues that are relevant to the current
word. The film makes this visible with a river meaning, a financial meaning and
a measured pull chart.

## Technology and rendering role

- **Primary technology:** Rendiv 0.2.6 (`@rendiv/core`, `@rendiv/cli`,
  `@rendiv/captions` and `@rendiv/fonts` are pinned in `package.json`).
- **Rendering role:** React/TypeScript components are frame-driven through
  `useFrame()` and rendered by the Rendiv CLI. The composition owns the animated
  diagrams, contextual examples, bars, captions and typography; FFmpeg is used
  only for final audio normalisation and preview packaging.
- **Runtime:** Node 26/Vite 7 project dependencies are retained in
  `package-lock.json`; the Rendiv render completed at 1080 x 1920 and 30 fps.

## Skills used and provenance

`skills/rendiv-video/` is the project-local Rendiv Video skill. Its front matter
identifies the `rendiv` author, version 1.0, Apache-2.0 licence and the current
React/TypeScript rendering model. `skills/PROVENANCE.txt` records commit
`6d6aca2bf17c02351213607056bfdc9fb0ea8e6c`. The official Rendiv CLI,
composition and frame-driven rendering APIs were used rather than a generic
browser capture script.

## Local narration and sound

Narration uses the installed Kokoro 82M q8 ONNX cache and `bf_emma` voice:

- model cache: `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- voice: `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`

`scripts/narrate.cjs` creates eight local line files and
`src/timing.json` carries measured word/cue intervals. `scripts/soundscape.py`
adds restrained transitions and connection accents. No TTS weights were
downloaded. The final mix is checked by decode and audio statistics; no local
ASR model was available for independent transcription.

## Render command and timing

```sh
scripts/build_audio.sh
scripts/render.sh
```

The native Rendiv render is recorded in `.review/render-timing.txt` at
**151.487s** for 733 frames. The profiling log identifies screenshot capture as
the bottleneck. The final packaging pass then produced the MP4, preview and
contact sheet.

## Full-render inspection and refinement

First-cut media verification and frame extracts are retained in `.review/`.
The final source has a three-beat explanatory structure:

1. a sentence as a room of clues;
2. river versus money neighbourhoods changing the meaning of “bank”;
3. an influence chart showing stronger relevance as stronger pull.

The refinement pass tightened the top/bottom safe-area hierarchy, simplified the
relationship diagrams into these three readable beats, and made the chart labels
large enough for mobile. A complete 733-frame rerender was then verified from
the actual MP4.

## Final media verification

- `final.mp4`: **24.5s container**, 733 video frames, **1080 x 1920**,
  **30/1 fps**, H.264/yuv420p, stereo AAC at 48 kHz.
- `preview.mp4`: 270 x 480, H.264/yuv420p, stereo AAC.
- `scripts/verify_media.py` passes decode, dimensions, fps, duration, codec,
  pixel format, stereo-AAC and audio-duration checks.
- The retained audio analysis reports finite samples, no clipping and a valid
  stereo AAC stream.

## Known limitations

- Attention weights shown in the bar chart are illustrative rather than a
  specific model’s measured values.
- The film explains contextual influence at beginner level, not every layer or
  head in a transformer.
- Kokoro narration is synthetic and word-level ASR verification was not
  available locally.
