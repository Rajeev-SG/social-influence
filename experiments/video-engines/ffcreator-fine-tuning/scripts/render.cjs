const fs = require('node:fs');
const path = require('node:path');

// FFCreator 7.x eagerly loads ECharts; Node 26 exposes `navigator`, so its
// browser detection otherwise runs before the package's Node code path.
Object.defineProperty(globalThis, 'navigator', {
  value: undefined,
  configurable: true,
  writable: true,
});

const {FFCreator} = require('ffcreator');
const {buildFilm} = require('../src/film.js');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'deliverables', 'final.mp4');
const timingPath = path.join(root, '.render', 'render-timing.json');
fs.mkdirSync(path.dirname(timingPath), {recursive: true});
fs.mkdirSync(path.dirname(output), {recursive: true});

const ffmpeg = process.env.FFMPEG_PATH || '/opt/homebrew/bin/ffmpeg';
const ffprobe = process.env.FFPROBE_PATH || '/opt/homebrew/bin/ffprobe';
FFCreator.setFFmpegPath(ffmpeg);
FFCreator.setFFprobePath(ffprobe);

const started = Date.now();
const creator = buildFilm();
creator.output(output);
creator.on('progress', (event) => {
  process.stdout.write(`\rFFCreator progress ${String(Math.round((event.percent || 0) * 100)).padStart(3, ' ')}%`);
});

new Promise((resolve, reject) => {
  creator.on('complete', resolve);
  creator.on('error', reject);
  creator.start();
})
  .then((event) => {
    const elapsed = Date.now() - started;
    fs.writeFileSync(timingPath, JSON.stringify({
      command: 'node scripts/render.cjs',
      startedAt: new Date(started).toISOString(),
      elapsedMs: elapsed,
      output,
      usage: event.useage,
    }, null, 2) + '\n');
    process.stdout.write(`\nFFCreator complete in ${(elapsed / 1000).toFixed(2)}s\n`);
  })
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
