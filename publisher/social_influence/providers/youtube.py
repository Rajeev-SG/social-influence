"""YouTube provider — official YouTube Data API v3 with our own OAuth client.

Auth model (personal/internal app, no public OAuth verification needed):
- OAuth client secret: $SOCIAL_INFLUENCE_STATE_DIR/google_oauth_client.json
- Refresh token:       $SOCIAL_INFLUENCE_STATE_DIR/google_token.json
Interactive consent reuses the brands.sgill@gmail.com Chrome session.

https://github.com/Rajeev-SG/social-influence — Issue #2.
"""

from __future__ import annotations

import json
import os
import random
import time
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

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
]

# The channel we must publish to. Guard against publishing to the wrong account.
EXPECTED_HANDLE = os.environ.get("GUTKITCHEN_YT_HANDLE", "thegutkitchen")


def _client_secret_path() -> Path:
    p = state_dir() / "google_oauth_client.json"
    if not p.exists():
        raise PermanentError(
            f"Missing {p}. Create a Google Cloud OAuth desktop client and save it there. "
            "See docs/PUBLISHING.md §YouTube auth."
        )
    return p


def _token_path() -> Path:
    return state_dir() / "google_token.json"


def youtube_client():
    """Return an authorized YouTube API client, refreshing tokens as needed."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    token_path = _token_path()
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:  # refresh token revoked / expired
            raise SessionExpired(f"Google token refresh failed: {e}") from e
    elif creds is None or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(_client_secret_path()), SCOPES)
        # Opens local browser for consent; reuse the logged-in Chrome session.
        creds = flow.run_local_server(port=0, open_browser=True)
        token_path.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def verify_channel(service) -> str:
    """Return the handle of the authenticated channel, verifying it matches EXPECTED_HANDLE."""
    resp = service.channels().list(part="snippet", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise SessionExpired("No YouTube channel on this Google account — is the right account logged in?")
    sn = items[0]["snippet"]
    custom = sn.get("customUrl", "")
    if EXPECTED_HANDLE not in custom.lstrip("@"):
        raise PermanentError(
            f"Authenticated YouTube channel is '{custom}', expected '@{EXPECTED_HANDLE}'. "
            "Refusing to publish to the wrong account. Fix GUTKITCHEN_YT_HANDLE or re-auth."
        )
    return custom


def upload(bundle: PostBundle) -> PublishResult:
    from googleapiclient.http import MediaFileUpload

    asset = bundle.primary_video()
    if asset is None:
        return PublishResult("youtube", False, error="YouTube requires a video asset; bundle has none", visibility=bundle.visibility)

    service = youtube_client()
    verify_channel(service)

    desc = bundle.caption_with_hashtags()
    if bundle.aigc:
        desc += "\n\n[AIGC] Visuals generated with AI-assisted tooling."
    if "#shorts" not in desc.lower() and "shorts" not in bundle.hashtags:
        desc += " #Shorts"

    body = {
        "snippet": {
            "title": (bundle.title or bundle.brand)[:100],
            "description": desc[:4900],
            "tags": [t.lstrip("#") for t in bundle.hashtags][:30],
            "categoryId": "26",  # Howto & Style
        },
        "status": {
            "privacyStatus": bundle.visibility if bundle.visibility in ("public", "unlisted", "private") else "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(asset.path), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")

    last_err: Exception | None = None
    for attempt in range(4):
        try:
            request = service.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"  youtube upload: {int(status.progress() * 100)}%")
            vid = response["id"]
            return PublishResult(
                "youtube",
                True,
                post_id=vid,
                url=f"https://www.youtube.com/watch?v={vid}",
                visibility=body["status"]["privacyStatus"],
            )
        except Exception as e:
            kind = classify_exception(e)
            last_err = e
            if kind is TransientError and attempt < 3:
                # resumable upload continues from where it left off
                time.sleep((2**attempt) + random.random())
                continue
            break

    msg = str(last_err)
    if "invalid_grant" in msg or "UnauthorizedClient" in msg:
        err = SessionExpired(msg)
    elif kind is TransientError:
        err = TransientError(msg)
    else:
        err = PermanentError(msg)
    return PublishResult("youtube", False, error=f"{type(err).__name__}: {err}", visibility=bundle.visibility)