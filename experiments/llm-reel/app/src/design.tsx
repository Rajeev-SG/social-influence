import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

loadFont({family:'Manrope',url:staticFile('fonts/Manrope.ttf'),weight:'200 800'});
loadFont({family:'Mono',url:staticFile('fonts/Mono.ttf')});
export const C={bg:'#080e18',ink:'#f1f0e8',muted:'#8a9dac',cyan:'#7aefde',blue:'#528dff',violet:'#b2a0ff',line:'#263b4b',amber:'#f1b97c'};
export const clamp=(x:number)=>Math.max(0,Math.min(1,x));
export const ease=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(.22,1,.36,1)});
export const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
export const hash=(n:number)=>{const v=Math.sin(n*127.1+311.7)*43758.5453;return v-Math.floor(v);};
export const Label:React.FC<{x?:number;y?:number;children:React.ReactNode;color?:string;size?:number}>=({x=0,y=0,children,color=C.muted,size=24})=><text x={x} y={y} fill={color} fontFamily="Mono" fontSize={size} letterSpacing={2}>{children}</text>;
export const Title:React.FC<{children:React.ReactNode;top?:number;size?:number;center?:boolean}>=({children,top=230,size=100,center=false})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();return <div style={{position:'absolute',top,left:88,right:100,fontSize:size,textAlign:center?'center':'left',fontWeight:650,letterSpacing:-5,lineHeight:1.08,translate:`0 ${lerp(38,0,ease(f,0,.7*fps))}px`,opacity:ease(f,0,.45*fps)}}>{children}</div>;
};
export const Accent:React.FC<{children:React.ReactNode;color?:string}>=({children,color=C.cyan})=><span style={{color}}>{children}</span>;
export const Defs=()=> <defs>
 <radialGradient id="halo"><stop stopColor={C.blue} stopOpacity=".27"/><stop offset="1" stopColor={C.blue} stopOpacity="0"/></radialGradient>
 <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1"><stop stopColor={C.cyan}/><stop offset="1" stopColor={C.blue}/></linearGradient>
 <linearGradient id="slab" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#163846"/><stop offset="1" stopColor="#0c1827"/></linearGradient>
 <filter id="bloom" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="9"/></filter>
 <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
 </defs>;
export const Dot=({x,y,r=5,color=C.cyan,opacity=1}:{x:number;y:number;r?:number;color?:string;opacity?:number})=><g opacity={opacity}><circle cx={x} cy={y} r={r*2.8} fill={color} opacity=".22" filter="url(#soft)"/><circle cx={x} cy={y} r={r} fill={color}/><circle cx={x-1} cy={y-1} r={r*.3} fill="white"/></g>;
export const Svg:React.FC<{children:React.ReactNode;style?:React.CSSProperties}>=({children,style})=><svg width="1080" height="1920" viewBox="0 0 1080 1920" style={{position:'absolute',inset:0,overflow:'visible',...style}}><Defs/>{children}</svg>;
export const Frame:React.FC<{children:React.ReactNode}>=({children})=> <div style={{position:'absolute',inset:0}}>{children}</div>;
export const Background=()=>{
 const f=useCurrentFrame();return <Svg>
 <ellipse cx={540+Math.sin(f/200)*100} cy="950" rx="650" ry="720" fill="url(#halo)" opacity=".7"/>
 <g stroke={C.line} strokeWidth="1" opacity=".18">{Array.from({length:16},(_,i)=><path key={i} d={`M${i*80-60} 0 V1920 M0 ${i*130+50} H1080`}/>)}</g>
 <g stroke={C.muted} opacity="0">{[[56,160],[1024,160],[56,1750],[1024,1750]].map(([x,y],i)=><path key={i} d={`M${x-7} ${y}h14 M${x} ${y-7}v14`}/>)}</g>
 </Svg>;
};
export const Token=({x,y,w=132,text,active=false,opacity=1,scale=1}:{x:number;y:number;w?:number;text:string;active?:boolean;opacity?:number;scale?:number})=><g transform={`translate(${x} ${y}) scale(${scale})`} opacity={opacity}>
 <path d={`M0 0 L12 -12 H${w+12} V66 L${w} 78 H0 Z`} fill={active?'#163c46':'#111f2d'} stroke={active?C.cyan:'#375563'} strokeWidth="1.5"/>
 <path d={`M0 0 H${w} V78 M${w} 0l12 -12 M${w} 78l12 -12`} fill="none" stroke={active?C.cyan:'#375563'} opacity=".65"/>
 <text x={w/2} y="50" fill={active?C.cyan:C.ink} fontSize="38" fontWeight="550" textAnchor="middle" fontFamily="Manrope">{text}</text>
 </g>;
