"""TikTok provider — browser/session-based publishing for accounts we own.

Deliberately NOT the official Content Posting API: that requires an app audit
for public posting. Primary implementation uses YanivGabay/tiktok-uploader
(Selenium against tiktok.com's own upload UI) driven by session cookies
exported from the GutKitchen Chrome profile via CDP.

Auth model:
- Cookies: $SOCIAL_INFLUENCE_STATE_DIR/tiktok_cookies.json (exported, gitignored)
- Export procedure: docs/PUBLISHING.md §TikTok auth (uses Playwriter + CDP).

Verification: after upload we re-read the profile grid with the same session
and capture the newly appeared video id + canonical post URL. If verification
cannot confirm (anti-bot page, timeout), the result is still recorded but
flagged `verified: false` so ledger consumers never mistake it for
confirmed-public.

Visibility mapping (TikTok has no 'unlisted'):
  public -> everyone | unlisted -> friends | private -> only_you

Fallback candidates if this lib breaks:
- makiisthenes/TiktokAutoUploader (session/web-endpoint based)
- a small Playwright publisher against tiktok.com/upload
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from .. import brandconfig
from ..bundle import PostBundle
from .base import (
    PermanentError,
    PublishResult,
    SessionExpired,
    state_dir,
)

VIS_MAP = {"public": "everyone", "unlisted": "friends", "private": "only_you"}

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def _cookies_path(brand: str) -> Path:
    p = state_dir() / brandconfig.tiktok_cookies_name(brand)
    if not p.exists():
        raise PermanentError(
            f"Missing {p}. Export TikTok cookies from this brand's Chrome profile "
            "(see docs/PUBLISHING.md §TikTok auth)."
        )
    return p


def _load_cookies(brand: str) -> list[dict]:
    raw = json.loads(_cookies_path(brand).read_text())
    cookies = [
        {"name": c["name"], "value": c["value"], "domain": c.get("domain", ""), "path": c.get("path", "/")}
        for c in raw
    ]
    if not any(c["name"] == "sessionid" for c in cookies):
        raise SessionExpired("TikTok cookies lack a sessionid — session expired. Re-export (docs §TikTok auth).")
    return cookies


def _latest_video_id(cookies: list[dict], handle: str) -> str | None:
    """Best-effort scrape of the newest video id on our own profile grid."""
    import requests

    sess = requests.Session()
    for c in cookies:
        sess.cookies.set(c["name"], c["value"], domain=c.get("domain") or ".tiktok.com")
    try:
        resp = sess.get(
            f"https://www.tiktok.com/@{handle}",
            timeout=30,
            headers={"User-Agent": _UA},
        )
        m = re.search(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
            resp.text,
            re.S,
        )
        if not m:
            return None
        data = json.loads(m.group(1))

        def find_item_list(node):
            if isinstance(node, dict):
                if "itemList" in node and isinstance(node["itemList"], list):
                    return node["itemList"]
                for v in node.values():
                    found = find_item_list(v)
                    if found is not None:
                        return found
            elif isinstance(node, list):
                for v in node:
                    found = find_item_list(v)
                    if found is not None:
                        return found
            return None

        items = find_item_list(data)
        if items:
            return str(items[0].get("id")) if items[0].get("id") else None
    except Exception:
        return None
    return None


def _verify_new_post(cookies: list[dict], handle: str, before_id: str | None, timeout_s: int = 90) -> str | None:
    """Poll the profile for a video id different from `before_id`. Returns id or None."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        latest = _latest_video_id(cookies, handle)
        if latest and latest != before_id:
            return latest
        time.sleep(10)
    return None


def upload(bundle: PostBundle) -> PublishResult:
    from tiktok_uploader.upload import upload_video

    asset = bundle.primary_video()
    if asset is None:
        return PublishResult("tiktok", False, error="TikTok requires a video asset; bundle has none", visibility=bundle.visibility)

    handle = brandconfig.expected_account(bundle.brand, "tiktok")
    if not handle:
        raise PermanentError(
            f"No TikTok account configured for brand '{bundle.brand}'. Set "
            f"{bundle.brand.upper().replace('-', '_')}_TIKTOK_USERNAME."
        )
    cookies = _load_cookies(brand=bundle.brand)
    description = bundle.caption_with_hashtags()[:2200]
    if bundle.aigc:
        description += " AIGC-assisted"  # honest disclosure for TikTok's AIGC labelling rules

    before_id = _latest_video_id(cookies, handle)
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
    except Exception as e:
        msg = str(e).lower()
        if any(k in msg for k in ("captcha", "challenge", "login", "session", "cookie")):
            return PublishResult("tiktok", False, error=f"SessionExpired: {e}", visibility=bundle.visibility)
        return PublishResult("tiktok", False, error=f"{type(e).__name__}: {e}", visibility=bundle.visibility)

    post_id = _verify_new_post(cookies, handle, before_id)
    if post_id:
        return PublishResult(
            "tiktok",
            True,
            post_id=post_id,
            url=f"https://www.tiktok.com/@{handle}/video/{post_id}",
            visibility=bundle.visibility,
            verified=True,
        )
    # Upload flow reported success but the grid did not confirm in time.
    # Record honestly as unverified so downstream never mistakes it for live.
    return PublishResult(
        "tiktok",
        True,
        post_id=None,
        url=None,
        error=None,
        visibility=bundle.visibility,
        verified=False,
    )