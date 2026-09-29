"""Shared provider plumbing: results, errors, session-state locations."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

PLATFORMS = ("youtube", "tiktok", "instagram")

# All reusable auth/session state lives under one directory OUTSIDE the repo.
# Override with SOCIAL_INFLUENCE_STATE_DIR in .env / environment.
def state_dir() -> Path:
    root = os.environ.get("SOCIAL_INFLUENCE_STATE_DIR", "~/.social-influence")
    p = Path(root).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


@dataclass
class PublishResult:
    platform: str
    success: bool
    post_id: str | None = None
    url: str | None = None
    error: str | None = None
    visibility: str = "public"
    verified: bool = True  # False = uploader reported success but platform not confirmed

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "success": self.success,
            "post_id": self.post_id,
            "url": self.url,
            "error": self.error,
            "visibility": self.visibility,
            "verified": self.verified,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }


class SessionExpired(Exception):
    """Raised when stored auth state can no longer be used; triggers re-auth docs."""


class TransientError(Exception):
    """Retryable failure (network blip, rate limit with backoff)."""


class PermanentError(Exception):
    """Non-retryable failure (policy, bad asset, challenge)."""


def classify_exception(exc: Exception) -> type:
    if isinstance(exc, (SessionExpired, PermanentError)):
        return PermanentError
    if isinstance(exc, TransientError):
        return TransientError
    name = type(exc).__name__.lower()
    text = str(exc).lower()
    if any(k in text for k in ("timeout", "connection", "503", "429", "500", "temporarily")):
        return TransientError
    if any(k in text for k in ("challenge", "captcha", "login_required", "consent", "permission")):
        return SessionExpired if "login" in text else PermanentError
    return PermanentError