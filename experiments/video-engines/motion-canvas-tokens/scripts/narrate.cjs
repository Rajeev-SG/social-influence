// Local Kokoro 82M q8 ONNX synthesis. No TTS weights are downloaded.
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const {spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '..');
const packageRoot = process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json';
const req = createRequire(packageRoot);
const {KokoroTTS} = req('kokoro-js');
const {RawAudio} = req('@huggingface/transformers');

(async () => {
  const script = JSON.parse(fs.readFileSync(path.join(__dirname, 'narration-script.json'), 'utf8'));
  const tts = await KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX', {
    dtype: 'q8',
    local_files_only: true,
  });
  const sr = 24000;
  const lead = Math.round(0.18 * sr);
  const chunks = [new Float32Array(lead)];
  const cues = [];
  let cursor = lead;

  for (let i = 0; i < script.length; i++) {
    const generated = await tts.generate(script[i].text, {voice: 'bf_emma', speed: 1.06});
    const samples = generated.audio;
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.008;
    while (first < last && Math.abs(samples[first]) < threshold) first++;
    while (last > first && Math.abs(samples[last]) < threshold) last--;
    first = Math.max(0, first - Math.round(0.065 * sr));
    last = Math.min(samples.length, last + Math.round(0.095 * sr));
    const clean = samples.slice(first, last);
    const start = cursor / sr;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sr;
    cues.push({text: script[i].text, start, end, index: i});
    const pause = Math.round(script[i].pause * sr);
    chunks.push(new Float32Array(pause));
    cursor += pause;
    console.log(`${i + 1}/${script.length} ${start.toFixed(3)}-${end.toFixed(3)} ${script[i].text}`);
  }

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  const rawPath = path.join(root, 'assets/audio/narration-raw.wav');
  const outPath = path.join(root, 'assets/audio/narration.wav');
  await new RawAudio(merged, sr).save(rawPath);
  const result = spawnSync('ffmpeg', [
    '-hide_banner', '-loglevel', 'error', '-y', '-i', rawPath,
    '-af', 'highpass=f=72,lowpass=f=11500,acompressor=threshold=0.11:ratio=2:attack=15:release=180:makeup=1.1,loudnorm=I=-17:TP=-2:LRA=8',
    '-ar', '48000', '-ac', '2', outPath,
  ], {stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
  fs.writeFileSync(path.join(root, 'assets/audio/narration-cues.json'), JSON.stringify({duration: cursor / sr, cues}, null, 2));
  console.log(`narration duration: ${(cursor / sr).toFixed(3)}s`);
})();
