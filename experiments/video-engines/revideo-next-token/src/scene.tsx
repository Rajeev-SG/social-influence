/** @jsxImportSource @revideo/2d/lib */
import {
  Circle,
  Line,
  Node,
  Rect,
  Txt,
  makeScene2D,
} from '@revideo/2d';
import {
  all,
  delay,
  easeInOutCubic,
  easeOutBack,
  easeOutCubic,
  linear,
  tween,
  waitFor,
} from '@revideo/core';
import timing from './timing.json' with {type: 'json'};
import {CAPTION_LINES, CANDIDATES, SENTENCE} from './data.js';
import {C, F} from './theme.js';

const cue = (id: string) => timing.cues.find(item => item.id === id)!;

function label(text: string, x: number, y: number, fill = C.muted, size = 28) {
  return new Txt({
    text,
    x,
    y,
    fill,
    fontFamily: F.mono,
    fontSize: size,
    fontWeight: 650,
    letterSpacing: 2.2,
    textAlign: 'left',
    offset: [-1, 0],
  });
}

function pill(text: string, x: number, y: number, width: number, active = false) {
  const root = new Node({x, y});
  root.add(
    new Rect({
      width,
      height: 88,
      radius: 18,
      fill: active ? '#173B43' : C.panel2,
      stroke: active ? C.cyan : C.line,
      lineWidth: active ? 3 : 2,
      shadowColor: active ? C.cyan : '#00000066',
      shadowBlur: active ? 26 : 18,
      shadowOffset: [0, 9],
    }),
  );
  root.add(
    new Txt({
      text,
      y: 2,
      fill: active ? C.cyan : C.ink,
      fontFamily: F.display,
      fontSize: 43,
      fontWeight: 650,
    }),
  );
  return root;
}

function captionNode(id: string) {
  const text = new Txt({
    text: CAPTION_LINES[id],
    y: 725,
    width: 900,
    fill: C.ink,
    fontFamily: F.display,
    fontSize: 39,
    fontWeight: 520,
    lineHeight: 54,
    textAlign: 'center',
    opacity: 0,
    shadowColor: '#000000AA',
    shadowBlur: 12,
    shadowOffset: [0, 3],
  });
  return text;
}

function makeArrowArc(radius: number) {
  const points = [];
  for (let i = 0; i <= 26; i += 1) {
    const angle = -2.42 + (i / 26) * 4.84;
    points.push([Math.cos(angle) * radius, Math.sin(angle) * radius] as [number, number]);
  }
  return new Line({
    points,
    stroke: C.cyan,
    lineWidth: 8,
    lineCap: 'round',
    endArrow: true,
    arrowSize: 22,
    shadowColor: C.cyan,
    shadowBlur: 18,
  });
}

export default makeScene2D('next-token', function* (view) {
  view.fill(C.bg);

  const stage = new Node({});
  const overlay = new Node({});
  view.add(stage);
  view.add(overlay);

  // Cinematic depth layers: a fixed grid, soft light pools, and slow stage drift.
  stage.add(new Rect({width: 1080, height: 1920, fill: C.bg}));
  for (let i = 0; i < 8; i += 1) {
    stage.add(
      new Line({
        points: [
          [-540 + i * 154, -960],
          [-540 + i * 154, 960],
        ],
        stroke: C.line,
        lineWidth: 1,
        opacity: 0.18,
      }),
    );
  }
  for (let i = 0; i < 11; i += 1) {
    stage.add(
      new Line({
        points: [
          [-540, -820 + i * 164],
          [540, -820 + i * 164],
        ],
        stroke: C.line,
        lineWidth: 1,
        opacity: 0.12,
      }),
    );
  }
  stage.add(new Circle({x: -250, y: -300, size: 760, fill: '#1A5360', opacity: 0.11}));
  stage.add(new Circle({x: 360, y: 340, size: 680, fill: '#285A93', opacity: 0.10}));
  stage.add(new Circle({x: 0, y: 0, size: 850, stroke: C.line, lineWidth: 2, opacity: 0.18}));
  stage.add(new Circle({x: 0, y: 0, size: 1120, stroke: C.line, lineWidth: 2, opacity: 0.12}));

  // Opening hook.
  const hook = new Node({});
  stage.add(hook);
  const orbit = new Circle({
    y: 215,
    size: 520,
    stroke: C.cyan,
    lineWidth: 3,
    opacity: 0,
    shadowColor: C.cyan,
    shadowBlur: 22,
  });
  const orbit2 = new Circle({
    y: 215,
    size: 390,
    stroke: C.blue,
    lineWidth: 2,
    opacity: 0,
    rotation: 18,
  });
  hook.add([orbit, orbit2]);
  hook.add(label('THE NEXT PIECE / A VISUAL PRIMER', -430, -690, C.cyan, 26));
  const hookNext = new Txt({
    text: 'NEXT',
    y: -385,
    fill: C.ink,
    fontFamily: F.display,
    fontSize: 158,
    fontWeight: 800,
    letterSpacing: -7,
    opacity: 0,
  });
  const hookToken = new Txt({
    text: 'TOKEN',
    y: -215,
    fill: C.cyan,
    fontFamily: F.display,
    fontSize: 158,
    fontWeight: 800,
    letterSpacing: -7,
    opacity: 0,
  });
  const hookMark = new Txt({
    text: '?',
    y: 205,
    fill: C.cyan,
    fontFamily: F.display,
    fontSize: 236,
    fontWeight: 700,
    opacity: 0,
    shadowColor: C.cyan,
    shadowBlur: 32,
  });
  const hookSub = new Txt({
    text: 'a model chooses one piece at a time',
    y: 475,
    fill: C.muted,
    fontFamily: F.display,
    fontSize: 38,
    fontWeight: 500,
    opacity: 0,
  });
  hook.add([hookNext, hookToken, hookMark, hookSub]);

  // Persistent sentence tape.
  const tape = new Node({y: -525, opacity: 0});
  stage.add(tape);
  tape.add(
    new Rect({
      width: 950,
      height: 220,
      radius: 32,
      fill: C.panel,
      stroke: C.line,
      lineWidth: 2,
      shadowColor: '#00000088',
      shadowBlur: 28,
      shadowOffset: [0, 14],
    }),
  );
  tape.add(label('CONTEXT / PIECES SO FAR', -425, -70, C.cyan, 24));
  const tapeTokens: Node[] = [];
  const xs = [-340, -210, -80, 58, 198];
  SENTENCE.forEach((word, index) => {
    const token = pill(word, xs[index], 35, index === 1 ? 112 : 106, index === 1);
    token.opacity(0);
    token.y(token.y() + 26);
    tape.add(token);
    tapeTokens.push(token);
  });
  const gap = new Node({x: 342, y: 35});
  gap.add(
    new Rect({
      width: 132,
      height: 88,
      radius: 18,
      fill: '#0A1B22',
      stroke: C.cyan,
      lineWidth: 3,
      shadowColor: C.cyan,
      shadowBlur: 18,
    }),
  );
  gap.add(new Txt({text: '?', fill: C.cyan, fontFamily: F.display, fontSize: 55, fontWeight: 700}));
  tape.add(gap);
  const tapeMat = pill('mat', 342, 35, 132, true);
  tapeMat.opacity(0);
  tape.add(tapeMat);
  const nextCursor = new Txt({
    text: '|',
    x: 446,
    y: 34,
    fill: C.cyan,
    fontFamily: F.mono,
    fontSize: 54,
    fontWeight: 700,
    opacity: 0,
    shadowColor: C.cyan,
    shadowBlur: 18,
  });
  tape.add(nextCursor);

  // Context reading: a scan crosses the known pieces and their signals converge.
  const scanBeam = new Rect({
    x: -365,
    y: 35,
    width: 8,
    height: 90,
    radius: 4,
    fill: C.cyan,
    opacity: 0,
    shadowColor: C.cyan,
    shadowBlur: 22,
  });
  tape.add(scanBeam);
  const contextGroup = new Node({y: 125, opacity: 0});
  contextGroup.add(label('READ → CONTEXT STATE', -315, -115, C.cyan, 25));
  const contextPanel = new Rect({
    x: 55,
    y: 45,
    width: 440,
    height: 120,
    radius: 28,
    fill: '#102A33',
    stroke: C.cyan,
    lineWidth: 2,
    shadowColor: C.cyan,
    shadowBlur: 22,
  });
  contextGroup.add(contextPanel);
  const contextCount = new Txt({
    text: '0 / 5 PIECES READ',
    x: 55,
    y: 45,
    fill: C.ink,
    fontFamily: F.mono,
    fontSize: 31,
    fontWeight: 700,
    letterSpacing: 1.5,
    textAlign: 'center',
  });
  contextGroup.add(contextCount);
  const contextSignals: Circle[] = [];
  for (let i = 0; i < 5; i += 1) {
    const x = [-340, -210, -80, 58, 198][i];
    contextGroup.add(
      new Line({
        points: [
          [x, -375],
          [x * 0.45 + 25, -155],
          [55, -15],
        ],
        stroke: i === 1 ? C.cyan : C.blue,
        lineWidth: i === 1 ? 3 : 2,
        opacity: 0.32,
      }),
    );
    const signal = new Circle({
      x,
      y: -375,
      size: i === 1 ? 18 : 13,
      fill: i === 1 ? C.cyan : C.blue,
      opacity: 0,
      shadowColor: i === 1 ? C.cyan : C.blue,
      shadowBlur: 16,
    });
    contextGroup.add(signal);
    contextSignals.push(signal);
  }
  stage.add(contextGroup);

  // Scoring and weighted-ballot rows.
  const scoreGroup = new Node({opacity: 0});
  stage.add(scoreGroup);
  scoreGroup.add(label('NEXT-PIECE SCORES / ILLUSTRATIVE', -430, -235, C.muted, 25));
  const scoreTitle = new Txt({
    text: 'What fits next?',
    x: -430,
    y: -145,
    fill: C.ink,
    fontFamily: F.display,
    fontSize: 88,
    fontWeight: 730,
    letterSpacing: -3,
    textAlign: 'left',
    offset: [-1, 0],
  });
  scoreGroup.add(scoreTitle);
  const rowNodes: {
    root: Node;
    fill: Rect;
    pct: Txt;
    dots: Circle[];
    word: string;
    value: number;
  }[] = [];
  CANDIDATES.forEach((candidate, index) => {
    const y = -15 + index * 138;
    const root = new Node({y, opacity: 0});
    root.add(
      new Rect({
        x: 30,
        width: 880,
        height: 112,
        radius: 22,
        fill: index === 0 ? '#123038' : '#0D2028',
        stroke: index === 0 ? C.cyan : C.line,
        lineWidth: index === 0 ? 2.5 : 1.5,
      }),
    );
    root.add(
      new Txt({
        text: candidate.word,
        x: -330,
        fill: index === 0 ? C.cyan : C.ink,
        fontFamily: F.mono,
        fontSize: 39,
        fontWeight: 700,
        letterSpacing: 0.01,
      }),
    );
    root.add(new Rect({x: 20, width: 330, height: 26, radius: 13, fill: '#203640'}));
    const fill = new Rect({
      x: 20,
      width: 0,
      height: 26,
      radius: 13,
      fill: candidate.color,
      shadowColor: candidate.color,
      shadowBlur: 18,
    });
    root.add(fill);
    const pct = new Txt({
      text: '0%',
      x: 385,
      fill: index === 0 ? C.cyan : C.muted,
      fontFamily: F.mono,
      fontSize: 34,
      fontWeight: 650,
    });
    root.add(pct);
    const dots: Circle[] = [];
    for (let j = 0; j < 8; j += 1) {
      const dot = new Circle({
        x: -195 + (j % 4) * 28,
        y: -23 + Math.floor(j / 4) * 46,
        size: j < Math.round(candidate.value / 8) ? 15 : 9,
        fill: candidate.color,
        opacity: 0,
        shadowColor: candidate.color,
        shadowBlur: 10,
      });
      root.add(dot);
      dots.push(dot);
    }
    scoreGroup.add(root);
    rowNodes.push({root, fill, pct, dots, word: candidate.word, value: candidate.value});
  });
  scoreGroup.add(label('VOTES → PROBABILITY', -430, 575, C.cyan, 25));

  // Selection layer: one ticket travels into the tape.
  const selectRing = new Circle({
    x: -185,
    y: -15,
    size: 150,
    stroke: C.cyan,
    lineWidth: 5,
    opacity: 0,
    shadowColor: C.cyan,
    shadowBlur: 30,
  });
  const matTicket = new Node({x: -185, y: -15, opacity: 0});
  matTicket.add(
    new Rect({
      width: 138,
      height: 86,
      radius: 18,
      fill: '#173B43',
      stroke: C.cyan,
      lineWidth: 3,
      shadowColor: C.cyan,
      shadowBlur: 28,
      shadowOffset: [0, 10],
    }),
  );
  matTicket.add(new Txt({text: 'mat', fill: C.cyan, fontFamily: F.display, fontSize: 42, fontWeight: 700}));

  // Predict-place-repeat loop.
  const loopGroup = new Node({y: 120, opacity: 0});
  const loopArc = makeArrowArc(255);
  loopGroup.add(loopArc);
  loopGroup.add(new Circle({size: 380, stroke: C.line, lineWidth: 2, opacity: 0.7}));
  loopGroup.add(new Circle({size: 245, fill: '#0D222A', stroke: C.cyan, lineWidth: 2}));
  loopGroup.add(label('READ', -72, -68, C.muted, 24));
  loopGroup.add(label('SCORE', -82, 2, C.cyan, 27));
  loopGroup.add(label('PLACE', -72, 72, C.muted, 24));
  loopGroup.add(
    new Txt({
      text: 'PREDICT  →  PLACE  →  REPEAT',
      y: 360,
      fill: C.cyan,
      fontFamily: F.mono,
      fontSize: 31,
      fontWeight: 700,
      letterSpacing: 2,
    }),
  );
  stage.add(loopGroup);

  // Final distinction.
  const truthGroup = new Node({y: 305, opacity: 0});
  truthGroup.add(
    new Rect({
      width: 865,
      height: 365,
      radius: 34,
      fill: '#2A2118',
      stroke: C.amber,
      lineWidth: 3,
      shadowColor: '#00000088',
      shadowBlur: 32,
      shadowOffset: [0, 16],
    }),
  );
  truthGroup.add(label('A PROBABILITY IS NOT A FACT CHECK', -375, -118, C.amber, 24));
  truthGroup.add(
    new Txt({
      text: 'Likely wording',
      x: -375,
      y: -18,
      fill: C.ink,
      fontFamily: F.display,
      fontSize: 73,
      fontWeight: 720,
      textAlign: 'left',
      offset: [-1, 0],
    }),
  );
  truthGroup.add(
    new Txt({
      text: 'is not guaranteed truth.',
      x: -375,
      y: 78,
      fill: C.amber,
      fontFamily: F.display,
      fontSize: 67,
      fontWeight: 720,
      textAlign: 'left',
      offset: [-1, 0],
    }),
  );
  truthGroup.add(
    new Txt({
      text: 'CHECK IMPORTANT CLAIMS.',
      x: -375,
      y: 151,
      fill: C.muted,
      fontFamily: F.mono,
      fontSize: 24,
      fontWeight: 650,
      letterSpacing: 2,
      textAlign: 'left',
      offset: [-1, 0],
    }),
  );
  stage.add(truthGroup);

  const captions = Object.fromEntries(timing.cues.map(item => [item.id, captionNode(item.id)]));
  Object.values(captions).forEach(node => overlay.add(node));

  // Slow camera drift, deliberately independent from the screen-space captions.
  const camera = tween(timing.total, value => {
    stage.scale(0.985 + value * 0.035);
    stage.rotation(Math.sin(value * Math.PI * 1.2) * 0.32);
    stage.position([Math.sin(value * Math.PI * 1.7) * 7, Math.cos(value * Math.PI * 1.15) * 8]);
  });

  const repeatDot = new Circle({
    x: -250,
    y: 120,
    size: 24,
    fill: C.cyan,
    opacity: 0,
    shadowColor: C.cyan,
    shadowBlur: 18,
  });
  overlay.add(repeatDot);

  function* hookBranch() {
    yield* waitFor(cue('p1').start);
    yield* all(
      hookNext.opacity(1, 0.42),
      hookNext.y(-350, 0.55, easeOutCubic),
      hookToken.opacity(1, 0.42),
      hookToken.y(-195, 0.55, easeOutCubic),
      hookMark.opacity(1, 0.5),
      hookMark.scale(1, 0.65, easeOutBack),
      hookSub.opacity(1, 0.55),
      orbit.opacity(0.7, 0.7),
      orbit2.opacity(0.35, 0.7),
      orbit.rotation(42, 1.8, linear),
      orbit2.rotation(-32, 1.8, linear),
    );
    yield* waitFor(1.28);
    yield* all(
      hook.opacity(0, 0.42),
      hook.y(-70, 0.42, easeInOutCubic),
      tape.opacity(1, 0.5),
      tape.y(-525, 0.72, easeInOutCubic),
    );
  }

  function* contextBranch() {
    yield* waitFor(cue('p2').start - 0.18);
    yield* all(
      tape.opacity(1, 0.22),
      ...tapeTokens.map((token, index) =>
        delay(
          index * 0.18,
          all(token.opacity(1, 0.28), token.y(35, 0.38, easeOutBack), token.scale(1, 0.38, easeOutBack)),
        ),
      ),
      gap.opacity(1, 0.35),
      contextGroup.opacity(1, 0.42),
      scanBeam.opacity(1, 0.18),
      scanBeam.x(390, 1.65, easeInOutCubic),
      tween(1.35, value => {
        contextCount.text(`${Math.min(5, Math.floor(value * 5.999))} / 5 PIECES READ`);
      }),
      ...contextSignals.map((signal, index) =>
        delay(
          index * 0.18,
          all(
            signal.opacity(1, 0.16),
            tween(0.82, value => {
              const eased = easeInOutCubic(value);
              const startX = [-340, -210, -80, 58, 198][index];
              signal.position([
                (1 - eased) * startX + eased * 55,
                (1 - eased) * -375 + eased * -15,
              ]);
            }),
            signal.opacity(0, 0.18),
          ),
        ),
      ),
    );
  }

  function* scoreBranch() {
    yield* waitFor(cue('p3').start - 0.12);
    yield* all(
      scoreGroup.opacity(1, 0.35),
      contextGroup.opacity(0.18, 0.38),
      contextGroup.y(55, 0.48, easeInOutCubic),
      scanBeam.opacity(0, 0.25),
      scoreTitle.x(-430, 0.55, easeOutCubic),
      ...rowNodes.map((row, index) =>
        delay(index * 0.12, all(row.root.opacity(1, 0.32), row.root.x(0, 0.45, easeOutCubic))),
      ),
    );
  }

  function* ballotBranch() {
    yield* waitFor(cue('p4').start - 0.12);
    yield* all(
      ...rowNodes.flatMap((row, index) =>
        row.dots.map((dot, dotIndex) =>
          delay(
            index * 0.11 + dotIndex * 0.055,
            all(
              dot.opacity(dotIndex < Math.ceil(row.value / 8) ? 1 : 0.25, 0.18),
              dot.x(80 + dotIndex * 22, 0.82, easeInOutCubic),
            ),
          ),
        ),
      ),
      ...rowNodes.map((row, index) =>
        delay(
          index * 0.12,
          all(
            row.fill.width((row.value / 62) * 330, 1.15, easeOutCubic),
            tween(1.15, value => {
              row.pct.text(`${Math.round(row.value * value)}%`);
            }),
          ),
        ),
      ),
    );
  }

  function* selectBranch() {
    yield* waitFor(cue('p5').start);
    yield* all(
      selectRing.opacity(1, 0.28),
      selectRing.scale(1.25, 0.38, easeOutBack),
      matTicket.opacity(1, 0.22),
      matTicket.scale(1.12, 0.34, easeOutBack),
    );
    yield* all(
      tween(0.82, value => {
        const eased = easeInOutCubic(value);
        const start = [-185, -15] as const;
        const control = [35, -360] as const;
        const end = [342, -490] as const;
        const x = (1 - eased) ** 2 * start[0] + 2 * (1 - eased) * eased * control[0] + eased ** 2 * end[0];
        const y = (1 - eased) ** 2 * start[1] + 2 * (1 - eased) * eased * control[1] + eased ** 2 * end[1];
        matTicket.position([x, y]);
      }),
      matTicket.scale(0.92, 0.82, easeInOutCubic),
    );
    yield* all(
      matTicket.opacity(0, 0.12),
      gap.opacity(0, 0.12),
      tapeMat.opacity(1, 0.22),
      tapeMat.scale(1.08, 0.22, easeOutBack).to(1, 0.18),
      selectRing.opacity(0, 0.28),
    );
  }

  function* repeatBranch() {
    yield* waitFor(cue('p6').start);
    yield* all(
      scoreGroup.opacity(0, 0.38),
      scoreGroup.y(-45, 0.42, easeInOutCubic),
      loopGroup.opacity(1, 0.45),
      loopGroup.scale(1, 0.55, easeOutBack),
      loopArc.end(1, 0.75, easeOutCubic),
      loopGroup.rotation(12, 1.55, linear),
      nextCursor.opacity(1, 0.22),
      tween(1.45, value => {
        nextCursor.opacity(Math.sin(value * Math.PI * 7) > -0.15 ? 1 : 0.2);
      }),
    );
    yield* all(
      repeatDot.opacity(1, 0.18),
      tween(0.95, value => {
        const angle = -2.42 + easeInOutCubic(value) * 4.84;
        repeatDot.position([Math.cos(angle) * 255, 120 + Math.sin(angle) * 255]);
      }),
    );
  }

  function* truthBranch() {
    yield* waitFor(cue('p7').start - 0.18);
    yield* all(
      loopGroup.opacity(0.18, 0.45),
      loopGroup.y(-30, 0.52, easeInOutCubic),
      truthGroup.opacity(1, 0.55),
      truthGroup.y(265, 0.72, easeOutCubic),
      repeatDot.opacity(0, 0.3),
    );
  }

  function* captionsBranch(item: (typeof timing.cues)[number]) {
    const node = captions[item.id];
    yield* waitFor(item.start);
    yield* node.opacity(1, 0.18);
    yield* waitFor(Math.max(0.1, item.dur - 0.18));
    yield* node.opacity(0, 0.18);
  }

  yield* all(
    camera,
    hookBranch(),
    contextBranch(),
    scoreBranch(),
    ballotBranch(),
    selectBranch(),
    repeatBranch(),
    truthBranch(),
    ...timing.cues.map(item => captionsBranch(item)),
    waitFor(timing.total),
  );
});
