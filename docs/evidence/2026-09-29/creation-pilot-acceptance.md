# Acceptance: brand queue to reviewed MP4 bundle

Date: 2026-09-29

## Expected behavior

For both brands, `social-influence create --brand <brand> --next` must select the
first unused topic, preserve the authoritative profile/evidence requirements,
run Content Machine creation and fail-closed QA, stop for review-bound
resumption, and advance the queue only after a reviewed render becomes a final
bundle. The two brands must use one interface without brand-name orchestration.

## Executed steps

1. Ran 23 unit tests covering queue order, source/media hashes, arithmetic,
   fallback rejection, machine QA, review staleness/completeness, locking and
   resume.
2. Produced and reviewed the GutKitchen pizza-bean bowl pilot with the supplied
   profile, Sainsbury source snapshots and Decimal calculation.
3. Produced and reviewed the AIForAccountants synthetic meeting-notes workflow
   using real browser recordings, retained model response and a human checklist.
4. Inspected first/middle/final frames, caption-safe regions, disclosure badges,
   exact locked scripts, audio signal and all Content Machine QA reports.
5. Re-ran the same command after review to create bundles and update queues.

## Evidence

- GutKitchen bundle: `output/gutkitchen/40g-protein-15g-fibre-pizza-bean-bowl-using-supermarket-ingr-967b36228b/attempt-0023/bundle/`
- GutKitchen review: `output/gutkitchen/40g-protein-15g-fibre-pizza-bean-bowl-using-supermarket-ingr-967b36228b/attempt-0023/review.json`
- AIForAccountants bundle: `output/ai-for-accountants/turn-raw-client-meeting-notes-into-a-follow-up-email-action--55f1a74aa4/attempt-0002/bundle/`
- AIForAccountants review: `output/ai-for-accountants/turn-raw-client-meeting-notes-into-a-follow-up-email-action--55f1a74aa4/attempt-0002/review.json`
- Candidate benchmark: `docs/ENGINE-BENCHMARK.md`
- Operating runbook: `docs/OPERATING-CREATION.md`
- Raw accepted run captures + manifests: `docs/evidence/2026-09-29/runs/`
- Initial failed captures preserved unchanged: `content-machine-doctor.initial.json`, `content-machine-smoke.initial.json`

GutKitchen final video: 31.15s, 1080x1920, 30fps. Caption sync: 14/14 segments,
median drift 78.5ms, P95 811.2ms, quality 0.866. Provenance, score and validation
pass. Frame zero shows the finished bowl plus ~40g PROTEIN / 15g+ FIBRE badges.
The fibre counter progresses as ingredients enter. AI-illustration and
label-estimate disclosures remain visible. Final CTA is singular.

AIForAccountants final video: 32.04s, 1080x1920, 30fps. Caption sync: median
drift 82.5ms, P95 97.1ms, quality 0.885. Provenance, score and validation pass.
Frames/OCR show raw synthetic notes, `INPUT -> AI STEP -> HUMAN CHECK`,
`SYNTHETIC DATA`, `REVIEW REQUIRED`, action tracing, checklist-gated save and
the final CTA. The bottom caption band is clean.

## Result

PASS for the requested creation and reviewed-render path on both brands.

The same command and generic orchestration produced radically different
content: generated food-illustration build for GutKitchen and real screen
workflow recording for AIForAccountants.

## Remaining risk

- Reviews are automated Codex agent reviews, not human sign-offs.
- GutKitchen uses disclosed AI food illustrations; real footage of the cooked
  recipe is preferable before public publishing.
- Evidence files are copied raw from the run/dependency tools and hash-manifested; the initial failed captures are preserved separately rather than overwritten. Postiz deployment, account connection, upload binding, manual publish and
  generated-post publishing remain unproven. The two pilot media folders are
  committed and `scripts/validate_packs.py` rechecks every pack hash in CI. The bundle payload is structurally
  shaped for Postiz drafts but contains deliberate binding placeholders. Issue #2 must remain open.
- Output and `brands/*/media/` are gitignored; retain run bundles and source
  media in durable storage.
