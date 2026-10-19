import {makeProject} from '@revideo/core';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/inter/800.css';
import '@fontsource/jetbrains-mono/500.css';
import '@fontsource/jetbrains-mono/600.css';
import '@fontsource/jetbrains-mono/700.css';
import timing from './timing.json' with {type: 'json'};
import film from './scene?scene';

const sample = 'Aa0123456789%?→.,:()';
await Promise.all(
  ['400', '500', '600', '700', '800'].map(weight =>
    document.fonts.load(`${weight} 40px "Inter"`, sample),
  ),
);
await Promise.all(
  ['500', '600', '700'].map(weight =>
    document.fonts.load(`${weight} 40px "JetBrains Mono"`, sample),
  ),
);
await document.fonts.ready;

export default makeProject({
  scenes: [film],
  settings: {
    shared: {
      size: {x: timing.width, y: timing.height},
      background: '#071117',
      range: [0, timing.total],
    },
    preview: {
      fps: timing.fps,
      resolutionScale: 1,
    },
    rendering: {
      fps: timing.fps,
      resolutionScale: 1,
      colorSpace: 'srgb',
      exporter: {
        name: '@revideo/core/wasm',
      },
    },
  },
});
