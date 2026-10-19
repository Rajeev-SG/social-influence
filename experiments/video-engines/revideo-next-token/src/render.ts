import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {renderVideo} from '@revideo/renderer';

const root = process.cwd();
const require = createRequire(import.meta.url);
const outDir = process.env.REVIDEO_OUT_DIR
  ? path.resolve(root, process.env.REVIDEO_OUT_DIR)
  : path.join(root, '.review');
fs.mkdirSync(outDir, {recursive: true});
const rangeStart = Number(process.env.REVIDEO_RANGE_START ?? '0');
const rangeEnd = Number(process.env.REVIDEO_RANGE_END ?? '0');

const chromeCandidates = [
  process.env.CHROMIUM,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
].filter((value): value is string => Boolean(value));
const executablePath = chromeCandidates.find(candidate => fs.existsSync(candidate));
const ffprobePath = execFileSync('sh', ['-c', 'command -v ffprobe']).toString().trim();
const ffmpegPath = require('@ffmpeg-installer/ffmpeg').path as string;
let lastProgressStep = -1;

const file = await renderVideo({
  projectFile: './src/project.ts',
  settings: {
    outFile: (process.env.REVIDEO_OUT_FILE ?? 'revideo-master.mp4') as `${string}.mp4`,
    outDir,
    workers: 1,
    logProgress: false,
    ffmpeg: {
      ffmpegPath,
      ffprobePath,
      ffmpegLogLevel: 'error',
    },
    puppeteer: {
      ...(executablePath ? {executablePath} : {}),
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    },
    projectSettings: {
      ...(rangeEnd > rangeStart ? {range: [rangeStart, rangeEnd]} : {}),
      size: {x: 1080, y: 1920},
      exporter: {
        name: '@revideo/core/wasm',
      },
    },
    viteConfig: {
      publicDir: path.join(root, 'assets'),
    },
    viteBasePort: 9710,
    progressCallback: (worker, progress) => {
      const step = Math.floor(progress * 10);
      if (step !== lastProgressStep) {
        lastProgressStep = step;
        console.log(`worker=${worker} progress=${step * 10}%`);
      }
    },
  },
});

console.log(`Revideo render complete: ${file}`);
