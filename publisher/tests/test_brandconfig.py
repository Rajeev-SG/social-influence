"""Brand-driven config: lazy env reads + cross-brand isolation."""

import pytest

from social_influence import brandconfig
from social_influence.bundle import load_bundle
from social_influence.providers.base import PermanentError, PLATFORMS


def test_expected_account_reads_env_lazily(monkeypatch):
    # set AFTER import — proves no import-time capture
    monkeypatch.setenv("OTHERBRAND_TIKTOK_USERNAME", "other.handle")
    assert brandconfig.expected_account("otherbrand", "tiktok") == "other.handle"
    monkeypatch.delenv("OTHERBRAND_TIKTOK_USERNAME")
    assert brandconfig.expected_account("otherbrand", "tiktok") == ""


def test_legacy_gutkitchen_fallback(monkeypatch):
    monkeypatch.setenv("GUTKITCHEN_TT_USERNAME", "gutkitchen.uk")
    assert brandconfig.expected_account("gutkitchen", "tiktok") == "gutkitchen.uk"
    monkeypatch.setenv("GUTKITCHEN_YOUTUBE_HANDLE", "thegutkitchen")
    assert brandconfig.expected_account("gutkitchen", "youtube") == "thegutkitchen"


def test_dashes_and_case_normalised(monkeypatch):
    monkeypatch.setenv("AI_FOR_ACCOUNTANTS_TIKTOK_USERNAME", "aifa")
    assert brandconfig.expected_account("ai-for-accountants", "tiktok") == "aifa"


def test_state_files_are_brand_prefixed():
    assert brandconfig.ig_session_name("gutkitchen") == "gutkitchen_ig_session.json"
    assert brandconfig.tiktok_cookies_name("ai-for-accountants") == "ai_for_accountants_tiktok_cookies.json"


def test_bundle_for_other_brand_cannot_use_gutkitchen_sessions(tmp_path, monkeypatch):
    """A bundle for a different brand must fail loudly, never reuse gutkitchen state."""
    (tmp_path / "media.mp4").write_bytes(b"0")
    d = tmp_path / "bundle.json"
    d.write_text(__import__("json").dumps({
        "brand": "someotherbrand",
        "post_id": "x",
        "caption": "c",
        "assets": [{"path": "media.mp4", "type": "video"}],
    }))
    from social_influence.providers import tiktok

    monkeypatch.setenv("SOCIAL_INFLUENCE_STATE_DIR", str(tmp_path / "state"))
    with pytest.raises(PermanentError, match="someotherbrand"):
        tiktok.upload(load_bundle(d))