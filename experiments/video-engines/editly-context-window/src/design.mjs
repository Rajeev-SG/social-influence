export const W = 1080;
export const H = 1920;

export const C = {
  bg: '#F3EFE7',
  bgDeep: '#DDD7CB',
  ink: '#14232D',
  muted: '#68747B',
  line: '#C9C2B6',
  paper: '#FFFDF7',
  blue: '#2864FF',
  teal: '#19A99B',
  coral: '#F06449',
  yellow: '#F2C14E',
  dark: '#14232D',
};

export const clamp = (value, min = 0, max = 1) => Math.max(min, Math.min(max, value));
export const mix = (a, b, t) => a + (b - a) * t;
export const segment = (value, start, end) => clamp((value - start) / Math.max(0.001, end - start));
export const easeOut = (t) => 1 - (1 - clamp(t)) ** 3;
export const easeInOut = (t) => {
  const x = clamp(t);
  return x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2;
};

export function roundedRect(ctx, x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + width - r, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + r);
  ctx.lineTo(x + width, y + height - r);
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
  ctx.lineTo(x + r, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

export function trackedText(ctx, text, x, y, spacing = 4) {
  let cursor = x;
  for (const character of text) {
    ctx.fillText(character, cursor, y);
    cursor += ctx.measureText(character).width + spacing;
  }
  return cursor - spacing;
}

export function wrapLines(ctx, text, maxWidth) {
  const words = text.split(/\s+/);
  const lines = [];
  let current = '';
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (current && ctx.measureText(candidate).width > maxWidth) {
      lines.push(current);
      current = word;
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  return lines;
}

export function drawRevealLine(ctx, text, x, y, size, progress, color = C.ink, weight = 700) {
  ctx.font = `${weight} ${size}px Manrope`;
  ctx.save();
  ctx.beginPath();
  ctx.rect(x - 8, y - size * 0.88, (ctx.measureText(text).width + 40) * easeOut(progress), size * 1.18);
  ctx.clip();
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  ctx.lineWidth = Math.max(2, size * 0.035);
  ctx.lineJoin = 'round';
  ctx.strokeText(text, x, y);
  ctx.fillText(text, x, y);
  ctx.restore();
}

export function drawBackground(ctx, time, accent = C.blue) {
  const gradient = ctx.createLinearGradient(0, 0, W, H);
  gradient.addColorStop(0, '#FAF7F1');
  gradient.addColorStop(0.52, C.bg);
  gradient.addColorStop(1, '#E5DED2');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, W, H);

  const glow = ctx.createRadialGradient(840, 360, 20, 840, 360, 680);
  glow.addColorStop(0, `${accent}20`);
  glow.addColorStop(1, `${accent}00`);
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, H);

  ctx.save();
  ctx.strokeStyle = '#1B303A0C';
  ctx.lineWidth = 1;
  const drift = (time * 4) % 96;
  for (let x = -96 + drift; x <= W + 96; x += 96) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, H);
    ctx.stroke();
  }
  for (let y = 92; y <= H; y += 96) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(W, y);
    ctx.stroke();
  }
  ctx.restore();

  const vignette = ctx.createRadialGradient(W / 2, H / 2, 420, W / 2, H / 2, 1120);
  vignette.addColorStop(0, '#00000000');
  vignette.addColorStop(1, '#221A101A');
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, W, H);
}

export function drawTopMeta(ctx, index, label, progress = 1) {
  ctx.save();
  ctx.globalAlpha *= easeOut(progress);
  ctx.fillStyle = C.muted;
  ctx.font = '600 23px Mono';
  trackedText(ctx, `0${index} / ${label}`, 82, 126, 3.2);
  ctx.fillStyle = C.blue;
  ctx.fillRect(82, 151, 92 * easeOut(progress), 5);
  ctx.restore();
}

export function drawDeskSurface(ctx, { x, y, width, height, slots = 5, lift = 0 }) {
  ctx.save();
  ctx.translate(0, lift);
  ctx.shadowColor = '#3C2F2130';
  ctx.shadowBlur = 38;
  ctx.shadowOffsetY = 24;
  const surface = ctx.createLinearGradient(x, y, x + width, y + height);
  surface.addColorStop(0, '#D7CFC0');
  surface.addColorStop(0.55, '#C6BBA9');
  surface.addColorStop(1, '#AFA28F');
  roundedRect(ctx, x, y, width, height, 48);
  ctx.fillStyle = surface;
  ctx.fill();
  ctx.shadowColor = 'transparent';

  roundedRect(ctx, x + 18, y + 18, width - 36, height - 72, 34);
  const inner = ctx.createLinearGradient(x, y, x, y + height);
  inner.addColorStop(0, '#EEE8DD');
  inner.addColorStop(1, '#D8CEBF');
  ctx.fillStyle = inner;
  ctx.fill();
  ctx.strokeStyle = '#FFFFFF80';
  ctx.lineWidth = 2;
  ctx.stroke();

  const gap = 18;
  const slotWidth = (width - 64 - gap * (slots - 1)) / slots;
  for (let index = 0; index < slots; index += 1) {
    const sx = x + 32 + index * (slotWidth + gap);
    roundedRect(ctx, sx, y + 72, slotWidth, height - 156, 18);
    ctx.fillStyle = '#9E927F55';
    ctx.fill();
    ctx.strokeStyle = '#8F826F66';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = '#75695728';
    ctx.fillRect(sx + slotWidth / 2 - 17, y + height - 73, 34, 5);
  }
  ctx.restore();
}

export function drawNoteCard(ctx, {
  x,
  y,
  width = 154,
  height = 202,
  label,
  detail = '',
  accent = C.blue,
  alpha = 1,
  rotation = 0,
  scale = 1,
}) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x + width / 2, y + height / 2);
  ctx.rotate(rotation);
  ctx.scale(scale, scale);
  ctx.translate(-width / 2, -height / 2);
  ctx.shadowColor = '#2F241930';
  ctx.shadowBlur = 18;
  ctx.shadowOffsetY = 12;
  roundedRect(ctx, 0, 0, width, height, 16);
  ctx.fillStyle = C.paper;
  ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.fillStyle = accent;
  ctx.fillRect(0, 0, width, 13);
  ctx.fillStyle = C.ink;
  ctx.font = '700 24px Manrope';
  const labelLines = wrapLines(ctx, label, width - 32);
  labelLines.slice(0, 2).forEach((line, index) => ctx.fillText(line, 16, 55 + index * 30));
  if (detail) {
    ctx.fillStyle = C.muted;
    ctx.font = '500 17px Mono';
    const detailLines = wrapLines(ctx, detail, width - 32);
    detailLines.slice(0, 3).forEach((line, index) => ctx.fillText(line, 16, 130 + index * 23));
  }
  ctx.strokeStyle = '#6D625333';
  ctx.lineWidth = 1.5;
  roundedRect(ctx, 0, 0, width, height, 16);
  ctx.stroke();
  ctx.restore();
}

export function drawCaption(ctx, time, cues) {
  const cue = cues.find((item) => time >= item.start && time < item.end + 0.12);
  if (!cue) return;
  const fadeIn = segment(time, cue.start, cue.start + 0.12);
  const fadeOut = 1 - segment(time, cue.end + 0.02, cue.end + 0.12);
  const alpha = Math.min(fadeIn, fadeOut);

  ctx.save();
  ctx.globalAlpha *= alpha;
  roundedRect(ctx, 62, 1568, 956, 226, 28);
  ctx.fillStyle = '#14232DEB';
  ctx.fill();
  ctx.fillStyle = C.teal;
  ctx.fillRect(92, 1602, 58, 6);
  ctx.fillStyle = C.paper;
  ctx.font = '600 47px Manrope';
  const lines = wrapLines(ctx, cue.text, 872);
  ctx.strokeStyle = C.paper;
  ctx.lineWidth = 1.5;
  lines.slice(0, 3).forEach((line, index) => {
    ctx.strokeText(line, 92, 1650 + index * 56);
    ctx.fillText(line, 92, 1650 + index * 56);
  });
  ctx.restore();
}

