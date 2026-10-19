# VideoFlow: Training versus inference

A 22.533-second beginner explainer that compares model training with inference
through one analogy: a chef tastes many dishes to learn one recipe, then uses
that fixed recipe on a new dish.

## Deliverables

- `deliverables/final.mp4` - 1080x1920, 30 fps, H.264 `yuv420p`, stereo AAC.
- `deliverables/preview.mp4` - 540x960 quick-review copy.
- `deliverables/contact-sheet.jpg` - extracted frames covering every scene.
- `src/` - editable narration, timing, VideoFlow graph, and visual renderer.
- `scripts/` - setup, local Kokoro synthesis, render, inspection, and verify.
- `assets/` - generated narration, timing, and original synthesized effects.
- `REPORT.md` - provenance, render timings, review loop, and QA evidence.

## Technology

The frame pipeline is a real VideoFlow 1.0.4 batch DAG:

```text
FrameProducer
  -> TimingProcessor
  -> FrameRendererProcessor
  -> FrameManifestConsumer
```

Each node runs in a VideoFlow worker over NATS JetStream. VideoFlow writes the
676 scene frames; FFmpeg performs final H.264/AAC muxing and preview encoding.

## Requirements

- Python 3.12+ (built with 3.14.7)
- Docker (built with 29.4.0)
- Node 22 at `/opt/homebrew/opt/node@22/bin/node`
- FFmpeg/FFprobe (built with 9.0.2)
- Existing local Kokoro q8 model cache and `bf_emma` voice from `content-machine`

No TTS weights are copied or downloaded by this project.

## Build

```bash
./scripts/setup.sh
./scripts/generate_audio.sh
./scripts/render.sh
./scripts/inspect_media.sh
./scripts/verify.sh
```

`generate_audio.sh` synthesizes each narration line with local Kokoro, records
measured line timings, creates original sound cues, and mixes exact-duration
stereo audio. `render.sh` starts a temporary NATS 2.12 container, runs the
VideoFlow graph, encodes the final and preview MP4s, then removes the container.

## Editable content

- `src/project.json` - narration copy, voice, speed, and pacing.
- `src/render_flow.py` - VideoFlow graph factory.
- `src/render_nodes.py` - producer, processors, and manifest consumer.
- `src/render_visuals.py` - five-scene visual system and caption rendering.
- `assets/audio/timing.json` - generated speech, scene, and sound timings.

Scene timing follows measured Kokoro WAV durations, so captions and major
visual events remain synchronized when the script is regenerated.
