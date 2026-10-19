import * as core from "/node_modules/@diffusionstudio/core/dist/core.es.js";

const composition = new core.Composition({
  width: 1080,
  height: 1920,
  background: "#071018",
  playbackEndBehavior: "pause",
});

const player = document.getElementById("player");
composition.mount(player);

const [openingSource, middleSource, finaleSource, audioSource, titleSource, closingSource] = await Promise.all([
  core.Source.from("/assets/blender/opening.mp4"),
  core.Source.from("/assets/hyperframes/middle.mp4"),
  core.Source.from("/assets/blender/finale.mp4"),
  core.Source.from("/assets/audio/mix.wav"),
  core.Source.from("/assets/diffusion/title-plate.png"),
  core.Source.from("/assets/diffusion/closing-plate.png"),
]);

const videoLayer = await composition.add(new core.Layer({ mode: "SEQUENTIAL" }));

const opening = new core.VideoClip(openingSource, {
  name: "Blender opening",
  duration: 7,
  effects: [
    { type: "brightness", value: 108 },
    { type: "contrast", value: 106 },
    { type: "saturate", value: 118 },
  ],
  transition: { duration: 0.55, type: "fade-to-black" },
});

const middle = new core.VideoClip(middleSource, {
  name: "HyperFrames comparative motion",
  duration: 73.8,
  effects: [
    { type: "brightness", value: 102 },
    { type: "contrast", value: 110 },
    { type: "saturate", value: 112 },
  ],
  transition: { duration: 0.55, type: "dissolve" },
});

const finale = new core.VideoClip(finaleSource, {
  name: "Blender finale",
  duration: 8,
  effects: [
    { type: "brightness", value: 106 },
    { type: "contrast", value: 108 },
    { type: "saturate", value: 118 },
  ],
});

await videoLayer.add(opening);
await videoLayer.add(middle);
await videoLayer.add(finale);

const graphicsLayer = await composition.add(new core.Layer({ mode: "DEFAULT" }), 0);

const title = new core.ImageClip(titleSource, {
  position: "center",
  width: "100%",
  height: "100%",
  delay: 0.55,
  duration: 4.7,
  animations: [
    {
      key: "translateY",
      frames: [
        { time: 0, value: 34 },
        { time: 0.75, value: 0 },
      ],
    },
  ],
});

const finalTitle = new core.ImageClip(closingSource, {
  position: "center",
  width: "100%",
  height: "100%",
  delay: 81.15,
  duration: 5.5,
  animations: [
    {
      key: "scale",
      frames: [
        { time: 0, value: 0.94 },
        { time: 0.85, value: 1 },
      ],
    },
  ],
});

await graphicsLayer.add(title);
await graphicsLayer.add(finalTitle);

const audioLayer = await composition.add(new core.Layer({ mode: "DEFAULT" }), 1);
const mix = new core.AudioClip(audioSource, {
  name: "Narration and score",
  duration: 88.8,
  volume: 1,
});
mix.fadeInDurationSeconds = 0.08;
mix.fadeOutDurationSeconds = 1.25;
await audioLayer.add(mix);

window.__filmComposition = composition;
window.__renderFilm = async () => {
  const encoder = new core.Encoder(composition, {
    format: "mp4",
    debug: true,
    video: {
      codec: "avc",
      bitrate: 14e6,
      fps: 30,
      resolution: 1,
    },
    audio: {
      enabled: true,
      codec: "aac",
      bitrate: 192e3,
      sampleRate: 48000,
      numberOfChannels: 2,
    },
    range: { end: 88.8 },
  });
  encoder.onProgress = ({ progress, total }) => {
    window.__renderProgress = total ? progress / total : 0;
  };
  return encoder.render("ai-tools-2026-diffusion-master.mp4");
};

window.__filmReady = true;
window.__filmDuration = composition.duration;
