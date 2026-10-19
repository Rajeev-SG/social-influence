# Benchmark Report

## Topic and teaching goal

**Topic:** PixiJS — How do AI agents use tools?

**Teaching goal:** An agent uses a tool by choosing it, supplying an action,
reading the result, and continuing from that new information.

**Audience:** Intelligent beginners. The video uses one persistent analogy:
an AI agent as an operator at a control desk, routing work through instrument
bays and receiving data back.

## Technology and rendering role

- **Primary visual technology:** PixiJS **8.22.0** (MIT).
- **Vendored artifact:** `assets/pixi.min.js`, fetched from
  `https://cdn.jsdelivr.net/npm/pixi.js@8.22.0/dist/pixi.min.js`.
- **Artifact SHA-256:**
  `06d9ef9823e743518793083c296d801e752db128cb1f519fbabe37e1259567ea`
  (840,663 bytes).
- **Runtime evidence:** both captures reported `renderer: "webgl"` and produced
  666 frames at 1080x1920.

PixiJS creates and renders every visual frame. `src/scene.js` builds the
continuous control room, agent core, tool cards, action/result packets, routed
data trails, chart, loop, kinetic captions, and transitions with PixiJS v8
`Application`, `Container`, `Graphics`, and `Text`. `Application.init()` runs
with `autoStart: false`, `preference: "webgl"`, and
`preserveDrawingBuffer: true`; `renderFrame(frame)` updates the scene and calls
`app.render()`. Playwright captures only the resulting canvas pixels. FFmpeg
does not draw the visuals; it encodes frames and handles audio/final packaging.

## Exact research provenance

Research and retrieval date: **2026-10-19**.

### Official PixiJS skills

Repository: `https://github.com/pixijs/pixijs-skills`

Inspected at commit
`df555b8fbc12acec1e1cfae942bef417f2579169`
([commit](https://github.com/pixijs/pixijs-skills/commit/df555b8fbc12acec1e1cfae942bef417f2579169)).
The implementation followed these official skill files:

- `skills/pixijs-application/SKILL.md` — async `Application.init()`,
  `autoStart: false`, manual `app.render()`, and `preserveDrawingBuffer`.
- `skills/pixijs-core-concepts/SKILL.md` — WebGL renderer and deterministic
  render-loop guidance.
- `skills/pixijs-scene-container/SKILL.md` — scene-graph grouping, transforms,
  visibility, and teardown.
- `skills/pixijs-scene-graphics/SKILL.md` — v8 shape-then-fill/stroke API.
- `skills/pixijs-scene-text/SKILL.md` — v8 options-object `Text` API and
  update-cost guidance.
- `skills/pixijs-ticker/SKILL.md` — fixed-rate/manual update patterns.
- `skills/pixijs-performance/SKILL.md` — object reuse/destroy tradeoffs.

Canonical raw source pattern:
`https://raw.githubusercontent.com/pixijs/pixijs-skills/<commit>/skills/<skill>/SKILL.md`.

### Official PixiJS documentation and source

- `https://pixijs.com/llms`
- `https://pixijs.com/8.x/guides/getting-started/intro`
- `https://pixijs.com/8.x/guides/getting-started/quick-start`
- `https://github.com/pixijs/pixijs` README, inspected at commit
  `458bcfddf8eb092144d24017d8f29014da70c146`
  ([commit](https://github.com/pixijs/pixijs/commit/458bcfddf8eb092144d24017d8f29014da70c146)).
- npm release metadata for `pixi.js@8.22.0`:
  `https://registry.npmjs.org/pixi.js/8.22.0`

### Community skills researched

- `https://github.com/gamedev-skills/awesome-gamedev-agent-skills`
- `https://github.com/freshtechbro/claudedesignskills` (`pixijs-2d`)

These were surveyed for current community conventions but were not used as
implementation authority. The maintained official PixiJS skills were newer and
directly matched v8.22.0.

## Local skills used

- **`speech`** from
  `/Users/rajeev/.codex/skills/speech/SKILL.md`: narration segmentation,
  concise natural phrasing, and audio validation discipline. Its cloud TTS CLI
  was not used because the worker brief explicitly required installed local
  Kokoro.
- **`playwright-cli`** from
  `/Users/rajeev/.codeium/windsurf/skills/playwright-cli/SKILL.md`: browser
  automation/session behavior and screenshot workflow. The implementation
  uses the installed Playwright Node API directly because this is a scripted
  deterministic renderer, not an interactive site.

`skill-index-refresh.py --find` found no installed PixiJS-specific skill. The
official PixiJS skills above were therefore researched from their maintained
repository and used as the authoritative technology workflow.

## Narration and sound design

- **Narration:** installed Kokoro-js **1.2.1** with Transformers.js **3.8.1**.
- **Model:** existing q8 ONNX cache at
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`.
- **Voice:** `bf_emma` from
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`.
- **Safety:** `generate-audio.mjs` sets `allowRemoteModels = false`, disables
  filesystem/browser model caches, and loads the existing model directory. No
  TTS weights were downloaded or copied.
- **Generation:** five original narration clips were generated in 7.018 s.
  Durations were 3.400, 3.375, 4.075, 2.950, and 4.400 seconds.
- **Sound design:** `effects.wav` is synthesized locally in
  `generate-audio.mjs`: low 47/94 Hz room hum, five short UI clicks at caption
  starts, and three restrained moving-data cues. No third-party audio assets
  are used.
- **Mix:** 22.2 s, 48 kHz stereo WAV; narration is placed at 0.45, 3.55, 7.75,
  12.65, and 16.55 s. The mix is loudness-limited to a measured 0.665 peak and
  0.0696 RMS.

## Render commands and measured timings

Commands:

```bash
node scripts/generate-audio.mjs
./scripts/mix-audio.sh
node scripts/render-frames.mjs first   # mandatory first cut
./scripts/build.sh first
node scripts/render-frames.mjs final   # creative refinement
./scripts/build.sh final
./scripts/verify.sh
```

Measured:

| Stage | Result |
|---|---:|
| Kokoro + effects generation | 7.018 s |
| First-cut 666-frame PixiJS/WebGL capture | 67.828 s |
| Final 666-frame PixiJS/WebGL capture | 68.265 s |
| Final FFmpeg encode/preview/contact sheet | 3.10 s real |

Final capture metadata: `1080`, `1920`, `30`, `22.2`, `webgl`, `666 frames`.

## Mandatory first-cut review

The complete first cut was rendered, encoded, and sampled at frames
15, 125, 245, 385, 515, and 645 (opening, tool choice, action, result, loop,
ending).

Concrete findings:

1. The opening caption was too faint during its first visible beat.
2. Packet labels and tool-card typography were undersized for phone review.
3. Action and result packets looked like separate cards instead of one
   continuous data exchange.
4. The ending did not state the complete four-step loop as one phrase.

### Creative refinement made

- Caption fades now resolve within 0.18 s and the caption plate/vignette
  contrast was increased.
- Packet labels were enlarged from 20 to 25 px.
- Added curved action/result routes with seven moving data beads per route,
  visibly connecting the agent and tool console in both directions.
- Added the closing ribbon `CHOOSE → ACT → READ → CONTINUE`.
- Reduced edge vignette opacity so the control-room details remain visible on
  small screens.

The narration, script, beat timing, encoding settings, and layout hierarchy
were preserved. All 666 frames were rerendered after these changes.

## Final media verification

### `deliverables/final.mp4`

- Duration: **22.200000 s**
- Size: **4,540,191 bytes**
- Video: **H.264**, **1080x1920**, **30/1 fps**, **yuv420p**
- Audio: **AAC**, **48,000 Hz**, **2 channels**
- Full mapped video+audio decode with `ffmpeg -xerror`: **PASS**
- SHA-256:
  `cdbbd6668e57d19205a56b3e5258b4ffb752a9fe49d6602dc1aee7982e1a2b8c`

### `deliverables/preview.mp4`

- Duration: **22.200000 s**
- Size: **1,094,131 bytes**
- Video: **H.264**, **540x960**, **30/1 fps**, **yuv420p**
- Audio: **AAC**, **48,000 Hz**, **2 channels**
- Full mapped video+audio decode with `ffmpeg -xerror`: **PASS**
- SHA-256:
  `279e95c54b15052d1a402c28634182c53f79fa3c6db516825f7a89d03cd2066c`

### `deliverables/contact-sheet.jpg`

- Six representative frames in a 3x2 sheet.
- Size: **137,186 bytes**
- SHA-256:
  `6d0d693e8b63ebe4071af6134f8059af06e63d6d808c969fbc9891f274b3f3a7`

### Synchronisation/audio evidence

- Mix duration exactly matched picture: **22.2 s**.
- 20 ms RMS analysis showed energy onsets at all five planned narration starts.
- The start offsets in `assets/audio/timing.json` exactly match the caption
  windows in `src/script.json` and `src/scene.js`.
- Final and preview audio streams both decoded without error.

## Known limitations

- This environment cannot provide a human perceptual listening report. Audio
  was verified through local generation metadata, waveform peak/RMS and onset
  analysis, caption/clip timing comparison, and full stream decode. The
  Kokoro output remains AI-generated voice audio.
- Chrome 155 used SwiftShader for deterministic headless WebGL capture. This
  is appropriate for repeatable frame production but is not a GPU performance
  benchmark.
- Captions use system Arial rather than a custom embedded font. This avoids an
  extra font asset/cache and rendered consistently in the pinned Chrome build.
- The renderer is deliberately a minimal UMD PixiJS workflow rather than a
  Vite application. This keeps the benchmark focused on PixiJS rendering and
  avoids retaining package-manager dependencies.
