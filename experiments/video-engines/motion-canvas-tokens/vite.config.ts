import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';

export default defineConfig({
  publicDir: 'assets',
  plugins: [motionCanvas()],
  server: {
    host: '127.0.0.1',
    port: 9000,
    strictPort: true,
  },
});
