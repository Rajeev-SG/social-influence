import { spawn } from "node:child_process";
import { once } from "node:events";
import { access, mkdir } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const root = resolve(import.meta.dirname, "..");
const tmp = resolve(root, ".render-tmp");
const deliverables = resolve(root, "deliverables");
const finalPath = resolve(deliverables, "final.mp4");
const previewPath = resolve(deliverables, "preview.mp4");
const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const durationSeconds = 21.6;
const fps = 30;
const frameCount = Math.round(durationSeconds * fps);

await execFileAsync("node", [resolve(root, "scripts/build.mjs")], {
  cwd: root,
  maxBuffer: 1024 * 1024 * 8,
});

for (const file of [
  resolve(root, "assets/narration.wav"),
  resolve(root, "assets/sound-design.wav"),
  resolve(tmp, "index.html"),
  resolve(tmp, "scene.bundle.js"),
]) {
  await access(file);
}
await mkdir(deliverables, { recursive: true });

const ffmpeg = spawn("ffmpeg", [
  "-hide_banner",
  "-loglevel", "error",
  "-y",
  "-f", "image2pipe",
  "-framerate", String(fps),
  "-c:v", "png",
  "-i", "-",
  "-i", resolve(root, "assets/narration.wav"),
  "-i", resolve(root, "assets/sound-design.wav"),
  "-filter_complex",
  "[1:a]volume=0.98[voice];[2:a]volume=0.14[sfx];" +
    "[voice][sfx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.88[a]",
  "-map", "0:v",
  "-map", "[a]",
  "-r", String(fps),
  "-fps_mode", "cfr",
  "-t", String(durationSeconds),
  "-c:v", "libx264",
  "-preset", "slow",
  "-crf", "17",
  "-profile:v", "high",
  "-pix_fmt", "yuv420p",
  "-c:a", "aac",
  "-b:a", "192k",
  "-ar", "48000",
  "-ac", "2",
  "-movflags", "+faststart",
  finalPath,
], { stdio: ["pipe", "ignore", "pipe"] });

let ffmpegStderr = "";
ffmpeg.stderr.on("data", (chunk) => {
  ffmpegStderr += chunk.toString();
});
const ffmpegClosed = once(ffmpeg, "close");

async function writeFrame(buffer) {
  if (ffmpeg.stdin.write(buffer)) return;
  await once(ffmpeg.stdin, "drain");
}

const browserStarted = Date.now();
const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
  args: [
    "--hide-scrollbars",
    "--force-color-profile=srgb",
    "--font-render-hinting=none",
  ],
});

const page = await browser.newPage({
  viewport: { width: 1080, height: 1920 },
  deviceScaleFactor: 1,
});
page.on("pageerror", (error) => {
  throw new Error(`Browser scene error: ${error.message}`);
});

await page.goto(pathToFileURL(resolve(tmp, "index.html")).href, { waitUntil: "load" });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });

const theatreMetadata = await page.evaluate(() => ({
  trackCount: window.__theatre.trackCount,
  durationSeconds: window.__theatre.durationSeconds,
  sequenceSubUnitsPerUnit: 30,
}));

console.log(
  `Rendering ${frameCount} Theatre.js frames (${theatreMetadata.trackCount} keyframed tracks, ` +
  `${theatreMetadata.sequenceSubUnitsPerUnit} subunits/s).`,
);

for (let frame = 0; frame < frameCount; frame += 1) {
  await page.evaluate((currentFrame) => window.__setFrame(currentFrame), frame);
  const png = await page.screenshot({ type: "png", animations: "disabled" });
  await writeFrame(png);
  if (frame % 60 === 0 || frame === frameCount - 1) {
    console.log(`Captured frame ${frame + 1}/${frameCount}`);
  }
}

ffmpeg.stdin.end();
const [ffmpegCode] = await ffmpegClosed;
await browser.close();

if (ffmpegCode !== 0) {
  throw new Error(`FFmpeg failed with code ${ffmpegCode}: ${ffmpegStderr}`);
}

const previewStarted = Date.now();
await execFileAsync("ffmpeg", [
  "-hide_banner",
  "-loglevel", "error",
  "-y",
  "-i", finalPath,
  "-vf", "scale=540:960:flags=lanczos",
  "-c:v", "libx264",
  "-preset", "medium",
  "-crf", "25",
  "-profile:v", "high",
  "-pix_fmt", "yuv420p",
  "-c:a", "aac",
  "-b:a", "128k",
  "-movflags", "+faststart",
  previewPath,
], { maxBuffer: 1024 * 1024 * 8 });

const finalCaptureEncodeSeconds = (previewStarted - browserStarted) / 1000;
const previewSeconds = (Date.now() - previewStarted) / 1000;
const fullPipelineSeconds = (Date.now() - browserStarted) / 1000;
console.log(
  `FINAL_CAPTURE_ENCODE_SECONDS=${finalCaptureEncodeSeconds.toFixed(3)} ` +
  `PREVIEW_ENCODE_SECONDS=${previewSeconds.toFixed(3)} ` +
  `FULL_PIPELINE_SECONDS=${fullPipelineSeconds.toFixed(3)}`,
);
console.log(`Theatre.js metadata: ${JSON.stringify(theatreMetadata)}`);
