import {Node, Rect, Txt, Circle, Line} from '@motion-canvas/2d';
import {
  all,
  createRef,
  easeInCubic,
  easeInOutCubic,
  easeOutCubic,
  ThreadGenerator,
  waitFor,
} from '@motion-canvas/core';

export const C = {
  bg: '#0a0f14',
  panel: '#111c24',
  panel2: '#172630',
  ink: '#f3f0e8',
  muted: '#91a3ad',
  mint: '#75e4cd',
  blue: '#78a8ff',
  violet: '#b8a2ff',
  amber: '#f4bb74',
  line: '#2a3b45',
};

export const sceneFont = 'Manrope';
export const monoFont = 'IBM Plex Mono';

export const FontStyles = (): null => {
  if (typeof document === 'undefined' || document.getElementById('token-fonts')) return null;
  const style = document.createElement('style');
  style.id = 'token-fonts';
  style.textContent = `
    @font-face { font-family: 'Manrope'; src: url('/fonts/Manrope.ttf') format('truetype'); font-weight: 200 800; font-style: normal; }
    @font-face { font-family: 'IBM Plex Mono'; src: url('/fonts/IBM-Plex-Mono.ttf') format('truetype'); font-weight: 400; font-style: normal; }
  `;
  document.head.appendChild(style);
  return null;
};

FontStyles();

export function* reveal(input: Node | (() => Node), duration = 0.45, y = 22): ThreadGenerator {
  const node = typeof input === 'function' ? (input as () => Node)() : input;
  const baseY = node.position.y();
  node.position.y(baseY + y);
  node.scale(0.94);
  yield* all(
    node.opacity(1, duration, easeOutCubic),
    node.position.y(baseY, duration, easeOutCubic),
    node.scale(1, duration, easeOutCubic),
  );
}

export function* fadeOut(input: Node | (() => Node), duration = 0.3): ThreadGenerator {
  const node = typeof input === 'function' ? (input as () => Node)() : input;
  yield* node.opacity(0, duration, easeInCubic);
}

export function* stagger(nodes: Node[], gap = 0.12, duration = 0.42): ThreadGenerator {
  for (const node of nodes) {
    yield* reveal(node, duration, 26);
    yield* waitFor(gap);
  }
}

export const Label = ({x = 0, y = 0, text, color = C.muted, size = 26, mono = false}: {
  x?: number;
  y?: number;
  text: string;
  color?: string;
  size?: number;
  mono?: boolean;
}) => (
  <Txt
    x={x}
    y={y}
    width={Math.abs(x) < 80 ? 840 : 400}
    text={text}
    fontFamily={mono ? monoFont : sceneFont}
    fontSize={size}
    fontWeight={mono ? 400 : 650}
    fill={color}
    letterSpacing={mono ? 2 : 1}
    textAlign="center"
    textWrap={true}
    lineHeight={1.1}
  />
);

export const Rule = ({x = 0, y = 0, width = 300, color = C.mint}: {x?: number; y?: number; width?: number; color?: string}) => (
  <Rect x={x} y={y} width={width} height={4} radius={2} fill={color} />
);

export const TokenTile = ({x, y, text, id, active = false, width = 178}: {
  x: number;
  y: number;
  text: string;
  id?: string;
  active?: boolean;
  width?: number;
}) => (
  <Node x={x} y={y} opacity={0} scale={0.94}>
    <Rect
      width={width}
      height={id ? 132 : 108}
      radius={18}
      fill={active ? '#183b42' : C.panel}
      stroke={active ? C.mint : C.line}
      lineWidth={3}
    />
    <Txt
      x={0}
      y={id ? -17 : 1}
      text={text}
      fontFamily={sceneFont}
      fontSize={40}
      fontWeight={720}
      fill={active ? C.mint : C.ink}
      textAlign="center"
    />
    {id ? (
      <Txt
        x={0}
        y={39}
        text={`#${id}`}
        fontFamily={monoFont}
        fontSize={20}
        fill={active ? C.mint : C.muted}
        textAlign="center"
        letterSpacing={2}
      />
    ) : null}
  </Node>
);

export const Background = () => (
  <Node>
    <Rect width={1080} height={1920} fill={C.bg} />
    <Circle x={790} y={280} width={760} height={760} fill={C.blue} opacity={0.055} />
    <Circle x={180} y={1550} width={620} height={620} fill={C.mint} opacity={0.035} />
    {Array.from({length: 11}, (_, i) => (
      <Rect key={`v-${i}`} x={-520 + i * 112} y={0} width={2} height={1920} fill={C.line} opacity={0.16} />
    ))}
    {Array.from({length: 12}, (_, i) => (
      <Rect key={`h-${i}`} x={0} y={-850 + i * 160} width={1080} height={2} fill={C.line} opacity={0.12} />
    ))}
    <Rect x={70} y={80} width={940} height={1760} radius={28} stroke={C.line} lineWidth={2} opacity={0.42} />
  </Node>
);

export const Dot = ({x, y, r = 8, color = C.mint, opacity = 1}: {x: number; y: number; r?: number; color?: string; opacity?: number}) => (
  <Node x={x} y={y} opacity={opacity}>
    <Circle width={r * 4} height={r * 4} fill={color} opacity={0.16} />
    <Circle width={r * 2} height={r * 2} fill={color} />
  </Node>
);

export const FlowLine = ({points, color = C.line, width = 4, opacity = 1}: {points: any[]; color?: string; width?: number; opacity?: number}) => (
  <Line points={points} stroke={color} lineWidth={width} lineCap="round" opacity={opacity} />
);

export const ease = easeInOutCubic;
export const out = easeOutCubic;
export const inOut = easeInOutCubic;
export const ref = createRef;
