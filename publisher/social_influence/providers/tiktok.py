"""TikTok provider — browser/session-based publishing for accounts we own.

Deliberately NOT the official Content Posting API: that requires an app audit
for public posting. Primary implementation uses YanivGabay/tiktok-uploader
(Selenium against tiktok.com's own upload UI) driven by session cookies
exported from the GutKitchen Chrome profile via CDP.

Auth model:
- Cookies: $SOCIAL_INFLUENCE_STATE_DIR/tiktok_cookies.json (exported, gitignored)
- Export procedure: docs/PUBLISHING.md §TikTok auth (uses Playwriter + CDP).

Visibility mapping (TikTok has no 'unlisted'):
  public -> everyone | unlisted -> friends | private -> only_you
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ..bundle import PostBundle
from .base import (
    PermanentError,
    PublishResult,
    SessionExpired,
    state_dir,
)

EXPECTED_HANDLE = os.environ.get("GUTKITCHEN_TT_USERNAME", "gutkitchen.uk")

VIS_MAP = {"public": "everyone", "unlisted": "friends", "private": "only_you"}


def _cookies_path() -> Path:
    p = state_dir() / "tiktok_cookies.json"
    if not p.exists():
        raise PermanentError(
            f"Missing {p}. Export TikTok cookies from the GutKitchen Chrome profile "
            "(see docs/PUBLISHING.md §TikTok auth)."
        )
    return p


def _load_cookies() -> list[dict]:
    raw = json.loads(_cookies_path().read_text())
    cookies = [
        {"name": c["name"], "value": c["value"], "domain": c.get("domain", ""), "path": c.get("path", "/")}
        for c in raw
    ]
    if not any(c["name"] == "sessionid" for c in cookies):
        raise SessionExpired("TikTok cookies lack a sessionid — session expired. Re-export (docs §TikTok auth).")
    return cookies


def upload(bundle: PostBundle) -> PublishResult:
    from tiktok_uploader.upload import upload_video

    asset = bundle.primary_video()
    if asset is None:
        return PublishResult("tiktok", False, error="TikTok requires a video asset; bundle has none", visibility=bundle.visibility)

    cookies = _load_cookies()
    description = bundle.caption_with_hashtags()[:2200]
    if bundle.aigc:
        description += " AIGC-assisted"  # honest disclosure for TikTok's AIGC labelling rules

    cover = bundle.cover()
    try:
        failed_videos = upload_video(
            str(asset.path),
            description=description,
            cookies_list=cookies,
            visibility=VIS_MAP.get(bundle.visibility, "everyone"),
            browser=os.environ.get("TIKTOK_BROWSER", "chrome"),
            headless=os.environ.get("TIKTOK_HEADLESS", "0") == "1",
            cover=str(cover.path) if cover else None,
        )
        if failed_videos:
            return PublishResult("tiktok", False, error=f"Upload rejected: {failed_videos}", visibility=bundle.visibility)
        # Selenium flow returns no post id; record the canonical account URL and
        # fill in the per-post link during post-publish verification.
        return PublishResult(
            "tiktok",
            True,
            post_id=None,
            url=f"https://www.tiktok.com/@{EXPECTED_HANDLE}",
            visibility=bundle.visibility,
        )
    except Exception as e:
        msg = str(e).lower()
        if any(k in msg for k in ("captcha", "challenge", "login", "session", "cookie")):
            return PublishResult("tiktok", False, error=f"SessionExpired: {e}", visibility=bundle.visibility)
        return PublishResult("tiktok", False, error=f"{type(e).__name__}: {e}", visibility=bundle.visibility)