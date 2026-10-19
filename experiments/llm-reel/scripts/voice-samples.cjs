const {createRequire}=require('node:module');
const req=createRequire(process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json');
const {KokoroTTS}=req('kokoro-js');
require('node:fs').mkdirSync('.review',{recursive:true});
(async()=>{
 const tts=await KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX',{dtype:'q8',local_files_only:true});
 for(const voice of ['bm_george','bf_emma','bm_fable']){
  const a=await tts.generate('How does ChatGPT actually know what to say? A likely next word is not a guarantee of truth.',{voice,speed:1.02});
  await a.save(`.review/sample-${voice}.wav`); console.log(voice,a.audio.length/a.sampling_rate);
 }
})();
