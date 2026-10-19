import { execFile } from "node:child_process";
import { access, mkdir } from "node:fs/promises";
import { promisify } from "node:util";
import { resolve } from "node:path";

const execFileAsync = promisify(execFile);
const root = resolve(import.meta.dirname, "..");
const finalPath = resolve(root, "deliverables/final.mp4");
const previewPath = resolve(root, "deliverables/preview.mp4");
const contactSheetPath = resolve(root, "deliverables/contact-sheet.jpg");
const frameDirectory = resolve(root, ".inspect-tmp", "final-contact-sheet");

async function run(command, args) {
  return execFileAsync(command, args, { maxBuffer: 1024 * 1024 * 16 });
}

function parseMeanVolume(stderr) {
  const match = stderr.match(/mean_volume:\s*(-?\d+(?:\.\d+)?) dB/);
  return match ? Number(match[1]) : null;
}

function parseMaxVolume(stderr) {
  const match = stderr.match(/max_volume:\s*(-?\d+(?:\.\d+)?) dB/);
  return match ? Number(match[1]) : null;
}

await access(finalPath);
await access(previewPath);
await mkdir(frameDirectory, { recursive: true });

const finalProbe = JSON.parse((await run("ffprobe", [
  "-v", "error",
  "-show_streams",
  "-show_format",
  "-of", "json",
  finalPath,
])).stdout);
const previewProbe = JSON.parse((await run("ffprobe", [
  "-v", "error",
  "-show_streams",
  "-show_format",
  "-of", "json",
  previewPath,
])).stdout);

const video = finalProbe.streams.find((stream) => stream.codec_type === "video");
const audio = finalProbe.streams.find((stream) => stream.codec_type === "audio");
const previewVideo = previewProbe.streams.find((stream) => stream.codec_type === "video");
const checks = {
  finalVideoCodec: video?.codec_name === "h264",
  finalVideoProfile: video?.profile === "High",
  finalDimensions: video?.width === 1080 && video?.height === 1920,
  finalPixelFormat: video?.pix_fmt === "yuv420p",
  finalFrameRate: video?.r_frame_rate === "30/1" && video?.avg_frame_rate === "30/1",
  finalFrameCount: Number(video?.nb_frames) === 648,
  finalDuration: Number(finalProbe.format.duration) >= 15 && Number(finalProbe.format.duration) <= 25,
  audioCodec: audio?.codec_name === "aac",
  audioChannels: audio?.channels === 2 && audio?.channel_layout === "stereo",
  audioSampleRate: Number(audio?.sample_rate) === 48000,
  previewSmaller: Number(previewProbe.format.size) < Number(finalProbe.format.size),
  previewDimensions: previewVideo?.width === 540 && previewVideo?.height === 960,
};

const decode = await run("ffmpeg", ["-v", "error", "-i", finalPath, "-f", "null", "-"]);
checks.cleanDecode = decode.stderr.trim().length === 0;

const audioStats = (await run("ffmpeg", [
  "-hide_banner",
  "-i", finalPath,
  "-map", "0:a",
  "-af", "volumedetect",
  "-f", "null",
  "-",
])).stderr;
const meanVolume = parseMeanVolume(audioStats);
const maxVolume = parseMaxVolume(audioStats);
checks.audioPresent = meanVolume !== null && meanVolume > -35 && maxVolume !== null && maxVolume < 1;

const sceneTimes = [0.8, 4.8, 10.2, 15.3, 19.6, 21.3];
for (let index = 0; index < sceneTimes.length; index += 1) {
  await run("ffmpeg", [
    "-v", "error",
    "-ss", String(sceneTimes[index]),
    "-i", finalPath,
    "-frames:v", "1",
    "-q:v", "2",
    resolve(frameDirectory, `frame-${index + 1}.jpg`),
  ]);
}

await run("ffmpeg", [
  "-hide_banner",
  "-loglevel", "error",
  "-y",
  "-framerate", "1",
  "-i", resolve(frameDirectory, "frame-%d.jpg"),
  "-vf", "scale=360:640:flags=lanczos,tile=3x2:padding=8:margin=8:color=0x0b1320",
  "-frames:v", "1",
  "-q:v", "3",
  contactSheetPath,
]);
await access(contactSheetPath);

const segmentAudio = [];
const script = JSON.parse((await run("node", [
  "-e", `console.log(require("fs").readFileSync(${JSON.stringify(resolve(root, "src/script.json"))}, "utf8"))`,
])).stdout);
for (const segment of script.segments) {
  const stats = (await run("ffmpeg", [
    "-hide_banner",
    "-ss", String(segment.start),
    "-t", String(segment.end - segment.start),
    "-i", finalPath,
    "-map", "0:a",
    "-af", "volumedetect",
    "-f", "null",
    "-",
  ])).stderr;
  segmentAudio.push({
    id: segment.id,
    meanVolume: parseMeanVolume(stats),
    maxVolume: parseMaxVolume(stats),
  });
}
checks.allCaptionWindowsContainAudio = segmentAudio.every(({ meanVolume: mean }) => mean !== null && mean > -35);

const failed = Object.entries(checks).filter(([, passed]) => !passed).map(([name]) => name);
console.log(JSON.stringify({
  checks,
  failed,
  final: {
    duration: Number(finalProbe.format.duration),
    size: Number(finalProbe.format.size),
    video: {
      codec: video.codec_name,
      profile: video.profile,
      width: video.width,
      height: video.height,
      pixFmt: video.pix_fmt,
      frameRate: video.avg_frame_rate,
      frames: Number(video.nb_frames),
    },
    audio: {
      codec: audio.codec_name,
      sampleRate: Number(audio.sample_rate),
      channels: audio.channels,
      layout: audio.channel_layout,
      meanVolume,
      maxVolume,
    },
  },
  preview: {
    duration: Number(previewProbe.format.duration),
    size: Number(previewProbe.format.size),
    width: previewVideo.width,
    height: previewVideo.height,
  },
  contactSheet: contactSheetPath,
  segmentAudio,
}, null, 2));

if (failed.length > 0) {
  throw new Error(`Inspection failed: ${failed.join(", ")}`);
}
