# Creation adapter — reviewed pilot path

## Acceptance status

Two different-brand pilot posts now complete the same path from ordered queue
item to reviewed MP4 and final bundle:

- GutKitchen: `output/gutkitchen/40g-protein-15g-fibre-pizza-bean-bowl-using-supermarket-ingr-967b36228b/attempt-0023/bundle/`
- AIForAccountants: `output/ai-for-accountants/turn-raw-client-meeting-notes-into-a-follow-up-email-action--55f1a74aa4/attempt-0002/bundle/`

Both queue items were marked generated only after Content Machine publish-prep
passed and an explicit review record matched the input, brief, MP4 and complete
engine artefact tree. Reviews were performed by Codex as an agent and state that
clearly; they are not human sign-offs.

**Postiz is not yet proven.** No Postiz deployment, connected social account,
upload-media ID, manual test publish, or generated-post publish has been
verified. `postiz-handoff.json` is intentionally an upload-binding handoff, not
an invented API request. Issue #2 remains open.

## Install and invoke

Python 3.11+; macOS/Linux (POSIX file locks). From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/social-influence create --brand gutkitchen --next
.venv/bin/social-influence create --brand ai-for-accountants --next
```

`--root /absolute/repository` may precede `create`; otherwise the current
directory must be the checkout root. The CLI does not call publishing services,
create posts, or schedule posts.

Required runtime variables:

```sh
export CONTENT_MACHINE_DIR=/absolute/path/to/content-machine
export OPENAI_BASE_URL=http://127.0.0.1:8080/v1
export SI_MODEL=opencode-go/glm-5.3-flash
export CM_PYTHON=/absolute/path/to/content-machine/.venv/bin/python
export CM_FFMPEG=/opt/homebrew/bin/ffmpeg
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/Cellar/x265/4.1/lib
export OPENAI_API_KEY='read privately from ~/.codex/config.toml'
```

Do not commit keys or `.env` files. The local router bearer token was read
programmatically and never written to repository artefacts. On this Mac, the
Homebrew FFmpeg binary initially fails because its x265 dylib link is stale;
the `DYLD_FALLBACK_LIBRARY_PATH` value is a process-local workaround. No
Homebrew link, library or shared setting was changed.

Content Machine: https://github.com/45ck/content-machine

Tested revision: `46cfe459d9ffbf40f847399e3f88c7c380074e7b`, package 0.2.2.
At that revision `npm ci` failed because the lock omitted platform optional
packages. The local checkout used `npm install --package-lock=false
--ignore-scripts --no-audit --no-fund` without changing tracked upstream files.
Its `.venv` contains `scenedetect` and `opencv-python-headless` for the cadence
gate. Node 26 raised a better-sqlite3 engine warning; prefer upstream-supported
Node 22/24 in a production environment. The dependency inventory still reports a
missing standalone Whisper binary/model; the exercised audio path uses Kokoro
timed unit timestamps and does not require Whisper. `docs/evidence/2026-09-29/content-machine-doctor.json` records that distinction.

## Workflow

1. Read `brands/<brand>/profile.md` and select the first unchecked `queue.md`
   item under a per-brand kernel lock.
2. Run Content Machine's `niche-profile-draft` skill with the whole profile,
   topic, source evidence, calculations, media rights and pack constraints.
   Save the exact prompt and unified `production-brief.json`.
3. Pass a compact profile-derived brief and pre-approved spoken copy into the
   real Content Machine `generate-short` JSON-stdio harness.
4. `generate-short` performs its normal script/audio/visual/render pipeline.
   Its generic prompt imposes a 60-word minimum and tends to expand approved
   copy. The adapter therefore runs a deterministic copy-lock rebuild with
   Content Machine's own `script-to-audio`, `timestamps-to-visuals`,
   `video-render` and `asset-ledger` stages. This preserves the reviewed script,
   shot order, captions and source/rights record.
5. Attach hash-matched supplied rights evidence to every generated ledger entry.
   Content Machine `publish-prep-review` then runs unconditionally with cadence,
   audio-signal, provenance and burned-caption-sync validation.
6. If any required gate fails, stop. If it passes, write
   `review.required.json` and stop again for full playback and brand/evidence
   review.
7. A reviewer copies that file to `review.json`, records identity and concrete
   passing notes for every check, then reruns the identical command. Approval is
   bound to input, brief, MP4 and engine-tree hashes. Stale or partial review
   cannot finalize.
8. Only then create the bundle and replace the exact queue line `- [ ]` with
   `- [x]`. Failed, missing, stale or unreviewed runs never advance the queue.

## Topic production pack

The first command writes `output/<brand>/<post-id>/selection.json`. Use that ID
for `brands/<brand>/posts/<post-id>.json`. The pack is an explicit operator
preproduction artefact; automated trend/topic selection is out of scope.

Required shape:

```json
{
  "topic": "Exact queue text",
  "sources": [{
    "url": "https://official-source.example/page",
    "file": "sources/source.txt",
    "sha256": "SHA256_OF_THE_SAVED_SOURCE"
  }],
  "evidence": {
    "Exact Evidence / QA bullet from profile.": "Source, calculation, or explicit not-applicable rationale."
  },
  "calculations": [{
    "name": "protein_g_per_serving",
    "terms": [{"grams": 200, "per100g": 5}],
    "claimed": 10
  }],
  "hook_narration": "Pre-approved spoken hook.",
  "scene_narration": ["Scene 1.", "Scene 2."],
  "cta_narration": "Pre-approved spoken CTA.",
  "media": [{
    "file": "media/topic/scene-001.mp4",
    "sha256": "SHA256_OF_THE_APPROVED_CLIP",
    "kind": "screen-recording",
    "rights": {
      "reviewStatus": "owned",
      "rightsStatus": "owned",
      "licenseName": "Own recording using synthetic data",
      "contentIdRisk": "none-known"
    }
  }]
}
```

Values above are schema examples. All paths resolve within the brand directory,
including symlinks. Source and media hashes are checked before generation and
again before finalization. Every profile Evidence / QA bullet needs an explicit
disposition. Decimal arithmetic totals must match within 0.1g; arithmetic does
not validate the underlying source or recipe applicability.

## Pilot materials

### GutKitchen

The first item uses validated Sainsbury label tables for one calculated portion:
235g drained cannellini, 100g lighter mozzarella, 150g passata and 50g spinach.
The Decimal result is 40.025g protein and a conservative 15.69g fibre lower
bound. The post says “around 40g” and “15g+”, states label estimates, and asks
viewers to check their pack. The recipe was not physically cooked and claims no
measured time or health effect.

At the user's explicit instruction to source/generate missing production
material, this pilot uses **generated food illustrations**, not footage of a
physically tested meal. They are disclosed on-frame as “AI food illustration |
label-based estimate” and retain provider/model/prompt/workflow provenance.
They are not silent generic stock. Real footage of the actual recipe remains
preferable before public publishing.

### AIForAccountants

The pilot uses a real Playwright browser recording of an own functional
“Workflow lab”, not an imitation of ChatGPT/OpenAI/vendor UI. All notes,
practice/client names and actions are synthetic. The email and action list are
the retained actual `opencode-go/deepseek-v4.1-flash` model response. The
workflow sets “TO CONFIRM” for unstated dates and blocks save until a human
checks every action, owner and review flag.

Persistent controls are `INPUT → AI STEP → HUMAN CHECK`, `SYNTHETIC DATA` and
`REVIEW REQUIRED`. No real client data, invented deadlines, tax/accounting
advice, compliance claim, productivity claim or autonomous approval is shown.

## Artefacts

Stable anchor: `output/<brand>/<topic-slug>-<topic-hash>/`.

Each `attempt-NNNN` retains profile, production input, source record, niche
prompt/brief, copied media and manifest, every Content Machine request/response
and log, full stage artefacts, provenance, review requirement/decision and the
final bundle when approved. Failed attempts remain for diagnosis.

Output directories and future media are gitignored to keep large files out of Git. The two pilot media folders and every pack source are committed. `scripts/validate_packs.py` checks content hashes and `git ls-files --error-unmatch`, so CI fails if a pack references missing or untracked inputs. Retain later media and reviewed bundles in durable storage.

Bundle contents:

- `video.mp4`
- `metadata.json` — title, caption, hashtags
- `source-qa.json` — source record and complete review decision
- `postiz-handoff.json` — media hash/path, content, target platforms and a
  structurally valid Postiz draft payload template with required bindings

Visual examples from both reviewed pilots are collected in [docs/examples/README.md](examples/README.md).

## Verification performed (2026-09-29)

- 23 standard-library tests pass; `scripts/validate_packs.py` and `scripts/validate_evidence.py` run in CI. Tests cover ordered queue selection, evidence and
  hash failures, calculation mismatch, fallback rejection, machine-QA failures,
  stale/partial/string-true review rejection, path traversal, locking, resume,
  distinct profile artifacts and the harness banner/JSON parser.
- Both real commands completed to reviewed bundles. GutKitchen is 31.15s,
  1080×1920, 30fps; AIForAccountants is 32.04s, 1080×1920, 30fps.
- Content Machine validate, score, provenance and caption-sync reports pass for
  both. GutKitchen caption quality is 0.866 (P95 drift 811ms); AIForAccountants
  is 0.885 (P95 drift 97ms).
- Full-timeline frame review found and rejected an earlier GutKitchen first-frame
  cadence flash; regenerated clips now open on the finished meal with both
  badges. OCR confirmed the accountant frames show raw notes, review rules,
  action tracing and the checklist-gated save.
- Candidate benchmark: `docs/ENGINE-BENCHMARK.md`. It compares MoneyPrinterTurbo,
  short-video-maker, OpenNolan, OpenShorts and Content Machine using the same
  GutKitchen contract and includes one real MoneyPrinterTurbo assembly smoke.
  It does not claim render-quality ranking where no candidate was render-tested.

## Remaining critical path

1. Deploy Postiz in the chosen environment and connect TikTok, Instagram and
   YouTube.
2. Prove one manual post through Postiz, then bind a generated bundle's uploaded
   media IDs/integration settings to a real Postiz request.
3. Publish one generated reviewed post and retain provider/Postiz response IDs.
4. Before public GutKitchen publishing, decide whether disclosed AI food
   illustrations are acceptable or replace them with footage of the cooked meal.
5. Add retry/error visibility for remote publishing jobs once the Postiz route
   exists.

Do not close Issue #2 until the Postiz and real-publish acceptance criteria are
verified.
