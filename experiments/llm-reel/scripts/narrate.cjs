// Reuse an existing Kokoro installation and cached ONNX weights. No model downloads.
const fs=require('node:fs');
const {createRequire}=require('node:module');
const req=createRequire(process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json');
const {KokoroTTS}=req('kokoro-js');
const {RawAudio}=req('@huggingface/transformers');
(async()=>{
 const tts=await KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX',{dtype:'q8',local_files_only:true});
 const script=JSON.parse(fs.readFileSync('script.json'));
 const sr=24000;let cursor=Math.round(.30*sr); const chunks=[new Float32Array(cursor)]; const cues=[];
 for(let i=0;i<script.length;i++){
  const audio=await tts.generate(script[i].text,{voice:'bf_emma',speed:0.96});
  // Remove the model's padded head/tail, retaining 70 ms breathing room.
  const samples=audio.audio; let first=0,last=samples.length-1;
  const threshold=.009;
  while(first<last && Math.abs(samples[first])<threshold)first++;
  while(last>first && Math.abs(samples[last])<threshold)last--;
  first=Math.max(0,first-Math.round(.07*sr));last=Math.min(samples.length,last+Math.round(.10*sr));
  const clean=samples.slice(first,last);
  const start=cursor/sr; chunks.push(clean);cursor+=clean.length;
  const end=cursor/sr;
  cues.push({...script[i],start,end,file:`audio/line-${i}.wav`});
  await audio.save(`app/public/audio/line-${i}.wav`);
  const pause=(i===14?1.0:i===1?.30:i===8?.38:i===11?.30:.23);chunks.push(new Float32Array(Math.round(pause*sr)));cursor+=Math.round(pause*sr);
  console.log(i,script[i].scene,start.toFixed(2),end.toFixed(2));
 }
 const merged=new Float32Array(cursor);let offset=0;for(const c of chunks){merged.set(c,offset);offset+=c.length;}
 await new RawAudio(merged,sr).save('app/public/audio/narration-raw.wav');
 fs.writeFileSync('app/src/timing.json',JSON.stringify({duration:cursor/sr,cues},null,2));
})();
