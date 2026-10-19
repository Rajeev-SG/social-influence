// Generate the complete voiceover from the already-installed Kokoro 82M q8 ONNX
// cache. This script never downloads model or voice weights.
const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");

const root = path.resolve(__dirname, "..");
const packageRoot = process.env.KOKORO_PACKAGE || "/Users/rajeev/Code/content-machine/package.json";
const req = createRequire(packageRoot);
const { KokoroTTS } = req("kokoro-js");
const { RawAudio } = req("@huggingface/transformers");

const expectedVoice = "/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin";
const resolvedPackage = req.resolve("kokoro-js");
const resolvedVoice = path.resolve(path.dirname(resolvedPackage), "../voices/bf_emma.bin");
if (resolvedVoice !== expectedVoice || !fs.existsSync(expectedVoice)) {
  throw new Error(`Kokoro voice mismatch: expected ${expectedVoice}, resolved ${resolvedVoice}`);
}

const script = JSON.parse(fs.readFileSync(path.join(root, "assets/script.json"), "utf8"));
const audioDir = path.join(root, "assets/audio");
fs.mkdirSync(audioDir, { recursive: true });

(async () => {
  const tts = await KokoroTTS.from_pretrained("onnx-community/Kokoro-82M-v1.0-ONNX", {
    dtype: "q8",
    device: "cpu",
    local_files_only: true,
  });

  const sampleRate = 24000;
  let cursor = Math.round(0.24 * sampleRate);
  const chunks = [new Float32Array(cursor)];
  const cues = [];

  for (let i = 0; i < script.length; i += 1) {
    const line = script[i];
    const audio = await tts.generate(line.text, { voice: "bf_emma", speed: 0.98 });
    const samples = audio.audio;

    // Remove model padding while preserving a short breathing margin.
    let first = 0;
    let last = samples.length - 1;
    const threshold = 0.009;
    while (first < last && Math.abs(samples[first]) < threshold) first += 1;
    while (last > first && Math.abs(samples[last]) < threshold) last -= 1;
    first = Math.max(0, first - Math.round(0.055 * sampleRate));
    last = Math.min(samples.length, last + Math.round(0.085 * sampleRate));

    const clean = samples.slice(first, last);
    const start = cursor / sampleRate;
    chunks.push(clean);
    cursor += clean.length;
    const end = cursor / sampleRate;

    await audio.save(path.join(audioDir, `line-${i}.wav`));
    cues.push({ ...line, start, end, file: `audio/line-${i}.wav` });

    const pauseSeconds = i === script.length - 1 ? 0.78 : i === 1 ? 0.34 : 0.25;
    const pause = new Float32Array(Math.round(pauseSeconds * sampleRate));
    chunks.push(pause);
    cursor += pause.length;
    process.stdout.write(`${i + 1}/${script.length} ${line.scene} ${start.toFixed(3)}-${end.toFixed(3)}s\n`);
  }

  const merged = new Float32Array(cursor);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  await new RawAudio(merged, sampleRate).save(path.join(audioDir, "narration-raw.wav"));

  fs.writeFileSync(
    path.join(root, "src/timing.json"),
    `${JSON.stringify({ duration: cursor / sampleRate, sampleRate, voice: expectedVoice, cues }, null, 2)}\n`,
  );

  const srtTime = (seconds) => {
    const ms = Math.round(seconds * 1000);
    const hours = String(Math.floor(ms / 3600000)).padStart(2, "0");
    const minutes = String(Math.floor((ms % 3600000) / 60000)).padStart(2, "0");
    const secs = String(Math.floor((ms % 60000) / 1000)).padStart(2, "0");
    const millis = String(ms % 1000).padStart(3, "0");
    return `${hours}:${minutes}:${secs},${millis}`;
  };
  fs.writeFileSync(
    path.join(root, "assets/captions.srt"),
    `${cues.map((cue, i) => `${i + 1}\n${srtTime(cue.start)} --> ${srtTime(cue.end)}\n${cue.text}\n`).join("\n")}\n`,
  );
})();
