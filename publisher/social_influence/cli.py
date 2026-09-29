"""social-influence publish — one PostBundle, selected platforms, isolated results.

Usage:
  social-influence publish ./posts/gutkitchen-001 --platforms youtube,tiktok,instagram
  social-influence publish ./posts/gutkitchen-001 --dry-run
  social-influence status

Each platform publishes or fails independently; a failure never blocks or
duplicates the others. Successful publishes are recorded in the ledger and
re-runs skip already-published (post_id, platform) pairs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .bundle import load_bundle
from .ledger import already_published, read_all, record
from .providers.base import PLATFORMS, PermanentError, PublishResult, TransientError


def _provider(platform: str):
    if platform == "youtube":
        from .providers import youtube

        return youtube
    if platform == "tiktok":
        from .providers import tiktok

        return tiktok
    if platform == "instagram":
        from .providers import instagram

        return instagram
    raise PermanentError(f"Unknown platform '{platform}'. Known: {', '.join(PLATFORMS)}")


def publish_bundle(bundle_path: str, platforms: list[str], dry_run: bool = False) -> list[PublishResult]:
    bundle = load_bundle(bundle_path)
    results: list[PublishResult] = []

    for platform in platforms:
        if platform not in PLATFORMS:
            results.append(PublishResult(platform, False, error=f"unknown platform; known: {PLATFORMS}"))
            continue
        if not dry_run and already_published(bundle.post_id, platform):
            print(f"  {platform}: already published — skipping (ledger)")
            results.append(PublishResult(platform, True, post_id=bundle.post_id, error=None))
            continue

        print(f"  {platform}: publishing post_id={bundle.post_id} visibility={bundle.visibility}")
        try:
            if dry_run:
                mod = _provider(platform)
                print(f"  {platform}: DRY-RUN would publish bundle to {platform}")
                results.append(PublishResult(platform, True, error=None, visibility=bundle.visibility))
                continue
            result = _provider(platform).upload(bundle)
        except (PermanentError, TransientError) as e:
            result = PublishResult(platform, False, error=str(e), visibility=bundle.visibility)
        except Exception as e:  # provider blew up outside its own guard
            result = PublishResult(platform, False, error=f"unhandled {type(e).__name__}: {e}", visibility=bundle.visibility)

        if result.success:
            print(f"  {platform}: OK {result.url or result.post_id}")
        else:
            print(f"  {platform}: FAILED — {result.error}")
        record(result)
        results.append(result)

    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="social-influence")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_pub = sub.add_parser("publish", help="publish a PostBundle to selected platforms")
    p_pub.add_argument("bundle", help="path to bundle.json or a bundle directory")
    p_pub.add_argument("--brand", default=None, help="override/confirm brand (must match bundle)")
    p_pub.add_argument("--platforms", default="youtube,tiktok,instagram", help="comma-separated subset")
    p_pub.add_argument("--dry-run", action="store_true", help="validate bundle + adapters without publishing")

    sub.add_parser("status", help="show publication ledger")

    args = ap.parse_args(argv)

    if args.cmd == "status":
        entries = read_all()
        print(json.dumps(entries, indent=2))
        return 0

    if args.cmd == "publish":
        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
        if args.brand:
            bundle = load_bundle(args.bundle)
            if bundle.brand != args.brand:
                print(f"error: bundle brand '{bundle.brand}' != --brand '{args.brand}'", file=sys.stderr)
                return 2
        results = publish_bundle(args.bundle, platforms, dry_run=args.dry_run)
        failed = [r for r in results if not r.success]
        print("\nsummary:")
        for r in results:
            print(f"  {r.platform:10s} {'OK ' if r.success else 'FAIL'} {(r.url or r.post_id or r.error or '')[:100]}")
        return 1 if failed and not args.dry_run else 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())