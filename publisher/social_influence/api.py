"""Optional local API wrapper around the publishing CLI.

POST /publish  {"bundle": "./posts/gutkitchen-001", "platforms": ["youtube","tiktok"]}

Run:  .venv/bin/uvicorn social_influence.api:app --port 8756
(Suitable for running over Tailscale on a residential machine — see docs/PUBLISHING.md §Hosting.)
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .bundle import load_bundle
from .cli import publish_bundle

app = FastAPI(title="social-influence publisher", version="0.1.0")


class PublishRequest(BaseModel):
    bundle: str = Field(..., description="path to bundle.json or bundle directory")
    platforms: list[str] = Field(default_factory=lambda: ["youtube", "tiktok", "instagram"])
    dry_run: bool = False


@app.post("/publish")
def publish(req: PublishRequest):
    try:
        bundle = load_bundle(req.bundle)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    results = publish_bundle(req.bundle, req.platforms, dry_run=req.dry_run)
    return {
        "bundle": {"brand": bundle.brand, "post_id": bundle.post_id},
        "dry_run": req.dry_run,
        "results": [r.to_dict() for r in results],
    }


@app.get("/health")
def health():
    return {"ok": True}