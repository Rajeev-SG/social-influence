import React from 'react';
import {AbsoluteFill,Sequence,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import timing from './timing.json';
import {Background,C,ease,lerp} from './design';
import {Hook,Tokens,Neural,Attention,Prediction,Generation,Training,Inference,Payoff,End} from './scenes';

export const durationInFrames=Math.ceil(timing.duration*30);
const starts=Object.fromEntries(timing.cues.filter((c,i,a)=>!i||a[i-1].scene!==c.scene).map(c=>[c.scene,Math.round(c.start*30)]));
starts.hook=0;
const names=Object.keys(starts);
const length=(name:string)=>{const i=names.indexOf(name);return (i===names.length-1?durationInFrames:starts[names[i+1]])-starts[name];};
const Stage:React.FC<{children:React.ReactNode;name:string}>=({children,name})=>{
 const f=useCurrentFrame();
 const reveal=name==='hook'?1:ease(f,0,12);
 const textAlpha=(name==='hook'?1:ease(f,8,20))*(name==='end'?1:1-ease(f,length(name)-8,length(name)));
 return <AbsoluteFill className={`stage-${name}`} style={{backgroundColor:C.bg,clipPath:`inset(0 ${(1-reveal)*100}% 0 0)`}}><style>{`.stage-${name} > div, .stage-${name} > svg text { filter: opacity(${textAlpha}); }`}</style><Background/>{children}</AbsoluteFill>;
};
const Captions=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 const cue=timing.cues.find(c=>f/fps>=c.start&&f/fps<c.end);
 if(!cue)return null;
 const caption:Caption={text:cue.text,startMs:cue.start*1000,endMs:cue.end*1000,timestampMs:null,confidence:1};
 return <div style={{position:'absolute',top:1528,left:90,right:120,textAlign:'left',fontSize:44,fontWeight:450,lineHeight:1.36,letterSpacing:-.6,color:C.ink,opacity:ease(f,cue.start*fps,cue.start*fps+3)}}>
 <div style={{width:38,height:2,background:C.cyan,marginBottom:18}}/>{caption.text}
 </div>;
};
export const Film=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <AbsoluteFill style={{backgroundColor:C.bg,color:C.ink,fontFamily:'Manrope',overflow:'hidden'}}>
 <Sequence from={starts.hook} durationInFrames={length('hook')+12} name="01 · The question"><Stage name="hook"><Hook/></Stage></Sequence>
 <Sequence from={starts.tokens} durationInFrames={length('tokens')+12} name="02 · Tokens"><Stage name="tokens"><Tokens/></Stage></Sequence>
 <Sequence from={starts.network} durationInFrames={length('network')+12} name="03 · Neural network"><Stage name="network"><Neural/></Stage></Sequence>
 <Sequence from={starts.attention} durationInFrames={length('attention')+12} name="04 · Attention"><Stage name="attention"><Attention/></Stage></Sequence>
 <Sequence from={starts.prediction} durationInFrames={length('prediction')+12} name="05 · Probabilities"><Stage name="prediction"><Prediction/></Stage></Sequence>
 <Sequence from={starts.generation} durationInFrames={length('generation')+12} name="06 · The loop"><Stage name="generation"><Generation/></Stage></Sequence>
 <Sequence from={starts.training} durationInFrames={length('training')+12} name="07 · Learning"><Stage name="training"><Training/></Stage></Sequence>
 <Sequence from={starts.inference} durationInFrames={length('inference')+12} name="08 · Answering"><Stage name="inference"><Inference/></Stage></Sequence>
 <Sequence from={starts.payoff} durationInFrames={length('payoff')+12} name="09 · Capabilities and limits"><Stage name="payoff"><Payoff/></Stage></Sequence>
 <Sequence from={starts.end} durationInFrames={length('end')+12} name="10 · Pullback"><Stage name="end"><End/></Stage></Sequence>
 <Captions/>
 <Audio src={staticFile('audio/narration.wav')}/>
 <Audio src={staticFile('audio/soundscape.wav')} volume={lerp(1,0,ease(f,durationInFrames-fps,durationInFrames))}/>
 </AbsoluteFill>;
};
