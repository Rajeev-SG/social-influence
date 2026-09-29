"""Publication ledger: append-only JSONL, one record per publish attempt.

Purpose:
- proof of record for every publish (content id, platform, ts, status, url)
- duplicate prevention: a provider is skipped if post_id already has a
  successful record for that platform
Lives in the repo's state dir / publications.jsonl — gitignored.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .providers.base import state_dir


def _ledger_path() -> Path:
    env = os.environ.get("SOCIAL_INFLUENCE_LEDGER", "")
    return Path(env).expanduser() if env else (state_dir() / "publications.jsonl")


def record(result, content_id: str | None = None) -> None:
    entry = result.to_dict()
    entry["content_id"] = content_id or entry["post_id"]
    with _ledger_path().open("a") as f:
        f.write(json.dumps(entry) + "\n")


def already_published(content_id: str, platform: str) -> bool:
    """True once any successful record exists for (content_id, platform).

    Matches either the creation-engine content id (bundle post_id) or a
    platform post id recorded earlier for the same content.
    """
    path = _ledger_path()
    if not path.exists():
        return False
    for line in path.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("platform") != platform or not e.get("success"):
            continue
        if e.get("content_id") == content_id or e.get("post_id") == content_id:
            return True
    return False


def read_all() -> list[dict]:
    path = _ledger_path()
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out