from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import movis as mv

from design import (
    AMBER,
    BACKGROUND,
    BLUE,
    CORAL,
    CYAN,
    FONT_MONO,
    FONT_TITLE,
    H,
    INK,
    LINE,
    MUTED,
    SURFACE,
    W,
    bezier,
    clamp,
    dashed_polyline,
    draw_arrow,
    draw_ball,
    draw_bucket,
    draw_knob,
    draw_tracking_text,
    ease,
    font,
    lerp,
    mix,
    rounded_panel,
)

ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src/timing.json").read_text())
CUES = TIMING["cues"]


def scene_at(t: float) -> int:
    bounds = [0.0, CUES[2]["start"], CUES[4]["start"], CUES[5]["start"]]
    return max(i for i, start in enumerate(bounds) if t >= start)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt) -> float:
    return draw.textlength(text, font=fnt)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and text_width(draw, candidate, fnt) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_header(draw: ImageDraw.ImageDraw, t: float) -> None:
    scene = scene_at(t)
    labels = ["01 / MISS", "02 / CORRECT", "03 / AI LOOP", "04 / REPEAT"]
    draw_tracking_text(draw, (78, 72), "HOW AI LEARNS", font(22, True), CYAN, 3.3)
    draw_tracking_text(draw, (830, 72), labels[scene], font(21, True), MUTED, 2.5)
    draw.line((78, 118, 1002, 118), fill=(*LINE, 180), width=2)
    progress = clamp(t / TIMING["duration"])
    draw.line((78, 118, lerp(78, 1002, progress), 118), fill=(*CYAN, 235), width=5)


def draw_caption(draw: ImageDraw.ImageDraw, t: float) -> None:
    cue = next((c for c in CUES if c["start"] <= t < c["end"]), None)
    if cue is None:
        return
    fade = ease(t, cue["start"], cue["start"] + 0.18)
    alpha = round(255 * fade)
    rounded_panel(draw, (70, 1565, 1010, 1842), fill=(8, 22, 31), outline=(31, 63, 72), radius=38)
    draw.rounded_rectangle((102, 1602, 116, 1802), radius=7, fill=(*CYAN, alpha))
    for size in (48, 45, 42, 39):
        fnt = font(size)
        lines = wrap_text(draw, cue["text"], fnt, 824)
        if len(lines) <= 4:
            break
    line_height = round(size * 1.16)
    y = 1604 if len(lines) <= 3 else 1587
    for line in lines:
        draw.text((152, y), line, font=fnt, fill=(*INK, alpha))
        y += line_height


def draw_transition(draw: ImageDraw.ImageDraw, t: float) -> None:
    scene = scene_at(t)
    if scene == 0:
        return
    bounds = [0.0, CUES[2]["start"], CUES[4]["start"], CUES[5]["start"]]
    local = t - bounds[scene]
    if local > 0.36:
        return
    p = ease(local, 0.0, 0.36, 2)
    x = lerp(-310, W + 180, p)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(band)
    bdraw.polygon([(x - 170, 0), (x + 60, 0), (x + 270, H), (x + 40, H)], fill=(*CYAN, 38))
    bdraw.line((x + 64, 0, x + 272, H), fill=(*INK, 130), width=3)
    draw._image.alpha_composite(band)


def draw_miss_scene(img: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    beat = CUES[1]["start"]
    handoff = t >= beat + 0.14
    draw.text((82, 186), "NOTICE THE MISS." if handoff else "MAKE A GUESS.", font=font(88), fill=INK)
    sweep = (t - beat) / 0.34
    if 0.0 <= sweep <= 1.0:
        x = lerp(-180, W + 180, sweep)
        band = Image.new("RGBA", (W, 340), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(band)
        bdraw.polygon([(x - 110, 0), (x + 35, 0), (x + 170, 340), (x + 25, 340)], fill=(*CYAN, 42))
        bdraw.line((x + 35, 0, x + 170, 340), fill=(*INK, 145), width=3)
        img.alpha_composite(band, (0, 150))
    draw.text((84, 292), "A visible mistake creates useful information.", font=font(34), fill=(*MUTED, 235))

    p0, p1, p2 = (118, 1322), (515, 575), (578, 862)
    target = (766, 862)
    dashed_polyline(draw, [bezier(p0, p1, p2, i / 48) for i in range(49)], CORAL, width=5, dash=18, gap=13, alpha=185)
    draw_bucket(draw, *target, scale=1.08)
    throw_p = ease(t, CUES[1]["start"] + 0.12, CUES[1]["end"] - 0.12, 2)
    ball = bezier(p0, p1, p2, throw_p)
    draw_ball(draw, *ball, radius=25, color=AMBER if throw_p < 0.98 else CORAL)
    if throw_p > 0.72:
        reveal = ease(t, CUES[1]["end"] - 0.72, CUES[1]["end"] - 0.12)
        draw_arrow(draw, (585, 910), (753, 910), CORAL, width=5, head=20, alpha=round(220 * reveal))
        draw.text((518, 944), "THIS FAR OFF", font=font(25, True), fill=(*CORAL, round(255 * reveal)))
        draw.line((585, 885, 753, 885), fill=(*CORAL, round(180 * reveal)), width=3)
    draw.text((82, 1452), "THE MISS IS NOT FAILURE. IT IS A MEASUREMENT.", font=font(24, True), fill=(*CYAN, 235))


def draw_adjust_scene(img: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    draw.text((82, 186), "FEEDBACK", font=font(92), fill=INK)
    draw.text((82, 282), "BECOMES A CORRECTION.", font=font(72), fill=CYAN)
    draw.text((84, 382), "Same bucket. A better-informed attempt.", font=font(33), fill=MUTED)

    old = [(118, 1322), (515, 575), (578, 862)]
    new = [(118, 1322), (555, 655), (765, 856)]
    dashed_polyline(draw, [bezier(*old, i / 48) for i in range(49)], CORAL, width=4, dash=13, gap=13, alpha=125)
    dashed_polyline(draw, [bezier(*new, i / 48) for i in range(49)], CYAN, width=5, dash=18, gap=11, alpha=220)
    draw_bucket(draw, 766, 862, scale=1.08)

    feedback = ease(t, CUES[2]["start"] + 0.16, CUES[2]["start"] + 1.45)
    draw_arrow(draw, (594, 932), (742, 932), CORAL, width=6, head=22, alpha=round(235 * feedback))
    draw.text((528, 973), "MEASURE THE GAP", font=font(24, True), fill=(*CORAL, round(255 * feedback)))

    adjust = ease(t, CUES[3]["start"] + 0.18, CUES[3]["end"] - 0.22, 2)
    ball = bezier(*new, adjust)
    draw_ball(draw, *ball, radius=25, color=CYAN)
    draw_knob(draw, 910, 1195, 0.25 + adjust * 0.62, color=CYAN, radius=58)
    draw.text((845, 1290), "AIM", font=font(22, True), fill=(*MUTED, 235))

    stages = ["MISS", "FEEDBACK", "ADJUST", "RETRY"]
    active = 0 if t < CUES[2]["start"] else 1 if t < CUES[3]["start"] + 0.25 else 2 if adjust < 0.86 else 3
    rail_y = 1425
    draw.line((128, rail_y, 886, rail_y), fill=(*LINE, 220), width=4)
    for i, label in enumerate(stages):
        x = 128 + i * 253
        color = CYAN if i <= active else LINE
        draw.ellipse((x - 13, rail_y - 13, x + 13, rail_y + 13), fill=(*color, 255))
        label_font = font(22, True)
        label_width = draw.textlength(label, font=label_font)
        draw.text(
            (x - label_width / 2, rail_y + 32),
            label,
            font=label_font,
            fill=(*(INK if i <= active else MUTED), 235),
        )


def draw_ai_scene(img: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    local = t - CUES[4]["start"]
    duration = CUES[5]["start"] - CUES[4]["start"]
    reveal = ease(local, 0.0, 0.65)
    error_stage = ease(local, 1.25, 2.75)
    adjust = ease(local, 3.15, duration - 1.05, 2)
    draw.text((82, 182), "AI USES THE", font=font(88), fill=(*INK, round(255 * reveal)))
    draw.text((82, 278), "SAME LOOP.", font=font(94), fill=(*CYAN, round(255 * reveal)))

    # The human analogy remains visible as a small through-line above the AI diagram.
    draw_bucket(draw, 895, 330, scale=0.36, target=False)
    dashed_polyline(draw, [(708, 330), (785, 278), (856, 320)], CYAN, width=3, dash=10, gap=9, alpha=round(165 * reveal))
    draw_ball(draw, 690, 340, radius=12, color=AMBER, alpha=round(255 * reveal))

    rounded_panel(draw, (78, 525, 356, 815), outline=CYAN, radius=34)
    rounded_panel(draw, (724, 525, 1002, 815), outline=BLUE, radius=34)
    draw_tracking_text(draw, (118, 570), "GUESS", font(22, True), CYAN, 2.2)
    draw_tracking_text(draw, (764, 570), "RIGHT ANSWER", font(22, True), BLUE, 2.0)
    draw.text((120, 627), f"{lerp(6.4, 7.72, adjust):.1f}", font=font(100), fill=INK)
    draw.text((766, 627), "8.0", font=font(100), fill=INK)
    draw.text((120, 754), "MODEL OUTPUT", font=font(18, True), fill=MUTED)
    draw.text((766, 754), "TRAINING LABEL", font=font(18, True), fill=MUTED)

    gap_left = 386
    gap_right = 694
    shrink = adjust
    end_x = lerp(gap_right, lerp(gap_right, gap_left, 0.82), shrink)
    draw.line((gap_left, 680, end_x, 680), fill=(*CORAL, round(245 * error_stage)), width=8)
    draw.line((gap_left, 650, gap_left, 710), fill=(*CORAL, 235), width=4)
    draw.line((gap_right, 650, gap_right, 710), fill=(*CORAL, round(185 * error_stage)), width=4)
    draw.text((452, 720), f"ERROR {lerp(1.6, 0.28, adjust):.1f}", font=font(25, True), fill=(*CORAL, round(255 * error_stage)))

    draw_arrow(draw, (540, 824), (540, 912), AMBER, width=5, head=19, alpha=round(225 * error_stage))
    draw_tracking_text(draw, (350, 868), "FEEDBACK ENTERS THE SETTINGS", font(20, True), AMBER, 1.6)

    cols, rows = 6, 3
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            base = ((idx * 37) % 101) / 100
            value = clamp(base * 0.48 + adjust * (0.18 + ((idx * 17) % 19) / 42))
            x = 170 + col * 148
            y = 1005 + row * 130
            draw_knob(draw, x, y, value, color=CYAN if (idx % 4) else BLUE, radius=38, alpha=220)
    draw.text((82, 1396), "PREDICT  →  COMPARE  →  NUDGE SETTINGS", font=font(27, True), fill=(*INK, 235))
    draw.text((82, 1440), "The analogy scales to many internal adjustments.", font=font(28), fill=MUTED)


def draw_repeat_scene(img: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    local = t - CUES[5]["start"]
    reveal = ease(local, 0.0, 0.55)
    draw.text((82, 182), "REPEAT TURNS", font=font(88), fill=(*INK, round(255 * reveal)))
    draw.text((82, 278), "ERROR INTO SIGNAL.", font=font(78), fill=(*CYAN, round(255 * reveal)))

    chart = (112, 615, 738, 1260)
    draw.line((chart[0], chart[3], chart[2], chart[3]), fill=(*LINE, 235), width=4)
    draw.line((chart[0], chart[1], chart[0], chart[3]), fill=(*LINE, 235), width=4)
    values = [180, 92, 41, 12]
    points = []
    for i, value in enumerate(values):
        x = lerp(170, 682, i / 3)
        y = lerp(720, 1172, i / 3) + math.sin(i * 1.4) * 18
        points.append((x, y))
    reveal_p = ease(local, 0.35, 1.75, 2)
    visible = max(2, round(lerp(2, len(points), reveal_p)))
    draw.line(points[:visible], fill=(*CYAN, 245), width=8, joint="curve")
    for i, ((x, y), value) in enumerate(zip(points, values)):
        if i >= visible:
            continue
        draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(*CYAN, 255), outline=(*INK, 220), width=3)
        draw.text((x - 31, y - 64), str(value), font=font(24, True), fill=(*INK, 235))
    draw_tracking_text(draw, (112, 572), "ILLUSTRATIVE ERROR", font(20, True), MUTED, 1.9)
    draw.text((112, 1322), "SMALLER FEEDBACK", font=font(22, True), fill=CYAN)
    draw.text((112, 1363), "means a better-informed adjustment.", font=font(28), fill=INK)

    # The original bucket now receives the converging attempts.
    draw_bucket(draw, 885, 875, scale=0.82)
    for i in range(4):
        start = (758 + i * 22, 1270 - i * 45)
        end = (865 + i * 10, 872 + i * 7)
        points_curve = [bezier(start, (865, 530 + i * 38), end, j / 26) for j in range(27)]
        dashed_polyline(draw, points_curve, CYAN if i == 3 else BLUE, width=3 + i, dash=10 + i * 2, gap=12, alpha=105 + i * 34)
    draw_ball(draw, 882, 871, radius=19, color=CYAN, alpha=round(255 * ease(local, 0.85, 1.55)))
    draw_tracking_text(draw, (765, 1328), "MISS → FEEDBACK → ADJUST", font(18, True), CYAN, 1.3)
    draw.text((765, 1372), "Then run it again.", font=font(29), fill=INK)

    end_p = ease(t, CUES[5]["end"] - 0.12, CUES[5]["end"] + 0.34, 2)
    if end_p <= 0.0:
        return
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay, "RGBA")
    odraw.rectangle((0, 500, W, 1500), fill=(7, 16, 25, round(248 * end_p)))
    img.alpha_composite(overlay)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_tracking_text(draw, (82, 590), "THE FEEDBACK LOOP", font(24, True), CYAN, 3.0)
    centers = ((225, 895), (540, 895), (855, 895))
    labels = ("MISS", "MEASURE", "ADJUST")
    for i, ((x, y), label) in enumerate(zip(centers, labels)):
        node_reveal = ease(t, CUES[5]["end"] - 0.08 + i * 0.14, CUES[5]["end"] + 0.24 + i * 0.14)
        radius = lerp(38, 82, node_reveal)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*SURFACE, round(235 * end_p)), outline=(*CYAN, round(245 * end_p)), width=5)
        draw.text((x, y), str(i + 1), font=font(50), fill=(*INK, round(255 * node_reveal)), anchor="mm")
        draw.text((x, y + 118), label, font=font(25, True), fill=(*INK, round(235 * node_reveal)), anchor="mm")
        if i < 2:
            draw_arrow(draw, (x + 105, y), (centers[i + 1][0] - 105, y), CYAN, width=6, head=23, alpha=round(220 * end_p))

    loop_y = 1125
    draw.arc((195, loop_y - 125, 885, loop_y + 125), 18, 162, fill=(*BLUE, round(185 * end_p)), width=6)
    draw_arrow(draw, (844, loop_y + 88), (885, loop_y + 22), BLUE, width=5, head=18, alpha=round(210 * end_p))
    draw.text((540, 1240), "REPEAT. THE ERROR GETS SMALLER.", font=font(48), fill=(*INK, round(255 * end_p)), anchor="mm")
    draw.text((540, 1322), "That is how AI learns from mistakes.", font=font(34), fill=(*CYAN, round(235 * end_p)), anchor="mm")


class FilmLayer:
    def __init__(self, size: tuple[int, int], duration: float) -> None:
        self.size = size
        self.duration = duration
        self._frame_rate = TIMING["fps"]

    def get_key(self, time: float) -> int:
        return round(time * self._frame_rate)

    def __call__(self, time: float) -> np.ndarray:
        img = BACKGROUND.copy()
        draw = ImageDraw.Draw(img, "RGBA")
        scene = scene_at(time)
        if scene == 0:
            draw_miss_scene(img, draw, time)
        elif scene == 1:
            draw_adjust_scene(img, draw, time)
        elif scene == 2:
            draw_ai_scene(img, draw, time)
        else:
            draw_repeat_scene(img, draw, time)
        draw_caption(draw, time)
        draw_header(draw, time)
        draw_transition(draw, time)
        return np.asarray(img, dtype=np.uint8)


def build_composition() -> mv.layer.Composition:
    scene = mv.layer.Composition(size=(W, H), duration=TIMING["duration"])
    scene.add_layer(FilmLayer((W, H), TIMING["duration"]), name="film")
    scene.add_layer(
        mv.layer.Audio(str(ROOT / "assets/audio/narration.wav")),
        name="narration",
        audio_level=0.0,
        audio=True,
    )
    scene.add_layer(
        mv.layer.Audio(str(ROOT / "assets/audio/soundscape.wav")),
        name="sound_design",
        audio_level=-7.5,
        audio=True,
    )
    return scene


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "deliverables/final.mp4")
    parser.add_argument("--preview-level", type=int, default=1)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--crf", type=int, default=18)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    scene = build_composition()
    started = time.perf_counter()
    with scene.preview(level=args.preview_level):
        scene.write_video(
            str(args.output),
            fps=args.fps,
            codec="libx264",
            pixelformat="yuv420p",
            audio=True,
            audio_codec="aac",
            output_params=[
                "-preset",
                "slow",
                "-crf",
                str(args.crf),
                "-movflags",
                "+faststart",
                "-ar",
                "48000",
            ],
        )
    elapsed = time.perf_counter() - started
    print(f"MOVIS_RENDER_SECONDS={elapsed:.3f}")
    print(f"MOVIS_OUTPUT={args.output}")


if __name__ == "__main__":
    main()
