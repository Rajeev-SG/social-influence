import React from 'react';
import {
  AbsoluteFill,
  KineticTypography,
  useCurrentFrame,
  interpolate,
  spring,
  Easing,
} from 'motionforge';
import timeline from './timeline.json';

export const TOTAL_FRAMES = 735;

const C = {
  ink: '#07101f',
  deep: '#0b1830',
  navy: '#112443',
  cream: '#f7f2e8',
  mint: '#98f5d3',
  cyan: '#68d9ff',
  violet: '#ad93ff',
  coral: '#ff806c',
  yellow: '#ffd66e',
  muted: '#a9bad2',
};

const secondsToFrames = (seconds: number) => Math.round(seconds * 30);
const segment = (id: string) => timeline.segments.find((item) => item.id === id)!;
const segmentStart = (id: string) => secondsToFrames(segment(id).start);
const segmentEnd = (id: string) => secondsToFrames(segment(id).end);

const SCENES = {
  hook: [0, segmentStart('definition')],
  machine: [segmentStart('definition'), segmentStart('low')],
  low: [segmentStart('low'), segmentStart('high')],
  high: [segmentStart('high'), segmentStart('tradeoff')],
  compare: [segmentStart('tradeoff'), segmentStart('end')],
  end: [segmentStart('end'), TOTAL_FRAMES],
} as const;

function clamp(value: number, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function fadeAt(frame: number, start: number, length: number) {
  return interpolate(frame, [start, start + length], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
}

function ease(frame: number, start: number, end: number, from: number, to: number, easing = Easing.easeOutCubic) {
  return interpolate(frame, [start, end], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing,
  });
}

function Caption({ text, frame, segmentId, tone = C.cream }: { text: string; frame: number; segmentId: string; tone?: string }) {
  const start = segmentStart(segmentId);
  const end = segmentEnd(segmentId);
  const opacity = fadeAt(frame, start, 12) * (1 - fadeAt(frame, end - 4, 7));
  return (
    <div className="caption" style={{ opacity, color: tone }}>
      {text}
    </div>
  );
}

function Eyebrow({ children, color = C.mint }: { children: React.ReactNode; color?: string }) {
  return <div className="eyebrow" style={{ color }}>{children}</div>;
}

function Pill({ children, color, fill = 'rgba(255,255,255,0.06)' }: { children: React.ReactNode; color: string; fill?: string }) {
  return <div className="pill" style={{ color, borderColor: `${color}55`, background: fill }}>{children}</div>;
}

function ChoiceMachine({ frame, mode }: { frame: number; mode: 'low' | 'high' }) {
  const t = clamp((frame - (mode === 'low' ? segmentStart('low') : segmentStart('high'))) / 100);
  const selected = mode === 'low' ? 0 : 2;
  const branchY = [260, 390, 520, 650];
  const pathOpacity = mode === 'low' ? 1 : ease(frame, 348, 382, 0, 1);
  return (
    <div className="machine-wrap" style={{ opacity: fadeAt(frame, mode === 'low' ? segmentStart('low') + 6 : segmentStart('high') + 6, 16) }}>
      <div className="machine-label">NEXT WORD</div>
      <div className="machine-core">
        <div className="core-orbit orbit-one" />
        <div className="core-orbit orbit-two" />
        <div className="core-dot" />
        <div className="core-word">choose</div>
      </div>
      <svg className="branch-svg" viewBox="0 0 800 760" aria-hidden="true">
        <defs>
          <linearGradient id="lineLow" x1="0" x2="1">
            <stop offset="0" stopColor={C.cyan} stopOpacity="0.2" />
            <stop offset="1" stopColor={C.cyan} stopOpacity="1" />
          </linearGradient>
          <linearGradient id="lineHigh" x1="0" x2="1">
            <stop offset="0" stopColor={C.violet} stopOpacity="0.15" />
            <stop offset="1" stopColor={C.violet} stopOpacity="1" />
          </linearGradient>
        </defs>
        <path d={`M180 380 C300 380 330 ${branchY[selected]} 480 ${branchY[selected]}`} stroke="url(#lineLow)" strokeWidth="22" fill="none" strokeDasharray="12 12" opacity={mode === 'low' ? pathOpacity : 0.12} />
        {branchY.map((y, index) => (
          <path
            key={y}
            d={`M180 380 C300 380 320 ${y} 465 ${y}`}
            stroke={mode === 'high' ? 'url(#lineHigh)' : '#2a4168'}
            strokeWidth={mode === 'high' ? 13 : 8}
            fill="none"
            opacity={mode === 'high' ? pathOpacity * (index === selected ? 1 : 0.32) : 0.18}
          />
        ))}
        {branchY.map((y, index) => (
          <g key={`node-${y}`} opacity={mode === 'high' ? pathOpacity : 0.2}>
            <circle cx="500" cy={y} r={index === selected ? 25 : 16} fill={index === selected ? (mode === 'high' ? C.coral : C.cyan) : C.navy} stroke={index === selected ? C.cream : '#38547e'} strokeWidth="5" />
            <text x="550" y={y + 12} fill={index === selected ? C.cream : '#7890b2'} fontSize="30" fontWeight={index === selected ? 800 : 650}>
              {['clear', 'bright', 'strange', 'quiet'][index]}
            </text>
          </g>
        ))}
      </svg>
      {mode === 'low' && <div className="lock-badge"><span>✓</span> safest route locked</div>}
      <div className="machine-meter">
        <span>{mode === 'low' ? 'TEMP 0.2' : 'TEMP 1.2'}</span>
        <div className="meter-track"><div className="meter-fill" style={{ width: `${mode === 'low' ? 20 : 84}%`, background: mode === 'low' ? C.cyan : C.coral }} /></div>
      </div>
    </div>
  );
}

function BranchLegend({ mode }: { mode: 'low' | 'high' }) {
  return (
    <div className="legend-row">
      <Pill color={mode === 'low' ? C.cyan : C.violet}>{mode === 'low' ? 'one safe route' : 'more possible routes'}</Pill>
      <span className="legend-note">{mode === 'low' ? 'the model stays focused' : 'variety gets a chance'}</span>
    </div>
  );
}

export function TemperatureFilm() {
  const frame = useCurrentFrame();
  const inHook = frame < SCENES.hook[1];
  const inMachine = frame >= SCENES.machine[0] && frame < SCENES.machine[1];
  const inLow = frame >= SCENES.low[0] && frame < SCENES.low[1];
  const inHigh = frame >= SCENES.high[0] && frame < SCENES.high[1];
  const inCompare = frame >= SCENES.compare[0] && frame < SCENES.compare[1];
  const inEnd = frame >= SCENES.end[0];
  const drift = Math.sin(frame / 42) * 5;

  return (
    <AbsoluteFill className="film" style={{ background: `radial-gradient(circle at 72% 15%, #18325b 0%, ${C.ink} 42%, #050a14 100%)` }}>
      <div className="grain" />
      <div className="top-rule"><span>MOTIONFORGE / BEGINNER EXPLAINER</span><span>01 — 06</span></div>

      {inHook && (
        <AbsoluteFill className="scene hook-scene">
          <div className="hook-kicker" style={{ opacity: fadeAt(frame, 5, 16) }}>
            <span className="signal-dot" /> A QUICK FIELD GUIDE
          </div>
          <div className="hook-title" style={{ transform: `translateY(${ease(frame, 8, 36, 42, 0)}px)` }}>
            <KineticTypography text="TEMPERATURE" type="velocity" fontSize={112} stagger={1.6} durationInFrames={24} color={C.cream} />
          </div>
          <div className="hook-sub" style={{ opacity: fadeAt(frame, 26, 20), transform: `translateY(${ease(frame, 26, 52, 28, 0)}px)` }}>
            how wild should the next word be?
          </div>
          <div className="dial-orbit" style={{ transform: `rotate(${frame * 0.65}deg) translateY(${drift}px)` }}>
            <div className="dial-ring ring-a" /><div className="dial-ring ring-b" /><div className="dial-ring ring-c" />
            <div className="dial-center">T</div>
            <div className="dial-tick tick-1" /><div className="dial-tick tick-2" /><div className="dial-tick tick-3" />
          </div>
          <Caption text="Temperature is a dial for uncertainty." frame={frame} segmentId="hook" tone={C.mint} />
        </AbsoluteFill>
      )}

      {inMachine && (
        <AbsoluteFill className="scene machine-scene">
          <Eyebrow>THE SETUP</Eyebrow>
          <h1 className="scene-heading">AI chooses <em>one</em> next word.</h1>
          <p className="scene-copy">Temperature changes how surprising that choice is allowed to be.</p>
          <div className="machine-flow" style={{ transform: `translateY(${ease(frame, 105, 132, 22, 0)}px)` }}>
            <div className="flow-card"><span>context</span><strong>“The sky is …”</strong></div>
            <div className="flow-arrow">→</div>
            <div className="flow-card highlighted"><span>choice machine</span><strong>pick one</strong></div>
            <div className="flow-arrow">→</div>
            <div className="flow-card"><span>output</span><strong>“blue”</strong></div>
          </div>
          <div className="mini-explain" style={{ opacity: fadeAt(frame, 138, 18) }}>
            <div className="mini-line"><i /> one distribution of possible answers</div>
            <div className="mini-line"><i /> one answer leaves the machine</div>
          </div>
          <Caption text="It controls variety—not intelligence." frame={frame} segmentId="definition" tone={C.yellow} />
        </AbsoluteFill>
      )}

      {inLow && (
        <AbsoluteFill className="scene split-scene">
          <div className="scene-topline"><Eyebrow color={C.cyan}>LOW TEMPERATURE</Eyebrow><Pill color={C.cyan}>TEMP 0.2</Pill></div>
          <h1 className="scene-heading">Focused. Predictable.</h1>
          <p className="scene-copy">The safest option wins. The same route keeps winning.</p>
          <ChoiceMachine frame={frame} mode="low" />
          <BranchLegend mode="low" />
          <Caption text="Low temperature feels like a locked route." frame={frame} segmentId="low" tone={C.cyan} />
        </AbsoluteFill>
      )}

      {inHigh && (
        <AbsoluteFill className="scene split-scene high-scene">
          <div className="scene-topline"><Eyebrow color={C.coral}>HIGH TEMPERATURE</Eyebrow><Pill color={C.coral}>TEMP 1.2</Pill></div>
          <h1 className="scene-heading">Surprising. Varied.</h1>
          <p className="scene-copy">More routes get a chance. The model can choose beyond the obvious.</p>
          <ChoiceMachine frame={frame} mode="high" />
          <BranchLegend mode="high" />
          <div className="spark-field" style={{ opacity: fadeAt(frame, 388, 18) }}>
            {[0, 1, 2, 3, 4, 5].map((i) => <span key={i} style={{ '--i': i } as React.CSSProperties} />)}
          </div>
          <Caption text="High temperature opens more possible paths." frame={frame} segmentId="high" tone={C.coral} />
        </AbsoluteFill>
      )}

      {inCompare && (
        <AbsoluteFill className="scene compare-scene">
          <Eyebrow>THE TRADE-OFF</Eyebrow>
          <h1 className="scene-heading">Same dial.<br /><span className="accent-word">Different feel.</span></h1>
          <div className="compare-grid" style={{ transform: `translateY(${ease(frame, 500, 525, 20, 0)}px)` }}>
            <div className="compare-card low-card">
              <div className="compare-icon">↘</div><div className="compare-label">LOW</div><strong>focused</strong><span>predictable</span>
              <div className="compare-bar"><i style={{ width: '35%' }} /></div>
            </div>
            <div className="compare-divider">vs</div>
            <div className="compare-card high-card">
              <div className="compare-icon">↗</div><div className="compare-label">HIGH</div><strong>creative</strong><span>surprising</span>
              <div className="compare-bar"><i style={{ width: '82%', background: C.coral }} /></div>
            </div>
          </div>
          <div className="compare-foot">Temperature changes <b>variety</b>, not <b>intelligence</b>.</div>
          <Caption text="Low is focused. High is creative." frame={frame} segmentId="tradeoff" tone={C.yellow} />
        </AbsoluteFill>
      )}

      {inEnd && (
        <AbsoluteFill className="scene end-scene">
          <div className="end-mark" style={{ transform: `scale(${ease(frame, 592, 622, 0.82, 1, Easing.easeOutBack)}) rotate(${ease(frame, 592, 626, -8, 0)}deg)` }}>T</div>
          <h1 className="end-title">Temperature = <span>choice style.</span></h1>
          <p className="end-copy">Low keeps it clear.<br />High makes room for surprise.</p>
          <div className="end-rule" />
          <div className="end-credit">A beginner's guide to AI temperature</div>
          <Caption text="Now you know what the dial is doing." frame={frame} segmentId="end" tone={C.mint} />
        </AbsoluteFill>
      )}

      <div className="progress-rail"><div className="progress-fill" style={{ width: `${(frame / (TOTAL_FRAMES - 1)) * 100}%` }} /></div>
    </AbsoluteFill>
  );
}
