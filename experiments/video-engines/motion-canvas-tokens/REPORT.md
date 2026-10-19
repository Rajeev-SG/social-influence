# Production Report

## Topic and teaching goal

**Motion Canvas — “What are tokens?”** teaches that a tokenizer turns text into
small reusable pieces, that those pieces may be whole words, fragments, or
punctuation, and that each piece is mapped to a number a model can process.

One analogy carries the film: a sentence ribbon enters a sorting gate, is cut
into labelled pieces, and those same pieces travel onward as IDs.

## Technology and rendering role

- **Primary technology:** Motion Canvas **3.17.2** (`@motion-canvas/core`,
  `@motion-canvas/2d`, `@motion-canvas/ui`, and
  `@motion-canvas/vite-plugin` are all pinned to 3.17.2).
- **Renderer role:** Motion Canvas evaluates the generator-based TypeScript/TSX
  scene at 1080 x 1920, 30 fps and writes 746 native PNG frames. All typography,
  diagrams, token tiles, transitions, captions and motion are authored as
  Motion Canvas nodes/signals/tweens.
- **Encoding:** FFmpeg 9.0.2 muxes the Motion Canvas sequence with the final
  stereo WAV and encodes H.264/AAC. FFmpeg does not generate the visuals.
- **Authoring reference:** current Motion Canvas Quickstart, Animation Flow,
  Tweening, Transitions, Media, Rendering and Configuration docs, plus the
  official `motion-canvas/motion-canvas` examples. Stable 3.17.2 was used
  rather than `3.18.0-alpha.0`.

## Skills used and provenance

The installed skill search returned no exact Motion Canvas match. Current
community repositories were checked; the most relevant maintained pack was
installed project-locally under `assets/skills/`:

- **Repository:** [VideoZero/skills](https://github.com/VideoZero/skills)
- **Exact commit:** `670ff96af6149f0ac8850380a466f073471e600c`
- **Commit date:** 2026-10-03
- **Commit purpose:** “fix wrong API examples against motion-canvas 3.17.2”
- **License:** Apache-2.0
- **Skills used:** `motion-canvas` (framework/API reference),
  `animation-basics` (timing, staging, easing), and `motion-canvas-agent`
  (render/inspection workflow reference). The agent HTTP plugin was not enabled
  in the final project; rendering used the official editor's PNG exporter.

The full pinned upstream tree is retained with its README and license so the
provenance is auditable without a network connection.

## Local narration and sound

Narration is original and locally synthesized with the existing **Kokoro 82M
v1.0 q8 ONNX** cache at
`/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`.
The exact local voice is `bf_emma.bin` from the existing `kokoro-js` voices
directory. `scripts/narrate.cjs` uses `local_files_only: true`; no TTS weights
or redundant environment were downloaded.

Seven sentences were generated at speed 1.06. Their measured intervals were:

| Cue | Start | End | Text |
|---:|---:|---:|---|
| 1 | 0.180 | 3.524 | Imagine your sentence as a ribbon entering a sorting machine. |
| 2 | 3.744 | 7.216 | A tokenizer cuts it into reusable pieces called tokens. |
| 3 | 7.456 | 11.869 | A token can be a whole word, a fragment, punctuation, or even a space pattern. |
| 4 | 12.109 | 14.553 | So playground can become play plus ground. |
| 5 | 14.773 | 18.041 | Each piece then gets an ID, a number the model can use. |
| 6 | 18.281 | 20.880 | Different tokenizers may draw the lines differently. |
| 7 | 21.099 | 23.782 | But text becomes chunks, and chunks become numbers. |

The first synthesis measured 26.039s and was rejected as out of contract; the
timing above is the corrected 24.282s narration. `scripts/soundscape.py` adds an
original restrained pad, caption-aligned glass ticks, token reveal ticks,
band-limited transition air moves, and a low closing resolve. The final mixed
asset is 24.7815s stereo PCM at 48 kHz before AAC encoding.

Caption and visual starts use the measured cue boundaries above. Audio sync was
checked from the generated line intervals, decoded waveform/level behavior,
cue-aligned effects, and a clean decode of the final mix. No local ASR runtime
or cached speech-recognition model was available, so no word-level transcription
is claimed.

## Render command and timing

Final render command:

```sh
npm run build
npm run render
python3 scripts/deliver.py
```

- Final Motion Canvas export: **40.26s real time**, 746 PNG frames.
- Final encode/preview/contact-sheet pass: **3.00s real time**.
- Earlier complete renders were also measured at 40.11s and 40.31s during QA.

## Full-render inspection findings and refinement

The first complete 746-frame render and encoded MP4 were inspected before
delivery. Native PNG QA found a blocking layout defect at frames
`000020`, `000104`, `000248`, `000492`, `000576` and `000627`: oversized text
extended toward or beyond the 1080px edges and collided with the centre
token/diagram layer.

Two concrete causes were identified:

1. The shared `Label` component defaulted to left alignment at `x=0`, so
   supposedly centred headings extended to the right.
2. `reveal()` treated its movement offset as an absolute y-position, pulling
   top headings and bottom captions into the centre during entry.

The substantive creative/layout repair:

- Constrained all shared labels to centred 840px text boxes inside a
  conservative 72–1008px mobile safe area.
- Split `A WORD ISN'T ALWAYS / ONE TOKEN` and
  `TOKENS ARE MODEL / CONVENTIONS` into deliberate hierarchy lines.
- Converted the opening and bridge captions to centred multi-line blocks and
  reduced long caption type.
- Preserved each node's authored position in `reveal()`, restoring top title,
  centre diagram and bottom caption zones.
- Strengthened hierarchy by keeping section titles in the upper third,
  explanatory diagrams in the centre, and spoken captions in the lower band.
- Re-rendered every Motion Canvas frame and rebuilt all three deliverables from
  that repaired sequence; the contact sheet is extracted from the repaired
  master.

## Final native-frame verification

The delivered `final.mp4` itself was decoded at native resolution for opening,
examples, ID, boundary, bridge and ending checks. OCR/pixel boxes were evaluated
against the 72–1008px safe area:

| Frame | Beat | Native size | Safe-area failures | Verified hierarchy |
|---:|---|---:|---:|---|
| 000020 | Opening headline/ribbon | 1080 x 1920 | 0 | title y 315–458; ribbon y 691–791 |
| 000104 | Opening caption | 1080 x 1920 | 0 | title y 315–458; caption y 1661–1695 |
| 000248 | Word-fragment examples | 1080 x 1920 | 0 | title y 307–444; caption y 1667–1699 |
| 000492 | ID mapping | 1080 x 1920 | 0 | title y 319–411; diagram y 764–1338; caption y 1667–1699 |
| 000576 | Tokenizer boundary | 1080 x 1920 | 0 | title y 307–444; diagram y 778–1054; caption y 1668–1700 |
| 000627 | Boundary hold | 1080 x 1920 | 0 | same separated hierarchy |
| 000650 | Text-to-ID bridge | 1080 x 1920 | 0 | bridge y 785–1252; caption y 1668–1692 |
| 000720 | Ending | 1080 x 1920 | 0 | takeaway centred at y 1036–1270 |

## Final media verification

- `final.mp4`: **24.7815s**, **1080 x 1920**, **30/1 fps**,
  **H.264**, **yuv420p**, **stereo AAC**, 48 kHz.
- `preview.mp4`: 24.7815s, 540 x 960, 30/1 fps, H.264/yuv420p, stereo AAC;
  697,277 bytes versus the 1,993,903-byte master.
- `contact-sheet.jpg`: 1500 x 1150 RGB, ten representative frames in a 5 x 2
  grid, regenerated from the repaired master.
- FFmpeg full decode with `-xerror`: passed for both final and preview.
- Audio: integrated **−17.3 LUFS**, LRA 1.1 LU, true peak **−4.9 dBFS**;
  no clipping.
- Motion Canvas project build (`tsc && vite build`): passed before the final
  full render.

## Known limitations

- Kokoro speech is synthetic and smoother than a directed human performance.
- Word-level ASR verification was not possible without adding a speech model;
  sync evidence is measured cue timing plus decoded audio/level review.
- Token splits and numeric IDs are explicitly illustrative. Real vocabularies
  can split the same words differently.
- The film explains tokenizer input representation, not training, attention,
  generation, retrieval, tools or the full internals of a language model.
