# QA Report

## Verified Output

- `final.mp4`: 1080×1920, H.264, 30fps, AAC stereo 48kHz, 88.875 seconds.
- `preview.mp4`: 720×1280 H.264 review copy.
- Audio: non-silent, mean -18.8 dB and peak -4.2 dB. The pre-encode mix measured
  approximately -15.1 LUFS integrated after narration/score ducking.
- HyperFrames `check`: runtime, layout, motion and 85/85 contrast checks passed.
  Remaining lint warnings describe the intentional root composition used to share the
  deterministic Three.js timeline.
- OCR spot checks confirmed the opening title, ranking shares, comparison labels,
  methodology warning and closing takeaway.

## Visual Refinement Passes

1. **Blender camera/identity pass:** replaced mirrored static labels with camera-tracked
   text, reduced oversized nodes, pulled the camera back, and changed to a neutral view
   transform. Opening and finale were rerendered from all 450 Blender frames.
2. **Final typography/readability pass:** replaced non-rendering Diffusion Studio text
   and image overlays with validated solid Manrope title/closing cards, then rerendered
   the finishing composite. OCR then detected the complete opening and closing copy.

## Deliberate Dark Regions

Automated `blackdetect` reports:

- 0.567–5.267s: solid title card. Text is present and OCR-verified.
- 7.000–7.167s: intentional fade-to-black transition.
- 81.167–86.667s: solid closing card. Text is present and OCR-verified.

These are not dropped frames or empty scenes.

## Engine Evaluation

| Engine | Actual contribution | Verified limitation |
| --- | --- | --- |
| HyperFrames | Primary 73.8s motion system; full check and render | Root-composition lint warnings retained for shared WebGL timeline |
| Three.js | Procedural constellation and camera drift inside HyperFrames | Must be deterministic and seek-safe |
| Blender 5.2.2 | Editable 3D scene, camera, lighting, 450 rendered frames | Homebrew build outputs PNG frames; FFmpeg performs video encode |
| Diffusion Studio 4.0.3 | Clip assembly, transitions, effects, audio, WebCodecs master | Adds license watermark; text/image overlay clips were not visible in exported frames |
| Kokoro | Local timestamped British narration | Existing cached model only; no Qwen3-TTS/Chatterbox weights were present |
| FFmpeg | Encoding, score mixing, loudness, preview and final type composite | Finishing pass needed because Diffusion Studio overlays failed |

## Unresolved Weaknesses

- Diffusion Studio’s free-tier watermark remains visible in the top-left.
- Blender labels intentionally enter and leave frame during the close opening move.
- Website traffic understates embedded Copilot and Meta AI usage; this is stated in the
  video and source notes instead of mixing incompatible metrics.
