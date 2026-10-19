#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
mkdir -p .review

if [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  export CHROMIUM
fi
FFPROBE_PATH=$(command -v ffprobe)
export FFPROBE_PATH

start=$(date +%s)
DISABLE_TELEMETRY=true PUPPETEER_SKIP_DOWNLOAD=1 npm run build

mkdir -p .review/segments
node - <<'NODE'
const fs = require('node:fs');
const path = require('node:path');
const root = process.cwd();
const timing = JSON.parse(fs.readFileSync(path.join(root, 'src/timing.json'), 'utf8'));
const fps = timing.fps;
const frames = Math.round(timing.total * fps);
const segmentSeconds = 5.05;
const segments = [];
for (let startFrame = 0, index = 0; startFrame < frames; index += 1) {
  const endFrame = Math.min(frames, startFrame + Math.round(segmentSeconds * fps));
  segments.push({
    index,
    startFrame,
    endFrame,
    start: startFrame / fps,
    end: endFrame / fps,
    file: `segment-${String(index).padStart(2, '0')}.mp4`,
  });
  startFrame = endFrame;
}
fs.writeFileSync(path.join(root, '.review', 'segments', 'plan.json'), `${JSON.stringify({fps, frames, segments}, null, 2)}\n`);
NODE

node - <<'NODE'
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = process.cwd();
const plan = JSON.parse(fs.readFileSync(path.join(root, '.review', 'segments', 'plan.json'), 'utf8'));
for (const segment of plan.segments) {
  const env = {
    ...process.env,
    DISABLE_TELEMETRY: 'true',
    PUPPETEER_SKIP_DOWNLOAD: '1',
    REVIDEO_RANGE_START: String(segment.start),
    REVIDEO_RANGE_END: String(segment.end),
    REVIDEO_OUT_DIR: '.review/segments',
    REVIDEO_OUT_FILE: segment.file,
  };
  console.log(`render segment ${segment.index}: ${segment.start.toFixed(3)}-${segment.end.toFixed(3)}`);
  const result = spawnSync(process.execPath, ['dist/render.js'], {cwd: root, env, stdio: 'inherit'});
  if (result.status !== 0) process.exit(result.status ?? 1);
}
const list = plan.segments.map(segment => `file '${path.join(root, '.review', 'segments', segment.file)}'`).join('\n');
fs.writeFileSync(path.join(root, '.review', 'segments', 'concat.txt'), `${list}\n`);
NODE

ffmpeg -hide_banner -loglevel error -y \
  -f concat -safe 0 -i .review/segments/concat.txt \
  -c copy -t 20.097833 .review/revideo-master.mp4

node - <<'NODE'
const fs = require('node:fs');
const {spawnSync} = require('node:child_process');
const media = '.review/revideo-master.mp4';
const result = spawnSync('ffprobe', [
  '-v', 'error', '-select_streams', 'v:0', '-count_frames',
  '-show_entries', 'stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_frames',
  '-show_entries', 'format=duration',
  '-of', 'json', media,
], {encoding: 'utf8'});
if (result.status !== 0) {
  console.error(result.stderr);
  process.exit(1);
}
const data = JSON.parse(result.stdout);
const stream = data.streams[0];
const duration = Number(data.format.duration);
const frames = Number(stream.nb_read_frames);
const valid = stream.codec_name === 'h264' && stream.width === 1080 && stream.height === 1920 &&
  stream.pix_fmt === 'yuv420p' && stream.r_frame_rate === '30/1' && frames >= 600 && duration >= 20.0;
console.log(JSON.stringify({codec: stream.codec_name, width: stream.width, height: stream.height,
  pix_fmt: stream.pix_fmt, fps: stream.r_frame_rate, frames, duration}, null, 2));
if (!valid) {
  console.error('full-master verification failed');
  process.exit(1);
}
fs.writeFileSync('.review/master-specs.json', JSON.stringify({...data, verified: true}, null, 2));
NODE

end=$(date +%s)
elapsed=$((end - start))
printf '{"seconds": %s, "command": "./scripts/render.sh", "mode": "four isolated Revideo ranges plus FFmpeg concat"}\n' "$elapsed" > .review/render-timing.json
printf 'render_seconds=%s\n' "$elapsed"
