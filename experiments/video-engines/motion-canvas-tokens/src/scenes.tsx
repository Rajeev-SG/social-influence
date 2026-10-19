import {Circle, Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, easeOutCubic, waitFor} from '@motion-canvas/core';
import {
  Background,
  C,
  Dot,
  FlowLine,
  Label,
  Rule,
  TokenTile,
  fadeOut,
  monoFont,
  reveal,
  sceneFont,
  stagger,
} from './design';

const xPositions = [-375, -188, -2, 184, 368];
const tokenText = ['Cats', ' chase', ' tiny', ' robots', '.'];
const exampleIds = ['3812', '4821', '904', '271', '13'];

const PhaseLabel = ({text, x, y, color = C.mint}: {text: string; x: number; y: number; color?: string}) => (
  <Node x={x} y={y} opacity={0}>
    <Rect x={-10} y={-22} width={310} height={44} radius={22} fill={C.panel} stroke={C.line} lineWidth={2} />
    <Txt x={0} y={0} text={text} fontFamily={monoFont} fontSize={20} fill={color} textAlign="center" letterSpacing={2} />
  </Node>
);

export default makeScene2D(function* (view) {
  const world = createRef<Node>();
  const title = createRef<Node>();
  const subtitle = createRef<Node>();
  const ribbon = createRef<Node>();
  const gate = createRef<Node>();
  const hookCaption = createRef<Node>();
  const splitTitle = createRef<Node>();
  const splitCaption = createRef<Node>();
  const tiles = Array.from({length: 5}, () => createRef<Node>());
  const examplePanel = createRef<Node>();
  const exampleTitle = createRef<Node>();
  const exampleCaption = createRef<Node>();
  const idPanel = createRef<Node>();
  const idTitle = createRef<Node>();
  const idCaption = createRef<Node>();
  const idTiles = Array.from({length: 5}, () => createRef<Node>());
  const idBars = Array.from({length: 5}, () => createRef<Rect>());
  const caveat = createRef<Node>();
  const caveatTitle = createRef<Node>();
  const caveatCaption = createRef<Node>();
  const bridge = createRef<Node>();
  const bridgeCaption = createRef<Node>();
  const bridgeLine = createRef<Rect>();
  const bridgeDots = Array.from({length: 6}, () => createRef<Node>());
  const end = createRef<Node>();

  view.add(
    <Node ref={world}>
      <Background />

      <Node ref={title} y={-625} opacity={0}>
        <Label x={0} y={0} text="WHAT ARE TOKENS?" color={C.ink} size={76} />
        <Rule x={0} y={62} width={300} color={C.mint} />
        <Label x={0} y={112} text="the bridge from words to numbers" color={C.muted} size={25} mono />
      </Node>

      <Node ref={ribbon} x={-26} y={-210} opacity={0}>
        <Rect x={0} y={0} width={780} height={118} radius={59} fill={C.panel} stroke={C.mint} lineWidth={3} />
        <Rect x={-370} y={0} width={14} height={118} radius={7} fill={C.mint} />
        <Txt x={-10} y={-7} text="Cats chase tiny robots." fontFamily={sceneFont} fontSize={54} fontWeight={720} fill={C.ink} textAlign="center" />
        <Txt x={-10} y={35} text="YOUR TEXT RIBBON" fontFamily={monoFont} fontSize={18} fill={C.muted} textAlign="center" letterSpacing={3} />
      </Node>

      <Node ref={gate} y={22} opacity={0}>
        <Rect x={0} y={0} width={230} height={340} radius={36} fill={C.panel2} stroke={C.blue} lineWidth={3} />
        <Rect x={0} y={-82} width={144} height={18} radius={9} fill={C.blue} opacity={0.8} />
        <Rect x={0} y={-36} width={144} height={18} radius={9} fill={C.mint} opacity={0.8} />
        <Rect x={0} y={10} width={144} height={18} radius={9} fill={C.violet} opacity={0.8} />
        <Txt x={0} y={115} text="TOKENIZER" fontFamily={monoFont} fontSize={22} fill={C.ink} textAlign="center" letterSpacing={2} />
        <Label x={0} y={158} text="cuts, then maps" color={C.muted} size={19} mono />
      </Node>

      <Node ref={hookCaption} y={715} opacity={0}>
        <Rect x={0} y={0} width={820} height={110} radius={22} fill={C.panel} opacity={0.94} />
        <Txt x={0} y={0} width={760} text={'Imagine your sentence as a ribbon\nentering a sorting machine.'} fontFamily={sceneFont} fontSize={34} fontWeight={650} fill={C.ink} textAlign="center" textWrap={true} lineHeight={1.16} />
      </Node>

      <Node ref={splitTitle} y={-615} opacity={0}>
        <Label x={0} y={0} text="CUT INTO TOKENS" color={C.ink} size={70} />
        <Label x={0} y={58} text="one possible split · reusable pieces" color={C.muted} size={24} mono />
      </Node>

      <Node y={-195} opacity={1}>
        <FlowLine points={[[-455, 0], [455, 0]]} color={C.line} width={3} opacity={0.8} />
        <Dot x={-455} y={0} r={7} color={C.blue} />
        <Dot x={455} y={0} r={7} color={C.mint} />
      </Node>

      {tokenText.map((text, i) => (
        <Node key={`token-${i}`} ref={tiles[i]}>
          <TokenTile x={xPositions[i]} y={-42} text={text} active={i === 0} width={i === 4 ? 112 : 178} />
        </Node>
      ))}

      <Node ref={splitCaption} y={250} opacity={0}>
        <Label x={0} y={0} text="whole word · word fragment · punctuation" color={C.muted} size={25} mono />
        <Rect x={0} y={48} width={690} height={3} fill={C.mint} opacity={0.7} />
      </Node>

      <Node ref={examplePanel} y={70} opacity={0}>
        <Rect x={0} y={0} width={860} height={610} radius={34} fill={C.panel} stroke={C.line} lineWidth={2} />
        <Rect x={-202} y={-188} width={392} height={82} radius={20} fill={C.panel2} stroke={C.mint} lineWidth={2} />
        <Txt x={-202} y={-188} text="playground" fontFamily={sceneFont} fontSize={46} fontWeight={720} fill={C.ink} textAlign="center" />
        <FlowLine points={[[-202, -118], [-202, -56]]} color={C.mint} width={4} />
        <Dot x={-202} y={-36} r={8} color={C.mint} />
        <TokenTile x={-328} y={82} text="play" active width={190} />
        <TokenTile x={-62} y={82} text="ground" active width={210} />

        <Rect x={230} y={-188} width={270} height={82} radius={20} fill={C.panel2} stroke={C.blue} lineWidth={2} />
        <Txt x={230} y={-188} text="hello!" fontFamily={sceneFont} fontSize={46} fontWeight={720} fill={C.ink} textAlign="center" />
        <FlowLine points={[[230, -118], [230, -56]]} color={C.blue} width={4} />
        <Dot x={230} y={-36} r={8} color={C.blue} />
        <TokenTile x={148} y={82} text="hello" width={190} />
        <TokenTile x={342} y={82} text="!" width={112} />

        <Label x={0} y={226} text="different tokenizers may draw the lines differently" color={C.muted} size={24} mono />
      </Node>

      <Node ref={exampleTitle} y={-615} opacity={0}>
        <Label x={0} y={-18} text="A WORD ISN'T ALWAYS" color={C.ink} size={52} />
        <Label x={0} y={38} text="ONE TOKEN" color={C.ink} size={52} />
        <Label x={0} y={92} text="illustrative split, not a universal rule" color={C.muted} size={21} mono />
      </Node>
      <Node ref={exampleCaption} y={720} opacity={0}>
        <Rect x={0} y={0} width={830} height={100} radius={20} fill={C.panel} opacity={0.94} />
        <Txt x={0} y={0} width={780} text="The pieces are small enough to reuse." fontFamily={sceneFont} fontSize={36} fontWeight={650} fill={C.ink} textAlign="center" textWrap={true} />
      </Node>

      <Node ref={idPanel} y={70} opacity={0}>
        <Rect x={0} y={0} width={890} height={640} radius={34} fill={C.panel} stroke={C.line} lineWidth={2} />
        <Label x={0} y={-248} text="EACH PIECE GETS AN ID" color={C.ink} size={48} />
        <Label x={0} y={-202} text="example numbers for this visual" color={C.muted} size={22} mono />
        {exampleIds.map((id, i) => (
          <Node key={`id-${i}`} ref={idTiles[i]}>
            <TokenTile x={xPositions[i]} y={-28} text={tokenText[i]} id={id} active={i === 0} width={i === 4 ? 112 : 168} />
          </Node>
        ))}
        {exampleIds.map((_, i) => (
          <Rect key={`bar-${i}`} ref={idBars[i]} x={xPositions[i]} y={190} width={82} height={0} radius={10} fill={i === 0 ? C.mint : C.blue} opacity={0.75} />
        ))}
        <FlowLine points={[[-430, 112], [430, 112]]} color={C.line} width={3} />
        <Label x={0} y={298} text="numbers the model can use" color={C.mint} size={28} mono />
      </Node>

      <Node ref={idTitle} y={-615} opacity={0}>
        <Label x={0} y={0} text="TOKENS BECOME IDS" color={C.ink} size={68} />
        <Label x={0} y={58} text="text pieces → machine-readable numbers" color={C.muted} size={23} mono />
      </Node>
      <Node ref={idCaption} y={720} opacity={0}>
        <Rect x={0} y={0} width={820} height={100} radius={20} fill={C.panel} opacity={0.94} />
        <Txt x={0} y={0} width={780} text="That mapping is the handoff to the model." fontFamily={sceneFont} fontSize={34} fontWeight={650} fill={C.ink} textAlign="center" textWrap={true} />
      </Node>

      <Node ref={caveat} y={62} opacity={0}>
        <Rect x={0} y={0} width={880} height={620} radius={34} fill={C.panel} stroke={C.line} lineWidth={2} />
        <Label x={0} y={-226} text="BOUNDARY LINES CAN MOVE" color={C.ink} size={46} />
        <Label x={0} y={-180} text="same word · different tokenizer · different split" color={C.muted} size={21} mono />

        <Rect x={0} y={-82} width={520} height={82} radius={20} fill={C.panel2} stroke={C.line} lineWidth={2} />
        <Txt x={0} y={-82} text="playground" fontFamily={sceneFont} fontSize={48} fontWeight={720} fill={C.ink} textAlign="center" />

        <Rect x={-206} y={72} width={180} height={82} radius={18} fill={'#183b42'} stroke={C.mint} lineWidth={2} />
        <Txt x={-206} y={72} text="play" fontFamily={sceneFont} fontSize={38} fontWeight={720} fill={C.mint} textAlign="center" />
        <Rect x={38} y={72} width={210} height={82} radius={18} fill={'#183b42'} stroke={C.mint} lineWidth={2} />
        <Txt x={38} y={72} text="ground" fontFamily={sceneFont} fontSize={38} fontWeight={720} fill={C.mint} textAlign="center" />
        <Label x={-40} y={185} text="TOKENIZER A" color={C.mint} size={19} mono />

        <Rect x={-226} y={280} width={220} height={82} radius={18} fill={'#17263a'} stroke={C.blue} lineWidth={2} />
        <Txt x={-226} y={280} text="playg" fontFamily={sceneFont} fontSize={38} fontWeight={720} fill={C.blue} textAlign="center" />
        <Rect x={52} y={280} width={190} height={82} radius={18} fill={'#17263a'} stroke={C.blue} lineWidth={2} />
        <Txt x={52} y={280} text="round" fontFamily={sceneFont} fontSize={38} fontWeight={720} fill={C.blue} textAlign="center" />
        <Label x={-40} y={382} text="TOKENIZER B · ILLUSTRATIVE" color={C.blue} size={19} mono />
      </Node>

      <Node ref={caveatTitle} y={-615} opacity={0}>
        <Label x={0} y={-18} text="TOKENS ARE MODEL" color={C.ink} size={52} />
        <Label x={0} y={38} text="CONVENTIONS" color={C.ink} size={52} />
        <Label x={0} y={92} text="the vocabulary defines the cut" color={C.muted} size={21} mono />
      </Node>
      <Node ref={caveatCaption} y={720} opacity={0}>
        <Rect x={0} y={0} width={850} height={100} radius={20} fill={C.panel} opacity={0.94} />
        <Txt x={0} y={0} width={790} text="Different tokenizers can draw the lines differently." fontFamily={sceneFont} fontSize={32} fontWeight={650} fill={C.ink} textAlign="center" textWrap={true} />
      </Node>

      <Node ref={bridge} y={45} opacity={0}>
        <Rect x={0} y={0} width={900} height={610} radius={34} fill={C.panel} stroke={C.line} lineWidth={2} />
        <Label x={-295} y={-210} text="TEXT" color={C.muted} size={27} mono />
        <Label x={0} y={-210} text="TOKENS" color={C.mint} size={27} mono />
        <Label x={295} y={-210} text="IDS" color={C.blue} size={27} mono />
        <FlowLine points={[[-295, -155], [-295, -70], [-125, -70], [-125, 68], [0, 68], [0, 165]]} color={C.mint} width={5} opacity={0.8} />
        <FlowLine points={[[0, 68], [135, 68], [135, -70], [295, -70], [295, -155]]} color={C.blue} width={5} opacity={0.8} />
        <Rect x={-295} y={-30} width={190} height={80} radius={18} fill={C.panel2} stroke={C.line} lineWidth={2} />
        <Txt x={-295} y={-30} text="Cats" fontFamily={sceneFont} fontSize={34} fill={C.ink} textAlign="center" />
        <TokenTile x={0} y={-30} text="Cats" active width={170} />
        <Rect x={295} y={-30} width={190} height={80} radius={18} fill={C.panel2} stroke={C.blue} lineWidth={2} />
        <Txt x={295} y={-30} text="#3812" fontFamily={monoFont} fontSize={30} fill={C.blue} textAlign="center" />
        <Label x={0} y={235} text="the same idea at every step: piece → value" color={C.muted} size={23} mono />
        <Rect ref={bridgeLine} x={0} y={174} width={0} height={5} radius={3} fill={C.mint} />
        {Array.from({length: 6}, (_, i) => (
          <Node key={`bridge-dot-${i}`} ref={bridgeDots[i]} x={-335 + i * 134} y={174} opacity={0}>
            <Dot x={0} y={0} r={7} color={i < 3 ? C.mint : C.blue} />
          </Node>
        ))}
      </Node>

      <Node ref={bridgeCaption} y={720} opacity={0}>
        <Rect x={0} y={0} width={860} height={100} radius={20} fill={C.panel} opacity={0.94} />
        <Txt x={0} y={0} width={800} text={'Text becomes chunks.\nChunks become numbers.'} fontFamily={sceneFont} fontSize={31} fontWeight={650} fill={C.ink} textAlign="center" textWrap={true} lineHeight={1.12} />
      </Node>

      <Node ref={end} y={80} opacity={0}>
        <Label x={0} y={-255} text="THE SHORT VERSION" color={C.mint} size={27} mono />
        <Txt x={0} y={-105} text="TOKENS =" fontFamily={sceneFont} fontSize={86} fontWeight={760} fill={C.ink} textAlign="center" />
        <Txt x={0} y={15} text="TEXT  →  CHUNKS  →  IDS" fontFamily={monoFont} fontSize={54} fill={C.mint} textAlign="center" letterSpacing={2} />
        <Rule x={0} y={116} width={570} color={C.blue} />
        <Txt x={0} y={215} text="small pieces. stable numbers." fontFamily={sceneFont} fontSize={38} fontWeight={650} fill={C.muted} textAlign="center" />
      </Node>
    </Node>,
  );

  // 0.0-3.74: hook and ribbon entrance, aligned to narration cue 1.
  yield* all(
    reveal(title, 0.7, 22),
    reveal(ribbon, 0.7, -20),
    reveal(gate, 0.7, 24),
  );
  yield* all(
    ribbon().position.x(32, 1.4, easeInOutCubic),
    gate().scale(1.04, 0.7, easeOutCubic).to(1, 0.7, easeInOutCubic),
  );
  yield* reveal(hookCaption, 0.45, 20);
  yield* waitFor(0.97);

  // 3.74-7.21: split the ribbon into reusable token tiles.
  yield* all(fadeOut(hookCaption, 0.22), fadeOut(ribbon, 0.22), fadeOut(gate, 0.22), fadeOut(title, 0.22));
  yield* reveal(splitTitle, 0.45, 18);
  for (let i = 0; i < tiles.length; i++) {
    yield* reveal(tiles[i](), 0.32, 30);
    yield* waitFor(0.04);
  }
  yield* reveal(splitCaption, 0.3, 16);
  yield* waitFor(0.92);

  // 7.43-14.55: examples establish token categories, then emphasize the split.
  yield* all(
    fadeOut(splitTitle, 0.22),
    fadeOut(splitCaption, 0.22),
    ...tiles.map((tile) => fadeOut(tile(), 0.18)),
  );
  yield* all(reveal(exampleTitle, 0.5, 18), reveal(examplePanel, 0.58, 28));
  yield* reveal(exampleCaption, 0.38, 18);
  yield* waitFor(3.75);
  yield* all(
    examplePanel().scale(1.018, 0.28, easeOutCubic).to(1, 0.27, easeInOutCubic),
    exampleCaption().opacity(0.62, 0.22).to(1, 0.33, easeOutCubic),
  );
  yield* waitFor(1.67);

  // 14.77-18.06: IDs turn pieces into model-ready values.
  yield* all(fadeOut(exampleTitle, 0.22), fadeOut(examplePanel, 0.22), fadeOut(exampleCaption, 0.22));
  yield* waitFor(0.22);
  yield* all(reveal(idTitle, 0.52, 18), reveal(idPanel, 0.52, 28));
  yield* all(
    ...idTiles.map((tile) => reveal(tile(), 0.42, 24)),
    ...idBars.map((bar, i) => bar().height(52 + i * 14, 0.68, easeOutCubic)),
  );
  yield* reveal(idCaption, 0.38, 18);
  yield* waitFor(1.51);

  // 18.28-20.88: show that boundary rules vary by tokenizer vocabulary.
  yield* all(fadeOut(idTitle, 0.22), fadeOut(idPanel, 0.22), fadeOut(idCaption, 0.22));
  yield* waitFor(0.22);
  yield* all(reveal(caveatTitle, 0.55, 18), reveal(caveat, 0.55, 28));
  yield* reveal(caveatCaption, 0.35, 18);
  yield* waitFor(1.48);

  // 21.10-23.45: recap the complete text-to-number handoff.
  yield* all(fadeOut(caveatTitle, 0.22), fadeOut(caveat, 0.22), fadeOut(caveatCaption, 0.22));
  yield* waitFor(0.22);
  yield* all(reveal(bridge, 0.52, 28), reveal(bridgeCaption, 0.35, 18));
  yield* bridgeLine().width(760, 0.65, easeOutCubic);
  yield* all(...bridgeDots.map((dot) => reveal(dot(), 0.35, 0)));
  yield* waitFor(0.61);

  // 23.45-24.80: final takeaway stays visible through the closing line.
  yield* all(fadeOut(bridge, 0.22), fadeOut(bridgeCaption, 0.22));
  yield* reveal(end, 0.45, 30);
  yield* waitFor(0.9);
});
