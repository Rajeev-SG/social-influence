"""PostBundle: the stable boundary between the creation engine and publishers.

A PostBundle is platform-agnostic. Each provider adapter translates it into
whatever the target platform actually requires. Media format is not fixed:
assets may be videos or images; adapters pick the right upload mode.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VALID_VISIBILITY = ("public", "unlisted", "private")


@dataclass
class Asset:
    path: Path
    type: str  # "video" | "image"
    role: str = "primary"  # "primary" | "thumbnail" | "cover"

    def resolved(self, base: Path) -> "Asset":
        p = Path(self.path)
        if not p.is_absolute():
            p = (base / p).resolve()
        return Asset(p, self.type, self.role)


@dataclass
class PostBundle:
    brand: str
    post_id: str
    caption: str = ""
    title: str | None = None
    hashtags: list[str] = field(default_factory=list)
    assets: list[Asset] = field(default_factory=list)
    visibility: str = "public"
    aigc: bool = False  # AI-generated-content flag, surfaced where platforms require disclosure
    platforms: list[str] = field(default_factory=lambda: ["youtube", "tiktok", "instagram"])
    extra: dict[str, Any] = field(default_factory=dict)

    def primary_video(self) -> Asset | None:
        for a in self.assets:
            if a.type == "video" and a.role == "primary":
                return a
        return next((a for a in self.assets if a.type == "video"), None)

    def primary_image(self) -> Asset | None:
        for a in self.assets:
            if a.type == "image" and a.role == "primary":
                return a
        return next((a for a in self.assets if a.type == "image"), None)

    def cover(self) -> Asset | None:
        return next((a for a in self.assets if a.role in ("thumbnail", "cover")), None)

    def caption_with_hashtags(self) -> str:
        tags = " ".join(f"#{t.lstrip('#')}" for t in self.hashtags)
        body = self.caption.strip()
        return f"{body}\n\n{tags}".strip()


def load_bundle(path: str | Path) -> PostBundle:
    """Load a bundle from a JSON file or a directory containing bundle.json."""
    p = Path(path).expanduser()
    base = p
    if p.is_dir():
        p = p / "bundle.json"
    if not p.exists():
        raise FileNotFoundError(f"No bundle found at {p}")
    raw = json.loads(p.read_text())
    assets = [Asset(Path(a["path"]), a.get("type", "video"), a.get("role", "primary")) for a in raw.get("assets", [])]
    bundle = PostBundle(
        brand=raw["brand"],
        post_id=raw["post_id"],
        caption=raw.get("caption", ""),
        title=raw.get("title"),
        hashtags=raw.get("hashtags", []),
        assets=assets,
        visibility=raw.get("visibility", "public"),
        aigc=bool(raw.get("aigc", False)),
        platforms=raw.get("platforms", ["youtube", "tiktok", "instagram"]),
        extra=raw.get("extra", {}),
    )
    bundle.assets = [a.resolved(base if base.is_dir() else base.parent) for a in bundle.assets]
    for a in bundle.assets:
        if not a.path.exists():
            raise FileNotFoundError(f"Asset missing: {a.path}")
    return bundle