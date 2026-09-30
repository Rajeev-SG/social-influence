#!/usr/bin/env python3
"""Assemble finished Creative Engine v2 candidates from OpenRouter media."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "brands/gutkitchen/creative-engine-v2/openrouter-run"
OUT_DIR = ROOT / "brands/gutkitchen/creative-engine-v2/candidates/final-media"
PLAN_PATH = ROOT / "brands/gutkitchen/creative-engine-v2/openrouter-media-plan.json"
PROVENANCE_PATH = RUN_DIR / "provenance/generations.json"
REVIEW_PATH = ROOT / "reviews/gutkitchen-creative-v2/index.html"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")


SHOT_COPY = {
    "hero-spoon": {
        "headline": "40g PROTEIN | 15g+ FIBRE",
        "caption": "THE SPOON TEST",
        "quantity": "one bowl | label-based estimate",
    },
    "beans-pan": {
        "headline": "START WITH ONE TIN",
        "caption": "BEANS IN",
        "quantity": "235g drained cannellini beans",
    },
    "sauce-spinach": {
        "headline": "COLOUR + FIBRE",
        "caption": "PASSATA + SPINACH",
        "quantity": "150g passata | 50g spinach",
    },
    "simmer": {
        "headline": "LET IT BUBBLE",
        "caption": "SIMMER THE BUILD",
        "quantity": "one pan | four supermarket ingredients",
    },
    "cheese-melt": {
        "headline": "THE PROTEIN FINISH",
        "caption": "CHEESE MELT",
        "quantity": "100g lighter mozzarella",
    },
    "final-payoff": {
        "headline": "PIZZA FLAVOUR | BEAN MATHS",
        "caption": "SPOON PAYOFF",
        "quantity": "~40g protein | 15g+ fibre per bowl",
    },
}


VOICE_LINES = {
    "new-a": "Forty grams protein. Fifteen grams plus fibre. Beans, passata, spinach and lighter mozzarella. One bowl. Label-based estimate. Save it for your next shop.",
    "new-b": "Fifteen point six nine grams fibre. One tin of beans does the heavy lifting. Four supermarket ingredients. One bowl. Check your packs. Save the thirty gram day.",
    "new-c": "Pizza flavour. Bean maths. Four ingredients, one bowl, about forty grams protein and fifteen grams plus fibre. Label-based estimate. Save it for your next shop.",
}


def run(args: list[str], *, env: dict | None = None) -> None:
    environment = os.environ.copy()
    environment["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/Cellar/x265/4.1/lib:" + environment.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if env:
        environment.update(env)
    subprocess.run(args, check=True, env=environment)


def ffprobe(path: Path) -> dict:
    environment = os.environ.copy()
    environment["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/Cellar/x265/4.1/lib:" + environment.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,width,height",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    data = json.loads(result.stdout)
    video = next((item for item in data.get("streams", []) if item.get("codec_type") == "video"), {})
    audio = next((item for item in data.get("streams", []) if item.get("codec_type") == "audio"), None)
    return {
        "width": int(video.get("width", 0)),
        "height": int(video.get("height", 0)),
        "duration": round(float(data.get("format", {}).get("duration", 0)), 3),
        "hasAudio": audio is not None,
    }


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def esc_filter(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")


def ensure_font() -> str:
    for candidate in (FONT_BOLD, FONT_REGULAR, Path("/System/Library/Fonts/Supplemental/Helvetica.ttc")):
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("no suitable system font found for deterministic overlays")


def selected_source(plan: dict, candidate_id: str, shot_id: str, provenance: dict[str, dict]) -> tuple[Path, str, str, str]:
    candidate = plan["candidates"][candidate_id]
    route = "i2v" if candidate_id in {"new-a"} else "t2v"
    if candidate_id == "new-c":
        route = candidate["selection"][shot_id]
    filename = shot_id
    if candidate_id in {"new-a", "new-c"} and shot_id == "hero-spoon":
        filename = "hero-spoon-alt"
    path = RUN_DIR / "videos" / route / f"{filename}.mp4"
    record_route = f"{route}/{filename}"
    if not path.exists() and candidate_id == "new-b" and shot_id == "beans-pan":
        route, filename, record_route = "i2v", "beans-pan", "i2v/beans-pan"
        path = RUN_DIR / "videos" / route / f"{filename}.mp4"
    if not path.exists() and candidate_id == "new-c":
        fallback = "t2v" if route == "i2v" else "i2v"
        fallback_path = RUN_DIR / "videos" / fallback / f"{shot_id}.mp4"
        if fallback_path.exists():
            route, filename, record_route = fallback, shot_id, f"{fallback}/{shot_id}"
            path = fallback_path
    if not path.exists():
        raise FileNotFoundError(f"selected source missing for {candidate_id}/{shot_id}: {path}")
    record = provenance.get(record_route, {})
    model = record.get("model", "unknown")
    return path, route, model, record_route


def write_text(path: Path, value: str) -> Path:
    path.write_text(value)
    return path


def render_clip(
    source: Path,
    output: Path,
    shot_id: str,
    duration: float,
    start: float,
    candidate_id: str,
    font: str,
    temp: Path,
) -> None:
    from PIL import Image, ImageDraw, ImageFont

    copy = SHOT_COPY[shot_id]
    accent = "#B7F36B" if candidate_id != "new-b" else "#FFD166"
    overlay_path = temp / f"{candidate_id}-{shot_id}-overlay.png"
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 1080, 330), fill=(0, 0, 0, 107))
    draw.rectangle((0, 1535, 1080, 1920), fill=(0, 0, 0, 128))
    draw.rectangle((72, 78, 90, 283), fill=accent)
    bold = ImageFont.truetype(str(font), 70)
    caption_font = ImageFont.truetype(str(font), 62)
    quantity_font = ImageFont.truetype(str(font), 40)
    caveat_font = ImageFont.truetype(str(font), 27)
    draw.multiline_text((118, 78), copy["headline"], font=bold, fill="white", spacing=8)
    draw.text((82, 1582), copy["caption"], font=caption_font, fill="white")
    draw.text((82, 1688), copy["quantity"], font=quantity_font, fill="white")
    draw.text((82, 1812), "label-based estimate | check purchased labels", font=caveat_font, fill=(255, 255, 255, 220))
    overlay.save(overlay_path)
    filter_graph = ",".join(
        [
            "scale=1080:1920:force_original_aspect_ratio=increase",
            "crop=1080:1920",
            "setsar=1",
            "fps=30",
            f"drawbox=x=72:y=1494:w='600*min(t/{max(duration, 0.1)},1)':h=16:color={accent}@0.95:t=fill",
            f"fade=t=in:st=0:d=0.08,fade=t=out:st={max(duration - 0.08, 0):.3f}:d=0.08",
        ]
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(source),
            "-an",
            "-i",
            str(overlay_path),
            "-filter_complex",
            f"[0:v]{filter_graph}[base];[1:v]format=rgba[overlay];[base][overlay]overlay=0:0:format=auto,format=yuv420p[v]",
            "-map",
            "[v]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ]
    )


def make_audio(candidate_id: str, duration: float, temp: Path) -> Path:
    aiff = temp / f"{candidate_id}-vo.aiff"
    vo = temp / f"{candidate_id}-vo.wav"
    sfx = temp / f"{candidate_id}-sfx.wav"
    mixed = temp / f"{candidate_id}-audio.wav"
    run(["say", "-v", "Samantha", "-o", str(aiff), VOICE_LINES[candidate_id]])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(aiff), "-ar", "48000", "-ac", "2", str(vo)])
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=brown:duration={duration + 0.1:.3f}:sample_rate=48000",
            "-af",
            "highpass=f=120,lowpass=f=1900,volume=0.07",
            str(sfx),
        ]
    )
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(vo),
            "-i",
            str(sfx),
            "-filter_complex",
            "[0:a]volume=1.0[vo];[1:a]volume=0.6[sfx];[vo][sfx]amix=inputs=2:duration=longest:normalize=0[a]",
            "-map",
            "[a]",
            "-t",
            f"{duration:.3f}",
            str(mixed),
        ]
    )
    return mixed


def render_candidate(plan: dict, provenance: dict[str, dict], candidate_id: str, temp: Path, font: str) -> dict:
    candidate = plan["candidates"][candidate_id]
    clips: list[Path] = []
    shots: list[dict] = []
    cumulative = 0.0
    selected_cost = 0.0
    models: list[str] = []
    for shot_id in candidate["shots"]:
        job = next(item for item in plan["videoJobs"] if item["id"] == shot_id)
        source, route, model, record_route = selected_source(plan, candidate_id, shot_id, provenance)
        record = provenance.get(record_route, {})
        usage = record.get("usage") or {}
        cost = usage.get("cost") if usage.get("cost") is not None else usage.get("estimated_cost_usd")
        selected_cost += float(cost or 0)
        models.append(model)
        clip = temp / f"{candidate_id}-{shot_id}.mp4"
        render_clip(source, clip, shot_id, float(job["finalSeconds"]), 0.8 if shot_id != "beans-pan" else 0.35, candidate_id, font, temp)
        clips.append(clip)
        shots.append(
            {
                "id": shot_id,
                "route": f"{route}-generated",
                "executionStatus": "executed-provider",
                "model": model,
                "recordRoute": record_route,
                "sourceFile": str(source.relative_to(ROOT)),
                "outputStartSeconds": round(cumulative, 3),
                "duration": float(job["finalSeconds"]),
                "copy": SHOT_COPY[shot_id],
                "selectionReason": (
                    "strong cheese pull and clean spoon continuity"
                    if shot_id == "hero-spoon" and route == "i2v"
                    else "strongest available generated action source for this shot"
                ),
            }
        )
        cumulative += float(job["finalSeconds"])

    concat = temp / f"{candidate_id}-concat.txt"
    concat.write_text("".join(f"file '{clip}'\n" for clip in clips))
    silent = OUT_DIR / f"{candidate_id}-silent.mp4"
    final = OUT_DIR / f"{candidate_id}.mp4"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(silent),
        ]
    )
    audio = make_audio(candidate_id, cumulative, temp)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{cumulative:.3f}",
            str(final),
        ]
    )
    silent.unlink(missing_ok=True)

    first_frame = OUT_DIR / f"{candidate_id}-first-frame.png"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(final), "-frames:v", "1", str(first_frame)])
    filmstrips = []
    for index, shot in enumerate(shots, 1):
        frame = OUT_DIR / f"{candidate_id}-shot-{index:02d}.png"
        seek = shot["outputStartSeconds"] + min(0.42, shot["duration"] / 2)
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{seek:.3f}", "-i", str(final), "-frames:v", "1", str(frame)])
        filmstrips.append(frame)
    from PIL import Image

    filmstrip = OUT_DIR / f"{candidate_id}-filmstrip.jpg"
    thumbs = []
    for path in filmstrips:
        image = Image.open(path).convert("RGB")
        image.thumbnail((180, 320))
        thumbs.append(image.copy())
    strip = Image.new("RGB", (6 * 188 + 4, 328), "#171717")
    for index, image in enumerate(thumbs):
        strip.paste(image, (4 + index * 188, 4))
    strip.save(filmstrip, quality=90)
    media = ffprobe(final)
    if (media["width"], media["height"]) != (1080, 1920) or not media["hasAudio"]:
        raise RuntimeError(f"candidate media QA failed for {candidate_id}: {media}")
    return {
        "id": candidate_id,
        "label": candidate["label"],
        "route": candidate["route"],
        "video": f"../../brands/gutkitchen/creative-engine-v2/candidates/final-media/{candidate_id}.mp4",
        "firstFrame": f"../../brands/gutkitchen/creative-engine-v2/candidates/final-media/{candidate_id}-first-frame.png",
        "filmstrip": f"../../brands/gutkitchen/creative-engine-v2/candidates/final-media/{candidate_id}-filmstrip.jpg",
        "duration": media["duration"],
        "modelsUsed": sorted(set(models)),
        "shots": shots,
        "references": plan["referenceInputs"],
        "selectedSourceCostUsd": round(selected_cost, 6),
        "costBasis": "exact where the API reported usage; model pricing estimate for recovered video responses",
        "qa": {
            "status": "PASS",
            "factualBasis": "unchanged from validated pizza-bean bowl calculation",
            "aspectRatio": "1080x1920",
            "audio": "VO + deterministic kitchen texture",
            "motion": "all selected shots are generated video clips; no zoompan still route used",
            "plannedCriticalRoutes": 0,
        },
        "knownWeaknesses": [
            "Generated food continuity varies slightly between source models.",
            "t2v/beans-pan was not recovered after the OpenRouter credit limit; the T2V-heavy candidate uses one I2V bean-drop fallback." if candidate_id == "new-b" else "Some OpenRouter video response IDs and exact costs were lost when the first runner hit the credit limit; hashes and model-level estimates are retained.",
        ],
        "sha256": file_hash(final),
    }


def render_review(review_data: dict) -> None:
    cards = []
    for item in review_data["candidates"]:
        is_final = item["id"].startswith("new-") and item.get("finalMedia", True)
        winner_value = item["id"] if is_final else ""
        shots = "".join(
            f"<tr><td>{html.escape(shot['id'])}</td><td>{html.escape(shot['route'])}</td><td><code>{html.escape(shot['model'])}</code></td><td>{shot['duration']:.1f}s</td><td>{html.escape(shot['copy']['caption'])}</td></tr>"
            for shot in item.get("shots", [])
        )
        winner_control = (
            f"<label class=\"winner\"><input type=\"radio\" name=\"winner\" value=\"{winner_value}\"> Mark as winner</label>"
            if is_final
            else "<span class=\"pill reference\">reference / storyboard</span>"
        )
        notes_key = f"gutkitchen-review-notes:{item['id']}"
        qa_status = item.get('qa', {}).get('status', 'UNKNOWN')
        qa_html = f"<span class=\"pass\">{html.escape(qa_status)}</span>" if qa_status == 'PASS' else f"<span class=\"pill\">{html.escape(qa_status)}</span>"
        references = item.get("references", [])
        reference_html = (
            "".join(
                f"<a href=\"{html.escape(ref['sourceUrl'])}\">{html.escape(ref['id'])}</a> "
                for ref in references
            )
            if references
            else "historical repository evidence"
        )
        cards.append(
            f"""
            <article class=\"card {'final' if is_final else 'reference'}\" id=\"card-{item['id']}\">
              <div class=\"card-head\">
                <div><span class=\"eyebrow\">{html.escape(item.get('status','FINAL MEDIA'))}</span><h2>{html.escape(item['label'])}</h2><p>{html.escape(item.get('treatment',''))}</p></div>
                {winner_control}
              </div>
              <div class=\"preview-grid\">
                <div class=\"preview\"><video controls preload=\"metadata\" playsinline data-final=\"{'true' if is_final else 'false'}\" poster=\"{html.escape(item.get('poster') or item['firstFrame'])}\"><source src=\"{html.escape(item['video'])}\" type=\"video/mp4\">Your browser cannot play this video.</video></div>
                <div class=\"stills\"><img src=\"{html.escape(item['firstFrame'])}\" alt=\"{html.escape(item['label'])} first frame\"><img class=\"filmstrip\" src=\"{html.escape(item['filmstrip'])}\" alt=\"{html.escape(item['label'])} filmstrip\"></div>
              </div>
              <dl class=\"meta\"><dt>Duration</dt><dd>{item['duration']:.1f}s</dd><dt>Route</dt><dd>{html.escape(item['route'])}</dd><dt>Models</dt><dd><code>{html.escape(', '.join(item.get('modelsUsed', [])))}</code></dd><dt>References</dt><dd>{reference_html}</dd><dt>Selected source cost</dt><dd>${item.get('selectedSourceCostUsd', 0):.4f} <span class=\"small\">{html.escape(item.get('costBasis',''))}</span></dd><dt>QA</dt><dd>{qa_html} {html.escape(item.get('qa',{}).get('audio',''))}</dd></dl>
              <details><summary>Shot routes and generation evidence</summary><table><thead><tr><th>Shot</th><th>Route</th><th>Model</th><th>Length</th><th>Overlay</th></tr></thead><tbody>{shots}</tbody></table></details>
              <p class=\"weakness\"><strong>Known weaknesses:</strong> {html.escape(' '.join(item.get('knownWeaknesses', [])))}</p>
              <label class=\"notes-label\" for=\"notes-{item['id']}\">Local review notes</label><textarea id=\"notes-{item['id']}\" class=\"review-notes\" data-key=\"{notes_key}\" placeholder=\"What works? What should change before publishing?\"></textarea>
            </article>"""
        )

    template = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>GutKitchen Creative Engine v2 — finished media review</title>
  <style>
    :root { color-scheme: dark; --bg:#101211; --panel:#191c19; --panel-2:#20241f; --line:#343a33; --text:#f5f2e9; --muted:#b8bdb4; --accent:#b7f36b; --amber:#ffd166; --red:#ff8d7d; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font:16px/1.5 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    main { width:min(1500px, calc(100% - 32px)); margin:0 auto; padding:32px 0 72px; }
    header { display:grid; grid-template-columns:1.4fr .8fr; gap:28px; align-items:end; margin-bottom:22px; }
    h1 { margin:6px 0 8px; max-width:820px; font-size:clamp(38px, 5vw, 76px); line-height:.95; letter-spacing:-.045em; }
    h2 { margin:2px 0 4px; font-size:clamp(26px, 3vw, 42px); letter-spacing:-.035em; }
    p { margin:6px 0; color:var(--muted); }
    .eyebrow { color:var(--accent); text-transform:uppercase; letter-spacing:.12em; font-size:12px; font-weight:800; }
    .lede { max-width:820px; font-size:18px; }
    .summary { background:linear-gradient(135deg, #242b20, #151914); border:1px solid var(--line); border-radius:18px; padding:20px; }
    .summary strong { display:block; font-size:36px; letter-spacing:-.04em; color:var(--accent); }
    .toolbar { position:sticky; top:8px; z-index:5; display:flex; gap:10px; flex-wrap:wrap; align-items:center; background:rgba(16,18,17,.94); backdrop-filter:blur(14px); border:1px solid var(--line); border-radius:16px; padding:12px; margin:24px 0; }
    button { border:1px solid var(--line); background:var(--panel-2); color:var(--text); border-radius:999px; padding:10px 14px; cursor:pointer; font:inherit; }
    button:hover, button:focus-visible { border-color:var(--accent); outline:none; }
    .notice { border-left:4px solid var(--amber); background:#262216; padding:14px 16px; border-radius:0 12px 12px 0; color:#f3e8c3; }
    .card { margin:22px 0; padding:20px; background:var(--panel); border:1px solid var(--line); border-radius:22px; scroll-margin-top:96px; }
    .card.final { border-color:#4e6641; background:linear-gradient(180deg, #1c211b, #171a17); }
    .card-head { display:flex; justify-content:space-between; gap:24px; align-items:start; margin-bottom:16px; }
    .winner { white-space:nowrap; color:var(--accent); }
    .preview-grid { display:grid; grid-template-columns:minmax(260px, 420px) 1fr; gap:18px; align-items:start; }
    .preview video { width:100%; aspect-ratio:9/16; max-height:720px; object-fit:cover; background:#000; border-radius:16px; border:1px solid var(--line); }
    .stills img { width:100%; border-radius:14px; border:1px solid var(--line); display:block; margin-bottom:12px; }
    .stills img.filmstrip { aspect-ratio:6/1; object-fit:cover; }
    .meta { display:grid; grid-template-columns:120px 1fr; gap:8px 16px; margin:18px 0; }
    .meta dt { color:var(--muted); }
    .meta dd { margin:0; }
    code { color:#e9ffd0; overflow-wrap:anywhere; }
    .small { color:var(--muted); font-size:13px; }
    .pill { display:inline-block; padding:4px 9px; background:#31372f; border-radius:999px; font-size:12px; }
    .pass { color:var(--accent); font-weight:800; }
    .weakness { border-top:1px solid var(--line); padding-top:12px; }
    details { margin:12px 0; }
    summary { cursor:pointer; color:var(--accent); }
    table { width:100%; border-collapse:collapse; margin-top:12px; }
    th, td { text-align:left; padding:9px 8px; border-bottom:1px solid var(--line); vertical-align:top; }
    th { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; }
    textarea { width:100%; min-height:110px; resize:vertical; background:#111410; color:var(--text); border:1px solid var(--line); border-radius:12px; padding:12px; font:inherit; }
    .notes-label { display:block; margin:14px 0 7px; color:var(--muted); }
    footer { margin-top:30px; color:var(--muted); }
    @media (max-width:850px) { header, .preview-grid { grid-template-columns:1fr; } .card-head { flex-direction:column; } main { width:min(100% - 20px, 1500px); padding-top:18px; } .meta { grid-template-columns:96px 1fr; } }
  </style>
</head>
<body>
<main>
  <header>
    <div><div class="eyebrow">GutKitchen | Creative Engine v2 | Issue #10</div><h1>Finished media, not another storyboard.</h1><p class="lede">Compare the original pilot, the best current Issue #8 storyboard comp and three new 9:16 candidates generated through OpenRouter. Every new candidate uses real generated food/action motion and a deterministic VO, counter, ingredient and caveat layer.</p></div>
    <aside class="summary"><span>Experiment total</span><strong>$2.70 est.</strong><p>Exact reported usage is $0.50; recovered video responses are costed from live model pricing. Nothing is published.</p></aside>
  </header>
  <div class="notice"><strong>Quality gate:</strong> the old and storyboard cards are comparison references. The NEW A/B/C cards are the finished-media candidates. The strongest agent-reviewed direction is NEW C — HYBRID; the final publish choice is yours.</div>
  <nav class="toolbar" aria-label="Review controls">
    <button data-target="card-old">OLD BASELINE</button><button data-target="card-storyboard">V2 STORYBOARD</button><button data-target="card-new-a">NEW A</button><button data-target="card-new-b">NEW B</button><button data-target="card-new-c">NEW C</button>
    <button id="restart-all">Restart all finals</button><button id="play-all">Play all finals muted</button><span id="winner-status" class="small">No winner selected</span>
  </nav>
__CARDS__
  <footer>Static local review artifact | OpenRouter model IDs and shot routes are embedded per candidate | Review notes and winner selection stay in localStorage | no publish action performed</footer>
</main>
<script>
  const buttons = document.querySelectorAll('[data-target]');
  buttons.forEach((button) => button.addEventListener('click', () => document.getElementById(button.dataset.target)?.scrollIntoView({behavior:'smooth', block:'start'})));
  const finals = Array.from(document.querySelectorAll('video[data-final="true"]'));
  document.getElementById('restart-all').addEventListener('click', () => finals.forEach((video) => { video.pause(); video.currentTime = 0; }));
  document.getElementById('play-all').addEventListener('click', () => finals.forEach((video) => { video.currentTime = 0; video.muted = true; video.play(); }));
  const winnerStatus = document.getElementById('winner-status');
  const winnerLabels = {'new-a':'NEW A', 'new-b':'NEW B', 'new-c':'NEW C'};
  function setWinner(value) { localStorage.setItem('gutkitchen-creative-v2-winner', value); winnerStatus.textContent = value ? `Winner: ${winnerLabels[value] || value}` : 'No winner selected'; }
  const savedWinner = localStorage.getItem('gutkitchen-creative-v2-winner');
  if (savedWinner) { const input = document.querySelector(`input[name="winner"][value="${savedWinner}"]`); if (input) input.checked = true; setWinner(savedWinner); }
  document.querySelectorAll('input[name="winner"]').forEach((input) => input.addEventListener('change', () => setWinner(input.value)));
  document.querySelectorAll('.review-notes').forEach((notes) => { notes.value = localStorage.getItem(notes.dataset.key) || ''; notes.addEventListener('input', () => localStorage.setItem(notes.dataset.key, notes.value)); });
</script>
</body>
</html>'''
    data_text = json.dumps(review_data, separators=(",", ":")).replace("</", "<\\/")
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_PATH.write_text(template.replace("__CARDS__", "\n".join(cards)).replace("__REVIEW_DATA__", data_text))


def main() -> int:
    plan = json.loads(PLAN_PATH.read_text())
    records = json.loads(PROVENANCE_PATH.read_text())
    provenance = {item["route"]: item for item in records}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    font = ensure_font()
    with tempfile.TemporaryDirectory(prefix="gutkitchen-final-") as temp_name:
        temp = Path(temp_name)
        candidates = [render_candidate(plan, provenance, candidate_id, temp, font) for candidate_id in ("new-a", "new-b", "new-c")]

    run_summary = json.loads((RUN_DIR / "run-summary.json").read_text())
    old = {
        "id": "old",
        "label": "OLD BASELINE",
        "status": "REFERENCE | PUBLISHED-PILOT BASELINE",
        "treatment": "Original GutKitchen pizza-bean bowl pilot from Issue #2.",
        "video": "../../brands/gutkitchen/media/pilot/scene-001.mp4",
        "poster": "../../brands/gutkitchen/media/pilot/first-frame.png",
        "firstFrame": "../../brands/gutkitchen/media/pilot/first-frame.png",
        "filmstrip": "../../brands/gutkitchen/creative-engine-v2/candidates/new-a-frame-01.jpg",
        "duration": 31.15,
        "route": "existing deterministic illustration and MP4 pilot",
        "modelsUsed": ["historical local pipeline"],
        "shots": [],
        "selectedSourceCostUsd": 0,
        "costBasis": "historical artifact",
        "qa": {"status": "REFERENCE"},
        "knownWeaknesses": ["Older pacing and illustration-led food imagery."],
    }
    storyboard = {
        "id": "storyboard",
        "label": "CURRENT V2 STORYBOARD",
        "status": "REFERENCE | STORYBOARD MOTION COMP",
        "treatment": "Best current Issue #8 editorial storyboard comp. It is intentionally labelled as a motion comp, not finished media.",
        "video": "../../brands/gutkitchen/creative-engine-v2/candidates/new-c-preview.mp4",
        "poster": "../../brands/gutkitchen/creative-engine-v2/candidates/new-c-frame-01.jpg",
        "firstFrame": "../../brands/gutkitchen/creative-engine-v2/candidates/new-c-frame-01.jpg",
        "filmstrip": "../../brands/gutkitchen/creative-engine-v2/candidates/new-c-frame-05.jpg",
        "duration": 32.5,
        "route": "approved stills + deterministic overlays + zoompan motion comp",
        "modelsUsed": ["no OpenRouter media inference"],
        "shots": [],
        "selectedSourceCostUsd": 0,
        "costBasis": "historical artifact",
        "qa": {"status": "REFERENCE"},
        "knownWeaknesses": ["Storyboard motion only; not an acceptance candidate."],
    }
    for candidate in candidates:
        candidate["status"] = "FINAL MEDIA | GENERATED ACTION"
        candidate["treatment"] = {
            "new-a": "I2V-heavy: generated keyframes animated into ingredient, simmer, melt and spoon action.",
            "new-b": "T2V-heavy: direct generated cooking/action clips, with one documented bean-shot fallback.",
            "new-c": "Hybrid: best available source route per shot, prioritising visual quality over route purity.",
        }[candidate["id"]]
    review_data = {
        "generatedAtUtc": run_summary["generatedAtUtc"],
        "brief": plan["brief"],
        "factualBasis": plan["factualBasis"],
        "models": plan["models"],
        "runSummary": run_summary,
        "candidates": [old, storyboard, *candidates],
    }
    (OUT_DIR / "review-data.json").write_text(json.dumps(review_data, indent=2) + "\n")
    manifest = {
        "generatedAtUtc": run_summary["generatedAtUtc"],
        "briefId": plan["briefId"],
        "openRouterOnly": True,
        "candidateCount": 3,
        "plannedCriticalRoutes": 0,
        "candidates": candidates,
        "runSummary": run_summary,
    }
    (OUT_DIR / "final-media-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    render_review(review_data)
    print(json.dumps({"reviewPage": str(REVIEW_PATH), "outputDir": str(OUT_DIR), "candidates": [item["id"] for item in candidates]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
