import React from 'react';
import {Easing, interpolate, useFrame} from '@rendiv/core';

export const C = {
  bg: '#0a1118',
  panel: '#12232d',
  panelSoft: '#18313a',
  ink: '#f4f0df',
  muted: '#9bb0b4',
  teal: '#72f0d2',
  blue: '#5b9dff',
  amber: '#ffbd6e',
  rose: '#f28c9d',
  line: '#2c4b56',
};

export const clamp = (value: number, min = 0, max = 1) =>
  Math.max(min, Math.min(max, value));

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const ease = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

export const smooth = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.ease),
  });

export const hash = (value: number) => {
  const x = Math.sin(value * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

export const Svg: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({
  children,
  style,
}) => (
  <svg
    width="1080"
    height="1920"
    viewBox="0 0 1080 1920"
    style={{position: 'absolute', inset: 0, overflow: 'visible', ...style}}
  >
    <defs>
      <radialGradient id="spot">
        <stop offset="0%" stopColor={C.teal} stopOpacity="0.20" />
        <stop offset="60%" stopColor={C.blue} stopOpacity="0.07" />
        <stop offset="100%" stopColor={C.bg} stopOpacity="0" />
      </radialGradient>
      <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor={C.teal} />
        <stop offset="100%" stopColor={C.blue} />
      </linearGradient>
      <filter id="soft">
        <feGaussianBlur stdDeviation="8" />
      </filter>
      <filter id="glow">
        <feGaussianBlur stdDeviation="18" />
      </filter>
    </defs>
    {children}
  </svg>
);

export const Backdrop: React.FC = () => {
  const frame = useFrame();
  const drift = Math.sin(frame / 90) * 18;
  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(circle at ${520 + drift}px 920px, #17343a 0, ${C.bg} 52%, #071016 100%)`}} />
      <Svg>
        <ellipse cx={540 + drift} cy={1030} rx={490} ry={720} fill="url(#spot)" />
        <g stroke={C.line} strokeWidth="1" opacity="0.30">
          {Array.from({length: 11}, (_, i) => (
            <path key={`v-${i}`} d={`M${i * 120 - 30} 150 Q540 ${280 + i * 8} ${i * 120 - 30} 1770`} fill="none" />
          ))}
          {Array.from({length: 8}, (_, i) => (
            <path key={`h-${i}`} d={`M60 ${230 + i * 190} Q540 ${180 + i * 190} 1020 ${230 + i * 190}`} fill="none" />
          ))}
        </g>
        <g fill={C.teal} opacity="0.28">
          {Array.from({length: 18}, (_, i) => {
            const x = 80 + hash(i * 3.2) * 920;
            const y = 170 + hash(i * 8.7) * 1550;
            const r = 1.5 + hash(i * 12.3) * 2.5;
            return <circle key={i} cx={x + Math.sin(frame / 48 + i) * 4} cy={y} r={r} />;
          })}
        </g>
      </Svg>
    </>
  );
};

export const Kicker: React.FC<{children: React.ReactNode; top?: number; color?: string}> = ({
  children,
  top = 126,
  color = C.teal,
}) => (
  <div style={{position: 'absolute', top, left: 84, right: 84, color, fontFamily: 'Mono', fontSize: 24, letterSpacing: 5, textTransform: 'uppercase'}}>
    {children}
  </div>
);

export const Title: React.FC<{children: React.ReactNode; top?: number; size?: number; align?: 'left' | 'center'}> = ({
  children,
  top = 224,
  size = 106,
  align = 'left',
}) => {
  const frame = useFrame();
  const reveal = ease(frame, 0, 20);
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: align === 'center' ? 74 : 84,
        right: align === 'center' ? 74 : 92,
        color: C.ink,
        fontFamily: 'Manrope',
        fontWeight: 700,
        fontSize: size,
        lineHeight: 1.02,
        letterSpacing: -3,
        textAlign: align,
        opacity: reveal,
        transform: `translateY(${(1 - reveal) * 32}px)`,
      }}
    >
      {children}
    </div>
  );
};

export const WordChip: React.FC<{
  text: string;
  x: number;
  y: number;
  active?: boolean;
  color?: string;
  scale?: number;
  opacity?: number;
  width?: number;
  small?: boolean;
}> = ({text, x, y, active = false, color = C.teal, scale = 1, opacity = 1, width, small = false}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      transform: `translate(-50%, -50%) scale(${scale})`,
      minWidth: width ?? (small ? 130 : 170),
      padding: small ? '16px 22px' : '21px 30px',
      borderRadius: 18,
      border: `2px solid ${active ? color : C.line}`,
      background: active ? `${color}1f` : '#12212acc',
      boxShadow: active ? `0 0 38px ${color}40` : 'none',
      color: active ? color : C.ink,
      fontFamily: 'Manrope',
      fontWeight: 700,
      fontSize: small ? 30 : 38,
      letterSpacing: -1,
      textAlign: 'center',
      opacity,
      whiteSpace: 'nowrap',
    }}
  >
    {text}
  </div>
);

export const Connection: React.FC<{
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  progress: number;
  weight: number;
  color?: string;
  label?: string;
  labelX?: number;
  labelY?: number;
}> = ({fromX, fromY, toX, toY, progress, weight, color = C.teal, label, labelX, labelY}) => {
  const bend = (fromX + toX) / 2;
  const d = `M${fromX} ${fromY} Q${bend} ${lerp(fromY, toY, 0.28)} ${toX} ${toY}`;
  return (
    <g opacity={clamp(progress * 1.25)}>
      <path d={d} fill="none" stroke={color} strokeOpacity={0.18 * weight} strokeWidth={22 * weight} filter="url(#glow)" />
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeOpacity={0.35 + weight * 0.55}
        strokeWidth={2 + weight * 8}
        strokeLinecap="round"
        pathLength={1}
        strokeDasharray="1"
        strokeDashoffset={1 - progress}
      />
      {label && (
        <text x={labelX ?? lerp(fromX, toX, 0.5)} y={labelY ?? lerp(fromY, toY, 0.5) - 14} textAnchor="middle" fill={color} fontFamily="Mono" fontSize="22" letterSpacing="1">
          {label}
        </text>
      )}
    </g>
  );
};

export const Node: React.FC<{x: number; y: number; color?: string; active?: boolean; label?: string}> = ({
  x,
  y,
  color = C.teal,
  active = true,
  label,
}) => (
  <g transform={`translate(${x} ${y})`}>
    <circle r={active ? 28 : 20} fill={active ? color : C.line} opacity={active ? 0.25 : 0.5} filter="url(#soft)" />
    <circle r={active ? 11 : 7} fill={active ? color : C.muted} />
    <circle cx="-3" cy="-3" r="3" fill={C.ink} opacity="0.8" />
    {label && <text x="22" y="8" fill={color} fontFamily="Mono" fontSize="22">{label}</text>}
  </g>
);

export const Rule: React.FC<{x: number; y: number; width: number; color?: string; progress?: number}> = ({
  x,
  y,
  width,
  color = C.teal,
  progress = 1,
}) => (
  <path d={`M${x} ${y} H${x + width * clamp(progress)}`} stroke={color} strokeWidth="3" opacity="0.7" />
);
