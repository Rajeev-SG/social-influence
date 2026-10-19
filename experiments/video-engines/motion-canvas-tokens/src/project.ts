import {makeProject} from '@motion-canvas/core';
import tokens from './scenes?scene';

export default makeProject({
  scenes: [tokens],
  audio: '/audio/mix.wav',
});
