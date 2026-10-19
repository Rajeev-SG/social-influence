import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { chromium } from 'playwright';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const FRAME_DIR = path.join(ROOT, 'assets', '.frames');
const OUT = path.join(ROOT, 'deliverables');
const TOTAL_FRAMES = 735;
fs.mkdirSync(FRAME_DIR, { recursive: true });
fs.mkdirSync(OUT, { recursive: true });

const vite = spawn('npx', ['vite', '--host', '127.0.0.1', '--port', '5173'], {
  cwd: ROOT,
  stdio: ['ignore', 'pipe', 'pipe'],
});
let viteLog = '';
vite.stdout.on('data', (d) => { viteLog += d.toString(); });
vite.stderr.on('data', (d) => { viteLog += d.toString(); });

async function waitForServer() {
  for (let i = 0; i < 80; i++) {
    try {
      execFileSync('curl', ['--noproxy', '*', '--fail', '--silent', '--show-error', 'http://127.0.0.1:5173/'], { stdio: 'pipe' });
      return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`Vite did not start. Log:\n${viteLog}`);
}

const started = Date.now();
let browser;
try {
  await waitForServer();
  browser = await chromium.launch({ headless: true, args: ['--no-proxy-server'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
  await page.waitForFunction(() => typeof window.__setFrame === 'function');
  for (let frame = 0; frame < TOTAL_FRAMES; frame++) {
    await page.evaluate((f) => window.__setFrame(f), frame);
    await page.screenshot({ path: path.join(FRAME_DIR, `frame-${String(frame).padStart(4, '0')}.png`), type: 'png' });
  }
} finally {
  if (browser) await browser.close();
  vite.kill('SIGTERM');
}

const framePattern = path.join(FRAME_DIR, 'frame-%04d.png');
execFileSync('ffmpeg', [
  '-y', '-framerate', '30', '-i', framePattern,
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
  path.join(ROOT, 'assets', 'picture.mp4'),
], { stdio: 'pipe' });

const elapsedMs = Date.now() - started;
fs.writeFileSync(path.join(ROOT, 'assets', 'render-timing.json'), `${JSON.stringify({ startedAt: new Date(started).toISOString(), elapsedMs, totalFrames: TOTAL_FRAMES, fps: 30 }, null, 2)}\n`);
fs.rmSync(FRAME_DIR, { recursive: true, force: true });
console.log(JSON.stringify({ elapsedMs, totalFrames: TOTAL_FRAMES, picture: path.join(ROOT, 'assets', 'picture.mp4') }, null, 2));
