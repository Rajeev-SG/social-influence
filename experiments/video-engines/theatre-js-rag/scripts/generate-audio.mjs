import { execFile } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { promisify } from "node:util";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const execFileAsync = promisify(execFile);
const root = resolve(import.meta.dirname, "..");
const assets = resolve(root, "assets");
const work = resolve(root, ".render-tmp", "audio-work");
const modelDir =
  "/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX";
const kokoroModule =
  "/Users/rajeev/Code/content-machine/node_modules/kokoro-js/dist/kokoro.js";
const script = JSON.parse(await readFile(resolve(root, "src/script.json"), "utf8"));

async function ffmpeg(args) {
  return execFileAsync("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", ...args], {
    maxBuffer: 1024 * 1024 * 16,
  });
}

async function probeDuration(file) {
  const { stdout } = await execFileAsync("ffprobe", [
    "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=nw=1:nk=1",
    file,
  ]);
  return Number(stdout.trim());
}

function writeWav(path, samples, sampleRate = 48000) {
  const channels = 2;
  const bytesPerSample = 2;
  const dataLength = samples.length * channels * bytesPerSample;
  const buffer = Buffer.alloc(44 + dataLength);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(channels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * channels * bytesPerSample, 28);
  buffer.writeUInt16LE(channels * bytesPerSample, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataLength, 40);
  for (let index = 0; index < samples.length; index += 1) {
    const value = Math.max(-1, Math.min(1, samples[index]));
    const pcm = Math.round(value * 32767);
    buffer.writeInt16LE(pcm, 44 + index * 4);
    buffer.writeInt16LE(pcm, 46 + index * 4);
  }
  return writeFile(path, buffer);
}

function synthesiseSoundDesign(durationSeconds = script.durationSeconds) {
  const sampleRate = 48000;
  const samples = new Float32Array(Math.ceil(durationSeconds * sampleRate));

  for (let i = 0; i < samples.length; i += 1) {
    const time = i / sampleRate;
    const slowPulse = 0.6 + 0.4 * Math.sin(time * Math.PI * 0.24);
    samples[i] +=
      0.006 * slowPulse * Math.sin(2 * Math.PI * 82.41 * time) +
      0.004 * slowPulse * Math.sin(2 * Math.PI * 123.47 * time);
  }

  const addChime = (time, baseFrequency, amplitude = 0.045) => {
    const start = Math.floor(time * sampleRate);
    const length = Math.floor(0.72 * sampleRate);
    for (let i = 0; i < length && start + i < samples.length; i += 1) {
      const t = i / sampleRate;
      const envelope = Math.exp(-7.2 * t) * Math.min(1, t * 90);
      samples[start + i] += amplitude * envelope * (
        Math.sin(2 * Math.PI * baseFrequency * t) +
        0.38 * Math.sin(2 * Math.PI * baseFrequency * 1.5 * t)
      );
    }
  };

  const addWhoosh = (time, amplitude = 0.032) => {
    const start = Math.floor(time * sampleRate);
    const length = Math.floor(0.42 * sampleRate);
    let low = 0;
    let seed = 271828;
    for (let i = 0; i < length && start + i < samples.length; i += 1) {
      const t = i / length;
      seed = (seed * 1664525 + 1013904223) >>> 0;
      const noise = (seed / 4294967296) * 2 - 1;
      low += 0.075 * (noise - low);
      const envelope = Math.sin(Math.PI * t) ** 2;
      samples[start + i] += amplitude * envelope * low;
    }
  };

  const addTick = (time, amplitude = 0.028) => {
    const start = Math.floor(time * sampleRate);
    const length = Math.floor(0.08 * sampleRate);
    for (let i = 0; i < length && start + i < samples.length; i += 1) {
      const t = i / sampleRate;
      samples[start + i] += amplitude * Math.exp(-52 * t) * Math.sin(2 * Math.PI * 920 * t);
    }
  };

  addChime(0.12, 659.25, 0.052);
  addWhoosh(2.28, 0.025);
  addChime(2.48, 523.25, 0.032);
  addWhoosh(7.12, 0.034);
  addChime(7.35, 783.99, 0.038);
  addTick(10.15);
  addTick(10.52, 0.023);
  addTick(10.9, 0.026);
  addWhoosh(12.58, 0.030);
  addChime(12.82, 698.46, 0.038);
  addTick(15.15, 0.022);
  addWhoosh(16.98, 0.028);
  addChime(17.24, 880, 0.043);
  addChime(20.82, 659.25, 0.055);

  return samples;
}

await rm(work, { recursive: true, force: true });
await mkdir(work, { recursive: true });
await mkdir(assets, { recursive: true });

const started = Date.now();
const { KokoroTTS } = await import(pathToFileURL(kokoroModule).href);
const tts = await KokoroTTS.from_pretrained(modelDir, { dtype: "q8" });
console.log(`Loaded local ${modelDir} with bf_emma.`);

const preparedSegments = [];
for (let index = 0; index < script.segments.length; index += 1) {
  const segment = script.segments[index];
  const rawPath = resolve(work, `raw-${index}.wav`);
  const preparedPath = resolve(work, `prepared-${index}.wav`);
  const audio = await tts.generate(segment.spoken, { voice: "bf_emma", speed: 1.08 });
  await writeFile(rawPath, Buffer.from(audio.toWav()));

  const rawDuration = await probeDuration(rawPath);
  const targetDuration = segment.end - segment.start - 0.12;
  const tempo = Math.min(1.45, Math.max(1, rawDuration / targetDuration));
  await ffmpeg([
    "-i", rawPath,
    "-af",
    `aresample=48000,atempo=${tempo.toFixed(6)},highpass=f=85,lowpass=f=12000,volume=1.18,alimiter=limit=0.82`,
    "-ac", "2",
    preparedPath,
  ]);
  const preparedDuration = await probeDuration(preparedPath);
  preparedSegments.push({ ...segment, rawDuration, preparedDuration, tempo });
  console.log(
    `Segment ${index + 1}/${script.segments.length}: ${rawDuration.toFixed(3)}s raw, ` +
    `${preparedDuration.toFixed(3)}s prepared, atempo ${tempo.toFixed(3)}.`,
  );
}

const narrationPath = resolve(assets, "narration.wav");
const narrationInputs = ["-f", "lavfi", "-t", String(script.durationSeconds), "-i", "anullsrc=r=48000:cl=stereo"];
const filters = [];
for (let index = 0; index < preparedSegments.length; index += 1) {
  narrationInputs.push("-i", resolve(work, `prepared-${index}.wav`));
  const delay = Math.round(preparedSegments[index].start * 1000);
  filters.push(`[${index + 1}:a]adelay=${delay}|${delay}[voice${index}]`);
}
const voiceLabels = preparedSegments.map((_, index) => `[voice${index}]`).join("");
filters.push(
  `[0:a]${voiceLabels}amix=inputs=${preparedSegments.length + 1}:duration=first:normalize=0,` +
  "volume=1.12,alimiter=limit=0.84[a]",
);
await ffmpeg([
  ...narrationInputs,
  "-filter_complex", filters.join(";"),
  "-map", "[a]",
  "-t", String(script.durationSeconds),
  "-ac", "2",
  "-ar", "48000",
  "-c:a", "pcm_s16le",
  narrationPath,
]);

const soundDesignPath = resolve(assets, "sound-design.wav");
await writeWav(soundDesignPath, synthesiseSoundDesign());
const narrationDuration = await probeDuration(narrationPath);
const soundDuration = await probeDuration(soundDesignPath);
await rm(work, { recursive: true, force: true });

console.log(
  `Generated narration (${narrationDuration.toFixed(3)}s) and sound design ` +
  `(${soundDuration.toFixed(3)}s) in ${((Date.now() - started) / 1000).toFixed(2)}s.`,
);
