from pathlib import Path
import json,re,html
root=Path(__file__).resolve().parents[1];d=json.loads((root/'timing.json').read_text())
p=root/'film/index.html';s=p.read_text();cues=d['cues'];groups={}
for c in cues:groups.setdefault(c['scene'],[]).append(c)
for i,(name,cs) in enumerate(groups.items()):
 a=0 if i==0 else cs[0]['start'];b=list(groups.values())[i+1][0]['start'] if i<len(groups)-1 else d['duration']
 s=re.sub(r'(id="scene-'+name+r'"[^>]*data-start=")[^"]+(" data-duration=")[^"]+',lambda m:m[1]+str(a)+m[2]+str(b-a),s)
s=re.sub(r'(id="root"[^>]*data-duration=")[^"]+',lambda m:m[1]+str(d['duration']),s)
for name in ['cup-track','narration','sound']:
 s=re.sub(r'(id="'+name+r'"[^>]*data-duration=")[^"]+',lambda m:m[1]+str(d['duration']),s)
caption=[]
for i,c in enumerate(cues):
 cls=' dark-caption' if c['scene'] in ['training','limits'] else ''
 caption.append(f'<div id="caption-{i}" class="caption clip{cls}" data-start="{c["start"]}" data-duration="{c["end"]-c["start"]}" data-track-index="5"><p>{html.escape(c["text"])}</p></div>')
s=re.sub(r'<!-- CAPTIONS_START -->.*?<!-- CAPTIONS_END -->','<!-- CAPTIONS_START -->\n'+'\n'.join(caption)+'\n<!-- CAPTIONS_END -->',s,flags=re.S)
s=re.sub(r'<!-- MOTION_START -->.*?<!-- MOTION_END -->','<!-- MOTION_START -->\n<script>\n'+(root/'film/motion.js').read_text()+'\n</script>\n<!-- MOTION_END -->',s,flags=re.S)
p.write_text(s);(root/'film/timing.js').write_text('window.FILM_TIMING = '+json.dumps(d,indent=2)+';\n')
