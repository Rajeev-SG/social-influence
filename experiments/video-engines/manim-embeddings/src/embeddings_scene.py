from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    Circle,
    Create,
    DashedLine,
    Dot,
    Ellipse,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MovingCameraScene,
    RoundedRectangle,
    Text,
    ValueTracker,
    VGroup,
    VMobject,
    Wait,
    linear,
    smooth,
)


ROOT = Path(__file__).resolve().parents[1]
TIMING = json.loads((ROOT / "src/timing.json").read_text())

BG = "#07111B"
PANEL = "#0B1B26"
PANEL_2 = "#102633"
INK = "#F2F0E8"
MUTED = "#8EA8B5"
LINE = "#244654"
CYAN = "#76F7D2"
BLUE = "#5B9DFF"
VIOLET = "#B58CFF"
AMBER = "#FFB86B"
FONT = "Avenir Next"
MONO = "Menlo"


def text(value: str, color: str = INK, font: str = FONT, size: float = 0.32) -> Text:
    return Text(value, font=font, color=color).scale(size / 0.32)


def fit_width(mobject: VMobject, width: float) -> VMobject:
    return mobject.scale(width / mobject.width)


def rounded_box(width: float, height: float, fill: str = PANEL, stroke: str = LINE) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.10,
        fill_color=fill,
        fill_opacity=0.96,
        stroke_color=stroke,
        stroke_width=1.6,
    )


def word_chip(label: str, accent: str = CYAN, width: float = 1.12) -> VGroup:
    box = rounded_box(width, 0.42, PANEL_2, accent)
    label_mobject = fit_width(text(label, INK, FONT, 0.23), width * 0.72)
    label_mobject.move_to(box)
    bar = Line(ORIGIN, RIGHT * 0.16, stroke_color=accent, stroke_width=4).next_to(box, LEFT, buff=0.12)
    return VGroup(box, label_mobject, bar)


def pin(label: str, position: np.ndarray, accent: str = CYAN, side: str = "right") -> VGroup:
    position = np.array(position, dtype=float)
    halo = Circle(radius=0.16, stroke_color=accent, stroke_width=1.2, stroke_opacity=0.32).move_to(position)
    core = Dot(position, radius=0.075, color=accent)
    label_mobject = text(label, INK, FONT, 0.20)
    if side == "left":
        label_mobject.next_to(core, LEFT, buff=0.12)
    elif side == "up":
        label_mobject.next_to(core, UP, buff=0.12)
    else:
        label_mobject.next_to(core, RIGHT, buff=0.12)
    return VGroup(halo, core, label_mobject)


def distance_label(value: str, position: np.ndarray, accent: str = CYAN) -> VGroup:
    badge = rounded_box(0.62, 0.27, "#0E2631", accent)
    label = text(value, accent, MONO, 0.18).move_to(badge)
    group = VGroup(badge, label).move_to(position)
    return group


def make_background() -> VGroup:
    glow_a = Ellipse(width=5.8, height=3.2, fill_color="#0D2A39", fill_opacity=0.36, stroke_width=0).move_to([0, 2.8, 0])
    glow_b = Ellipse(width=4.8, height=2.4, fill_color="#14213E", fill_opacity=0.18, stroke_width=0).move_to([0, -2.9, 0])
    grid = VGroup()
    for x in np.linspace(-2.35, 2.35, 11):
        grid.add(Line([x, -3.9, 0], [x, 3.9, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.16))
    for y in np.linspace(-3.6, 3.6, 11):
        grid.add(Line([-2.35, y, 0], [2.35, y, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.12))
    return VGroup(glow_a, glow_b, grid)


def make_topline(duration: float, clock: ValueTracker) -> VGroup:
    eyebrow = text("EMBEDDINGS  /  MEANING MAP", CYAN, MONO, 0.16)
    fit_width(eyebrow, 2.35).to_edge(UP, buff=0.22).to_edge(LEFT, buff=0.35)
    progress_base = Line([-2.02, 3.52, 0], [2.02, 3.52, 0], stroke_color=LINE, stroke_width=2).set_opacity(0.52)
    progress = Line([-2.02, 3.52, 0], [-2.02, 3.52, 0], stroke_color=CYAN, stroke_width=4)

    def update_progress(m: Line, _dt: float | None = None):
        amount = max(0.0, min(1.0, clock.get_value() / duration))
        if amount <= 0.001:
            m.set_opacity(0)
        else:
            m.set_opacity(1)
            m.put_start_and_end_on(np.array([-2.02, 3.52, 0]), np.array([-2.02 + 4.04 * amount, 3.52, 0]))

    progress.add_updater(update_progress)
    return VGroup(eyebrow, progress_base, progress)


class CaptionBank(VGroup):
    def __init__(self, cues: list[dict], clock: ValueTracker):
        super().__init__()
        self.cues = cues
        self.clock = clock
        self.layers = []
        for index, cue in enumerate(cues):
            words = cue["text"].split()
            lines = []
            while words:
                take = 4 if len(words) > 6 else len(words)
                lines.append(" ".join(words[:take]))
                words = words[take:]
            label = text("\n".join(lines), INK, FONT, 0.205)
            fit_width(label, 3.62)
            label.move_to([0, -3.27, 0])
            bg = rounded_box(4.08, 0.72, "#0A1923", "#2A5261").move_to([0, -3.27, 0])
            bar = RoundedRectangle(
                width=0.08,
                height=0.38,
                corner_radius=0.03,
                fill_color=CYAN if index != 3 else AMBER,
                fill_opacity=1,
                stroke_width=0,
            ).next_to(bg, LEFT, buff=0.16)
            layer = VGroup(bg, bar, label)
            layer.set_opacity(0)
            self.layers.append(layer)
            self.add(layer)
        self.add_updater(self._update)

    def _update(self, _m: VMobject, _dt: float | None = None):
        now = self.clock.get_value()
        for layer, cue in zip(self.layers, self.cues):
            fade = min((now - cue["start"]) / 0.12, (cue["end"] - now) / 0.12, 1.0)
            layer.set_opacity(max(0.0, min(1.0, fade)))


def make_hook() -> VGroup:
    title = text("A WORD IS NOT\nITS MEANING.", INK, FONT, 0.60)
    fit_width(title, 3.62).move_to([0, 1.72, 0])
    underline = Line([-1.65, 0.93, 0], [0.88, 0.93, 0], stroke_color=CYAN, stroke_width=4)
    chips = VGroup(
        word_chip("puppy", CYAN, 1.15).move_to([-1.08, -0.18, 0]).rotate(-0.12),
        word_chip("dog", BLUE, 1.02).move_to([0.70, 0.10, 0]).rotate(0.10),
        word_chip("car", AMBER, 0.92).move_to([-0.10, -1.35, 0]).rotate(-0.08),
    )
    orbit_a = Ellipse(width=3.35, height=1.12, stroke_color=BLUE, stroke_width=1.6).set_stroke(opacity=0.24).rotate(0.18).move_to([0, -0.52, 0])
    orbit_b = Ellipse(width=2.55, height=0.82, stroke_color=CYAN, stroke_width=1.6).set_stroke(opacity=0.28).rotate(-0.32).move_to([0, -0.52, 0])
    caption = text("no built-in address", MUTED, MONO, 0.18).move_to([0, -2.08, 0])
    return VGroup(orbit_a, orbit_b, title, underline, chips, caption)


def make_coordinates() -> VGroup:
    title = fit_width(text("NUMBERS  ->  COORDINATES", CYAN, MONO, 0.18), 3.1).move_to([0, 2.22, 0])
    vector_card = rounded_box(2.85, 1.12, PANEL_2, CYAN).move_to([0, 0.62, 0])
    word = fit_width(text("puppy", INK, FONT, 0.30), 1.20).move_to([0, 0.91, 0])
    values = fit_width(text("[ 0.82   -0.31   0.56 ]", CYAN, MONO, 0.22), 2.34).move_to([0, 0.43, 0])
    card = VGroup(vector_card, word, values)
    arrow = Line([0, -0.02, 0], [0, -0.78, 0], stroke_color=CYAN, stroke_width=2.5)
    target = VGroup(
        rounded_box(3.82, 1.78, "#091923", LINE).move_to([0, -1.38, 0]),
        Line([-1.72, -1.02, 0], [1.72, -1.02, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Line([-1.72, -1.42, 0], [1.72, -1.42, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Line([-1.72, -1.82, 0], [1.72, -1.82, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Line([-1.18, -2.16, 0], [-1.18, -0.62, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Line([-0.38, -2.16, 0], [-0.38, -0.62, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Line([0.42, -2.16, 0], [0.42, -0.62, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Line([1.22, -2.16, 0], [1.22, -0.62, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.52),
        Dot([-0.38, -1.52, 0], radius=0.09, color=CYAN),
        fit_width(text("meaning map", MUTED, MONO, 0.17), 1.42).move_to([0, -0.82, 0]),
    )
    return VGroup(title, card, arrow, target)


def make_map_shell() -> VGroup:
    frame = rounded_box(3.88, 4.72, "#081721", "#285463").move_to([0, -0.18, 0])
    grid = VGroup()
    for x in np.linspace(-1.72, 1.72, 7):
        grid.add(Line([x, -2.26, 0], [x, 1.90, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.42))
    for y in np.linspace(-2.15, 1.85, 7):
        grid.add(Line([-1.78, y, 0], [1.78, y, 0], stroke_color=LINE, stroke_width=1).set_opacity(0.34))
    axes = VGroup(
        Line([-1.86, -0.18, 0], [1.86, -0.18, 0], stroke_color=BLUE, stroke_width=1.2).set_opacity(0.52),
        Line([0, -2.32, 0], [0, 1.98, 0], stroke_color=BLUE, stroke_width=1.2).set_opacity(0.52),
    )
    label = text("MEANING MAP", CYAN, MONO, 0.16).move_to([0, 1.60, 0])
    hint = text("close = similar", MUTED, MONO, 0.15).move_to([0, -1.98, 0])
    return VGroup(frame, grid, axes, label, hint)


def make_map_details() -> tuple[VGroup, dict[str, VGroup], VGroup]:
    positions = {
        "puppy": np.array([-0.78, 0.28, 0]),
        "dog": np.array([-0.34, -0.17, 0]),
        "kitten": np.array([0.72, 0.68, 0]),
        "car": np.array([1.18, -1.36, 0]),
    }
    pins = {
        "puppy": pin("puppy", positions["puppy"], CYAN, "up"),
        "dog": pin("dog", positions["dog"], BLUE, "left"),
        "kitten": pin("kitten", positions["kitten"], VIOLET, "right"),
        "car": pin("car", positions["car"], AMBER, "right"),
    }
    neighbourhood = VGroup(
        Ellipse(width=2.18, height=1.52, fill_color=CYAN, fill_opacity=0.055, stroke_color=CYAN, stroke_width=1.6)
        .set_stroke(opacity=0.32)
        .rotate(-0.18)
        .move_to([-0.52, 0.08, 0]),
        text("RELATED WORDS", CYAN, MONO, 0.14).move_to([-1.02, -0.86, 0]),
    )
    return VGroup(neighbourhood, *pins.values()), pins, neighbourhood


def make_distance_detail(positions: dict[str, np.ndarray]) -> VGroup:
    close = DashedLine(positions["puppy"], positions["dog"], stroke_color=CYAN, stroke_width=3.2, dash_length=0.08)
    near = DashedLine(positions["puppy"], positions["kitten"], stroke_color=VIOLET, stroke_width=2.2, dash_length=0.08)
    far = DashedLine(positions["puppy"], positions["car"], stroke_color=AMBER, stroke_width=2.4, dash_length=0.10)
    close_label = distance_label("0.18", np.array([-0.22, -0.42, 0]), CYAN)
    near_label = distance_label("0.47", np.array([0.18, 0.96, 0]), VIOLET)
    far_label = distance_label("1.62", np.array([0.10, -0.92, 0]), AMBER)
    comparison = VGroup(
        rounded_box(1.62, 0.34, "#0D2C2D", CYAN).move_to([-1.02, -2.57, 0]),
        fit_width(text("NEAR = SIMILAR", CYAN, MONO, 0.14), 1.28).move_to([-1.02, -2.57, 0]),
        rounded_box(1.62, 0.34, "#2B231A", AMBER).move_to([1.02, -2.57, 0]),
        fit_width(text("FAR = DIFFERENT", AMBER, MONO, 0.14), 1.28).move_to([1.02, -2.57, 0]),
    )
    return VGroup(close, near, far, close_label, near_label, far_label, comparison)


def make_ending() -> VGroup:
    top = text("EMBEDDINGS", CYAN, MONO, 0.19).move_to([0, 2.36, 0])
    title = fit_width(text("RELATIONSHIPS\nYOU CAN MEASURE.", INK, FONT, 0.47), 3.60).move_to([0, 1.72, 0])
    rule = Line([-1.45, 0.94, 0], [1.45, 0.94, 0], stroke_color=CYAN, stroke_width=3)
    trio = VGroup(
        word_chip("near", CYAN, 0.90).move_to([-1.12, 0.20, 0]),
        text("=", MUTED, MONO, 0.30).move_to([0, 0.20, 0]),
        word_chip("related", BLUE, 1.22).move_to([1.10, 0.20, 0]),
    )
    return VGroup(top, title, rule, trio)


class EmbeddingsScene(MovingCameraScene):
    def construct(self):
        duration = TIMING["duration"]
        cues = TIMING["cues"]
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        background = make_background()
        topline = make_topline(duration, clock)
        captions = CaptionBank(cues, clock)
        self.add(background, topline, captions)

        hook = make_hook()
        coordinates = make_coordinates()
        map_shell = make_map_shell()
        map_details, pins, neighbourhood = make_map_details()
        distance_detail = make_distance_detail({
            "puppy": np.array([-0.78, 0.28, 0]),
            "dog": np.array([-0.34, -0.17, 0]),
            "kitten": np.array([0.72, 0.68, 0]),
            "car": np.array([1.18, -1.36, 0]),
        })
        ending = make_ending()
        map_world = VGroup(map_shell, neighbourhood, *pins.values())
        map_spatial = VGroup(
            map_shell[0],
            map_shell[1],
            map_shell[2],
            neighbourhood[0],
            pins["puppy"][0],
            pins["puppy"][1],
            pins["dog"][0],
            pins["dog"][1],
            pins["kitten"][0],
            pins["kitten"][1],
            pins["car"][0],
            pins["car"][1],
        )
        ending_background_type = VGroup(
            map_shell[3],
            map_shell[4],
            *[pins[key][2] for key in ("puppy", "dog", "kitten", "car")],
        )

        def hold_until(target: float):
            remaining = target - clock.get_value()
            if remaining > 0.001:
                self.wait(remaining)

        def cue_window(index: int) -> tuple[float, float]:
            return cues[index]["start"], cues[index]["end"]

        # 1. Hook: the problem statement, with unplaced words.
        start, end = cue_window(0)
        hold_until(start)
        self.play(FadeIn(hook, shift=UP * 0.12), run_time=0.65, rate_func=smooth)
        hold_until(end)

        # 2. Coordinates: a word becomes a vector and then a map address.
        start, end = cue_window(1)
        hold_until(start)
        self.play(FadeOut(hook), FadeIn(coordinates, shift=UP * 0.12), run_time=0.72, rate_func=smooth)
        self.play(
            coordinates[1].animate.scale(1.04).shift(UP * 0.05),
            Create(coordinates[2]),
            run_time=0.82,
            rate_func=smooth,
        )
        hold_until(end)

        # 3. Neighbourhood: pins land in a shared spatial field.
        start, end = cue_window(2)
        hold_until(start)
        self.play(FadeOut(coordinates), FadeIn(map_shell, shift=UP * 0.12), run_time=0.70, rate_func=smooth)
        self.play(FadeIn(neighbourhood, shift=UP * 0.04), run_time=0.34, rate_func=smooth)
        pin_animations = [FadeIn(pins[key], shift=UP * 0.16) for key in ("puppy", "dog", "kitten", "car")]
        self.play(LaggedStart(*pin_animations, lag_ratio=0.22), run_time=min(3.20, max(0.8, end - start - 1.25)), rate_func=smooth)
        hold_until(end)

        # 4. Distance: the same field becomes a measurable relationship.
        start, end = cue_window(3)
        hold_until(start)
        self.play(
            FadeOut(neighbourhood[1]),
            Create(distance_detail[0]),
            Create(distance_detail[1]),
            Create(distance_detail[2]),
            run_time=0.92,
            rate_func=smooth,
        )
        self.play(FadeIn(distance_detail[3:], shift=UP * 0.06), run_time=0.66, rate_func=smooth)
        hold_until(end)

        # 5. Ending: pull the analogy together and make the takeaway explicit.
        start, end = cue_window(4)
        hold_until(start)
        self.play(
            FadeOut(distance_detail),
            FadeOut(ending_background_type),
            run_time=0.22,
            rate_func=smooth,
        )
        self.play(
            map_spatial.animate.scale(0.72).shift(DOWN * 1.00).set_opacity(0.16),
            FadeIn(ending, shift=UP * 0.12),
            run_time=0.52,
            rate_func=smooth,
        )
        hold_until(end)

        # Keep the final frame present through the narration tail and fade the caption.
        hold_until(duration)
        self.wait(0.12)
