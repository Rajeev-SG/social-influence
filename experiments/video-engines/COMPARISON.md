# Programmatic Video Engine Comparison

## Method

Each technology produced one complete 15–25 second 1080 x 1920 educational
video. Every project used the installed Kokoro 82M q8 `bf_emma` narration,
original synthesized sound design, measured cue timing and a mandatory
full-render → frame/audio inspection → creative refinement → re-render loop.

The ranking prioritises visual fidelity and motion sophistication, then
explanatory clarity, typography, synchronisation, output reliability and
development friction. Render time is evidence, not the primary quality score.

## Ranked results

| Rank | Technology | Topic | Visual / motion result | Measured render evidence | Skill and provenance |
|---:|---|---|---|---|---|
| 1 | Motion Canvas | Tokens | Best overall kinetic typography, hierarchy and transition control. | 40.26s native export + 3.00s delivery. | VideoZero skills commit `670ff96…`; Motion Canvas 3.17.2 docs. |
| 2 | Revideo | Next-token prediction | Excellent generator-scene animation with strong probability storytelling. | 11s refined four-range render + concat. | `revideo-video` skill; Revideo 0.11.0. |
| 3 | Three.js | Neural network | Strongest depth, perspective and signal-flow visualisation. | 82.540s final render. | `speech` + `playwright`; Three.js 0.180.0 docs. |
| 4 | PixiJS | Agent tools | Fast, crisp WebGL diagrams and animated action/result packets. | 68.265s final capture + 3.10s packaging. | Official PixiJS skills commit `df555b8…`. |
| 5 | Manim | Embeddings | Best mathematical/geospatial explanation and measured-distance clarity. | 16.35s render; 27.30s full pipeline. | `DominikPeters/manim-skill` commit `f27ced8…`; Manim 0.22.0. |
| 6 | Mediabunny | Multimodal AI | Strong convergence storytelling with the most controlled encode/mux path. | 24.51s refined render. | `official-first-docs`, `web-search`, `compare-screenshots`, Remotion skills; Mediabunny 1.56.1. |
| 7 | Lottie-web | Hallucination | Reusable, consistent motion system with clear plausible-versus-true contrast. | 36.337s capture + 3.108s encode. | Lottie-web 5.13.0 package/schema; no matching installed skill. |
| 8 | MotionForge | Temperature | Strong kinetic type and branching choice paths; some package/export friction. | 130.114s refined render. | `speech`; MotionForge 1.4.0. |
| 9 | Theatre.js | RAG | Strong editable keyframe timeline and pipeline storytelling; slow browser capture. | 142.935s refined render + 0.682s packaging. | No Theatre.js skill; `transcribe` consulted; Theatre core 0.7.2. |
| 10 | Movis | Learning from mistakes | Good custom-layer animation and feedback-loop explanation. | 56.701s refined render. | `kajisho5/ffmpeg-skill` v2.10.4; Movis 0.7.1. |
| 11 | Editly | Context window | Reliable editorial transitions and desk/capacity metaphor. | 43.57s final render. | `6missedcalls/video-editing-skill` commit `7dc6e1d…`; Editly 0.15.0-rc.1. |
| 12 | FFCreator | Fine-tuning | Fast, competent scene composition; less bespoke motion depth. | 5.34s final render. | `speech`, `worker-context-discipline`, `web-search`, `transcribe`; FFCreator 7.5.8. |
| 13 | Rendiv | Attention | Clear React frame model and relationship graphics; screenshot capture dominated runtime. | 151.487s render. | `rendiv-video` commit `6d6aca2…`; Rendiv 0.2.6. |
| 14 | VideoFlow | Training vs inference | Distinct DAG-based production and solid recipe analogy; more infrastructure for similar visual output. | 106.395s DAG render + 1.936s encode. | No matching skill; VideoFlow 1.0.4 + NATS 2.12.15. |

## Evidence notes

- All 14 masters are H.264 `yuv420p`, 1080 x 1920, 30 fps with stereo 48 kHz
  AAC and pass full FFmpeg decode.
- Durations range from 19.29s to 24.78s, within the required 15–25s window.
- Individual `REPORT.md` files contain exact versions, skill sources, render
  commands, measured timings, first-cut findings, refinement changes and media
  verification.
- The shared gallery links every master, preview, contact sheet and report.

## Output reliability findings

- Motion Canvas and Revideo produced the cleanest authoring-to-render loop.
- FFCreator was the fastest encoder but required more manual art direction to
  reach the same visual level.
- Rendiv and Theatre.js produced capable timelines but were slowed by browser
  screenshot capture.
- VideoFlow proved that graph runtimes can render video reliably, but the
  infrastructure cost exceeded the visual benefit for this short-form format.
- Three.js and PixiJS delivered the strongest bespoke visual systems after
  deterministic frame capture was added.
- Mediabunny offered the most explicit control over pixel format, codecs and
  muxing, at the cost of a more complex WebCodecs pipeline.
