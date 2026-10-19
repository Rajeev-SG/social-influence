const path = require('node:path');
const {
  FFCreator,
  FFScene,
  FFImage,
  FFText,
  FFRect,
} = require('ffcreator');

const root = path.resolve(__dirname, '..');
const visual = (name) => path.join(root, 'assets', 'visuals', name);
const font = path.join(root, 'assets', 'fonts', 'Manrope.ttf');
const mono = path.join(root, 'assets', 'fonts', 'Mono.ttf');
const timing = require('./timing.json');

const COLORS = {
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
const FPS = timing.fps;
const TRANSITION = 0.28;

function animate(node, from, to, time, delay, ease = 'Quadratic.Out') {
  node.addAnimate({from, to, time, delay, ease});
}

function fade(node, delay, duration = 0.36, from = 0, to = 1) {
  animate(node, {alpha: from}, {alpha: to}, duration, delay, 'Quadratic.Out');
}

function fadeOut(node, delay, duration = 0.30) {
  animate(node, {alpha: 1}, {alpha: 0}, duration, delay, 'Quadratic.In');
}

function addImage(scene, file, x, y, width, height, options = {}) {
  const node = new FFImage({
    path: visual(file),
    x,
    y,
    width,
    height,
    scale: options.scale ?? 1,
    rotate: options.rotate ?? 0,
    opacity: options.opacity ?? 1,
  });
  if (options.anchor !== undefined) node.setAnchor(options.anchor);
  scene.addChild(node);
  return node;
}

function addText(scene, value, x, y, size, color, options = {}) {
  const node = new FFText({
    text: value,
    x,
    y,
    fontSize: size,
    color,
    font: options.font ?? font,
  });
  node.setStyle({
    fontFamily: options.font === mono ? 'Mono' : 'Manrope',
    fontWeight: options.weight ?? 700,
    align: options.align ?? 'left',
    wordWrap: Boolean(options.wrapWidth),
    wordWrapWidth: options.wrapWidth,
    lineHeight: options.lineHeight ?? Math.round(size * 1.15),
  });
  if (options.align === 'center') node.alignCenter();
  else node.setAnchor(0, 0);
  if (options.opacity !== undefined) node.setOpacity(options.opacity);
  scene.addChild(node);
  return node;
}

function addCaption(scene, value, delayIn, delayOut = null, width = 820) {
  const bg = addImage(scene, 'caption-bg.png', 540, 1712, 920, 180, {opacity: 0});
  const label = addText(scene, value, 540, 1730, 34, COLORS.ink, {
    align: 'center',
    wrapWidth: width,
    lineHeight: 43,
    weight: 650,
    opacity: 0,
  });
  fade(bg, delayIn, 0.24);
  fade(label, delayIn, 0.24);
  if (delayOut !== null) {
    fadeOut(bg, delayOut, 0.22);
    fadeOut(label, delayOut, 0.22);
  }
}

function addChapterLabel(scene, value, delay = 0) {
  const label = addText(scene, value, 82, 178, 23, COLORS.cyan, {
    font: mono,
    weight: 700,
    opacity: 0,
  });
  fade(label, delay, 0.28);
}

function addProgress(scene, progress) {
  const track = new FFRect({x: 82, y: 1842, width: 916, height: 4, color: COLORS.line});
  scene.addChild(track);
  const bar = new FFRect({x: 82, y: 1842, width: 916 * progress, height: 4, color: COLORS.cyan});
  scene.addChild(bar);
}

function addThroughLine(scene, activeIndex) {
  const stages = ['BASE', 'EXAMPLES', 'PRACTICE', 'SETTINGS', 'OUTCOME'];
  const xs = [122, 326, 535, 744, 948];
  const rail = new FFRect({x: 122, y: 88, width: 826, height: 3, color: COLORS.line});
  scene.addChild(rail);
  xs.forEach((x, index) => {
    const active = index === activeIndex;
    const reached = index <= activeIndex;
    const marker = new FFRect({
      x: x - 8,
      y: 81,
      width: 16,
      height: 16,
      color: active ? COLORS.coral : reached ? COLORS.cyan : COLORS.line,
    });
    scene.addChild(marker);
    addText(scene, stages[index], x, 126, 18, active ? COLORS.ink : COLORS.muted, {
      align: 'center',
      font: mono,
      weight: active ? 800 : 650,
    });
  });
}

function addBackground(scene) {
  addImage(scene, 'background.png', 540, 960, 1080, 1920);
}

function buildBase(scene, chapter, cues) {
  addBackground(scene);
  addThroughLine(scene, 0);
  addChapterLabel(scene, 'FINE-TUNING / 01', 0);
  const title = addText(scene, 'Start broad.', 82, 322, 108, COLORS.ink, {weight: 760, opacity: 0});
  const title2 = addText(scene, 'Then specialize.', 82, 438, 102, COLORS.cyan, {weight: 760, opacity: 0});
  fade(title, 0.15, 0.36);
  fade(title2, 0.38, 0.36);

  const core = addImage(scene, 'core.png', 540, 1030, 680, 680, {opacity: 0, scale: 0.88});
  fade(core, 0.25, 0.42);
  animate(core, {scale: 0.88, rotation: -0.05}, {scale: 1, rotation: 0.02}, 2.4, 0.25, 'Quadratic.InOut');

  const chips = [
    ['chip-language.png', 160, 730, -0.12],
    ['chip-code.png', 920, 730, 0.10],
    ['chip-reasoning.png', 140, 1310, 0.10],
    ['chip-style.png', 940, 1310, -0.10],
  ];
  chips.forEach(([file, x, y, rotate], index) => {
    const chip = addImage(scene, file, x, y, 300, 92, {opacity: 0, rotate});
    fade(chip, 0.45 + index * 0.10, 0.30);
    animate(chip, {x: x + (x < 540 ? -42 : 42), y: y + 16}, {x, y}, 0.42, 0.45 + index * 0.10);
  });
  addCaption(scene, cues[0].caption, cues[0].start - chapter.start, null);
  addProgress(scene, 0.18);
}

function buildCourse(scene, chapter, cues) {
  addBackground(scene);
  addThroughLine(scene, 1);
  addChapterLabel(scene, 'FINE-TUNING / 02', 0);
  const title = addText(scene, 'A focused course.', 82, 320, 102, COLORS.ink, {weight: 760, opacity: 0});
  const sub = addText(scene, 'Examples + feedback.', 82, 430, 49, COLORS.cyan, {weight: 700, opacity: 0});
  fade(title, 0.15, 0.34);
  fade(sub, 0.38, 0.34);

  const cards = [
    ['course-card-1.png', 210, 870, -0.08, 0.36],
    ['course-card-2.png', 540, 835, 0, 0.48],
    ['course-card-3.png', 870, 870, 0.08, 0.60],
  ];
  cards.forEach(([file, x, y, rotate, delay], index) => {
    const card = addImage(scene, file, x, y, 320, 380, {opacity: 0, rotate});
    fade(card, delay, 0.36);
    animate(card, {y: y + 90, rotation: rotate * 1.8}, {y, rotation: rotate}, 0.52, delay, 'Quadratic.Out');
  });

  const arrow1 = addImage(scene, 'outcome-arrow.png', 370, 1120, 150, 58, {opacity: 0, rotate: 0});
  const arrow2 = addImage(scene, 'outcome-arrow.png', 710, 1120, 150, 58, {opacity: 0, rotate: 0});
  fade(arrow1, 0.88, 0.20);
  fade(arrow2, 1.00, 0.20);

  const check = addImage(scene, 'feedback-check.png', 400, 1320, 140, 140, {opacity: 0});
  const edit = addImage(scene, 'feedback-edit.png', 680, 1320, 140, 140, {opacity: 0});
  fade(check, 1.22, 0.28);
  fade(edit, 1.42, 0.28);
  const label = addText(scene, 'CURATED EXAMPLES', 210, 1485, 24, COLORS.muted, {font: mono, weight: 700, opacity: 0});
  const label2 = addText(scene, 'COACH FEEDBACK', 680, 1485, 24, COLORS.muted, {font: mono, weight: 700, opacity: 0});
  fade(label, 1.58, 0.24);
  fade(label2, 1.72, 0.24);

  addCaption(scene, cues[0].caption, cues[0].start - chapter.start, cues[1].start - chapter.start - 0.12);
  addCaption(scene, cues[1].caption, cues[1].start - chapter.start, null);
  addProgress(scene, 0.42);
}

function buildAnalogy(scene, chapter, cues) {
  addBackground(scene);
  addThroughLine(scene, 2);
  addChapterLabel(scene, 'SPECIALIST TRAINING / 03', 0);
  const title = addText(scene, 'A chef already knows cooking.', 82, 312, 78, COLORS.ink, {wrapWidth: 900, lineHeight: 88, weight: 750, opacity: 0});
  const title2 = addText(scene, 'A bakery adds a focused shift.', 82, 510, 60, COLORS.coral, {wrapWidth: 900, lineHeight: 72, weight: 720, opacity: 0});
  fade(title, 0.18, 0.38);
  fade(title2, 1.72, 0.32);

  const chef = addImage(scene, 'chef.png', 295, 1070, 390, 510, {opacity: 0, scale: 0.92});
  const pastry = addImage(scene, 'pastry.png', 775, 1010, 450, 297, {opacity: 0, scale: 0.88});
  const recipe = addImage(scene, 'recipe-card.png', 540, 1330, 330, 347, {opacity: 0, scale: 0.92});
  fade(chef, 0.20, 0.36);
  animate(chef, {scale: 0.92, y: 1130}, {scale: 1, y: 1070}, 0.52, 0.20);
  fade(pastry, 0.72, 0.36);
  animate(pastry, {scale: 0.88, x: 835}, {scale: 1, x: 775}, 0.52, 0.72);
  fade(recipe, 1.08, 0.32);
  animate(recipe, {scale: 0.92, y: 1385}, {scale: 1, y: 1330}, 0.48, 1.08);

  const link = addImage(scene, 'outcome-arrow.png', 535, 1040, 220, 84, {opacity: 0});
  fade(link, 0.92, 0.22);
  const note = addText(scene, 'guided examples + coaching', 540, 1572, 29, COLORS.amber, {align: 'center', weight: 700, opacity: 0});
  fade(note, 1.86, 0.28);

  addCaption(scene, cues[0].caption, cues[0].start - chapter.start, cues[1].start - chapter.start - 0.12);
  addCaption(scene, cues[1].caption, cues[1].start - chapter.start, null);
  addProgress(scene, 0.68);
}

function buildSettings(scene, chapter, cues) {
  addBackground(scene);
  addThroughLine(scene, 3);
  addChapterLabel(scene, 'INTERNAL SETTINGS / 04', 0);
  const title = addText(scene, 'Adjust selected settings.', 82, 320, 80, COLORS.ink, {wrapWidth: 900, lineHeight: 92, weight: 760, opacity: 0});
  const sub = addText(scene, 'The foundation stays.', 82, 505, 54, COLORS.cyan, {weight: 720, opacity: 0});
  fade(title, 0.16, 0.38);
  fade(sub, 0.54, 0.34);

  const before = addText(scene, 'BASE SETTINGS', 170, 705, 21, COLORS.muted, {font: mono, weight: 700, opacity: 0});
  const after = addText(scene, 'AFTER FOCUSED TRAINING', 810, 705, 21, COLORS.cyan, {align: 'center', font: mono, weight: 700, opacity: 0});
  fade(before, 0.10, 0.24);
  fade(after, 0.72, 0.24);
  const base = addImage(scene, 'dials-base.png', 540, 945, 820, 520, {opacity: 0});
  fade(base, 0.10, 0.26);
  const tuned = addImage(scene, 'dials-tuned.png', 540, 945, 820, 520, {opacity: 0});
  fade(tuned, 0.72, 0.40);
  animate(tuned, {scale: 0.98}, {scale: 1.015}, 1.6, 0.72, 'Quadratic.InOut');

  const foundation = new FFRect({x: 180, y: 1315, width: 720, height: 122, color: COLORS.panel});
  scene.addChild(foundation);
  const foundationLabel = addText(scene, 'FOUNDATION STAYS', 540, 1392, 32, COLORS.ink, {align: 'center', font: mono, weight: 700, opacity: 0});
  fade(foundationLabel, 1.12, 0.28);
  const bead = new FFRect({x: 180, y: 1315, width: 720, height: 6, color: COLORS.coral});
  scene.addChild(bead);
  animate(bead, {x: 180, width: 80}, {x: 820, width: 80}, 1.65, 0.76, 'Quadratic.InOut');

  addCaption(scene, cues[0].caption, cues[0].start - chapter.start, null);
  addProgress(scene, 0.86);
}

function buildSpecialist(scene, chapter, cues) {
  addBackground(scene);
  addThroughLine(scene, 4);
  addChapterLabel(scene, 'RESULT / 05', 0);
  const title = addText(scene, 'Same base. Better fit.', 82, 322, 91, COLORS.ink, {wrapWidth: 910, lineHeight: 102, weight: 760, opacity: 0});
  const sub = addText(scene, 'Fine-tuning is focused adaptation.', 82, 520, 42, COLORS.cyan, {wrapWidth: 900, weight: 700, opacity: 0});
  fade(title, 0.18, 0.38);
  fade(sub, 0.52, 0.32);

  const base = addImage(scene, 'base-model.png', 285, 1035, 360, 425, {opacity: 0, scale: 0.92});
  const arrow = addImage(scene, 'outcome-arrow.png', 540, 1015, 220, 84, {opacity: 0});
  const specialist = addImage(scene, 'specialist-model.png', 795, 1035, 360, 425, {opacity: 0, scale: 0.92});
  fade(base, 0.18, 0.32);
  animate(base, {x: 235, scale: 0.92}, {x: 285, scale: 1}, 0.48, 0.18);
  fade(arrow, 0.58, 0.20);
  fade(specialist, 0.70, 0.34);
  animate(specialist, {x: 845, scale: 0.92}, {x: 795, scale: 1}, 0.48, 0.70);

  const general = addText(scene, 'GENERALIST', 285, 1325, 24, COLORS.muted, {align: 'center', font: mono, weight: 700, opacity: 0});
  const focused = addText(scene, 'SPECIALIST', 795, 1325, 24, COLORS.coral, {align: 'center', font: mono, weight: 700, opacity: 0});
  fade(general, 0.88, 0.22);
  fade(focused, 1.02, 0.22);
  const end = addText(scene, 'NOT STARTING OVER', 540, 1515, 35, COLORS.amber, {align: 'center', font: mono, weight: 700, opacity: 0});
  fade(end, 1.62, 0.28);
  addCaption(scene, cues[0].caption, cues[0].start - chapter.start, null);
  addProgress(scene, 1);
}

function buildFilm() {
  const creator = new FFCreator({
    cacheDir: path.join(root, '.render', 'cache'),
    outputDir: path.join(root, 'deliverables'),
    width: timing.width,
    height: timing.height,
    fps: FPS,
    crf: 17,
    preset: 'slow',
    render: 'canvas',
    antialias: true,
    parallel: 3,
    highWaterMark: '4mb',
    audio: {
      path: path.join(root, 'assets', 'audio', 'mix.wav'),
      bg: true,
      loop: false,
      volume: 1,
      start: 0,
    },
    ffmpeglog: false,
  });

  const starts = [
    0,
    timing.cues.find((c) => c.id === 'course').start,
    timing.cues.find((c) => c.id === 'analogy').start,
    timing.cues.find((c) => c.id === 'settings').start,
    timing.cues.find((c) => c.id === 'specialist').start,
    timing.duration,
  ];
  const chapters = [
    {name: 'base', build: buildBase, cueIds: ['base']},
    {name: 'course', build: buildCourse, cueIds: ['course', 'examples']},
    {name: 'analogy', build: buildAnalogy, cueIds: ['analogy', 'adapt']},
    {name: 'settings', build: buildSettings, cueIds: ['settings']},
    {name: 'specialist', build: buildSpecialist, cueIds: ['specialist']},
  ];

  chapters.forEach((chapter, index) => {
    const start = starts[index];
    const end = starts[index + 1];
    const scene = new FFScene();
    scene.setBgColor(COLORS.navy);
    scene.setDuration(end - start + (index < chapters.length - 1 ? TRANSITION : 0));
    if (index < chapters.length - 1) scene.setTransition('fade', TRANSITION);
    else scene.setTransition('fade', 0);
    chapter.build(scene, {start, end}, chapter.cueIds.map((id) => timing.cues.find((c) => c.id === id)));
    creator.addChild(scene);
  });

  return creator;
}

module.exports = {buildFilm, COLORS, TRANSITION};
