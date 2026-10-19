# Engine Evaluation Evidence

- HyperFrames render: 2,214 frames, 73.8s, four workers, hardware browser GPU, 56.9s
  total render time.
- Blender 5.2.2 LTS: 450 actual 1080×1920 PNG frames rendered from
  `src/blender/ai-tools-2026.blend`; opening and finale encoded at 30fps.
- Diffusion Studio Core 4.0.3: `Composition`, sequential `VideoClip`s, transition
  configs, effect arrays, `AudioClip`, and `Encoder` with AVC/AAC output. The exported
  master is retained at `assets/diffusion/diffusion-master.mp4`.
- Diffusion Studio overlay evidence: `TextClip` and `ImageClip` content was absent in
  exported frames despite valid sources and layer insertion. The project therefore
  documents the substitution instead of crediting those overlays to Diffusion Studio.
- Final typography evidence: `scripts/finish-with-type.sh` uses validated Manrope PNG
  plates. OCR at 1.0s and 81.2s reads the required opening and closing messages.
