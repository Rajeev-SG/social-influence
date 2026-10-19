import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { KokoroTTS } from "/Users/rajeev/Code/content-machine/node_modules/kokoro-js/dist/kokoro.js";
import { env } from "/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/dist/transformers.node.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = path.join(root, "assets", "audio");
const modelDir = "/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX";
const script = JSON.parse(await fs.readFile(path.join(root, "src", "script.json"), "utf8"));

await fs.mkdir(outDir, { recursive: true });
env.allowRemoteModels = false;
env.allowLocalModels = true;
env.useFSCache = false;
env.useBrowserCache = false;

const started = Date.now();
const tts = await KokoroTTS.from_pretrained(modelDir, { dtype: "q8", device: "cpu" });
const timing = [];

for (const item of script.narration) {
  const audio = await tts.generate(item.text, { voice: "bf_emma", speed: 1.02 });
  const file = path.join(outDir, `${item.id}.wav`);
  await audio.save(file);
  const sampleRate = audio.sampling_rate || 24000;
  const duration = audio.audio.length / sampleRate;
  timing.push({ ...item, file: path.relative(root, file), duration });
}

await fs.writeFile(path.join(outDir, "timing.json"), `${JSON.stringify({ voice: "bf_emma", modelDir, sampleRate: 24000, timing }, null, 2)}\n`);

function writeWav(file, channels, sampleRate) {
  const frames = channels[0].length;
  const dataLength = frames * channels.length * 2;
  const buffer = Buffer.alloc(44 + dataLength);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(channels.length, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * channels.length * 2, 28);
  buffer.writeUInt16LE(channels.length * 2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataLength, 40);
  let offset = 44;
  for (let i = 0; i < frames; i++) {
    for (const channel of channels) {
      buffer.writeInt16LE(Math.max(-32768, Math.min(32767, Math.round(channel[i] * 32767))), offset);
      offset += 2;
    }
  }
  return fs.writeFile(file, buffer);
}

const effectRate = 48000;
const effectFrames = Math.round(script.duration_seconds * effectRate);
const left = new Float32Array(effectFrames);
const right = new Float32Array(effectFrames);
let seed = 91731;
const random = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296 * 2 - 1;
};
for (let i = 0; i < effectFrames; i++) {
  const t = i / effectRate;
  const hum = 0.014 * Math.sin(2 * Math.PI * 47 * t) + 0.006 * Math.sin(2 * Math.PI * 94 * t + 0.4);
  const shimmer = 0.0025 * Math.sin(2 * Math.PI * 188 * t) * (0.5 + 0.5 * Math.sin(t * 0.7));
  left[i] += hum + shimmer;
  right[i] += hum * 0.96 + shimmer * 1.04;
}
for (const start of [0.45, 3.55, 7.75, 12.65, 16.55]) {
  const begin = Math.round(start * effectRate);
  for (let j = 0; j < Math.round(0.055 * effectRate); j++) {
    const i = begin + j;
    if (i >= effectFrames) break;
    const env = Math.exp(-j / (0.010 * effectRate));
    const click = env * (0.035 * Math.sin(2 * Math.PI * 820 * j / effectRate) + 0.012 * random());
    left[i] += click * 0.95;
    right[i] += click;
  }
}
for (const start of [7.95, 12.85, 17.0]) {
  const begin = Math.round(start * effectRate);
  for (let j = 0; j < Math.round(0.42 * effectRate); j++) {
    const i = begin + j;
    if (i >= effectFrames) break;
    const p = j / (0.42 * effectRate);
    const env = Math.sin(Math.PI * p) * 0.024;
    const data = env * (random() * 0.55 + 0.45 * Math.sin(2 * Math.PI * (260 + 440 * p) * j / effectRate));
    left[i] += data * (1 - p * 0.55);
    right[i] += data * (0.45 + p * 0.55);
  }
}
await writeWav(path.join(outDir, "effects.wav"), [left, right], effectRate);

console.log(JSON.stringify({
  elapsedMs: Date.now() - started,
  clips: timing.map(({ id, duration }) => ({ id, duration })),
  effects: { file: "assets/audio/effects.wav", duration: script.duration_seconds, sampleRate: effectRate, channels: 2 },
}, null, 2));
