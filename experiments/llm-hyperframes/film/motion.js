/* Seekable GSAP: all state belongs to one paused Hyperframes timeline.
 * Word entrances adapt the installed text-stagger registry primitive. */
(() => {
const cues=window.FILM_TIMING.cues,D=window.FILM_TIMING.duration;
const t=i=>cues[i].start;const tl=gsap.timeline({paused:true});
const enter=(el,at,delay=0)=>tl.fromTo(el,{opacity:0,y:32},{opacity:1,y:0,duration:.65,ease:'power3.out'},at+delay);
const leave=(el,at)=>tl.to(el,{opacity:0,y:-18,duration:.24,ease:'power2.in'},at);
const swap=(old,next,at)=>{leave(old,at-.25);enter(next,at+.04);};
// The framework owns .clip visibility. Only inner typography/objects are animated.
// Scope the registry pattern to the actual word spans, not their line wrappers.
tl.fromTo('#hook-question .line > span',{opacity:0,y:55},{opacity:1,y:0,duration:.65,stagger:.1,ease:'power3.out'},.15);
tl.fromTo('#hook-answer',{opacity:0,y:30},{opacity:1,y:0,duration:.7,ease:'power3.out'},t(1)+.05);
leave('#hook-question',t(1)-.28);leave('#hook-answer',t(2)-.28);
// One continuously authored cup links the example, the loop and the ending.
tl.fromTo('#cup-art',{opacity:0,y:55,scale:.86},{opacity:1,y:0,scale:1,duration:1.1,ease:'power3.out'},.3);
tl.fromTo('#tea-surface,#tea-shine',{opacity:0},{opacity:1,duration:.7,ease:'power2.inOut'},t(3)+.05);
for(let i=0;i<3;i++){
 tl.fromTo(document.querySelectorAll('.steam')[i],{y:15,opacity:.12},{y:-21,opacity:.48,duration:2.2+i*.16,yoyo:true,repeat:8,ease:'sine.inOut'},.3+i*.25);
}
enter('#example-sentence',t(2));
tl.fromTo('#tea-choice',{opacity:0,y:160},{opacity:1,y:160,duration:.45,ease:'power3.out'},t(2)+.8);
enter('#bike-choice,#bike-art',t(2)+.8);
tl.fromTo('#tea-underline',{scaleX:0},{scaleX:1,duration:.45,ease:'power2.out'},t(3)+.12);
tl.to('#tea-choice',{y:0,duration:.72,ease:'power3.inOut'},t(3)+.05);
tl.to('#bike-choice,#bike-art',{opacity:0,x:100,rotation:6,duration:.55,ease:'power2.in'},t(3)+1.6);
tl.to('#cup-art',{x:130,y:70,scale:.82,duration:.85,ease:'power3.inOut'},t(2));
leave('#example-sentence,#tea-choice,#tea-underline',t(4)-.3);
tl.set('#cup-art',{opacity:0},t(4));
// Learning is one simple contrast: patterns learned before, used now.
enter('#training-heading',t(4)+.08);
tl.fromTo('.example-row',{opacity:0,y:32},{opacity:1,y:0,duration:.7,stagger:.24,ease:'power3.out'},t(4)+.6);
leave('#training-examples',t(5)-.24);
enter('#training-pair',t(5)+.1);
tl.fromTo('#training-rule',{scaleY:0},{scaleY:1,duration:.7,ease:'power2.inOut'},t(5)+.25);
leave('#training-heading,#training-pair,#training-rule',t(6)-.25);
// The complete prompt appears first; spacing opens only when pieces are explained.
enter('#loop-heading-a',t(6)+.03);
tl.fromTo('#loop-message',{opacity:0,y:24},{opacity:1,y:0,duration:.7,ease:'power3.out'},t(6)+.5);
tl.fromTo('.divider',{scaleY:0},{scaleY:1,duration:.5,stagger:.12,ease:'power2.out'},t(6)+1.0);
document.querySelectorAll('.piece').forEach((piece,i)=>{
 tl.to(piece,{backgroundColor:'#e89cb1',duration:.18},t(6)+1.45+i*.28);
 tl.to(piece,{backgroundColor:'rgba(232,156,177,0)',duration:.22},t(6)+1.75+i*.28);
});
swap('#loop-heading-a','#loop-heading-b',t(7));
tl.fromTo('#piece-tea',{opacity:0,y:70,scale:.88},{opacity:1,y:0,scale:1,duration:.75,ease:'back.out(1.1)'},t(7)+.6);
tl.fromTo('#cup-art',{opacity:0,x:310,y:330,scale:.50},{opacity:1,x:310,y:330,scale:.50,duration:.6,immediateRender:false},t(7)+.6);
swap('#loop-heading-b','#loop-heading-c',t(8));
enter('#piece-comma',t(8)+.25);enter('#piece-please',t(8)+1.0);enter('#piece-period',t(9)+.12);
enter('#loop-arrow,#loop-note',t(8)+.1);
tl.fromTo('#repeat-stroke',{strokeDasharray:1,strokeDashoffset:1},{strokeDashoffset:0,duration:.9,ease:'power2.inOut'},t(8)+.15);
leave('#loop-heading-c,#loop-message,#answer-line,#loop-arrow,#loop-note',t(10)-.3);
tl.set('#cup-art',{opacity:0},t(10));
// Three familiar capabilities, no extra diagrams.
enter('#useful-title',t(10)+.05);
tl.fromTo('.verb',{opacity:0,y:38},{opacity:1,y:0,duration:.7,stagger:.72,ease:'power3.out'},t(10)+.8);
leave('#useful-title,.verb',t(11)-.25);
// Quiet ending: the one thing to remember.
tl.fromTo('#limits-heading',{y:24,opacity:1},{y:0,opacity:1,duration:.6,ease:'power3.out'},t(11));
tl.fromTo('#cup-art',{opacity:0,x:0,y:0,scale:.8},{opacity:1,x:0,y:0,scale:.8,duration:.9,ease:'power3.out',immediateRender:false},t(11)+.3);
enter('#check-line',t(12)+1.6);
window.__timelines['main']=tl;
})();
