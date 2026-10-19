// Generate the complete voiceover from the already-installed Kokoro 82M q8 ONNX cache.
// This script refuses to download model or voice weights.
const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");

const root = path.resolve(__dirname, "..");
const packageRoot = process.env.KOKORO_PACKAGE || "/Users/rajeev/Code/content-machine/package.json";
const req = createRequire(packageRoot);
const { KokoroTTS } = req("kokoro-js");
const { RawAudio } = req("@huggingface/transformers");

const MODEL_CACHE =
  "/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX";
const EXPECTED_VOICE = "/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin";
const resolvedPackage = req.resolve("kokoro-js");
const resolvedVoice = path.resolve(path.dirname(resolvedPackage), "../voices/bf_emma.bin");

if (!fs.existsSync(MODEL_CACHE) || !fs.existsSync(path.join(MODEL_CACHE, "onnx", "model_quantized.onnx"))) {
  throw new Error(`Missing installed Kokoro cache at ${MODEL_CACHE}; refusing to download weights.`);
}
if (resolvedVoice !== EXPECTED_VOICE || !fs.existsSync(EXPECTED_VOICE)) {
  throw new Error(`Kokoro voice mismatch: expected ${EXPECTED_VOICE}, resolved ${resolvedVoice}`);
}

function normalize(samples, targetPeak = 0.86) {
  let peak = 0;
  for (const sample of samples) peak = Math.max(peak, Math.abs(sample));
  if (peak === 0) return samples;
  const gain = targetPeak / peak;
  return Float32Array.from(samples, (sample) => sample * gain);
}

async function main() {
  const script = JSON.parse(fs.readFileSync(path.join(root, "src", "script.json"), "utf8"));
  const tts = await KokoroTTS.from_pretrained("onnx-community/Kokoro-82M-v1.0-ONNX", {
    dtype: "q8",
    device: "cpu",
    local_files_only: true,
  });

  const sampleRate = script.sampleRate;
  const chunks = [new Float32Array(Math.round(0.22 * sampleRate))];
  const cues = [];
  let cursor = chunks[0].length;

  for (let index = 0; index < script.lines.length; index += 1) {
    const line = script.lines[index];
    const generated = await tts.generate(line.text, {
      voice: script.voice,
      speed: script.speed,
    });
    const samples = normalize(generated.audio);
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.008;
    while (first < last && Math.abs(samples[first]) < threshold) first += 1;
    while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
    first = Math.max(0, first - Math.round(0.055 * sampleRate));
    last = Math.min(samples.length, last + Math.round(0.11 * sampleRate));
    const clean = samples.slice(first, last);
    const start = cursor / sampleRate;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sampleRate;
    cues.push({ ...line, start, end, samples: clean.length });

    const pauseSeconds = index === script.lines.length - 1 ? 0.68 : index === 1 ? 0.3 : 0.22;
    chunks.push(new Float32Array(Math.round(pauseSeconds * sampleRate)));
    cursor += chunks[chunks.length - 1].length;
    process.stdout.write(
      `line ${index + 1}/${script.lines.length} ${line.scene} ${start.toFixed(3)}-${end.toFixed(3)}s\n`,
    );
  }

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  const audioDir = path.join(root, "assets", "audio");
  fs.mkdirSync(audioDir, { recursive: true });
  await new RawAudio(merged, sampleRate).save(path.join(audioDir, "narration.wav"));
  fs.writeFileSync(
    path.join(root, "src", "timing.json"),
    `${JSON.stringify(
      {
        topic: script.topic,
        voice: EXPECTED_VOICE,
        voiceName: script.voice,
        speed: script.speed,
        sampleRate,
        duration: cursor / sampleRate,
        cues,
      },
      null,
      2,
    )}\n`,
  );
  process.stdout.write(`narration duration: ${(cursor / sampleRate).toFixed(3)}s\n`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
