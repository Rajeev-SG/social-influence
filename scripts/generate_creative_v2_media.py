#!/usr/bin/env python3
"""Execute the OpenRouter media experiment for GutKitchen Creative Engine v2."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from social_influence.openrouter_media import (  # noqa: E402
    GenerationRecord,
    OpenRouterMediaClient,
    OpenRouterMediaError,
    load_records,
    write_records,
)


PLAN_PATH = ROOT / "brands/gutkitchen/creative-engine-v2/openrouter-media-plan.json"
RUN_DIR = ROOT / "brands/gutkitchen/creative-engine-v2/openrouter-run"
RECORD_LOCK = Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_plan() -> dict:
    return json.loads(PLAN_PATH.read_text())


def model_by_id(models: list[dict], model_id: str) -> dict:
    for model in models:
        if model.get("id") == model_id:
            return model
    raise OpenRouterMediaError(f"model not present in live discovery: {model_id}")


def ensure_supported(model: dict, params: dict, *, route: str) -> dict:
    """Keep requests within the live video-model capability record."""
    actual = dict(params)
    durations = model.get("supported_durations") or []
    resolutions = model.get("supported_resolutions") or []
    ratios = model.get("supported_aspect_ratios") or []
    if durations and actual.get("duration") not in durations:
        actual["duration"] = min(durations, key=lambda value: abs(value - int(actual.get("duration", 5))))
    if resolutions and actual.get("resolution") not in resolutions:
        actual["resolution"] = resolutions[0]
    if ratios and actual.get("aspect_ratio") not in ratios:
        actual["aspect_ratio"] = "9:16" if "9:16" in ratios else ratios[0]
    if "generate_audio" in model:
        actual["generate_audio"] = bool(model["generate_audio"])
    if not model.get("seed", True):
        actual.pop("seed", None)
    print(f"MODEL {route}: {model['id']} -> {actual}")
    return actual


def frame_hashes(reference_dir: Path, plan: dict) -> list[dict]:
    records: list[dict] = []
    for source in plan["referenceInputs"]:
        source_id = source["id"].removesuffix("-action")
        for frame_type in ("first", "middle", "action"):
            path = reference_dir / f"{source_id}-{frame_type}.jpg"
            if not path.exists():
                raise FileNotFoundError(f"missing reference capture: {path}")
            records.append(
                {
                    "id": f"{source_id}-{frame_type}",
                    "sourceId": source["id"],
                    "sourceUrl": source["sourceUrl"],
                    "path": str(path),
                    "sha256": sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                    "retention": "ephemeral-not-committed",
                }
            )
    return records


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def save_gzip_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)


def cached_record(route: str, output_path: Path) -> GenerationRecord | None:
    for item in load_records(RUN_DIR / "provenance/generations.json"):
        if item.get("route") == route and Path(item.get("output_path", "")) == output_path:
            if output_path.exists() and sha256(output_path.read_bytes()).hexdigest() == item.get("output_sha256"):
                return GenerationRecord(**item)
    return None


def estimated_video_cost(model: dict, params: dict) -> float | None:
    duration = int(params.get("duration", 0))
    pricing = model.get("pricing_skus") or {}
    if model["id"] == "minimax/hailuo-3-max":
        rate = float(pricing.get("duration_seconds_480p", 0))
        return round(rate * duration, 6)
    if model["id"] == "minimax/hailuo-3":
        rate = float(pricing.get("duration_seconds", 0))
        return round(rate * duration, 6)
    if model["id"] == "alibaba/wan-3.0":
        rate = float(pricing.get("duration_seconds_480p", 0))
        return round(rate * duration, 6)
    return None


def recovered_video_record(
    route: str,
    job: dict,
    model: dict,
    keyframe: Path | None,
    output_path: Path,
    params: dict,
) -> GenerationRecord:
    """Reconstruct provenance for bytes already downloaded before a runner failure."""
    timestamp = datetime.fromtimestamp(output_path.stat().st_mtime, timezone.utc).isoformat()
    estimate = estimated_video_cost(model, params)
    return GenerationRecord(
        route=route,
        model=model["id"],
        prompt=job["prompt"],
        request={"model": model["id"], **params},
        input_references=[OpenRouterMediaClient.file_record(keyframe)] if keyframe else [],
        output_path=str(output_path),
        output_sha256=sha256(output_path.read_bytes()).hexdigest(),
        started_at=timestamp,
        completed_at=timestamp,
        elapsed_seconds=0.0,
        job_id=None,
        generation_id=None,
        provider=None,
        usage={
            "cost": None,
            "estimated_cost_usd": estimate,
            "cost_basis": "model pricing_skus estimate; exact response lost after runner exception",
        },
        attempts=[{"status": "recovered-existing-output", "output_sha256": sha256(output_path.read_bytes()).hexdigest()}],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=Path("/tmp/gutkitchen-ref-captures"),
        help="directory containing ephemeral first/middle/action reference captures",
    )
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    plan = load_plan()
    client = OpenRouterMediaClient()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    discovery_images = client.discover_image_models()
    discovery_videos = client.discover_video_models()
    save_gzip_json(RUN_DIR / "discovery/raw/images.json.gz", discovery_images)
    save_gzip_json(RUN_DIR / "discovery/raw/videos.json.gz", discovery_videos)

    image_models = discovery_images.get("data", [])
    video_models = discovery_videos.get("data", [])
    primary_image = model_by_id(image_models, plan["models"]["imagePrimary"])
    iteration_image = model_by_id(image_models, plan["models"]["imageIteration"])
    image_endpoint_records = {}
    for model in (primary_image, iteration_image):
        image_endpoint_records[model["id"]] = client.image_model_endpoints(model["id"])
    save_gzip_json(RUN_DIR / "discovery/raw/image-endpoints.json.gz", image_endpoint_records)
    save_json(
        RUN_DIR / "discovery/summary.json",
        {
            "queriedAtUtc": utc_now(),
            "api": plan["api"],
            "imageModels": [primary_image, iteration_image],
            "videoModels": [
                model_by_id(video_models, model_id)
                for model_id in sorted(set(plan["models"]["i2v"] + plan["models"]["t2v"]))
            ],
            "imageEndpointCapabilities": image_endpoint_records,
            "rawSnapshots": [
                "raw/images.json.gz",
                "raw/videos.json.gz",
                "raw/image-endpoints.json.gz",
            ],
        },
    )

    references = frame_hashes(args.reference_dir, plan)
    save_json(RUN_DIR / "reference-inputs.json", {"frames": references, "policy": plan["referenceInputs"]})
    representative_refs = [
        args.reference_dir / "ref-05-action.jpg",
        args.reference_dir / "ref-09-middle.jpg",
        args.reference_dir / "ref-12-first.jpg",
    ]

    art_prompt = (
        "You are the creative director for a vertical food short. Analyse the attached real reference frames "
        "for framing, information density, shot rhythm, food placement, typography hierarchy, overlay positioning, "
        "camera style and transitions. Do not copy creator branding, exact compositions or imagery. Return JSON with "
        "keys: visualSystem, shotRhythm, firstSecond, typography, overlayZones, transitions, candidateNotes. "
        "Use only observations supported by the frames and the factual brief below. "
        f"Brief: {plan['brief']}. Factual basis: {json.dumps(plan['factualBasis'])}."
    )
    direction_output = RUN_DIR / "creative-direction.json"
    direction_record = cached_record("creative-direction", direction_output) or client.chat_multimodal(
        route="creative-direction",
        model=plan["models"]["creativeDirection"],
        prompt=art_prompt,
        input_references=representative_refs,
        params={"max_tokens": 1800, "reasoning_effort": "low"},
        output_path=direction_output,
    )
    records: list[GenerationRecord] = [direction_record]
    write_records([direction_record], RUN_DIR / "provenance/generations.json")

    image_records: list[GenerationRecord] = []

    def generate_image_job(image_spec: dict, model_id: str, suffix: str = "") -> GenerationRecord:
        output = RUN_DIR / "images" / f"{image_spec['id']}{suffix}.png"
        route = f"image/{image_spec['id']}{suffix}"
        cached = cached_record(route, output)
        if cached:
            print(f"CACHE {route}: {output.name}")
            return cached
        model = model_by_id(image_models, model_id)
        params = {"aspect_ratio": "9:16", "quality": "high"}
        if "seed" in (model.get("supported_parameters") or {}):
            params["seed"] = 900 + len(image_records)
        return client.generate_image(
            route=route,
            model=model_id,
            prompt=image_spec["prompt"],
            output_path=output,
            params=params,
        )

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(generate_image_job, spec, plan["models"]["imagePrimary"]) for spec in plan["imagePrompts"]]
        futures.extend(
            pool.submit(generate_image_job, spec, plan["models"]["imageIteration"], "-flare-alt")
            for spec in plan["imagePrompts"]
            if spec["id"] in {"hero-spoon", "cheese-melt"}
        )
        for future in as_completed(futures):
            record = future.result()
            image_records.append(record)
            write_records([record], RUN_DIR / "provenance/generations.json")
    image_records.sort(key=lambda item: item.route)
    records.extend(image_records)
    keyframes = {
        Path(item.output_path).stem.replace("-flare-alt", ""): Path(item.output_path)
        for item in image_records
        if not item.route.endswith("-flare-alt")
    }

    video_specs = []
    for job in plan["videoJobs"]:
        video_specs.append((f"i2v/{job['id']}", job, job["i2vModel"], job.get("imageKeyframe"), ""))
        video_specs.append((f"t2v/{job['id']}", job, job["t2vModel"], None, ""))
        if job["id"] in plan["alternativeJobs"]:
            video_specs.append((f"i2v/{job['id']}-alt", job, job["i2vModel"], job.get("imageKeyframe"), "-alt"))

    def generate_video_job(route: str, job: dict, model_id: str, keyframe: str | None, suffix: str) -> GenerationRecord:
        model = model_by_id(video_models, model_id)
        params = ensure_supported(model, job["params"], route=route)
        output_dir = RUN_DIR / "videos" / route.split("/", 1)[0]
        output = output_dir / f"{job['id']}{suffix}.mp4"
        cached = cached_record(route, output)
        if cached:
            print(f"CACHE {route}: {output.name}")
            return cached
        frame = keyframes.get(keyframe) if keyframe else None
        if output.exists() and output.stat().st_size:
            recovered = recovered_video_record(route, job, model, frame, output, params)
            with RECORD_LOCK:
                write_records([recovered], RUN_DIR / "provenance/generations.json")
            print(f"RECOVER {route}: {output.name}")
            return recovered
        return client.submit_video(
            route=route,
            model=model_id,
            prompt=job["prompt"],
            output_path=output,
            frame_images=[frame] if frame else [],
            params=params,
            poll_seconds=20,
        )

    video_records: list[GenerationRecord] = []
    failures: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(generate_video_job, *spec) for spec in video_specs]
        for future in as_completed(futures):
            try:
                record = future.result()
            except Exception as exc:  # keep completed work and report exact gaps
                failures.append({"error": str(exc)})
                print(f"FAIL video job: {exc}", file=sys.stderr)
                continue
            video_records.append(record)
            with RECORD_LOCK:
                write_records([record], RUN_DIR / "provenance/generations.json")
    video_records.sort(key=lambda item: item.route)
    records.extend(video_records)

    records.sort(key=lambda item: item.route)
    write_records(records, RUN_DIR / "provenance/generations.json")
    total_cost = sum(
        float(item.usage.get("cost", 0))
        for item in records
        if item.usage and item.usage.get("cost") is not None
    )
    summary = {
        "generatedAtUtc": utc_now(),
        "briefId": plan["briefId"],
        "openRouterOnly": True,
        "creativeDirectionModel": plan["models"]["creativeDirection"],
        "imageModels": sorted({item.model for item in image_records}),
        "videoModels": sorted({item.model for item in video_records}),
        "generationCount": len(records),
        "imageCount": len(image_records),
        "videoCount": len(video_records),
        "referenceFrameCount": len(references),
        "referenceFramesCommitted": False,
        "totalCostUsdWhereReported": round(total_cost, 6),
        "estimatedVideoCostUsd": round(
            sum((item.usage or {}).get("estimated_cost_usd") or 0 for item in video_records), 6
        ),
        "failures": failures,
        "artDirectionOutput": "creative-direction.json",
        "provenance": "provenance/generations.json",
    }
    save_json(RUN_DIR / "run-summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
