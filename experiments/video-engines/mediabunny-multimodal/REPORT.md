# Benchmark report: Mediabunny — How does multimodal AI work?

Date: 2026-10-19 (Europe/London)

## Topic and teaching goal

**Topic:** How multimodal AI combines images, audio, and text.

**One-sentence goal:** Teach intelligent beginners that different input senses
become compatible representations the model can combine before producing one
answer.

The central analogy is **different senses become shared notes**. Image, audio,
and text fragments visibly converge into one workspace containing visual,
acoustic, and semantic notes; the last scene combines those notes into one
answer.

## Technology and rendering role

- **Mediabunny:** `mediabunny` 1.56.1 from
  `/Users/rajeev/Code/content-machine/node_modules/mediabunny`.
- **Browser encoder:** Playwright Chromium with WebCodecs; Playwright 1.63.0.
- **TTS:** `kokoro-js` 1.2.1 with
  `@huggingface/transformers` 3.8.1.
- **Inspection/review derivatives:** FFmpeg 9.0.2.

Mediabunny performs the substantive encode and mux:

- `VideoSampleSource` receives explicit 1080 × 1920 limited-range BT.709 I420
  frames produced from the Canvas scene, then encodes them as H.264/AVC.
- `AudioBufferSource` receives the complete stereo PCM mix, resamples it to
  48 kHz, and encodes AAC.
- `Output` + `Mp4OutputFormat` + `BufferTarget` write the H.264/AAC streams into
  one fast-start MP4.
- The renderer records the WebCodecs configurations:
  `avc1.640028`, 1080 × 1920, 30 fps, variable bitrate;
  `mp4a.40.2`, 2 channels, 48 kHz, 192 kbps.

FFmpeg does not encode or remux `final.mp4`. It only makes `preview.mp4`,
extracts inspection frames/audio, and verifies the Mediabunny result.

## Research and skill provenance

Installed skill discovery used the required command:

```sh
python3 /Users/rajeev/.codex/scripts/skill-index-refresh.py \
  --find "video production Remotion animation encoding muxing Mediabunny audio captions"
```

The same index was queried separately for Remotion/video rendering, media
encoding/muxing, and Kokoro/caption workflows. All returned `no skill matched`.
No Mediabunny-specific skill was invented or claimed.

Skills actually used:

- `official-first-docs`, `/Users/rajeev/.codex/skills/official-first-docs/SKILL.md`
  — required current authoritative documentation before API implementation.
- `web-search`, `/Users/rajeev/.agents/skills/web-search/SKILL.md` — SearXNG was
  attempted first. It returned no results because `google cse` was rate-limited;
  authoritative library documentation was then resolved through Context7.
- `compare-screenshots`, `/Users/rajeev/.codex/skills/compare-screenshots/SKILL.md`
  — evidence-first frame review for overlap, stale captions, incomplete
  fragments, transition state, and final hold.
- Repository-local current Remotion Agent Skills v4.0.536:
  `remotion-best-practices`, `remotion-multimedia`, and `remotion-captions`,
  located at
  `/Users/rajeev/Code/social-influence/experiments/llm-reel/.agents/skills/`.
  These supplied the current creative/caption checklist and the official
  Mediabunny overview route. Remotion itself was not used to render this video.

Mediabunny API sources, accessed 2026-10-19:

- Context7 library ID `/vanilagy/mediabunny`.
- [Quick start: create a new MP4](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/quick-start.md).
- [Media sources: CanvasSource](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/media-sources.md).
- [Writing media files](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/writing-media-files.md).
- [Composable conversions](https://github.com/vanilagy/mediabunny/blob/main/docs/guide/converting-media-files.md).
- Installed 1.56.1 source/type declarations:
  `src/media-source.ts`, `src/encode.ts`, `src/output.ts`,
  `src/output-format.ts`, and `dist/modules/src/*.d.ts`.

These sources established the current `VideoSampleSource`, `AudioBufferSource`,
`Quality`, `Output`, and MP4 target signatures used in the renderer.

## Local TTS and audio

- Model cache:
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`
- Model file: `onnx/model_quantized.onnx`, 92,361,116 bytes.
- Voice:
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`,
  522,240 bytes.
- Settings: `bf_emma`, speed 0.96, CPU, dtype `q8`, `local_files_only: true`.
- No TTS model, voice, or other weights were downloaded.

Kokoro generated six measured utterances at 24 kHz. The resulting mono float WAV
was converted to stereo PCM16 with FFmpeg, then mixed with an original procedural
bed: low drone, scene-start tones, and short filtered noise swells. Captions use
the sample-derived start/end times written to `src/timing.json`.

The complete 22.822-second source mix was played locally with `afplay`
(`status=0`, 24 seconds wall time). The muxed audio was also decoded and checked
with EBU R128 and `astats`. A human ear review was not available inside the
execution environment; objective intelligibility/sync evidence and full playback
were used instead.

## Commands and measured timings

```sh
node scripts/generate-narration.cjs
ffmpeg -i assets/audio/narration.wav -ac 2 -acodec pcm_s16le assets/audio/narration-pcm16.wav
mv assets/audio/narration-pcm16.wav assets/audio/narration.wav
python3 scripts/generate-soundtrack.py
node scripts/render.mjs --out deliverables/final.mp4 --label first-cut
# first-cut inspection and refinement, then:
node scripts/render.mjs --out deliverables/final.mp4 --label refined
scripts/build-review.sh
scripts/qa-inspect.sh
```

Measured wall times:

- Kokoro generation: **10.30 s**
- Sound design/mix: **0.58 s**
- First complete Mediabunny render: **12.21 s**
- Refined Mediabunny render: **24.51 s**
- Preview/contact sheet: **1.33 s**
- Final automated QA: **1.04 s**

The refined render is slower because `CanvasSource` was replaced with an explicit
RGB→I420 conversion path needed for literal `yuv420p` output.

## Mandatory full-render inspection

The first complete MP4 decoded successfully. Frames were extracted and visually
inspected at the opening (1.20 s), image (6.30 s), image→audio handoff (8.05 s),
audio (9.70 s), text (12.85 s), text→convergence handoff (14.55 s), convergence
(16.75 s), combined answer (21.20 s), and ending (23.10 s). Muxed audio was
decoded separately and compared with the cue timeline.

Concrete first-cut weaknesses:

1. **Stale captions at scene changes.** At 8.05 s and 14.55 s the old caption was
   still prominent after the next scene had begun.
2. **Text-scene collision.** At 12.85 s the “words → shared representation”
   label touched/overlapped the third semantic bar.
3. **Incomplete hook fragment.** At 1.20 s the text modality card was visible but
   blank while its staggered reveal was still at zero.
4. **Color-format mismatch.** The first encoder path reported `yuvj420p`
   (full-range 4:2:0) instead of the requested literal `yuv420p`.

Audio measurements on the first cut were already healthy and were retained:
- Integrated loudness: −14.3 LUFS
- Loudness range: 2.6 LU
- True peak: −1.7 dBFS
- No decode errors or clipped flat regions

## Creative/technical refinement

Exact changes made after inspecting the complete first cut:

- Caption visibility now ends at cue end + 0.14 s instead of + 0.52 s, with the
  fade-out beginning at cue end instead of 0.18 s later. New scene captions no
  longer compete with outgoing captions.
- In `src/scene.js`, semantic bars moved from `y = 1230 + 62 × row` to
  `y = 1212 + 56 × row`; the label baseline moved from 1392 to 1402. The label is
  now separated from all three bars.
- Hook modality reveals now stagger from scene progress rather than the slower
  orbit progress. Image, audio, and text fragments plus their labels are all
  legible by the 1.20 s review frame.
- `scripts/render.mjs` now converts Canvas RGBA to clamped limited-range BT.709
  I420 and feeds `VideoSampleSource` instead of using `CanvasSource`. Mediabunny
  still performs H.264/AAC encoding and MP4 muxing, but the stream now reports
  exact `yuv420p`/`tv` range.
- Buffer base64 transfer was chunked to avoid stack overflow on larger outputs.

The refined render was extracted at the same timestamps and checked again. All
three visual defects were absent; opening, transitions, convergence, answer, and
ending remained legible and coherent.

## Final media verification

`deliverables/final.mp4`:

- Container: MP4 (`isom`, fast-start compatible), 11,217,797 bytes.
- Video: H.264 High, `avc1.640028`, `yuv420p`, BT.709 limited (`tv`) range.
- Dimensions: 1080 × 1920.
- Frame rate: 30/1 fps average and nominal; 697 frames.
- Video duration: 23.233333 s.
- Audio: AAC-LC, `mp4a.40.2`, 48,000 Hz, 2 channels, stereo, 164,112 bps.
- Container duration: 23.317333 s (includes the AAC tail).
- Full decode: FFmpeg decoded all 697 frames with an empty error log.
- Loudness: −14.3 LUFS integrated, 2.6 LU LRA, −1.7 dBFS true peak.

`deliverables/preview.mp4`:

- 540 × 960, H.264 `yuv420p`, 30 fps, stereo AAC-LC.
- 945,140 bytes; 23.233333 s.

`deliverables/contact-sheet.jpg`:

- JPEG, 1080 × 1280, 176 KB.
- Six frames in scene order: hook, image, audio, text, shared representations,
  combined answer.

## Known limitations

- “One model” is a beginner-level simplification. Production multimodal systems
  may use modality-specific encoders/adapters plus a shared fusion/generation
  model; the important concept is alignment into compatible representations.
- Captions are sentence-level and measured from generated utterance boundaries,
  not word-level karaoke timestamps.
- The agent could not perform a subjective human listening review. Full local
  playback, decoded waveform/loudness checks, cue timing, and generated source
  text provide the available audio QA evidence.
- The build currently relies on the existing `content-machine` package/cache
  paths for Playwright, Mediabunny, Kokoro, and Transformers. It intentionally
  does not duplicate dependencies or weights.
- This FFmpeg build has no `drawtext` filter, so the contact sheet is unlabeled;
  its six-frame order is specified here and in `README.md`.
- No `node_modules`, model weights, caches, or temporary render frames are
  retained in the benchmark directory.
