# Creative QA — simpler Hyperframes version

## Main creative change

The Remotion original is untouched. This is a new 45-second Hyperframes film with **six beats and 112 spoken words**. It keeps one familiar cup-of-tea example, replaces abstract technical graphics with simple illustration and sentence completion, and removes token IDs, probabilities, network diagrams and extra labels. Teaching priorities are: learned patterns → choose a next piece → repeat → check facts.

## Actual render / review / improvement cycle

1. Rendered a complete 1080×1920 first cut with Hyperframes, then inspected frames/contact sheets and submitted the actual video for multimodal viewing and listening.
2. Review found the tea comparison intuitive, the earlier-learning/current-answer distinction clear, the next-piece loop understandable, and the visual treatment no longer overwhelming. The listening check correctly transcribed the middle narration.
3. Made a substantive clarity/polish pass:
   - Kept bicycle visible through its spoken comparison instead of dismissing it early.
   - Added one-at-a-time highlighting to the familiar message pieces, without introducing IDs or terminology.
   - Snapped punctuation naturally against the preceding word: `tea, please.`, not `tea , please .`.
   - Removed the cup's faint pre-cut fade outlines at scene changes.
   - Made the final takeaway headline immediately readable on the green cut rather than slowly fading into contrast.
   - Increased caption size slightly for mobile reading.
   - A final listening/clarity review confirmed the calmer story. In response, softened the capability beat to the same paper background, and made the existing text quieter than the bold newly generated continuation. Whole-word highlights now have extra breathing room.
4. Reran Hyperframes check and made a complete delivery-quality render. The final contact sheet comes from the delivered MP4, not a mockup or browser-only preview.

## Verified

- Hyperframes check passes: no runtime errors, no motion errors, no layout issues in nine samples; all **38/38** text contrast checks pass WCAG AA.
- Static lint retains non-blocking structural suggestions to split the six simple scene groups and captions into sub-compositions. The shared cup and global seekable timeline intentionally remain in one small composition; these are source-organisation advisories, not playback defects.
- Final video: **1080×1920, 30 fps, 1,354 frames**, H.264/yuv420p and stereo AAC at 48 kHz. Container duration is **45.2 seconds**, including audio padding; authored duration is 45.12 seconds.
- Master and preview both decode completely with FFmpeg without errors.
- Captions use the actual generated utterance durations and exact PCM sample placement, with breathing margins. They are sentence-level captions, not guessed word timings.
- Original sparse plucked chords and soft tactile taps; narration remains the focus. Final mix measured approximately −16.11 LUFS integrated and −3.43 dBTP, with ample headroom.
- Local cached Kokoro bf_emma reused; no new voice model weights or inference environment downloaded. Voice is explicitly disclosed as AI-generated.

## Intentional simplification

“Sentence completer” is an analogy for the core next-token mechanism, not an exhaustive account of reasoning, the ChatGPT product, tools or retrieval. Pieces of text can be smaller than words. Illustrative completions are not a trace from a live model. The synthetic voice is more even than a directed human performance. Quiet holds and generous space are deliberate responses to the user's request for less overwhelm.
