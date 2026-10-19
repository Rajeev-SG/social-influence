# Report

## Topic and teaching goal

Topic: **How does AI learn from mistakes?**

Teaching goal: show beginners that a model can learn from the difference
between a guess and a desired answer by turning that feedback into repeated,
small adjustments, using one continuous bucket-toss analogy.

## Technology and role

- **Primary production technology:** Movis `0.7.1` (MIT), installed from PyPI
  into a disposable Python `3.11.15` environment.
- **Official sources checked:**
  <https://github.com/rezoo/movis>, <https://rezoo.github.io/movis/overview.html>,
  <https://rezoo.github.io/movis/install.html>, and the repository examples
  linked from the README. The current `main` commit observed during research
  was `64a96185c7fc94b5630daaad2226279b5323c61e`; the latest release was
  `v0.7.1`.
- **Rendering role:** `src/render_video.py` builds a `movis.layer.Composition`
  at `(1080, 1920)`, registers a custom `FilmLayer` whose `__call__(time)`
  returns RGBA frames, adds `movis.layer.Audio` layers, and calls
  `Composition.write_video()` with `libx264`, `yuv420p`, `aac`, `+faststart`,
  30 fps and 48 kHz output. Movis therefore produces the picture, timeline,
  audio composition and encoded master.
- **Auxiliary technology:** FFmpeg `9.0.2` for narration conditioning, proxy
  encoding, decode checks and frame extraction. It is not the visual renderer.

## Skills used and provenance

1. **ffmpeg-skill** — vendored at `skills/ffmpeg-skill/`, from
   <https://github.com/kajisho5/ffmpeg-skill>, release `v2.10.4`, tag commit
   `11a70aa680c0916581164dc49957a1b64ec57a79`, MIT. Used `probe.py`,
   `check.py`, `look.py`, `audio.py` and `proxy.py` for probing, compliance,
   contact frames, audio extraction and preview generation.
2. **transcribe** — installed skill source
   `/Users/rajeev/.codex/skills/transcribe/SKILL.md`. Its workflow was consulted
   for independent speech verification, but the CLI requires `OPENAI_API_KEY`;
   that variable was unset, so no external transcription call was made.
3. **Skill discovery** — `python3
   /Users/rajeev/.codex/scripts/skill-index-refresh.py --find "..."` was run
   for Movis/motion graphics/video and audio transcription intents. No
   Movis-specific skill was found. Public searches for Movis `SKILL.md` also
   found no maintained match. No unrelated skill was relabeled as Movis.

The Remotion baseline at `../llm-reel/` was read for quality reference only.
Its typography, measured cue timing, sound-design restraint and review loop
informed the visual standard; Remotion is not used in this production.

## Local narration and audio

- TTS: already-installed Kokoro 82M q8 ONNX, model cache
  `/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX`.
- Voice: exact requested file
  `/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin`,
  SHA-256
  `669fe0647f9dd04fcab92f1439a40eeb4c8b4ab1f82e4996fe3d918ce4a63b73`.
  The script verifies that the installed `kokoro-js` voice has the same hash
  before calling `voice: 'bf_emma'`.
- `scripts/narrate.cjs` sets `transformers.env.localFilesOnly = true`, refuses
  missing cache/voice files, trims model padding, measures each cue, and writes
  `src/timing.json`. It downloaded no TTS weights.
- Result: six cues, 649 frames, `21.633333333333333` seconds. Cue spans:
  `0.220–2.921`, `3.161–5.014`, `5.254–7.537`, `7.777–9.922`,
  `10.262–18.009`, `18.449–20.559` seconds.
- Narration conditioning: FFmpeg high-pass, low-pass, compressor and loudnorm
  to approximately −17 LUFS. `scripts/soundscape.py` synthesizes an original
  48 kHz stereo ambient bed, bucket whoosh/thunk, feedback chime, aim clicks,
  loop ticks and closing resolve. Movis mixes narration at 0 dB and soundscape
  at −7.5 dB.

## Render command and timing

Final command:

```sh
.venv/bin/python src/render_video.py --output deliverables/final.mp4 --fps 30 --crf 18
```

- First complete render: **40.307 s** (649 frames).
- Required refinement render: **56.701 s** (649 frames).

The final command is the second, refined render. `./scripts/build.sh` reproduces
the audio, render and preview stages.

## Full-render inspection findings

First-cut frames were extracted from the actual MP4 at `0.40`, `2.20`, `3.25`,
`5.80`, `8.20`, `10.25`, `12.80`, `15.80`, `18.40` and `21.20` seconds and
reviewed with the FFmpeg skill. The first complete cut exposed:

1. The opening `MAKE A GUESS.` / `NOTICE THE MISS.` cross-dissolve overlapped
   both phrases around 3.25 s.
2. The long AI-loop caption overflowed its lower panel around 10.25 s and
   collided with its metadata line.
3. Process/rail labels were too small for a mobile review.
4. The final second repeated the chart and left an inconclusive tail.

The audio track was decoded and played back in full (`afplay`, exit status 0).
Every cue had non-trivial RMS/peak energy in the raw Kokoro output, and the
encoded mix retained comparable cue-window energy. An envelope cross-correlation
against `assets/audio/narration.wav` measured a **0.0 ms global lag**. The
transcribe skill could not provide an independent transcript because
`OPENAI_API_KEY` was not set; this is recorded as a limitation rather than
claimed as human listening/transcription.

## Exact creative refinement

The second render made one substantive pass:

- Replaced the opening cross-dissolve with a single-title masked handoff and a
  deliberate cyan sweep, so the phrases never overlap.
- Made captions adaptive (48/45/42/39 px, maximum four lines) and removed the
  in-frame metadata label that collided with the longest cue.
- Increased rail/process type to 22–27 px for mobile readability.
- Added a final animated `MISS → MEASURE → ADJUST` loop card with the explicit
  conclusion: “That is how AI learns from mistakes.”
- Rebuilt the contact-sheet sampling to show `0.70`, `3.45`, `6.15`, `8.75`,
  `11.25`, `15.35`, `18.90` and `21.15` seconds, covering every major scene and
  the end card without sampling a transition wipe.

## Final media verification

- `deliverables/final.mp4`: **1,361,834 bytes**, 21.633333 s, 1080 × 1920,
  30/1 fps constant, H.264 High, `yuv420p`, 649 frames.
- Audio: AAC, stereo, 48,000 Hz, 21.633 s.
- `deliverables/preview.mp4`: **468,820 bytes**, 21.633333 s, 540 × 960, 30/1
  fps, H.264, stereo AAC at 48 kHz; smaller than the master.
- `deliverables/contact-sheet.jpg`: JPEG, 2160 × 1920, eight labeled frames.
- FFmpeg full decode: no errors.
- FFmpeg-skill `check.py --platform custom --max-duration 25 --aspect 9:16
  --lufs -16 --tp -1.5 --content`: PASS for duration, aspect, constant frame
  rate, colour, audio, loudness (**−17.4 LUFS**), true peak (**−4.6 dBTP**),
  black (**0%**), frozen (**2.7 s longest**) and silence (**6%**). The only
  warning is the optional absence of a separate subtitle track; captions are
  burned into the picture.

## Known limitations

- Kokoro narration is synthetic and more even than a directed human
  performance.
- The bucket-toss analogy and the `6.4 → 7.7 / 8.0` numbers are pedagogical
  illustrations, not a live model trace or a complete explanation of gradient
  descent.
- No separate language-tagged subtitle stream is included; the required
  captions are burned in.
- The system FFmpeg build lacks `drawtext`, so the vendored skill’s timed-sheet
  mode was run with `--no-timecode` and the final contact sheet was assembled
  from its extracted frames with Pillow.
- Independent ASR verification was unavailable without `OPENAI_API_KEY`; the
  report relies on playback, full decode, cue energy and 0.0 ms envelope lag.
