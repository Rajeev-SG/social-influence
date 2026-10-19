// Generate the benchmark narration with the already-installed Kokoro 82M q8
// ONNX setup. This intentionally refuses remote model loading.
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');

const ROOT = path.resolve(__dirname, '..');
const MODEL_CACHE =
  '/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX';
const VOICE_PATH =
  '/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin';
const PACKAGE_ROOT =
  process.env.KOKORO_PACKAGE || '/Users/rajeev/Code/content-machine/package.json';
const req = createRequire(PACKAGE_ROOT);
const {KokoroTTS} = req('kokoro-js');
const transformers = req('@huggingface/transformers');
const {RawAudio} = transformers;

const sha256 = (file) =>
  crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

if (!fs.existsSync(path.join(MODEL_CACHE, 'config.json'))) {
  throw new Error(`Kokoro cache missing: ${MODEL_CACHE}`);
}
if (!fs.existsSync(VOICE_PATH)) {
  throw new Error(`Kokoro voice missing: ${VOICE_PATH}`);
}

const installedVoice = path.join(
  path.dirname(path.dirname(req.resolve('kokoro-js'))),
  'voices',
  'bf_emma.bin',
);
if (!fs.existsSync(installedVoice) || sha256(installedVoice) !== sha256(VOICE_PATH)) {
  throw new Error('The requested bf_emma voice path does not match the installed Kokoro voice.');
}

transformers.env.localFilesOnly = true;
transformers.env.allowLocalModels = true;

(async () => {
  const tts = await KokoroTTS.from_pretrained(
    'onnx-community/Kokoro-82M-v1.0-ONNX',
    {dtype: 'q8', device: 'cpu', local_files_only: true},
  );
  const script = JSON.parse(fs.readFileSync(path.join(ROOT, 'script.json'), 'utf8'));
  const sr = 24000;
  const lead = Math.round(0.22 * sr);
  let cursor = lead;
  const chunks = [new Float32Array(lead)];
  const cues = [];
  fs.mkdirSync(path.join(ROOT, 'assets/audio'), {recursive: true});

  for (let i = 0; i < script.length; i += 1) {
    const audio = await tts.generate(script[i].text, {
      voice: 'bf_emma',
      speed: 0.94,
    });
    const samples = audio.audio;
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.009;
    while (first < last && Math.abs(samples[first]) < threshold) first += 1;
    while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
    first = Math.max(0, first - Math.round(0.065 * sr));
    last = Math.min(samples.length, last + Math.round(0.095 * sr));
    const clean = samples.slice(first, last);
    const start = cursor / sr;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sr;
    cues.push({
      ...script[i],
      start,
      end,
      file: `assets/audio/line-${i}.wav`,
    });
    await audio.save(path.join(ROOT, `assets/audio/line-${i}.wav`));

    const pause = i === 3 ? 0.34 : i === 4 ? 0.44 : i === 5 ? 1.05 : 0.24;
    chunks.push(new Float32Array(Math.round(pause * sr)));
    cursor += Math.round(pause * sr);
    process.stdout.write(
      `${i + 1}/${script.length} ${script[i].scene} ${start.toFixed(3)}-${end.toFixed(3)}\n`,
    );
  }

  // Pad to an exact 30 fps frame count so visual cues and media duration align.
  const fps = 30;
  const frameCount = Math.ceil((cursor / sr) * fps);
  cursor = Math.round((frameCount / fps) * sr);
  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  await new RawAudio(merged, sr).save(
    path.join(ROOT, 'assets/audio/narration-raw.wav'),
  );
  fs.writeFileSync(
    path.join(ROOT, 'src/timing.json'),
    `${JSON.stringify(
      {
        fps,
        frame_count: frameCount,
        duration: cursor / sr,
        voice: 'bf_emma',
        voice_path: VOICE_PATH,
        voice_sha256: sha256(VOICE_PATH),
        model_cache: MODEL_CACHE,
        cues,
      },
      null,
      2,
    )}\n`,
  );
  process.stdout.write(
    `Wrote ${frameCount} frames / ${(cursor / sr).toFixed(3)} seconds.\n`,
  );
})();
