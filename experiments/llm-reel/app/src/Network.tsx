import React from 'react';
import {C,Dot,ease,hash,lerp} from './design';

type P={x:number;y:number;z:number;scale:number};
// A real rotating 3D lattice, projected into SVG. Every pulse travels an edge.
export const Network:React.FC<{f:number;x?:number;y?:number;scale?:number;quiet?:boolean}>=({f,x=530,y=1010,scale=1,quiet=false})=>{
 const layers=7,n=10;
 const turn=-.3+Math.sin(f/160)*.25;
 const points:P[][]=Array.from({length:layers},(_,l)=>Array.from({length:n},(_,j)=>{
  const a=j/n*Math.PI*2+turn+l*.12;
  const xx=(l-3)*107, yy=Math.cos(a)*191,zz=Math.sin(a)*166;
  const rx=xx*.88+zz*.48,rz=-xx*.48+zz*.88;
  const s=850/(850+rz);
  return {x:x+(rx+yy*.10)*s*scale,y:y+(yy-xx*.33)*s*scale,z:rz,scale:s};
 }));
 const edges=points.slice(0,-1).flatMap((p,l)=>p.flatMap((a,j)=>[0,1,3].map((d)=>({a,b:points[l+1][(j+d)%n],l,j,d}))));
 const reveal=ease(f,0,36);
 return <g opacity={reveal}>
 <ellipse cx={x} cy={y+220*scale} rx={380*scale} ry={56*scale} fill={C.blue} opacity=".07" filter="url(#bloom)"/>
 {points.map((ps,l)=><g key={l}><path d={ps.map((p,i)=>`${i?'L':'M'}${p.x} ${p.y}`).join(' ')+'Z'} fill={l%2===0?'#518dff':'#7aefde'} fillOpacity=".04" stroke={C.blue} strokeOpacity=".4" strokeWidth="1"/>
 <text x={ps[0].x} y={ps[0].y+43*scale} fill={C.muted} opacity=".7" fontSize={19*scale} fontFamily="Mono" textAnchor="middle">{String(l+1).padStart(2,'0')}</text></g>)}
 {edges.map(({a,b,l,j,d},i)=>{
  const phase=((f*.018-l*.14-j*.033-d*.021)%1+1)%1;
  const hot=Math.pow(Math.max(0,Math.sin((f/13-l*.65-j*.15))),7);
  const color=(j+d)%3===0?C.violet:C.cyan;
  return <g key={i}>
  <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={color} strokeOpacity={.12+hot*.42} strokeWidth={.8+hot*.8}/>
  {!quiet&&i%3===0&&<Dot x={lerp(a.x,b.x,phase)} y={lerp(a.y,b.y,phase)} color={color} r={3.3*scale} opacity={.4+hot*.6}/>}
  </g>;
 })}
 {points.flat().sort((a,b)=>b.z-a.z).map((p,i)=><Dot key={i} x={p.x} y={p.y} r={(2.7+hash(i)*1.6)*p.scale*scale} opacity={.4+hash(i+9)*.6} color={i%4===0?C.violet:C.cyan}/>)}
 </g>;
};
