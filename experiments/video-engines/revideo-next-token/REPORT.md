# REPORT

## Topic and teaching goal

**Topic:** How does next-token prediction work?

**Teaching goal:** Show that a language model reads the pieces already present, scores possible next pieces as a probability distribution, selects one, appends it, and repeats—without implying that likely wording is guaranteed truth.

## Technology and rendering role

- **Primary production technology:** Revideo **0.11.0** (`@revideo/core`, `@revideo/2d`, `@revideo/renderer`, `@revideo/ffmpeg`, `@revideo/vite-plugin`, and `@revideo/ui`, all pinned at 0.11.0).
- **Revideo role:** `src/scene.tsx` defines the complete 1080 × 1920, 30 fps film as a deterministic Revideo/Motion Canvas generator scene. Revideo drives all typography, diagrams, camera motion, transitions, cue timing, and frame production in headless Chromium.
- **Exporter:** Revideo’s `@revideo/core/wasm` MP4 exporter produced the frame timeline. Four finite ranges were rendered in isolated Node processes and concatenated with FFmpeg.
- **Post-production:** FFmpeg 9.0.2 mixed the already measured narration and procedural effects, normalized the mix, and encoded the review copy/contact sheet. It did not generate the animated picture.
- **Runtime used:** Node 26.7.0, FFmpeg/FFprobe 9.0.2, Google Chrome for headless Chromium.

Current official material consulted:

- `https://midrender.com/revideo/docs`
- `https://midrender.com/revideo/docs/guide/installation-and-setup`
- `https://midrender.com/revideo/docs/guide/project-structure`
- `https://midrender.com/revideo/docs/guide/rendering-videos`
- `https://midrender.com/revideo/docs/api-reference/renderer/renderVideo`
- `https://github.com/midrender/revideo` and `packages/template`
- `https://github.com/midrender/examples`

The official repository was active and unarchived at research time; npm `@revideo/core@0.11.0` is the current release used here.

## Skills used and provenance

1. **Installed local skill: `revideo-video`**
   - Source: `praxstack/skills-and-personas`
   - Path: `skills/teacher/skills/revideo-video/SKILL.md`
   - Exact commit: `e1d196e74ed88df3f5cdce8a06390331f9862300`
   - Installed locally to: `assets/skills/revideo-video/`
   - SKILL.md SHA-256: `da339aab390be6f16f21889a95d2fe30f2421601374b4f8429c1eedde8784302`
   - Upstream state checked: MIT licensed, non-archived, pushed 2026-10-18.
   - Guides used: `references/revideo-guide.md`, `references/quality-bar.md`, `references/voice-and-audio.md`, and `references/lessons-learned.md`.
   - Installation method: `skill-installer` helper with `--dest` inside this experiment, so no shared skill directory was changed.

2. **`skill-installer`**
   - Path: `/Users/rajeev/.codex/skills/.system/skill-installer/SKILL.md`
   - Used only to verify supported GitHub installation options and install the Revideo skill locally.

3. **`web-search`**
   - Path: `/Users/rajeev/.agents/skills/web-search/SKILL.md`
   - Used with SearXNG as the primary search route for current Revideo docs, repositories, examples, and skill discovery.

No installed Revideo-specific skill matched `skill-index-refresh.py`; the relevant maintained community skill was discovered through GitHub code search and validated before local installation.

## Local TTS and audio

- **Voice:** Kokoro 82M q8 ONNX, `bf_emma`.
- **Existing model cache:** `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- **Existing voice file:** `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`
- `scripts/narrate.cjs` uses `local_files_only: true`; no TTS weights or redundant environments were downloaded.
- Seven utterances were synthesized at speed 0.97, energy-trimmed with breathing margins, placed by exact sample count, and saved as the exact reference clips used by the mix.
- `scripts/soundscape.py` synthesises the original stereo pad, glass ticks, restrained whooshes, low impacts, and closing resolve with the Python standard library. No sampled or third-party audio is used.
- Final mix: narration at unity, procedural bed at 0.32, stereo output, loudness-normalized to −16 LUFS.

## Render command and timing

```sh
./scripts/render.sh
```

Measured refined full-render time: **11 seconds** for four isolated Revideo ranges plus FFmpeg concatenation and the mandatory 603-frame gate. `.review/render-timing.json` records the same command and timing.

## Full-render inspection findings

The initial Revideo FFmpeg-exporter attempts were treated as render-pipeline failures and were not packaged:

- An `Infinity` render override produced a 0.133-second / 4-frame file.
- Revideo 0.11’s FFmpeg `ImageStream` failed on Node 26 with `stream.push() after EOF`; one worker attempt also tried to mux `visuals.mp4` before it was complete, leaving an invalid partial stream with no usable `moov`.
- The complete solution was finite-range Wasm MP4 rendering in isolated processes, followed by stream-copy concatenation and a hard frame/duration gate.

The first valid complete cut rendered **603 frames / 20.121333 seconds** and was mixed with audio before review. Actual extracted frames and the contact sheet showed:

- Motion Canvas `Txt` coordinates act as centers; left-anchored labels and the truth card were clipped at the frame edge.
- Caption `lineHeight: 1.28` was interpreted as pixels, overlapping the two caption lines.
- The context beat left too much empty space and did not visibly explain “reading the pieces.”
- The repeat beat showed the loop but did not visibly leave the next position open.

Audio inspection on the first valid cut found the narration/effects present and clean, but the saved per-line reference clips included Kokoro padding that was not part of the timed mix. That reference asset mismatch was fixed before final synchronization verification.

## Creative refinement changes

1. Converted every left-aligned label, score headline, and truth-card text block to explicit left anchors; widened safe margins and removed all edge clipping.
2. Changed caption line height from `1.28` to 54 pixels, producing clean two-line captions with no collisions.
3. Added a persistent context-reading visual: a cyan scan crosses the five sentence pieces, five signals converge into a central `5 / 5 PIECES READ` state, and that state recedes when scoring begins.
4. Kept the score/ballot story but clarified its hierarchy with the corrected `NEXT-PIECE SCORES / ILLUSTRATIVE`, `What fits next?`, and `VOTES → PROBABILITY` labels.
5. Added a blinking next cursor after the selected `mat`, so the repeated prediction loop visibly leaves the next piece position active.
6. Reworked the final amber card sizing/anchors so `Likely wording / is not guaranteed truth.` remains fully readable under camera drift.
7. Regenerated trimmed per-line TTS references and rechecked all seven cues against the mixed audio; measured offsets were **0–10 ms**.

## Final media verification

- `deliverables/final.mp4`
  - Video: H.264, yuv420p, 1080 × 1920, 30/1 fps, **603 frames**, 20.100 seconds stream duration.
  - Container: 20.121333 seconds including standard AAC/MOV timing padding.
  - Audio: AAC LC, 48 kHz, **2 channels / stereo**.
  - Full FFmpeg decode with `-xerror`: no errors.
  - Integrated loudness: **−16.0 LUFS**; true peak: **−3.9 dBFS**.
  - Size: 7,321,550 bytes.
- `deliverables/preview.mp4`
  - H.264/yuv420p, 540 × 960, 30/1 fps, 603 frames, stereo AAC, 1,119,793 bytes.
  - Full FFmpeg decode with `-xerror`: no errors.
- `deliverables/contact-sheet.jpg`
  - JPEG RGB, 1080 × 1044, 256,491 bytes.
  - Eight representative frames: hook, context reading, scoring, weighted ballot, selection, append, repeat, and likely-versus-truth.
- Caption/voice synchronization: all seven measured cue references matched the final mix within **0–10 ms**.
- Source typecheck: `npm run typecheck` passes.

## Known limitations

- The narration is synthetic Kokoro speech; it is clear and consistent but less expressive than a directed human performance.
- Captions are sentence-level, not fabricated word-level karaoke timestamps.
- The displayed 62/20/12/6 percentages are explicitly illustrative, not a trace from a production model. Sampling can choose a lower-probability token.
- The example uses word-sized “pieces” for beginner clarity; real tokenizers also split words into fragments and include punctuation.
- The film explains next-token prediction only. It does not cover retrieval, tools, training-data governance, or product-specific conversation features.
- Revideo 0.11’s FFmpeg image stream exporter was incompatible with this Node 26 environment. The delivered picture still comes entirely from Revideo through its supported Wasm MP4 exporter; FFmpeg is limited to segment concatenation, audio mixing, verification, and delivery encoding.
