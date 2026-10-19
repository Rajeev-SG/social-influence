// Generate the voice locally from the already-installed Kokoro 82M q8 ONNX cache.
// This script intentionally uses local_files_only and never downloads weights.
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');

const root = path.resolve(__dirname, '..');
const packageRoot = process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json';
const req = createRequire(packageRoot);
const {KokoroTTS} = req('kokoro-js');
const {RawAudio} = req('@huggingface/transformers');

const script = JSON.parse(fs.readFileSync(path.join(root, 'script.json'), 'utf8'));
const audioDir = path.join(root, 'assets', 'audio');
const lineDir = path.join(audioDir, 'lines');
fs.mkdirSync(lineDir, {recursive: true});

function trimmedSamples(samples, sampleRate) {
  let first = 0;
  let last = samples.length - 1;
  const threshold = 0.009;
  while (first < last && Math.abs(samples[first]) < threshold) first += 1;
  while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
  first = Math.max(0, first - Math.round(0.07 * sampleRate));
  last = Math.min(samples.length, last + Math.round(0.10 * sampleRate));
  return samples.slice(first, last);
}

function wordsFor(text, start, end) {
  const tokens = text.trim().split(/\s+/);
  const step = (end - start) / Math.max(1, tokens.length);
  return tokens.map((word, index) => ({
    text: word,
    start: Number((start + index * step).toFixed(3)),
    end: Number((start + (index + 1) * step).toFixed(3)),
  }));
}

(async () => {
  const tts = await KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX', {
    dtype: 'q8',
    local_files_only: true,
  });
  const sampleRate = 24000;
  const pauseAfter = [0.24, 0.22, 0.24, 0.24, 0.22, 0.24, 0.22, 0.30];
  const chunks = [new Float32Array(Math.round(0.20 * sampleRate))];
  let cursor = chunks[0].length;
  const cues = [];

  for (let index = 0; index < script.length; index += 1) {
    const item = script[index];
    const generated = await tts.generate(item.text, {voice: 'bf_emma', speed: 0.96});
    const clean = trimmedSamples(generated.audio, sampleRate);
    const start = cursor / sampleRate;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sampleRate;
    const linePath = path.join(lineDir, `line-${index}.wav`);
    await generated.save(linePath);
    cues.push({
      scene: item.scene,
      text: item.text,
      start: Number(start.toFixed(3)),
      end: Number(end.toFixed(3)),
      words: wordsFor(item.text, start, end),
      file: `audio/lines/line-${index}.wav`,
    });
    const pause = new Float32Array(Math.round(pauseAfter[index] * sampleRate));
    chunks.push(pause);
    cursor += pause.length;
    process.stdout.write(`${index + 1}/${script.length} ${item.scene} ${start.toFixed(2)}-${end.toFixed(2)}\n`);
  }

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  await new RawAudio(merged, sampleRate).save(path.join(audioDir, 'narration-raw.wav'));
  fs.writeFileSync(
    path.join(root, 'src', 'timing.json'),
    `${JSON.stringify({duration: Number((cursor / sampleRate).toFixed(3)), cues}, null, 2)}\n`,
  );
  process.stdout.write(`wrote ${cursor / sampleRate}s of local narration\n`);
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
