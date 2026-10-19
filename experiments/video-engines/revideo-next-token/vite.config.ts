import {defineConfig} from 'vite';
import motionCanvas from '@revideo/vite-plugin';

export default defineConfig({
  publicDir: 'assets',
  plugins: [motionCanvas()],
  build: {
    minify: false,
  },
});
