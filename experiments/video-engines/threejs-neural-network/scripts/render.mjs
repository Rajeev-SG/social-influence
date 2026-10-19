import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync, spawn } from "node:child_process";
import { createRequire } from "node:module";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const argValue = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 && args[index + 1] ? args[index + 1] : fallback;
};
const label = argValue("--label", "final");
const keepTemp = args.includes("--keep-temp");
const forceAudio = args.includes("--force-audio");
const deliver = args.includes("--deliver");
const output = path.resolve(root, argValue("--output", label === "final" ? "deliverables/final.mp4" : `.render-tmp/${label}/first-cut.mp4`));
const tempDir = path.join(root, ".render-tmp", label);
const qaDir = path.join(tempDir, "qa");
fs.rmSync(tempDir, { recursive: true, force: true });
fs.mkdirSync(qaDir, { recursive: true });
fs.mkdirSync(path.dirname(output), { recursive: true });

const startedAt = process.hrtime.bigint();
const run = (command, commandArgs, options = {}) => {
  console.log(`$ ${command} ${commandArgs.join(" ")}`);
  execFileSync(command, commandArgs, { cwd: root, stdio: "inherit", ...options });
};

function ensureAudio() {
  const timingPath = path.join(root, "assets", "audio", "timing.json");
  const narrationPath = path.join(root, "assets", "audio", "narration.wav");
  const soundscapePath = path.join(root, "assets", "audio", "soundscape.wav");
  if (!forceAudio && fs.existsSync(timingPath) && fs.existsSync(narrationPath) && fs.existsSync(soundscapePath)) {
    console.log("audio: reusing generated narration and soundscape");
    return;
  }

  run(process.execPath, ["scripts/generate-narration.cjs"]);
  run("ffmpeg", [
    "-y",
    "-i",
    "assets/audio/narration-raw.wav",
    "-af",
    "highpass=f=75,lowpass=f=11000,acompressor=threshold=0.12:ratio=2:attack=15:release=180:makeup=1.2,loudnorm=I=-17:TP=-2:LRA=8",
    "-ar",
    "48000",
    "-ac",
    "1",
    "assets/audio/narration.wav",
  ]);
  run("python3", ["scripts/generate-soundtrack.py"]);
  fs.rmSync(path.join(root, "assets", "audio", "narration-raw.wav"), { force: true });
}

function serveRoot() {
  const mime = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".wav": "audio/wav",
    ".mp4": "video/mp4",
    ".jpg": "image/jpeg",
    ".png": "image/png",
  };
  const server = http.createServer((request, response) => {
    const requestPath = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    const filePath = path.resolve(root, `.${requestPath}`);
    if (!filePath.startsWith(root) || !fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
      response.writeHead(404);
      response.end("not found");
      return;
    }
    response.writeHead(200, { "Content-Type": mime[path.extname(filePath)] || "application/octet-stream" });
    fs.createReadStream(filePath).pipe(response);
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => resolve({ server, port: server.address().port }));
  });
}

function ffmpegPicture(frameCount) {
  const ffmpeg = spawn("ffmpeg", [
    "-y",
    "-loglevel",
    "error",
    "-f",
    "image2pipe",
    "-framerate",
    "30",
    "-i",
    "-",
    "-frames:v",
    String(frameCount),
    "-c:v",
    "libx264",
    "-preset",
    "slow",
    "-crf",
    "16",
    "-pix_fmt",
    "yuv420p",
    path.join(tempDir, "picture.mp4"),
  ]);
  return ffmpeg;
}

async function writeFrame(page, frame, ffmpeg) {
  const buffer = await page.screenshot({ type: "png", animations: "disabled" });
  if (!ffmpeg.stdin.write(buffer)) {
    await new Promise((resolve) => ffmpeg.stdin.once("drain", resolve));
  }
}

async function main() {
  ensureAudio();
  const timing = JSON.parse(fs.readFileSync(path.join(root, "assets", "audio", "timing.json"), "utf8"));
  const { server, port } = await serveRoot();
  const require = createRequire("/Users/rajeev/Code/content-machine/package.json");
  const { chromium } = require("playwright");
  const browser = await chromium.launch({
    headless: true,
    args: ["--hide-scrollbars", "--force-color-profile=srgb", "--disable-lcd-text"],
  });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
  });
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));

  await page.goto(`http://127.0.0.1:${port}/src/index.html?capture=1`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => window.__SCENE_READY__ === true);
  const meta = await page.evaluate(() => window.__SCENE_META__);
  const fps = meta.fps || 30;
  const duration = meta.duration || timing.duration;
  const frameCount = Math.round(duration * fps);
  console.log(`scene meta: ${meta.width}x${meta.height} ${fps}fps ${duration.toFixed(3)}s (${frameCount} frames)`);

  const ffmpeg = ffmpegPicture(frameCount);
  let ffmpegError = "";
  ffmpeg.stderr.on("data", (chunk) => { ffmpegError += chunk.toString(); });
  const ffmpegDone = new Promise((resolve, reject) => {
    ffmpeg.on("error", reject);
    ffmpeg.on("close", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg picture failed (${code}): ${ffmpegError}`))));
  });

  for (let frame = 0; frame < frameCount; frame += 1) {
    await page.evaluate((time) => window.__SEEK__(time), frame / fps);
    await writeFrame(page, frame, ffmpeg);
    if (frame % 60 === 0) console.log(`captured ${frame}/${frameCount}`);
  }
  ffmpeg.stdin.end();
  await ffmpegDone;

  const cueStarts = timing.cues.map((cue) => cue.start);
  const sampleTimes = [
    Math.min(0.45, duration * 0.1),
    Math.min(duration - 0.3, (cueStarts[1] ?? 4) + 0.45),
    Math.min(duration - 0.3, (cueStarts[2] ?? 8) + 0.55),
    Math.min(duration - 0.3, (cueStarts[3] ?? 12) + 0.55),
    Math.min(duration - 0.3, (cueStarts[4] ?? 16) + 0.55),
    Math.max(0, duration - 0.55),
  ];
  const framePaths = [];
  for (let index = 0; index < sampleTimes.length; index += 1) {
    await page.evaluate((time) => window.__SEEK__(time), sampleTimes[index]);
    const framePath = path.join(qaDir, `frame-${index}.png`);
    await page.screenshot({ path: framePath, type: "png", animations: "disabled" });
    framePaths.push(framePath);
  }

  await browser.close();
  server.close();

  const mixArgs = [
    "-y",
    "-loglevel",
    "error",
    "-i",
    path.join(tempDir, "picture.mp4"),
    "-i",
    "assets/audio/narration.wav",
    "-i",
    "assets/audio/soundscape.wav",
    "-filter_complex",
    "[1:a]volume=1.0[voice];[2:a]volume=0.34[bed];[voice][bed]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[aout]",
    "-map",
    "0:v:0",
    "-map",
    "[aout]",
    "-c:v",
    "copy",
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-ar",
    "48000",
    "-ac",
    "2",
    "-movflags",
    "+faststart",
    "-shortest",
    output,
  ];
  run("ffmpeg", mixArgs);

  const contactSheet = path.join(tempDir, "contact-sheet.jpg");
  const contactArgs = ["-y", "-loglevel", "error"];
  for (const framePath of framePaths) contactArgs.push("-i", framePath);
  contactArgs.push(
    "-filter_complex",
    "[0:v]scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2:color=0x06101b[v0];[1:v]scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2:color=0x06101b[v1];[2:v]scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2:color=0x06101b[v2];[3:v]scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2:color=0x06101b[v3];[4:v]scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2:color=0x06101b[v4];[5:v]scale=360:640:force_original_aspect_ratio=decrease,pad=360:640:(ow-iw)/2:(oh-ih)/2:color=0x06101b[v5];[v0][v1][v2][v3][v4][v5]xstack=inputs=6:layout=0_0|360_0|720_0|0_640|360_640|720_640:fill=0x06101b[out]",
    "-map",
    "[out]",
    "-frames:v",
    "1",
    "-q:v",
    "2",
    contactSheet,
  );
  run("ffmpeg", contactArgs);

  if (deliver) {
    run("ffmpeg", [
      "-y",
      "-loglevel",
      "error",
      "-i",
      output,
      "-vf",
      "scale=540:960",
      "-c:v",
      "libx264",
      "-preset",
      "medium",
      "-crf",
      "28",
      "-pix_fmt",
      "yuv420p",
      "-c:a",
      "aac",
      "-b:a",
      "96k",
      "-movflags",
      "+faststart",
      path.join(root, "deliverables", "preview.mp4"),
    ]);
    fs.copyFileSync(contactSheet, path.join(root, "deliverables", "contact-sheet.jpg"));
  }

  const elapsedSeconds = Number(process.hrtime.bigint() - startedAt) / 1e9;
  console.log(`RENDER_SECONDS=${elapsedSeconds.toFixed(3)}`);
  console.log(`OUTPUT=${path.relative(root, output)}`);
  console.log(`FRAMES=${frameCount}`);
  console.log(`CONSOLE_ERRORS=${consoleErrors.length}`);
  if (consoleErrors.length > 0) console.log(consoleErrors.join("\n"));

  if (!keepTemp) fs.rmSync(tempDir, { recursive: true, force: true });
  else console.log(`TEMP_RETAINED_FOR_REVIEW=${path.relative(root, tempDir)}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
