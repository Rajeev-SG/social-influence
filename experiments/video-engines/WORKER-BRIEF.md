# Video Engine Benchmark Worker Brief

Create one complete 15-25 second educational video in this repository. Work only
inside the assigned `technology-topic/` directory and do not edit sibling
experiments or shared benchmark files.

## Required output

```text
technology-topic/
  src/                  editable source
  scripts/              build, render and inspection scripts
  assets/               necessary local assets, excluding model weights/caches
  deliverables/
    final.mp4
    preview.mp4
    contact-sheet.jpg
  REPORT.md
  README.md
```

The final MP4 must be 1080x1920, 30 fps, H.264, yuv420p, 15-25 seconds, with
stereo AAC audio. `preview.mp4` must be smaller and quick to review. The contact
sheet must show representative frames from every major scene.

## Creative standard

- Beat the existing Remotion baseline in `../llm-reel/` for clarity and visual
  polish, while keeping this video simpler and more digestible than a dense
  technical lecture.
- Use one clear beginner-friendly analogy and one visual through-line.
- Make the visuals explain the idea rather than decorate it.
- Use bespoke kinetic typography, animated diagrams/data, cinematic depth,
  precise easing, deliberate transitions and readable mobile typography.
- Do not use static-image pans, generic slideshows, repetitive paragraph cards,
  decorative particle noise, or stock AI-brain imagery.
- Give the assigned technology a substantive role. If it is not a standalone
  renderer, build the smallest compatible capture/encoding workflow and prove
  how the technology produces the video.

## Narration and sound

- Write an original, natural, accurate beginner script before implementation.
- Use the already-installed Kokoro 82M q8 ONNX setup:
  - model cache:
    `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
  - voice:
    `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`
- Do not download TTS weights or create redundant environments.
- If TTS fails, document the exact failure and use the strongest lightweight
  local fallback without hiding the compromise.
- Synchronise captions and key visual events to narration.
- Use restrained, purposeful sound design. Synthesise effects when possible or
  use clearly licensed assets. Mix narration consistently and clearly.

## Research and skills

- Discover installed skills with
  `python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "<intent>"`.
- Search for maintained official/community skills for the assigned technology.
- Read current official documentation, examples and rendering guidance.
- Record every skill used in `REPORT.md`. Never invent a skill or use stale APIs.

## Mandatory review loop

1. Implement and render a complete video.
2. Inspect the actual MP4 and extracted frames, including opening, middle,
   transitions and ending.
3. Listen to the narration/audio and verify synchronisation.
4. Identify concrete creative, explanatory and technical weaknesses.
5. Make at least one substantive creative improvement pass.
6. Re-render and verify the final files.

Run only checks that can genuinely catch failures. Prove with FFmpeg or the
chosen tooling that the final video decodes, has the correct dimensions, frame
rate and duration, and contains audio.

## Report evidence

`REPORT.md` must include:

- topic and one-sentence teaching goal;
- technology and exact version;
- role the technology plays in rendering;
- skills used and where they came from;
- local TTS/audio approach;
- render command and measured render time;
- full-render inspection findings;
- exact changes made during creative refinement;
- final media verification results;
- known limitations.

Do not commit or retain model weights, caches, node_modules, temporary render
frames, or unrelated generated files. Do not make a Git commit; the orchestrator
will review and commit the complete benchmark.
