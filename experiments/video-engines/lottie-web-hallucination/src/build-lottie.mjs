#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;

const hex = (value, opacity = 100) => {
  const clean = value.replace("#", "");
  return {
    a: 0,
    k: [
      parseInt(clean.slice(0, 2), 16) / 255,
      parseInt(clean.slice(2, 4), 16) / 255,
      parseInt(clean.slice(4, 6), 16) / 255,
      opacity / 100,
    ],
  };
};

const opaqueColor = (value) => {
  const clean = value.replace("#", "");
  return {
    a: 0,
    k: [
      parseInt(clean.slice(0, 2), 16) / 255,
      parseInt(clean.slice(2, 4), 16) / 255,
      parseInt(clean.slice(4, 6), 16) / 255,
      1,
    ],
  };
};
const paintOpacity = (value) => Math.round((value.k?.[3] ?? 1) * 100);

const frame = (seconds) => Math.round(seconds * FPS);
const clampFrame = (value) => Math.max(0, value);

function easing(name = "out", dimensions = 1) {
  const values =
    name === "in"
      ? { x: [0.55], y: [1] }
      : name === "smooth"
        ? { x: [0.42], y: [0] }
        : { x: [0.2], y: [1] };
  return {
    i: { x: Array(dimensions).fill(values.x[0]), y: Array(dimensions).fill(values.y[0]) },
    o: { x: Array(dimensions).fill(name === "in" ? 0.82 : 0.22), y: Array(dimensions).fill(name === "in" ? 0.05 : 1) },
  };
}

function property(values, times, dimensions = 1, easeName = "out") {
  const e = easing(easeName, dimensions);
  return {
    a: 1,
    k: values.map((value, index) => {
      const normalized = dimensions === 1 ? [value] : value;
      const next = values[Math.min(index + 1, values.length - 1)];
      const nextNormalized = dimensions === 1 ? [next] : next;
      return {
        t: times[index],
        s: normalized,
        e: nextNormalized,
        ...(index === values.length - 1 ? {} : e),
      };
    }),
  };
}

const staticProperty = (value) => ({ a: 0, k: value });
const transform = (
  position,
  scale = 100,
  rotation = 0,
  opacity = 100,
  anchor = [0, 0, 0],
) => ({
  o: staticProperty(opacity),
  r: staticProperty(rotation),
  p: staticProperty([...position, 0]),
  a: staticProperty(anchor),
  s: staticProperty([scale, scale, 100]),
});

function animatedTransform(
  position,
  scale = 100,
  opacity = 100,
  duration = 22,
  enter = 10,
  exit = 8,
  fromOffset = [0, -55],
  exitOffset = [0, 35],
  rotation = 0,
  anchor = [0, 0, 0],
) {
  const exitStart = Math.max(enter + 1, duration - exit);
  return {
    o: staticProperty(opacity),
    r: staticProperty(rotation),
    p: property(
      [
        [position[0] + fromOffset[0], position[1] + fromOffset[1], 0],
        [position[0], position[1], 0],
        [position[0], position[1], 0],
        [position[0] + exitOffset[0], position[1] + exitOffset[1], 0],
      ],
      [0, enter, exitStart, duration],
      3,
      "out",
    ),
    a: staticProperty(anchor),
    s: property(
      [
        [scale * 0.94, scale * 0.94, 100],
        [scale, scale, 100],
        [scale, scale, 100],
        [scale * 1.02, scale * 1.02, 100],
      ],
      [0, enter, exitStart, duration],
      3,
      "out",
    ),
  };
}

function imageLayer(id, asset, { x, y, scale = 1, opacity = 100, ip, op, enter = 10, exit = 8, from = [0, -55], to = [0, 35], rotation = 0 }) {
  return {
    ddd: 0,
    ind: 0,
    ty: 2,
    nm: `text:${id}`,
    refId: id,
    sr: 1,
    ks: animatedTransform(
      [x, y],
      scale * 100,
      opacity,
      Math.max(1, op - ip),
      enter,
      exit,
      from,
      to,
      rotation,
      [asset.width / 2, asset.height / 2, 0],
    ),
    ao: 0,
    ip,
    op,
    st: 0,
    w: asset.width,
    h: asset.height,
  };
}

function group(items) {
  return {
    ty: "gr",
    nm: "group",
    it: [
      ...items,
      {
        ty: "tr",
        p: staticProperty([0, 0]),
        a: staticProperty([0, 0]),
        s: staticProperty([100, 100]),
        r: staticProperty(0),
        o: staticProperty(100),
        sk: staticProperty(0),
        sa: staticProperty(0),
      },
    ],
  };
}

function rectShape(width, height, radius, fill, stroke, strokeWidth = 0) {
  const items = [
    { ty: "rc", d: 1, p: staticProperty([width / 2, height / 2]), s: staticProperty([width, height]), r: staticProperty(radius) },
  ];
  if (fill) items.push({ ty: "fl", c: opaqueColor(`#${fill.k.slice(0, 3).map((value) => Math.round(value * 255).toString(16).padStart(2, "0")).join("")}`), o: staticProperty(paintOpacity(fill)), r: 1, bm: 0 });
  if (stroke) items.push({ ty: "st", c: opaqueColor(`#${stroke.k.slice(0, 3).map((value) => Math.round(value * 255).toString(16).padStart(2, "0")).join("")}`), o: staticProperty(paintOpacity(stroke)), w: staticProperty(strokeWidth), lc: 2, lj: 2, ml: 4, bm: 0 });
  return group(items);
}

function ellipseShape(width, height, fill, stroke, strokeWidth = 0) {
  const items = [{ ty: "el", d: 1, p: staticProperty([width / 2, height / 2]), s: staticProperty([width, height]) }];
  if (fill) items.push({ ty: "fl", c: opaqueColor(`#${fill.k.slice(0, 3).map((value) => Math.round(value * 255).toString(16).padStart(2, "0")).join("")}`), o: staticProperty(paintOpacity(fill)), r: 1, bm: 0 });
  if (stroke) items.push({ ty: "st", c: opaqueColor(`#${stroke.k.slice(0, 3).map((value) => Math.round(value * 255).toString(16).padStart(2, "0")).join("")}`), o: staticProperty(paintOpacity(stroke)), w: staticProperty(strokeWidth), lc: 2, lj: 2, ml: 4, bm: 0 });
  return group(items);
}

function shapeLayer(name, shapes, { ip, op, x = 0, y = 0, scale = 100, opacity = 100, enter = 10, exit = 8, from = [0, -35], to = [0, 25], rotation = 0 }) {
  return {
    ddd: 0,
    ind: 0,
    ty: 4,
    nm: name,
    sr: 1,
    ks: animatedTransform([x, y], scale, opacity, Math.max(1, op - ip), enter, exit, from, to, rotation),
    ao: 0,
    shapes,
    ip,
    op,
    st: 0,
    bm: 0,
  };
}

function pathShape(points, closed = false) {
  return {
    ty: "sh",
    d: 1,
    ks: staticProperty({
      i: points.map(() => [0, 0]),
      o: points.map(() => [0, 0]),
      v: points,
      c: closed,
    }),
  };
}

function pathLayer(name, points, { ip, op, color, width = 10, trimStart = 0, trimEnd = 100, trimAt = 12, opacity = 100 }) {
  const trim = {
    ty: "tm",
    s: property([trimStart, trimStart], [0, trimAt], 1, "out"),
    e: property([trimStart, trimEnd], [0, trimAt], 1, "out"),
    o: staticProperty(0),
    m: 1,
    nm: "draw",
  };
  return {
    ddd: 0,
    ind: 0,
    ty: 4,
    nm: name,
    sr: 1,
    ks: {
      o: property([0, opacity], [0, trimAt], 1, "out"),
      r: staticProperty(0),
      p: staticProperty([0, 0, 0]),
      a: staticProperty([0, 0, 0]),
      s: staticProperty([100, 100, 100]),
    },
    ao: 0,
    shapes: [
      group([
        pathShape(points),
        { ty: "st", c: opaqueColor(`#${color.k.slice(0, 3).map((value) => Math.round(value * 255).toString(16).padStart(2, "0")).join("")}`), o: staticProperty(paintOpacity(color)), w: staticProperty(width), lc: 2, lj: 2, ml: 4, bm: 0 },
        trim,
      ]),
    ],
    ip,
    op,
    st: 0,
    bm: 0,
  };
}

function cardLayer(name, { ip, op, x, y, width, height, radius = 48, fill, stroke, strokeWidth = 4, accent = false }) {
  return shapeLayer(
    name,
    [rectShape(width, height, radius, fill, stroke, strokeWidth)],
    {
      ip,
      op,
      x: x - width / 2,
      y: y - height / 2,
      enter: accent ? 14 : 11,
      exit: 7,
      from: [0, accent ? -70 : -45],
      to: [0, 30],
    },
  );
}

function barLayer(name, { ip, op, x, y, width, height = 18, color, delay = 0 }) {
  return shapeLayer(
    name,
    [rectShape(width, height, height / 2, color, null)],
    {
      ip: ip + delay,
      op,
      x: x - width / 2,
      y: y - height / 2,
      enter: 8,
      exit: 5,
      from: [-22, 0],
      to: [18, 0],
    },
  );
}

function sceneCaption(index, timing, assets, ip, op) {
  const item = assets.get(`caption_${String(index + 1).padStart(2, "0")}`);
  return imageLayer(item.id, item, {
    x: WIDTH / 2,
    y: 1738,
    scale: Math.min(1, 920 / item.width),
    ip,
    op: Math.min(op, frame(timing.endSeconds) + 3),
    enter: 6,
    exit: 5,
    from: [0, 28],
    to: [0, 18],
  });
}

async function main() {
  const manifest = JSON.parse(await fs.readFile(path.join(ROOT, "assets", "text-manifest.json"), "utf8"));
  const timings = JSON.parse(await fs.readFile(path.join(ROOT, "assets", "audio", "narration-timing.json"), "utf8"));
  const assets = new Map(manifest.items.map((item) => [item.id, item]));
  const totalFrames = Math.ceil(timings.durationSeconds * FPS);
  const lineStarts = timings.lines.map((line) => frame(line.startSeconds));
  const sceneRanges = [
    [0, lineStarts[2] - 4],
    [lineStarts[2] - 4, lineStarts[3] - 4],
    [lineStarts[3] - 4, lineStarts[5] - 4],
    [lineStarts[5] - 4, lineStarts[6] - 4],
    [lineStarts[6] - 4, totalFrames],
  ];
  const lineRanges = timings.lines.map((line, index) => ({
    ...line,
    ip: clampFrame(frame(line.startSeconds) - (index === 0 ? 2 : 5)),
    op: Math.min(
      totalFrames,
      index < timings.lines.length - 1
        ? clampFrame(frame(timings.lines[index + 1].startSeconds) - 2)
        : totalFrames,
    ),
  }));

  const layers = [];
  const add = (layer) => layers.push(layer);

  // Ambient depth and the orange story rail are the visual through-line.
  add(shapeLayer("ambient-orbit-a", [ellipseShape(520, 520, hex("#63D5FF", 5), hex("#63D5FF", 13), 3)], { ip: 0, op: totalFrames, x: -220, y: 260, opacity: 100, enter: 22, exit: 2, from: [-50, -30], to: [35, 20] }));
  add(shapeLayer("ambient-orbit-b", [ellipseShape(720, 720, hex("#FF8A4C", 4), hex("#FF8A4C", 11), 3)], { ip: 0, op: totalFrames, x: 720, y: 1220, opacity: 100, enter: 22, exit: 2, from: [45, 20], to: [-35, -25] }));
  add(pathLayer("story-rail-top", [[70, 260], [330, 185], [665, 245], [1020, 175]], { ip: 0, op: totalFrames, color: hex("#FF8A4C", 50), width: 8, trimAt: 22 }));
  add(pathLayer("story-rail-bottom", [[45, 1575], [360, 1515], [715, 1585], [1035, 1515]], { ip: 0, op: totalFrames, color: hex("#63D5FF", 35), width: 6, trimAt: 22 }));

  // Scene 1: hook and analogy.
  {
    const [ip, op] = sceneRanges[0];
    add(cardLayer("story-card-shadow", { ip, op: op - 5, x: 552, y: 1074, width: 824, height: 514, radius: 68, fill: hex("#020812", 42), accent: true }));
    add(cardLayer("story-card", { ip, op, x: 540, y: 1052, width: 824, height: 514, radius: 68, fill: hex("#142B40", 96), stroke: hex("#FF8A4C", 65), strokeWidth: 5, accent: true }));
    add(imageLayer("label_story", assets.get("label_story"), { x: 274, y: 812, scale: 0.92, ip, op, from: [-40, -35] }));
    add(pathLayer("quote-flow-1", [[225, 930], [355, 895], [490, 930]], { ip: ip + 3, op, color: hex("#FFD166", 80), width: 13, trimAt: 15 }));
    add(pathLayer("quote-flow-2", [[245, 976], [375, 941], [520, 976]], { ip: ip + 6, op, color: hex("#FFD166", 55), width: 9, trimAt: 15 }));
    add(imageLayer("hook_why", assets.get("hook_why"), { x: 540, y: 385, scale: 0.94, ip, op, from: [0, -95], to: [0, -30] }));
    add(imageLayer("hook_hallucinate", assets.get("hook_hallucinate"), { x: 540, y: 565, scale: 0.91, ip, op, from: [0, -65], to: [0, -25], enter: 13 }));
    add(imageLayer("analogy_a", assets.get("analogy_a"), { x: 540, y: 1020, scale: 0.96, ip: ip + 12, op, from: [0, -38], to: [0, 25] }));
    add(imageLayer("analogy_b", assets.get("analogy_b"), { x: 540, y: 1125, scale: 0.94, ip: ip + 18, op, from: [0, -28], to: [0, 28] }));
    add(shapeLayer("fact-checker-absent", [ellipseShape(132, 132, hex("#FF6B6B", 15), hex("#FF6B6B", 90), 7)], { ip: ip + 25, op, x: 776, y: 1226, enter: 12, from: [38, 22], to: [18, 18] }));
    add(pathLayer("absent-cross-a", [[814, 1192], [858, 1236]], { ip: ip + 29, op, color: hex("#FF6B6B"), width: 11, trimAt: 10 }));
    add(pathLayer("absent-cross-b", [[858, 1192], [814, 1236]], { ip: ip + 31, op, color: hex("#FF6B6B"), width: 11, trimAt: 10 }));
    add(imageLayer("confidence_high", assets.get("confidence_high"), { x: 310, y: 1342, scale: 0.9, ip: ip + 34, op, from: [-24, -18], to: [14, 16] }));
    add(imageLayer("verification_off", assets.get("verification_off"), { x: 805, y: 1342, scale: 0.9, ip: ip + 36, op, from: [24, -18], to: [14, 16] }));
    add(cardLayer("confidence-meter-track", { ip: ip + 38, op, x: 540, y: 1404, width: 690, height: 30, radius: 15, fill: hex("#1A3A52", 90) }));
    add(cardLayer("confidence-meter-fill", { ip: ip + 42, op, x: 472, y: 1404, width: 554, height: 30, radius: 15, fill: hex("#FFD166", 88) }));
    add(imageLayer("caption_01", assets.get("caption_01"), { x: 540, y: 1738, scale: Math.min(1, 920 / assets.get("caption_01").width), ip: lineRanges[0].ip, op: lineRanges[0].op, from: [0, 28], to: [0, 18] }));
    add(sceneCaption(1, lineRanges[1], assets, lineRanges[1].ip, Math.min(op, lineRanges[1].op)));
  }

  // Scene 2: next-piece prediction, with probability bars.
  {
    const [ip, op] = sceneRanges[1];
    add(cardLayer("prediction-panel", { ip, op, x: 540, y: 935, width: 900, height: 1135, radius: 72, fill: hex("#0D2033", 95), stroke: hex("#63D5FF", 38), strokeWidth: 4 }));
    add(imageLayer("label_predict", assets.get("label_predict"), { x: 540, y: 330, scale: 0.95, ip, op, from: [0, -70] }));
    const tokenRows = [
      { id: "token_the", y: 610, color: hex("#1A3A52", 100), enter: 10 },
      { id: "token_opened", y: 805, color: hex("#1A3A52", 100), enter: 16 },
      { id: "token_1927", y: 1015, color: hex("#512F2B", 100), enter: 22 },
    ];
    tokenRows.forEach((row, index) => {
      const item = assets.get(row.id);
      add(cardLayer(`token-card-${index}`, { ip: ip + row.enter, op, x: 540, y: row.y, width: 760, height: 142, radius: 38, fill: row.color, stroke: index === 2 ? hex("#FF8A4C", 65) : hex("#63D5FF", 22), strokeWidth: 3 }));
      add(imageLayer(row.id, item, { x: 540, y: row.y, scale: Math.min(0.82, 620 / item.width), ip: ip + row.enter, op, from: [index % 2 ? 34 : -34, -20], to: [0, 25] }));
    });
    add(pathLayer("prediction-thread", [[540, 1102], [540, 1168], [410, 1215], [410, 1260]], { ip: ip + 28, op, color: hex("#FF8A4C", 82), width: 8, trimAt: 14 }));
    const candidates = [
      { id: "candidate_1889", y: 1302, width: 250, color: hex("#67E8B5", 65) },
      { id: "candidate_1927", y: 1402, width: 420, color: hex("#FF8A4C", 88) },
      { id: "candidate_1930", y: 1502, width: 155, color: hex("#A9B8CB", 52) },
    ];
    candidates.forEach((row, index) => {
      const item = assets.get(row.id);
      add(imageLayer(row.id, item, { x: 265, y: row.y, scale: 0.76, ip: ip + 31 + index * 5, op, from: [-22, 0], to: [12, 18] }));
      add(barLayer(`prob-bar-${index}`, { ip: ip + 33 + index * 5, op, x: 435 + row.width / 2, y: row.y, width: row.width, height: 20, color: row.color, delay: 0 }));
      add(shapeLayer(`prob-dot-${index}`, [ellipseShape(26, 26, row.color, null)], { ip: ip + 33 + index * 5, op, x: 412, y: row.y, enter: 5, exit: 3, from: [-10, 0], to: [6, 0] }));
    });
    add(sceneCaption(2, lineRanges[2], assets, lineRanges[2].ip, Math.min(op, lineRanges[2].op)));
  }

  // Scene 3: plausible story and verified fact diverge.
  {
    const [ip, op] = sceneRanges[2];
    add(imageLayer("fact_sentence", assets.get("fact_sentence"), { x: 540, y: 355, scale: 0.96, ip, op, from: [0, -75] }));
    add(shapeLayer("story-origin", [ellipseShape(132, 132, hex("#FFD166", 17), hex("#FFD166", 90), 6)], { ip, op, x: 540, y: 555, enter: 11, from: [0, -32], to: [0, 25] }));
    add(pathLayer("diverge-left", [[540, 618], [540, 695], [315, 760], [265, 820]], { ip: ip + 8, op, color: hex("#FF8A4C", 95), width: 13, trimAt: 14 }));
    add(pathLayer("diverge-right", [[540, 618], [540, 695], [765, 760], [815, 820]], { ip: ip + 10, op, color: hex("#67E8B5", 95), width: 13, trimAt: 14 }));
    add(cardLayer("plausible-shadow", { ip: ip + 12, op: op - 4, x: 277, y: 1045, width: 420, height: 410, radius: 54, fill: hex("#020812", 38) }));
    add(cardLayer("plausible-card", { ip: ip + 12, op, x: 265, y: 1028, width: 420, height: 410, radius: 54, fill: hex("#3B2726", 96), stroke: hex("#FF8A4C", 72), strokeWidth: 5 }));
    add(cardLayer("verified-shadow", { ip: ip + 15, op: op - 4, x: 827, y: 1045, width: 420, height: 410, radius: 54, fill: hex("#020812", 38) }));
    add(cardLayer("verified-card", { ip: ip + 15, op, x: 815, y: 1028, width: 420, height: 410, radius: 54, fill: hex("#183A38", 96), stroke: hex("#67E8B5", 72), strokeWidth: 5 }));
    add(imageLayer("plausible_label", assets.get("plausible_label"), { x: 265, y: 875, scale: 0.93, ip: ip + 16, op, from: [0, -25], to: [0, 22] }));
    add(imageLayer("verified_label", assets.get("verified_label"), { x: 815, y: 875, scale: 0.93, ip: ip + 18, op, from: [0, -25], to: [0, 22] }));
    add(imageLayer("date_1927", assets.get("date_1927"), { x: 265, y: 1030, scale: 0.95, ip: ip + 21, op, from: [0, -35], to: [0, 22] }));
    add(imageLayer("date_1889", assets.get("date_1889"), { x: 815, y: 1030, scale: 0.95, ip: ip + 23, op, from: [0, -35], to: [0, 22] }));
    add(shapeLayer("story-mark", [ellipseShape(86, 86, hex("#FF8A4C", 12), hex("#FF8A4C", 85), 5)], { ip: ip + 26, op, x: 265, y: 1225, enter: 8, from: [0, -18], to: [0, 18] }));
    add(pathLayer("story-x-a", [[240, 1200], [290, 1250]], { ip: ip + 29, op, color: hex("#FF8A4C"), width: 8, trimAt: 8 }));
    add(pathLayer("story-x-b", [[290, 1200], [240, 1250]], { ip: ip + 31, op, color: hex("#FF8A4C"), width: 8, trimAt: 8 }));
    add(shapeLayer("fact-check-mark", [ellipseShape(86, 86, hex("#67E8B5", 12), hex("#67E8B5", 85), 5)], { ip: ip + 28, op, x: 815, y: 1225, enter: 8, from: [0, -18], to: [0, 18] }));
    add(pathLayer("fact-check-stem", [[786, 1226], [807, 1248], [850, 1198]], { ip: ip + 32, op, color: hex("#67E8B5"), width: 10, trimAt: 9 }));
    add(imageLayer("fluency", assets.get("fluency"), { x: 540, y: 1475, scale: 0.95, ip: ip + 36, op, from: [0, -35], to: [0, 25] }));
    add(sceneCaption(3, lineRanges[3], assets, lineRanges[3].ip, Math.min(op, lineRanges[3].op)));
    add(sceneCaption(4, lineRanges[4], assets, lineRanges[4].ip, Math.min(op, lineRanges[4].op)));
  }

  // Scene 4: a thinning pattern leaves a gap that is filled by an invention.
  {
    const [ip, op] = sceneRanges[3];
    add(imageLayer("pattern_label", assets.get("pattern_label"), { x: 540, y: 355, scale: 0.96, ip, op, from: [0, -70] }));
    const xs = [165, 315, 465, 615, 765, 915];
    const patternColors = ["#63D5FF", "#63D5FF", "#63D5FF", "#FFD166", "#FFD166", "#FF8A4C"];
    xs.forEach((x, index) => {
      const width = index === 3 ? 145 : 118;
      const isGap = index === 3;
      add(shapeLayer(
        `pattern-piece-${index}`,
        [rectShape(width, 160, 34, hex(patternColors[index], isGap ? 30 : 82), hex(patternColors[index], isGap ? 38 : 70), 4)],
        { ip: ip + index * 3, op, x: x - width / 2, y: 660, enter: 10, exit: 5, from: [0, index % 2 ? -42 : -28], to: [0, 22] },
      ));
    });
    add(pathLayer("pattern-connector", [[165, 742], [915, 742]], { ip: ip + 8, op, color: hex("#63D5FF", 45), width: 7, trimAt: 18 }));
    for (let index = 0; index < 5; index += 1) {
      add(shapeLayer(`pattern-tick-${index}`, [rectShape(68, 7, 4, hex(index < 3 ? "#63D5FF" : "#FFD166", 52), null)], { ip: ip + 10 + index * 2, op, x: 165 + index * 150, y: 865, enter: 6, exit: 3, from: [-12, 0], to: [8, 0] }));
    }
    add(shapeLayer("invention-fill", [rectShape(145, 160, 34, hex("#FF8A4C", 78), hex("#FFD166", 95), 5)], { ip: ip + 22, op, x: 475, y: 660, enter: 13, exit: 4, from: [190, -135], to: [25, 20] }));
    add(pathLayer("invention-arrow", [[845, 1035], [695, 925], [625, 835]], { ip: ip + 28, op, color: hex("#FF8A4C", 88), width: 12, trimAt: 13 }));
    add(cardLayer("invention-card", { ip: ip + 31, op, x: 540, y: 1170, width: 820, height: 235, radius: 54, fill: hex("#3B2726", 94), stroke: hex("#FF8A4C", 65), strokeWidth: 5 }));
    add(imageLayer("invention_label", assets.get("invention_label"), { x: 540, y: 1170, scale: 0.96, ip: ip + 35, op, from: [0, -32], to: [0, 22] }));
    add(sceneCaption(5, lineRanges[5], assets, lineRanges[5].ip, Math.min(op, lineRanges[5].op)));
  }

  // Scene 5: conclusion and call to action.
  {
    const [ip, op] = sceneRanges[4];
    add(imageLayer("plausible_word", assets.get("plausible_word"), { x: 540, y: 590, scale: 0.92, ip, op, from: [-70, -35], to: [0, -18] }));
    add(pathLayer("not-equal-a", [[285, 815], [795, 770]], { ip: ip + 12, op, color: hex("#FFD166"), width: 22, trimAt: 12 }));
    add(pathLayer("not-equal-b", [[285, 885], [795, 840]], { ip: ip + 15, op, color: hex("#FFD166"), width: 22, trimAt: 12 }));
    add(imageLayer("true_word", assets.get("true_word"), { x: 540, y: 1055, scale: 0.92, ip: ip + 18, op, from: [70, 35], to: [0, 20] }));
    add(cardLayer("check-pill-shadow", { ip: ip + 27, op: op - 3, x: 550, y: 1382, width: 865, height: 190, radius: 95, fill: hex("#020812", 38) }));
    add(cardLayer("check-pill", { ip: ip + 27, op, x: 540, y: 1368, width: 865, height: 190, radius: 95, fill: hex("#F5F7FF", 96), stroke: hex("#67E8B5", 88), strokeWidth: 5 }));
    add(imageLayer("check_claim", assets.get("check_claim"), { x: 540, y: 1368, scale: 0.94, ip: ip + 31, op, from: [0, -28], to: [0, 18] }));
    add(imageLayer("small_source", assets.get("small_source"), { x: 540, y: 1545, scale: 0.92, ip: ip + 35, op, from: [0, -25], to: [0, 18] }));
    add(shapeLayer("closing-check", [ellipseShape(120, 120, hex("#67E8B5", 15), hex("#67E8B5", 92), 7)], { ip: ip + 39, op, x: 885, y: 1545, enter: 12, from: [28, 22], to: [18, 16] }));
    add(pathLayer("closing-check-mark", [[846, 1547], [874, 1575], [928, 1517]], { ip: ip + 43, op, color: hex("#67E8B5"), width: 13, trimAt: 10 }));
    add(sceneCaption(6, lineRanges[6], assets, lineRanges[6].ip, op));
  }

  const backgroundAsset = { id: "bg", w: WIDTH, h: HEIGHT, u: "", p: "../../assets/background.jpg", e: 1 };
  const imageAssets = manifest.items.map((item) => ({
    id: item.id,
    w: item.width,
    h: item.height,
    u: "",
    p: `../../assets/${item.path}`,
    e: 1,
  }));
  const backgroundLayer = {
    ddd: 0,
    ind: 0,
    ty: 2,
    nm: "background",
    refId: "bg",
    sr: 1,
    ks: transform(
      [WIDTH / 2, HEIGHT / 2],
      100,
      0,
      100,
      [WIDTH / 2, HEIGHT / 2, 0],
    ),
    ao: 0,
    ip: 0,
    op: totalFrames,
    st: 0,
    w: WIDTH,
    h: HEIGHT,
    bm: 0,
  };
  const orderedLayers = [...layers].reverse();
  orderedLayers.push(backgroundLayer);
  orderedLayers.forEach((layer, index) => {
    layer.ind = index + 1;
  });

  const lottie = {
    v: "5.13.0",
    fr: FPS,
    ip: 0,
    op: totalFrames,
    w: WIDTH,
    h: HEIGHT,
    nm: "Why AI Hallucinates - Lottie-web benchmark",
    ddd: 0,
    assets: [backgroundAsset, ...imageAssets],
    layers: orderedLayers,
    markers: [
      { tm: 0, cm: "scene-1-hook-analogy", dr: lineStarts[2] },
      { tm: lineStarts[2], cm: "scene-2-predict", dr: lineStarts[3] - lineStarts[2] },
      { tm: lineStarts[3], cm: "scene-3-diverge", dr: lineStarts[5] - lineStarts[3] },
      { tm: lineStarts[5], cm: "scene-4-gap", dr: lineStarts[6] - lineStarts[5] },
      { tm: lineStarts[6], cm: "scene-5-close", dr: totalFrames - lineStarts[6] },
    ],
    meta: {
      generator: "src/build-lottie.mjs",
      renderer: "lottie-web 5.13.0 SVG",
      audioDurationSeconds: timings.durationSeconds,
    },
  };

  await fs.writeFile(path.join(ROOT, "src", "lottie.json"), JSON.stringify(lottie) + "\n");
  await fs.writeFile(
    path.join(ROOT, "src", "lottie-summary.json"),
    JSON.stringify(
      {
        fps: FPS,
        width: WIDTH,
        height: HEIGHT,
        durationSeconds: timings.durationSeconds,
        totalFrames,
        layerCount: orderedLayers.length,
        assetCount: imageAssets.length + 1,
        sceneStartsSeconds: lottie.markers.map((marker) => marker.tm / FPS),
        markers: lottie.markers,
      },
      null,
      2,
    ) + "\n",
  );
  console.log(`Wrote src/lottie.json: ${orderedLayers.length} layers, ${totalFrames} frames`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
