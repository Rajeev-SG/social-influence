# Report: What Are Embeddings?

## Topic and teaching goal

**Topic:** embeddings in beginner terms.

**One-sentence goal:** Teach that an embedding represents a word as numbers that place it on a meaning map, so related words are close and computers can compare meaning by measuring distance.

The film uses one continuous analogy and visual through-line: words without addresses become numerical coordinates, land on a shared map, form a related-word neighbourhood, and produce measurable near/far relationships.

## Technology and rendering role

- **Primary production technology:** Manim Community `0.22.0`.
- **Runtime:** CPython `3.13.12`, selected through `uv 0.10.11`.
- **Renderer:** Manim Cairo renderer, 22 played animations in the retained final render log.
- **Output:** `1080 x 1920`, `30/1 fps`, H.264, `yuv420p`.
- **Audio:** stereo AAC, 48 kHz.
- **Supporting tools:** FFmpeg/FFprobe `9.0.2`, Node `v26.7.0`, Pillow `11.3.0`, NumPy `2.3.4`.

Manim creates all visual frames: typography, vector cards, map grids, pins, neighbourhoods, distance paths, transitions, camera/depth movement and burned-in captions. FFmpeg only normalizes and mixes audio, muxes it with the Manim picture, re-encodes the smaller preview, extracts review frames/contact sheets and verifies the encoded files.

Render command:

```sh
./scripts/build.sh final
```

The exact Manim invocation is assembled in `scripts/build.sh` and uses Manim 0.22.0's current `--output_file`, `--resolution`, `--fps`, `--video-codec`, `--pixel-format` and `--encoder-option` flags.

## Current documentation and examples researched

Research date: 2026-10-18/19.

- [Manim Community stable documentation v0.22.0](https://docs.manim.community/en/stable/)
- [Installation with uv](https://docs.manim.community/en/stable/installation/uv.html)
- [Output and configuration tutorial](https://docs.manim.community/en/stable/tutorials/output_and_config.html)
- [Example gallery](https://docs.manim.community/en/stable/examples.html)
- [Manim render CLI reference](https://docs.manim.community/en/stable/reference/manim.cli.render.html)
- [ManimCommunity/manim releases](https://github.com/ManimCommunity/manim/releases)

The installed CLI help was checked before rendering. This mattered because 0.22.0 uses `--output_file` rather than `--output`, names portrait quality folders by frame height (`1920p30`), and exposes current encoder controls.

## Skills used and provenance

Installed-skill discovery used:

```sh
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "manim video animation rendering ffmpeg narration captions sound design"
```

The installed index returned no Manim-specific skill. Broader searches found `remotion` but no relevant installed Manim workflow. Community research identified maintained Manim agent skills; the frame-review skill was selected because it directly supports the benchmark's mandatory render-to-PNG-frame review loop.

### manim-frame-review

- **Source:** `https://github.com/DominikPeters/manim-skill`
- **Repository path:** `manim-skill/`
- **Commit:** `f27ced8f8bb010131e96593c0cba20b5ab6e01ed`
- **Repository version:** 1.0.20 (commit `chore: bump version to 1.0.20`, 2026-10-04)
- **License:** MIT
- **Installed path:** `skills/manim-frame-review/`
- **Skill metadata name:** `manim-skill`
- **SKILL.md SHA-256:** `58ad771f16f0b1a427e5eb3554ffb635f7438fddfe487aeb42ed48339b323f50`
- **Installed with:** `/Users/rajeev/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py`, pinned to the commit above and redirected into this experiment.

Used for the frame-review methodology: inspect an overview first, inspect full-size key frames, and iterate from actual rendered output. The final benchmark-specific implementation additionally inspected encoded MP4 frames and mobile-scale ending frames.

### skill-installer

- **Path:** `/Users/rajeev/.codex/skills/.system/skill-installer/SKILL.md`
- **Role:** installed the pinned community skill into the assigned directory without changing global skill state.

No other skill was used in production or review. Exact lock data is in `skills-lock.json`.

## Local TTS and audio

Narration was generated locally with the already-installed Kokoro 82M q8 ONNX setup:

- model cache: `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- quantized model SHA-256: `fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478`
- voice: `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`
- voice SHA-256: `669fe0647f9dd04fcab92f1439a40eeb4c8b4ab1f82e4996fe3d918ce4a63b73`
- mode: `dtype: q8`, `device: cpu`, `local_files_only: true`

`scripts/narrate.cjs` resolves the local `kokoro-js` package and fails if its built-in voice resolver does not point to the exact requested `bf_emma.bin` file. Five original lines were generated at 24 kHz, energy-trimmed with short breathing margins, and placed by exact sample count. The resulting measured speech timeline is 18.945 s; `src/timing.json` and `assets/captions.srt` are derived from those samples rather than estimated word timings.

`scripts/soundscape.py` synthesizes an original restrained A-minor bed plus location-panned glass tones, transition air moves and a low final resolve with NumPy. `scripts/deliver.py` applies voice EQ/compression, mixes dialogue above effects, limits peaks and targets approximately -16 LUFS. The delivered MP4 audio was played in full with `/usr/bin/afplay`; the waveform showed five clear phrases and measured silence only in the final 0.86 s tail.

## Full-render inspection and refinement

The required complete render -> inspect -> refine -> re-render loop was run repeatedly because the first visual pass exposed real failures.

### First complete full render

- Full 1080 x 1920 Manim render completed in **15.38 s**.
- The first encoded cut had correct captions, timing and audio, but all explanatory scene layers were invisible.
- Full-size opening/middle/transition/ending frames and the contact sheet confirmed this was not a contact-sheet-only issue.
- Root cause: `FadeIn`/`Create` inherited target mobjects whose opacity had already been flattened to zero, so their end states were also zero.
- Audio inspection found five distinct narration phrases, clean gaps, -16.0 LUFS integrated loudness and no clipping.

### Substantive creative refinement

Exact changes made:

1. Rebuilt animation target handling so Manim interpolates from invisible to the intended styled objects instead of to zero-opacity copies.
2. Added a shaded **RELATED WORDS** neighbourhood around puppy/dog/kitten so the spatial analogy reads before the distance scene.
3. Rebalanced pin label sides and replaced a generic distance sentence with explicit **NEAR = SIMILAR** and **FAR = DIFFERENT** comparison badges.
4. Fit the coordinate numerals inside their card. The final `5.02s` audit proves the values are fully visible rather than clipped.
5. Rebuilt the small coordinate-map target so its grid, label and point stay inside one panel.
6. Increased the hierarchy of the map: close/far line weights, colour semantics, a common spatial field and animated landing order.
7. Removed the ending's secondary **language becomes spatial** phrase.
8. Made the ending spatial-only: map and pin labels fade away, the diagram retreats/dims, and the **RELATIONSHIPS YOU CAN MEASURE** headline and near/related equation dominate before 16.60 s.
9. Redesigned contact-sheet labels and panel dimensions to prevent text collisions.
10. Separated the 0.18/0.47/1.62 distance badges from the pin labels and faded the related-words annotation when the measurement layer appears.

Post-refinement full renders took **19.95 s**, **14.99 s**, **13.36 s**, and the retained final render took **16.35 s** (some unchanged segments were cached). The complete retained build, including local TTS, soundscape, render, delivery, verification and audit exports, took **27.30 s** wall time.

### Final mobile-scale review

- `audit/coordinates-5.02-mobile.jpg`: all coordinate numerals fit; the arrow and map target form a clear word -> numbers -> address sequence.
- `audit/ending-16.60-mobile.jpg`, `audit/ending-17.55-mobile.jpg`, `audit/ending-18.35-mobile.jpg`: the final headline and diagram remain dominant across the last 3.2 seconds.
- `audit/ending-mobile-audit.jpg`: retained three-frame comparison strip.
- `deliverables/contact-sheet.jpg`: all five major scenes represented from the delivered master.

The independent ending review was addressed directly: the secondary phrase is gone, background labels are removed, and the headline/diagram hierarchy is established by 16.60 s.

## Final media verification

Verification evidence: `audit/final-verification.json`; render log: `audit/render-final.log`.

| File | Result |
|---|---|
| `deliverables/final.mp4` | 1080 x 1920, H.264, yuv420p, 30/1 fps, 593 decoded frames, stereo AAC 48 kHz, 19.764388 s container duration |
| `deliverables/preview.mp4` | 540 x 960, H.264, yuv420p, 30/1 fps, 593 decoded frames, stereo AAC 48 kHz, 19.766667 s |
| `deliverables/contact-sheet.jpg` | Valid JPEG, 275,916 bytes, five major scene panels |

Both MP4s passed full FFmpeg decode with `-xerror` and explicit video/audio stream mapping. Audio measured approximately **-16.0 LUFS integrated**, **1.3 LU LRA**, and **-3.9 dBTP** on the master (preview peak -3.3 dBTP after re-encode). The speech timeline is 18.945 s and inside the required 15-25 s range; the MP4 container includes normal AAC/MOV padding.

Delivered hashes:

```text
53f78199793c6c0feb57c2e154759be990eb5b635997361c505f9be5ee908d1a  final.mp4
4b4fe7188f3f3b48b37ac9d9b937d701a405e849d95a8aab381285bd1793f2cc  preview.mp4
3aaca2350a9704bee9e2b4d523a41dca91a17cf41cec4c540bd6994e1a941f6f  contact-sheet.jpg
```

## Known limitations

- The narration is synthetic British English (Kokoro `bf_emma`) and is more even than a directed human performance.
- The meaning map is a two-dimensional teaching projection. The displayed coordinates and distances are illustrative, not outputs from a named embedding model.
- Embeddings can use many dimensions and model-specific similarity functions; the film intentionally teaches the spatial intuition only.
- The typography uses macOS system fonts (Avenir Next and Menlo), so a non-macOS rerender needs equivalent installed fonts.
- No live side-by-side audience study against the Remotion baseline was run; the comparison is based on the brief's clarity/polish standard and actual full-render inspection.

## Retention

No model weights, TTS caches, Node modules, Python environments, Manim segment caches or temporary extracted review frames are retained. The editable scene, scripts, source audio, captions, pinned skill, final media and focused audit evidence remain inside this experiment directory.
