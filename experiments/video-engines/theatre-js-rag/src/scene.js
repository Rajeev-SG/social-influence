import theatre from "@theatre/core";
import theatreState from "./theatre-state.json";
import script from "./script.json";

const { getProject } = theatre;
const stage = document.querySelector("#stage");
const caption = document.querySelector("#caption-text");
const captionFill = document.querySelector("#caption-progress-fill");
const timecode = document.querySelector("#timecode");

const project = getProject("What is RAG", { state: theatreState });
const sheet = project.sheet("Scene");
const visual = sheet.object("VisualSystem", {
  titleOpacity: 0,
  titleY: 80,
  titleScale: 0.92,
  explainOpacity: 0,
  termsReveal: 0,
  questionX: 720,
  libraryOpacity: 0,
  libraryProgress: 0,
  contextOpacity: 0,
  contextProgress: 0,
  generateOpacity: 0,
  pipelineProgress: 0,
  answerReveal: 0,
  finaleOpacity: 0,
  cameraZoom: 1.05,
  cameraY: 25,
  accentGlow: 0.5,
});

function clamp(value, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function applyVisualValues(values) {
  const style = stage.style;
  style.setProperty("--title-o", values.titleOpacity);
  style.setProperty("--title-y", `${values.titleY}px`);
  style.setProperty("--title-scale", values.titleScale);
  style.setProperty("--explain-o", values.explainOpacity);
  style.setProperty("--terms-p", values.termsReveal);
  style.setProperty("--question-x", `${values.questionX}px`);
  style.setProperty("--library-o", values.libraryOpacity);
  style.setProperty("--library-p", values.libraryProgress);
  style.setProperty("--context-o", values.contextOpacity);
  style.setProperty("--context-p", values.contextProgress);
  style.setProperty("--generate-o", values.generateOpacity);
  style.setProperty("--pipeline-p", values.pipelineProgress);
  style.setProperty("--answer-p", values.answerReveal);
  style.setProperty("--finale-o", values.finaleOpacity);
  style.setProperty("--camera-zoom", values.cameraZoom);
  style.setProperty("--camera-y", `${values.cameraY}px`);
  style.setProperty("--accent-glow", values.accentGlow);
}

visual.onValuesChange(applyVisualValues);

function renderCaption(position) {
  const segment = script.segments.find(({ start, end }) => position >= start && position < end)
    ?? script.segments.at(-1);
  const localProgress = clamp((position - segment.start) / Math.max(0.001, segment.end - segment.start));
  caption.textContent = segment.caption;
  captionFill.style.width = `${clamp(position / script.durationSeconds) * 100}%`;
  const minutes = Math.floor(position / 60);
  const seconds = Math.floor(position % 60);
  const tenths = Math.floor((position % 1) * 10);
  timecode.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
  caption.style.setProperty("--caption-p", localProgress);
}

window.__theatre = {
  project,
  sheet,
  visual,
  trackCount: Object.keys(theatreState.sheetsById.Scene.sequence.tracksByObject.VisualSystem.trackData).length,
  durationSeconds: script.durationSeconds,
};

window.__setFrame = async (frame) => {
  const position = frame / script.fps;
  sheet.sequence.position = position;
  applyVisualValues(visual.value);
  renderCaption(position);
  await new Promise((resolve) => requestAnimationFrame(() => resolve()));
  return { frame, position };
};

async function initialise() {
  await project.ready;
  await window.__setFrame(0);
  window.__ready = true;
}

initialise();
