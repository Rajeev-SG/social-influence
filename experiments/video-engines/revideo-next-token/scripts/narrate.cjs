// Local Kokoro narration using the existing q8 ONNX cache. No model weights are downloaded.
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const {spawnSync} = require('node:child_process');
const crypto = require('node:crypto');

const root = path.resolve(__dirname, '..');
const audioDir = path.join(root, 'assets', 'audio');
fs.mkdirSync(audioDir, {recursive: true});

const packageRoot = process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json';
const req = createRequire(packageRoot);
const {KokoroTTS} = req('kokoro-js');
const {RawAudio} = req('@huggingface/transformers');

(async () => {
  const tts = await KokoroTTS.from_pretrained(
    'onnx-community/Kokoro-82M-v1.0-ONNX',
    {dtype: 'q8', local_files_only: true},
  );
  const script = JSON.parse(fs.readFileSync(path.join(root, 'assets', 'script.json'), 'utf8'));
  const sr = 24000;
  const lead = Math.round(0.28 * sr);
  const tail = Math.round(0.62 * sr);
  const pauses = [0.25, 0.22, 0.22, 0.23, 0.22, 0.30];
  let cursor = lead;
  const chunks = [new Float32Array(lead)];
  const cues = [];

  for (let i = 0; i < script.length; i += 1) {
    const audio = await tts.generate(script[i].say, {voice: 'bf_emma', speed: 0.97});
    const samples = audio.audio;
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.009;
    while (first < last && Math.abs(samples[first]) < threshold) first += 1;
    while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
    first = Math.max(0, first - Math.round(0.065 * sr));
    last = Math.min(samples.length, last + Math.round(0.09 * sr));
    const clean = samples.slice(first, last);
    const start = cursor / sr;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sr;
    cues.push({
      ...script[i],
      start,
      end,
      dur: end - start,
      file: `audio/line-${i}.wav`,
    });
    await new RawAudio(clean, sr).save(path.join(audioDir, `line-${i}.wav`));

    if (i < script.length - 1) {
      const pause = new Float32Array(Math.round(pauses[i] * sr));
      chunks.push(pause);
      cursor += pause.length;
    }
  }

  chunks.push(new Float32Array(tail));
  cursor += tail;
  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  const rawPath = path.join(audioDir, 'narration-raw.wav');
  await new RawAudio(merged, sr).save(rawPath);

  const processedPath = path.join(audioDir, 'narration.wav');
  const ff = spawnSync('ffmpeg', [
    '-hide_banner',
    '-loglevel',
    'error',
    '-y',
    '-i',
    rawPath,
    '-af',
    'highpass=f=78,lowpass=f=11500,acompressor=threshold=0.12:ratio=2:attack=15:release=180:makeup=1.15,loudnorm=I=-17:TP=-2:LRA=8',
    '-ar',
    '48000',
    processedPath,
  ]);
  if (ff.status !== 0) {
    throw new Error(`narration processing failed: ${ff.stderr.toString()}`);
  }

  const scriptHash = crypto
    .createHash('sha256')
    .update(fs.readFileSync(path.join(root, 'assets', 'script.json')))
    .digest('hex')
    .slice(0, 16);
  const timing = {
    width: 1080,
    height: 1920,
    fps: 30,
    total: cursor / sr,
    duration: cursor / sr,
    hash: scriptHash,
    cues,
  };
  fs.writeFileSync(path.join(root, 'src', 'timing.json'), `${JSON.stringify(timing, null, 2)}\n`);
  console.log(JSON.stringify({duration: timing.duration, cues}, null, 2));
})();
