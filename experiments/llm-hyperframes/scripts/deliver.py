from pathlib import Path
import subprocess,json,tempfile
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];out=root/'deliverables';out.mkdir(exist_ok=True)
def run(*a):subprocess.run(a,check=True)
run('ffmpeg','-v','error','-y','-i',str(root/'.review/master-render.mp4'),'-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=8','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out/'final.mp4'))
run('ffmpeg','-v','error','-y','-i',str(out/'final.mp4'),'-vf','scale=540:960','-c:v','libx264','-crf','22','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(out/'preview.mp4'))
d=json.loads((root/'timing.json').read_text());c=d['cues']
shots=[('The question',1.8),('Tea or bicycle?',c[3]['start']+1.1),('Tea fits',c[3]['end']-.35),('Learned patterns',c[4]['start']+2.6),('Earlier versus now',c[5]['start']+2.2),('Small pieces',c[6]['start']+2.5),('Build a whole answer',c[9]['start']+1.1),('Useful results',c[10]['end']-.5),('Check important facts',c[12]['end']-.4)]
w,h,band=360,640,38;sheet=Image.new('RGB',(w*3,(h+band)*3),'#efe7d4');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(root/'film/assets/fonts/Manrope.ttf'),18)
with tempfile.TemporaryDirectory() as tmp:
 for i,(label,t) in enumerate(shots):
  p=Path(tmp)/f'{i}.jpg';run('ffmpeg','-v','error','-y','-ss',str(t),'-i',str(out/'final.mp4'),'-frames:v','1','-vf',f'scale={w}:{h}',str(p))
  x=(i%3)*w;y=(i//3)*(h+band);sheet.paste(Image.open(p),(x,y+band));draw.text((x+12,y+9),f'{t:05.2f}s / {label}',font=font,fill='#2e4a2a')
sheet.save(out/'contact-sheet.jpg',quality=94,subsampling=0)
print('Delivered final.mp4, preview.mp4 and contact-sheet.jpg to',out)
