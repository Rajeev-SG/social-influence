# REPORT

## Topic and teaching goal

**Topic:** What is fine-tuning?

**Teaching goal:** Show beginners that fine-tuning is focused additional
training for an already-trained model: curated examples and feedback adapt
selected behavior for a specialist task while the broad foundation remains.

The visual through-line is `BASE -> EXAMPLES -> PRACTICE -> SETTINGS -> OUTCOME`.
The specialist-training analogy is a chef who already knows cooking and learns a
bakery's croissant style through a few guided shifts, recipes, and coaching.

## Technology and rendering role

- **Primary production technology:** FFCreator **7.5.8** (`ffcreator` npm
  package), with `inkpaint` 2.8.1 and `canvas` 3.2.3.
- **FFCreator role:** `src/film.js` creates five `FFScene` chapters at
  1080x1920 / 30 fps using `FFImage`, `FFText`, `FFRect`, scene transitions,
  FFCreator animations, and timed captions. FFCreator/InkPaint rasterizes the
  complete animated picture and FFCreator's FFmpeg synthesis writes the H.264
  master.
- **Audio:** one pre-mixed stereo WAV is attached as FFCreator global audio;
  FFCreator encodes it as AAC.
- **Post-production:** FFmpeg 9.0.2 generates the smaller preview copy,
  contact sheet, extracted-frame QA, loudness measurement, and decode checks.
- **Runtime used:** Node 26.7.0, npm 11.19.0, FFmpeg/FFprobe 9.0.2.

Current official material consulted:

- `https://github.com/tnfe/FFCreator`
- `https://raw.githubusercontent.com/tnfe/FFCreator/master/README.md`
- `https://raw.githubusercontent.com/tnfe/FFCreator/master/package.json`
- `https://raw.githubusercontent.com/tnfe/FFCreator/master/docs/guide/installation.md`
- npm registry `ffcreator` release metadata.

The official README and installation guide confirm the required Node.js,
FFmpeg, `node-canvas`, and `headless-gl` roles used here. The maintained GitHub
source currently reports package version `8.0.1`; the current published npm
release is `7.5.8`, which is the version actually rendered.

## Skills used and provenance

1. **Installed skill: `speech`**
   - Path: `/Users/rajeev/.codex/skills/speech/SKILL.md`
   - Used for narration discipline: short beginner script, natural pacing,
     explicit delivery constraints, and validation of intelligibility and cue
     timing. Its OpenAI backend was deliberately not used because this benchmark
     mandates the local Kokoro setup.

2. **Installed skill: `worker-context-discipline`**
   - Path: `/Users/rajeev/.codex/skills/worker-context-discipline/SKILL.md`
   - Used to keep the delegated work bounded to one assigned directory and to
     preserve concrete acceptance evidence without expanding scope.

3. **Installed skill: `web-search`**
   - Path: `/Users/rajeev/.agents/skills/web-search/SKILL.md`
   - Used with SearXNG as the primary route for current FFCreator repository,
     package, and installation documentation.

4. **Installed skill: `transcribe`**
   - Path: `/Users/rajeev/.codex/skills/transcribe/SKILL.md`
   - Consulted for local audio QA options. No API transcription was used; the
     final audio was instead played with `afplay` and checked against exact
     Kokoro reference clips.

No FFCreator-specific installed skill matched `skill-index-refresh.py`; the
current FFCreator API was verified from the official repository and installed
package type/source files instead.

## Local TTS and audio

- **Voice:** Kokoro 82M q8 ONNX, `bf_emma`.
- **Existing model cache:** `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- **Existing voice file:** `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`
- `scripts/narrate.cjs` uses `local_files_only: true`; no TTS weights or
  redundant environments were downloaded.
- Seven utterances were synthesized at speed 0.95, silence-trimmed with 55 ms
  head and 75 ms tail breathing margins, placed by exact sample count, and saved
  as the reference clips used for synchronization.
- `scripts/soundscape.py` synthesizes the original stereo suspended pad, glass
  ticks, restrained transfer whooshes, low impacts, and closing resolve with
  the Python standard library. No sampled or third-party audio is used.
- `scripts/mix_audio.sh` mixes narration at unity and the bed at 0.34, limits
  peaks, and normalizes the mix to a stable spoken-video level.
- The delivered audio was played directly from the final MP4 extraction with
  `afplay` after rendering.

## Render command and timings

Commands:

```sh
node scripts/render.cjs
./scripts/render.sh
```

Measured FFCreator render timings:

- First complete valid full render: **6.52 seconds**.
- Creative-refinement render: **5.63 seconds**.
- Final safe-area correction render: **5.34 seconds**.

The final timing record is written by `scripts/render.cjs` to
`.render/render-timing.json` during rendering. The FFCreator usage string for
the final run reported `time 5.34`, `memory 23917160 46432256 512933888`,
`cpu 51.5%`, and `68.3%`.

## Full-render inspection findings

The first complete render was decoded and its actual MP4 frames were inspected:

- The opening and core model diagram were readable, with a clear broad-to-
  focused title beat.
- The course scene explained curated examples and feedback, but the first pass
  left short empty title-card intervals at chapter entry, especially around
  15.25s and 19.65s.
- The chef/pastry analogy was visually distinct and beginner-readable, but the
  scene needed a stronger connection to the model-settings explanation.
- The settings scene made the dial board clear, but the first pass did not
  explicitly label the before/after states.
- The ending comparison was understandable; the generalist/specialist panels
  were slightly delayed relative to the narration.
- Audio inspection found narration and effects present, clean, and consistently
  mixed. Cross-correlation of the final mix against all seven saved Kokoro
  reference clips measured **4.5-5.0 ms** offsets.

Native setup findings were kept separate from the visual review: this rig had
npm install scripts disabled, so `canvas` and `gl` initially had no native
bindings; Node 26 also required temporary C++20 and Python compatibility
adjustments for `gl`, plus a Node-only ECharts detection shim in the render
entry. Those temporary dependency files are not retained.

## Creative refinement changes

The substantive refinement pass made these exact changes:

1. Added a persistent `BASE -> EXAMPLES -> PRACTICE -> SETTINGS -> OUTCOME`
   adaptation rail to every scene, with the active stage highlighted and prior
   stages visible as context.
2. Moved the core, cards, chef/pastry/recipe, dial board, and generalist/
   specialist panels 0.2-0.5 seconds earlier so chapter transitions land on
   explanatory visuals instead of empty title states.
3. Added explicit `BASE SETTINGS` and `AFTER FOCUSED TRAINING` labels to the
   settings scene and made the before/after crossfade more immediate.
4. Made the selected-settings needle sweep and `FOUNDATION STAYS` message
   arrive earlier and more visibly.
5. Corrected the right-side settings label from x=910 to x=810 after the
   refined contact sheet showed it approaching the safe-area edge.

The final render was re-extracted and rechecked after these changes.

## Final media verification

`python3 scripts/verify_media.py` passed its contract gate. Evidence:

- `deliverables/final.mp4`
  - H.264, yuv420p, 1080x1920, 30/1 fps, 691 frames.
  - Container duration: **23.065542 seconds**; video stream duration:
    **23.033333 seconds**.
  - AAC LC, 48 kHz, 2 channels / stereo.
  - Full FFmpeg decode with `-xerror`: no errors.
  - Integrated loudness: **-16.1 LUFS**; true peak: **-3.5 dBFS**.
  - Size: **2,723,169 bytes**.
- `deliverables/preview.mp4`
  - H.264/yuv420p, 540x960, 30/1 fps, 691 frames, stereo AAC 48 kHz.
  - Full FFmpeg decode with `-xerror`: no errors.
  - Size: **604,391 bytes**.
- `deliverables/contact-sheet.jpg`
  - MJPEG RGB, 1000x1166.
  - Five representative frames covering all five major scenes.
  - Size: **164,789 bytes**.
- Caption/voice synchronization: all seven measured cue references matched the
  final mix within **4.5-5.0 ms**.
- Final MP4 audio extraction played successfully with `afplay`.
- Source syntax checks passed for the Node and Python scripts and shell wrappers.

## Known limitations

- The narration is synthetic Kokoro speech; it is clear and consistent but less
  expressive than a directed human performance.
- Captions are sentence-level, not word-level karaoke timestamps.
- The chef/bakery story is a deliberately simple specialist-training analogy,
  not a literal description of gradient updates or model internals.
- The dial-board graphic explains selective adaptation conceptually; it does not
  show a real model's parameter count, layer names, or training traces.
- FFCreator's npm release is `7.5.8` while the maintained GitHub source tree
  currently labels itself `8.0.1`; the rendered API is the published 7.5.8 API.
- Native `canvas`/`gl` setup for Node 26 required temporary local build
  compatibility work. No dependency tree, model cache, or native build output
  is retained in the deliverable.
