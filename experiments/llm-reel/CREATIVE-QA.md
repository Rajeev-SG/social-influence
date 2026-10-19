# Creative QA

## Render → review → refinement

A complete 58.2-second first cut was rendered and inspected using actual exported frames/contact sheets and full-video multimodal review, including listening. Three real British voice samples were compared; Emma was selected over George and Fable.

The first cut was too presentation-like. The substantive refinement:

- Removed the persistent slide counters, borders and repeated page framing; varied title placement and scale.
- Rebuilt the probability display as dimensional towers with a common baseline and a visible selection.
- Connected generation to the actual sentence: selected tokens travel into the output, and the return path shows output becoming context.
- Made the learned-settings field visibly tune, settle and freeze; inference then routes signals through unchanged settings.
- Replaced a recycled network/caution icon with typed capability examples and an explicitly false, fluent sentence.
- Assembled the ending into the complete token/context/probability/output/feedback system.
- Slowed the voice delivery while removing the model's padded pauses. Runtime fell to 51.2 seconds without removing any narration.
- Increased the audibility and specificity of interaction ticks, air transfers and restrained low-frequency arrivals.
- Enlarged explanatory labels and captions. Kept probability values explicitly illustrative.

Subsequent full renders exposed a genuine handoff issue: transparent scene layers allowed outgoing text to collide with incoming text during a wipe. The final version uses opaque masked handoffs, with outgoing type cleared before the boundary and incoming type delayed until the reveal. Close transition-frame strips were inspected after this repair.

## Verification

- Full-resolution render: 1080 × 1920, 30/1 fps, 1,535 frames; 51.2-second MP4 including AAC padding.
- H.264 / yuv420p, stereo AAC at 48 kHz; both master and preview fully decode in FFmpeg without errors.
- Final mix: approximately **−16.05 LUFS integrated**, **−3.14 dBTP**. Dialogue remains dominant; no clipping.
- Fifteen caption cues are driven by exact generated-sample timing, with trimmed breathing margins. All cues are ordered, non-overlapping and inside the narration duration. Sentence captions, not fabricated word timestamps.
- TypeScript check and full Remotion render succeed. Studio loads the finished composition.
- Full-video multimodal listening independently transcribed the opening, middle and closing lines. Review confirmed accurate subtitle phrasing/sync and audible, balanced clicks, air transfers and low impacts after the sound pass.
- Opening, all major scenes, ending, and closely spaced transition frames inspected from the actual encoded output. Final contact sheet is extracted from the delivered master, not browser mockups.

## Honest limits

The British narration is synthetic, with a more even delivery than a directed human performance. Visuals explain an intentionally simplified transformer mechanism; token IDs, probabilities and the false-answer example are not a live ChatGPT trace. The film does not explain retrieval, tools, multimodal inputs, or training-data governance. These are deliberate scope choices, not missing production stages. Artistic quality remains a human judgment; render success alone was not treated as sufficient.
