#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SHARED_REQUIRE = createRequire(
  "/Users/rajeev/Code/content-machine/package.json",
);
const { chromium } = SHARED_REQUIRE("playwright");
const CHROME =
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const outputPath = path.resolve(
  ROOT,
  process.argv[2] ?? "deliverables/final.mp4",
);
const previewPath = path.resolve(
  ROOT,
  process.argv[3] ?? "deliverables/preview.mp4",
);
const framesDir = path.resolve(
  ROOT,
  process.argv[4] ?? ".render-tmp/final-frames",
);
const finalTemp = path.join(ROOT, ".render-tmp", "final.partial.mp4");
const previewTemp = path.join(ROOT, ".render-tmp", "preview.partial.mp4");
const BATCH_SIZE = 120;

function mimeType(filePath) {
  return (
    {
      ".html": "text/html; charset=utf-8",
      ".js": "text/javascript; charset=utf-8",
      ".json": "application/json; charset=utf-8",
      ".jpg": "image/jpeg",
      ".png": "image/png",
      ".wav": "audio/wav",
    }[path.extname(filePath).toLowerCase()] ?? "application/octet-stream"
  );
}

async function startServer() {
  const server = http.createServer(async (request, response) => {
    try {
      const url = new URL(request.url ?? "/", "http://127.0.0.1");
      const relative = decodeURIComponent(url.pathname).replace(/^\/+/, "");
      const filePath = path.resolve(ROOT, relative);
      if (!filePath.startsWith(`${ROOT}${path.sep}`)) {
        response.writeHead(403).end("Forbidden");
        return;
      }
      const data = await fs.readFile(filePath);
      response.writeHead(200, {
        "Content-Type": mimeType(filePath),
        "Cache-Control": "no-store",
      });
      response.end(data);
    } catch {
      response.writeHead(404).end("Not found");
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  return { server, origin: `http://127.0.0.1:${address.port}` };
}

function encode(inputPattern, output, { preview = false } = {}) {
  const videoFilter = preview
    ? "scale=540:960:flags=lanczos:in_range=full:out_range=tv,format=yuv420p"
    : "scale=in_range=full:out_range=tv,format=yuv420p";
  const args = [
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-framerate",
    "30",
    "-start_number",
    "0",
    "-i",
    inputPattern,
    "-i",
    path.join(ROOT, "assets", "audio", "mix.wav"),
    "-map",
    "0:v:0",
    "-map",
    "1:a:0",
    "-c:v",
    "libx264",
    "-preset",
    preview ? "medium" : "slow",
    "-crf",
    preview ? "25" : "17",
    "-vf",
    videoFilter,
    "-pix_fmt",
    "yuv420p",
    "-color_range",
    "tv",
    "-colorspace",
    "bt709",
    "-color_primaries",
    "bt709",
    "-color_trc",
    "bt709",
    "-profile:v",
    "high",
    "-level",
    "4.0",
    "-r",
    "30",
    "-c:a",
    "aac",
    "-b:a",
    preview ? "128k" : "192k",
    "-ar",
    "48000",
    "-ac",
    "2",
    "-movflags",
    "+faststart",
    "-shortest",
    output,
  ];
  const result = spawnSync("ffmpeg", args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`FFmpeg failed while writing ${output}`);
  }
}

async function main() {
  const summary = JSON.parse(
    await fs.readFile(path.join(ROOT, "src", "lottie-summary.json"), "utf8"),
  );
  if (summary.fps !== 30 || summary.width !== 1080 || summary.height !== 1920) {
    throw new Error("Lottie summary does not match the 1080x1920 30fps target");
  }
  await fs.rm(framesDir, { recursive: true, force: true });
  await fs.mkdir(framesDir, { recursive: true });
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  const { server, origin } = await startServer();
  const browserErrors = [];

  const captureStarted = performance.now();
  for (let batchStart = 0; batchStart < summary.totalFrames; batchStart += BATCH_SIZE) {
    const browser = await chromium.launch({
      executablePath: CHROME,
      headless: true,
      args: [
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-color-profile=srgb",
        "--font-render-hinting=none",
      ],
    });
    const page = await browser.newPage({
      viewport: { width: 1080, height: 1920 },
      deviceScaleFactor: 1,
    });
    page.on("pageerror", (error) => browserErrors.push(String(error)));
    page.on("console", (message) => {
      if (message.type() === "error") browserErrors.push(message.text());
    });
    await page.goto(`${origin}/src/render/index.html`, {
      waitUntil: "networkidle",
    });
    await page.waitForFunction(() => window.__lottieReady === true);
    await page.evaluate(() => document.fonts.ready);

    const batchEnd = Math.min(summary.totalFrames, batchStart + BATCH_SIZE);
    for (let frame = batchStart; frame < batchEnd; frame += 1) {
      await page.evaluate((value) => window.__lottieFrame(value), frame);
      await page.screenshot({
        path: path.join(framesDir, `frame-${String(frame).padStart(5, "0")}.jpg`),
        type: "jpeg",
        quality: 96,
        animations: "disabled",
        caret: "hide",
        scale: "css",
      });
    }
    await browser.close();
    console.log(`captured ${batchEnd}/${summary.totalFrames}`);
  }
  const captureMs = Math.round(performance.now() - captureStarted);
  await new Promise((resolve) => server.close(resolve));
  if (browserErrors.length > 0) {
    throw new Error(`Browser errors: ${browserErrors.join(" | ")}`);
  }
  for (let frame = 0; frame < summary.totalFrames; frame += 1) {
    const framePath = path.join(framesDir, `frame-${String(frame).padStart(5, "0")}.jpg`);
    const stat = await fs.stat(framePath);
    if (stat.size < 10_000) {
      throw new Error(`Frame ${frame} is missing or unexpectedly small`);
    }
  }

  const encodeStarted = performance.now();
  await fs.rm(finalTemp, { force: true });
  await fs.rm(previewTemp, { force: true });
  encode(path.join(framesDir, "frame-%05d.jpg"), finalTemp);
  encode(path.join(framesDir, "frame-%05d.jpg"), previewTemp, {
    preview: true,
  });
  await fs.rename(finalTemp, outputPath);
  await fs.rename(previewTemp, previewPath);
  const encodeMs = Math.round(performance.now() - encodeStarted);
  await fs.rm(framesDir, { recursive: true, force: true });
  await fs.writeFile(
    path.join(ROOT, "assets", "render-timing.json"),
    JSON.stringify(
      {
        command: "node scripts/render-video.mjs deliverables/final.mp4 deliverables/preview.mp4",
        frames: summary.totalFrames,
        captureMs,
        encodeMs,
        totalMs: captureMs + encodeMs,
        finalBytes: (await fs.stat(outputPath)).size,
        previewBytes: (await fs.stat(previewPath)).size,
      },
      null,
      2,
    ) + "\n",
  );
  console.log(
    JSON.stringify(
      {
        frames: summary.totalFrames,
        captureMs,
        encodeMs,
        totalMs: captureMs + encodeMs,
        output: path.relative(ROOT, outputPath),
        preview: path.relative(ROOT, previewPath),
      },
      null,
      2,
    ),
  );
}

main().catch(async (error) => {
  console.error(error);
  await fs.rm(framesDir, { recursive: true, force: true });
  await fs.rm(finalTemp, { force: true });
  await fs.rm(previewTemp, { force: true });
  process.exit(1);
});
