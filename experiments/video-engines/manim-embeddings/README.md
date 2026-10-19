# What Are Embeddings?

A complete 19.8-second vertical Manim film explaining embeddings with one simple analogy: a meaning map where related words sit close together.

## Watch

- [Final 1080 x 1920 master](deliverables/final.mp4)
- [540 x 960 review copy](deliverables/preview.mp4)
- [Contact sheet](deliverables/contact-sheet.jpg)
- [Mobile-scale ending audit](audit/ending-mobile-audit.jpg)
- [Production evidence](REPORT.md)

The final master is H.264/yuv420p at 30 fps with stereo 48 kHz AAC. The preview is a smaller, quick-review re-encode. The contact sheet contains one representative frame from each of the five major scenes.

## Production

Manim Community 0.22.0 is the primary production technology. `src/embeddings_scene.py` constructs every visual element, transition, spatial relationship and burned-in caption as animated Manim mobjects. FFmpeg is used only to normalize/mix audio, mux the Manim picture, make the review copy, extract audit frames and verify the encoded files.

The story moves through five beats:

1. Words do not arrive with built-in meanings.
2. An embedding gives a word numerical coordinates.
3. Related words land in one neighbourhood on a meaning map.
4. Distance becomes a measurable proxy for similarity.
5. Embeddings turn language into relationships.

## Rebuild

Prerequisites:

- macOS with FFmpeg 9.x, Node 22+ and `uv`
- Python 3.13 (selected automatically by the build script)
- the existing local Kokoro 82M q8 ONNX installation used by `content-machine`

Run the complete build from this directory:

```sh
./scripts/build.sh final
```

The build generates local narration, synthesizes the soundscape, renders the Manim scene at 1080 x 1920/30, mixes and encodes the deliverables, runs decode/spec/loudness checks, and refreshes the retained mobile audit frames. Manim's transient media directory is `.work/`; it is not part of the delivered tree.

To regenerate only the speech and measured cue data:

```sh
node scripts/narrate.cjs
```

`scripts/narrate.cjs` resolves the already-installed `kokoro-js` package and verifies that it uses the requested voice file:

```text
/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin
```

The model call is `local_files_only: true`; no TTS weights or model caches are downloaded or stored here.

## Files

- `src/embeddings_scene.py`: complete Manim scene and motion choreography.
- `src/timing.json`: measured narration/caption timing.
- `assets/script.json`: original narration script.
- `assets/captions.srt`: sentence-level captions.
- `assets/audio/`: generated voice, procedural sound design and final mix.
- `scripts/build.sh`: full render/delivery pipeline.
- `scripts/narrate.cjs`: local Kokoro narration and cue measurement.
- `scripts/soundscape.py`: original NumPy score and synchronized effects.
- `scripts/deliver.py`: mix, master/preview encoding and contact sheet.
- `scripts/verify.py`: FFmpeg decode and FFprobe/EBU R128 checks.
- `scripts/audit_frames.sh`: retained mobile-scale inspection frames.
- `skills/manim-frame-review/`: pinned Manim frame-review skill.
- `audit/`: retained render log, verification JSON and review frames.
- `REPORT.md`: research, provenance, render loop and final evidence.

## Skill provenance

The frame-review workflow is vendored from `DominikPeters/manim-skill` at commit `f27ced8f8bb010131e96593c0cba20b5ab6e01ed` (MIT, repository version 1.0.20). The installed `SKILL.md` SHA-256 is `58ad771f16f0b1a427e5eb3554ffb635f7438fddfe487aeb42ed48339b323f50`; full lock metadata is in `skills-lock.json`.

## Scope

The coordinates and distances are deliberately illustrative. The film teaches the spatial intuition behind embeddings, not a specific model, index, training method or production retrieval system.
