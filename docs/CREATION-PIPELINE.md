# Creation pipeline

The deep-research report is not passed wholesale to the video generator on every run. It is compiled into small, persistent brand profiles plus content queues.

## Contract

For every post:

1. Load `brands/<brand>/profile.md`.
2. Select one unused item from `brands/<brand>/queue.md`.
3. Research/validate the specific post topic and attach sources or calculations required by the profile.
4. Run Content Machine's `niche-profile-draft` logic so the profile shapes the hook, script, shots, captions and packaging together.
5. Generate the short with Content Machine `generate-short` (or the selected creation engine once Issue #2 benchmarking is complete).
6. Run publish-prep / QA.
7. Hand the final MP4 + caption/title/metadata to Postiz.
8. Mark the queue item produced/published and retain the run artifacts for later performance feedback.

## Why this shape

The research report is strategic source material. The engine should consume a compact, stable profile plus one concrete topic, not re-read a long research report and reinterpret the brand on every post.

## Content Machine mapping

The current Content Machine `niche-profile-draft` expects:

- hook patterns
- tone rules
- pacing rules
- forbidden phrases
- CTA options
- visual guidance
- thumbnail / first-frame guidance
- platform target

The brand profiles in this repo use those same concepts.

## Launch sequence

Start with **GutKitchen** and **AIForAccountants**, as recommended by the research. Produce 3–5 pilot videos per brand before bulk generation. Use those pilots to validate the visual template, narration and hook grammar before creating the first 20-post batch.

Do not block this on automated discovery or the future decision engine.
