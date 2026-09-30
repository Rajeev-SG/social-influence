# social-influence

Autonomous AI-native social media brands that build audiences and sell digital products.

## MVP architecture

Keep the common backend deliberately small:

| Component | Purpose | Initial implementation |
|---|---|---|
| **Discover** | Find topics/questions/trends worth covering | Manual / ChatGPT deep research first; automate later |
| **Create** | Research → script → assets → finished short-form content | Content Machine and/or MoneyPrinterTurbo + LLMs |
| **Publish** | Schedule and publish across social platforms | Self-hosted publisher (YouTube Data API + cookie/session-based TikTok & Instagram uploaders) — see `docs/PUBLISHING.md`; Postiz is not used |
| **Sell** | Storefront, checkout and digital delivery | Existing commerce platform; do not rebuild |
| **Measure** | Collect social performance and sales/conversion data | Platform/Postiz + store APIs; thin normalisation layer |
| **Decide** | Use results to choose what to make/post/sell next | **Primary custom component** |

### Core loop

```text
Discover demand
      ↓
Decision agent
      ↓
Create content
      ↓
Postiz
      ↓
Social platforms
      ↓
Views / clicks / sales
      ↓
Measure
      └────────────→ Decision agent
```

The optimisation target is ultimately **commercial performance**, not content volume. Engagement is an intermediate signal.

## Build principle

**Do not wait for the autonomous backend before publishing.**

Creation and publishing are already largely solved. Start building an audience immediately using manual/high-quality discovery and research, while the supporting automation is built underneath the live operation.

Initial launch sequence:

1. Research and select the first niche(s).
2. Define initial content pillars, formats, hooks and evidence standards.
3. Create the social accounts.
4. Connect accounts to Postiz.
5. Connect Content Machine and/or MoneyPrinterTurbo into the creation path.
6. Generate and QA an initial content batch.
7. Start publishing.
8. Record basic performance data from day one.
9. Build automated discovery, measurement and decision-making only after real content is producing useful feedback.

## Scope guardrail

Do **not** turn the MVP into a 20-component marketing platform.

The first version needs only:

```text
research → create → publish → measure → decide
                         ↓
                        sell
```

Everything else is an optimisation or later capability unless real operating data proves it is needed.


## Launch critical path

This is the shortest path to a live audience and is deliberately separate from later backend automation:

1. **Content research** — pick the niche/sub-niche, audience, positioning, content pillars, hooks, formats and visual style.
2. **Accounts** — create the initial TikTok, Instagram and YouTube accounts.
3. **Postiz** — connect the accounts and verify publishing.
4. **Creation engine** — wire Content Machine and/or MoneyPrinterTurbo into Postiz.
5. **Initial batch** — generate and QA roughly 10–20 posts.
6. **Publish** — start a consistent cadence immediately.
7. **Observe** — capture basic post-level performance from day one.

Automated trend discovery, sophisticated attribution, product generation and the decision engine are **not launch blockers**. Manual/ChatGPT deep research should supply discovery until live performance data justifies deeper automation.

## Creation CLI prototype (Issue #2)

`social-influence create --brand gutkitchen --next` and the same command for
`ai-for-accountants` select the next queued topic, run profile-driven Content
Machine creation, enforce publish-prep QA, pause for review-bound resumption,
and create a final MP4 bundle only after approval. Two different-style pilot
posts have completed that path. See
[operating instructions and verification](docs/OPERATING-CREATION.md).

Postiz deployment, connected accounts and real publishing remain unverified.
The GutKitchen pilot uses disclosed AI food illustrations; real footage of the
cooked recipe is preferable before public publishing. Run checks with
`python3 -m unittest discover -s tests -v`.
