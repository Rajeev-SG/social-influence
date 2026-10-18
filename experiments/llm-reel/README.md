# The Next Token

A finished, standalone Remotion experiment: **how language models work**, in approximately 51 seconds. 1080 × 1920, 30 fps, H.264/AAC. No connection to the repository's publishing/content pipeline.

## Watch

- [Finished master](deliverables/final.mp4)
- [540 × 960 review copy](deliverables/preview.mp4)
- [Contact sheet](deliverables/contact-sheet.jpg)
- [Narration and timecoded storyboard](STORYBOARD.md)
- [Creative review and verification](CREATIVE-QA.md)

## Preview / rerender

Requires Node 22.13+ (or another version supported by the pinned Remotion release), FFmpeg, Python 3 and Pillow.

```sh
cd experiments/llm-reel/app
npm ci
npm run dev
# Choose TheNextToken in Remotion Studio.
npm run check
npm run render
```

The render command makes a full-resolution PNG-frame-based master, finishes the mix to a −16 LUFS target, and creates the preview and contact sheet. Outputs go to `deliverables/`; the intermediate is ignored under `.review/`. There are no remote media dependencies at render time. Remotion may acquire its supported headless browser on first use.

## Edit

- `app/src/scenes.tsx`: ten independently authored sequences and their motion choreography.
- `app/src/Network.tsx`: deterministic 3D projected lattice with particles travelling its edges.
- `app/src/design.tsx`: typography, geometry, colour, easing and reusable token primitives.
- `app/src/Film.tsx`: sequence timing, masked handoffs, captions and audio.
- `script.json`: narration text. `app/src/timing.json`: measured, sample-derived cue times.
- `scripts/soundscape.py`: original stereo ambient score, interaction ticks, air transfers and closing resolve.

All motion comes from Remotion's current frame. No CSS animations, stock footage, pre-rendered diagram images, or AI-image pans.

### Narration, without downloading models

The included finished narration is sufficient to rerender. It is **AI-generated speech**, synthesised locally with the existing **Kokoro 82M q8 ONNX** cache and **bf_emma** British voice. George, Emma and Fable were actually sampled; a multimodal listening comparison preferred Emma for naturalness and diction. Qwen3-TTS/Chatterbox weights were not present in the inspected caches/model directories; installed MLX audio code alone did not provide a usable voice model. No new TTS weights or redundant Python environment were downloaded.

To regenerate speech on this machine, from the experiment root:

```sh
node scripts/narrate.cjs
# Existing installation; set KOKORO_PACKAGE to another package.json that resolves
# kokoro-js and @huggingface/transformers if using a different machine.
ffmpeg -y -i app/public/audio/narration-raw.wav \
  -af 'highpass=f=75,lowpass=f=11000,acompressor=threshold=0.12:ratio=2:attack=15:release=180:makeup=1.2,loudnorm=I=-17:TP=-2:LRA=8' \
  -ar 48000 app/public/audio/narration.wav
/Users/rajeev/Code/mlx-vlm/.venv/bin/python scripts/soundscape.py
```

The last command reuses an existing NumPy environment; any Python with NumPy works. Speech generation is explicitly `local_files_only`. Each utterance is energy-trimmed with breathing margins, placed on the timeline by exact sample count, and captioned for its full measured duration. Captions are sentence-level, not unverified word-level karaoke. Regenerating narration changes timing; update the storyboard if changing the script.

## Design and factual scope

Charcoal/navy, warm white, luminous mint, blue and sparse violet. Amber is reserved for uncertainty. Manrope for editorial type; IBM Plex Mono for technical annotations. Strong mobile-scale type, restrained surface depth, and geometry which carries the explanation.

The film explains the **core text-generation mechanism**, not every capability of the ChatGPT product. Real products can also retrieve sources, use tools, and retain conversation context. Tokens can be words, word fragments, punctuation or other text pieces; the simple sentence happens to illustrate word-sized pieces. Token IDs use a cl100k-base example, not a claim about ChatGPT's current tokenizer. Probability values and the false Moon statement are explicitly illustrative. Sampling is not necessarily choosing the largest probability. Diagrams compress the many heads, layers and transformations of a real transformer. Fixed weights during ordinary inference do not mean the conversation context cannot change.

### Sources / references

- [Official Remotion skills](https://github.com/remotion-dev/skills), installed locally with the requested skills CLI; creation, markup/animation, audio, captions and rendering guidance consulted.
- [Remotion render reference](https://www.remotion.dev/docs/cli/render).
- [3Blue1Brown: attention in transformers](https://www.3blue1brown.com/lessons/attention): explanatory reference, particularly contextual relationships and layered processing. No imagery copied into the film.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762).
- [Kokoro voice documentation](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

Manrope and IBM Plex Mono are SIL OFL licensed; notices accompany the font files. Kokoro weights/implementation are Apache-2.0; weights are not distributed here. The music and effects are original procedural synthesis. Remotion's own commercial-use terms still apply to use of Remotion. The included paid multimodal-review helper is optional and requires an existing `OPENROUTER_API_KEY`; it is not involved in rendering or TTS.
