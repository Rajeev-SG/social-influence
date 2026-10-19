import * as THREE from "./vendor/three.module.js";

const canvas = document.getElementById("three-canvas");
const renderer = new THREE.WebGLRenderer({
  canvas,
  alpha: true,
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(1);
renderer.setSize(1080, 1920, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.1, 120);

const positions = [];
const colors = [];
const colorA = new THREE.Color("#68e0ff");
const colorB = new THREE.Color("#ffb45c");
for (let i = 0; i < 260; i += 1) {
  const theta = i * 2.3999632297;
  const y = 1 - (2 * (i + 0.5)) / 260;
  const radial = Math.sqrt(Math.max(0, 1 - y * y));
  const distance = 10 + (i % 7) * 0.85;
  positions.push(
    Math.cos(theta) * radial * distance,
    y * distance,
    Math.sin(theta) * radial * distance,
  );
  const color = i % 9 === 0 ? colorB : colorA;
  colors.push(color.r, color.g, color.b);
}

const geometry = new THREE.BufferGeometry();
geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
const particles = new THREE.Points(
  geometry,
  new THREE.PointsMaterial({
    size: 0.075,
    vertexColors: true,
    transparent: true,
    opacity: 0.72,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  }),
);
scene.add(particles);

const ringGroup = new THREE.Group();
for (let i = 0; i < 5; i += 1) {
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(4.5 + i * 1.35, 0.018, 8, 160),
    new THREE.MeshBasicMaterial({
      color: i % 2 ? 0xffb45c : 0x68e0ff,
      transparent: true,
      opacity: 0.18,
      blending: THREE.AdditiveBlending,
    }),
  );
  ring.rotation.x = Math.PI / 2 + i * 0.16;
  ring.rotation.z = i * 0.31;
  ringGroup.add(ring);
}
scene.add(ringGroup);

const nodes = [];
const palette = [0x68e0ff, 0x5a87ff, 0xff6b55, 0x5a87ff, 0xeaf6ff, 0x5a87ff, 0x5ee0b7, 0xffb45c];
for (let i = 0; i < palette.length; i += 1) {
  const angle = (i / palette.length) * Math.PI * 2;
  const node = new THREE.Mesh(
    new THREE.IcosahedronGeometry(i === 7 ? 0.32 : 0.22, 2),
    new THREE.MeshBasicMaterial({
      color: palette[i],
      transparent: true,
      opacity: 0.78,
      blending: THREE.AdditiveBlending,
    }),
  );
  node.position.set(Math.cos(angle) * 7.4, (i - 3.5) * 0.72, Math.sin(angle) * 7.4);
  nodes.push(node);
  scene.add(node);
}

function renderAt(progress) {
  const angle = progress * Math.PI * 1.35;
  camera.position.set(
    Math.sin(angle) * 3.6,
    2.8 - progress * 4.2,
    21 - progress * 5.5,
  );
  camera.lookAt(0, -0.2 + progress * 0.8, 0);
  particles.rotation.y = angle * 0.32;
  particles.rotation.x = Math.sin(progress * Math.PI) * 0.16;
  ringGroup.rotation.y = angle * 0.22;
  ringGroup.rotation.z = angle * 0.12;
  nodes.forEach((node, index) => {
    const pulse = 1 + Math.sin(progress * Math.PI * 8 + index) * 0.12;
    node.scale.setScalar(pulse);
    node.position.y += Math.sin(progress * Math.PI * 2 + index) * 0.0007;
  });
  renderer.render(scene, camera);
}

window.__aiTools3D = { renderAt };
renderAt(0);
window.__buildAIToolsTimeline();
