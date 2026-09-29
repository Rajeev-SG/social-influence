"""Per-brand platform configuration.

A PostBundle carries `brand`; every provider resolves credentials, session
files and the expected account through this module so a bundle for any brand
publishes to that brand's accounts (never another brand's session).

Env contract (BRAND upper-cased, dashes -> underscores):
    {BRAND}_{PLATFORM}_USERNAME   expected account handle (wrong-account guard)
    {BRAND}_IG_PASSWORD           Instagram password (instagram only)
    {BRAND}_YOUTUBE_HANDLE        legacy alias for the YouTube handle
Legacy gutkitchen-specific names (GUTKITCHEN_IG_USERNAME, GUTKITCHEN_TT_USERNAME,
GUTKITCHEN_YT_HANDLE) are accepted as fallbacks for backwards compatibility.
"""

from __future__ import annotations

import os

PLATFORM_KEYS = {"youtube": ("YOUTUBE_HANDLE", "YT_HANDLE"), "tiktok": ("TIKTOK_USERNAME", "TT_USERNAME"), "instagram": ("IG_USERNAME", "IG_USERNAME")}


def _prefix(brand: str) -> str:
    return brand.upper().replace("-", "_")


def expected_account(brand: str, platform: str) -> str:
    """The account handle we must be publishing as for this brand+platform."""
    prefix = _prefix(brand)
    primary, alias = PLATFORM_KEYS[platform]
    return (
        os.environ.get(f"{prefix}_{primary}")
        or os.environ.get(f"{prefix}_{alias}")
        or ""
    )


def instagram_password(brand: str) -> str:
    prefix = _prefix(brand)
    return os.environ.get(f"{prefix}_IG_PASSWORD") or os.environ.get("GUTKITCHEN_IG_PASSWORD") or ""


def ig_session_name(brand: str) -> str:
    return f"{_prefix(brand).lower()}_ig_session.json"


def tiktok_cookies_name(brand: str) -> str:
    return f"{_prefix(brand).lower()}_tiktok_cookies.json"
