import React from 'react';
import {
  Audio,
  CanvasElement,
  Fill,
  Sequence,
  interpolate,
  staticFile,
  useCompositionConfig,
  useFrame,
} from '@rendiv/core';
import {CaptionRenderer, createHighlightedCaptions} from '@rendiv/captions';
import {useLocalFont} from '@rendiv/fonts';
import {
  Backdrop,
  C,
  Connection,
  Kicker,
  Node,
  Rule,
  Svg,
  Title,
  WordChip,
  clamp,
  ease,
  lerp,
  smooth,
} from './design';
import timing from './timing.json';

const narrationUrl = staticFile('audio/narration.wav');
const soundscapeUrl = staticFile('audio/soundscape.wav');
const manropeUrl = staticFile('fonts/Manrope.ttf');
const monoUrl = staticFile('fonts/Mono.ttf');

const fps = 30;
export const durationInFrames = Math.ceil(timing.duration * fps);
const sceneNames = [...new Set(timing.cues.map((cue) => cue.scene))];
const sceneStarts = Object.fromEntries(
  sceneNames.map((name) => [name, Math.round(timing.cues.find((cue) => cue.scene === name)!.start * fps)]),
) as Record<string, number>;
const sceneLength = (name: string) => {
  const index = sceneNames.indexOf(name);
  const next = sceneNames[index + 1];
  return (next ? sceneStarts[next] : durationInFrames) - sceneStarts[name];
};

const captions = createHighlightedCaptions(
  timing.cues.map((cue) => ({
    text: cue.text,
    startMs: cue.start * 1000,
    endMs: cue.end * 1000,
    words: cue.words.map((word) => ({
      text: word.text,
      startMs: word.start * 1000,
      endMs: word.end * 1000,
    })),
  })),
  {maxWordsPerChunk: 4},
);

const Stage: React.FC<{
  name: string;
  children: React.ReactNode;
}> = ({name, children}) => {
  const frame = useFrame();
  const length = sceneLength(name);
  const reveal = ease(frame, 0, 15);
  const exit = 1 - ease(frame, length - 12, length);
  return (
    <Fill style={{opacity: exit, clipPath: `inset(0 ${(1 - reveal) * 100}% 0 0)`}}>
      <Backdrop />
      {children}
    </Fill>
  );
};

const Intro: React.FC = () => {
  const frame = useFrame();
  const length = sceneLength('intro');
  const reveal = ease(frame, 0, 32);
  const orbit = frame * 0.8;
  return (
    <Stage name="intro">
      <Kicker>ATTENTION / A BEGINNER'S MAP</Kicker>
      <Title top={270} size={116}>
        Which words
        <br />
        <span style={{color: C.teal}}>matter here?</span>
      </Title>
      <Svg>
        <g transform="translate(540 1110)">
          <circle r={345 + Math.sin(frame / 26) * 8} fill="none" stroke={C.line} strokeWidth="2" />
          <circle r={298} fill="none" stroke={C.teal} strokeOpacity="0.35" strokeWidth="2" strokeDasharray="4 18" strokeDashoffset={-frame * 1.4} />
          <circle r={250} fill="none" stroke={C.blue} strokeOpacity="0.26" strokeWidth="2" strokeDasharray="92 700" strokeDashoffset={-frame * 2.2} />
          <circle r={196 + reveal * 16} fill="url(#spot)" />
          <circle r={124 + Math.sin(frame / 18) * 4} fill="#122b32" stroke={C.teal} strokeWidth="3" />
          <text x="0" y="18" textAnchor="middle" fill={C.teal} fontFamily="Manrope" fontWeight="750" fontSize="74">bank</text>
          <text x="0" y="172" textAnchor="middle" fill={C.muted} fontFamily="Mono" fontSize="23" letterSpacing="4">THE TARGET WORD</text>
        </g>
        {[
          ['river', -220, -250, C.blue],
          ['water', 244, -198, C.teal],
          ['current', 286, 216, C.teal],
          ['money', -272, 222, C.amber],
          ['cash', -360, -22, C.amber],
          ['account', 362, 18, C.amber],
        ].map(([text, x, y, color], i) => {
          const angle = (i / 6) * Math.PI * 2 + orbit * 0.006;
          const px = 540 + (x as number) + Math.cos(angle) * 10;
          const py = 1110 + (y as number) + Math.sin(angle) * 10;
          return <WordChip key={text as string} text={text as string} x={px} y={py} color={color as string} active={i === 0 || i === 3} scale={lerp(0.82, 1, reveal)} opacity={reveal} small />;
        })}
      </Svg>
      <div style={{position: 'absolute', left: 88, right: 88, top: 1550, color: C.muted, fontFamily: 'Mono', fontSize: 25, letterSpacing: 2}}>
        words borrow meaning from their neighbours
      </div>
      <div style={{position: 'absolute', left: 88, right: 88, top: 1640, color: C.teal, fontFamily: 'Mono', fontSize: 22, letterSpacing: 3, opacity: ease(frame, length * 0.46, length * 0.7)}}>
        ONE TARGET WORD / MANY CONTEXT SIGNALS
      </div>
    </Stage>
  );
};

const Context: React.FC = () => {
  const frame = useFrame();
  const reveal = ease(frame, 0, 34);
  const sentence = ['the', 'river', 'bank', 'was', 'muddy'];
  return (
    <Stage name="context">
      <Kicker>01 / READ THE ROOM</Kicker>
      <Title top={254} size={102}>
        The words
        <br />
        <span style={{color: C.teal}}>around a word</span>
        <br />
        change its meaning.
      </Title>
      <Svg>
        <g opacity={reveal}>
          <rect x="82" y="720" width="916" height="126" rx="24" fill="#10232c" stroke={C.line} strokeWidth="2" />
          {sentence.map((word, i) => (
            <text key={word} x={145 + i * 180} y={800} fill={word === 'bank' ? C.teal : C.ink} fontFamily="Manrope" fontSize={word === 'bank' ? 58 : 48} fontWeight={word === 'bank' ? 750 : 550}>
              {word}
            </text>
          ))}
          <path d="M383 850 Q383 1010 540 1110" fill="none" stroke={C.teal} strokeOpacity="0.2" strokeWidth="24" filter="url(#glow)" />
          <path d="M383 850 Q383 1010 540 1110" fill="none" stroke={C.teal} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - reveal} />
          <path d="M575 850 Q575 1010 540 1110" fill="none" stroke={C.blue} strokeOpacity="0.22" strokeWidth="18" filter="url(#glow)" />
          <path d="M575 850 Q575 1010 540 1110" fill="none" stroke={C.blue} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - reveal} />
          <Node x={383} y={850} color={C.teal} label="river" />
          <Node x={575} y={850} color={C.blue} label="muddy" />
          <WordChip text="bank" x={540} y={1110} color={C.teal} active scale={lerp(0.85, 1, reveal)} />
          <text x="540" y="1302" textAnchor="middle" fill={C.muted} fontFamily="Mono" fontSize="25" letterSpacing="3">CONTEXT → CURRENT WORD</text>
        </g>
      </Svg>
    </Stage>
  );
};

const River: React.FC = () => {
  const frame = useFrame();
  const p = ease(frame, 0, 42);
  const pulse = 0.5 + Math.sin(frame / 12) * 0.12;
  return (
    <Stage name="river">
      <Kicker>02 / CLUES FROM “RIVER”</Kicker>
      <Title top={246} size={106}>
        <span style={{color: C.blue}}>River</span> points
        <br />
        to a river bank.
      </Title>
      <Svg>
        <path d="M80 920 Q285 700 540 1045 T1000 890" fill="none" stroke={C.blue} strokeOpacity="0.16" strokeWidth="70" filter="url(#glow)" />
        <path d="M80 920 Q285 700 540 1045 T1000 890" fill="none" stroke={C.blue} strokeOpacity="0.75" strokeWidth="3" strokeDasharray="10 16" strokeDashoffset={-frame * 2} />
        <Connection fromX={218} fromY={1080} toX={540} toY={1180} progress={p} weight={0.85} color={C.blue} label="water" labelX={338} labelY={1060} />
        <Connection fromX={280} fromY={1370} toX={540} toY={1180} progress={ease(frame, 8, 48)} weight={0.62} color={C.teal} label="current" labelX={360} labelY={1300} />
        <Connection fromX={812} fromY={1120} toX={540} toY={1180} progress={ease(frame, 15, 52)} weight={0.32} color={C.muted} label="mud" labelX={710} labelY={1088} />
        <WordChip text="river" x={218} y={1080} color={C.blue} active scale={lerp(0.8, 1, p)} />
        <WordChip text="water" x={278} y={1370} color={C.teal} active scale={lerp(0.8, 1, ease(frame, 8, 48))} />
        <WordChip text="mud" x={812} y={1120} color={C.muted} scale={lerp(0.8, 1, ease(frame, 15, 52))} />
        <g transform="translate(540 1180)">
          <circle r={142 + pulse * 7} fill="none" stroke={C.blue} strokeOpacity="0.35" strokeWidth="2" />
          <circle r={105} fill="#142d39" stroke={C.blue} strokeWidth="3" />
          <text y="16" textAnchor="middle" fill={C.ink} fontFamily="Manrope" fontWeight="750" fontSize="66">bank</text>
          <text y="172" textAnchor="middle" fill={C.blue} fontFamily="Mono" fontSize="22" letterSpacing="3">RIVER EDGE</text>
        </g>
        <text x="540" y="1578" textAnchor="middle" fill={C.muted} fontFamily="Manrope" fontSize="37">the nearby words agree</text>
      </Svg>
    </Stage>
  );
};

const Money: React.FC = () => {
  const frame = useFrame();
  const p = ease(frame, 0, 42);
  return (
    <Stage name="money">
      <Kicker>03 / CLUES FROM “MONEY”</Kicker>
      <Title top={246} size={106}>
        <span style={{color: C.amber}}>Money</span> points
        <br />
        to a financial bank.
      </Title>
      <Svg>
        <rect x="86" y="700" width="908" height="470" rx="44" fill="#161d27" stroke={C.amber} strokeOpacity="0.34" strokeWidth="2" />
        <path d="M220 1010 H860 M220 1080 H860 M220 1150 H860" stroke={C.amber} strokeOpacity="0.12" strokeWidth="2" />
        <Connection fromX={238} fromY={825} toX={540} toY={1015} progress={p} weight={0.78} color={C.amber} label="cash" labelX={350} labelY={850} />
        <Connection fromX={824} fromY={812} toX={540} toY={1015} progress={ease(frame, 9, 48)} weight={0.72} color={C.amber} label="account" labelX={712} labelY={836} />
        <Connection fromX={820} fromY={1308} toX={540} toY={1015} progress={ease(frame, 16, 54)} weight={0.34} color={C.rose} label="loan" labelX={716} labelY={1268} />
        <WordChip text="money" x={238} y={825} color={C.amber} active scale={lerp(0.8, 1, p)} />
        <WordChip text="cash" x={238} y={1088} color={C.amber} active scale={lerp(0.8, 1, ease(frame, 8, 48))} />
        <WordChip text="account" x={824} y={812} color={C.amber} active scale={lerp(0.8, 1, ease(frame, 9, 48))} />
        <WordChip text="loan" x={820} y={1308} color={C.rose} scale={lerp(0.8, 1, ease(frame, 16, 54))} />
        <g transform="translate(540 1015)">
          <circle r={138 + Math.sin(frame / 18) * 7} fill="none" stroke={C.amber} strokeOpacity="0.32" strokeWidth="2" />
          <rect x="-110" y="-82" width="220" height="164" rx="22" fill="#2a2520" stroke={C.amber} strokeWidth="3" />
          <text y="16" textAnchor="middle" fill={C.ink} fontFamily="Manrope" fontWeight="750" fontSize="66">bank</text>
          <text y="172" textAnchor="middle" fill={C.amber} fontFamily="Mono" fontSize="22" letterSpacing="3">MONEY INSTITUTION</text>
        </g>
        <text x="540" y="1578" textAnchor="middle" fill={C.muted} fontFamily="Manrope" fontSize="37">same target word, new neighbourhood</text>
      </Svg>
    </Stage>
  );
};

const Measure: React.FC = () => {
  const frame = useFrame();
  const p = ease(frame, 0, 38);
  const rows = [
    {word: 'river', value: 0.86, color: C.blue},
    {word: 'water', value: 0.72, color: C.teal},
    {word: 'cash', value: 0.34, color: C.amber},
    {word: 'loan', value: 0.16, color: C.rose},
  ];
  return (
    <Stage name="measure">
      <Kicker>04 / THE ATTENTION IDEA</Kicker>
      <Title top={248} size={112}>
        Attention
        <br />
        <span style={{color: C.teal}}>measures the pull.</span>
      </Title>
      <Svg>
        <text x="88" y="706" fill={C.muted} fontFamily="Mono" fontSize="25" letterSpacing="3">ILLUSTRATIVE INFLUENCE FOR “BANK”</text>
        {rows.map((row, i) => {
          const y = 830 + i * 142;
          const width = 680 * row.value * p;
          return (
            <g key={row.word}>
              <text x="88" y={y + 13} fill={C.ink} fontFamily="Manrope" fontWeight="650" fontSize="38">{row.word}</text>
              <rect x="310" y={y - 24} width="680" height="42" rx="21" fill="#17252c" />
              <rect x="310" y={y - 24} width={width} height="42" rx="21" fill={row.color} opacity="0.78" />
              <circle cx={310 + width} cy={y - 3} r={9 + Math.sin(frame / 12 + i) * 2} fill={row.color} />
              <text x="1018" y={y + 11} textAnchor="end" fill={row.color} fontFamily="Mono" fontSize="28">{Math.round(row.value * 100 * p)}%</text>
            </g>
          );
        })}
        <path d="M88 1432 H992" stroke={C.line} strokeWidth="2" />
        <text x="88" y="1502" fill={C.muted} fontFamily="Manrope" fontSize="33">more relevant clues → stronger influence</text>
        <text x="88" y="1552" fill={C.muted} fontFamily="Mono" fontSize="21" letterSpacing="2">A SIMPLE VISUAL, NOT A MODEL WEIGHT DUMP</text>
      </Svg>
    </Stage>
  );
};

const Ask: React.FC = () => {
  const frame = useFrame();
  const p = ease(frame, 0, 32);
  return (
    <Stage name="ask">
      <Kicker>05 / EVERY WORD DOES THIS</Kicker>
      <Title top={260} size={112} align="center">
        What matters
        <br />
        <span style={{color: C.teal}}>here?</span>
      </Title>
      <Svg>
        <g transform="translate(540 1110)">
          <circle r={350} fill="none" stroke={C.line} strokeWidth="2" />
          <circle r={282} fill="none" stroke={C.teal} strokeOpacity="0.42" strokeWidth="3" strokeDasharray="8 22" strokeDashoffset={-frame * 2.3} />
          <circle r={222} fill="none" stroke={C.blue} strokeOpacity="0.25" strokeWidth="2" />
          <circle r={132} fill="#132d33" stroke={C.teal} strokeWidth="3" />
          <text y="18" textAnchor="middle" fill={C.teal} fontFamily="Manrope" fontWeight="750" fontSize="64">bank</text>
          {['river', 'water', 'money', 'cash'].map((word, i) => {
            const angle = (i / 4) * Math.PI * 2 + frame * 0.018;
            const x = Math.cos(angle) * 350;
            const y = Math.sin(angle) * 350;
            return <WordChip key={word} text={word} x={540 + x} y={1110 + y} color={i < 2 ? C.blue : C.amber} active scale={lerp(0.8, 1, p)} small />;
          })}
          <path d="M-270 -210 Q-120 -330 0 -350 Q130 -330 270 -210" fill="none" stroke={C.teal} strokeOpacity="0.3" strokeWidth="2" />
          <text x="0" y="-392" textAnchor="middle" fill={C.muted} fontFamily="Mono" fontSize="22" letterSpacing="3">LOOK AROUND</text>
        </g>
      </Svg>
    </Stage>
  );
};

const Shape: React.FC = () => {
  const frame = useFrame();
  const p = ease(frame, 0, 36);
  return (
    <Stage name="shape">
      <Kicker>06 / CONTEXT SHAPES MEANING</Kicker>
      <Title top={252} size={112} align="center">
        The strongest clues
        <br />
        <span style={{color: C.teal}}>shape the meaning.</span>
      </Title>
      <Svg>
        <g transform="translate(540 1080)">
          <path d="M-420 -220 Q-140 -80 0 0 Q140 -80 420 -220" fill="none" stroke={C.blue} strokeOpacity="0.22" strokeWidth="28" filter="url(#glow)" />
          <path d="M-420 220 Q-140 80 0 0 Q140 80 420 220" fill="none" stroke={C.amber} strokeOpacity="0.22" strokeWidth="28" filter="url(#glow)" />
          <path d="M-420 -220 Q-140 -80 0 0" fill="none" stroke={C.blue} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />
          <path d="M-420 220 Q-140 80 0 0" fill="none" stroke={C.amber} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - p} />
          <path d="M0 0 Q150 -82 420 -220" fill="none" stroke={C.teal} strokeOpacity="0.32" strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - ease(frame, 16, 56)} />
          <path d="M0 0 Q150 82 420 220" fill="none" stroke={C.teal} strokeOpacity="0.32" strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - ease(frame, 16, 56)} />
          <Node x={-420} y={-220} color={C.blue} label="river" />
          <Node x={-420} y={220} color={C.amber} label="money" />
          <Node x={0} y={0} color={C.teal} label="bank" />
          <Node x={420} y={-220} color={C.blue} label="river edge" />
          <Node x={420} y={220} color={C.amber} label="financial" />
          <circle r={102} fill="#122c33" stroke={C.teal} strokeWidth="3" />
          <text y="16" textAnchor="middle" fill={C.ink} fontFamily="Manrope" fontWeight="750" fontSize="54">bank</text>
        </g>
        <text x="540" y="1510" textAnchor="middle" fill={C.ink} fontFamily="Manrope" fontWeight="650" fontSize="42">relationships become meaning</text>
        <text x="540" y="1572" textAnchor="middle" fill={C.muted} fontFamily="Mono" fontSize="22" letterSpacing="3">ATTENTION = CONTEXT-WEIGHTED RELATIONSHIPS</text>
      </Svg>
    </Stage>
  );
};

const End: React.FC = () => {
  const frame = useFrame();
  const p = ease(frame, 0, 30);
  return (
    <Stage name="end">
      <Kicker color={C.amber}>THE SHORT VERSION</Kicker>
      <div style={{position: 'absolute', left: 82, right: 82, top: 330, color: C.ink, fontFamily: 'Manrope', fontSize: 126, lineHeight: 0.98, letterSpacing: -5, fontWeight: 760, opacity: p, transform: `translateY(${(1 - p) * 32}px)`}}>
        Attention
        <br />
        <span style={{color: C.teal}}>chooses</span>
        <br />
        the meaning.
      </div>
      <Svg>
        <g transform="translate(540 1170)">
          <circle r={250 + Math.sin(frame / 22) * 8} fill="none" stroke={C.teal} strokeOpacity="0.28" strokeWidth="2" />
          <circle r={192} fill="none" stroke={C.amber} strokeOpacity="0.34" strokeWidth="3" strokeDasharray="30 22" strokeDashoffset={-frame * 1.8} />
          <circle r={128} fill="#172c30" stroke={C.teal} strokeWidth="3" />
          <text y="18" textAnchor="middle" fill={C.teal} fontFamily="Manrope" fontWeight="750" fontSize="62">context</text>
          <path d="M-355 0 H-150 M150 0 H355" stroke={C.line} strokeWidth="2" />
          <Node x={-390} y={0} color={C.blue} label="clues" />
          <Node x={390} y={0} color={C.amber} label="meaning" />
        </g>
        <text x="540" y="1588" textAnchor="middle" fill={C.muted} fontFamily="Mono" fontSize="24" letterSpacing="3">A WORD READS ITS NEIGHBOURS</text>
      </Svg>
    </Stage>
  );
};

const sceneComponents: Record<string, React.FC> = {
  intro: Intro,
  context: Context,
  river: River,
  money: Money,
  measure: Measure,
  ask: Ask,
  shape: Shape,
  end: End,
};

const Captions: React.FC = () => (
  <CaptionRenderer
    captions={captions}
    align="bottom"
    padding={92}
    style={{zIndex: 20, maxWidth: 900, margin: '0 auto'}}
    activeStyle={{
      color: C.ink,
      fontFamily: 'Manrope',
      fontSize: 43,
      fontWeight: 650,
      lineHeight: 1.25,
      textShadow: '0 3px 18px rgba(0,0,0,0.55)',
    }}
    highlightedWordStyle={{color: C.teal, fontWeight: 800}}
  />
);

export const AttentionFilm: React.FC = () => {
  useLocalFont({family: 'Manrope', src: manropeUrl, format: 'truetype', weight: '200 800'});
  useLocalFont({family: 'Mono', src: monoUrl, format: 'truetype', weight: '400'});
  return (
    <CanvasElement id="Attention">
      <Fill style={{backgroundColor: C.bg, color: C.ink, overflow: 'hidden'}}>
        {sceneNames.map((name) => {
          const Scene = sceneComponents[name];
          return (
            <Sequence key={name} name={`scene-${name}`} from={sceneStarts[name]} durationInFrames={sceneLength(name)}>
              <Scene />
            </Sequence>
          );
        })}
        <Captions />
        <Audio src={narrationUrl} volume={0.98} />
        <Audio src={soundscapeUrl} volume={0.34} />
      </Fill>
    </CanvasElement>
  );
};

