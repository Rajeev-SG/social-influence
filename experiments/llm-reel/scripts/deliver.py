"""Finish this film's mix, encode its review copy, and make its contact sheet."""
from pathlib import Path
import json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
out=root/'deliverables';out.mkdir(exist_ok=True)
def run(*args): subprocess.run(args,check=True)
run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(root/'.review/final-picture.mp4'),'-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=8','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out/'final.mp4'))
run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out/'final.mp4'),'-vf','scale=540:960','-c:v','libx264','-crf','23','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(out/'preview.mp4'))
timing=json.loads((root/'app/src/timing.json').read_text());cues=timing['cues']
scenes={}
for c in cues: scenes.setdefault(c['scene'],[]).append(c)
def scene_time(scene,frac):
 a=scenes[scene][0]['start'];b=scenes[scene][-1]['end'];return a+(b-a)*frac
frames=[('The question',scene_time('hook',.35)),('Not a stored answer',scene_time('hook',.77)),('Tokenisation',scene_time('tokens',.68)),('Inside the network',scene_time('network',.60)),('Attention',scene_time('attention',.81)),('Next-token probabilities',scene_time('prediction',.69)),('Predict, append, repeat',scene_time('generation',.74)),('Learning the settings',scene_time('training',.78)),('Using fixed settings',scene_time('inference',.66)),('One loop, many uses',scene_time('payoff',.35)),('Fluency is not truth',scene_time('payoff',.84)),('The complete mechanism',scene_time('end',.64))]
w,h,band=360,640,42
sheet=Image.new('RGB',(w*4,(h+band)*3),'#080e18');draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype(str(root/'app/public/fonts/Manrope.ttf'),18)
with tempfile.TemporaryDirectory() as tmp:
 for i,(label,t) in enumerate(frames):
  p=Path(tmp)/f'{i}.png';run('ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(out/'final.mp4'),'-frames:v','1','-vf',f'scale={w}:{h}',str(p))
  x=(i%4)*w;y=(i//4)*(h+band)
  sheet.paste(Image.open(p),(x,y+band));draw.text((x+12,y+11),f'{t:05.2f}s  /  {label}',fill='#7aefde',font=font)
sheet.save(out/'contact-sheet.jpg',quality=94,subsampling=0)
print('Delivered:',out/'final.mp4',out/'preview.mp4',out/'contact-sheet.jpg',sep='\n')
