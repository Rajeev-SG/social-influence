import json
from pathlib import Path

from social_influence.bundle import load_bundle


def test_bundle_from_dir(tmp_path: Path):
    (tmp_path / "media.mp4").write_bytes(b"0")
    d = tmp_path / "bundle.json"
    d.write_text(json.dumps({
        "brand": "gutkitchen",
        "post_id": "gutkitchen-001",
        "title": "t",
        "caption": "c",
        "hashtags": ["a", "#b"],
        "assets": [{"path": "media.mp4", "type": "video"}],
        "platforms": ["youtube", "tiktok", "instagram"],
    }))
    b = load_bundle(d)
    assert b.brand == "gutkitchen"
    assert b.primary_video() is not None
    assert b.caption_with_hashtags().endswith("#a #b")


def test_image_only_bundle(tmp_path: Path):
    (tmp_path / "card.png").write_bytes(b"0")
    d = tmp_path / "bundle.json"
    d.write_text(json.dumps({
        "brand": "gutkitchen", "post_id": "x", "caption": "c",
        "assets": [{"path": "card.png", "type": "image"}],
    }))
    b = load_bundle(d)
    assert b.primary_video() is None
    assert b.primary_image() is not None
