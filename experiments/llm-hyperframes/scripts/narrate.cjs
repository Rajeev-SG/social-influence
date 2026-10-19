const fs=require('node:fs');const {createRequire}=require('node:module');
const req=createRequire(process.env.KOKORO_PACKAGE||'/Users/rajeev/Code/content-machine/package.json');
const {KokoroTTS}=req('kokoro-js');const {RawAudio}=req('@huggingface/transformers');
(async()=>{
const model=await KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX',{dtype:'q8',local_files_only:true});
const sr=24000;let cursor=Math.round(.35*sr);const chunks=[new Float32Array(cursor)],cues=[];
for(const unit of JSON.parse(fs.readFileSync('script.json'))){
 const a=await model.generate(unit.text,{voice:'bf_emma',speed:.91});
 let first=0,last=a.audio.length-1;
 while(first<last&&Math.abs(a.audio[first])<.009)first++;
 while(last>first&&Math.abs(a.audio[last])<.009)last--;
 const clean=a.audio.slice(Math.max(0,first-Math.round(.08*sr)),Math.min(a.audio.length,last+Math.round(.13*sr)));
 const start=cursor/sr;chunks.push(clean);cursor+=clean.length;
 cues.push({...unit,start,end:cursor/sr});
 const pause=.34;chunks.push(new Float32Array(Math.round(pause*sr)));cursor+=Math.round(pause*sr);
 console.log(unit.scene,start.toFixed(2),(cursor/sr).toFixed(2));
}
chunks.push(new Float32Array(Math.round(.65*sr)));cursor+=Math.round(.65*sr);
let offset=0;const merged=new Float32Array(cursor);for(const c of chunks){merged.set(c,offset);offset+=c.length;}
await new RawAudio(merged,sr).save('.review/narration-raw.wav');
fs.writeFileSync('timing.json',JSON.stringify({duration:cursor/sr,cues},null,2));
})();
