# VideoFlow benchmark report: Training versus inference

## Teaching goal

Teach a beginner that training repeatedly learns a pattern from examples by
comparing guesses with answers and adjusting, while inference applies the fixed
learned pattern to one new input to make one prediction.

The analogy is a chef tasting many dishes to learn one recipe, then using that
fixed recipe for a new dish. The visual through-line is `MANY DISHES -> ONE
RECIPE -> NEW DISH`.

## Technology and rendering role

- Technology: VideoFlow
- Exact version: `videoflow==1.0.4` from PyPI
- Python: 3.14.7
- Runtime messaging: NATS Server 2.12.15 via `nats:2.12-alpine`
- Local worker client: `nats-py==2.16.0`
- Frame renderer: Pillow 11.3.0
- Encoder: FFmpeg 9.0.2

VideoFlow is the primary render technology. `src/render_flow.py` builds a
`Flow(..., flow_type=BATCH)` containing four named nodes:

1. `FrameProducer` emits frame indices 0-675.
2. `TimingProcessor` maps each frame to scene progress and the active caption.
3. `FrameRendererProcessor` renders a 1080x1920 Pillow frame.
4. `FrameManifestConsumer` records and sorts every frame event.

The graph ran through VideoFlow's `LocalProcessEngine` as one subprocess per
node over NATS JetStream. VideoFlow produced all 676 JPEG frames. FFmpeg only
muxed/encoded those frames with the mixed audio and generated the smaller
preview; it did not create the scene content.

## Research and skill provenance

Installed-skill discovery was performed with:

```bash
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py \
  --find "VideoFlow video rendering motion graphics Kokoro TTS ffmpeg vertical explainer"
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "video rendering"
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "Kokoro TTS"
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "motion graphics"
```

No relevant installed VideoFlow, Kokoro, or motion-graphics skill was found.
The one `video rendering` result was `cloudflare-deploy`, which was inspected
and rejected as unrelated. **No installed skill content was used**, so there is
no skill implementation provenance beyond this discovery record.

Current source documentation consulted on 2026-10-19:

- VideoFlow tagged README and local run guidance:
  `https://github.com/videoflow/videoflow/blob/v1.0.4/README.md`
- Tagged custom node contract (`ProducerNode.next`,
  `ProcessorNode.process`, `ConsumerNode.consume`, and `open`/`close`):
  `https://github.com/videoflow/videoflow/blob/v1.0.4/examples/custom_nodes.py`
- Node reconstruction and JSON-serializable constructor rules:
  `https://github.com/videoflow/videoflow/blob/v1.0.4/videoflow/core/node.py`
- Local subprocess/NATS engine:
  `https://github.com/videoflow/videoflow/blob/v1.0.4/videoflow/engines/local.py`
- Verified CLI:
  `videoflow run-local --help` from `videoflow==1.0.4`
- PyPI metadata:
  `https://pypi.org/project/videoflow/`

Local Kokoro implementation used as provenance:

- `/Users/rajeev/Code/content-machine/src/audio/tts/kokoro.ts`
- `kokoro-js==1.2.1`
- `@huggingface/transformers==3.8.1`

## Local narration and sound

Kokoro used the installed q8 ONNX cache without copying or downloading weights:

- Model:
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- Voice:
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`
- Voice ID: `bf_emma`
- Speed: 1.04
- Node runtime: v22.23.2
- Total synthesis time: 7.851 seconds

Each narration line was synthesized separately so its exact WAV duration could
drive captions and scene timing:

| Line | Start (s) | End (s) | Duration (s) | Synthesis (ms) |
|---|---:|---:|---:|---:|
| training | 0.420 | 6.045 | 5.625 | 2240 |
| recipe | 6.325 | 9.875 | 3.550 | 1343 |
| fixed | 10.255 | 13.655 | 3.400 | 1281 |
| prediction | 13.935 | 18.460 | 4.525 | 1683 |
| takeaway | 18.800 | 21.375 | 2.575 | 995 |

Sound is original and synthesized locally:

- `training-ticks.wav`: six short tonal examples at 3.460 s, gain 0.18.
- `lock-click.wav`: click and low thump at 13.535 s, gain 0.24.
- `resolve-chime.wav`: three-note resolution at 18.720 s, gain 0.17.

The final 48 kHz stereo mix is sample-aligned to 22.5333 seconds and uses a
smooth 0.84 peak limiter. No stock audio or third-party audio assets are used.

## Render command and timings

Final command:

```bash
./scripts/render.sh
```

Final measured run:

- VideoFlow DAG and 676-frame render: 106.395 s
- FFmpeg final + preview encode: 1.936 s
- Total: 108.331 s

Full review-loop renders:

| Pass | VideoFlow | FFmpeg | Total |
|---|---:|---:|---:|
| Initial complete render | 158.713 s | 1.876 s | 160.589 s |
| Refined complete render | 109.292 s | 1.714 s | 111.006 s |
| Final alignment render | 106.395 s | 1.936 s | 108.331 s |

## Full-render inspection findings

The initial complete MP4 was decoded and frames were extracted at 0.18 s,
training examples, training adjustment, recipe transition, inference input,
inference output, takeaway, and ending. The contact sheet and full-resolution
frames showed:

- Opening, scene hierarchy, captions, and training/inference color systems
  were readable and visually distinct.
- The training notebook's `TASTE`, `COMPARE`, and `ADJUST` labels overlapped in
  a single unreadable cluster at full resolution.
- The transition made the state change clear but left the analogy's through-line
  under-articulated below the notebook and recipe cards.
- The mixed WAV was 0.0667 seconds shorter than the frame timeline because the
  FFmpeg loudnorm chain trimmed trailing samples.
- FFmpeg reported `yuvj420p` because the JPEG frames arrived as full-range
  input, despite the requested `yuv420p`.

Final extracted-frame inspection confirmed the notebook labels are separated,
the transition now shows `MANY DISHES -> ONE RECIPE -> NEW DISH`, captions stay
inside the mobile safe area, and opening/middle/transition/ending frames remain
readable.

## Creative and technical refinement

Exact changes after the first complete render:

1. Rebuilt the training notebook step row with separate x positions and
   connectors so `TASTE`, `COMPARE`, and `ADJUST` are individually legible.
2. Added a substantive transition through-line panel mapping `MANY DISHES` to
   `ONE RECIPE` to `NEW DISH`, making the analogy explain the state change
   instead of merely decorating it.
3. Tightened that panel's chips to centered 220-pixel widths after the second
   pass revealed the first chip extending beyond the container.
4. Replaced the lossy FFmpeg mix tail with exact sample-domain stereo mixing and
   a smooth peak limiter.
5. Converted full-range JPEG input explicitly to television-range `yuv420p`.

The video was fully rerendered after the creative pass and again after the final
chip-alignment correction.

## Final media verification

Commands:

```bash
./scripts/inspect_media.sh
./scripts/verify.sh
```

Final results:

- Dimensions: 1080x1920
- Frame rate: 30/1
- Duration: 22.533333 s
- Decoded frames: 676
- Video codec: H.264
- Pixel format: `yuv420p`
- Audio codec: AAC
- Audio: stereo, 48 kHz
- Full FFmpeg decode: pass
- Preview smaller than final: pass
- Contact sheet: 1080x1076 JPEG, representative frames from all five scenes
- Mix duration: 22.5333 s, exact match
- Mix level: -18.45 dBFS RMS, -2.2 dB peak
- Clipped samples: 0
- Every narration line active: pass

Deliverable SHA-256:

- `final.mp4`: `e2f7ccb2d13682d547579a616ded65b8be4fb88bb266ac58c77a9f1234d224b2`
- `preview.mp4`: `2bf3461fbb1a2704e5555653c919c5c608febd11787f14a09b4f9dc739a8a8ca`
- `contact-sheet.jpg`: `969d4829c3376e84a146dd7a39ae7b67eb3a1c78c94f607a7aeff6f4e6530c53`

## Known limitations

- Kokoro line-level synthesis provides exact line spans but no word-level forced
  alignment; captions animate across measured line spans rather than highlighting
  individual words.
- No local speech-to-text engine/model was installed. Independent transcript
  recognition was therefore not performed without downloading weights. The
  actual WAV/MP4 audio was decoded and checked by sample count, per-line energy,
  silence, peak, clipping, and synchronization against the original Kokoro units.
- VideoFlow's automatic dev-broker startup produced an empty NATS handshake in
  two attempts. The final reproducible script explicitly starts NATS 2.12.15 in
  Docker and calls `videoflow run-local --no-infra`; the temporary container is
  removed on exit.
- The renderer references macOS Arial system fonts rather than redistributing
  font files.
