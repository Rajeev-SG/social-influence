import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { PlayerComposition } from 'motionforge';
import './styles.css';
import { TemperatureFilm, TOTAL_FRAMES } from './scene';

function App() {
  const [frame, setFrame] = useState(0);
  useEffect(() => {
    (window as unknown as { __setFrame?: (frame: number) => void }).__setFrame = setFrame;
  }, []);
  return (
    <div className="capture-root">
      <PlayerComposition
        id="temperature-in-ai"
        component={TemperatureFilm}
        width={1080}
        height={1920}
        fps={30}
        durationInFrames={TOTAL_FRAMES}
        frame={frame}
        playing={false}
      />
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
