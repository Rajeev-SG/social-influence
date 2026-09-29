"""Instagram provider — instagrapi (subzeroid/instagrasi -> subzeroid/instagrapi).

Private-API publishing for accounts we own; avoids Meta App Review entirely.

Auth model:
- Credentials come from env (GUTKITCHEN_IG_USERNAME / GUTKITCHEN_IG_PASSWORD, via .env).
- Device + session state persist at $SOCIAL_INFLUENCE_STATE_DIR/ig_session.json so
  repeat publishes never re-login. Re-login only if the session is invalidated.

Publishing modes (chosen from the PostBundle, not a fixed media format):
- video asset  -> clip_upload (Reel)
- image asset  -> photo_upload (feed post)
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
    TransientError,
    classify_exception,
    state_dir,
)

EXPECTED_USERNAME = os.environ.get("GUTKITCHEN_IG_USERNAME", "gutkitchen.uk")


def _session_path() -> Path:
    return state_dir() / "ig_session.json"


def _client():
    from instagrapi import Client

    cl = Client()
    cl.delay_range = [2, 6]
    return cl


def ig_login():
    """Return an authenticated instagrapi Client.

    Rehydrates the persisted session WITHOUT a password login on every publish;
    falls back to a fresh password login only when the session is invalid.
    """
    from dotenv import get_key

    username = os.environ.get("GUTKITCHEN_IG_USERNAME") or get_key(_dotenv_path(), "GUTKITCHEN_IG_USERNAME")
    password = os.environ.get("GUTKITCHEN_IG_PASSWORD") or get_key(_dotenv_path(), "GUTKITCHEN_IG_PASSWORD")
    if not username or not password:
        raise PermanentError(
            "Instagram credentials missing. Put GUTKITCHEN_IG_USERNAME / GUTKITCHEN_IG_PASSWORD in .env "
            "(gitignored). See docs/PUBLISHING.md §Instagram auth."
        )

    cl = _client()
    session_path = _session_path()
    if session_path.exists():
        try:
            cl.load_settings(str(session_path))
            cl.get_timeline_feed()  # validate the rehydrated session — no password used
            print("  instagram: reusing persisted session (no password login)")
            return cl
        except Exception as e:
            print(f"  instagram: persisted session invalid ({type(e).__name__}) — re-login required")

    # Only here: fresh password login (first publish, or session invalidated)
    cl = _client()
    cl.login(username, password)
    if cl.username is None:
        raise SessionExpired("Instagram password login failed — check credentials or complete any challenge in the browser.")
    if cl.username.lower() != EXPECTED_USERNAME.lower():
        raise PermanentError(
            f"Instagram login is for '{cl.username}', expected '{EXPECTED_USERNAME}'. "
            "Refusing to publish to the wrong account."
        )
    session_path.write_text(json.dumps(cl.get_settings()))
    print("  instagram: fresh password login complete — session persisted")
    return cl


def _dotenv_path() -> Path:
    return Path(os.environ.get("SOCIAL_INFLUENCE_DOTENV", ".env"))


def upload(bundle: PostBundle) -> PublishResult:
    video = bundle.primary_video()
    image = bundle.primary_image()
    if video is None and image is None:
        return PublishResult("instagram", False, error="Bundle has no video or image asset", visibility=bundle.visibility)

    try:
        cl = ig_login()
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
            post_id=media.pk,
            url=f"https://www.instagram.com/p/{media.code}/",
            visibility=bundle.visibility,
        )
    except Exception as e:
        kind = classify_exception(e)
        if kind is TransientError:
            return PublishResult("instagram", False, error=f"TransientError: {e}", visibility=bundle.visibility)
        return PublishResult("instagram", False, error=f"{type(e).__name__}: {e}", visibility=bundle.visibility)