(() => {
  const W = 1080;
  const H = 1920;
  const FPS = 30;
  const DURATION = 22.2;

  const C = {
    ink: 0x071015,
    panel: 0x0c1b22,
    panel2: 0x10262e,
    line: 0x24404a,
    pale: 0xe9f3f0,
    muted: 0x89a4a8,
    cyan: 0x4ee6d2,
    cyan2: 0x18bda9,
    amber: 0xffbf69,
    coral: 0xff756d,
    blue: 0x68a9ff,
    green: 0x7ee081,
  };

  const app = new PIXI.Application();
  let ready = false;
  let activeVariant = "first";

  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
  const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const range = (t, a, b) => clamp((t - a) / (b - a));
  const pulse = (t, speed = 1) => 0.5 + 0.5 * Math.sin(t * speed);

  function text(str, x, y, size, color = C.pale, opts = {}) {
    const t = new PIXI.Text({
      text: str,
      style: {
        fontFamily: "Arial",
        fontSize: size,
        fontWeight: opts.weight || "700",
        fill: color,
        align: opts.align || "left",
        letterSpacing: opts.letterSpacing ?? 0,
        wordWrap: true,
        wordWrapWidth: opts.wrap || 900,
        lineHeight: opts.lineHeight || Math.round(size * 1.12),
        stroke: opts.stroke ? { color: opts.stroke, width: opts.strokeWidth || 3 } : undefined,
      },
    });
    t.x = x;
    t.y = y;
    if (opts.anchor) t.anchor.set(...opts.anchor);
    return t;
  }

  function rect(g, x, y, w, h, radius, fill, alpha = 1, stroke = null, strokeWidth = 2) {
    g.roundRect(x, y, w, h, radius).fill({ color: fill, alpha });
    if (stroke !== null) g.stroke({ color: stroke, width: strokeWidth, alpha: 0.95 });
    return g;
  }

  function line(g, points, color, width = 4, alpha = 1) {
    g.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
    g.stroke({ color, width, alpha, cap: "round", join: "round" });
    return g;
  }

  function dot(g, x, y, r, color, alpha = 1) {
    g.circle(x, y, r).fill({ color, alpha });
    return g;
  }

  function drawGrid(root, t) {
    const g = new PIXI.Graphics();
    g.rect(0, 0, W, H).fill(C.ink);
    for (let x = 54; x < W; x += 82) line(g, [[x, 0], [x, H]], C.line, 1, 0.28);
    for (let y = 72; y < H; y += 82) line(g, [[0, y], [W, y]], C.line, 1, 0.22);
    for (let i = 0; i < 18; i++) {
      const y = (i * 137 + t * 36) % H;
      line(g, [[0, y], [W, y]], i % 3 === 0 ? C.cyan : C.blue, 1, i % 3 === 0 ? 0.10 : 0.045);
    }
    root.addChild(g);
  }

  function drawTopRail(root, t) {
    const g = new PIXI.Graphics();
    rect(g, 42, 42, 996, 86, 24, C.panel, 0.96, C.line, 2);
    dot(g, 82, 85, 8, C.cyan, 1);
    dot(g, 110, 85, 8, C.amber, 1);
    dot(g, 138, 85, 8, C.coral, 1);
    root.addChild(g);
    root.addChild(text("AGENT // TOOL OPERATIONS", 176, 67, 27, C.pale, { letterSpacing: 2 }));
    root.addChild(text(`LOOP ${String(Math.floor(t * 10) % 100).padStart(2, "0")}`, 820, 67, 23, C.cyan, { letterSpacing: 2 }));
    const bar = new PIXI.Graphics();
    const progress = clamp(t / DURATION);
    rect(bar, 42, 142, 996 * progress, 7, 4, C.cyan, 0.9);
    root.addChild(bar);
  }

  function drawAgentCore(root, t, emphasis = 0) {
    const cx = 540;
    const cy = 670;
    const g = new PIXI.Graphics();
    const p = pulse(t, 3.4);
    for (let i = 0; i < 3; i++) {
      const r = 176 + i * 48 + p * (i === 0 ? 8 : 2);
      g.circle(cx, cy, r).stroke({ color: i === 0 ? C.cyan : C.line, width: i === 0 ? 7 : 3, alpha: i === 0 ? 0.78 : 0.5 });
    }
    g.roundRect(cx - 142, cy - 142, 284, 284, 58).fill({ color: C.panel2, alpha: 1 }).stroke({ color: C.cyan, width: 8, alpha: 0.82 });
    g.roundRect(cx - 98, cy - 98, 196, 196, 38).fill({ color: C.ink, alpha: 1 }).stroke({ color: C.line, width: 3 });
    for (let i = 0; i < 6; i++) {
      const a = t * 0.6 + i * Math.PI / 3;
      dot(g, cx + Math.cos(a) * 118, cy + Math.sin(a) * 118, 8, i % 2 ? C.amber : C.cyan);
    }
    root.addChild(g);
    root.addChild(text("AGENT", cx, cy - 38, 42, C.pale, { anchor: [0.5, 0], letterSpacing: 5 }));
    root.addChild(text("goal → plan", cx, cy + 16, 24, C.muted, { anchor: [0.5, 0], letterSpacing: 1 }));
    if (emphasis > 0) {
      const e = new PIXI.Graphics();
      e.circle(cx, cy, 304 + emphasis * 16).stroke({ color: C.amber, width: 5, alpha: 0.25 + 0.25 * pulse(t, 5) });
      root.addChild(e);
    }
  }

  function drawToolCard(root, x, y, w, h, label, sub, color, selected, t, index) {
    const g = new PIXI.Graphics();
    const lift = selected ? -18 + Math.sin(t * 5 + index) * 4 : 0;
    const yy = y + lift;
    rect(g, x, yy, w, h, 26, selected ? C.panel2 : C.panel, 0.98, selected ? color : C.line, selected ? 5 : 2);
    g.roundRect(x + 24, yy + 24, 66, 66, 18).fill({ color, alpha: selected ? 1 : 0.55 });
    for (let j = 0; j < 3; j++) g.rect(x + 42, yy + 42 + j * 12, 30 - j * 6, 4).fill(C.ink);
    root.addChild(g);
    root.addChild(text(label, x + 112, yy + 30, 30, selected ? C.pale : C.muted, { letterSpacing: 1 }));
    root.addChild(text(sub, x + 112, yy + 73, 21, selected ? color : C.muted, { letterSpacing: 1 }));
    if (selected) {
      const ring = new PIXI.Graphics();
      ring.roundRect(x - 10, yy - 10, w + 20, h + 20, 32).stroke({ color, width: 3, alpha: 0.46 + 0.2 * pulse(t, 4) });
      root.addChild(ring);
    }
  }

  function drawCaption(root, lines, t, start, end) {
    const alpha = Math.min(range(t, start, start + 0.18), 1 - range(t, end - 0.3, end));
    if (alpha <= 0) return;
    const g = new PIXI.Graphics();
    rect(g, 64, 1490, 952, 284, 30, C.ink, 0.84 * alpha, C.line, 2);
    root.addChild(g);
    const title = lines[0] || "";
    const body = lines[1] || "";
    const a = text(title, 112, 1532, 48, C.pale, { wrap: 860, letterSpacing: 1 });
    const b = text(body, 112, 1612, 48, C.cyan, { wrap: 860, letterSpacing: 1 });
    a.alpha = alpha;
    b.alpha = alpha;
    root.addChild(a, b);
  }

  function drawPacket(root, x, y, label, color, t, tilt = 0) {
    const g = new PIXI.Graphics();
    g.roundRect(x, y, 260, 106, 22).fill({ color: C.panel2, alpha: 0.98 }).stroke({ color, width: 4 });
    g.roundRect(x + 18, y + 18, 224, 16, 8).fill({ color, alpha: 0.25 });
    g.roundRect(x + 18, y + 52, 130, 12, 6).fill({ color, alpha: 0.85 });
    g.roundRect(x + 160, y + 52, 82, 12, 6).fill({ color: C.muted, alpha: 0.65 });
    g.roundRect(x + 18, y + 78, 180, 8, 4).fill({ color: C.muted, alpha: 0.38 });
    g.angle = tilt;
    root.addChild(g);
    const labelNode = text(label, x + 130, y - 30, 25, color, { anchor: [0.5, 0], letterSpacing: 2 });
    root.addChild(labelNode);
  }

  function drawRoute(root, t, from, to, color, p, label) {
    const g = new PIXI.Graphics();
    const midX = (from[0] + to[0]) / 2;
    const midY = Math.min(from[1], to[1]) - 88;
    g.moveTo(from[0], from[1]);
    g.bezierCurveTo(midX, midY, midX, midY, to[0], to[1]);
    g.stroke({ color: C.line, width: 8, alpha: 0.72, cap: "round" });
    for (let i = 0; i < 7; i++) {
      const q = (p * 1.35 + i * 0.12) % 1;
      const x = lerp(from[0], to[0], q);
      const y = lerp(from[1], to[1], q) - Math.sin(Math.PI * q) * 88;
      g.circle(x, y, 7 + 3 * Math.sin(q * Math.PI)).fill({ color, alpha: 0.30 + 0.50 * (1 - Math.abs(q - 0.5) * 2) });
    }
    root.addChild(g);
    root.addChild(text(label, midX, midY - 48, 18, color, { anchor: [0.5, 0], align: "center", letterSpacing: 2 }));
  }

  function drawLoop(root, t, p) {
    const g = new PIXI.Graphics();
    const cx = 540;
    const cy = 1038;
    g.arc(cx, cy, 286, -Math.PI * 0.84, Math.PI * 0.84).stroke({ color: C.line, width: 20, alpha: 0.85 });
    g.arc(cx, cy, 286, -Math.PI * 0.84, -Math.PI * 0.84 + Math.PI * 1.68 * p).stroke({ color: C.cyan, width: 20, alpha: 0.95, cap: "round" });
    const a = -Math.PI * 0.84 + Math.PI * 1.68 * p;
    const x = cx + Math.cos(a) * 286;
    const y = cy + Math.sin(a) * 286;
    g.circle(x, y, 17).fill(C.amber);
    root.addChild(g);
  }

  function drawScene(root, t) {
    drawGrid(root, t);
    drawTopRail(root, t);

    const titleAlpha = 1 - range(t, 2.75, 3.35);
    if (titleAlpha > 0) {
      const title = text("HOW DO AI AGENTS", 540, 280, 72, C.pale, { anchor: [0.5, 0], align: "center", letterSpacing: 3 });
      const title2 = text("USE TOOLS?", 540, 370, 88, C.cyan, { anchor: [0.5, 0], align: "center", letterSpacing: 3 });
      title.alpha = title2.alpha = titleAlpha;
      root.addChild(title, title2);
      const rule = new PIXI.Graphics();
      rect(rule, 374, 494, 332, 8, 4, C.amber, titleAlpha);
      root.addChild(rule);
    }

    const phaseChoose = range(t, 2.8, 7.3);
    const phaseAction = range(t, 7.2, 12.2);
    const phaseResult = range(t, 12.1, 16.4);
    const phaseContinue = range(t, 16.3, 22.2);
    const coreEmphasis = Math.max(phaseChoose, phaseAction, phaseResult, phaseContinue);
    drawAgentCore(root, t, coreEmphasis);

    if (t < 7.5) {
      const slide = easeOut(range(t, 2.7, 4.2));
      drawToolCard(root, 66, 950 + (1 - slide) * 140, 286, 190, "SEARCH", "find information", C.blue, t > 3.5 && t < 5.1, t, 0);
      drawToolCard(root, 397, 950 + (1 - slide) * 140, 286, 190, "CALCULATE", "compute a result", C.amber, t >= 5.1, t, 1);
      drawToolCard(root, 728, 950 + (1 - slide) * 140, 286, 190, "DATABASE", "read structured data", C.coral, false, t, 2);
      root.addChild(text("CHOOSE THE TOOL THAT FITS", 540, 1218, 32, C.pale, { anchor: [0.5, 0], align: "center", letterSpacing: 2 }));
    }

    if (t >= 7.1 && t < 12.35) {
      const p = easeInOut(range(t, 7.3, 11.7));
      drawRoute(root, t, [210, 1050], [700, 1015], C.amber, p, "ACTION PACKET");
      drawPacket(root, lerp(82, 612, p), lerp(1120, 1038, p), "ACTION", C.amber, t, -2 + Math.sin(t * 4) * 2);
      const consoleG = new PIXI.Graphics();
      rect(consoleG, 78, 1236, 924, 182, 24, C.panel, 0.96, C.line, 2);
      rect(consoleG, 112, 1272, 620, 18, 9, C.cyan, 0.22);
      rect(consoleG, 112, 1314, 410, 14, 7, C.amber, 0.75);
      rect(consoleG, 112, 1352, 760, 12, 6, C.muted, 0.28);
      root.addChild(consoleG);
      root.addChild(text("action = { query: “latest sales” }", 112, 1254, 27, C.pale, { wrap: 850 }));
      root.addChild(text("exact input, not a vague wish", 112, 1382, 21, C.muted, { wrap: 850 }));
    }

    if (t >= 11.9) {
      const p = easeInOut(range(t, 12.05, 15.7));
      drawRoute(root, t, [770, 1015], [170, 1080], C.cyan, p, "RESULT PACKET");
      drawPacket(root, lerp(680, 116, p), lerp(1025, 1142, p), "RESULT", C.cyan, t, 2 - Math.sin(t * 4) * 2);
      const resultG = new PIXI.Graphics();
      rect(resultG, 78, 1236, 924, 182, 24, C.panel, 0.96, C.cyan2, 3);
      for (let i = 0; i < 5; i++) {
        const w = 74 + ((i * 37 + t * 12) % 140);
        rect(resultG, 122 + i * 152, 1352 - w, 86, w, 12, i === 2 ? C.green : C.cyan, 0.72);
      }
      root.addChild(resultG);
      root.addChild(text("result = { status: “ok”, rows: 3 }", 112, 1254, 27, C.pale, { wrap: 850 }));
      root.addChild(text("new information changes the next move", 112, 1382, 21, C.muted, { wrap: 850 }));
    }

    if (t >= 15.9) {
      const p = range(t, 16.1, 21.5);
      drawLoop(root, t, p);
      const labels = [
        ["CHOOSE", 260, 782, C.blue],
        ["ACT", 820, 782, C.amber],
        ["READ", 820, 1300, C.cyan],
        ["CONTINUE", 260, 1300, C.green],
      ];
      labels.forEach(([label, x, y, color], i) => {
        const a = clamp((p - i * 0.17) * 5);
        const n = text(label, x, y, 32, color, { anchor: [0.5, 0], align: "center", letterSpacing: 3 });
        n.alpha = a;
        root.addChild(n);
      });
      const ribbon = new PIXI.Graphics();
      const rp = clamp(range(t, 17.1, 18.2));
      rect(ribbon, 104, 1402, 872, 58, 18, C.panel2, 0.84 * rp, C.cyan2, 2);
      root.addChild(ribbon);
      const ribbonText = text("CHOOSE  →  ACT  →  READ  →  CONTINUE", 540, 1418, 27, C.pale, { anchor: [0.5, 0], align: "center", letterSpacing: 2 });
      ribbonText.alpha = rp;
      root.addChild(ribbonText);
    }

    drawCaption(root, ["THINK OF AN AI AGENT", "AT A CONTROL DESK"], t, 0.45, 3.4);
    drawCaption(root, ["SEE THE GOAL.", "CHOOSE THE RIGHT TOOL."], t, 3.55, 7.55);
    drawCaption(root, ["SUPPLY AN ACTION:", "THE EXACT REQUEST."], t, 7.75, 12.45);
    drawCaption(root, ["THE TOOL RUNS.", "IT RETURNS A RESULT."], t, 12.65, 16.35);
    drawCaption(root, ["READ THE RESULT.", "UPDATE. CONTINUE."], t, 16.55, 22.1);

    const vignette = new PIXI.Graphics();
    vignette.rect(0, 0, 160, H).fill({ color: C.ink, alpha: 0.28 });
    vignette.rect(W - 160, 0, 160, H).fill({ color: C.ink, alpha: 0.28 });
    vignette.rect(0, 0, W, 112).fill({ color: C.ink, alpha: 0.18 });
    vignette.rect(0, H - 110, W, 110).fill({ color: C.ink, alpha: 0.30 });
    root.addChild(vignette);
  }

  async function init(variant = "first") {
    activeVariant = variant;
    await app.init({
      canvas: document.getElementById("stage"),
      width: W,
      height: H,
      background: C.ink,
      antialias: true,
      autoStart: false,
      preference: "webgl",
      preserveDrawingBuffer: true,
      resolution: 1,
      autoDensity: false,
    });
    ready = true;
    renderFrame(0);
    return { width: W, height: H, fps: FPS, duration: DURATION, renderer: app.renderer.name, variant };
  }

  function renderFrame(frame) {
    if (!ready) return;
    const t = Math.max(0, Math.min(DURATION, frame / FPS));
    app.stage.removeChildren().forEach((child) => child.destroy({ children: true }));
    drawScene(app.stage, t);
    app.render();
    return { frame, t, renderer: app.renderer.name };
  }

  window.videoScene = {
    init,
    renderFrame,
    meta: { W, H, FPS, DURATION, variant: activeVariant },
  };
})();
