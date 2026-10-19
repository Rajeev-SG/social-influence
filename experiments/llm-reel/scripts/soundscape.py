"""Original ambient score and edge-synchronised sound design. No sampled assets."""
import json, wave
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'app/src/timing.json').read_text())
sr=48000; duration=data['duration']; t=np.arange(round(duration*sr))/sr
rng=np.random.default_rng(82); left=np.zeros(len(t));right=left.copy()
# Spacious D minor / suspended harmonic bed; no rhythmic competition with speech.
for freq,amp in [(73.416,.006),(110,.004),(146.832,.003),(220,.002),(293.665,.0018),(349.228,.0011)]:
    env=.7+.3*np.sin(2*np.pi*.035*t+freq)
    left+=amp*env*np.sin(2*np.pi*freq*t+.10*np.sin(2*np.pi*.09*t))
    right+=amp*env*np.sin(2*np.pi*(freq+.07)*t+.10*np.sin(2*np.pi*.08*t))
# Soft glass ticks on meaningful transitions and individual token reveals.
events=[(c['start'],i%4) for i,c in enumerate(data['cues'])]
events += [(next(c['start'] for c in data['cues'] if c['scene']=='tokens')+.65+i*.29,i) for i in range(5)]
events += [(next(c['start'] for c in data['cues'] if c['scene']=='generation')+s,i) for i,s in enumerate([.45,1.45,2.6,3.6])]
for start,i in events:
    n=int(.65*sr); u=np.arange(n)/sr;env=np.exp(-u*15)*(1-np.exp(-u*180))
    f=440*2**([0,7,12,14,19][i%5]/12)
    tone=(np.sin(2*np.pi*f*u)+.25*np.sin(2*np.pi*2.003*f*u))*env*.14
    pos=int(start*sr);end=min(pos+n,len(tone)+pos,len(t))
    pan=.2+.6*(i%5)/4
    left[pos:end]+=tone[:end-pos]*(1-pan);right[pos:end]+=tone[:end-pos]*pan
    # A quiet, diffuse echo.
    echo=pos+int(.16*sr);end2=min(echo+n,len(t))
    if end2>echo:
        right[echo:end2]+=tone[:end2-echo]*.16
# Air transfers at chapter changes, band-limited by moving-average differences.
for start in [c['start'] for i,c in enumerate(data['cues']) if i and c['scene']!=data['cues'][i-1]['scene']]:
    n=int(.85*sr);u=np.arange(n)/sr
    noise=rng.normal(0,1,n); smooth=np.convolve(noise,np.ones(19)/19,'same');fine=np.convolve(noise,np.ones(4)/4,'same');
    whoosh=(fine-smooth)*np.sin(np.pi*u/.85)**3*.07
    p=max(0,int((start-.28)*sr));e=min(p+n,len(t));left[p:e]+=whoosh[:e-p];right[p:e]+=whoosh[:e-p]*.8
# Quiet low-frequency impacts give the physical handoffs weight.
for scene in ['network','prediction','inference']:
    at=next(c['start'] for c in data['cues'] if c['scene']==scene)
    n=int(.55*sr);u=np.arange(n)/sr
    hit=np.sin(2*np.pi*(76*u-18*u*u))*np.exp(-u*10)*(1-np.exp(-u*140))*.08
    p=int(at*sr);e=min(p+n,len(t));left[p:e]+=hit[:e-p];right[p:e]+=hit[:e-p]
# Low, gentle resolve under the closing line.
p=int(data['cues'][-1]['start']*sr);u=t[:len(t)-p]
resolve=np.sin(2*np.pi*146.832*u)*np.exp(-u*1.4)*.06*(1-np.exp(-u*12))
left[p:]+=resolve;right[p:]+=resolve
fade=np.minimum(t/1.5,1)*np.minimum((duration-t)/1.1,1)
stereo=np.stack([left*fade*1.4,right*fade*1.4],axis=-1)
with wave.open(str(root/'app/public/audio/soundscape.wav'),'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(stereo,-1,1)*32767).astype('<i2').tobytes())
print('Original soundscape:',duration,'seconds; peak',np.max(np.abs(stereo)))
