import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const CONTENT_MACHINE = '/Users/rajeev/Code/content-machine';
const KOKORO = path.join(CONTENT_MACHINE, 'node_modules/kokoro-js/dist/kokoro.js');
const TRANSFORMERS = path.join(CONTENT_MACHINE, 'node_modules/@huggingface/transformers/dist/transformers.js');
const MODEL_CACHE = path.join(CONTENT_MACHINE, 'node_modules/@huggingface/transformers/.cache/');
const MODEL_ID = 'onnx-community/Kokoro-82M-v1.0-ONNX';
const VOICE = 'bf_emma';

const segments = [
  { id: 'hook', text: 'AI has to choose the next word.' },
  { id: 'definition', text: 'Temperature is the dial for how surprising that choice can be.' },
  { id: 'low', text: 'Turn it low, and the path stays focused: the safest option wins every time.' },
  { id: 'high', text: 'Turn it up, and more paths become possible.' },
  { id: 'tradeoff', text: 'Low temperature feels predictable. High temperature feels creative.' },
  { id: 'end', text: 'It changes variety, not intelligence.' },
];

const assets = path.join(ROOT, 'assets');
const parts = path.join(assets, 'narration-parts');
fs.mkdirSync(parts, { recursive: true });
const partPaths = [];
const timing = [];
let cursor = 0;

for (const segment of segments) {
  const out = path.join(parts, `${segment.id}.wav`);
  if (!fs.existsSync(out)) {
    const { KokoroTTS } = await import(`file://${KOKORO}`);
    const { env } = await import(`file://${TRANSFORMERS}`);
    env.allowRemoteModels = false;
    env.allowLocalModels = true;
    env.localModelPath = MODEL_CACHE;
    env.cacheDir = MODEL_CACHE;
    const tts = await KokoroTTS.from_pretrained(MODEL_ID, { dtype: 'q8', device: 'cpu' });
    const audio = await tts.generate(segment.text, { voice: VOICE, speed: 1.0 });
    await audio.save(out);
  }
  const probe = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', out], { encoding: 'utf8' }).trim();
  const duration = Number(probe);
  timing.push({ id: segment.id, text: segment.text, start: Number(cursor.toFixed(4)), end: Number((cursor + duration).toFixed(4)), duration: Number(duration.toFixed(4)), file: path.relative(ROOT, out) });
  cursor += duration + 0.12;
  partPaths.push(out);
}

const narration = path.join(assets, 'narration.wav');
const paddedInputs = partPaths.map((_, i) => {
  const filter = i < partPaths.length - 1 ? 'apad=pad_dur=0.12' : 'anull';
  return `[${i}:a]${filter}[p${i}]`;
});
const filter = paddedInputs.join(';') + ';' + partPaths.map((_, i) => `[p${i}]`).join('') + `concat=n=${partPaths.length}:v=0:a=1[voice]`;
const args = ['-y'];
for (const p of partPaths) args.push('-i', p);
args.push('-filter_complex', filter, '-map', '[voice]', '-ar', '48000', '-ac', '2', narration);
execFileSync('ffmpeg', args, { stdio: 'pipe' });

const total = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', narration], { encoding: 'utf8' }).trim());
const timeline = {
  fps: 30,
  durationInFrames: 660,
  narrationDuration: Number(total.toFixed(4)),
  segments: timing,
};
fs.writeFileSync(path.join(ROOT, 'src', 'timeline.json'), `${JSON.stringify(timeline, null, 2)}\n`);
fs.writeFileSync(path.join(assets, 'narration_timing.json'), `${JSON.stringify(timeline, null, 2)}\n`);
console.log(JSON.stringify({ narration, total, segments: timing }, null, 2));
