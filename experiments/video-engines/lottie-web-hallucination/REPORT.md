# Benchmark Report

## Topic and teaching goal

Topic: **Lottie-web - Why does AI hallucinate?**

One-sentence goal: teach beginners that a language model predicts plausible
next pieces from learned patterns instead of querying a fact database, so a
fluent answer can still be wrong and important claims need verification.

The central analogy is **a confident storyteller without a fact-checker**. The
visual through-line is a story rail that splits into a plausible-story branch
and a verified-fact branch, then thins into an invented gap before resolving to
`PLAUSIBLE != TRUE`.

## Technology and rendering role

Assigned technology: **lottie-web 5.13.0**.

`src/build-lottie.mjs` emits a Lottie JSON composition at 1080x1920, 30 fps,
579 frames, with 91 layers, 35 assets and five scene markers. The composition
contains the substantive motion design: kinetic typography, cards, probability
bars, vector path draws, split/merge diagrams, transitions and captions.

`src/render/index.html` loads the vendored `lottie-web` runtime and calls
`lottie.loadAnimation` with the SVG renderer. `scripts/render-video.mjs` uses
the documented `goToAndStop(value, isFrame)` control to seek every frame and
captures the rendered SVG in Google Chrome. FFmpeg then encodes the frame
sequence and local audio. This is the smallest compatible Lottie-web
capture/encoding workflow; Lottie-web remains the primary motion engine.

Exact runtime provenance (checked 2026-10-19):

- npm package: `lottie-web@5.13.0`
- registry tarball: `https://registry.npmjs.org/lottie-web/-/lottie-web-5.13.0.tgz`
- npm dist integrity: `sha512-+gfBXl6sxXMPe8tKQm7qzLnUy5DUPJPKIyRHwtpCpyUEYjHYRJC/5gjUvdkuO2c3JllrPtHXH5UJJK8LRYl5yQ==`
- vendored `assets/vendor/lottie.min.js` SHA-256:
  `2eb762973aec914d981f426123040bfac9d26217239605e225ddc7cee17618ac`
- MIT license retained at `assets/vendor/lottie-web-5.13.0-LICENSE.txt`

Current official references used:

- https://github.com/airbnb/lottie-web/wiki/loadAnimation-options
- https://github.com/airbnb/lottie-web/wiki/Usage
- https://github.com/airbnb/lottie-web/wiki/Renderer-Settings
- https://github.com/airbnb/lottie-web/wiki/Markers
- https://github.com/airbnb/lottie-web/blob/master/player/js/elements/ImageElement.js
- https://github.com/airbnb/lottie-web/blob/master/player/js/utils/TransformProperty.js

These were retrieved through Context7 library `/airbnb/lottie-web` and current
official GitHub/npm sources. LottieFiles' current developer portal was checked
for ecosystem context at https://developers.lottiefiles.com/ but was not used
as the runtime API.

## Skills used

- `official-first-docs` from
  `/Users/rajeev/.codex/skills/official-first-docs/SKILL.md`:
  used its version-current, official-first retrieval order for lottie-web.
- `playwright` from `/Users/rajeev/.codex/skills/playwright/SKILL.md`:
  used for real-browser network/DOM/screenshot diagnostics during renderer
  debugging and proof. The deterministic build uses the same installed
  Playwright library (`playwright 1.63.0`) rather than test files.

Skill discovery used
`python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find ...`.
Queries for Lottie, Kokoro, motion graphics, browser rendering and video QA
returned no Lottie-specific installed skill (`no skill matched`). No skill was
invented or represented as official.

## Script and factual provenance

The mechanism statement follows OpenAI's current explanation that language
models learn through next-word prediction and can confidently produce false
specific facts:
https://openai.com/index/why-language-models-hallucinate/

The example claim is deliberately false. The official Eiffel Tower history
states that the structure was completed and inaugurated on March 31, 1889, and
opened to the public on May 15, 1889:

- https://www.toureiffel.paris/en/the-monument/history
- https://www.toureiffel.paris/en/news/130-years/1889-2019-130-years-amazement
- https://www.toureiffel.paris/en/news/130-years/tower-highlight-1889-world-exhibition

The video uses `1889` as the verified fact and `1927` only as the plausible
invented answer.

## Local TTS and audio

No TTS weights were downloaded. `scripts/generate-narration.mjs` disables
remote model loading and uses the already-installed local setup:

- Kokoro model:
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- q8 ONNX file:
  `.../onnx/model_quantized.onnx`, 92,361,116 bytes, SHA-256
  `fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478`
- voice:
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`,
  522,240 bytes, SHA-256
  `669fe0647f9dd04fcab92f1439a40eeb4c8b4ab1f82e4996fe3d918ce4a63b73`
- `kokoro-js 1.2.1`, `@huggingface/transformers 3.8.1`, CPU `dtype: q8`
- voice `bf_emma`, speed `1.22`

`scripts/mix-audio.py` trims leading/trailing Kokoro silence with 35 ms of
breathing room, concatenates seven segments with 80 ms gaps, normalizes speech,
and synthesizes restrained panned tones/noise for transitions and the
claim/verification contrast.

Final narration timing:

| Line | Start | End |
|---|---:|---:|
| hook | 0.00 s | 1.53 s |
| analogy | 1.61 s | 3.98 s |
| prediction | 4.06 s | 8.44 s |
| claim | 8.52 s | 11.45 s |
| verify | 11.53 s | 14.48 s |
| gap | 14.56 s | 16.80 s |
| close | 16.88 s | 19.21 s |

## Render command and timing

Final render command:

```bash
node scripts/render-video.mjs \
  deliverables/final.mp4 \
  deliverables/preview.mp4 \
  /tmp/lottie-web-hallucination-final-frames
```

Machine-readable timing is in `assets/render-timing.json` (the temporary frame
path is normalized out of its command label):

- frames: 579
- browser capture: 34,013 ms
- FFmpeg encode of final + preview: 3,005 ms
- total: 37,018 ms
- final bytes: 1,444,727
- preview bytes: 562,379

Toolchain: Node 26.7.0, Python 3.14.7, FFmpeg 9.0.2, Google Chrome
155.0.8059.84, Playwright 1.63.0.

## Mandatory first-cut review

A complete first cut was rendered before refinement: 743 frames, 24.733 s,
1080x1920 H.264/yuv420p with stereo AAC. Its MP4 was decoded into 12 labelled
frames covering the opening, each major scene, transitions and ending, and the
full audio was played through macOS `afplay` and analyzed.

Concrete findings:

1. Card and panel fills were composited over their labels/dates, muting the
   `PLAUSIBLE STORY`, `VERIFIED FACT`, probability and CTA typography.
2. Kokoro segment boundaries included 215-248 ms of leading silence, so
   captions appeared before audible speech. Segment tails added roughly
   0.57-0.93 s of dead air and slowed the pacing.
3. Caption ranges overlapped near the claim/verify transition, producing two
   captions at once around 14.60 s.
4. The story-to-pattern transition briefly stacked the outgoing and incoming
   headings.
5. After the layer-order correction, the closing white CTA lost contrast
   against its white pill.

## Creative/technical refinement

At least one substantive creative improvement was made and verified:

- Reversed the generated content layers into Lottie's top-first order while
  keeping the background last, so labels, dates, bars and CTA text sit above
  their panels and cards.
- Trimmed Kokoro leading/trailing silence before timing derivation, reducing
  the video from 24.735 s to 19.29 s and aligning caption keys with audible
  speech onsets.
- Set caption out-points from the next line's in-point so captions cannot
  overlap.
- Removed scene-range overlap at the story/pattern boundary.
- Changed `CHECK IMPORTANT CLAIMS` to dark navy on the light pill.
- Corrected image-layer anchors to asset centres and waited for Lottie's
  `loaded_images` event before capture, a renderer-correctness prerequisite
  found during implementation.

## Final media verification

`npm run verify` and direct FFmpeg decoding passed:

| File | Duration | Video | Audio | Size |
|---|---:|---|---|---:|
| `final.mp4` | 19.290 s | 1080x1920, 30/1 fps, H.264, yuv420p | AAC, 48 kHz, 2 channels | 1,444,727 B |
| `preview.mp4` | 19.290 s | 540x960, 30/1 fps, H.264, yuv420p | AAC, 48 kHz, 2 channels | 562,379 B |
| `contact-sheet.jpg` | n/a | 1348x3400 JPEG | n/a | 768,308 B |

Additional QA:

- `ffmpeg -i <mp4> -f null -` completed without decode errors for both MP4s.
- decoded mix mean volume: -20.5 dB; max volume: -1.9 dB
- no silence of 0.35 s or longer at -45 dB was found in the final mix
- line-start RMS rises measured 7.04-33.98 dB at the seven caption keys
- full 19.29 s playback through `afplay` completed
- the final contact sheet visibly confirms clean transitions, readable
  captions, bright card labels, readable probability bars and a high-contrast
  closing CTA

## Known limitations

- The explanation is intentionally beginner-level and uses the colloquial term
  "hallucination"; it is not a complete account of any specific model
  architecture or every cause of factual error.
- Kokoro `bf_emma` is synthetic narration. Audio was played and objectively
  measured, but no human listening panel rated pronunciation or performance.
- Typography is generated from local macOS fonts into transparent PNG assets
  for deterministic browser capture. `src/text-spec.json` remains editable and
  regenerates those assets, but the Lottie file references raster typography.
- The browser capture uses JPEG quality 96 intermediates before H.264 encoding;
  this is visually validated but is not a lossless mastering workflow.
- Rendering depends on the existing local Chrome/Playwright and
  `content-machine` Kokoro installation paths documented above. Those
  dependencies, model weights and caches are intentionally not retained here.
