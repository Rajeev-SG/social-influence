# A Cup of Context

A second, **simpler** explanation of how ChatGPT writes. A separate Hyperframes experiment; the original Remotion film remains unchanged.

**45 seconds · 1080 × 1920 · 30 fps · narrated British English**

## Watch

- [Finished video](deliverables/final.mp4)
- [Smaller preview](deliverables/preview.mp4)
- [Contact sheet](deliverables/contact-sheet.jpg)
- [Script and storyboard](STORYBOARD.md)
- [Creative QA](CREATIVE-QA.md)

## What changed creatively

One familiar example—“I'd love a cup of…”—carries the explanation. A warm, illustrated teacup replaces the technical network aesthetic. There are no token IDs, percentages, neural lattices or layered dashboards. Six calm beats explain patterns learned earlier, choosing the next text piece, repeating, useful results, and the need to check facts.

## Preview, edit, render

Requires Node 22+, FFmpeg, Python 3 and Pillow. All visual and audio assets are local. The pinned Hyperframes CLI may install its browser/runtime dependencies on first use.

```sh
cd experiments/llm-hyperframes/film
npm ci
npm run dev
npm run check
npm run render
```

`render` makes a Hyperframes delivery-quality master, targets −16 LUFS for the mix, and exports the smaller preview and contact sheet. Intermediates and framework caches are ignored.

- `film/index.html`: six scene clips, shared cup illustration, captions, audio and compiled timeline.
- `film/style.css`: warm editorial palette, serif typography and mobile layout.
- `film/motion.js`: the editable, paused GSAP timeline. After editing it, run `npm run sync` to embed it into the HTML; the inline registration is required by Hyperframes' static lint.
- `script.json` / `timing.json`: spoken words and exact, sample-derived sentence timings.
- `scripts/sync-timing.py`: updates the HTML's captions, scene windows, duration and embedded timeline.
- `scripts/narrate.cjs`: offline speech using the already-cached Kokoro model and `bf_emma`. Set `KOKORO_PACKAGE` to the path of a package.json which resolves your existing `kokoro-js` installation if needed. No model download.
- `scripts/sound.py`: original sparse chord and tactile-tap synthesis. Uses any existing Python environment with NumPy.

The voice is **AI-generated**. To regenerate it, run `node scripts/narrate.cjs` from the experiment root, normalise `.review/narration-raw.wav` into `film/assets/narration.wav`, regenerate the sound track, then run `npm run sync`. Changing spoken timing may require adjusting the few illustrative beat offsets in `motion.js`.

### Hyperframes skills and provenance

Installed the official `heygen-com/hyperframes` router, faceless-explainer and relevant core, animation, keyframe, creative, audio, registry and CLI skills. Used the `editorial-forest` frame preset, with Manrope substituted for small captions to improve mobile reading and reduced chrome to lower cognitive load. The word-rise entrance adapts the installed `text-stagger` registry component; its original source is retained under `film/compositions/components/`.

Hyperframes Studio allows direct timeline/text/design editing. Its **Edit with Framey** button can open the [HyperFrames desktop app](https://hyperframes.dev/studio/download) for chat-based editing; it is optional, not a render dependency.

### Scope and licences

“Advanced sentence completer” is a beginner-friendly analogy for autoregressive text generation, not a claim that the full ChatGPT product only finishes sentences. The film intentionally omits attention mathematics, tokenisation details, retrieval and tools. Small text pieces are not always entire words. Training examples and continuations are illustrations, not measured output from a live model.

Source Serif 4 and Manrope are SIL OFL licensed; notices accompany the fonts. The cup and bicycle are original SVG artwork; music/effects are original synthesis. GSAP 3.14.2 uses its [standard no-charge licence](https://gsap.com/standard-license); its distributed header is preserved. Hyperframes is Apache-2.0. Kokoro model weights are not distributed. Optional multimodal review uses an existing OpenRouter key; rendering and narration do not require cloud credentials.
