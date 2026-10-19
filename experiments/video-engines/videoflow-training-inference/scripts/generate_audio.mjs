import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(SCRIPT_DIR, "..");
const CONTENT_MACHINE = "/Users/rajeev/Code/content-machine";
const MODEL_DIR = path.join(
  CONTENT_MACHINE,
  "node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX",
);
const VOICE_PATH = path.join(
  CONTENT_MACHINE,
  "node_modules/kokoro-js/voices/bf_emma.bin",
);
const OUTPUT_DIR = path.join(ROOT, "assets", "audio");

for (const required of [MODEL_DIR, VOICE_PATH]) {
  if (!fs.existsSync(required)) {
    throw new Error(`Required local Kokoro artifact is missing: ${required}`);
  }
}

const requireFromContentMachine = createRequire(
  path.join(CONTENT_MACHINE, "package.json"),
);
const { KokoroTTS } = requireFromContentMachine("kokoro-js");
const transformers = requireFromContentMachine("@huggingface/transformers");
transformers.env.allowRemoteModels = false;
transformers.env.allowLocalModels = true;

const project = JSON.parse(
  fs.readFileSync(path.join(ROOT, "src", "project.json"), "utf8"),
);
const linePaths = [];
const lines = [];
let sampleRate = 24000;
let cursor = Number(project.lead_seconds);

fs.mkdirSync(OUTPUT_DIR, { recursive: true });
const ttsStarted = Date.now();
console.log("loading", MODEL_DIR);
const tts = await KokoroTTS.from_pretrained(MODEL_DIR, { dtype: "q8" });
console.log("loaded", Date.now() - ttsStarted, "ms");

for (let index = 0; index < project.narration.length; index += 1) {
  const item = project.narration[index];
  const started = Date.now();
  console.log("synthesizing", index + 1, item.id);
  const audio = await tts.generate(item.text, {
    voice: project.voice,
    speed: project.speed,
  });
  console.log("generated", index + 1, audio.audio.length, audio.sampling_rate);
  sampleRate = audio.sampling_rate;
  const linePath = path.join(OUTPUT_DIR, `line-${String(index + 1).padStart(2, "0")}.wav`);
  await audio.save(linePath);
  console.log("saved", index + 1, linePath);
  const duration = audio.audio.length / audio.sampling_rate;
  const pause = Number(project.pauses_seconds[index] ?? 0);
  lines.push({
    ...item,
    start: Number(cursor.toFixed(4)),
    end: Number((cursor + duration).toFixed(4)),
    duration: Number(duration.toFixed(4)),
    path: path.relative(ROOT, linePath),
    synthesis_ms: Date.now() - started,
  });
  linePaths.push(linePath);
  cursor += duration + pause;
}

const rawTotal = cursor + Number(project.tail_seconds);
const fps = Number(project.fps);
const totalFrames = Math.ceil(rawTotal * fps);
const totalDuration = totalFrames / fps;
const lastLineEnd = lines.at(-1).end;
const introEnd = Math.min(lines[0].end, lines[0].start + 2.72);
const trainingEnd = lines[1].end + 0.36;
const transitionEnd = lines[2].end + 0.12;
const inferenceEnd = lines[3].end + 0.18;
const scenes = [
  { id: "intro", start: 0, end: Number(introEnd.toFixed(4)) },
  {
    id: "training",
    start: Number(introEnd.toFixed(4)),
    end: Number(trainingEnd.toFixed(4)),
  },
  {
    id: "transition",
    start: Number(trainingEnd.toFixed(4)),
    end: Number(transitionEnd.toFixed(4)),
  },
  {
    id: "inference",
    start: Number(transitionEnd.toFixed(4)),
    end: Number(inferenceEnd.toFixed(4)),
  },
  {
    id: "outro",
    start: Number(inferenceEnd.toFixed(4)),
    end: Number(totalDuration.toFixed(4)),
  },
];

const timing = {
  fps,
  width: project.width,
  height: project.height,
  sample_rate: sampleRate,
  voice: project.voice,
  voice_path: VOICE_PATH,
  model_path: MODEL_DIR,
  kokoro_js_version: JSON.parse(
    fs.readFileSync(
      path.join(CONTENT_MACHINE, "node_modules/kokoro-js/package.json"),
      "utf8",
    ),
  ).version,
  lead_seconds: project.lead_seconds,
  tail_seconds: project.tail_seconds,
  pauses_seconds: project.pauses_seconds,
  lines,
  scenes,
  sound_events: [
    {
      id: "training-ticks",
      at: Number((scenes[1].start + 0.32).toFixed(4)),
      gain: 0.18,
    },
    {
      id: "lock-click",
      at: Number((scenes[2].end - 0.24).toFixed(4)),
      gain: 0.24,
    },
    {
      id: "resolve-chime",
      at: Number((scenes[4].start + 0.08).toFixed(4)),
      gain: 0.17,
    },
  ],
  last_line_end: lastLineEnd,
  raw_duration_before_frame_alignment: Number(rawTotal.toFixed(4)),
  total_frames: totalFrames,
  total_duration: Number(totalDuration.toFixed(4)),
  tts_total_ms: Date.now() - ttsStarted,
};

fs.writeFileSync(
  path.join(OUTPUT_DIR, "timing.json"),
  `${JSON.stringify(timing, null, 2)}\n`,
);
console.log(
  JSON.stringify(
    {
      lines: lines.map(({ id, start, end, duration, synthesis_ms }) => ({
        id,
        start,
        end,
        duration,
        synthesis_ms,
      })),
      total_duration: timing.total_duration,
      total_frames: timing.total_frames,
      tts_total_ms: timing.tts_total_ms,
    },
    null,
    2,
  ),
);
