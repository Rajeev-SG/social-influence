"""Instagram provider — instagrapi (subzeroid/instagrapi).

Private-API publishing for accounts we own; avoids Meta App Review entirely.

Auth model:
- Per-brand credentials resolve via brandconfig: {BRAND}_IG_USERNAME /
  {BRAND}_IG_PASSWORD (env or .env, gitignored).
- Device + session state persist at $SOCIAL_INFLUENCE_STATE_DIR/{brand}_ig_session.json.
  Repeat publishes rehydrate that session WITHOUT a password login; a fresh
  password login happens only when the session is invalid.

Publishing modes (chosen from the PostBundle, not a fixed media format):
- video asset  -> clip_upload (Reel)
- image asset  -> photo_upload (feed post)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .. import brandconfig
from ..bundle import PostBundle
from .base import (
    PermanentError,
    PublishResult,
    SessionExpired,
    TransientError,
    classify_exception,
    state_dir,
)


def _session_path(brand: str) -> Path:
    return state_dir() / brandconfig.ig_session_name(brand)


def _dotenv_path() -> Path:
    return Path(os.environ.get("SOCIAL_INFLUENCE_DOTENV", ".env"))


def _credentials(brand: str) -> tuple[str, str]:
    from dotenv import get_key

    username = os.environ.get(f"{brand.upper().replace('-', '_')}_IG_USERNAME") or get_key(
        _dotenv_path(), f"{brand.upper().replace('-', '_')}_IG_USERNAME"
    )
    password = brandconfig.instagram_password(brand) or get_key(_dotenv_path(), "GUTKITCHEN_IG_PASSWORD")
    if not username or not password:
        raise PermanentError(
            f"Instagram credentials for brand '{brand}' missing. Set "
            f"{brand.upper().replace('-', '_')}_IG_USERNAME / {brand.upper().replace('-', '_')}_IG_PASSWORD in .env "
            "(gitignored). See docs/PUBLISHING.md §Instagram auth."
        )
    return username, password


def _client():
    from instagrapi import Client

    cl = Client()
    cl.delay_range = [2, 6]
    return cl


def ig_login(brand: str) -> tuple[object, str]:
    """Return (authenticated Client, username) for this brand.

    Rehydrates the persisted session WITHOUT a password login on every publish;
    falls back to a fresh password login only when the session is invalid.
    """
    username, password = _credentials(brand)
    expected = brandconfig.expected_account(brand, "instagram") or username

    cl = _client()
    session_path = _session_path(brand)
    if session_path.exists():
        try:
            cl.load_settings(str(session_path))
            cl.get_timeline_feed()  # validate the rehydrated session — no password used
            got = cl.account_info().username.lower()
            if got != expected.lower():
                raise PermanentError(
                    f"Instagram session is for '{got}', expected '{expected}'. "
                    "Refusing to publish to the wrong account."
                )
            print("  instagram: reusing persisted session (no password login)")
            return cl, got
        except PermanentError:
            raise
        except Exception as e:
            print(f"  instagram: persisted session invalid ({type(e).__name__}) — re-login required")

    # Only here: fresh password login (first publish, or session invalidated)
    cl = _client()
    cl.login(username, password)
    if cl.username is None:
        raise SessionExpired("Instagram password login failed — check credentials or complete any challenge in the browser.")
    got = cl.username.lower()
    if got != expected.lower():
        raise PermanentError(
            f"Instagram login is for '{got}', expected '{expected}'. "
            "Refusing to publish to the wrong account."
        )
    session_path.write_text(json.dumps(cl.get_settings()))
    print("  instagram: fresh password login complete — session persisted")
    return cl, got


def upload(bundle: PostBundle) -> PublishResult:
    video = bundle.primary_video()
    image = bundle.primary_image()
    if video is None and image is None:
        return PublishResult("instagram", False, error="Bundle has no video or image asset", visibility=bundle.visibility)

    try:
        cl, _ = ig_login(bundle.brand)
    except Exception as e:
        kind = classify_exception(e)
        if kind is PermanentError and "expected" in str(e):
            raise
        return PublishResult("instagram", False, error=f"{type(e).__name__}: {e}", visibility=bundle.visibility)

    caption = bundle.caption_with_hashtags()
    cover = bundle.cover()
    cover_path = str(cover.path) if cover else None

    try:
        if video is not None:
            media = cl.clip_upload(str(video.path), caption=caption, thumbnail=cover_path)
        else:
            media = cl.photo_upload(str(image.path), caption=caption)
        return PublishResult(
            "instagram",
            True,
            post_id=str(media.pk),
            url=f"https://www.instagram.com/p/{media.code}/",
            visibility=bundle.visibility,
        )
    except Exception as e:
        kind = classify_exception(e)
        if kind is TransientError:
            return PublishResult("instagram", False, error=f"TransientError: {e}", visibility=bundle.visibility)
        return PublishResult("instagram", False, error=f"{type(e).__name__}: {e}", visibility=bundle.visibility)