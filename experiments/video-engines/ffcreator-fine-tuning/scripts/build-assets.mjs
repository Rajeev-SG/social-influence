import {createCanvas, registerFont} from 'canvas';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outDir = path.join(root, 'assets', 'visuals');
fs.mkdirSync(outDir, {recursive: true});

registerFont(path.join(root, 'assets', 'fonts', 'Manrope.ttf'), {family: 'Manrope'});
registerFont(path.join(root, 'assets', 'fonts', 'Mono.ttf'), {family: 'Mono'});

const C = {
  ink: '#F7F2E8',
  muted: '#A7B4B0',
  navy: '#07151B',
  panel: '#10252C',
  cyan: '#67E8D3',
  blue: '#6D8CFF',
  coral: '#FF785A',
  amber: '#FFD166',
  line: '#294249',
};

function save(name, canvas) {
  fs.writeFileSync(path.join(outDir, name), canvas.toBuffer('image/png'));
}

function roundedRect(ctx, x, y, w, h, r, fill, stroke = null, lineWidth = 2) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  if (fill) {
    ctx.fillStyle = fill;
    ctx.fill();
  }
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = lineWidth;
    ctx.stroke();
  }
}

function text(ctx, value, x, y, size, color = C.ink, weight = 650, family = 'Manrope', align = 'left') {
  ctx.save();
  ctx.font = `${weight} ${size}px ${family}`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(value, x, y);
  ctx.restore();
}

function line(ctx, x1, y1, x2, y2, color, width = 2, alpha = 1) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
  ctx.restore();
}

function buildBackground() {
  const canvas = createCanvas(1080, 1920);
  const ctx = canvas.getContext('2d');
  const bg = ctx.createLinearGradient(0, 0, 0, 1920);
  bg.addColorStop(0, '#061218');
  bg.addColorStop(0.55, '#0A1C23');
  bg.addColorStop(1, '#07151B');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, 1080, 1920);

  const topGlow = ctx.createRadialGradient(540, 390, 80, 540, 390, 690);
  topGlow.addColorStop(0, 'rgba(109,140,255,0.22)');
  topGlow.addColorStop(0.55, 'rgba(103,232,211,0.07)');
  topGlow.addColorStop(1, 'rgba(7,21,27,0)');
  ctx.fillStyle = topGlow;
  ctx.fillRect(0, 0, 1080, 1200);

  const warmGlow = ctx.createRadialGradient(880, 1510, 30, 880, 1510, 580);
  warmGlow.addColorStop(0, 'rgba(255,120,90,0.12)');
  warmGlow.addColorStop(1, 'rgba(7,21,27,0)');
  ctx.fillStyle = warmGlow;
  ctx.fillRect(0, 900, 1080, 1020);

  ctx.save();
  ctx.globalAlpha = 0.16;
  for (let x = 60; x < 1080; x += 120) line(ctx, x, 0, x, 1920, C.line, 1);
  for (let y = 100; y < 1920; y += 140) line(ctx, 0, y, 1080, y, C.line, 1);
  ctx.restore();

  line(ctx, 82, 120, 300, 120, C.cyan, 4, 0.8);
  line(ctx, 780, 1800, 998, 1800, C.coral, 4, 0.7);
  save('background.png', canvas);
}

function buildCore() {
  const canvas = createCanvas(680, 680);
  const ctx = canvas.getContext('2d');
  ctx.translate(340, 340);
  for (const [radius, color, width, alpha] of [
    [276, C.blue, 2, 0.28],
    [224, C.cyan, 3, 0.36],
    [170, C.coral, 2, 0.22],
  ]) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.setLineDash([10, 18]);
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  const halo = ctx.createRadialGradient(0, 0, 20, 0, 0, 215);
  halo.addColorStop(0, 'rgba(103,232,211,0.26)');
  halo.addColorStop(1, 'rgba(103,232,211,0)');
  ctx.fillStyle = halo;
  ctx.fillRect(-230, -230, 460, 460);

  const top = [[0, -156], [152, -74], [0, 8], [-152, -74]];
  const bottom = [[0, 8], [152, -74], [152, 112], [0, 194]];
  const left = [[0, 8], [-152, -74], [-152, 112], [0, 194]];
  const poly = (points, fill, stroke) => {
    ctx.beginPath();
    points.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 3;
    ctx.stroke();
  };
  poly(top, '#21404A', C.cyan);
  poly(bottom, '#132E38', C.blue);
  poly(left, '#17343E', C.coral);

  for (let row = -2; row <= 2; row += 1) {
    for (let col = -2; col <= 2; col += 1) {
      const x = col * 42 + row * 18;
      const y = row * 38 - 20;
      ctx.fillStyle = (row + col) % 3 === 0 ? C.cyan : C.blue;
      ctx.globalAlpha = 0.42 + 0.08 * ((row + col + 10) % 3);
      ctx.fillRect(x - 6, y - 6, 12, 12);
    }
  }
  ctx.globalAlpha = 1;
  const nodes = [[-240, -210], [250, -170], [-270, 182], [238, 216], [0, -282], [0, 292]];
  for (const [x, y] of nodes) {
    line(ctx, x * 0.45, y * 0.45, x, y, C.cyan, 2, 0.32);
    ctx.fillStyle = C.cyan;
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#07151B';
    ctx.lineWidth = 4;
    ctx.stroke();
  }
  save('core.png', canvas);
}

function buildSkillChip(name, label, accent) {
  const canvas = createCanvas(300, 92);
  const ctx = canvas.getContext('2d');
  roundedRect(ctx, 2, 2, 296, 88, 22, 'rgba(16,37,44,0.94)', accent, 3);
  ctx.fillStyle = accent;
  ctx.beginPath();
  ctx.arc(40, 46, 12, 0, Math.PI * 2);
  ctx.fill();
  text(ctx, label, 70, 58, 31, C.ink, 700);
  save(name, canvas);
}

function buildCourseCard(index, kicker, titleValue, body, accent) {
  const canvas = createCanvas(320, 380);
  const ctx = canvas.getContext('2d');
  roundedRect(ctx, 4, 4, 312, 372, 30, 'rgba(15,39,47,0.97)', accent, 3);
  roundedRect(ctx, 28, 30, 264, 58, 18, accent);
  text(ctx, kicker, 160, 69, 22, '#07151B', 800, 'Mono', 'center');
  text(ctx, titleValue, 28, 145, 38, C.ink, 750);
  const lines = body.split('|');
  lines.forEach((value, i) => text(ctx, value, 28, 207 + i * 40, 25, C.muted, 500));
  line(ctx, 28, 326, 292, 326, C.line, 2);
  text(ctx, `EXAMPLE ${String(index + 1).padStart(2, '0')}`, 28, 354, 18, accent, 700, 'Mono');
  save(`course-card-${index + 1}.png`, canvas);
}

function buildFeedback() {
  const check = createCanvas(180, 180);
  const ctx = check.getContext('2d');
  ctx.fillStyle = C.cyan;
  ctx.beginPath();
  ctx.arc(90, 90, 72, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#07151B';
  ctx.lineWidth = 14;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(52, 91);
  ctx.lineTo(79, 118);
  ctx.lineTo(130, 61);
  ctx.stroke();
  save('feedback-check.png', check);

  const edit = createCanvas(180, 180);
  const e = edit.getContext('2d');
  e.fillStyle = C.amber;
  e.beginPath();
  e.arc(90, 90, 72, 0, Math.PI * 2);
  e.fill();
  e.strokeStyle = '#07151B';
  e.lineWidth = 11;
  e.lineCap = 'round';
  e.beginPath();
  e.moveTo(56, 116);
  e.lineTo(119, 53);
  e.moveTo(68, 58);
  e.lineTo(116, 106);
  e.stroke();
  save('feedback-edit.png', edit);
}

function buildChef() {
  const canvas = createCanvas(430, 560);
  const ctx = canvas.getContext('2d');
  const glow = ctx.createRadialGradient(215, 310, 20, 215, 310, 230);
  glow.addColorStop(0, 'rgba(255,209,102,0.16)');
  glow.addColorStop(1, 'rgba(255,209,102,0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, 430, 560);

  roundedRect(ctx, 95, 300, 240, 222, 76, '#17323A', C.amber, 4);
  roundedRect(ctx, 138, 263, 154, 126, 56, '#D69A72', '#F7C39A', 4);
  ctx.fillStyle = '#2B211E';
  ctx.beginPath();
  ctx.arc(181, 322, 8, 0, Math.PI * 2);
  ctx.arc(250, 322, 8, 0, Math.PI * 2);
  ctx.fill();
  line(ctx, 190, 356, 242, 356, '#7D4637', 5, 1);

  roundedRect(ctx, 94, 132, 242, 162, 74, '#F7F2E8', C.ink, 4);
  ctx.fillStyle = '#F7F2E8';
  ctx.beginPath();
  ctx.arc(132, 142, 56, 0, Math.PI * 2);
  ctx.arc(214, 116, 70, 0, Math.PI * 2);
  ctx.arc(300, 148, 54, 0, Math.PI * 2);
  ctx.fill();
  line(ctx, 111, 254, 320, 254, '#C8C3B9', 3, 1);
  line(ctx, 136, 281, 294, 281, C.coral, 6, 1);

  ctx.strokeStyle = C.amber;
  ctx.lineWidth = 8;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(332, 374);
  ctx.bezierCurveTo(382, 332, 396, 295, 380, 260);
  ctx.stroke();
  for (let i = 0; i < 3; i += 1) {
    ctx.beginPath();
    ctx.moveTo(375 - i * 8, 275 + i * 6);
    ctx.lineTo(398 + i * 4, 260 + i * 3);
    ctx.stroke();
  }
  save('chef.png', canvas);
}

function buildPastry() {
  const canvas = createCanvas(500, 330);
  const ctx = canvas.getContext('2d');
  const glow = ctx.createRadialGradient(250, 170, 10, 250, 170, 235);
  glow.addColorStop(0, 'rgba(255,209,102,0.20)');
  glow.addColorStop(1, 'rgba(255,209,102,0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, 500, 330);
  ctx.strokeStyle = C.amber;
  ctx.lineWidth = 34;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.arc(250, 162, 112, Math.PI * 0.18, Math.PI * 1.82);
  ctx.stroke();
  ctx.lineWidth = 7;
  ctx.strokeStyle = '#FFE4A3';
  for (const offset of [-55, 0, 55]) {
    ctx.beginPath();
    ctx.arc(250 + offset * 0.28, 162, 84, Math.PI * 0.35, Math.PI * 1.65);
    ctx.stroke();
  }
  ctx.fillStyle = C.coral;
  for (const [x, y] of [[92, 96], [408, 105], [84, 244], [422, 236]]) {
    ctx.beginPath();
    ctx.arc(x, y, 7, 0, Math.PI * 2);
    ctx.fill();
  }
  save('pastry.png', canvas);
}

function buildRecipeCard() {
  const canvas = createCanvas(380, 400);
  const ctx = canvas.getContext('2d');
  roundedRect(ctx, 4, 4, 372, 392, 28, '#122B33', C.coral, 3);
  text(ctx, 'HOUSE STYLE', 30, 58, 23, C.coral, 800, 'Mono');
  text(ctx, 'croissants', 30, 116, 47, C.ink, 750);
  const rows = [
    ['01', 'laminate'],
    ['02', 'proof'],
    ['03', 'shape'],
    ['04', 'bake'],
  ];
  rows.forEach(([n, label], i) => {
    const y = 180 + i * 52;
    ctx.fillStyle = i === 2 ? C.amber : C.cyan;
    ctx.beginPath();
    ctx.arc(46, y - 7, 14, 0, Math.PI * 2);
    ctx.fill();
    text(ctx, n, 46, y, 15, '#07151B', 800, 'Mono', 'center');
    text(ctx, label, 78, y, 28, i === 2 ? C.amber : C.ink, 650);
    line(ctx, 78, y + 16, 334, y + 16, C.line, 2);
  });
  save('recipe-card.png', canvas);
}

function drawDials(ctx, tuned) {
  roundedRect(ctx, 4, 4, 812, 512, 32, 'rgba(13,34,42,0.98)', tuned ? C.cyan : C.line, 4);
  text(ctx, tuned ? 'SELECTED SETTINGS ADJUST' : 'BROAD INTERNAL SETTINGS', 42, 62, 28, tuned ? C.cyan : C.muted, 800, 'Mono');
  const labels = ['tone', 'format', 'domain', 'style', 'facts', 'tools'];
  const active = new Set([0, 1, 2, 3, 5]);
  labels.forEach((label, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 140 + col * 270;
    const y = 188 + row * 185;
    const color = tuned && active.has(i) ? (i % 2 ? C.coral : C.cyan) : '#587077';
    ctx.strokeStyle = color;
    ctx.lineWidth = tuned && active.has(i) ? 7 : 4;
    ctx.beginPath();
    ctx.arc(x, y, 66, 0, Math.PI * 2);
    ctx.stroke();
    line(ctx, x, y, x + Math.cos(-Math.PI / 2 + i * 0.42 + (tuned && active.has(i) ? 0.9 : 0)) * 48,
      y + Math.sin(-Math.PI / 2 + i * 0.42 + (tuned && active.has(i) ? 0.9 : 0)) * 48,
      color, tuned && active.has(i) ? 8 : 5);
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.fill();
    text(ctx, label, x, y + 112, 27, tuned && active.has(i) ? C.ink : C.muted, 700, 'Manrope', 'center');
  });
}

function buildDials() {
  for (const [name, tuned] of [['dials-base.png', false], ['dials-tuned.png', true]]) {
    const canvas = createCanvas(820, 520);
    drawDials(canvas.getContext('2d'), tuned);
    save(name, canvas);
  }
}

function buildOutcomeModels() {
  const make = (name, specialist) => {
    const canvas = createCanvas(440, 520);
    const ctx = canvas.getContext('2d');
    const accent = specialist ? C.coral : C.blue;
    roundedRect(ctx, 8, 8, 424, 504, 38, specialist ? '#2B2023' : '#132A39', accent, 5);
    text(ctx, specialist ? 'SPECIALIST' : 'BASE MODEL', 220, 68, 27, accent, 800, 'Mono', 'center');
    roundedRect(ctx, 52, 112, 336, 254, 28, specialist ? '#4B2B2A' : '#1A3850', null);
    for (let row = 0; row < 5; row += 1) {
      for (let col = 0; col < 6; col += 1) {
        const active = specialist && [0, 1, 2, 7, 8].includes(row * 6 + col);
        ctx.fillStyle = active ? C.coral : (row + col) % 3 === 0 ? C.cyan : C.blue;
        ctx.globalAlpha = active ? 0.92 : 0.38;
        roundedRect(ctx, 82 + col * 48, 140 + row * 44, 26, 22, 6, ctx.fillStyle);
      }
    }
    ctx.globalAlpha = 1;
    text(ctx, specialist ? 'focused behavior' : 'broad patterns', 220, 426, 32, C.ink, 700, 'Manrope', 'center');
    text(ctx, specialist ? 'same foundation' : 'ready to adapt', 220, 472, 23, C.muted, 550, 'Manrope', 'center');
    save(name, canvas);
  };
  make('base-model.png', false);
  make('specialist-model.png', true);
}

function buildArrow() {
  const canvas = createCanvas(320, 120);
  const ctx = canvas.getContext('2d');
  line(ctx, 18, 60, 270, 60, C.cyan, 12);
  ctx.fillStyle = C.cyan;
  ctx.beginPath();
  ctx.moveTo(300, 60);
  ctx.lineTo(245, 22);
  ctx.lineTo(245, 98);
  ctx.closePath();
  ctx.fill();
  save('outcome-arrow.png', canvas);
}

function buildCaptionBackground() {
  const canvas = createCanvas(920, 180);
  const ctx = canvas.getContext('2d');
  roundedRect(ctx, 2, 2, 916, 176, 34, 'rgba(5,16,21,0.82)', 'rgba(103,232,211,0.22)', 2);
  save('caption-bg.png', canvas);
}

buildBackground();
buildCore();
buildSkillChip('chip-language.png', 'language', C.cyan);
buildSkillChip('chip-code.png', 'code', C.blue);
buildSkillChip('chip-reasoning.png', 'reasoning', C.coral);
buildSkillChip('chip-style.png', 'style', C.amber);
buildCourseCard(0, 'CURATED', 'Clear answers', 'specific|and labelled', C.cyan);
buildCourseCard(1, 'FEEDBACK', 'Correct misses', 'coach says|try again', C.amber);
buildCourseCard(2, 'REPEAT', 'Build habits', 'fewer examples|better fit', C.coral);
buildFeedback();
buildChef();
buildPastry();
buildRecipeCard();
buildDials();
buildOutcomeModels();
buildArrow();
buildCaptionBackground();

console.log(`wrote ${fs.readdirSync(outDir).length} visual assets to ${outDir}`);
