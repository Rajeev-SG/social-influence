# Recommendations

## Strongest standalone engines

1. **Motion Canvas** — best default for premium kinetic typography and
   diagram-led explainers. It offered the strongest hierarchy, easing and
   authoring-to-render reliability.
2. **Revideo** — best speed/quality balance. It handled complex animated
   explanations and produced the shortest reliable full render in the benchmark.
3. **Manim** — best for mathematics, geometry, spatial relationships and
   scientific explanation. It is less cinematic by default but extremely
   effective when the subject benefits from measured diagrams.

## Strongest visual/compositing libraries

- **Three.js** for genuine depth, camera movement and physical-looking network
  or spatial systems.
- **PixiJS** for fast 2D scene graphs, data flows, interface-like diagrams and
  high-volume animated objects.
- **Lottie-web** when motion should be authored once as a reusable JSON asset
  and replayed consistently across tools or products.
- **Theatre.js** when designers need editable keyframe tracks and an
  animation-state object rather than code-only timing.

## Strongest production combinations

- **Motion Canvas or Revideo + Kokoro + procedural sound + FFmpeg** is the best
  general short-form explainer stack: strong visuals, precise timing and simple
  delivery.
- **Three.js or PixiJS + deterministic Playwright capture + FFmpeg** is the best
  route for bespoke visual systems that exceed timeline-template constraints.
- **Canvas + Mediabunny/WebCodecs** is the best route when exact H.264/AAC
  encoding, pixel format and MP4 muxing must be owned by the application.
- **Theatre.js + browser capture** fits design-led teams that want editable
  keyframes and object tracks; budget extra render time.
- **Manim + FFmpeg** remains the strongest specialist combination for
  mathematical and scientific explainers.

## Practical selection guide

- Need the best-looking general social explainer: **Motion Canvas**.
- Need the fastest high-quality iteration loop: **Revideo**.
- Need diagrams, geometry or equations: **Manim**.
- Need depth and physical spatial motion: **Three.js**.
- Need dense animated data/interface motion: **PixiJS**.
- Need reusable animation assets: **Lottie-web**.
- Need direct control of encoding/muxing: **Mediabunny**.
- Need rapid editorial assembly: **Editly** or **FFCreator**.
- Need graph/pipeline-shaped production infrastructure: **VideoFlow**, accepting
  higher setup complexity.

## Overall recommendation

For future agent-produced explainers, use **Motion Canvas or Revideo as the
primary authoring renderer**, Three.js/PixiJS/Lottie-web as targeted visual
layers, local Kokoro for narration, procedural sound design, and FFmpeg for
review derivatives and objective media QA. Keep Mediabunny in the stack when
the product needs first-class control over WebCodecs encoding and MP4 muxing.
