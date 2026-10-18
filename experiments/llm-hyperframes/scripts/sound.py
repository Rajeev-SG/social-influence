"""Original, deliberately sparse sound: soft taps and warm plucked chords."""
from pathlib import Path
import wave,json
import numpy as np
root=Path(__file__).resolve().parents[1];d=json.loads((root/'timing.json').read_text())
sr=48000;t=np.arange(round(d['duration']*sr))/sr;a=np.zeros((len(t),2));rng=np.random.default_rng(2026)
def put(at,sig,pan=.5):
 p=round(at*sr);n=min(len(sig),len(a)-p)
 a[p:p+n,0]+=sig[:n]*(1-pan);a[p:p+n,1]+=sig[:n]*pan
# A soft C6 chord once per phrase group, with a rounded, unobtrusive attack.
for at in [0,6.43,11.48,20.35,33.51,40.16]:
 u=np.arange(sr*4)/sr
 for i,f in enumerate([130.813,195.998,261.626,329.628]):
  sig=(np.sin(2*np.pi*f*u)+.13*np.sin(2*np.pi*f*2*u))*np.exp(-u*1.3)*(1-np.exp(-u*14))*.009
  put(at+i*.045,sig,.25+i*.16)
# Gentle tactile arrivals only where a word is chosen or appended.
starts=[d['cues'][3]['start']+.22,d['cues'][7]['start']+.92,d['cues'][8]['start']+.4,d['cues'][8]['start']+1.2,d['cues'][9]['start']+.32]
for i,at in enumerate(starts):
 u=np.arange(int(sr*.18))/sr
 sig=(np.sin(2*np.pi*(390+70*i)*u)+rng.normal(0,.17,len(u)))*np.exp(-u*42)*(1-np.exp(-u*300))*.09
 put(at,sig,.45)
fade=np.minimum(t/.5,1)*np.minimum((d['duration']-t)/.8,1)
a*=fade[:,None]
with wave.open(str(root/'film/assets/sound.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
