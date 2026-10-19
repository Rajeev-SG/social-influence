import * as THREE from "../assets/vendor/three.module.js";

const stage = document.querySelector("#stage");
const canvas = document.querySelector("#scene");
const caption = document.querySelector("#caption");
const phaseLabel = document.querySelector("#phaseLabel");
const timecode = document.querySelector("#timecode");
const progress = document.querySelector("#progress");
const intro = document.querySelector("#intro");
const route = document.querySelector("#route");
const inputChips = document.querySelector("#inputChips");
const formula = document.querySelector("#formula");
const outputCard = document.querySelector("#outputCard");
const finalTitle = document.querySelector("#finalTitle");
const depthProof = document.querySelector("#depthProof");

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(1);
renderer.setSize(1080, 1920, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x06101b);
scene.fog = new THREE.Fog(0x06101b, 12, 33);

const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.1, 100);
camera.position.set(0, 0.35, 18.2);

const ambient = new THREE.HemisphereLight(0x8fdfff, 0x07101b, 1.2);
scene.add(ambient);
const keyLight = new THREE.PointLight(0x6ce7ff, 38, 24, 2);
keyLight.position.set(-6, 6, 8);
scene.add(keyLight);
const fillLight = new THREE.PointLight(0xb18cff, 26, 22, 2);
fillLight.position.set(6, -2, 5);
scene.add(fillLight);
const warmLight = new THREE.PointLight(0xffc475, 16, 16, 2);
warmLight.position.set(2, 4, -3);
scene.add(warmLight);

const grid = new THREE.GridHelper(36, 36, 0x16425a, 0x0a2131);
grid.position.set(0, -5.6, -5.2);
grid.rotation.x = -Math.PI / 2;
grid.material.transparent = true;
grid.material.opacity = 0.16;
scene.add(grid);

const network = new THREE.Group();
network.position.set(0, 0.45, 0);
scene.add(network);

const layers = [
  [-5.05, [-3.15, -1.05, 1.05, 3.15], 0.12],
  [-1.65, [-2.7, -0.9, 0.9, 2.7], -0.22],
  [1.75, [-1.85, 0, 1.85], 0.18],
  [5.15, [-1.12, 1.12], -0.08],
];

const nodeGeometry = new THREE.SphereGeometry(0.33, 28, 18);
const nodeGlowGeometry = new THREE.SphereGeometry(0.48, 18, 12);
const signalGeometry = new THREE.SphereGeometry(0.12, 14, 10);
const nodeData = [];
const edgeData = [];
const signalData = [];

const nodeColors = [0x72e8ff, 0x72e8ff, 0x95f2c4, 0xb38cff, 0xffca72];

for (let layerIndex = 0; layerIndex < layers.length; layerIndex += 1) {
  const [x, ys, zBias] = layers[layerIndex];
  for (let nodeIndex = 0; nodeIndex < ys.length; nodeIndex += 1) {
    const z = zBias + (nodeIndex % 2 === 0 ? 0.4 : -0.34);
    const position = new THREE.Vector3(x, ys[nodeIndex], z);
    const color = nodeColors[Math.min(layerIndex, nodeColors.length - 1)];
    const material = new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity: 0.72,
      roughness: 0.28,
      metalness: 0.18,
    });
    const mesh = new THREE.Mesh(nodeGeometry, material);
    mesh.position.copy(position);
    network.add(mesh);

    const glowMaterial = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 0.08,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const glow = new THREE.Mesh(nodeGlowGeometry, glowMaterial);
    glow.position.copy(position);
    network.add(glow);

    nodeData.push({ mesh, glow, material, glowMaterial, position, layerIndex, nodeIndex, phase: nodeIndex * 0.8 + layerIndex * 1.35 });
  }
}

function addEdge(from, to, weight, edgeIndex) {
  const start = from.position;
  const end = to.position;
  const middle = start.clone().lerp(end, 0.5);
  middle.z += (edgeIndex % 2 === 0 ? 1 : -1) * (0.42 + (edgeIndex % 3) * 0.12);
  middle.y += Math.sin(edgeIndex * 1.7) * 0.25;
  const curve = new THREE.CatmullRomCurve3([start, middle, end]);
  const radius = 0.018 + weight * 0.062;
  const color = edgeIndex % 3 === 0 ? 0x69e5ff : edgeIndex % 3 === 1 ? 0x8c9fff : 0xc28dff;
  const material = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: 0.12,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 18, radius, 6, false), material);
  network.add(tube);

  const signal = new THREE.Mesh(signalGeometry, new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: 0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  }));
  signal.position.copy(curve.getPoint(0));
  network.add(signal);

  edgeData.push({ curve, tube, material, weight, edgeIndex, from, to });
  signalData.push({ signal, curve, edgeIndex, offset: (edgeIndex * 0.173) % 1 });
}

let edgeIndex = 0;
for (let layerIndex = 0; layerIndex < layers.length - 1; layerIndex += 1) {
  const currentLayer = nodeData.filter((node) => node.layerIndex === layerIndex);
  const nextLayer = nodeData.filter((node) => node.layerIndex === layerIndex + 1);
  for (const from of currentLayer) {
    for (const to of nextLayer) {
      const weight = 0.26 + ((edgeIndex * 37) % 74) / 100;
      addEdge(from, to, weight, edgeIndex);
      edgeIndex += 1;
    }
  }
}

const haloCanvas = document.createElement("canvas");
haloCanvas.width = 96;
haloCanvas.height = 96;
const haloContext = haloCanvas.getContext("2d");
const haloGradient = haloContext.createRadialGradient(48, 48, 2, 48, 48, 48);
haloGradient.addColorStop(0, "rgba(118,235,255,0.6)");
haloGradient.addColorStop(0.45, "rgba(118,235,255,0.16)");
haloGradient.addColorStop(1, "rgba(118,235,255,0)");
haloContext.fillStyle = haloGradient;
haloContext.fillRect(0, 0, 96, 96);
const haloTexture = new THREE.CanvasTexture(haloCanvas);
const haloMaterial = new THREE.SpriteMaterial({
  map: haloTexture,
  transparent: true,
  opacity: 0,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});
const halo = new THREE.Sprite(haloMaterial);
halo.scale.set(4.8, 4.8, 1);
network.add(halo);

const cueTimes = [
  { start: 0, end: 4, label: "THE ANALOGY" },
  { start: 4, end: 8, label: "INPUT CLUES" },
  { start: 8, end: 12, label: "WEIGHTED PATHS" },
  { start: 12, end: 16, label: "SUM + ACTIVATE" },
  { start: 16, end: 21, label: "TRAIN THE CONNECTIONS" },
  { start: 21, end: 24, label: "THE PATTERN" },
];

function clamp(value, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function smoothstep(a, b, value) {
  const x = clamp((value - a) / (b - a));
  return x * x * (3 - 2 * x);
}

function windowAlpha(value, start, end, fade = 0.32) {
  return smoothstep(start, start + fade, value) * (1 - smoothstep(end - fade, end, value));
}

function setOverlay(element, alpha, y = 0, scale = 1) {
  element.style.opacity = alpha.toFixed(4);
  element.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0) scale(${scale.toFixed(4)})`;
}

function renderFrame(rawTime) {
  const time = Number(rawTime) || 0;
  const duration = window.__SCENE_META__?.duration || 23.5;
  const introOut = cueTimes[1].start - 0.45;
  const inputWindow = windowAlpha(time, cueTimes[1].start, cueTimes[2].start + 0.25, 0.5);
  const connectionWindow = windowAlpha(time, cueTimes[2].start - 0.18, cueTimes[3].start + 0.25, 0.5);
  const activationWindow = windowAlpha(time, cueTimes[3].start - 0.18, cueTimes[4].start + 0.25, 0.5);
  const trainingWindow = windowAlpha(time, cueTimes[4].start - 0.18, cueTimes[5].start + 0.25, 0.5);
  const finalWindow = windowAlpha(time, cueTimes[5].start - 0.12, duration + 0.35, 0.42);
  const currentCue = cueTimes.reduce((current, item) => (time >= item.start ? item : current), cueTimes[0]);

  setOverlay(intro, 1 - smoothstep(introOut - 0.75, introOut + 0.08, time), smoothstep(0, introOut, time) * -36, 1 - smoothstep(introOut - 0.25, introOut + 0.25, time) * 0.06);
  setOverlay(route, 0.2 + 0.8 * Math.max(inputWindow, connectionWindow), 0, 1);
  setOverlay(inputChips, inputWindow, 12 * (1 - inputWindow), 0.94 + inputWindow * 0.06);
  setOverlay(formula, activationWindow, 12 * (1 - activationWindow), 0.97 + activationWindow * 0.03);
  setOverlay(outputCard, Math.max(trainingWindow * 0.78, finalWindow), 8 * (1 - Math.max(trainingWindow, finalWindow)), 0.98 + Math.max(trainingWindow, finalWindow) * 0.02);
  setOverlay(finalTitle, finalWindow, 20 * (1 - finalWindow), 0.96 + finalWindow * 0.04);
  setOverlay(depthProof, Math.max(connectionWindow, activationWindow, trainingWindow) * 0.85, 8, 1);

  phaseLabel.textContent = currentCue.label;
  caption.textContent = currentCue.caption || "A neural network is a team of tiny decision helpers.";
  const formatted = `00:${String(Math.floor(time)).padStart(2, "0")}`;
  timecode.textContent = formatted;
  progress.style.transform = `scaleX(${clamp(time / duration).toFixed(4)})`;

  const drift = time * 0.38;
  const cameraTarget = new THREE.Vector3(
    Math.sin(time * 0.36) * 1.18 + Math.sin(time * 0.13) * 0.32,
    0.35 + Math.cos(time * 0.27) * 0.22,
    18.1 + Math.sin(time * 0.22) * 0.82,
  );
  camera.position.lerp(cameraTarget, 0.16);
  camera.lookAt(0, 0.35, 0);

  network.rotation.y = Math.sin(time * 0.17) * 0.15 + Math.sin(time * 0.08) * 0.04;
  network.rotation.x = Math.cos(time * 0.13) * 0.055;
  network.position.y = 0.45 + Math.sin(time * 0.21) * 0.12;

  for (const node of nodeData) {
    const pulse = 0.5 + 0.5 * Math.sin(time * 3.2 + node.phase);
    const active = node.layerIndex === 0 ? inputWindow : node.layerIndex === 1 || node.layerIndex === 2 ? Math.max(connectionWindow, activationWindow) : Math.max(trainingWindow, finalWindow);
    node.material.emissiveIntensity = 0.55 + active * 1.2 + pulse * 0.28;
    node.glowMaterial.opacity = 0.06 + active * 0.12 + pulse * 0.025;
    node.mesh.scale.setScalar(1 + pulse * 0.045 + active * 0.08);
    node.glow.scale.setScalar(1 + pulse * 0.11 + active * 0.2);
    node.mesh.position.z = node.position.z + Math.sin(time * 0.4 + node.phase) * 0.08;
    node.glow.position.copy(node.mesh.position);
  }

  for (const edge of edgeData) {
    const active = edge.edgeIndex % 3 === 0 ? Math.max(connectionWindow, activationWindow, trainingWindow) : Math.max(connectionWindow * 0.75, activationWindow, trainingWindow * 0.8);
    edge.material.opacity = (0.05 + edge.weight * 0.12 + active * (0.1 + edge.weight * 0.34)) * (1 - finalWindow * 0.38);
  }

  for (const signal of signalData) {
    const travel = (time * 0.48 + signal.offset) % 1;
    const point = signal.curve.getPoint(travel);
    signal.signal.position.copy(point);
    const active = Math.max(inputWindow, connectionWindow, activationWindow, trainingWindow, finalWindow);
    signal.signal.material.opacity = active * (0.22 + 0.5 * Math.sin(travel * Math.PI) ** 2) * (1 - finalWindow * 0.32);
    signal.signal.scale.setScalar(0.7 + 0.65 * Math.sin(travel * Math.PI));
  }

  halo.position.set(-0.4 + Math.sin(time * 0.24) * 0.32, 0.5, 0.8 + Math.cos(time * 0.19) * 0.35);
  haloMaterial.opacity = 0.08 + activationWindow * 0.13 + trainingWindow * 0.05;
  keyLight.position.x = -6 + Math.sin(time * 0.22) * 1.6;
  fillLight.position.y = -2 + Math.cos(time * 0.18) * 1.4;

  renderer.render(scene, camera);
}

const fallbackTimeline = {
  duration: 23.5,
  cues: cueTimes.map((item, index) => ({ ...item, caption: [
    "A neural network is a team of tiny decision helpers.",
    "Each helper receives simple clues: edges, curves, or bright spots.",
    "The next layer combines clues through weighted connections.",
    "A node adds bias, sums the signals, then applies an activation.",
    "Training tunes the weights until layers turn clues into clear patterns.",
  ][index] || "Together, layers find patterns." })),
};

let timeline = fallbackTimeline;
try {
  const response = await fetch("../assets/audio/timing.json");
  if (response.ok) timeline = await response.json();
} catch {
  timeline = fallbackTimeline;
}

if (Array.isArray(timeline.cues) && timeline.cues.length > 0) {
  const labels = ["THE ANALOGY", "INPUT CLUES", "WEIGHTED PATHS", "SUM + ACTIVATE", "TRAIN THE CONNECTIONS", "THE PATTERN"];
  for (let i = 0; i < cueTimes.length; i += 1) {
    const cue = timeline.cues[Math.min(i, timeline.cues.length - 1)];
    cueTimes[i].start = cue.start;
    cueTimes[i].end = i < timeline.cues.length - 1 ? timeline.cues[i + 1].start : (timeline.duration || 23.5) + 0.2;
    cueTimes[i].caption = cue.caption || cue.text || fallbackTimeline.cues[i]?.caption;
    cueTimes[i].label = labels[i] || cueTimes[i].label;
  }
}

window.__SCENE_META__ = {
  width: 1080,
  height: 1920,
  fps: 30,
  duration: timeline.duration || 23.5,
};
window.__SEEK__ = (time) => {
  renderFrame(time);
  return true;
};
window.__SCENE_READY__ = true;
renderFrame(0);

