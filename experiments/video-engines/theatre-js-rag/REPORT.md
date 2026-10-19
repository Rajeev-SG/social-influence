# REPORT: What is RAG?

## Topic and teaching goal

Topic: Retrieval-Augmented Generation (RAG).

Teaching goal: explain RAG as looking up useful notes before answering, using a
notebook-library analogy that makes retrieval, context, and generation visible
as one connected process.

## Technology and rendering role

- Primary animation/production technology: Theatre.js `@theatre/core@0.7.2`.
- Browser capture: `playwright-core@1.55.1` driving Google Chrome
  `155.0.8059.84`.
- Build: `esbuild@0.25.10`.
- Encode: FFmpeg `9.0.2` with `libx264` and native AAC.
- Local TTS: `kokoro-js@1.2.1` with Kokoro-82M-v1.0-ONNX q8 and `bf_emma`.

The Theatre.js project is named `What is RAG`, sheet `Scene`, object
`VisualSystem`. Its saved state contains 17 editable `BasicKeyframedTrack`
tracks covering scene opacity, title motion, retrieval progress, context
assembly, pipeline progress, answer reveal, camera motion, and accent light.
The sequence is 21.6 seconds at 30 subunits per second.

For every output frame, `scripts/render.mjs` sets
`sheet.sequence.position = frame / 30`. Theatre resolves the keyframed values,
`object.onValuesChange` applies them to HTML/SVG/CSS variables, and Playwright
captures the resulting 1080x1920 browser frame. PNG frames are streamed
directly to FFmpeg and encoded with the generated narration/effects mix. This
makes Theatre.js the actual animation timeline and playhead, not merely an
installed dependency.

## Research and provenance

Research date: 2026-10-19.

Official Theatre.js sources consulted:

- [Core API](https://www.theatrejs.com/docs/latest/api/core) for
  `getProject`, sheets, objects, `sequence.position`, and `onValuesChange`.
- [Projects](https://www.theatrejs.com/docs/latest/manual/projects) for saved
  project state and production loading.
- [Sequences](https://www.theatrejs.com/docs/latest/manual/sequences) for
  keyframe/tween semantics and programmatic playback.
- [Releases](https://www.theatrejs.com/docs/latest/releases) for current
  package guidance.
- [Theatre.js GitHub](https://github.com/theatre-js/theatre) for package
  licensing and project status.
- npm registry: `@theatre/core` latest resolved to `0.7.2`.

The official `latest` documentation currently presents the stable 0.5-era API;
the published core package is `0.7.2`. No stale pre-0.5 APIs were used.

### Skills

- Skill discovery command:
  `python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "Theatre.js animation render browser video"`.
  Result: `no skill matched`. No Theatre.js-specific installed skill was used.
- `/Users/rajeev/.codex/skills/transcribe/SKILL.md` was consulted for narration
  QA. Its CLI was not executed because the documented `OPENAI_API_KEY`
  prerequisite was absent. No local Whisper module or executable was installed.
- No other skill was used.

## Script and audio

The original narration is in `src/script.json`. The five caption windows are
also the audio-placement windows, so visual changes and captions follow the
spoken explanation.

`scripts/generate-audio.mjs` loaded the specified local q8 ONNX directory and
the local `bf_emma.bin` voice. No TTS weight or voice was downloaded or copied.
Kokoro generated five 24kHz segments. FFmpeg resampled them to 48kHz stereo and
applied these measured tempo normalizations:

| Segment | Raw | Prepared | Tempo |
| --- | ---: | ---: | ---: |
| title | 1.925s | 1.917s | 1.000 |
| plain-english | 7.125s | 5.387s | 1.324 |
| retrieve | 6.200s | 5.435s | 1.142 |
| context | 4.950s | 4.323s | 1.143 |
| generate | 5.650s | 4.235s | 1.336 |

The final local generation run took 10.59 seconds. The prepared narration was
placed at the exact `script.json` start times and combined with deterministic
JavaScript-synthesized low pad tones, short paper-like noise transitions,
soft chimes, and retrieval ticks. No downloaded sound assets were used.

## Render commands and timing

Commands:

```sh
node scripts/generate-audio.mjs
node scripts/render.mjs
node scripts/inspect.mjs
```

`node scripts/render.mjs` rebuilds Theatre state/bundle, captures 648 frames
from Chrome, encodes `final.mp4`, then creates `preview.mp4`.

Measured render timing:

| Pass | Theatre/Chrome capture + final encode | Preview encode | Full pipeline |
| --- | ---: | ---: | ---: |
| Initial complete render | 149.132s | 1.068s | 150.200s |
| Creative refinement rerender | 142.935s | 0.682s | 143.617s |

The initial script printed the full-pipeline number under
`FULL_RENDER_SECONDS`; the script was subsequently corrected to report the
three values separately. The final media corresponds to the 143.617-second
refinement rerender.

## Full-render inspection and refinement

The initial complete MP4 was decoded and inspected using extracted frames at
0.70s, 2.20s, 2.65s, 4.80s, 7.55s, 9.60s, 12.85s, 13.35s, 15.30s, 17.35s,
18.70s, 20.60s, and 21.30s.

Findings:

- Opening, definition, generation, and ending were readable and visually
  coherent on a mobile 9:16 frame.
- Retrieval highlighted matching notebooks but did not clearly show the useful
  pages being gathered and associated with the question.
- The context scene had transparent/overlapping panels and crowded arrow labels.
- The 20.60s frame showed finale text ghosting behind the completed answer
  during the crossfade.
- The R/A/G rows sat too close to the answer sheet.
- Theatre keyframe handles were linear, which made motion less polished.

Exact creative/technical refinement:

- Added three animated note-page cards that travel from selected library books
  toward the question, plus a `GATHERED / 03 useful pages` result card.
- Reworked the context scene into separated question -> notes -> model-context
  zones, made the context panel opaque, narrowed/repositioned the note stack,
  and moved the arrow labels out of the note content.
- Delayed `finaleOpacity` from `20.55 -> 21.05` to `20.88 -> 21.18`, removing
  the 20.60s text collision.
- Changed all Theatre keyframe interpolation handles to
  `[0.25, 0.1, 0.25, 1]` for smooth in/out motion.
- Reduced the R/A/G stack width from 790px to 570px and adjusted the library
  shelf/chip positions.

The changed scene was fully rerendered. Refined frames at 4.80s, 8.60s,
10.20s, 11.70s, 15.30s, 18.70s, 20.60s, and 21.30s were extracted and
inspected. The new retrieval action, separated context diagram, clean 20.60s
transition, and ending were confirmed. The final six-scene contact sheet was
also visually inspected.

## Audio QA

- The full 21.6-second narration was played back with `ffplay`.
- Overall final-mix measurements: mean `-17.9 dB`, max `0.0 dB`, 1,036,800
  stereo samples.
- Caption-window mean levels: title `-18.6 dB`, plain-English `-18.2 dB`,
  retrieval `-18.0 dB`, context `-17.9 dB`, generation `-17.9 dB`.
- FFmpeg `astats` reported no flat samples in the first-pass analysis.

The `transcribe` skill could not provide independent ASR verification because
its required `OPENAI_API_KEY` was not set. Playback, source text, generated
segment durations, and objective per-window audio analysis were used instead.

## Final media verification

Automated `node scripts/inspect.mjs` result: all 15 assertions passed.

`final.mp4`:

- container: MP4, 7,882,754 bytes, 21.600 seconds.
- video: H.264 High, 1080x1920, yuv420p, 30/1 fps, 648 frames.
- audio: AAC-LC, stereo, 48,000Hz, 21.600 seconds.
- full FFmpeg decode: no errors.
- SHA-256: `f017bd4b7675de56682f51f1d7754a41ce2beb032bdfdda7d5bf7ce0cc30080a`.

`preview.mp4`:

- 540x960 H.264/yuv420p, 30fps, stereo AAC, 21.600 seconds.
- 1,315,340 bytes, smaller than the final.
- SHA-256: `88fd9655d73be4ffb309f8d520d9ede4ecefdd64924ab6718ee1ad60dff48f35`.

`contact-sheet.jpg`:

- 147,937 bytes, six representative frames covering every major scene.
- SHA-256: `f7969bf8420e18f9bce94fafbd51b702cd62e6f63154bff2cf6e9cf4a3700d7c`.

## Known limitations

- Word-level ASR verification was unavailable because no transcription API key
  or local Whisper runtime was present.
- Kokoro's 24kHz output is resampled to the required 48kHz delivery rate; three
  narration segments required tempo normalization to stay within the
  21.6-second lesson.
- The AAC mix reaches 0.0dB at isolated peaks. FFmpeg reported no flat/clipped
  runs, but inter-sample peaks remain possible.
- Theatre.js Studio is not bundled in the final production path. Editability is
  provided through the saved Theatre project state and the declarative track
  generator in `scripts/build.mjs`.
- Theatre.js documentation is stable but 0.5-era while the current published
  core package is 0.7.2; the implementation follows the current package API.
