// Reuse the installed Kokoro 82M q8 ONNX runtime and cache. Never download weights.
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

const root = path.resolve(__dirname, '..');
const packageRoot = process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json';
const req = createRequire(packageRoot);
const { KokoroTTS } = req('kokoro-js');
const { RawAudio } = req('@huggingface/transformers');

const OUT_DIR = path.join(root, 'assets', 'audio');
const TMP_DIR = path.join(OUT_DIR, '.tts-tmp');

(async () => {
  fs.mkdirSync(TMP_DIR, { recursive: true });
  const tts = await KokoroTTS.from_pretrained(
    'onnx-community/Kokoro-82M-v1.0-ONNX',
    { dtype: 'q8', device: 'cpu', local_files_only: true },
  );

  const script = JSON.parse(fs.readFileSync(path.join(root, 'src', 'script.json'), 'utf8'));
  const sampleRate = 24000;
  let cursor = Math.round(0.24 * sampleRate);
  const chunks = [new Float32Array(cursor)];
  const cues = [];

  for (let index = 0; index < script.length; index += 1) {
    const item = script[index];
    const audio = await tts.generate(item.text, { voice: 'bf_emma', speed: 0.96 });
    const samples = audio.audio;

    // Trim Kokoro's padded silence while retaining a natural breath margin.
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.009;
    while (first < last && Math.abs(samples[first]) < threshold) first += 1;
    while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
    first = Math.max(0, first - Math.round(0.065 * sampleRate));
    last = Math.min(samples.length, last + Math.round(0.085 * sampleRate));

    const clean = samples.slice(first, last);
    const start = cursor / sampleRate;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sampleRate;
    cues.push({ ...item, start, end });

    await audio.save(path.join(TMP_DIR, `line-${index}.wav`));
    const pauseSeconds = index === script.length - 1 ? 0.72 : index === 3 ? 0.34 : 0.24;
    chunks.push(new Float32Array(Math.round(pauseSeconds * sampleRate)));
    cursor += Math.round(pauseSeconds * sampleRate);
    process.stdout.write(`${index + 1}/${script.length} ${start.toFixed(3)}-${end.toFixed(3)}\n`);
  }

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  await new RawAudio(merged, sampleRate).save(path.join(OUT_DIR, 'narration-raw.wav'));
  fs.writeFileSync(
    path.join(root, 'src', 'timing.json'),
    `${JSON.stringify({ duration: cursor / sampleRate, sampleRate, cues }, null, 2)}\n`,
  );
})();

