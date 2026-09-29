"""Instagram cross-brand isolation: password fallback, expected-account guard,
session-file collision-freedom — the highest-risk cross-brand failure modes."""

import json

import pytest

from social_influence import brandconfig
from social_influence.providers import instagram
from social_influence.providers.base import PermanentError, TransientError


def test_instagram_password_no_cross_brand_fallback(monkeypatch):
    monkeypatch.setenv("GUTKITCHEN_IG_PASSWORD", "gut-secret")
    # a non-gutkitchen brand must never inherit gutkitchen's password
    assert brandconfig.instagram_password("otherbrand") == ""
    assert brandconfig.instagram_password("ai-for-accountants") == ""
    # gutkitchen keeps its legacy fallback
    assert brandconfig.instagram_password("gutkitchen") == "gut-secret"


def test_ig_login_fails_loudly_without_expected_account(monkeypatch, tmp_path):
    """Username resolvable from .env but expected-account env unset → refuse, never guess."""
    dotenv = tmp_path / "test.env"
    dotenv.write_text("OTHERBRAND_IG_USERNAME=someone\nOTHERBRAND_IG_PASSWORD=pw\n")
    monkeypatch.setenv("SOCIAL_INFLUENCE_DOTENV", str(dotenv))
    for var in ("OTHERBRAND_IG_USERNAME", "OTHERBRAND_IG_PASSWORD"):
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(PermanentError, match="refusing to guess"):
        instagram.ig_login("otherbrand")


def test_session_file_names_never_collide_with_legacy():
    # the legacy repo-relative ig_session.json must not be reachable for any brand
    for brand in ("gutkitchen", "ai-for-accountants", "otherbrand"):
        assert brandconfig.ig_session_name(brand) != "ig_session.json"
    assert brandconfig.ig_session_name("ai-for-accountants") == "ai_for_accountants_ig_session.json"


def test_transient_session_error_keeps_session(monkeypatch, tmp_path):
    """A network blip during validation must NOT trigger a password login."""
    dotenv = tmp_path / "test.env"
    dotenv.write_text("GUTKITCHEN_IG_USERNAME=gutkitchen.uk\nGUTKITCHEN_IG_PASSWORD=pw\n")
    monkeypatch.setenv("SOCIAL_INFLUENCE_DOTENV", str(dotenv))
    monkeypatch.setenv("GUTKITCHEN_IG_USERNAME", "gutkitchen.uk")
    monkeypatch.setenv("GUTKITCHEN_IG_PASSWORD", "pw")

    session = tmp_path / "state" / "gutkitchen_ig_session.json"
    monkeypatch.setenv("SOCIAL_INFLUENCE_STATE_DIR", str(tmp_path / "state"))
    session.parent.mkdir(parents=True, exist_ok=True)
    session.write_text("{}")

    class FakeClient:
        def load_settings(self, p):
            pass

        def get_timeline_feed(self):
            raise ConnectionError("connection reset")

    monkeypatch.setattr(instagram, "_client", lambda: FakeClient())
    with pytest.raises(TransientError, match="session kept"):
        instagram.ig_login("gutkitchen")
    # session file untouched (not deleted) — no re-login happened
    assert session.exists()


def test_password_login_rate_limited(monkeypatch, tmp_path):
    monkeypatch.setenv("SOCIAL_INFLUENCE_STATE_DIR", str(tmp_path / "state"))
    (tmp_path / "state").mkdir(parents=True, exist_ok=True)
    (tmp_path / "state" / "gutkitchen_last_ig_login").write_text(str(__import__("time").time()))
    with pytest.raises(PermanentError, match="cooldown"):
        instagram._password_login_allowed("gutkitchen")


def test_auth_error_classification():
    assert instagram._is_auth_error(Exception("login_required: please log in"))
    assert instagram._is_auth_error(Exception("401 Unauthorized"))
    assert not instagram._is_auth_error(Exception("HTTP 429 rate limit exceeded"))
    assert not instagram._is_auth_error(Exception("connection timeout"))
