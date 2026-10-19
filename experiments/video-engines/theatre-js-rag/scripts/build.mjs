import { build } from "esbuild";
import { mkdir, writeFile, copyFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const tmp = resolve(root, ".render-tmp");
const duration = 21.6;

function track(id, keyframes) {
  return {
    type: "BasicKeyframedTrack",
    __debugName: id,
    keyframes: keyframes.map(([position, value], index) => ({
      id: `${id}_${index}`,
      value,
      position,
      handles: [0.25, 0.1, 0.25, 1],
      connectedRight: index < keyframes.length - 1,
      type: "bezier",
    })),
  };
}

const tracks = {
  titleOpacity: [[0, 0], [0.35, 1], [2.15, 1], [2.55, 0]],
  titleY: [[0, 80], [0.7, 0], [2.2, 0], [2.55, -40]],
  titleScale: [[0, 0.92], [0.8, 1], [2.2, 1.02], [2.55, 1.07]],
  explainOpacity: [[2.2, 0], [2.65, 1], [6.85, 1], [7.35, 0]],
  termsReveal: [[2.7, 0], [4.0, 1], [6.8, 1], [7.2, 1]],
  questionX: [[2.5, 720], [3.35, 90], [6.85, 90], [7.45, 540]],
  libraryOpacity: [[7.1, 0], [7.55, 1], [12.35, 1], [12.9, 0]],
  libraryProgress: [[7.4, 0], [10.7, 1], [12.45, 1]],
  contextOpacity: [[12.55, 0], [13, 1], [16.75, 1], [17.25, 0]],
  contextProgress: [[12.8, 0], [15.4, 1], [17, 1]],
  generateOpacity: [[17, 0], [17.45, 1], [20.8, 1], [21.25, 0]],
  pipelineProgress: [[17.2, 0], [19.8, 1], [20.8, 1]],
  answerReveal: [[18.3, 0], [19.65, 1], [20.8, 1]],
  finaleOpacity: [[20.88, 0], [21.18, 1], [21.6, 1]],
  cameraZoom: [[0, 1.05], [2.5, 1], [7.2, 1.02], [12.8, 1], [17.2, 1.02], [21.6, 1]],
  cameraY: [[0, 25], [2.5, 0], [7.2, 0], [12.8, -12], [17.2, 0], [21.6, 0]],
  accentGlow: [[0, 0.5], [2.4, 1], [7.2, 0.7], [12.7, 1], [17.1, 0.75], [21.6, 1]],
};

const trackIdByPropPath = {};
const trackData = {};
for (const [propName, keyframes] of Object.entries(tracks)) {
  const id = `${propName}Track`;
  trackIdByPropPath[JSON.stringify([propName])] = id;
  trackData[id] = track(id, keyframes);
}

const theatreState = {
  sheetsById: {
    Scene: {
      staticOverrides: { byObject: {} },
      sequence: {
        type: "PositionalSequence",
        length: duration,
        subUnitsPerUnit: 30,
        tracksByObject: {
          VisualSystem: { trackIdByPropPath, trackData },
        },
      },
    },
  },
  definitionVersion: "0.4.0",
  revisionHistory: ["source-authored-2026-10-19"],
};

await mkdir(tmp, { recursive: true });
await writeFile(
  resolve(root, "src/theatre-state.json"),
  `${JSON.stringify(theatreState, null, 2)}\n`,
);
await copyFile(resolve(root, "src/index.html"), resolve(tmp, "index.html"));
await copyFile(resolve(root, "src/styles.css"), resolve(tmp, "styles.css"));

await build({
  entryPoints: [resolve(root, "src/scene.js")],
  outfile: resolve(tmp, "scene.bundle.js"),
  bundle: true,
  minify: true,
  format: "iife",
  target: "chrome120",
  legalComments: "none",
});

console.log(`Built Theatre.js scene for ${duration}s at 30fps.`);
