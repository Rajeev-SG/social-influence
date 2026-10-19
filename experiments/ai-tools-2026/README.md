# The Most Used AI Tools of 2026

Finished 1080×1920, 30fps Instagram Reel comparing ChatGPT, Gemini, Claude,
DeepSeek, Grok, Microsoft Copilot and Perplexity by one consistent metric:
worldwide AI-assistant website-visit share in September 2026. Meta AI is handled
separately because its primary distribution is embedded inside Meta apps.

## Deliverables

- `deliverables/final.mp4` — 88.875-second finished Reel.
- `deliverables/preview.mp4` — 720×1280 compressed review copy.
- `deliverables/contact-sheet.jpg` — representative frames.
- `review/index.html` — browser-viewable review gallery.
- `narration/` — script, measured cue timing and original narration WAV.
- `sources/` — ranking, product and toolchain evidence.
- `qa/QA.md` — verification, refinement passes, limitations and engine results.

## Production Stack

- **HyperFrames 0.8.176:** primary comparative motion system, kinetic typography,
  animated ranking bars and split-screen product sequences. The 73.8-second middle
  render used four workers and hardware WebGL/Metal.
- **Three.js:** deterministic real-time particle/ring constellation behind the
  HyperFrames timeline.
- **Blender 5.2.2 LTS:** editable scripted 3D scene with camera tracking, emissive
  materials and actual 1080×1920 frames for the seven-second opening and eight-second
  finale.
- **Diffusion Studio Core 4.0.3:** browser/WebCodecs assembly of the Blender and
  HyperFrames clips, dissolve/fade transitions, contrast/saturation treatment, audio
  layer and final MP4 encode.
- **Kokoro 82M q8 ONNX:** local British `bf_emma` narration with measured cue timing.
- **FFmpeg 9.0.2:** Blender frame encoding, original score mixing, -14 LUFS mastering,
  preview generation and the final solid typography-card composite.

Diffusion Studio Core adds its required “Made with Diffusion Studio” watermark because
no commercial license key was available. Its `TextClip` and `ImageClip` overlays did
not appear in the actual renderer, so the validated Manrope title/closing cards are
composited in the final FFmpeg finishing pass. Diffusion Studio still produced the
video assembly, transitions, effects, audio mux and WebCodecs master.

## Rebuild

```bash
node scripts/generate-narration.cjs
bash scripts/mix-audio.sh
blender --background --python src/blender/build_scene.py -- --build
bash scripts/blender-to-video.sh
npx --yes hyperframes@0.8.176 check src/hyperframes
npm run render:middle
bash scripts/build-title-plates.sh
npm run render:diffusion
bash scripts/finish-with-type.sh
```

The existing repository experiments and their uncommitted work were not changed.
