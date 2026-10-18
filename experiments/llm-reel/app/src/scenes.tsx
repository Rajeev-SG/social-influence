import {useCurrentFrame,useVideoConfig} from 'remotion';
import timing from './timing.json';
import {Accent,C,Dot,Label,Svg,Title,Token,ease,hash,lerp,clamp} from './design';
import {Network} from './Network';
const sceneLen=(name:string)=>{
 const cues=timing.cues.filter(c=>c.scene===name);const next=timing.cues.find(c=>c.start>cues[cues.length-1].start&&c.scene!==name);
 return (next?next.start:timing.duration)-cues[0].start;
};

export const Hook=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 const beat=timing.cues[1].start*fps;
 const change=ease(f,beat,beat+18),morph=ease(f,(sceneLen('hook')-.95)*fps,(sceneLen('hook')-.15)*fps);
 return <>
 <div style={{position:'absolute',left:88,top:143,fontFamily:'Mono',fontSize:24,letterSpacing:4,color:C.cyan,opacity:ease(f,0,20)}}>THE NEXT TOKEN / A SHORT FILM</div>
 <div style={{position:'absolute',left:86,top:270,fontSize:128,lineHeight:1.1,letterSpacing:-7,fontWeight:650,opacity:1-change,translate:`0 ${-20*change}px`}}>
 {['How does','ChatGPT','know?'].map((w,i)=><div key={w} style={{overflow:'hidden',paddingBottom:10,marginBottom:-10}}><div style={{color:i===1?C.cyan:C.ink,translate:`0 ${lerp(160,0,ease(f,i*5,i*5+27))}px`}}>{w}</div></div>)}
 </div>
 <div style={{position:'absolute',left:86,top:270,fontSize:120,lineHeight:1.08,letterSpacing:-6,fontWeight:600,opacity:change,translate:`0 ${lerp(40,0,change)}px`}}>Not a<br/><Accent>stored answer.</Accent></div>
 <Svg>
 <g opacity={1-morph} transform={`translate(540 1110) scale(${lerp(.82,1.1,ease(f,0,150))})`}>
 {[0,1,2].map(n=><g key={n} transform={`rotate(${-24+n*55+f*.10})`}>
 <ellipse rx={290+n*22} ry={105+n*23} fill="none" stroke={n===1?C.cyan:C.blue} strokeWidth="1.7" opacity=".45"/>
 <ellipse rx={290+n*22} ry={105+n*23} fill="none" stroke={C.cyan} strokeWidth="3" strokeDasharray="80 1400" strokeDashoffset={-f*3-n*120}/>
 <Dot x={Math.cos(f*.022+n*2)*(290+n*22)} y={Math.sin(f*.022+n*2)*(105+n*23)} r={6}/>
 </g>)}
 <circle r="170" fill="url(#halo)"/>
 <path d="M-90-102H90L115-77V105H-90Z" fill="url(#slab)" stroke={C.cyan}/><path d="M90-102V-77H115" fill="none" stroke={C.cyan}/>
 <text x="0" y="39" fill={C.cyan} fontSize="128" textAnchor="middle">?</text>
 </g>
 <g opacity={morph} transform={`translate(0 ${lerp(300,0,morph)})`}><rect x="90" y="754" width="868" height="132" rx="25" fill="#101e2a" stroke={C.cyan} strokeOpacity=".7"/><text x="130" y="836" fill={C.ink} fontSize="53">The cat sat on the</text><path d="M860 802l22 22-22 22 M880 824h-36" fill="none" stroke={C.cyan} strokeWidth="3"/></g>
 </Svg></>;
};

export const Tokens=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const split=ease(f,.35*fps,1.5*fps),fly=ease(f,(sceneLen('tokens')-.8)*fps,sceneLen('tokens')*fps);
 const texts=['The','cat','sat','on','the'];const ids=[791,8415,7731,389,279];
 return <><Title>Language,<br/><Accent>in pieces.</Accent></Title><Svg>
 <g opacity={1-split}><rect x="90" y="754" width="868" height="132" rx="25" fill="#101e2a" stroke={C.cyan} strokeOpacity=".7"/><text x="130" y="836" fill={C.ink} fontSize="53">The cat sat on the</text><path d="M860 802l22 22-22 22 M880 824h-36" fill="none" stroke={C.cyan} strokeWidth="3"/></g>
 {texts.map((text,i)=>{
  const tx=i<3?125+i*280:270+(i-3)*340,ty=i<3?825:1090;
  const x=lerp(lerp(132+i*156,tx,split),100+i*44,fly),y=lerp(lerp(780,ty,split),1080-i*58,fly);
  const vector=ease(f,45+i*4,75+i*4)*(1-fly);
  return <g key={i}>
  <g transform={`translate(${x} ${y}) rotate(${lerp(0,-12,fly)})`}><Token x={0} y={Math.sin(f/20+i)*7*split} w={170} text={text} active scale={lerp(1,.5,fly)}/>
  <text x="85" y="147" textAnchor="middle" fill={C.cyan} opacity={split*(1-fly)} fontFamily="Mono" fontSize="29">{Math.floor(lerp(0,ids[i],ease(f,35+i*5,65+i*5)))}</text>
  <g opacity={vector}>{Array.from({length:8},(_,j)=><rect key={j} x={18+j*19} y={174-hash(i*7+j)*36} width="9" height={10+hash(i*7+j)*36} fill={j%3?C.blue:C.cyan} opacity={.3+hash(j)*.7}/>)}</g>
  </g>
  {fly>0&&<path d={`M${x+70} ${y+40}Q550 ${700+i*70} 850 930`} stroke={C.cyan} strokeOpacity={fly*.3} fill="none" strokeWidth="1.4"/>}
  </g>;
 })}
 <g opacity={ease(f,60,85)*(1-fly)}><Label x={90} y={1420} size={28}>TEXT → TOKEN IDs → NUMERICAL VECTORS</Label></g>
 </Svg></>;
};

export const Neural=()=>{
 const f=useCurrentFrame();return <><Title center top={210} size={94}>Meaning lives in<br/><Accent>the connections.</Accent></Title><Svg>
 <g transform={`translate(540 1000) scale(${lerp(.87,1.12,ease(f,0,150))}) translate(-540 -1000)`}><Network f={f} y={1000} scale={1.1}/></g>
 <g opacity={ease(f,15,45)}><path d="M190 1220H90V1340H370" stroke={C.cyan} opacity=".6" fill="none"/><Label x={90} y={1390} color={C.cyan} size={31}>ATTENTION</Label><text x="90" y="1440" fill={C.muted} fontSize="35">Information moves between tokens.</text>
 <path d="M910 825h55V675H710" stroke={C.blue} opacity=".6" fill="none"/><Label x={710} y={650} size={25}>LAYER BY LAYER</Label></g>
 {[0,1,2,3,4].map(i=>{const p=clamp((f-i*8)/75);return <g key={i} opacity={Math.sin(p*Math.PI)*.9} transform={`translate(${lerp(60,920,p)} ${lerp(1160-i*55,780+i*25,p)})`}><rect width="63" height="37" rx="5" fill="#153b45" stroke={C.cyan}/><text x="31" y="26" fontSize="20" fontFamily="Mono" textAnchor="middle" fill={C.cyan}>{[791,8415,7731,389,279][i]}</text></g>;})}
 </Svg></>;
};

export const Attention=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const chosen=ease(f,2.1*fps,2.65*fps);
 const xs=[140,335,520,695,855],ws=['The','cat','sat','on','the'];
 return <><div style={{position:'absolute',top:240,left:90,fontFamily:'Mono',color:C.muted,fontSize:27,letterSpacing:3}}>ATTENTION / RELEVANCE IN CONTEXT</div>
 <Svg>
 <text x="540" y="506" textAnchor="middle" fontSize="138" letterSpacing="-6" fill={C.ink} fontWeight="550" opacity={ease(f,0,25)}>…on the <tspan fill={C.cyan}>what?</tspan></text>
 {ws.map((w,i)=>{const energy=(i===1?.75:i===2?.55:.15)*(1+.12*Math.sin(f/11+i));return <g key={i} opacity={ease(f,i*4,20+i*4)}>
 <text x={xs[i]} y="725" textAnchor="middle" fill={i===1||i===2?C.cyan:C.ink} fontSize="56" fontWeight="550">{w}</text>
 <path d={`M${xs[i]} 762 Q${xs[i]} ${960+i*8},540 1060`} fill="none" stroke={i===1?C.cyan:C.blue} strokeWidth={1+energy*8} strokeOpacity={energy} pathLength="1" strokeDasharray="1" strokeDashoffset={1-ease(f,12+i*5,50+i*5)}/>
 {[0,1,2].map(k=>{const t=(f*.014+k/3+i*.13)%1;const x=(1-t)*(1-t)*xs[i]+2*(1-t)*t*xs[i]+t*t*540,y=(1-t)*(1-t)*762+2*(1-t)*t*(960+i*8)+t*t*1060;return <Dot key={k} x={x} y={y} r={2+energy*5} opacity={ease(f,20,40)*energy} color={i===1?C.cyan:C.blue}/>;})}
 </g>})}
 <g transform="translate(540 1065)"><circle r={128+Math.sin(f/15)*4} fill="none" stroke={C.cyan} strokeOpacity=".24"/><circle r="98" fill="#102832" stroke={C.cyan} strokeWidth="2"/><text y="21" textAnchor="middle" fontSize="65" fill={C.cyan} fontWeight="600">{chosen>.6?'mat':'…'}</text></g>
 <g opacity={chosen}><text x="780" y="1075" fill={C.muted} fontSize="37">moon</text><path d="M776 1045l101 35" stroke={C.muted} strokeWidth="2"/></g>
 <text x="540" y="1350" textAnchor="middle" fill={C.ink} fontSize="64" fontWeight="550">Context changes the odds.</text>
 </Svg></>;
};

export const Prediction=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const pick=ease(f,(sceneLen('prediction')-1.3)*fps,(sceneLen('prediction')-.6)*fps);
 const words=['mat','floor','bed','moon'],values=[68,21,8,3];
 return <><Title top={215} size={110}>What comes<br/><Accent>next?</Accent></Title><Svg>
 <text x="945" y="465" fill={C.cyan} fontSize="176" letterSpacing="-10" fontWeight="500" textAnchor="end">{Math.round(68*ease(f,10,55))}<tspan fontSize="73">%</tspan></text>
 <text x="90" y="687" fill={C.muted} fontSize="38">The cat sat on the <tspan fill={C.ink}>___</tspan></text>
 {[0,1,2,3].map(i=><path key={i} d={`M90 ${1290-i*150}H945`} stroke={C.line} strokeDasharray="3 8" strokeOpacity=".65"/>)}
 {words.map((w,i)=>{
 const t=ease(f,13+i*7,65+i*7),x=125+i*210,h=values[i]/68*480*t,y=1290-h,dim=lerp(1,i===0?1:.3,pick);
 return <g key={w} opacity={dim}>
 <path d={`M${x} 1290V${y}H${x+120}V1290Z`} fill={i===0?'#16454a':'#172d46'} stroke={i===0?C.cyan:C.blue} strokeOpacity=".7"/>
 <path d={`M${x+120} ${y}l25 -22v${h}l-25 22Z`} fill={i===0?'#102d34':'#111e32'} stroke={i===0?C.cyan:C.blue} strokeOpacity=".5"/>
 <path d={`M${x} ${y}l25 -22h120l-25 22Z`} fill={i===0?C.cyan:C.blue} fillOpacity={i===0?.8:.35} stroke={i===0?C.cyan:C.blue}/>
 {Array.from({length:7},(_,j)=><path key={j} d={`M${x} ${1290-j*h/7}h120`} stroke={i===0?C.cyan:C.blue} opacity=".15"/>)}
 <text x={x+60} y={y-53} textAnchor="middle" fill={i===0?C.cyan:C.muted} fontFamily="Mono" fontSize="32">{Math.round(values[i]*t)}%</text>
 <text x={x+60} y="1365" textAnchor="middle" fill={i===0?C.cyan:C.ink} fontSize="46" fontWeight="600">{w}</text>
 {i===0&&<g opacity={pick}><path d={`M${x-20} ${y-42}v-20h30 M${x+140} ${y-42}v-20h-30`} stroke={C.cyan} strokeWidth="3" fill="none"/><Dot x={x+60} y={y-11} r={7}/></g>}
 </g>;
 })}
 <Label x={90} y={1460} size={30}>ILLUSTRATIVE PROBABILITIES</Label>
 </Svg></>;
};

export const Generation=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 const first=ease(f,.45*fps,1.45*fps),second=ease(f,2.6*fps,3.6*fps);const isSecond=f>2.6*fps;const p=isSecond?second:first;const angle=p*Math.PI*1.5-Math.PI/2;
 const append1=first>.98,append2=second>.98;
 return <><Title center top={235} size={105}>Predict. Append.<br/><Accent>Repeat.</Accent></Title><Svg>
 <g transform="translate(540 975)">
 <circle r="250" fill="none" stroke={C.line} strokeWidth="3"/>
 <circle r="250" fill="none" stroke={C.cyan} strokeWidth="4" strokeDasharray="175 1395" transform={`rotate(${p*270-90})`}/>
 <circle r="216" fill="none" stroke={C.blue} strokeOpacity=".3" strokeDasharray="2 10"/>
 <path d="M-125-100H125V100H-125Z" fill="url(#slab)" stroke={C.cyan} strokeOpacity=".7"/>
 {Array.from({length:5},(_,i)=>Array.from({length:4},(_,j)=><g key={`${i}-${j}`}><path d={`M${-88+i*43} ${-60+j*40}l43 ${i%2?40:-40}`} stroke={C.cyan} opacity=".18"/><Dot x={-88+i*43} y={-60+j*40} r={2.5} opacity={.35+Math.sin(f/8+i+j)*.2}/></g>))}
 <text y="17" textAnchor="middle" fill={C.ink} fontSize="49" fontWeight="600">LLM</text>
 <Dot x={Math.cos(angle)*250} y={Math.sin(angle)*250} r={8}/>
 <g transform="translate(0 -250)"><rect x="-125" y="-25" width="250" height="50" fill={C.bg}/><text y="10" textAnchor="middle" fill={C.cyan} fontSize="31" fontFamily="Mono">READ CONTEXT</text></g>
 <g transform="translate(250 40)"><rect x="-85" y="-25" width="170" height="50" fill={C.bg}/><text y="10" textAnchor="middle" fill={C.cyan} fontSize="31" fontFamily="Mono">PREDICT</text></g>
 </g>
 <g opacity={!append2?1:0}>
 <Token x={lerp(470,790,p)} y={lerp(930,1345,p)} text={isSecond?'.':'mat'} w={isSecond?70:135} active scale={lerp(1,.8,p)}/>
 </g>
 <path d="M540 1230V1300H140V1420H540" stroke={C.cyan} fill="none" strokeOpacity=".35" strokeWidth="2"/>
 <text x="90" y="1395" fill={C.ink} fontSize="53" fontWeight="550">The cat sat on the<tspan fill={C.cyan}>{append1?' mat':''}{append2?'.':''}</tspan></text>
 <Label x={90} y={1480} size={25}>THE OUTPUT BECOMES THE NEXT INPUT</Label>
 </Svg></>;
};

const WeightField=({f,frozen=false,y=1000,scale=1}:{f:number;frozen?:boolean;y?:number;scale?:number})=>{
 const duration=sceneLen('training')*30;const settle=ease(f,duration-55,duration-10);const t=frozen?duration: f;
 return <g transform={`translate(540 ${y}) scale(${scale}) matrix(.94,-.24,.45,.78,0,0)`}>
 <path d="M-360-220H360V220L340 242H-380V-198Z" fill="#0c1a27" stroke="#64899b"/>
 <path d="M-360-220V220H360 M-360 220l-20 22 M360 220l-20 22" stroke="#94c2d0" opacity=".5" fill="none"/>
 {Array.from({length:13*8},(_,i)=>{
 const col=i%13,row=Math.floor(i/13),v=.25+hash(i)*.65;
 const stable=hash(i)*.7,changing=hash(i+Math.floor(t/6))*.7;
 const value=frozen?stable:lerp(changing,stable,settle);
 return <g key={i} transform={`translate(${-330+col*53},${-190+row*52})`}>
 <rect width="34" height="34" rx="4" fill={i%7===0?C.violet:C.cyan} opacity={v*.65}/>
 <path d={`M7 27L${8+value*29} 7`} stroke={C.ink} opacity=".7" strokeWidth="2"/>
 <circle cx="17" cy="17" r="11" fill="none" stroke={C.ink} strokeOpacity=".13"/>
 </g>;
 })}
 {!frozen&&<path d={`M${lerp(-375,390,settle)} -225V230`} stroke={C.cyan} strokeWidth="4" opacity={Math.sin(settle*Math.PI)}/>}
 </g>;
};

export const Training=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const cue=timing.cues.find(c=>c.scene==='training')!;const beat=(timing.cues.find(c=>c.text.startsWith('Training adjusted'))!.start-cue.start)*fps;
 const learn=ease(f,beat,beat+18),finish=ease(f,(sceneLen('training')-1.4)*fps,(sceneLen('training')-.4)*fps);
 return <><div style={{position:'absolute',top:240,left:88,fontSize:105,fontWeight:600,letterSpacing:-5,lineHeight:1.1,opacity:1-learn}}>Where did this<br/><Accent>come from?</Accent></div>
 <div style={{position:'absolute',top:230,left:88,fontSize:114,fontWeight:600,letterSpacing:-5,lineHeight:1.1,opacity:learn}}>Learn the<br/><Accent>patterns.</Accent></div><Svg>
 <WeightField f={f} y={1040}/>
 {Array.from({length:17},(_,i)=>{const p=(f/80+i/17)%1;return <g key={i} opacity={Math.sin(p*Math.PI)*.7*learn*(1-finish)} transform={`translate(${lerp(-150,310,p)} ${790+i*27})`}><path d="M0 0h115" stroke={i%2?C.blue:C.cyan} strokeWidth="2"/><text y="-9" fill={C.muted} fontFamily="Mono" fontSize="19">{['text','01 10','{ }','example'][i%4]}</text></g>})}
 <Label x={90} y={710} color={C.cyan} size={29}>TRAINING / CHANGE THE SETTINGS</Label>
 <g opacity={learn}><text x="90" y="1398" fill={C.cyan} fontSize="50" fontWeight="600">Billions of internal adjustments.</text><text x="90" y="1454" fill={C.muted} fontSize="34">Patterns learned from examples.</text></g>
 <g opacity={finish}><path d="M710 721H938V807" stroke={C.cyan} fill="none"/><Label x={710} y={698} size={24} color={C.cyan}>LEARNED WEIGHTS</Label><Dot x={938} y={807} r={5}/></g>
 </Svg></>;
};

export const Inference=()=>{
 const f=useCurrentFrame();const shrink=ease(f,0,40);
 return <><Title top={230} size={108}>Same settings.<br/><Accent>New answer.</Accent></Title><Svg>
 <WeightField f={f} frozen y={lerp(1040,945,shrink)} scale={lerp(1,.76,shrink)}/>
 <g opacity={shrink}>
 <Label x={308} y={1160} color={C.cyan} size={29}>THE WEIGHTS STAY FIXED</Label>
 <path d="M155 1270Q40 750 350 860 M740 870Q1010 760 930 1280" stroke={C.blue} strokeOpacity=".55" strokeWidth="2" fill="none"/>
 <path d="M155 1270Q40 750 350 860 M740 870Q1010 760 930 1280" stroke={C.cyan} strokeWidth="5" fill="none" pathLength="100" strokeDasharray="7 93" strokeDashoffset={-f*1.1}/>
 <Token x={90} y={1290} text="prompt" w={175}/><Token x={755} y={1290} text="reply" w={175} active/>
 <text x="540" y="1435" fill={C.muted} textAnchor="middle" fontSize="35">Use what was learned. Don’t retrain.</text>
 </g>
 </Svg></>;
};

export const Payoff=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const cues=timing.cues.filter(c=>c.scene==='payoff');const beat=(cues[1].start-cues[0].start)*fps,caution=ease(f,beat,beat+16);
 const outputs=[['EXPLAIN','Light scatters in the atmosphere.'],['CODE','return ideas.map(makeSomething);'],['CREATE','A city that wakes with the tide.']];
 return <>
 <div style={{opacity:1-caution}}><Title center top={220} size={100}>One mechanism.<br/><Accent>Many abilities.</Accent></Title><Svg>
 <path d="M130 670V1400" stroke={C.cyan} opacity=".45"/>
 {outputs.map(([label,text],i)=>{const count=Math.floor(text.length*ease(f,6+i*20,43+i*20));return <g key={label} opacity={ease(f,i*18,i*18+17)}><Dot x={130} y={760+i*250} r={7}/><path d={`M130 ${760+i*250}H180`} stroke={C.cyan} opacity=".6"/><Label x={210} y={744+i*250} size={27} color={i===1?C.violet:C.cyan}>{label}</Label><text x="210" y={809+i*250} fill={C.ink} fontFamily={i===1?'Mono':'Manrope'} fontSize={i===1?35:39}>{text.slice(0,count)}<tspan fill={C.cyan}>▌</tspan></text></g>})}
 </Svg></div>
 <div style={{opacity:caution}}><Title top={220} size={108}>Likely doesn’t<br/>mean <Accent color={C.amber}>true.</Accent></Title><Svg>
 <Label x={90} y={730} color={C.amber} size={28}>AN ILLUSTRATIVE FALSE ANSWER</Label>
 <text x="90" y="930" fill={C.ink} fontSize="91" letterSpacing="-3" fontWeight="500">The Moon is</text><text x="90" y="1048" fill={C.ink} fontSize="91" letterSpacing="-3" fontWeight="500">made of <tspan fill={C.amber}>glass.</tspan></text>
 <path d="M438 1085H950" stroke={C.amber} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1-ease(f,beat+15,beat+45)}/>
 <path d="M90 1180H950" stroke={C.line}/>
 <text x="90" y="1290" fill={C.amber} fontSize="60" fontWeight="550">Fluency ≠ truth.</text>
 <Label x={90} y={1390} size={27}>CHECK IMPORTANT CLAIMS.</Label>
 </Svg></div>
 </>;
};

export const End=()=>{
 const f=useCurrentFrame();const e=ease(f,0,65);
 return <><div style={{position:'absolute',left:86,top:240,fontSize:110,lineHeight:1.08,letterSpacing:-5,fontWeight:600}}>Powerful<br/><Accent>prediction.</Accent><br/><span style={{display:'block',marginTop:38,color:C.muted,fontWeight:450}}>Not perfect<br/>knowledge.</span></div>
 <Svg>
 <g transform={`translate(540 1160) scale(${lerp(1.5,1,e)}) translate(-540 -1160)`} opacity={ease(f,0,16)}>
 <path d="M190 1135H260 M590 1135H685 M780 1135H875" stroke={C.cyan} opacity=".55" strokeWidth="2"/>
 <Token x={110} y={1095} w={90} text="text" active scale={.9}/>
 <Network f={f+120} x={430} y={1140} scale={.38} quiet/>
 {[0,1,2].map(i=><rect key={i} x={692+i*26} y={1180-[95,55,26][i]} width="17" height={[95,55,26][i]} fill={i===0?C.cyan:C.blue} opacity=".8"/>)}
 <Token x={854} y={1095} w={90} text="next" active scale={.9}/>
 <path d="M904 1220V1335H155V1220" stroke={C.cyan} strokeOpacity=".4" strokeWidth="2" fill="none"/>
 <path d="M904 1220V1335H155V1220" stroke={C.cyan} strokeWidth="3" fill="none" pathLength="100" strokeDasharray="6 94" strokeDashoffset={-f*.5}/>
 <Label x={93} y={1270} size={24}>TOKENS</Label><Label x={350} y={1270} size={24}>CONTEXT</Label><Label x={665} y={1270} size={24}>PREDICT</Label><Label x={840} y={1270} size={24}>APPEND</Label>
 <text x="540" y="1435" textAnchor="middle" fill={C.cyan} fontFamily="Mono" fontSize="27" letterSpacing="4">REPEAT</text>
 </g>
 </Svg></>;
};
