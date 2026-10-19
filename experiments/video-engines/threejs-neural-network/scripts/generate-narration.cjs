const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");

const root = path.resolve(__dirname, "..");
const packageRoot = process.env.KOKORO_PACKAGE || "/Users/rajeev/Code/content-machine/package.json";
const req = createRequire(packageRoot);
const { KokoroTTS } = req("kokoro-js");
const { RawAudio } = req("@huggingface/transformers");

const MODEL_CACHE = "/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX";
const VOICE_FILE = "/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin";

async function main() {
  if (!fs.existsSync(MODEL_CACHE) || !fs.existsSync(VOICE_FILE)) {
    throw new Error("Required installed Kokoro cache or bf_emma voice is missing; refusing to download weights.");
  }

  const script = JSON.parse(fs.readFileSync(path.join(root, "script.json"), "utf8"));
  const tts = await KokoroTTS.from_pretrained("onnx-community/Kokoro-82M-v1.0-ONNX", {
    dtype: "q8",
    local_files_only: true,
  });

  const sampleRate = 24000;
  const chunks = [new Float32Array(Math.round(0.2 * sampleRate))];
  const cues = [];
  let cursor = chunks[0].length;

  for (let index = 0; index < script.lines.length; index += 1) {
    const line = script.lines[index];
    const generated = await tts.generate(line.text, {
      voice: script.voice || "bf_emma",
      speed: script.speed || 0.96,
    });
    const samples = generated.audio;
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.008;
    while (first < last && Math.abs(samples[first]) < threshold) first += 1;
    while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
    first = Math.max(0, first - Math.round(0.065 * sampleRate));
    last = Math.min(samples.length, last + Math.round(0.1 * sampleRate));
    const clean = samples.slice(first, last);
    const start = cursor / sampleRate;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sampleRate;
    cues.push({ ...line, start, end });

    const pauseSeconds = index === script.lines.length - 1 ? 0.62 : index === 1 ? 0.24 : 0.2;
    const pause = new Float32Array(Math.round(pauseSeconds * sampleRate));
    chunks.push(pause);
    cursor += pause.length;
    console.log(`line ${index + 1}/${script.lines.length}: ${start.toFixed(3)}-${end.toFixed(3)}`);
  }

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  const audioDir = path.join(root, "assets", "audio");
  fs.mkdirSync(audioDir, { recursive: true });
  await new RawAudio(merged, sampleRate).save(path.join(audioDir, "narration-raw.wav"));
  fs.writeFileSync(
    path.join(audioDir, "timing.json"),
    `${JSON.stringify({ voice: script.voice, speed: script.speed, sampleRate, duration: cursor / sampleRate, cues }, null, 2)}\n`,
  );
  console.log(`narration duration: ${(cursor / sampleRate).toFixed(3)}s`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
