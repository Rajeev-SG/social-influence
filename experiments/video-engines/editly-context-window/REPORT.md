# Production Report

## Topic and teaching goal

**Editly — “What is a context window?”** explains that a model can only consider
a bounded amount of text at once. The desk analogy makes the limit concrete:
notes fill the workspace, older notes may be trimmed or summarised, and the
current context is not permanent memory.

## Technology and rendering role

- **Primary technology:** Editly 0.15.0-rc.1 with `canvas` 2.11.2.
- **Rendering role:** Editly assembles canvas-rendered animated scenes, applies
  directional transitions, mixes narration and sound, and writes the H.264/AAC
  master. The visual system is authored in `src/scenes.mjs` and `src/design.mjs`.
- **Runtime:** Node 22 was used for the final render; the retained render logs
  show 1080 x 1920 output at 30 fps.

## Skills used and provenance

`assets/skills/video-editing-skill/` is the
[6missedcalls/video-editing-skill](https://github.com/6missedcalls/video-editing-skill)
package pinned to commit `7dc6e1da66f43eff44c3692d4b84e06aef6590b6`.
`skills-lock.json` records the exact ref and content hashes. The Editly API was
also checked against the current package documentation.

## Local narration and sound

Narration uses the installed Kokoro 82M q8 ONNX cache and `bf_emma` voice:

- model cache: `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- voice: `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`

No TTS weights were downloaded. `scripts/narrate.cjs` generates the local line
audio, `scripts/build.sh` processes it to 48 kHz stereo, and
`scripts/soundscape.py` creates the restrained interface and transition bed.
The cue file is `src/timing.json`; its six measured lines run from 0.24s to
21.11s. Audio was checked by full decode, stream inspection and level analysis.
No local ASR runtime was available, so word-level transcription is not claimed.

## Render command and timing

```sh
scripts/build.sh
scripts/render.sh
```

The retained final render log is `src/.render/final-render-4.log`: **43.57s**
real time for the final master. Earlier complete render logs measure 38.93s,
41.08s and 44.41s. `scripts/deliver.py` then builds the preview and contact
sheet.

## Full-render inspection and refinement

The first-cut review artifacts are retained under `src/.render/review2/`,
including hook, desk, capacity-fill, capacity-trim, transitions, meaning, limit
and ending frames. The final source/render pass uses:

- a tighter lower caption band and smaller long captions;
- 0.32s directional transitions between the desk and capacity beats;
- separate fill and trim states so the limit is explained rather than merely
  shown;
- a cleaner meaning/limit hierarchy and a dedicated ending frame.

The source and four complete render logs show the refinement was followed by a
full re-render, not a static contact-sheet edit. The final contact sheet is
generated from the delivered master.

## Final media verification

- `final.mp4`: **23.078292s**, **1080 x 1920**, **30/1 fps**, H.264,
  yuv420p, stereo AAC at 48 kHz, 690 video frames.
- `preview.mp4`: 23.078292s, 540 x 960, 30/1 fps, H.264/yuv420p, stereo AAC.
- Both files pass full FFmpeg decode.
- Audio is decoded as stereo AAC and measured for level/absence of clipping.

## Known limitations

- The context-window metaphor is intentionally simplified; actual systems may
  use structured memory, retrieval or application-level summarisation.
- The model is described as using context now, not as having permanent memory.
- Kokoro narration is synthetic and no independent ASR model was added.
