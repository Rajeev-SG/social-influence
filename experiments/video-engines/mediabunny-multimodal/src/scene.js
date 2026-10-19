(() => {
  "use strict";

  const W = 1080;
  const H = 1920;
  const FPS = 30;

  const C = {
    ink: "#07101b",
    ink2: "#0c1726",
    panel: "#101e30",
    panel2: "#16283d",
    white: "#f7fbff",
    mist: "#a9bbcd",
    muted: "#6f8297",
    coral: "#ff7b6b",
    coral2: "#ffb09f",
    cyan: "#52d7d0",
    cyan2: "#a0fff5",
    gold: "#f6c667",
    violet: "#a78bfa",
    line: "rgba(187, 215, 239, 0.16)",
  };

  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const lerp = (a, b, t) => a + (b - a) * t;
  const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
  const easeInOut = (t) => {
    const x = clamp(t);
    return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  };
  const smoothstep = (t) => {
    const x = clamp(t);
    return x * x * (3 - 2 * x);
  };

  function roundedRect(ctx, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
  }

  function fillRounded(ctx, x, y, width, height, radius, fill, stroke = null, lineWidth = 1) {
    roundedRect(ctx, x, y, width, height, radius);
    ctx.fillStyle = fill;
    ctx.fill();
    if (stroke) {
      ctx.strokeStyle = stroke;
      ctx.lineWidth = lineWidth;
      ctx.stroke();
    }
  }

  function setFont(ctx, size, weight = 700, family = "Inter, Helvetica Neue, Arial, sans-serif") {
    ctx.font = `${weight} ${size}px ${family}`;
    ctx.textBaseline = "alphabetic";
    ctx.textAlign = "left";
  }

  function drawTracked(ctx, text, x, y, size, color, weight = 700, tracking = 0) {
    setFont(ctx, size, weight);
    ctx.fillStyle = color;
    if (!tracking) {
      ctx.fillText(text, x, y);
      return;
    }
    let cursor = x;
    for (const char of text) {
      ctx.fillText(char, cursor, y);
      cursor += ctx.measureText(char).width + tracking;
    }
  }

  function wrapLines(ctx, text, maxWidth) {
    const words = text.split(/\s+/);
    const lines = [];
    let line = "";
    for (const word of words) {
      const candidate = line ? `${line} ${word}` : word;
      if (ctx.measureText(candidate).width > maxWidth && line) {
        lines.push(line);
        line = word;
      } else {
        line = candidate;
      }
    }
    if (line) lines.push(line);
    return lines;
  }

  function drawParagraph(ctx, text, x, y, maxWidth, size, lineHeight, color, weight = 650) {
    setFont(ctx, size, weight);
    ctx.fillStyle = color;
    const lines = wrapLines(ctx, text, maxWidth);
    lines.forEach((line, index) => ctx.fillText(line, x, y + index * lineHeight));
    return lines.length * lineHeight;
  }

  function drawBackground(ctx, t) {
    const base = ctx.createLinearGradient(0, 0, 0, H);
    base.addColorStop(0, "#07101b");
    base.addColorStop(0.52, "#0b1725");
    base.addColorStop(1, "#08111d");
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, W, H);

    const glowA = ctx.createRadialGradient(900, 260, 40, 900, 260, 560);
    glowA.addColorStop(0, "rgba(82, 215, 208, 0.13)");
    glowA.addColorStop(1, "rgba(82, 215, 208, 0)");
    ctx.fillStyle = glowA;
    ctx.fillRect(300, 0, 780, 880);

    const glowB = ctx.createRadialGradient(120, 1510, 40, 120, 1510, 610);
    glowB.addColorStop(0, "rgba(255, 123, 107, 0.12)");
    glowB.addColorStop(1, "rgba(255, 123, 107, 0)");
    ctx.fillStyle = glowB;
    ctx.fillRect(0, 900, 720, 1020);

    ctx.save();
    ctx.globalAlpha = 0.18;
    ctx.strokeStyle = "rgba(137, 171, 199, 0.15)";
    ctx.lineWidth = 1;
    const offset = (t * 7) % 72;
    for (let x = -72 + offset; x < W + 72; x += 72) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (let y = -72 + offset; y < H + 72; y += 72) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
    ctx.restore();

    const vignette = ctx.createRadialGradient(W / 2, H / 2, 420, W / 2, H / 2, 1110);
    vignette.addColorStop(0, "rgba(0, 0, 0, 0)");
    vignette.addColorStop(0.72, "rgba(0, 0, 0, 0.04)");
    vignette.addColorStop(1, "rgba(0, 0, 0, 0.48)");
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, W, H);
  }

  function drawChrome(ctx, t, timing, sceneKey) {
    fillRounded(ctx, 72, 62, 312, 58, 29, "rgba(8, 18, 30, 0.72)", "rgba(167, 204, 230, 0.16)");
    ctx.beginPath();
    ctx.arc(105, 91, 8, 0, Math.PI * 2);
    ctx.fillStyle = C.cyan;
    ctx.fill();
    drawTracked(ctx, "MEDIA / NOTES", 128, 99, 18, C.white, 750, 1.7);

    const sceneIndex = ["hook", "image", "audio", "text", "converge", "answer"].indexOf(sceneKey);
    drawTracked(ctx, `${String(sceneIndex + 1).padStart(2, "0")} / 06`, 878, 99, 18, C.mist, 700, 1.5);

    const progressX = 72;
    const progressY = 1840;
    const progressW = 936;
    const segmentGap = 8;
    const segmentW = (progressW - segmentGap * 5) / 6;
    const globalP = clamp(t / timing.duration);
    for (let i = 0; i < 6; i += 1) {
      const start = i / 6;
      const end = (i + 1) / 6;
      const local = clamp((globalP - start) / (end - start));
      fillRounded(
        ctx,
        progressX + i * (segmentW + segmentGap),
        progressY,
        segmentW,
        7,
        3.5,
        "rgba(184, 211, 232, 0.16)",
      );
      if (local > 0) {
        fillRounded(
          ctx,
          progressX + i * (segmentW + segmentGap),
          progressY,
          Math.max(7, segmentW * easeOut(local)),
          7,
          3.5,
          i === 5 ? C.coral : C.cyan,
        );
      }
    }
  }

  function drawCaption(ctx, t, timing) {
    const cue =
      timing.cues.find((item) => t >= item.start - 0.12 && t <= item.end + 0.14) ||
      (t < timing.cues[0].start
        ? {
            caption: "How does multimodal AI work?",
            start: 0,
            end: timing.cues[0].start,
          }
        : null);
    if (!cue) return;

    const fadeIn = smoothstep((t - cue.start + 0.18) / 0.26);
    const fadeOut = cue.end > 0 ? 1 - smoothstep((t - cue.end) / 0.14) : 1;
    const alpha = clamp(Math.min(fadeIn, fadeOut));
    if (alpha <= 0) return;

    ctx.save();
    ctx.globalAlpha = alpha;
    setFont(ctx, 36, 650);
    const lines = wrapLines(ctx, cue.caption, 820);
    const boxHeight = 70 + (lines.length - 1) * 45;
    const y = 1666 - (lines.length - 1) * 22;
    fillRounded(ctx, 72, y, 936, boxHeight, 28, "rgba(3, 10, 18, 0.76)", "rgba(190, 216, 235, 0.12)");
    ctx.fillStyle = C.white;
    lines.forEach((line, index) => ctx.fillText(line, 108, y + 49 + index * 45));
    ctx.restore();
  }

  function drawKicker(ctx, index, label, accent, p) {
    const reveal = easeOut(p / 0.18);
    ctx.save();
    ctx.globalAlpha = reveal;
    fillRounded(ctx, 72, 152, 112, 46, 23, "rgba(7, 16, 27, 0.72)", "rgba(188, 213, 233, 0.14)");
    drawTracked(ctx, String(index).padStart(2, "0"), 102, 183, 18, accent, 800, 1.8);
    drawTracked(ctx, label, 214, 184, 20, C.mist, 750, 2.2);
    ctx.restore();
  }

  function drawImageGlyph(ctx, x, y, size, p, accent = C.coral) {
    ctx.save();
    ctx.translate(x, y);
    const settle = easeOut(clamp(p * 1.25));
    ctx.rotate(lerp(-0.05, 0, settle));
    fillRounded(ctx, -size / 2, -size / 2, size, size, size * 0.13, "#17283b", "rgba(211, 231, 245, 0.18)", 2);
    const sky = ctx.createLinearGradient(0, -size / 2, 0, size / 2);
    sky.addColorStop(0, "#27425c");
    sky.addColorStop(0.58, accent);
    sky.addColorStop(1, "#542f42");
    fillRounded(ctx, -size * 0.4, -size * 0.38, size * 0.8, size * 0.55, size * 0.08, sky);
    ctx.beginPath();
    ctx.arc(size * 0.18, -size * 0.16, size * 0.095, 0, Math.PI * 2);
    ctx.fillStyle = C.gold;
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(-size * 0.4, size * 0.17);
    ctx.lineTo(-size * 0.08, -size * 0.08);
    ctx.lineTo(size * 0.18, size * 0.17);
    ctx.closePath();
    ctx.fillStyle = "#1a3148";
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(-size * 0.06, size * 0.17);
    ctx.lineTo(size * 0.22, -size * 0.02);
    ctx.lineTo(size * 0.4, size * 0.17);
    ctx.closePath();
    ctx.fillStyle = "#264865";
    ctx.fill();
    ctx.restore();
  }

  function drawAudioGlyph(ctx, x, y, size, t, accent = C.cyan) {
    ctx.save();
    ctx.translate(x, y);
    const ring = ctx.createRadialGradient(0, 0, size * 0.1, 0, 0, size * 0.65);
    ring.addColorStop(0, "rgba(82, 215, 208, 0.18)");
    ring.addColorStop(1, "rgba(82, 215, 208, 0)");
    ctx.fillStyle = ring;
    ctx.fillRect(-size * 0.72, -size * 0.72, size * 1.44, size * 1.44);
    ctx.beginPath();
    ctx.arc(0, 0, size * 0.53, 0, Math.PI * 2);
    ctx.fillStyle = "#102538";
    ctx.fill();
    ctx.strokeStyle = "rgba(163, 229, 230, 0.22)";
    ctx.lineWidth = 2;
    ctx.stroke();
    for (let i = -5; i <= 5; i += 1) {
      const wave = Math.sin(t * 4.8 + i * 0.75) * 0.5 + Math.sin(t * 2.2 + i) * 0.22;
      const height = size * (0.14 + Math.abs(wave) * 0.28);
      fillRounded(ctx, i * size * 0.075 - size * 0.021, -height / 2, size * 0.042, height, size * 0.021, accent);
    }
    ctx.restore();
  }

  function drawTextGlyph(ctx, x, y, size, p, accent = C.gold) {
    ctx.save();
    ctx.translate(x, y);
    const reveal = easeOut(clamp(p * 1.3));
    fillRounded(ctx, -size / 2, -size * 0.38, size, size * 0.76, size * 0.11, "#17283b", "rgba(211, 231, 245, 0.18)", 2);
    fillRounded(ctx, -size * 0.35, -size * 0.21, size * 0.7 * reveal, size * 0.11, size * 0.055, accent);
    fillRounded(ctx, -size * 0.35, size * 0.02, size * 0.51 * reveal, size * 0.08, size * 0.04, "#b6c5d4");
    fillRounded(ctx, -size * 0.35, size * 0.17, size * 0.61 * reveal, size * 0.08, size * 0.04, "#70869c");
    ctx.restore();
  }

  function drawPill(ctx, x, y, width, label, color, active = 1) {
    ctx.save();
    ctx.globalAlpha = active;
    fillRounded(ctx, x, y, width, 64, 32, "rgba(15, 30, 47, 0.92)", "rgba(194, 219, 238, 0.16)", 2);
    ctx.beginPath();
    ctx.arc(x + 32, y + 32, 10, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    drawTracked(ctx, label, x + 55, y + 41, 19, C.white, 750, 1.1);
    ctx.restore();
  }

  function drawHook(ctx, t, timing, p) {
    drawKicker(ctx, 1, "THE IDEA", C.coral, p);
    const titleIn = easeOut(clamp(p / 0.23));
    ctx.save();
    ctx.globalAlpha = titleIn;
    ctx.translate(0, lerp(46, 0, titleIn));
    setFont(ctx, 108, 780);
    ctx.fillStyle = C.white;
    ctx.fillText("How does", 72, 380);
    ctx.fillText("multimodal AI", 72, 502);
    ctx.fillStyle = C.coral;
    ctx.fillText("work?", 72, 624);
    ctx.restore();

    drawParagraph(
      ctx,
      "Different senses become shared notes.",
      76,
      725,
      820,
      38,
      52,
      C.mist,
      580,
    );

    const orbitP = easeInOut(clamp((p - 0.18) / 0.66));
    ctx.save();
    ctx.translate(540, 1110);
    ctx.rotate(t * 0.12);
    ctx.strokeStyle = "rgba(113, 221, 216, 0.22)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(0, 0, 332, -2.75, -0.48);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, 242, 0.2, 2.65);
    ctx.strokeStyle = "rgba(255, 158, 138, 0.2)";
    ctx.stroke();
    ctx.restore();

    const cx = 540 + Math.cos(t * 0.7) * 14;
    const cy = 1110 + Math.sin(t * 0.8) * 12;
    const halo = ctx.createRadialGradient(cx, cy, 30, cx, cy, 270);
    halo.addColorStop(0, "rgba(82, 215, 208, 0.18)");
    halo.addColorStop(1, "rgba(82, 215, 208, 0)");
    ctx.fillStyle = halo;
    ctx.fillRect(cx - 290, cy - 290, 580, 580);
    fillRounded(ctx, cx - 142, cy - 142, 284, 284, 72, "rgba(18, 38, 57, 0.92)", "rgba(173, 224, 236, 0.22)", 3);
    drawTracked(ctx, "ONE", cx - 52, cy - 24, 30, C.mist, 800, 3);
    drawTracked(ctx, "MODEL", cx - 92, cy + 43, 50, C.white, 780, 1.2);

    const positions = [
      { x: 180, y: 950, label: "IMAGE", color: C.coral, fn: drawImageGlyph },
      { x: 540, y: 825, label: "AUDIO", color: C.cyan, fn: drawAudioGlyph },
      { x: 888, y: 1245, label: "TEXT", color: C.gold, fn: drawTextGlyph },
    ];
    positions.forEach((item, index) => {
      const phase = easeOut(clamp((p - 0.04 - index * 0.08) / 0.45));
      const driftX = Math.cos(t * (0.7 + index * 0.12) + index) * 12;
      const driftY = Math.sin(t * (0.8 + index * 0.08) + index * 2) * 12;
      item.fn(ctx, item.x + driftX, item.y + driftY, 132, phase, item.color);
      drawPill(ctx, item.x - 82, item.y + 90, 164, item.label, item.color, phase);
    });
  }

  function drawArrow(ctx, x1, y1, x2, y2, color, progress = 1, width = 5) {
    const p = easeOut(clamp(progress));
    const xm = lerp(x1, x2, p);
    const ym = lerp(y1, y2, p);
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(xm, ym);
    ctx.stroke();
    if (p > 0.92) {
      const angle = Math.atan2(y2 - y1, x2 - x1);
      ctx.translate(x2, y2);
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.moveTo(-18, -12);
      ctx.lineTo(0, 0);
      ctx.lineTo(-18, 12);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawImageScene(ctx, t, timing, p) {
    drawKicker(ctx, 2, "IMAGE", C.coral, p);
    drawParagraph(ctx, "An image becomes a map of visual relationships.", 72, 310, 860, 66, 78, C.white, 760);
    drawParagraph(ctx, "The model can represent what it sees without keeping the pixels.", 76, 520, 810, 32, 45, C.mist, 560);

    const cardP = easeOut(clamp((p - 0.12) / 0.5));
    ctx.save();
    ctx.globalAlpha = cardP;
    ctx.translate(0, lerp(70, 0, cardP));
    fillRounded(ctx, 72, 650, 650, 565, 42, "rgba(16, 31, 48, 0.92)", "rgba(193, 218, 236, 0.16)", 3);
    const sky = ctx.createLinearGradient(0, 690, 0, 1170);
    sky.addColorStop(0, "#28475f");
    sky.addColorStop(0.52, "#f27c72");
    sky.addColorStop(1, "#66364d");
    fillRounded(ctx, 106, 685, 582, 352, 27, sky);
    ctx.beginPath();
    ctx.arc(564, 788, 58, 0, Math.PI * 2);
    ctx.fillStyle = C.gold;
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(106, 1037);
    ctx.lineTo(322, 824);
    ctx.lineTo(512, 1037);
    ctx.closePath();
    ctx.fillStyle = "#223b51";
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(350, 1037);
    ctx.lineTo(518, 886);
    ctx.lineTo(688, 1037);
    ctx.closePath();
    ctx.fillStyle = "#315773";
    ctx.fill();
    drawTracked(ctx, "PIXELS", 130, 1110, 18, C.mist, 750, 2.1);
    drawTracked(ctx, "COLOUR / SHAPE / RELATION", 130, 1160, 25, C.white, 700, 1.2);
    ctx.restore();

    const pathP = easeInOut(clamp((p - 0.25) / 0.55));
    drawArrow(ctx, 724, 932, 850, 932, "rgba(255, 123, 107, 0.72)", pathP, 7);

    ctx.save();
    ctx.translate(864, 760);
    fillRounded(ctx, -112, 0, 224, 460, 38, "rgba(12, 27, 43, 0.94)", "rgba(194, 219, 238, 0.16)", 3);
    drawTracked(ctx, "VISUAL", -68, 54, 19, C.coral2, 780, 1.5);
    drawTracked(ctx, "NOTES", -51, 92, 27, C.white, 780, 1.5);
    const tags = ["edge", "colour", "space"];
    tags.forEach((tag, index) => {
      const y = 160 + index * 88;
      const local = easeOut(clamp((pathP - index * 0.12) / 0.48));
      ctx.globalAlpha = local;
      fillRounded(ctx, -78, y, 156, 54, 27, "rgba(255, 123, 107, 0.14)", "rgba(255, 123, 107, 0.32)");
      drawTracked(ctx, tag, -36, y + 36, 19, C.coral2, 680, 0.8);
      ctx.globalAlpha = 1;
    });
    for (let i = 0; i < 8; i += 1) {
      const pulse = 0.5 + 0.5 * Math.sin(t * 3 + i * 0.9);
      ctx.beginPath();
      ctx.arc(-66 + (i % 4) * 44, 435 + Math.floor(i / 4) * 32, 5 + pulse * 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 123, 107, ${0.32 + pulse * 0.45})`;
      ctx.fill();
    }
    ctx.restore();
  }

  function drawAudioScene(ctx, t, timing, p) {
    drawKicker(ctx, 3, "AUDIO", C.cyan, p);
    drawParagraph(ctx, "Audio becomes a pattern of timing and tone.", 72, 310, 870, 66, 78, C.white, 760);
    drawParagraph(ctx, "The waveform is compressed into acoustic notes the model can compare.", 76, 520, 850, 32, 45, C.mist, 560);

    const reveal = easeOut(clamp(p / 0.42));
    ctx.save();
    ctx.translate(540, 955);
    const glow = ctx.createRadialGradient(0, 0, 40, 0, 0, 500);
    glow.addColorStop(0, "rgba(82, 215, 208, 0.16)");
    glow.addColorStop(1, "rgba(82, 215, 208, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(-520, -520, 1040, 1040);

    for (let ring = 0; ring < 4; ring += 1) {
      ctx.beginPath();
      ctx.arc(0, 0, 220 + ring * 58, t * (0.2 + ring * 0.03), Math.PI * 1.7 + t * (0.2 + ring * 0.03));
      ctx.strokeStyle = `rgba(82, 215, 208, ${0.17 - ring * 0.025})`;
      ctx.lineWidth = 3;
      ctx.stroke();
    }

    ctx.lineCap = "round";
    for (let i = -13; i <= 13; i += 1) {
      const x = i * 28;
      const envelope = Math.pow(1 - Math.abs(i) / 16, 0.65);
      const motion =
        Math.sin(t * 4.1 + i * 0.62) * 0.5 +
        Math.sin(t * 2.15 + i * 0.31) * 0.32 +
        Math.sin(t * 6.3 + i) * 0.12;
      const height = (56 + Math.abs(motion) * 240) * envelope * reveal;
      const gradient = ctx.createLinearGradient(0, -height / 2, 0, height / 2);
      gradient.addColorStop(0, C.cyan2);
      gradient.addColorStop(0.5, C.cyan);
      gradient.addColorStop(1, "#277c91");
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 12;
      ctx.beginPath();
      ctx.moveTo(x, -height / 2);
      ctx.lineTo(x, height / 2);
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.arc(0, 0, 112, 0, Math.PI * 2);
    ctx.fillStyle = "#10263a";
    ctx.fill();
    ctx.strokeStyle = "rgba(166, 238, 235, 0.34)";
    ctx.lineWidth = 3;
    ctx.stroke();
    drawTracked(ctx, "TONE", -51, -4, 23, C.cyan2, 780, 1.8);
    drawTracked(ctx, "RHYTHM", -73, 38, 23, C.white, 780, 1.2);
    ctx.restore();

    const tags = [
      { x: 98, label: "TIMING", color: C.cyan },
      { x: 404, label: "TONE", color: C.violet },
      { x: 686, label: "RHYTHM", color: C.gold },
    ];
    tags.forEach((tag, index) => {
      const local = easeOut(clamp((p - 0.24 - index * 0.1) / 0.42));
      drawPill(ctx, tag.x, 1325, 246, tag.label, tag.color, local);
    });
    drawParagraph(
      ctx,
      "sound -> acoustic representation",
      98,
      1480,
      820,
      35,
      46,
      C.white,
      700,
    );
  }

  function drawTextScene(ctx, t, timing, p) {
    drawKicker(ctx, 4, "TEXT", C.gold, p);
    drawParagraph(ctx, "Text becomes a web of words and context.", 72, 310, 860, 66, 78, C.white, 760);
    drawParagraph(ctx, "Tokens carry ideas into a representation the model can align.", 76, 520, 850, 32, 45, C.mist, 560);

    const words = [
      { text: "bright", x: 82, y: 700, w: 250, color: C.gold },
      { text: "quiet", x: 362, y: 700, w: 226, color: C.cyan },
      { text: "morning", x: 618, y: 700, w: 336, color: C.coral },
      { text: "idea", x: 82, y: 835, w: 210, color: C.violet },
      { text: "context", x: 322, y: 835, w: 288, color: C.gold },
      { text: "meaning", x: 640, y: 835, w: 314, color: C.cyan },
    ];
    words.forEach((word, index) => {
      const local = easeOut(clamp((p - 0.12 - index * 0.055) / 0.4));
      const bob = Math.sin(t * 2.2 + index * 0.9) * 4;
      ctx.save();
      ctx.globalAlpha = local;
      fillRounded(ctx, word.x, word.y + bob, word.w, 92, 46, "rgba(18, 35, 53, 0.94)", "rgba(198, 220, 237, 0.16)", 2);
      ctx.beginPath();
      ctx.arc(word.x + 35, word.y + 46 + bob, 9, 0, Math.PI * 2);
      ctx.fillStyle = word.color;
      ctx.fill();
      drawTracked(ctx, word.text, word.x + 60, word.y + 59 + bob, 27, C.white, 680, 0.7);
      ctx.restore();
    });

    drawArrow(ctx, 540, 968, 540, 1088, "rgba(246, 198, 103, 0.75)", easeInOut(clamp((p - 0.34) / 0.36)), 6);
    const vectorP = easeOut(clamp((p - 0.32) / 0.52));
    fillRounded(ctx, 128, 1110, 824, 314, 42, "rgba(14, 30, 47, 0.95)", "rgba(198, 220, 237, 0.16)", 3);
    drawTracked(ctx, "SEMANTIC NOTES", 176, 1172, 20, C.gold, 780, 2);
    for (let row = 0; row < 3; row += 1) {
      const y = 1212 + row * 56;
      const rowP = clamp((vectorP - row * 0.12) / 0.58);
      fillRounded(ctx, 176, y, 728 * easeOut(rowP), 30, 15, row === 1 ? "rgba(246, 198, 103, 0.62)" : "rgba(82, 215, 208, 0.46)");
      for (let dot = 0; dot < 7; dot += 1) {
        ctx.beginPath();
        ctx.arc(196 + dot * 106, y + 15, 6, 0, Math.PI * 2);
        ctx.fillStyle = dot % 2 === 0 ? C.white : C.muted;
        ctx.fill();
      }
    }
    drawTracked(ctx, "words -> shared representation", 176, 1402, 25, C.white, 650, 1.1);
  }

  function drawConnector(ctx, startX, startY, endX, endY, color, progress, bend) {
    const p = easeInOut(clamp(progress));
    const controlX = lerp(startX, endX, 0.52);
    const controlY = lerp(startY, endY, 0.52) + bend;
    const end = p;
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 8;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    const samples = 28;
    for (let i = 1; i <= samples * end; i += 1) {
      const u = i / samples;
      const x = (1 - u) * (1 - u) * startX + 2 * (1 - u) * u * controlX + u * u * endX;
      const y = (1 - u) * (1 - u) * startY + 2 * (1 - u) * u * controlY + u * u * endY;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
    const u = end;
    const x = (1 - u) * (1 - u) * startX + 2 * (1 - u) * u * controlX + u * u * endX;
    const y = (1 - u) * (1 - u) * startY + 2 * (1 - u) * u * controlY + u * u * endY;
    ctx.beginPath();
    ctx.arc(x, y, 11, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.restore();
  }

  function drawConvergeScene(ctx, t, timing, p) {
    drawKicker(ctx, 5, "REPRESENTATIONS", C.violet, p);
    drawParagraph(ctx, "Different senses become shared notes.", 72, 310, 900, 72, 82, C.white, 780);
    drawParagraph(ctx, "Each modality is encoded into a compatible space.", 76, 510, 850, 32, 45, C.mist, 560);

    const sourceP = easeOut(clamp(p / 0.22));
    drawImageGlyph(ctx, 170, 725, 112, sourceP, C.coral);
    drawAudioGlyph(ctx, 540, 675, 112, t, C.cyan);
    drawTextGlyph(ctx, 888, 725, 112, sourceP, C.gold);
    drawPill(ctx, 82, 825, 176, "IMAGE", C.coral, sourceP);
    drawPill(ctx, 452, 775, 176, "AUDIO", C.cyan, sourceP);
    drawPill(ctx, 800, 825, 176, "TEXT", C.gold, sourceP);

    const connectorP = easeInOut(clamp((p - 0.13) / 0.54));
    drawConnector(ctx, 170, 888, 540, 1060, "rgba(255, 123, 107, 0.82)", connectorP, -70);
    drawConnector(ctx, 540, 838, 540, 1060, "rgba(82, 215, 208, 0.82)", connectorP, 0);
    drawConnector(ctx, 888, 888, 540, 1060, "rgba(246, 198, 103, 0.82)", connectorP, 70);

    const cardP = easeOut(clamp((p - 0.22) / 0.52));
    ctx.save();
    ctx.globalAlpha = cardP;
    ctx.translate(540, 1265);
    ctx.scale(lerp(0.88, 1, cardP), lerp(0.88, 1, cardP));
    const cardGlow = ctx.createRadialGradient(0, 0, 60, 0, 0, 470);
    cardGlow.addColorStop(0, "rgba(167, 139, 250, 0.18)");
    cardGlow.addColorStop(1, "rgba(167, 139, 250, 0)");
    ctx.fillStyle = cardGlow;
    ctx.fillRect(-500, -500, 1000, 1000);
    fillRounded(ctx, -430, -230, 860, 460, 58, "rgba(18, 34, 53, 0.96)", "rgba(195, 185, 255, 0.27)", 3);
    drawTracked(ctx, "SHARED NOTES", -194, -154, 23, C.violet, 800, 2.6);
    const rows = [
      { label: "visual", value: "edges / colour / space", color: C.coral },
      { label: "acoustic", value: "tone / rhythm / timing", color: C.cyan },
      { label: "semantic", value: "words / ideas / context", color: C.gold },
    ];
    rows.forEach((row, index) => {
      const y = -62 + index * 88;
      const rowP = clamp((connectorP - 0.25 - index * 0.12) / 0.5);
      ctx.globalAlpha = cardP * rowP;
      fillRounded(ctx, -360, y, 720, 64, 32, "rgba(255, 255, 255, 0.045)", "rgba(200, 219, 235, 0.12)");
      drawTracked(ctx, row.label.toUpperCase(), -326, y + 41, 18, row.color, 780, 1.4);
      drawTracked(ctx, row.value, -132, y + 41, 22, C.white, 620, 0.4);
    });
    ctx.restore();
  }

  function drawAnswerScene(ctx, t, timing, p) {
    drawKicker(ctx, 6, "COMBINED ANSWER", C.coral, p);
    drawParagraph(ctx, "The model joins the shared notes.", 72, 315, 880, 68, 80, C.white, 780);
    drawParagraph(ctx, "Then it produces one answer.", 76, 515, 820, 34, 47, C.mist, 580);

    const reveal = easeOut(clamp(p / 0.42));
    ctx.save();
    ctx.translate(540, 1035);
    ctx.scale(lerp(0.9, 1, reveal), lerp(0.9, 1, reveal));
    ctx.rotate(Math.sin(t * 0.8) * 0.008);
    const glow = ctx.createRadialGradient(0, 0, 80, 0, 0, 530);
    glow.addColorStop(0, "rgba(255, 123, 107, 0.22)");
    glow.addColorStop(0.58, "rgba(82, 215, 208, 0.1)");
    glow.addColorStop(1, "rgba(82, 215, 208, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(-560, -560, 1120, 1120);
    fillRounded(ctx, -432, -315, 864, 630, 64, "rgba(19, 37, 57, 0.97)", "rgba(205, 226, 241, 0.22)", 3);
    drawTracked(ctx, "COMBINED ANSWER", -172, -232, 22, C.coral2, 800, 2.4);
    drawTracked(ctx, "ONE", -130, -82, 78, C.white, 820, 2);
    drawTracked(ctx, "ANSWER", -237, 25, 108, C.white, 820, 1.4);
    drawParagraph(
      ctx,
      "from image + audio + text",
      -310,
      133,
      620,
      31,
      42,
      C.mist,
      620,
    );
    const chips = [
      { label: "IMAGE", x: -310, color: C.coral },
      { label: "AUDIO", x: -110, color: C.cyan },
      { label: "TEXT", x: 90, color: C.gold },
    ];
    chips.forEach((chip, index) => {
      const chipP = clamp((reveal - 0.22 - index * 0.1) / 0.55);
      drawPill(ctx, chip.x, 206, 180, chip.label, chip.color, chipP);
    });
    ctx.restore();

    const endP = easeOut(clamp((p - 0.5) / 0.5));
    ctx.save();
    ctx.globalAlpha = endP;
    drawTracked(ctx, "DIFFERENT SENSES", 72, 1518, 26, C.mist, 780, 3);
    drawTracked(ctx, "BECOME SHARED NOTES.", 72, 1582, 48, C.white, 800, 0.6);
    ctx.fillStyle = C.coral;
    fillRounded(ctx, 72, 1612, 510 * endP, 11, 5.5, C.coral);
    ctx.restore();
  }

  function sceneForTime(t, timing) {
    const starts = timing.cues.map((cue) => cue.start);
    const bounds = [
      { key: "hook", start: 0, end: Math.max(2.8, starts[1] - 0.2) },
      { key: "image", start: Math.max(2.8, starts[1] - 0.2), end: starts[2] - 0.15 },
      { key: "audio", start: starts[2] - 0.15, end: starts[3] - 0.15 },
      { key: "text", start: starts[3] - 0.15, end: starts[4] - 0.15 },
      { key: "converge", start: starts[4] - 0.15, end: starts[5] - 0.15 },
      { key: "answer", start: starts[5] - 0.15, end: timing.duration + 0.2 },
    ];
    return bounds.find((item) => t < item.end) || bounds[bounds.length - 1];
  }

  function drawFrame(ctx, t, timing) {
    const time = clamp(t, 0, timing.duration);
    const scene = sceneForTime(time, timing);
    const p = clamp((time - scene.start) / Math.max(0.2, scene.end - scene.start));
    drawBackground(ctx, time);
    if (scene.key === "hook") drawHook(ctx, time, timing, p);
    if (scene.key === "image") drawImageScene(ctx, time, timing, p);
    if (scene.key === "audio") drawAudioScene(ctx, time, timing, p);
    if (scene.key === "text") drawTextScene(ctx, time, timing, p);
    if (scene.key === "converge") drawConvergeScene(ctx, time, timing, p);
    if (scene.key === "answer") drawAnswerScene(ctx, time, timing, p);
    drawChrome(ctx, time, timing, scene.key);
    drawCaption(ctx, time, timing);

    const transition = 0.18;
    const sceneProgress = p;
    if (sceneProgress < transition && scene.start > 0) {
      const alpha = 1 - sceneProgress / transition;
      ctx.fillStyle = `rgba(7, 16, 27, ${alpha * 0.42})`;
      ctx.fillRect(0, 0, W, H);
      const wipe = ctx.createLinearGradient(0, 0, W, 0);
      wipe.addColorStop(0, "rgba(82, 215, 208, 0)");
      wipe.addColorStop(0.52, `rgba(82, 215, 208, ${alpha * 0.12})`);
      wipe.addColorStop(1, "rgba(82, 215, 208, 0)");
      ctx.fillStyle = wipe;
      ctx.fillRect(0, 0, W, H);
    }
  }

  window.SceneRenderer = Object.freeze({
    width: W,
    height: H,
    fps: FPS,
    drawFrame,
  });
})();
