#!/usr/bin/env node
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const sharedRequire = createRequire(
  "/Users/rajeev/Code/content-machine/package.json",
);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SHARED_NODE_MODULES = "/Users/rajeev/Code/content-machine/node_modules";
const MODEL_DIR =
  "/Users/rajeev/Code/content-machine/node_modules/@huggingface/transformers/.cache/onnx-community/Kokoro-82M-v1.0-ONNX";
const VOICE_PATH =
  "/Users/rajeev/Code/content-machine/node_modules/kokoro-js/voices/bf_emma.bin";
const OUTPUT_DIR = path.join(ROOT, ".render-tmp", "tts-segments");

const { KokoroTTS } = sharedRequire("kokoro-js");
const transformers = sharedRequire("@huggingface/transformers");

async function main() {
  const narration = JSON.parse(
    await fs.readFile(path.join(ROOT, "src", "narration.json"), "utf8"),
  );
  await fs.access(MODEL_DIR);
  await fs.access(VOICE_PATH);
  await fs.rm(OUTPUT_DIR, { recursive: true, force: true });
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  transformers.env.allowRemoteModels = false;
  transformers.env.allowLocalModels = true;
  transformers.env.useFSCache = false;
  transformers.env.localModelPath = path.dirname(path.dirname(MODEL_DIR));

  const started = performance.now();
  const tts = await KokoroTTS.from_pretrained(
    `onnx-community/${path.basename(MODEL_DIR)}`,
    { dtype: "q8", device: "cpu" },
  );
  const loadMs = Math.round(performance.now() - started);

  for (let index = 0; index < narration.lines.length; index += 1) {
    const line = narration.lines[index];
    const lineStarted = performance.now();
    const audio = await tts.generate(line.text, {
      voice: narration.voice,
      speed: narration.speed,
    });
    const output = path.join(OUTPUT_DIR, `${String(index + 1).padStart(2, "0")}-${line.id}.wav`);
    await audio.save(output);
    console.log(
      `${line.id}: ${Math.round(performance.now() - lineStarted)} ms -> ${path.relative(ROOT, output)}`,
    );
  }

  console.log(`Kokoro q8 model load: ${loadMs} ms`);
  console.log(`Segments: ${narration.lines.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
