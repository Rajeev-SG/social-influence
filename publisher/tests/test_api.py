"""API security contract: bearer auth required, bundle paths allow-listed."""
from fastapi.testclient import TestClient


def client(monkeypatch, tmp_path):
    import os
    os.environ["SOCIAL_INFLUENCE_API_TOKEN"] = "test-token"
    os.environ["SOCIAL_INFLUENCE_ALLOWED_ROOTS"] = str(tmp_path / "posts")
    from social_influence.api import app
    return TestClient(app)


def test_publish_requires_bearer(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    assert c.post("/publish", json={"bundle": "x"}).status_code == 401
    assert c.post("/publish", json={"bundle": "x"}, headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_publish_rejects_paths_outside_allowlist(monkeypatch, tmp_path):
    c = client(monkeypatch, tmp_path)
    r = c.post("/publish", json={"bundle": "/etc/passwd"}, headers={"Authorization": "Bearer test-token"})
    assert r.status_code == 403


def test_health_open():
    from social_influence.api import app
    c = TestClient(app)
    assert c.get("/health").json() == {"ok": True}
