import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { registerFont } from 'canvas';
import editly from 'editly';
import { createSceneFunction } from './scenes.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const timing = JSON.parse(fs.readFileSync(path.join(here, 'timing.json'), 'utf8'));

registerFont(path.join(root, 'assets', 'fonts', 'Manrope.ttf'), {
  family: 'Manrope',
});
registerFont(path.join(root, 'assets', 'fonts', 'Mono.ttf'), { family: 'Mono' });

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
};

const output = path.resolve(root, getArg('--out', 'deliverables/final.mp4'));
const preview = args.includes('--preview');
const transitionDuration = 0.32;
const tail = 1.25;
const totalDuration = timing.duration + tail;
const cue = (id) => timing.cues.find((item) => item.id === id).start;
const sceneStarts = [
  0,
  cue('desk') - transitionDuration,
  cue('fills') - transitionDuration,
  cue('now') - transitionDuration,
  cue('limit') - transitionDuration,
];
const sceneNames = ['hook', 'desk', 'capacity', 'meaning', 'limit'];
const transitions = [
  { name: 'directional-left', duration: transitionDuration, audioInCurve: 'tri', audioOutCurve: 'tri' },
  { name: 'directionalWarp', duration: transitionDuration, audioInCurve: 'tri', audioOutCurve: 'tri' },
  { name: 'directional-up', duration: transitionDuration, audioInCurve: 'tri', audioOutCurve: 'tri' },
  { name: 'fade', duration: transitionDuration, audioInCurve: 'tri', audioOutCurve: 'tri' },
  null,
];

const clips = sceneNames.map((scene, index) => {
  const start = sceneStarts[index];
  const nextStart = index + 1 < sceneStarts.length ? sceneStarts[index + 1] : totalDuration;
  const transition = index < transitions.length - 1 ? transitionDuration : 0;
  const duration = nextStart - start + transition;
  return {
    duration,
    transition: transitions[index],
    layers: [{
      type: 'canvas',
      func: createSceneFunction({ scene, clipStart: start, clipDuration: duration, cues: timing.cues }),
    }],
  };
});

fs.mkdirSync(path.dirname(output), { recursive: true });

await editly({
  outPath: output,
  width: preview ? 540 : 1080,
  height: preview ? 960 : 1920,
  fps: 30,
  allowRemoteRequests: false,
  fast: preview,
  verbose: false,
  logTimes: false,
  clips,
  clipsAudioVolume: 0,
  outputVolume: 1,
  audioTracks: [
    { path: path.join(root, 'assets', 'audio', 'narration.wav'), mixVolume: 1 },
    { path: path.join(root, 'assets', 'audio', 'soundscape.wav'), mixVolume: 0.34 },
  ],
  customOutputArgs: [
    '-c:v', 'libx264',
    '-preset', preview ? 'veryfast' : 'medium',
    '-crf', preview ? '27' : '17',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', preview ? '96k' : '192k',
    '-ar', '48000',
    '-movflags', '+faststart',
  ],
});

process.stdout.write(`Rendered ${output}\nPlanned duration: ${totalDuration.toFixed(3)}s\n`);
