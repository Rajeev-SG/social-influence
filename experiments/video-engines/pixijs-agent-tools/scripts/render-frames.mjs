import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "/Users/rajeev/Code/content-machine/node_modules/playwright/index.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const variant = process.argv[2] || "first";
const frameDir = path.join(root, ".work", `frames-${variant}`);
const browserProfile = path.join(root, ".work", `chrome-${variant}`);
const frameCount = 666;
await fs.rm(frameDir, { recursive: true, force: true });
await fs.rm(browserProfile, { recursive: true, force: true });
await fs.mkdir(frameDir, { recursive: true });

const started = Date.now();
const context = await chromium.launchPersistentContext(browserProfile, {
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--use-gl=swiftshader",
    "--enable-unsafe-swiftshader",
    "--disable-background-timer-throttling",
  ],
});
const page = await context.newPage();
await page.setViewportSize({ width: 1080, height: 1920 });
page.on("console", (msg) => {
  if (msg.type() === "error") console.error("PAGE:", msg.text());
});
await page.goto(`file://${path.join(root, "src", "index.html")}?variant=${encodeURIComponent(variant)}`);
const info = await page.evaluate((v) => window.videoScene.init(v), variant);
for (let frame = 0; frame < frameCount; frame++) {
  await page.evaluate((f) => window.videoScene.renderFrame(f), frame);
  await page.locator("canvas").screenshot({
    path: path.join(frameDir, `frame-${String(frame).padStart(5, "0")}.png`),
    animations: "disabled",
    caret: "hide",
  });
  if (frame % 150 === 0) console.log(`frame ${frame}/${frameCount}`);
}
await context.close();
await fs.rm(browserProfile, { recursive: true, force: true });
const elapsedMs = Date.now() - started;
await fs.writeFile(path.join(root, ".work", `render-${variant}.json`), `${JSON.stringify({ info, frameCount, elapsedMs }, null, 2)}\n`);
console.log(JSON.stringify({ info, frameCount, elapsedMs, frameDir }, null, 2));
