# Benchmark Report

## Topic and teaching goal

Topic: **Lottie-web - Why does AI hallucinate?**

One-sentence goal: teach beginners that a language model predicts plausible
next pieces of text instead of checking a fact database, so a fluent answer can
still be wrong.

The single analogy is **a confident storyteller without a fact-checker**. The
visual through-line is a warm orange "story" path that branches into a plausible
story and a verified fact, then returns to the instruction to check claims.

## Technology and rendering role

- Motion renderer: `lottie-web` **5.13.0**, SVG renderer.
- Vendored runtime: `assets/vendor/lottie.min.js`, SHA-256
  `2eb762973aec914d981f426123040bfac9d26217239605e225ddc7cee17618ac`.
- Generated composition: `src/lottie.json`, 579 frames at 30 fps, 1080x1920,
  91 layers and 35 local assets.
- Role: lottie-web produces all primary motion graphics. It renders the
  background, story rails, diverging paths, probability bars, pattern blocks,
  confidence meter, status marks, animated transforms and timed typography
  assets. `src/render/index.html` only hosts the player and exposes
  `goToAndStop(frame, true)` for deterministic Playwright capture.
- Capture: Playwright 1.63.0 with installed Chrome, one browser batch per 120
  frames. FFmpeg 9.0.2 encodes the captured frames and mixed audio.

This is a minimal compatible workflow: author generated Lottie JSON, load it
with lottie-web, scrub exact frames in a browser, then encode the resulting
pixels. Lottie is not a decorative side element; every scene's explanatory
geometry and motion is in the Lottie timeline.

## Research and skill provenance

Research date: **2026-10-19**.

### Installed skill discovery and usage

The required searches were run:

```text
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find \
  "Lottie web animation rendering video motion graphics"
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find \
  "local Kokoro TTS narration audio mix video"
```

Both returned `no skill matched`. No skill was invented and no unlisted skill
was used. The following installed skills were consulted and used as noted:

| Skill | Source | Use |
|---|---|---|
| `compare-screenshots` | `/Users/rajeev/.codex/skills/compare-screenshots/SKILL.md` | Representative-frame, boundary and image-evidence discipline for the render review. |
| `acceptance-proof` | `/Users/rajeev/.codex/skills/acceptance-proof/SKILL.md` | Real-browser evidence and clean-console acceptance structure. |
| `transcribe` | `/Users/rajeev/.codex/skills/transcribe/SKILL.md` | Consulted for narration QA. Not executed: its required `OPENAI_API_KEY` was not set and no local Whisper runtime was installed. |

### Official documentation and runtime

- lottie-web repository: https://github.com/airbnb/lottie-web
  - HEAD inspected: `bede03d25d232826e0c9dca1733d542d8a7754fb`.
- lottie-web README:
  https://github.com/airbnb/lottie-web/blob/master/README.md
- Usage wiki (renderer and `goToAndStop`):
  https://github.com/airbnb/lottie-web/wiki/Usage
- `loadAnimation` options:
  https://github.com/airbnb/lottie-web/wiki/loadAnimation-options
- Renderer settings:
  https://github.com/airbnb/lottie-web/wiki/Renderer-Settings
- npm package: https://www.npmjs.com/package/lottie-web
  - Version used: `5.13.0`.
  - Tarball SHA-256:
    `00f306a9b5669abf9622c418b549681d1b858e0b7fa7ea6adc0772ca57c3fd4f`.
- Lottie format specification repository:
  https://github.com/lottie/lottie-spec
  - HEAD inspected: `4b55957472f8718e34e9c1298f0e8f021b6c597f`.

### Community skills/references

- LottieFiles `motion-design-skill`:
  https://github.com/LottieFiles/motion-design-skill
  - HEAD inspected: `f9a8a041b85185ee4881b3471d3415e939aac772`.
  - SKILL.md: https://raw.githubusercontent.com/LottieFiles/motion-design-skill/main/skills/motion-design/SKILL.md
  - Used principles: primary/secondary/ambient motion layers, decelerating
    entrances, accelerating exits, limited simultaneous movers,1/3-distance
    restraint and short stagger budgets.
- diffusionstudio `text-to-lottie` community skill:
  https://github.com/diffusionstudio/lottie
  - HEAD inspected: `3c72912fad543897f90045ed4d355813837927fc`.
  - Used guidance: ground motion in concrete assets, think like a camera
    operator, specify FPS/duration and keep a local Lottie player for preview.

No community skill code was copied. They were current research references; the
actual composition is authored by `src/build-lottie.mjs`.

## Narration and sound design

- TTS: installed `kokoro-js` **1.2.1**.
- Model: installed q8 ONNX cache at
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`.
- Voice: `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`.
- Remote model access is disabled in `scripts/generate-narration.mjs`; no TTS
  weights were downloaded.
- Delivery speed: `1.22`. `scripts/mix-audio.py` removes leading/trailing
  silence while preserving a 35 ms breath, resamples to 48 kHz, normalizes the
  speech peak to 0.82, then adds a restrained synthesized bed.
- Sound design: one soft opening swoop, subtle transition ticks, a low
  descending tone when the wrong date appears, a two-note verification chime
  for `1889`, and a quiet closing lift. Effects are synthesized mathematically;
  no third-party audio assets are used.
- Final mix: 19.29 seconds, 48 kHz stereo PCM before AAC encode. Decoded final
  audio measured -20.53 dB RMS, -1.88 dB peak and zero flat-factor/clipping
  indicators.
- Caption/visual timing is generated from
  `assets/audio/narration-timing.json`, not hard-coded independently.

## Render command and measured timing

Command:

```bash
node scripts/render-video.mjs deliverables/final.mp4 deliverables/preview.mp4
```

Measured for the delivered 579-frame source timeline:

- Browser capture: **36,337 ms**
- FFmpeg final + preview encode: **3,108 ms**
- Total: **39,445 ms**
- Final bytes: **1,489,948**
- Preview bytes: **580,290**

Evidence is retained in `assets/render-timing.json`. The encoded MP4 contains
578 complete frames because FFmpeg ends at the 19.29-second audio boundary;
the Lottie source has 579 frames (0..578) and the final duration is compliant.

## Mandatory render-review-refine cycle

### Complete first cut

A complete first cut was rendered before refinement and decoded successfully:
24.735 seconds, H.264/yuv420p, 1080x1920, 30 fps, stereo AAC. Audio measured
-21.59 dB RMS and -1.72 dB peak.

Representative opening, middle, transition and ending frames were extracted,
assembled into a contact sheet and inspected. The audio was decoded and checked
with FFmpeg `astats` and `silencedetect`; line boundaries were also compared to
the generated timing JSON.

### Full-render inspection findings

1. **Major visual defect:** the first contact sheet showed the background,
   story rails, path trims and status marks, but typography and filled cards
   disappeared after roughly 0.73 seconds.
2. **Root cause:** layer transform helpers used a fixed 22-frame local opacity
   timeline. Long scene layers therefore faded out early and remained hidden.
3. **Secondary renderer issue:** animated layer opacity caused lottie-web's SVG
   renderer to set image/shape parent groups to `display:none` at otherwise
   valid mid-scene frames.
4. **Audio pacing:** the first narration pass was too slow/long for the required
   duration; it was tightened by trimming Kokoro's dead air and preserving
   natural inter-line pauses.
5. **Capture robustness:** an unbatched Chromium run stopped producing usable
   frames after the SVG became more populated. This could create a plausible
   but truncated MP4.
6. **Encoding issue:** JPEG-sourced frames initially encoded as `yuvj420p`,
   not the required `yuv420p`.

### Creative and technical refinement

Exact changes after inspection:

- Changed transform animations from a fixed 22-frame window to each layer's
  actual scene duration, so content remains present until its real exit.
- Changed image/shape layer visibility to static opacity while retaining
  Lottie-animated position, scale, trim paths and timed layer windows.
- Preserved paint transparency in Lottie fill/stroke opacity fields instead of
  relying on RGBA color arrays.
- Added a substantive creative layer to the analogy: **CONFIDENCE HIGH /
  VERIFICATION OFF** labels and a story-confidence meter under the
  storyteller card. This makes the "confident but unchecked" mechanism visible,
  not merely stated.
- Corrected probability-bar centering in the next-piece example.
- Rebuilt scene markers and captions from measured speech starts: hook/analogy,
  prediction, divergence, gap invention and close.
- Split Chromium capture into 120-frame batches, asserted every frame exists,
  and made final/preview replacement atomic.
- Added explicit full-range JPEG to limited-range BT.709 `yuv420p` conversion.
- Rerendered and regenerated the preview and contact sheet after these changes.

## Final QA evidence

`bash scripts/verify-media.sh` decoded both MP4s without error and asserted:

| File | Duration | Video | Audio | Size |
|---|---:|---|---|---:|
| `final.mp4` | 19.29 s | H.264, yuv420p, 1080x1920, 30/1 | AAC, 48 kHz, stereo | 1,489,948 B |
| `preview.mp4` | 19.29 s | H.264, yuv420p, 540x960, 30/1 | AAC, 48 kHz, stereo | 580,290 B |
| `contact-sheet.jpg` | n/a | JPEG, 1348x3400 | n/a | 797,068 B |

Additional evidence:

- Clean browser probes at representative frames: one Lottie SVG, zero console
  or page errors.
- OCR of the contact sheet recovered the hook, `CONFIDENT STORYTELLER`,
  `WITHOUT A FACT-CHECKER`, `PREDICT NEXT PIECE`, `1927`, `1889`,
  `PLAUSIBLE STORY`, `VERIFIED FACT`, `FLUENCY != EVIDENCE`, and closing claim
  check content.
- `ffmpeg -i final.mp4 -f null -` and the equivalent preview decode completed
  without errors.
- Current deliverable hashes:
  - `final.mp4`:
    `7d6353fac350e122c9687efaadce36b48b047d01dfded156060222df2b2dbd93`
  - `preview.mp4`:
    `b0c94f6ff649355579332893bed23e11bebc16094edf6990b2555b4c00568072`
  - `contact-sheet.jpg`:
    `61cd9cd83d3d2c29cbf2b2a2d6505cdeefa704be8e9ae4fe175c400df662c648`

## Known limitations

- The brief referenced `../llm-reel/` as a baseline, but that directory was not
  present in the supplied workspace. The requested clarity/simplicity standard
  was applied directly; no side-by-side baseline comparison was possible.
- No human auditory playback or local speech-to-text runtime was available
  (`OPENAI_API_KEY` unset, Whisper/MLX Whisper/faster-whisper absent). Narration
  was therefore verified through the exact Kokoro source text, generated line
  timing, FFmpeg decode/dynamics, silence boundaries and caption alignment
  rather than a separate transcript. This is the main QA limitation.
- Typography is generated as transparent PNG assets and animated inside Lottie,
  rather than using Lottie native text/glyph layers. This keeps rendering
  deterministic across the installed browser/runtime while Lottie still owns
  the motion, timing and scene composition.
- The video uses one concrete factual example (Eiffel Tower 1927 vs 1889) to
  keep the explanation digestible. It does not survey all hallucination causes,
  such as training-data errors, decoding settings or retrieval failures.
