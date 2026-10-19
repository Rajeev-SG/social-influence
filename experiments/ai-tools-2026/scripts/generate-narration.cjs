const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");

const projectRoot = path.resolve(__dirname, "..");
const requireFromContentMachine = createRequire(
  process.env.KOKORO_PACKAGE || "/Users/rajeev/Code/content-machine/package.json",
);
const { KokoroTTS } = requireFromContentMachine("kokoro-js");
const { RawAudio } = requireFromContentMachine("@huggingface/transformers");

const outputDir = path.join(projectRoot, "narration");
const lineDir = path.join(outputDir, "lines");

function trimSilence(samples, threshold = 0.009) {
  let first = 0;
  let last = samples.length - 1;
  while (first < last && Math.abs(samples[first]) < threshold) first += 1;
  while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
  first = Math.max(0, first - Math.round(0.08 * 24000));
  last = Math.min(samples.length, last + Math.round(0.14 * 24000));
  return samples.slice(first, last);
}

(async () => {
  fs.mkdirSync(lineDir, { recursive: true });
  const script = JSON.parse(
    fs.readFileSync(path.join(projectRoot, "script.json"), "utf8"),
  );
  const tts = await KokoroTTS.from_pretrained(
    "onnx-community/Kokoro-82M-v1.0-ONNX",
    { dtype: "q8", local_files_only: true },
  );

  const sampleRate = 24000;
  const chunks = [new Float32Array(Math.round(0.32 * sampleRate))];
  const cues = [];
  let cursor = chunks[0].length;

  for (const line of script) {
    const result = await tts.generate(line.text, {
      voice: "bf_emma",
      speed: 1.11,
    });
    const samples = trimSilence(result.audio);
    const start = cursor / sampleRate;
    chunks.push(samples);
    cursor += samples.length;
    const end = cursor / sampleRate;
    const linePath = path.join(lineDir, `${String(line.id).padStart(2, "0")}.wav`);
    await result.save(linePath);
    cues.push({ ...line, start, end, file: path.relative(outputDir, linePath) });

    const pauseSeconds =
      line.id === 1 ? 0.72 :
      line.id === 3 ? 0.62 :
      line.id === 7 ? 0.78 :
      line.id === 8 ? 0.70 :
      line.id === 9 ? 0.90 :
      0.42;
    const pause = new Float32Array(Math.round(pauseSeconds * sampleRate));
    chunks.push(pause);
    cursor += pause.length;
  }

  chunks.push(new Float32Array(Math.round(0.55 * sampleRate)));
  cursor += chunks[chunks.length - 1].length;

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }

  await new RawAudio(merged, sampleRate).save(
    path.join(outputDir, "narration.wav"),
  );
  fs.writeFileSync(
    path.join(outputDir, "timing.json"),
    JSON.stringify({ sampleRate, duration: cursor / sampleRate, cues }, null, 2),
  );
  console.log(JSON.stringify({ duration: cursor / sampleRate, cues }, null, 2));
})();
