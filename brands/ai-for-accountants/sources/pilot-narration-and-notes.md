# AIForAccountants pilot — narration + source notes

Pilot for queue item 1: *Turn raw client meeting notes into a follow-up email + action list, with human-review checklist.*
All data is synthetic. No real client data. No time-saving, tax, compliance or productivity claims.

## Files
- Clips: `brands/ai-for-accountants/media/pilot/scene-001.mp4` … `scene-006.mp4` (6 × ~8s, 1080×1920, 30fps, silent)
- Contact sheet: `brands/ai-for-accountants/media/pilot/contact-sheet.png`
- Evidence: `pilot-notes.json`, `pilot-prompt.txt`, `pilot-model-response.json`
- Recorder: `scripts/prepare-accountants-pilot.mjs`

## Visual contract in every clip
- Top 1400px = core 'Workflow lab' UI; bottom 400px = plain dark `#182431` caption band from y=1510.
- Persistent strip: **INPUT → AI STEP → HUMAN CHECK**, with the current stage highlighted.
- Persistent badges: **SYNTHETIC DATA** and **REVIEW REQUIRED**.
- Title bar states: own functional demo — not a ChatGPT/OpenAI UI.
- The demo UI is our own; no ChatGPT/OpenAI/other vendor UI is imitated or shown.

## Real vs synthetic
- **Real:** the browser recording, the UI interactions, the checklist controls, and the model call. The email and action list on screen are the actual response from `opencode-go/deepseek-v4.1-flash` via the local cliproxyapi `/chat/completions` route.
- **Synthetic:** the meeting notes, the practice name (Rowan & Co), the client (Bluebell Cafe Ltd), and every action/owner in them.
- Credentials are read from `~/.codex/config.toml` at run time and are never printed or written to any artifact.

## Six-scene desired narration (ordinary neutral voice; parent adds via CM)

1. **scene-001 — Start with the raw meeting notes.** "This is a real workflow, not a mock-up. These are synthetic meeting notes, clearly labelled. No dates, no amounts, no advice — exactly the messy input an AI step usually gets wrong."
2. **scene-002 — Set the task and the rule before the model runs.** "Before the model runs, we set the task and the review rule: use only these notes, and any date the notes don't state stays 'to confirm'."
3. **scene-003 — One real model call returns structured JSON.** "One call to the model, and it comes back as structured JSON — subject, email, action list and review flags. This is model output, so it's untrusted until a person checks it."
4. **scene-004 — The model drafts the follow-up email.** "The model drafts the email. Notice it does not invent a deadline. Every date is 'to confirm'. It's a draft — not sent, not advice."
5. **scene-005 — The human reads every action back against the notes.** "Now the human step. Every action is read back against the notes. If a date wasn't stated, it stays 'to confirm'. Nothing is approved yet."
6. **scene-006 — The save is gated by the checklist.** "The save is blocked until a human completes the checklist: every action traced, no deadline invented, owners match the notes, no advice added. AI drafts. A person checks. Only then does it save."

## Source/guidance notes (generic drafting + human oversight; no feature marketing)
- OpenAI API docs, Text generation — models produce text used as a starting point, not a verified outcome: https://developers.openai.com/api/docs/guides/text (accessed 2026-09-29)
- OpenAI API docs, Evals — model output should be tested against stated content criteria: https://developers.openai.com/api/docs/guides/evals (accessed 2026-09-29)
- NIST AI RMF Generative AI Profile (NIST AI 600-1, Jul 2024) — human oversight and review are expected controls for generative-AI use: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf (accessed 2026-09-29)
These are generic drafting/oversight references, not vendor feature claims.

## QA notes
- No time-savings, tax, compliance or productivity claims.
- Jurisdiction-neutral; no accounting-standard assertion is made.
- Output that could affect a client communication shows an explicit human review/control point.
- Model output is retained verbatim in `pilot-model-response.json`; displayed email/actions are that same response, not re-written by hand.
- Recorder note: `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/Cellar/x265/4.1/lib` is set for ffmpeg; clips encoded with libx264, no audio track.
