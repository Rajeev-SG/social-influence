import {
  C,
  W,
  clamp,
  drawBackground,
  drawCaption,
  drawDeskSurface,
  drawNoteCard,
  drawRevealLine,
  drawTopMeta,
  easeInOut,
  easeOut,
  mix,
  roundedRect,
  segment,
  trackedText,
} from './design.mjs';

const cardLabels = [
  ['SYSTEM', 'rules'],
  ['YOUR NOTE', 'new input'],
  ['EARLIER', 'messages'],
  ['TOOL', 'result'],
  ['OPEN', 'space'],
];

function titleBlock(ctx, lines, progress, top = 238) {
  lines.forEach((line, index) => {
    ctx.font = `700 ${line.size}px Manrope`;
    drawRevealLine(
      ctx,
      line.text,
      line.x ?? 80,
      top + index * 132,
      line.size,
      segment(progress, index * 0.13, 0.62 + index * 0.13),
      line.color ?? C.ink,
    );
  });
}

function drawHook(ctx, time, local) {
  drawTopMeta(ctx, 1, 'THE QUESTION', segment(local, 0, 0.7));
  titleBlock(ctx, [
    { text: 'WHAT IS A', size: 94 },
    { text: 'CONTEXT', size: 142, color: C.blue },
    { text: 'WINDOW?', size: 142 },
  ], segment(local, 0.08, 1.5), 286);

  const arrive = easeOut(segment(time, 0.65, 2.0));
  drawDeskSurface(ctx, { x: 74, y: 824, width: 932, height: 514, slots: 5, lift: mix(70, 0, arrive) });
  const labels = ['NOTE 1', 'NOTE 2', 'NOTE 3', 'NOTE 4', 'NOTE 5'];
  labels.forEach((label, index) => {
    const reveal = easeOut(segment(time, 0.8 + index * 0.13, 1.45 + index * 0.13));
    drawNoteCard(ctx, {
      x: 112 + index * 177,
      y: mix(680, 918, reveal),
      width: 150,
      height: 202,
      label,
      detail: index === 4 ? 'available' : 'context',
      accent: index === 4 ? C.teal : C.blue,
      alpha: reveal,
      rotation: mix(-0.08 + index * 0.025, -0.018 + index * 0.009, reveal),
      scale: mix(0.78, 1, reveal),
    });
  });

  ctx.fillStyle = C.muted;
  ctx.font = '600 25px Mono';
  trackedText(ctx, 'ONE FINITE WORKSPACE', 82, 1440, 3.6);
  ctx.fillStyle = C.ink;
  ctx.font = '650 43px Manrope';
  ctx.fillText('Five visible slots. A hard edge.', 82, 1496);
}

function drawDesk(ctx, time, local, cueStart) {
  drawTopMeta(ctx, 2, 'THE DESK ANALOGY', segment(local, 0, 0.7));
  titleBlock(ctx, [
    { text: 'THE MODEL’S', size: 92 },
    { text: 'DESK', size: 150, color: C.teal },
  ], segment(local, 0.08, 1.1), 276);

  const landing = easeOut(segment(time, cueStart - 0.34, cueStart + 1.1));
  drawDeskSurface(ctx, { x: 74, y: 742, width: 932, height: 572, slots: 5, lift: mix(64, 0, landing) });

  cardLabels.forEach(([label, detail], index) => {
    const reveal = easeOut(segment(time, cueStart - 0.24 + index * 0.11, cueStart + 0.55 + index * 0.11));
    const bob = Math.sin(time * 1.3 + index * 0.9) * 3.5 * reveal;
    drawNoteCard(ctx, {
      x: 112 + index * 177,
      y: 832 + bob,
      width: 150,
      height: 214,
      label,
      detail,
      accent: [C.coral, C.blue, C.blue, C.yellow, C.teal][index],
      alpha: reveal,
      rotation: mix(-0.12 + index * 0.03, -0.025 + index * 0.012, reveal),
      scale: mix(0.7, 1, reveal),
    });
  });

  const line = easeOut(segment(time, cueStart + 0.35, cueStart + 1.35));
  ctx.strokeStyle = `${C.blue}99`;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(126, 1420);
  ctx.lineTo(126 + 776 * line, 1420);
  ctx.stroke();
  ctx.fillStyle = C.ink;
  ctx.font = '650 40px Manrope';
  ctx.fillText('Everything it can consider in one go', 82, 1490);
}

function drawCapacity(ctx, time, cues) {
  const fillCue = cues[2];
  const trimCue = cues[3];
  drawTopMeta(ctx, 3, 'CAPACITY', segment(time, fillCue.start - 0.25, fillCue.start + 0.45));
  titleBlock(ctx, [
    { text: 'WHEN THE', size: 92 },
    { text: 'DESK FILLS', size: 134, color: C.coral },
  ], segment(time, fillCue.start - 0.22, fillCue.start + 1.12), 252);

  drawDeskSurface(ctx, { x: 74, y: 738, width: 932, height: 546, slots: 5 });
  cardLabels.forEach(([label, detail], index) => {
    const exit = index === 0 ? easeInOut(segment(time, trimCue.start + 0.38, trimCue.start + 1.18)) : 0;
    drawNoteCard(ctx, {
      x: 112 + index * 177 - exit * 320,
      y: 826 - exit * 55,
      width: 150,
      height: 214,
      label,
      detail,
      accent: [C.coral, C.blue, C.blue, C.yellow, C.teal][index],
      alpha: 1 - exit * 0.85,
      rotation: -0.025 + index * 0.012 - exit * 0.12,
    });
  });

  const incoming = easeOut(segment(time, fillCue.start + 0.25, fillCue.start + 1.28));
  drawNoteCard(ctx, {
    x: mix(790, 814, incoming),
    y: mix(532, 826, incoming),
    width: 150,
    height: 214,
    label: 'NEW NOTE',
    detail: 'next request',
    accent: C.coral,
    rotation: mix(0.13, 0.02, incoming),
    scale: mix(0.82, 1, incoming),
  });

  const sorting = easeOut(segment(time, trimCue.start + 0.1, trimCue.start + 0.9));
  ctx.save();
  ctx.globalAlpha *= sorting;
  ctx.fillStyle = C.ink;
  ctx.font = '700 26px Mono';
  trackedText(ctx, 'THE APP MAY', 82, 1380, 2.8);

  roundedRect(ctx, 82, 1410, 258, 78, 22);
  ctx.fillStyle = `${C.coral}18`;
  ctx.fill();
  ctx.strokeStyle = C.coral;
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillStyle = C.coral;
  ctx.font = '700 31px Manrope';
  ctx.fillText('TRIM', 177, 1459);

  roundedRect(ctx, 370, 1410, 326, 78, 22);
  ctx.fillStyle = `${C.teal}18`;
  ctx.fill();
  ctx.strokeStyle = C.teal;
  ctx.stroke();
  ctx.fillStyle = C.teal;
  ctx.fillText('SUMMARIZE', 428, 1459);

  ctx.fillStyle = C.muted;
  ctx.font = '500 21px Mono';
  ctx.fillText('OLDER NOTES', 742, 1436);
  ctx.fillText('FIT NEXT REQUEST', 742, 1472);
  ctx.restore();
}

function drawMeaning(ctx, time, cueStart) {
  drawTopMeta(ctx, 4, 'WHAT CONTEXT MEANS', segment(time, cueStart - 0.28, cueStart + 0.42));
  titleBlock(ctx, [
    { text: 'CONTEXT =', size: 102 },
    { text: 'RIGHT NOW', size: 136, color: C.blue },
  ], segment(time, cueStart - 0.25, cueStart + 1.0), 260);

  const focus = easeOut(segment(time, cueStart + 0.2, cueStart + 1.3));
  const beam = ctx.createLinearGradient(0, 555, 0, 1380);
  beam.addColorStop(0, `${C.yellow}00`);
  beam.addColorStop(0.3, `${C.yellow}2C`);
  beam.addColorStop(1, `${C.yellow}00`);
  ctx.fillStyle = beam;
  ctx.beginPath();
  ctx.moveTo(470, 500);
  ctx.lineTo(1015, 1355);
  ctx.lineTo(85, 1355);
  ctx.closePath();
  ctx.fill();

  drawDeskSurface(ctx, { x: 118, y: 786, width: 844, height: 510, slots: 5, lift: mix(24, 0, focus) });
  cardLabels.forEach(([label, detail], index) => {
    const pulse = 1 + Math.sin(time * 1.5 + index) * 0.012 * focus;
    drawNoteCard(ctx, {
      x: 153 + index * 160,
      y: 874,
      width: 138,
      height: 196,
      label,
      detail,
      accent: index === 4 ? C.teal : C.blue,
      alpha: 0.96,
      scale: pulse,
    });
  });

  ctx.fillStyle = C.ink;
  ctx.font = '650 38px Manrope';
  ctx.fillText('Available to the model now', 118, 1430);
  ctx.fillStyle = C.muted;
  ctx.font = '500 27px Mono';
  ctx.fillText('CONTEXT ≠ PERMANENT MEMORY', 118, 1484);

  ctx.save();
  ctx.globalAlpha *= 0.28 + 0.16 * Math.sin(time * 0.9);
  ctx.translate(858, 594);
  ctx.rotate(-0.09);
  for (let index = 0; index < 4; index += 1) {
    roundedRect(ctx, index * 8, -index * 12, 164, 92, 12);
    ctx.fillStyle = index === 0 ? C.dark : '#6D7476';
    ctx.fill();
  }
  ctx.restore();
}

function drawLimit(ctx, time, cueStart) {
  drawTopMeta(ctx, 5, 'THE LIMIT', segment(time, cueStart - 0.28, cueStart + 0.42));
  titleBlock(ctx, [
    { text: 'EVERY WINDOW', size: 92 },
    { text: 'HAS A LIMIT', size: 132, color: C.coral },
  ], segment(time, cueStart - 0.25, cueStart + 1.0), 266);

  const grow = easeInOut(segment(time, cueStart + 0.28, cueStart + 1.45));
  const width = mix(788, 918, grow);
  const x = mix(146, 81, grow);
  drawDeskSurface(ctx, { x, y: 774, width, height: 526, slots: 7 });
  const labels = ['NOTE', 'NOTE', 'NOTE', 'NOTE', 'NOTE', 'MORE', 'MORE'];
  labels.forEach((label, index) => {
    const reveal = index < 5 ? 1 : easeOut(segment(time, cueStart + 0.7 + (index - 5) * 0.18, cueStart + 1.25 + (index - 5) * 0.18));
    drawNoteCard(ctx, {
      x: x + 30 + index * ((width - 60) / 7) + 7,
      y: 858,
      width: (width - 60) / 7 - 14,
      height: 194,
      label,
      detail: index < 5 ? 'fits' : 'fits too',
      accent: index < 5 ? C.blue : C.teal,
      alpha: reveal,
      scale: mix(0.86, 1, reveal),
    });
  });

  const finite = easeOut(segment(time, cueStart + 1.25, cueStart + 2.05));
  ctx.save();
  ctx.translate(540, 1418);
  ctx.rotate(-0.025);
  ctx.globalAlpha *= finite;
  roundedRect(ctx, -315, -58, 630, 116, 28);
  ctx.fillStyle = `${C.coral}16`;
  ctx.fill();
  ctx.strokeStyle = C.coral;
  ctx.lineWidth = 4;
  ctx.stroke();
  ctx.fillStyle = C.coral;
  ctx.font = '700 50px Manrope';
  ctx.textAlign = 'center';
  ctx.fillText('BIGGER ≠ UNLIMITED', 0, 17);
  ctx.restore();
  ctx.textAlign = 'left';
}

export function createSceneFunction({ scene, clipStart, clipDuration, cues }) {
  const sceneIndex = ['hook', 'desk', 'capacity', 'meaning', 'limit'].indexOf(scene);
  return function sceneFunction({ canvas }) {
    return {
      onRender(progress) {
        const ctx = canvas.getContext('2d');
        const time = clipStart + progress * clipDuration;
        const local = progress * clipDuration;
        drawBackground(ctx, time, scene === 'capacity' ? C.coral : scene === 'meaning' ? C.yellow : C.blue);

        const sourceTime = progress * clipDuration;
        const outgoing = 1 - segment(sourceTime, clipDuration - 0.28, clipDuration - 0.18);
        const incoming = sceneIndex === 0 ? 1 : segment(sourceTime, 0.32, 0.40);
        const contentAlpha = Math.min(outgoing, incoming);

        ctx.save();
        ctx.globalAlpha = contentAlpha;
        if (scene === 'hook') drawHook(ctx, time, local);
        if (scene === 'desk') drawDesk(ctx, time, local, cues[1].start);
        if (scene === 'capacity') drawCapacity(ctx, time, cues);
        if (scene === 'meaning') drawMeaning(ctx, time, cues[4].start);
        if (scene === 'limit') drawLimit(ctx, time, cues[5].start);
        ctx.restore();

        drawCaption(ctx, time, cues);
      },
    };
  };
}

