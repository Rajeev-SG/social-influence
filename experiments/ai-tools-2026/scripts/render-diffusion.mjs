import { createRequire } from "node:module";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const requireFromContentMachine = createRequire(
  "/Users/rajeev/Code/content-machine/package.json",
);
const { chromium } = requireFromContentMachine("playwright");

const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".mp4": "video/mp4",
  ".wav": "audio/wav",
  ".png": "image/png",
  ".ttf": "font/ttf",
};

const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url ?? "/", "http://localhost");
    const relative = url.pathname === "/" ? "src/diffusion/index.html" : url.pathname.slice(1);
    const filePath = path.resolve(root, relative);
    if (!filePath.startsWith(root + path.sep)) {
      response.writeHead(403).end("Forbidden");
      return;
    }
    const body = await readFile(filePath);
    response.writeHead(200, {
      "Content-Type": mime[path.extname(filePath)] ?? "application/octet-stream",
      "Content-Length": body.length,
      "Cross-Origin-Opener-Policy": "same-origin",
      "Cross-Origin-Embedder-Policy": "credentialless",
      "Cache-Control": "no-store",
    });
    response.end(body);
  } catch {
    response.writeHead(404).end("Not found");
  }
});

await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const { port } = server.address();
const url = `http://127.0.0.1:${port}/src/diffusion/index.html`;
const outputPath = path.join(root, "assets", "diffusion", "diffusion-master.mp4");

const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({
    viewport: { width: 1200, height: 900 },
    acceptDownloads: true,
  });
  const page = await context.newPage();
  page.on("console", (message) => {
    if (message.type() === "error") console.error("[browser]", message.text());
  });
  page.on("pageerror", (error) => console.error("[pageerror]", error));
  await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
  await page.waitForFunction(() => window.__filmReady === true, null, { timeout: 120000 });
  console.log("Diffusion Studio composition ready", await page.evaluate(() => window.__filmDuration));

  const [download] = await Promise.all([
    page.waitForEvent("download", { timeout: 900000 }),
    page.evaluate(() => window.__renderFilm()),
  ]);
  await download.saveAs(outputPath);
  console.log(`Saved Diffusion Studio render: ${outputPath}`);
} finally {
  await browser.close();
  server.close();
}
