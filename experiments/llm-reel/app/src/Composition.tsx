import {Composition} from 'remotion';
import {Film,durationInFrames} from './Film';
export const MyComposition=()=> <Composition id="TheNextToken" component={Film} durationInFrames={durationInFrames} fps={30} width={1080} height={1920}/>;
