#!/usr/bin/env node
// Render the Canvas scene system and encode/mux the MP4 with Mediabunny + WebCodecs.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const contentMachinePackage = process.env.KOKORO_PACKAGE || "/Users/rajeev/Code/content-machine/package.json";
const req = createRequire(contentMachinePackage);
const { chromium } = req("playwright");

const MEDIA_BUNNY_BUNDLE =
  "/Users/rajeev/Code/content-machine/node_modules/mediabunny/dist/bundles/mediabunny.mjs";
const INDEX_FILE = path.join(root, "src", "index.html");
const TIMING_FILE = path.join(root, "src", "timing.json");
const MIX_FILE = path.join(root, "assets", "audio", "mix.wav");

const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  if (process.argv[index]?.startsWith("--")) args.set(process.argv[index].slice(2), process.argv[index + 1]);
}
const outputFile = path.resolve(root, args.get("out") || "deliverables/final.mp4");
const label = args.get("label") || "render";

function readWavStereo(file) {
  const buffer = fs.readFileSync(file);
  const view = new DataView(buffer.buffer, buffer.byteOffset, buffer.byteLength);
  const riff = view.getUint32(0, true);
  const wave = view.getUint32(8, true);
  if (riff !== 0x46464952 || wave !== 0x45564157) throw new Error("mix.wav is not a RIFF/WAVE file");
  let offset = 12;
  let format = null;
  let data = null;
  while (offset + 8 <= buffer.length) {
    const id = view.getUint32(offset, true);
    const size = view.getUint32(offset + 4, true);
    const body = offset + 8;
    if (id === 0x20746d66) {
      format = {
        channels: view.getUint16(body + 2, true),
        sampleRate: view.getUint32(body + 4, true),
        bits: view.getUint16(body + 14, true),
      };
    } else if (id === 0x61746164) {
      data = { offset: body, size };
    }
    offset = body + size + (size % 2);
  }
  if (!format || !data || format.channels !== 2 || format.bits !== 16) {
    throw new Error("mix.wav must be stereo 16-bit PCM");
  }
  const frames = data.size / 4;
  const left = new Float32Array(frames);
  const right = new Float32Array(frames);
  for (let index = 0; index < frames; index += 1) {
    left[index] = view.getInt16(data.offset + index * 4, true) / 32768;
    right[index] = view.getInt16(data.offset + index * 4 + 2, true) / 32768;
  }
  return { left, right, sampleRate: format.sampleRate };
}

function bytesToBase64(bytes) {
  let binary = "";
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, Math.min(bytes.length, index + chunkSize)));
  }
  return btoa(binary);
}

async function main() {
  const started = Date.now();
  const timing = JSON.parse(fs.readFileSync(TIMING_FILE, "utf8"));
  const mix = readWavStereo(MIX_FILE);
  const audioDuration = mix.left.length / mix.sampleRate;
  const duration = Math.min(24.5, Math.max(19.5, audioDuration + 0.42));
  const frameCount = Math.round(duration * 30);
  if (duration > 24.99) throw new Error(`duration ${duration.toFixed(3)} exceeds the 25 second cap`);
  fs.mkdirSync(path.dirname(outputFile), { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(INDEX_FILE).href, { waitUntil: "load" });
  const bundleCode = fs.readFileSync(MEDIA_BUNNY_BUNDLE, "utf8");
  await page.addScriptTag({
    type: "module",
    content:
      `${bundleCode}\n` +
      "globalThis.Mediabunny = { Output, Mp4OutputFormat, BufferTarget, VideoSampleSource, VideoSample, AudioBufferSource, Quality };",
  });
  await page.waitForFunction(() => Boolean(window.Mediabunny?.Output && window.SceneRenderer));

  const result = await page.evaluate(
    async ({ timing, leftB64, rightB64, sampleRate, duration, frameCount, label }) => {
      const decodeBase64 = (base64) => {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
        return new Float32Array(bytes.buffer);
      };
      const left = decodeBase64(leftB64);
      const right = decodeBase64(rightB64);
      const audioFrames = Math.round(duration * sampleRate);
      const audioBuffer = new AudioBuffer({
        length: audioFrames,
        numberOfChannels: 2,
        sampleRate,
      });
      audioBuffer.copyToChannel(left.subarray(0, Math.min(left.length, audioFrames)), 0);
      audioBuffer.copyToChannel(right.subarray(0, Math.min(right.length, audioFrames)), 1);

      const canvas = document.querySelector("#stage");
      const ctx = canvas.getContext("2d", { alpha: false });
      const M = window.Mediabunny;
      const output = new M.Output({
        format: new M.Mp4OutputFormat({ fastStart: "in-memory" }),
        target: new M.BufferTarget(),
      });
      let videoEncoderConfig = null;
      let audioEncoderConfig = null;
      const videoSource = new M.VideoSampleSource({
        codec: "avc",
        quality: new M.Quality({ quality: "very-high", bitrateMode: "variable" }),
        keyFrameInterval: 2,
        onEncoderConfig: (config) => {
          videoEncoderConfig = config;
        },
      });
      const audioSource = new M.AudioBufferSource(
        {
          codec: "aac",
          quality: new M.Quality({ quality: "high", bitrateMode: "variable" }),
          transform: { sampleRate: 48000, numberOfChannels: 2 },
          onEncoderConfig: (config) => {
            audioEncoderConfig = config;
          },
        },
        { startTimestamp: 0 },
      );
      output.addVideoTrack(videoSource, { frameRate: 30, name: "Mediabunny multimodal scene" });
      output.addAudioTrack(audioSource, { name: "Kokoro bf_emma + generated sound design", languageCode: "eng" });
      output.setMetadataTags({
        title: "Mediabunny - How does multimodal AI work?",
        artist: "Mediabunny benchmark",
        comment: "Canvas frames and Kokoro audio encoded and muxed by Mediabunny.",
      });
      await output.start();
      const audioDone = audioSource.add(audioBuffer).then(() => audioSource.close());
      const yuv = new Uint8Array(canvas.width * canvas.height * 1.5);
      const ySize = canvas.width * canvas.height;
      const chromaWidth = canvas.width / 2;
      const chromaPlaneSize = chromaWidth * (canvas.height / 2);
      const clampByte = (value) => Math.max(0, Math.min(255, value));
      for (let frame = 0; frame < frameCount; frame += 1) {
        const time = frame / window.SceneRenderer.fps;
        window.SceneRenderer.drawFrame(ctx, time, timing);
        const rgba = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        for (let row = 0; row < canvas.height; row += 2) {
          for (let column = 0; column < canvas.width; column += 2) {
            const p0 = (row * canvas.width + column) * 4;
            const p1 = p0 + 4;
            const p2 = p0 + canvas.width * 4;
            const p3 = p2 + 4;

            yuv[row * canvas.width + column] = clampByte(
              ((47 * rgba[p0] + 157 * rgba[p0 + 1] + 16 * rgba[p0 + 2] + 128) >> 8) + 16,
            );
            yuv[row * canvas.width + column + 1] = clampByte(
              ((47 * rgba[p1] + 157 * rgba[p1 + 1] + 16 * rgba[p1 + 2] + 128) >> 8) + 16,
            );
            yuv[(row + 1) * canvas.width + column] = clampByte(
              ((47 * rgba[p2] + 157 * rgba[p2 + 1] + 16 * rgba[p2 + 2] + 128) >> 8) + 16,
            );
            yuv[(row + 1) * canvas.width + column + 1] = clampByte(
              ((47 * rgba[p3] + 157 * rgba[p3 + 1] + 16 * rgba[p3 + 2] + 128) >> 8) + 16,
            );

            const r = (rgba[p0] + rgba[p1] + rgba[p2] + rgba[p3]) >> 2;
            const g = (rgba[p0 + 1] + rgba[p1 + 1] + rgba[p2 + 1] + rgba[p3 + 1]) >> 2;
            const b = (rgba[p0 + 2] + rgba[p1 + 2] + rgba[p2 + 2] + rgba[p3 + 2]) >> 2;
            const chromaIndex = (row >> 1) * chromaWidth + (column >> 1);
            yuv[ySize + chromaIndex] = clampByte(
              ((-30 * r - 100 * g + 130 * b + 128) >> 8) + 128,
            );
            yuv[ySize + chromaPlaneSize + chromaIndex] = clampByte(
              ((130 * r - 116 * g - 12 * b + 128) >> 8) + 128,
            );
          }
        }
        const sample = new M.VideoSample(yuv, {
          format: "I420",
          codedWidth: canvas.width,
          codedHeight: canvas.height,
          timestamp: time,
          duration: 1 / window.SceneRenderer.fps,
          colorSpace: {
            primaries: "bt709",
            transfer: "bt709",
            matrix: "bt709",
            fullRange: false,
          },
        });
        await videoSource.add(sample, { keyFrame: frame % 60 === 0 });
        sample.close();
      }
      videoSource.close();
      await audioDone;
      await output.finalize();
      const buffer = output.target.buffer;
      const bytes = new Uint8Array(buffer);
      let binary = "";
      const chunkSize = 0x8000;
      for (let index = 0; index < bytes.length; index += chunkSize) {
        binary += String.fromCharCode(...bytes.subarray(index, Math.min(bytes.length, index + chunkSize)));
      }
      return {
        b64: btoa(binary),
        byteLength: buffer.byteLength,
        mimeType: await output.getMimeType(),
        videoEncoderConfig,
        audioEncoderConfig,
        duration,
        frameCount,
        label,
      };
    },
    {
      timing,
      leftB64: bytesToBase64(new Uint8Array(mix.left.buffer, mix.left.byteOffset, mix.left.byteLength)),
      rightB64: bytesToBase64(new Uint8Array(mix.right.buffer, mix.right.byteOffset, mix.right.byteLength)),
      sampleRate: mix.sampleRate,
      duration,
      frameCount,
      label,
    },
  );

  await browser.close();
  fs.writeFileSync(outputFile, Buffer.from(result.b64, "base64"));
  const elapsed = (Date.now() - started) / 1000;
  process.stdout.write(
    `${label} wrote ${outputFile} (${result.byteLength} bytes) in ${elapsed.toFixed(2)}s\n` +
      `mime type: ${result.mimeType}\n` +
      `video encoder: ${JSON.stringify(result.videoEncoderConfig)}\n` +
      `audio encoder: ${JSON.stringify(result.audioEncoderConfig)}\n` +
      `duration: ${result.duration.toFixed(3)}s, frames: ${result.frameCount}\n`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
