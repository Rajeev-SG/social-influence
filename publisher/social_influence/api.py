"""Optional local API wrapper around the publishing CLI.

POST /publish  {"bundle": "./posts/gutkitchen-001", "platforms": ["youtube","tiktok"]}

Security model:
- Bearer-token auth: set SOCIAL_INFLUENCE_API_TOKEN in .env / environment;
  requests must carry `Authorization: Bearer <token>`. 401 otherwise.
- Bundle paths are allow-listed: only paths under SOCIAL_INFLUENCE_ALLOWED_ROOTS
  (default: the repo's `posts/` directory) resolve and are publishable.
- Unknown platforms are rejected, not silently dropped.

Run:  .venv/bin/uvicorn social_influence.api:app --port 8756
For remote (Tailscale) use the token is mandatory — see docs/PUBLISHING.md §Hosting.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .bundle import load_bundle
from .cli import publish_bundle
from .providers.base import PLATFORMS

app = FastAPI(title="social-influence publisher", version="0.1.0")


def allowed_roots() -> list[Path]:
    raw = os.environ.get("SOCIAL_INFLUENCE_ALLOWED_ROOTS", "")
    roots = [Path(r).expanduser().resolve() for r in raw.split(":") if r.strip()]
    if not roots:
        roots = [(Path(__file__).resolve().parent.parent.parent / "posts").resolve()]
    return roots


def _require_token(authorization: str = Header(default="")) -> None:
    expected = os.environ.get("SOCIAL_INFLUENCE_API_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="SOCIAL_INFLUENCE_API_TOKEN is not set; the publish API is disabled. "
            "Set a strong token in .env to enable it.",
        )
    supplied = authorization.removeprefix("Bearer ").strip()
    if not supplied or supplied != expected:
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")


class PublishRequest(BaseModel):
    bundle: str = Field(..., description="path to bundle.json or bundle directory (must be under an allowed root)")
    platforms: list[str] = Field(default_factory=lambda: ["youtube", "tiktok", "instagram"])
    dry_run: bool = False


def _resolve_bundle(bundle_path: str) -> Path:
    p = Path(bundle_path).expanduser()
    resolved = (p if p.is_absolute() else (Path.cwd() / p)).resolve()
    roots = allowed_roots()
    if not any(resolved == r or r in resolved.parents for r in roots):
        raise HTTPException(
            status_code=403,
            detail=f"bundle path outside allowed roots: {[str(r) for r in roots]}",
        )
    return resolved


@app.post("/publish", dependencies=[Depends(_require_token)])
def publish(req: PublishRequest):
    unknown = [p for p in req.platforms if p not in PLATFORMS]
    if unknown:
        raise HTTPException(status_code=400, detail=f"unknown platforms: {unknown}; known: {PLATFORMS}")
    resolved = _resolve_bundle(req.bundle)
    try:
        bundle = load_bundle(resolved)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    results = publish_bundle(str(resolved), req.platforms, dry_run=req.dry_run)
    return {
        "bundle": {"brand": bundle.brand, "post_id": bundle.post_id},
        "dry_run": req.dry_run,
        "results": [r.to_dict() for r in results],
    }


@app.get("/health")
def health():
    return {"ok": True}