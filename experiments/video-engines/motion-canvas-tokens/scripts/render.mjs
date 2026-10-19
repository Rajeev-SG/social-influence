#!/usr/bin/env node
// Start the Motion Canvas editor, render the project's image sequence, and close cleanly.
import fs from 'node:fs';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {createRequire} from 'node:module';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const args = process.argv.slice(2);
const rangeArg = args.includes('--range') ? args[args.indexOf('--range') + 1] : null;
const timeoutMinutes = Number(args.includes('--timeout-min') ? args[args.indexOf('--timeout-min') + 1] : 12);
const output = path.join(root, 'output');
const metaPath = path.join(root, 'src/project.meta');
const metaBackup = fs.readFileSync(metaPath, 'utf8');
const require = createRequire(path.join(root, 'package.json'));
const {chromium} = require('playwright');

function pngFiles() {
  if (!fs.existsSync(output)) return [];
  return fs.readdirSync(output, {recursive: true}).filter((file) => String(file).endsWith('.png'));
}

async function waitForEditor() {
  const deadline = Date.now() + 120000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch('http://127.0.0.1:9000/', {signal: AbortSignal.timeout(1500)});
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error('Motion Canvas editor did not start on 127.0.0.1:9000');
}

let server;
let browser;
try {
  if (rangeArg) {
    const [start, end] = rangeArg.split('-').map(Number);
    const meta = JSON.parse(metaBackup);
    meta.shared.range = [start, end];
    fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
    console.log(`draft range ${start}-${end}s`);
  }
  fs.rmSync(output, {recursive: true, force: true});
  server = spawn('npm', ['run', 'serve'], {cwd: root, stdio: 'ignore'});
  await waitForEditor();
  browser = await chromium.launch({headless: true});
  const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
  await page.goto('http://127.0.0.1:9000/', {waitUntil: 'networkidle'});
  await page.waitForTimeout(2500);
  const renderButton = page.getByRole('button', {name: /render/i}).first();
  await renderButton.click();
  console.log('Motion Canvas render started');
  const deadline = Date.now() + timeoutMinutes * 60000;
  let previous = -1;
  let stable = 0;
  let count = 0;
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 3000));
    count = pngFiles().length;
    console.log(`frames: ${count}`);
    if (count > 0 && count === previous) stable += 1;
    else stable = 0;
    if (stable >= 3) break;
    previous = count;
  }
  if (count < 2) throw new Error(`render produced too few frames: ${count}`);
  console.log(`render complete: ${count} frames in ${output}`);
} finally {
  fs.writeFileSync(metaPath, metaBackup);
  if (browser) await browser.close();
  if (server) server.kill('SIGTERM');
}
