"""No publishing side effects. A successful render is not yet an approved post."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request
from contextlib import contextmanager
from decimal import Decimal, DecimalException

CM_REVISION = "46cfe459d9ffbf40f847399e3f88c7c380074e7b"
QUEUE = re.compile(r"^(- \[) (\] )(.+?)(\r?\n)?$")
CHECKS = ("profile", "claims_and_calculations", "visual_grammar", "first_frame",
          "pacing", "captions", "audio", "cta", "rights", "privacy", "ai_label")


class Blocked(Exception):
    """Actionable failure; never advance the queue."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def post_id(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60]
    return f"{slug}-{sha(topic.encode())[:10]}"


def next_item(queue: str):
    for index, line in enumerate(queue.splitlines(keepends=True)):
        match = QUEUE.match(line)
        if match:
            return index, match.group(3)
    raise Blocked("No unused queue items")


@contextmanager
def brand_lock(path: Path):
    with path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Blocked("This brand already has an active create run") from error
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise Blocked(f"Path leaves brand directory: {relative}")
    return path


def requirements(profile: str) -> list[str]:
    match = re.search(r"^## Evidence / QA\s*\n(.*?)(?=^## |\Z)", profile, re.M | re.S)
    if not match:
        raise Blocked("Brand profile must contain Evidence / QA")
    return [line[2:].strip() for line in match[1].splitlines() if line.startswith("- ")]


def production_pack(brand_dir: Path, topic: str, profile: str):
    path = brand_dir / "posts" / f"{post_id(topic)}.json"
    if not path.is_file():
        raise Blocked(f"Missing production pack: {path}. Supply topic-specific source evidence "
                      "and rights-cleared real footage; stock or synthetic replacements are not permitted.")
    pack = read_json(path)
    if pack.get("topic") != topic:
        raise Blocked("Production pack topic does not match selected queue item")
    sources = pack.get("sources", [])
    if not sources:
        raise Blocked("Production pack needs source evidence")
    snapshots = []
    for source in sources:
        evidence = inside(brand_dir, source["file"])
        if not source.get("url") or file_sha(evidence) != source.get("sha256"):
            raise Blocked("Source snapshot missing URL or has changed")
        snapshots.append({**source, "text": evidence.read_text()})
    coverage = pack.get("evidence", {})
    if any(not isinstance(coverage.get(item), str) or not coverage[item].strip()
           for item in requirements(profile)):
        raise Blocked("Every profile Evidence / QA bullet needs an explicit evidence disposition")
    # Arithmetic is deterministic; source accuracy and applicability still require review.
    for calculation in pack.get("calculations", []):
        terms = calculation["terms"]
        if not terms:
            raise Blocked("Empty nutrient calculation")
        result = sum(Decimal(str(t["grams"])) * Decimal(str(t["per100g"])) / 100
                     for t in terms)
        if any(Decimal(str(t[k])) < 0 for t in terms for k in ("grams", "per100g")):
            raise Blocked("Negative nutrient inputs")
        if abs(result - Decimal(str(calculation["claimed"]))) > Decimal("0.1"):
            raise Blocked(f"Calculation mismatch: {calculation['name']}: {result}")
    media = pack.get("media", [])
    if not media:
        raise Blocked("No approved real footage; refusing generic stock fallback")
    for item in media:
        asset = inside(brand_dir, item["file"])
        if asset.suffix.lower() not in {".mp4", ".mov", ".webm", ".mkv"}:
            raise Blocked("Production media must be real video, not still-image placeholders")
        if file_sha(asset) != item.get("sha256") or not isinstance(item.get("rights"), dict) or not item["rights"]:
            raise Blocked("Media has changed or lacks rights evidence")
        if item.get("kind") == "generated-food-illustration":
            if not pack.get("generation_authorization") or not pack.get("disclosure"):
                raise Blocked("Generated illustration requires explicit authorization and disclosure")
            if not all(item["rights"].get(k) for k in ("provider", "model", "prompt", "workflow")):
                raise Blocked("Generated media needs provider, model, prompt and workflow provenance")
            if pack.get("ai_content_label_required") is not True or not pack.get("ai_content_label_text"):
                raise Blocked("Generated media requires a platform AI-content label contract")
        elif item.get("kind") not in {"real-food-footage", "screen-recording"}:
            raise Blocked("Unapproved visual kind")
    return pack, snapshots


def engine(root: Path) -> Path:
    value = os.environ.get("CONTENT_MACHINE_DIR")
    if not value:
        raise Blocked("Set CONTENT_MACHINE_DIR to the documented pinned Content Machine checkout")
    path = Path(value).expanduser().resolve()
    revision = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    if revision != CM_REVISION:
        raise Blocked(f"Content Machine revision mismatch; expected {CM_REVISION}")
    if not (path / "node_modules" / "tsx").is_dir():
        raise Blocked("Content Machine dependencies are not installed")
    return path


def draft(cm: Path, profile: str, topic: str, pack: dict, sources: list, run: Path):
    skill = (cm / "skills/niche-profile-draft/SKILL.md").read_text()
    write_json(run / "source-record.json", sources)
    unique_sources = list({source["file"]: source for source in sources}.values())
    prompt = (skill + "\n\nAUTHORITATIVE BRAND PROFILE:\n" + profile +
              "\n\nTOPIC: " + topic + "\nGROUNDED PRODUCTION INPUTS:\n" +
              json.dumps({"pack": pack, "sources": unique_sources}, ensure_ascii=False) +
              '\nReturn a JSON object with nonempty string fields hook, script, pacing, '
              'caption, title, cta, first_frame; nonempty arrays shots and hashtags. '
              'Each shot describes the approved asset, duration, composition and overlays. '
              'Carry source URLs and evidence dispositions through in source_record. '
              'Do not invent claims, footage, ingredient values, capabilities or time savings. '
              'Use only the supplied assets; describe required counters/status strips exactly.')
    (run / "niche-profile-draft.prompt.txt").write_text(prompt)
    if not os.environ.get("OPENAI_API_KEY"):
        raise Blocked("OPENAI_API_KEY is required for niche-profile drafting and Content Machine")
    url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    body = {"model": os.environ.get("SI_MODEL", "gpt-4o"),
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}}
    request = urllib.request.Request(url + "/chat/completions", data=json.dumps(body).encode(),
                                    headers={"Content-Type": "application/json",
                                             "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]})
    with urllib.request.urlopen(request, timeout=180) as response:
        value = json.load(response)
    result = json.loads(value["choices"][0]["message"]["content"])
    if pack.get("hook_narration"):
        result["hook"] = pack["hook_narration"]
    if pack.get("scene_narration"):
        result["script"] = "\n\n".join(pack["scene_narration"])
    if pack.get("cta_narration"):
        result["cta"] = pack["cta_narration"]
    if isinstance(result.get("script"), list):
        scenes = result["script"]
        if not scenes or not all(isinstance(scene, str) and scene.strip() for scene in scenes):
            raise Blocked("Draft script array must contain nonempty strings")
        result["script"] = "\n\n".join(scene.strip() for scene in scenes)
    for key in ("hook", "script", "pacing", "caption", "title", "cta", "first_frame"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise Blocked(f"Draft missing {key}")
    for key in ("shots", "hashtags"):
        if not isinstance(result.get(key), list) or not result[key]:
            raise Blocked(f"Draft missing {key}")
    # Preserve the actual source evidence, not merely the model's retelling of it.
    result["source_record"] = {"sources": [{k: v for k, v in source.items() if k != "text"} for source in sources], "evidence": pack["evidence"],
                               "calculations": pack.get("calculations", [])}
    write_json(run / "production-brief.json", result)
    return result


def harness(cm: Path, tool: str, request: dict, run: Path):
    write_json(run / f"{tool}.request.json", request)
    env = {**os.environ, "CM_CONFIG": str(run / "cm.config.json")}
    # Process-local FFmpeg fix for the machine's stale Homebrew x265 link; no system change.
    env.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/Cellar/x265/4.1/lib")
    with (run / f"{tool}.stderr.log").open("w") as stderr:
        result = subprocess.run(["node", "--import", "tsx", str(cm / f"scripts/harness/{tool}.ts")],
                                cwd=cm, env=env, input=json.dumps(request), text=True,
                                stdout=subprocess.PIPE, stderr=stderr, timeout=3600)
    (run / f"{tool}.response.json").write_text(result.stdout)
    try:
        # Remotion progress banners may precede the harness JSON on stdout.
        start = result.stdout.find("{")
        if start < 0:
            raise ValueError("no JSON object found on stdout")
        response = json.loads(result.stdout[start:])
    except ValueError as error:
        raise Blocked(f"{tool} returned invalid JSON; see run logs") from error
    if result.returncode or response.get("ok") is not True:
        raise Blocked(f"{tool} failed; see {run / (tool + '.response.json')}")
    return response["result"]



def rebuild_locked_render(cm: Path, run: Path, pack: dict, brief: dict, topic: str):
    """Use generate-short first, then rebuild copy-bound stages from approved text."""
    generated = read_json(run / "engine/script/script.json")
    scenes_text = pack.get("scene_narration") or []
    if len(scenes_text) != 6:
        raise Blocked("Locked render requires exactly six scene narration entries")
    source_scenes = generated.get("scenes", [])
    scenes = []
    for index, text in enumerate(scenes_text):
        source = source_scenes[index] if index < len(source_scenes) else {}
        scene = {
            "id": f"scene-{index + 1:03d}",
            "text": text,
            "visualDirection": source.get("visualDirection") or f"Use approved shot {index + 1}.",
            "mood": source.get("mood") or "practical",
        }
        if source.get("extra"):
            scene["extra"] = source["extra"]
        scenes.append(scene)
    locked = dict(generated)
    locked.update({
        "hook": pack.get("hook_narration") or brief.get("hook") or "",
        "cta": pack.get("cta_narration") or brief.get("cta") or "",
        "scenes": scenes,
        "reasoning": "Deterministic copy lock: approved production-pack narration replaces generic script expansion.",
    })
    write_json(run / "engine/script/script.json", locked)

    audio = harness(cm, "script-to-audio", {
        "scriptPath": str(run / "engine/script/script.json"),
        "outputDir": str(run / "engine/audio"),
        "voice": pack.get("voice", "bf_emma"),
        "ttsEngine": "kokoro",
        "ttsSpeed": pack.get("tts_speed", 0.80),
        "requireWhisper": True,
    }, run)
    visuals = harness(cm, "timestamps-to-visuals", {
        "timestampsPath": str(run / "engine/audio/timestamps.json"),
        "outputPath": str(run / "engine/visuals/visuals.json"),
        "visualQualityPath": str(run / "engine/visuals/visual-quality.json"),
        "provider": "local",
        "providers": ["local"],
        "localDir": str(run / "media"),
        "localManifest": str(run / "local-manifest.json"),
        "orientation": "portrait",
        "exportVisualQuality": True,
    }, run)
    render = harness(cm, "video-render", {
        "visualsPath": str(run / "engine/visuals/visuals.json"),
        "timestampsPath": str(run / "engine/audio/timestamps.json"),
        "audioPath": str(run / "engine/audio/audio.wav"),
        "outputPath": str(run / "engine/render/video.mp4"),
        "outputMetadataPath": str(run / "engine/render/render.json"),
        "exportCaptions": True,
        "captionExportPath": str(run / "engine/render/captions.remotion.json"),
        "captionSrtPath": str(run / "engine/render/captions.srt"),
        "captionAssPath": str(run / "engine/render/captions.ass"),
        "orientation": "portrait",
        "fps": 30,
        "downloadAssets": False,
        "captionPreset": "minimal",
        "captionMode": "page",
    }, run)
    write_json(run / "engine/quality-summary.json", {
        "schemaVersion": "1.0.0",
        "ready": bool(visuals.get("visualQualityPassed")) and bool(render.get("captionQualityPassed")),
        "visual": {
            "passed": visuals.get("visualQualityPassed"),
            "score": visuals.get("visualQualityScore"),
            "artifactPath": str(run / "engine/visuals/visual-quality.json"),
        },
        "captions": {
            "passed": render.get("captionQualityPassed"),
            "score": render.get("captionQualityScore"),
            "artifactPath": str(run / "engine/render/captions.remotion.json"),
            "srtPath": str(run / "engine/render/captions.srt"),
            "assPath": str(run / "engine/render/captions.ass"),
        },
    })
    harness(cm, "asset-ledger", {
        "outputPath": str(run / "engine/provenance/asset-ledger.json"),
        "existingLedgerPath": str(run / "engine/provenance/asset-ledger.json"),
        "artifacts": {
            "scriptPath": str(run / "engine/script/script.json"),
            "audioPath": str(run / "engine/audio/audio.wav"),
            "timestampsPath": str(run / "engine/audio/timestamps.json"),
            "audioMetadataPath": str(run / "engine/audio/audio.json"),
            "visualsPath": str(run / "engine/visuals/visuals.json"),
            "renderPath": str(run / "engine/render/video.mp4"),
            "renderMetadataPath": str(run / "engine/render/render.json"),
            "captionExportPath": str(run / "engine/render/captions.remotion.json"),
            "captionSrtPath": str(run / "engine/render/captions.srt"),
            "captionAssPath": str(run / "engine/render/captions.ass"),
            "qualitySummaryPath": str(run / "engine/quality-summary.json"),
        },
        "generatedDefaults": {
            "topic": topic,
            "provider": "content-machine",
            "workflow": "content-machine/deterministic-copy-repair",
            "usageMode": "generated-asset",
            "reviewStatus": "generated-local",
            "rightsStatus": "generated-local",
            "licenseName": "repo-generated",
        },
        "mergeStrategy": "upsert-by-asset-id",
        "addFileHashes": True,
    }, run)

def enrich_ledger(run: Path, pack: dict):
    """Retain every generated entry; attach rights only to hash-matched input footage."""
    ledger = read_json(run / "engine/provenance/asset-ledger.json")
    allowed = {"sourceUrl", "author", "licenseName", "licenseUrl", "licenseStatus",
               "rightsStatus", "reviewStatus", "attributionText", "attributionPlacement",
               "attributionRequired", "rightsFlags", "contentIdRisk", "provider", "model", "prompt", "workflow", "usageMode"}
    assets = ledger.get("assets", [])
    if not assets:
        raise Blocked("Generated asset ledger is empty")
    media = {asset["sha256"]: asset["rights"] for asset in pack["media"]}
    for asset in assets:
        if asset.get("stage") == "script-to-audio":
            asset.setdefault("contentIdRisk", "none-known")
        if asset.get("kind") == "visual-scene":
            path = Path(asset.get("localPath", ""))
            if not path.is_file() or not path.resolve().is_relative_to((run / "media").resolve()):
                raise Blocked("Ledger contains an unapproved visual")
            rights = media.get(file_sha(path))
            if rights is None:
                raise Blocked("Ledger visual hash does not match supplied footage")
            asset.update({k: v for k, v in rights.items() if k in allowed})
    # Upstream summary describes pre-enrichment statuses; omit rather than report stale counts.
    ledger.pop("summary", None)
    write_json(run / "engine/provenance/review-ledger.json", ledger)


def check_machine_review(run: Path):
    production = read_json(run / "production-input.json")
    if any(item.get("kind") == "generated-food-illustration" for item in production.get("media", [])):
        if production.get("ai_content_label_required") is not True or not production.get("ai_content_label_text"):
            raise Blocked("Generated-food render lacks a hard platform AI-content label contract")
    for relative in ("publish-prep/validate.json", "publish-prep/score.json",
                     "publish-prep/provenance.json"):
        if read_json(run / "engine" / relative).get("passed") is not True:
            raise Blocked(f"Required QA failed: {relative}")
    quality = read_json(run / "engine/quality-summary.json")
    if quality.get("ready") is not True:
        raise Blocked("Visual/caption readiness failed or unknown")
    visuals = read_json(run / "engine/visuals/visuals.json")
    if visuals.get("fallbacks") != 0:
        raise Blocked("Visual fallback detected; refusing generic replacement")
    approved = {str(p.resolve()) for p in (run / "media").iterdir()}
    for scene in visuals.get("scenes", []):
        if str(Path(scene.get("assetPath", "")).resolve()) not in approved:
            raise Blocked("Rendered visual is not in the approved local asset set")
    if not visuals.get("scenes"):
        raise Blocked("No rendered scenes")
    for name in ("video.mp4", "captions.remotion.json", "captions.srt", "captions.ass"):
        path = run / "engine/render" / name
        if not path.is_file() or not path.stat().st_size:
            raise Blocked(f"Missing render artifact: {name}")


def tree_hash(run: Path) -> str:
    """Bind final approval to all machine artifacts, not only the MP4."""
    records = [(str(p.relative_to(run)), file_sha(p)) for p in sorted((run / "engine").rglob("*"))
               if p.is_file()]
    return sha(json.dumps(records).encode())


def require_review(run: Path, input_hash: str):
    expected = {"input_sha256": input_hash,
                "video_sha256": file_sha(run / "engine/render/video.mp4"),
                "engine_sha256": tree_hash(run),
                "brief_sha256": file_sha(run / "production-brief.json")}
    template = {**expected, "passed": False, "reviewer": "",
                "checks": {key: {"passed": False, "notes": ""} for key in CHECKS}}
    write_json(run / "review.required.json", template)
    path = run / "review.json"
    if not path.is_file():
        raise Blocked(f"Render awaits full playback and brand/evidence review. Complete {path} "
                      "from review.required.json, then rerun the same create command.")
    review = read_json(path)
    if any(review.get(k) != v for k, v in expected.items()):
        raise Blocked("Review is stale: inputs, brief or rendered artifacts have changed")
    if review.get("passed") is not True or not str(review.get("reviewer", "")).strip():
        raise Blocked("Final editorial review has not passed")
    for key in CHECKS:
        check = review.get("checks", {}).get(key, {})
        if check.get("passed") is not True or not str(check.get("notes", "")).strip():
            raise Blocked(f"Final editorial review incomplete: {key}")
    return review


def create(root: Path, brand: str):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", brand):
        raise Blocked("Invalid brand slug")
    brand_dir = root / "brands" / brand
    if not brand_dir.is_dir():
        raise Blocked(f"Unknown brand: {brand}")
    with brand_lock(brand_dir / ".create.lock"):
        queue_path = brand_dir / "queue.md"
        queue = queue_path.read_bytes().decode()
        index, topic = next_item(queue)
        profile = (brand_dir / "profile.md").read_text()
        post = root / "output" / brand / post_id(topic)
        post.mkdir(parents=True, exist_ok=True)
        run = None
        try:
            write_json(post / "selection.json", {"brand": brand, "topic": topic,
                       "post_id": post_id(topic), "required_evidence": requirements(profile)})
            pack, sources = production_pack(brand_dir, topic, profile)
            digest = sha(json.dumps([profile, topic, pack, sources], sort_keys=True).encode())
            cm = engine(root)
            pending = post / "pending.json"
            if pending.is_file() and read_json(pending)["input_sha256"] == digest:
                run = post / read_json(pending)["attempt"]
                brief = read_json(run / "production-brief.json")
            else:
                count = len(list(post.glob("attempt-*"))) + 1
                run = post / f"attempt-{count:04d}"
                run.mkdir()
                (run / "profile.md").write_text(profile)
                write_json(run / "production-input.json", pack)
                brief = draft(cm, profile, topic, pack, sources, run)
                media_dir = run / "media"
                media_dir.mkdir()
                manifest = {}
                for i, asset in enumerate(pack["media"]):
                    source = inside(brand_dir, asset["file"])
                    target = media_dir / f"{i:03d}-{source.name}"
                    shutil.copy2(source, target)
                    manifest[f"scene-{i+1:03d}"] = str(target)
                if manifest:
                    paths = [manifest[f"scene-{i+1:03d}"] for i in range(len(pack["media"]))]
                    manifest["hook"] = paths[0]
                    manifest["cta"] = paths[-1]
                write_json(run / "local-manifest.json", manifest)
                write_json(run / "cm.config.json", {"llm": {"provider": "openai",
                           "model": os.environ.get("SI_MODEL", "gpt-4o")},
                           "visuals": {"provider": "local", "fallbackProviders": [],
                                       "local": {"dir": str(media_dir)}}})
                compact_brief = {key: brief[key] for key in (
                    "hook", "script", "pacing", "caption", "title", "cta", "first_frame", "shots"
                )}
                exact_copy = {
                    "hook": pack.get("hook_narration", brief["hook"]),
                    "scenes": pack.get("scene_narration", []),
                    "cta": pack.get("cta_narration", brief["cta"]),
                }
                request = {"topic": "PRE-APPROVED SCRIPT: COPY VERBATIM. DO NOT REWRITE, EXPAND, OR ADD WORDS. " +
                           json.dumps(exact_copy, ensure_ascii=False) +
                           "\nProfile-derived visual brief: " + json.dumps(compact_brief, ensure_ascii=False) +
                           "\nExactly six scenes total including scene 1 as the hook. Each visualDirection must be concise.",
                           "archetype": "howto", "targetDuration": 32,
                           "outputDir": str(run / "engine"), "llmProvider": "openai",
                           "visuals": {"provider": "local", "providers": ["local"],
                                       "localDir": str(media_dir), "localManifest": str(run / "local-manifest.json")},
                           "audio": {"requireWhisper": True, "voice": pack.get("voice", "bf_emma")},
                           "render": {"exportCaptions": True, "captionPreset": "minimal", "captionMode": "page"},
                           "publishPrep": {"enabled": False, "requirePass": True,
                                           "platform": "tiktok"}}
                harness(cm, "generate-short", request, run)
                rebuild_locked_render(cm, run, pack, brief, topic)
                enrich_ledger(run, pack)
                # Review only AFTER attaching supplied rights evidence to the full emitted ledger.
                # This is mandatory; generate-short alone cannot finalize the queue.
                review = harness(cm, "publish-prep-review", {
                    "videoPath": str(run / "engine/render/video.mp4"),
                    "scriptPath": str(run / "engine/script/script.json"),
                    "captionExportPath": str(run / "engine/render/captions.remotion.json"),
                    "assetLedgerPath": str(run / "engine/provenance/review-ledger.json"),
                    "outputDir": str(run / "engine/publish-prep"),
                    "platform": "tiktok", "validate": {"cadence": True, "audioSignal": True,
                                                         "captionSync": True}}, run)
                if review.get("passed") is not True:
                    raise Blocked("Content Machine publish-prep rejected this render")
                check_machine_review(run)
                write_json(pending, {"input_sha256": digest, "attempt": run.name})
            check_machine_review(run)
            review = require_review(run, digest)
            # Recheck source inputs and queue after slow generation/review work.
            current_pack, current_sources = production_pack(brand_dir, topic, profile)
            if current_pack != pack or current_sources != sources or (brand_dir / "profile.md").read_text() != profile:
                raise Blocked("Production inputs changed during generation")
            if queue_path.read_bytes().decode() != queue:
                raise Blocked("Queue changed during generation; no queue update performed")
            bundle = run / "bundle"
            bundle.mkdir(exist_ok=True)
            shutil.copy2(run / "engine/render/video.mp4", bundle / "video.mp4")
            write_json(bundle / "metadata.json", {k: brief[k] for k in ("title", "caption", "hashtags")})
            write_json(bundle / "source-qa.json", {"source_record": brief["source_record"], "review": review})
            content = brief["caption"] + "\n\n" + " ".join(brief["hashtags"])
            # Structurally matches Postiz CreatePostDto for a draft. Placeholders
            # must be replaced with the real upload/integration bindings before send.
            api_payload_template = {
                "type": "draft",
                "shortLink": False,
                "date": "${POSTIZ_ISO_DATE}",
                "tags": [{"value": tag.lstrip("#"), "label": tag} for tag in brief["hashtags"]],
                "posts": [{
                    "integration": {"id": "${POSTIZ_INTEGRATION_ID}"},
                    "value": [{
                        "content": content,
                        "image": [{"id": "${POSTIZ_MEDIA_ID}", "path": "${POSTIZ_MEDIA_PATH}"}],
                    }],
                }],
            }
            generated_food = any(item.get("kind") == "generated-food-illustration" for item in pack.get("media", []))
            write_json(bundle / "postiz-handoff.json", {
                "status": "structurally-ready-awaiting-upload-and-integration-binding",
                "publish_readiness": {
                    "ready_for_publication": not generated_food,
                    "blockers": ["AI-generated food visuals require explicit public-use approval and platform AI-content labeling"] if generated_food else [],
                },
                "platform_ai_label_required": generated_food,
                "platform_ai_label_text": pack.get("ai_content_label_text") if generated_food else None,
                "publish": False,
                "media": {"path": str(bundle / "video.mp4"), "sha256": review["video_sha256"]},
                "title": brief["title"], "content": content,
                "targets": ["tiktok", "instagram", "youtube"],
                "api_payload_template": api_payload_template,
                "required_bindings": ["Postiz upload response media id and path",
                                      "connected integration id per target",
                                      "ISO date for draft/schedule",
                                      "provider settings when changing type from draft"]})
            write_json(post / "latest.json", {"status": "reviewed", "bundle": str(bundle), "attempt": run.name})
            lines = queue.splitlines(keepends=True)
            lines[index] = lines[index].replace("- [ ]", "- [x]", 1)
            tmp = queue_path.with_suffix(".md.tmp")
            tmp.write_bytes("".join(lines).encode())
            tmp.replace(queue_path)
            write_json(post / "status.json", {"status": "generated", "bundle": str(bundle)})
            return bundle
        except Exception as error:
            write_json(post / "status.json", {"status": "blocked", "attempt": run.name if run else None,
                                              "reason": str(error)})
            raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (default: cwd)")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("create")
    command.add_argument("--brand", required=True)
    command.add_argument("--next", action="store_true", required=True)
    args = parser.parse_args()
    try:
        print(create(args.root.resolve(), args.brand))
    except (Blocked, OSError, ValueError, KeyError, TypeError, DecimalException, subprocess.SubprocessError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
