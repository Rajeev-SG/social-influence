# Publishing — self-hosted, zero paid SaaS

The publisher turns a **PostBundle** into real posts on YouTube, TikTok and
Instagram for accounts we own. No Postiz, no scheduling SaaS, no TikTok/Meta
app review.

```text
PostBundle (posts/<post-id>/bundle.json)
      ↓  social-influence publish <path> --platforms youtube,tiktok,instagram
self-hosted publisher (publisher/)
      ↓
YouTube (Data API v3, own OAuth client)
TikTok  (tiktok-uploader, cookie session from our Chrome profile)
Instagram (instagrapi, username/password + persisted session)
      ↓
verified published post (browser-verified, ledger recorded)
```

## Layout

```text
publisher/
  pyproject.toml            deps + `social-influence` CLI entrypoint
  .env.example              environment template (copy to .env)
  social_influence/
    bundle.py               PostBundle — the stable boundary with the creation engine
    cli.py                  `social-influence publish` / `status`
    ledger.py               append-only publication ledger + duplicate prevention
    api.py                  optional FastAPI POST /publish
    providers/
      youtube.py            YouTube Data API v3 (OAuth, unverified personal app)
      tiktok.py             tiktok-uploader (Selenium + exported cookies)
      instagram.py          instagrapi (session-persisted)
  scripts/
    youtube_auth.py         one-time OAuth bootstrap (fixed loopback port)
    render_fibre_upgrades.py  example creation-engine output (PIL + ffmpeg)
    tiktok-cookie-export.js cookie export helper (runs inside Playwriter)
posts/<post-id>/            bundle.json + assets (the post itself)
```

## Setup

```bash
cd publisher
uv venv .venv && uv pip install -e .
cp .env.example .env   # then fill in GUTKITCHEN_IG_PASSWORD
```

All reusable state lives in `$SOCIAL_INFLUENCE_STATE_DIR` (default
`~/.social-influence`), outside the repo, gitignored and never committed:

| File | What |
|---|---|
| `google_oauth_client.json` | OAuth desktop client secret (Google Cloud) |
| `google_token.json` | OAuth refresh token (auto-refreshed) |
| `{brand}_ig_session.json` | Instagram session per brand (device + cookies via instagrapi) |
| `{brand}_tiktok_cookies.json` | TikTok cookies per brand, exported from the Chrome profile |
| `publications.jsonl` | publication ledger |

Brand config contract: each brand resolves its own accounts via
`{BRAND}_IG_USERNAME`, `{BRAND}_IG_PASSWORD`, `{BRAND}_TIKTOK_USERNAME`,
`{BRAND}_YOUTUBE_HANDLE` (see `publisher/social_influence/brandconfig.py`).
A bundle's `brand` selects the config; providers refuse to publish if the
authenticated account doesn't match the brand's configured account.

## Authentication per platform

### YouTube (Data API v3, no app-review blocking)

1. In Google Cloud (project `gutkitchen-publisher`, account
   `brands.sgill@gmail.com`): YouTube Data API v3 is enabled; OAuth consent is
   **External/Testing** with that account as test user; a **Desktop app**
   OAuth client exists.
2. One-time token bootstrap:
   ```bash
   .venv/bin/python scripts/youtube_auth.py &
   # open the printed URL in the brands.sgill@gmail.com Chrome profile,
   # choose the account, Continue → select all scopes → Continue
   ```
3. Tokens persist at `~/.social-influence/google_token.json` and refresh
   automatically on every publish. Re-auth only if revoked: delete the file
   and repeat step 2.

### Instagram (instagrapi, no Meta App Review)

Credentials from `.env` (`GUTKITCHEN_IG_USERNAME` / `GUTKITCHEN_IG_PASSWORD`).
First use logs in and persists device+session to `~/.social-influence/ig_session.json`;
later publishes reuse it without re-login (verified). If a session is
invalidated (`login_required` / challenge), delete the brand's `_ig_session.json` and let
the next publish re-login. If Instagram throws a verification challenge,
complete it manually in the GutKitchen Chrome profile first, then retry.

### TikTok (cookie session, no Content Posting API audit)

1. In the GutKitchen Chrome profile (`brands.sgill@gmail.com`), be logged in
   to `@gutkitchen.uk` at tiktok.com.
2. Export cookies (Playwriter session bound to that profile):
   ```bash
   playwriter -s <session> -e 'state.page = context.pages().find(p => p.url().includes("tiktok.com")) ?? (await context.newPage()); await state.page.goto("https://www.tiktok.com/explore"); await import("<repo>/publisher/scripts/...")'
   ```
   or inline: `getCDPSession({ page })` + `Network.getCookies` for tiktok.com
   → write JSON to `~/.social-influence/gutkitchen_tiktok_cookies.json`
   (the script `publisher/scripts/tiktok-cookie-export.js` documents this).
3. Session validity = `sessionid` cookie present. If uploads start failing
   with session errors, re-export the cookies.

## Publishing

```bash
# one PostBundle → selected platforms (per-platform isolation)
.venv/bin/social-influence publish ../posts/gutkitchen-001 \
  --brand gutkitchen --platforms youtube,tiktok,instagram

# validate without publishing
.venv/bin/social-influence publish ../posts/gutkitchen-001 --dry-run

# publication ledger
.venv/bin/social-influence status
```

Guarantees:
- per-platform isolation: a TikTok failure never blocks/duplicates YouTube or Instagram
- ledger-backed dedupe: re-running a bundle skips (post_id, platform) pairs already published
- retries only for transient failures (network/5xx), exponential backoff
- account guard: refuses to publish if the authenticated account doesn't
  match `GUTKITCHEN_YT_HANDLE` / `GUTKITCHEN_IG_USERNAME` / `GUTKITCHEN_TT_USERNAME`

Optional API (bearer-token protected):
```bash
# SOCIAL_INFLUENCE_API_TOKEN must be set in .env — without it /publish returns 503
uvicorn social_influence.api:app --port 8756
curl -X POST http://localhost:8756/publish \
  -H "Authorization: Bearer $SOCIAL_INFLUENCE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bundle": "../posts/gutkitchen-001", "platforms": ["youtube","tiktok"]}'
```
Bundle paths are allow-listed to `SOCIAL_INFLUENCE_ALLOWED_ROOTS` (default: the
repo's `posts/` directory) — the API cannot publish arbitrary host files.

## PostBundle

Platform-agnostic; media format is not fixed (adapters choose video/image
upload modes). See `publisher/social_influence/bundle.py`:

```json
{
  "brand": "gutkitchen",
  "post_id": "gutkitchen-001",
  "title": "...",                        // title where relevant (YouTube)
  "caption": "...",                      // caption/description
  "hashtags": ["highfibre", "guthealth"],
  "assets": [
    { "path": "fibre-upgrades.mp4", "type": "video", "role": "primary" },
    { "path": "cover.jpg", "type": "image", "role": "cover" }
  ],
  "visibility": "public",                // public | unlisted | private
  "aigc": true,                          // AI-generated-content disclosure
  "platforms": ["youtube", "tiktok", "instagram"]
}
```

Platform mapping:
- YouTube: video asset → Short (vertical ≤60s, `#Shorts`), title + description
- TikTok: video asset → public video; `unlisted`→`friends`, `private`→`only_you` (lossy — TikTok has no unlisted)
- Instagram: video → Reel, image → feed photo; cover asset → thumbnail

## Hosting on the old Mac (after the local test)

The publisher is plain Python + ffmpeg and runs anywhere. TikTok/Instagram
session automation behaves best from a residential/browser environment, so
the old Mac over Tailscale is the intended host:

1. Clone the repo, `uv venv && uv pip install -e .` inside `publisher/`.
2. Copy `~/.social-influence/` state to that machine (or re-auth there).
3. Run as a launchd agent (keepalive, `/publisher` as cwd):
   `uvicorn social_influence.api:app --host 0.0.0.0 --port 8756` behind
   Tailscale, or keep using the CLI directly from the creation engine.
4. Keep state dir on the same machine as the browser session exports.

## Observed fragility

- TikTok upload has no API-returned post id; the ledger records the account
  URL and the per-post link is filled during browser verification.
- instagrapi cannot generate thumbnails without MoviePy/ffmpeg wiring — the
  bundle should carry a `cover` asset (we always supply one).
- Instagram accounts younger than the first publish may draw extra scrutiny;
  if a challenge appears, complete it manually in the Chrome profile, then retry.
- YouTube OAuth client is unverified (Testing, 100-user cap) — fine for internal use.
