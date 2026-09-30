"""CLI and publishing-pipeline tests: platform parsing, dry-run, ledger dedupe,
per-platform isolation — all with mocked provider upload functions."""

import json
from pathlib import Path

import pytest

from social_influence.bundle import load_bundle
from social_influence.cli import publish_bundle
from social_influence.ledger import _ledger_path


def make_bundle(tmp_path: Path, post_id: str = "gutkitchen-001") -> Path:
    (tmp_path / "media.mp4").write_bytes(b"0")
    d = tmp_path / "bundle.json"
    d.write_text(json.dumps({
        "brand": "gutkitchen",
        "post_id": post_id,
        "caption": "c",
        "assets": [{"path": "media.mp4", "type": "video"}],
        "platforms": ["youtube", "tiktok", "instagram"],
        "visibility": "public",
    }))
    return d


@pytest.fixture
def isolated_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv("SOCIAL_INFLUENCE_LEDGER", str(tmp_path / "ledger.jsonl"))
    return tmp_path / "ledger.jsonl"


def _mock_provider(monkeypatch, platform: str, result, calls: list):
    """Patch the provider module's upload fn; record invocations."""
    import importlib

    mod = importlib.import_module(f"social_influence.providers.{platform}")

    def fake_upload(bundle):
        calls.append((platform, bundle.post_id))
        return result(platform)

    monkeypatch.setattr(mod, "upload", fake_upload)


def test_cli_platform_parsing(isolated_ledger, monkeypatch, tmp_path):
    bundle_path = make_bundle(tmp_path)
    calls: list = []
    from social_influence.providers.base import PublishResult

    for platform in ("youtube", "tiktok", "instagram"):
        _mock_provider(monkeypatch, platform, lambda p: PublishResult(p, True, post_id="x"), calls)
    results = publish_bundle(str(bundle_path), ["youtube", "tiktok"])
    assert [r.platform for r in results] == ["youtube", "tiktok"]
    assert all(r.success for r in results)
    assert sorted(p for p, _ in calls) == ["tiktok", "youtube"]


def test_cli_dry_run_publishes_nothing(isolated_ledger, monkeypatch, tmp_path):
    bundle_path = make_bundle(tmp_path)
    calls: list = []

    def fail_if_called(bundle):
        raise AssertionError("upload must not run in dry-run")

    for platform in ("youtube", "tiktok", "instagram"):
        mod = __import__(f"social_influence.providers.{platform}", fromlist=["upload"])
        monkeypatch.setattr(mod, "upload", fail_if_called)

    results = publish_bundle(str(bundle_path), ["youtube", "tiktok", "instagram"], dry_run=True)
    assert all(r.success for r in results)
    assert not isolated_ledger.exists()  # dry-run writes no ledger records


def test_ledger_dedupe_skips_published(isolated_ledger, monkeypatch, tmp_path):
    from social_influence.providers.base import PublishResult

    bundle_path = make_bundle(tmp_path)
    calls: list = []
    for platform in ("youtube", "tiktok", "instagram"):
        _mock_provider(monkeypatch, platform, lambda p: PublishResult(p, True, post_id="pid-1"), calls)

    publish_bundle(str(bundle_path), ["youtube", "instagram"])
    n_first = len(calls)
    results = publish_bundle(str(bundle_path), ["youtube", "instagram"])  # same bundle again
    assert len(calls) == n_first  # no second upload
    assert all(r.success for r in results)  # reported as already-published success


def test_tiktok_failure_does_not_duplicate_youtube(isolated_ledger, monkeypatch, tmp_path):
    from social_influence.providers.base import PublishResult

    bundle_path = make_bundle(tmp_path, post_id="iso-test")
    calls: list = []

    def ok_youtube(p):
        return PublishResult(p, True, post_id="yt-1", url="https://youtu.be/yt-1")

    def fail_tiktok(p):
        return PublishResult(p, False, error="SessionExpired: challenge")

    _mock_provider(monkeypatch, "youtube", ok_youtube, calls)
    _mock_provider(monkeypatch, "tiktok", fail_tiktok, calls)

    results = publish_bundle(str(bundle_path), ["youtube", "tiktok"])
    by_platform = {r.platform: r for r in results}
    assert by_platform["youtube"].success and by_platform["youtube"].post_id == "yt-1"
    assert not by_platform["tiktok"].success

    # ledger: youtube recorded once as success, tiktok as failure
    entries = [json.loads(l) for l in isolated_ledger.read_text().splitlines()]
    yt = [e for e in entries if e["platform"] == "youtube"]
    assert len(yt) == 1 and yt[0]["post_id"] == "yt-1"

    # a re-run must not re-publish youtube
    publish_bundle(str(bundle_path), ["youtube", "tiktok"])
    yt_entries = [e for e in entries if e["platform"] == "youtube"]
    assert len(yt_entries) == 1


def test_visibility_mapping_and_unknown_platform(isolated_ledger, tmp_path):
    from social_influence.providers.tiktok import VIS_MAP

    assert VIS_MAP["public"] == "everyone"
    assert VIS_MAP["private"] == "only_you"

    from social_influence.providers.base import PublishResult, PLATFORMS

    results = publish_bundle(str(make_bundle(tmp_path)), ["nope"])
    assert not results[0].success
    assert "unknown platform" in results[0].error