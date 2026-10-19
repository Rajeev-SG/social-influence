import React from 'react';
import {Composition, setRootComponent} from '@rendiv/core';
import {AttentionFilm, durationInFrames} from './Attention';

const Root: React.FC = () => (
  <Composition
    id="Attention"
    component={AttentionFilm}
    durationInFrames={durationInFrames}
    fps={30}
    width={1080}
    height={1920}
  />
);

setRootComponent(Root);
