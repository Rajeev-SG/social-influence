# Report: MotionForge — What is temperature in AI?

## Topic and teaching goal

**Topic:** what “temperature” means when an AI chooses the next token.

**One-sentence goal:** Teach a beginner that temperature controls how surprising
the next choice is allowed to be: low temperature keeps a focused route, high
temperature opens more possible routes, and neither setting changes intelligence.

The film uses one analogy and visual through-line: a “choice machine” receives
context, chooses one next word, and sends it down either one locked route or a
fan of possible routes.

## Technology and rendering role

- **Primary production technology:** MotionForge `1.4.0` (`motionforge` npm package).
- **Upstream source observed:** `codedbytahir/motionforge`, commit
  `d0f24662dc5de7f44f914ff18fe34ea901eee6b8`.
- **Runtime:** Node `v26.7.0`, React `19.2.0`, Vite `7.2.2`, TypeScript `5.9.3`.
- **MotionForge role:** `src/scene.tsx` supplies all typography, scene timing,
  diagrams, animated paths, captions, transitions and deterministic frame state.
  `src/main.tsx` mounts the scene through MotionForge `PlayerComposition` at a
  controlled frame.
- **Capture/encoding role:** `scripts/render.mjs` drives that MotionForge
  composition in headless Chromium and saves 735 PNG frames at 1080x1920.
  FFmpeg `9.0.2` encodes those frames as H.264/yuv420p and muxes AAC audio.
  FFmpeg does not generate any visual content.
- **Output:** `final.mp4` is 1080x1920, 30/1 fps, 24.5 seconds, H.264,
  yuv420p, with 48 kHz stereo AAC. `preview.mp4` is 540x960.

MotionForge’s README describes the framework as deterministic and frame-accurate
and exposes `KineticTypography` for kinetic type. Its current `renderer/export.ts`
contains a browser-only WebCodecs/WebM path and explicitly notes that the simple
chunk concatenation is not a complete muxer; therefore this project uses the
smallest compatible capture/encoding workflow described above.

## Current documentation and examples researched

Research date: 2026-10-19.

- [MotionForge repository README](https://github.com/codedbytahir/motionforge/blob/d0f24662dc5de7f44f914ff18fe34ea901eee6b8/README.md)
  — deterministic frame-accurate React/WebGL engine, MotionForge usage and
  `KineticTypography` API.
- [MotionForge `motionforge@1.4.0` package metadata](https://www.npmjs.com/package/motionforge)
  — current release, MIT license and renderer/player exports.
- [Kokoro-js README](https://www.npmjs.com/package/kokoro-js) and the installed
  `1.2.1` package README at
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/README.md`
  — local `KokoroTTS.from_pretrained`, q8 dtype, CPU device, `generate()` and
  WAV output.
- [Hugging Face Generation Strategies](https://huggingface.co/docs/transformers/generation_strategies)
  — current decoding-strategy guidance; sampling temperature controls randomness
  when selecting the next generated token.

## Skills used and provenance

The required skill search was run with:

```sh
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py \
  --find "MotionForge video rendering motion graphics ffmpeg narration Kokoro"
```

It returned **no installed MotionForge skill**. A second search for
`speech narration audio TTS` returned one installed skill:

- **Skill:** `speech`
- **Path:** `/Users/rajeev/.codex/skills/speech/SKILL.md`
- **Provenance:** installed local Codex skill, discovered by the required
  `skill-index-refresh.py` search.
- **Use:** its narration workflow and audio validation conventions were followed;
  its OpenAI TTS CLI was intentionally not used because the brief mandates the
  already-installed local Kokoro setup. No invented or stale MotionForge skill
  was used.

## Local TTS and audio

- **Engine:** Kokoro 82M q8 ONNX through installed `kokoro-js` `1.2.1`.
- **Model cache:** `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`.
- **Voice:** `bf_emma` from
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`.
- **Safety:** `generate_audio.mjs` sets `env.allowRemoteModels=false`, so no TTS
  weights can be downloaded. No model weights or caches were copied into this
  project.
- **Narration:** six original segments are synthesized as WAV clips and measured
  with `ffprobe`; 120 ms pauses are inserted between clips. The resulting
  `assets/narration.wav` is 24.35 seconds at 48 kHz stereo.
- **Captions:** `src/timeline.json` records measured segment start/end times and
  the scene/caption component uses those timestamps.
- **Sound design:** `scripts/generate_sfx.sh` synthesizes local `lock.wav`,
  `sparkle.wav`, and `whoosh.wav` with FFmpeg oscillators/noise and places them
  at the low-temperature, high-temperature and comparison cues.

Kokoro synthesis succeeded on the first complete run. Later repeated synthesis
attempts exited with code 134 inside the bundled phonemizer after the six
segment WAVs already existed; the idempotent script therefore reuses those
verified clips and does not repeat TTS inference.

## Render command and measured time

Command:

```sh
node scripts/generate_audio.mjs
bash scripts/build.sh
```

The refined full render is recorded in `assets/render-timing.json`:

- started: `2026-10-19T00:33:45.131Z`
- elapsed: **130,114 ms** (2 minutes 10.114 seconds)
- frames: 735 at 30 fps

`scripts/build.sh` also generated the SFX, captured the MotionForge frame
sequence, encoded `picture.mp4`, mixed the final audio, made the preview and
contact sheet, and invoked verification.

## Full-render inspection findings

Representative extracted frames covered the opening, setup, low transition,
low scene, high transition, high scene, comparison transition, comparison scene,
end transition and ending. The first complete render was inspected before
refinement and found:

1. The low-temperature path visually ended beside the wrong branch node, making
   the deterministic route too faint and ambiguous.
2. The contact-sheet sampling tiled only ten frames and omitted the ending.

The actual low/high/ending frames and the contact sheet were visually inspected
again after the refinement. The low scene now has a bright dashed cyan route
ending at `clear`, a `SAFEST ROUTE LOCKED` badge, and dimmed alternatives. The
high scene has four distinct paths with `strange` selected. The contact sheet is
now a deliberate 3x2 map containing all six major scenes, including the ending.

The mixed MP4 audio was played end-to-end with `afplay` and exited 0. Audio was
also measured with `astats`/`volumedetect`: peak -6.030838 dBFS, RMS
-23.822206 dBFS, no flat factor, and 1,168,800 samples in the extracted stereo
WAV. `silencedetect` found no unexpected silence block of 250 ms or longer.

## Exact creative refinement

The substantive refinement pass changed:

- `src/scene.tsx`: the low route now targets the `clear` node using the selected
  branch coordinate, is thicker/brighter, and its label contrast is increased;
  low mode receives an explanatory `safest route locked` badge.
- `src/styles.css`: added the lock badge treatment.
- `scripts/build.sh`: replaced interval sampling with exact frame selection
  (`20, 120, 260, 420, 540, 700`) and a 3x2 contact-sheet tile so every major
  scene, including the ending, is represented.

After the change, the project was type-checked and fully re-rendered. No
unrelated files or sibling experiments were edited.

## Final media verification

`node scripts/verify.mjs` wrote `assets/qa.json` and reported:

| File | Verified |
| --- | --- |
| `deliverables/final.mp4` | 1080x1920, H.264, yuv420p, 30/1 fps, 24.500000 s, AAC 48 kHz stereo |
| `deliverables/preview.mp4` | 540x960, H.264, yuv420p, 30/1 fps, 24.500000 s, AAC 48 kHz stereo |
| `deliverables/contact-sheet.jpg` | MJPEG, 874x1008, 3x2 six-scene contact sheet |

Additional checks passed:

- `npx tsc --noEmit`
- `ffmpeg -v error -xerror -i deliverables/final.mp4 -f null -`
- `afplay` playback of the actual mixed audio (exit 0)
- `ffprobe` stream inspection and `astats`/`volumedetect` audio measurement

## Known limitations

- MotionForge’s published `motionforge@1.4.0` package advertises
  `motionforge/styles.css`, but that file is absent from the installed package;
  the composition uses its own `src/styles.css` and does not import the missing
  file.
- The current MotionForge renderer export path is browser-oriented and its
  simple WebCodecs chunk concatenation is not a complete MP4 muxer, so the
  deterministic frame capture plus FFmpeg encoding workflow is used and
  documented above.
- The local phonemizer process is unstable when repeatedly synthesizing clips
  after the first successful run; existing verified Kokoro segment WAVs are
  reused by the idempotent build script. No TTS fallback was needed.
