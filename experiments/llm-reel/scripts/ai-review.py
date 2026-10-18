"""Optional multimodal creative QA through an existing OpenRouter credential."""
import os,sys,json,base64,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
(root/'.review').mkdir(exist_ok=True)
mode=sys.argv[1]
if mode=='voices':
 content=[{'type':'text','text':'Listen to these three locally generated voice samples for a premium British-English science explainer. Assess actual audible naturalness, prosody, clarity and pronunciation (especially ChatGPT). Rank them, identify artifacts, and select the best. The order is George, Emma, Fable. Be exact, not flattering.'}]
 for name in ['bm_george','bf_emma','bm_fable']:
  content += [{'type':'text','text':name},{'type':'input_audio','input_audio':{'data':base64.b64encode((root/f'.review/sample-{name}.wav').read_bytes()).decode(),'format':'wav'}}]
else:
 file=root/('.review/first-cut.mp4' if mode=='first' else 'deliverables/preview.mp4')
 content=[{'type':'text','text':"Watch and listen to this FINAL 51.2-second portrait explainer. Evaluate the actual supplied video, not an assumed duration. Check the 9.68, 14.60, 18.39, 23.06, 28.62, 36.05, 40.93 and 47.75 second transitions for overlapping titles; the intended handoff is an opaque masked reveal. Check narration naturalness, subtitle sync, the audibility of interaction ticks/air transfers/low impacts, and whether the redesigned diagrams explain the ideas. Give a frank artistic assessment; separate verified objective defects from preferences and do not invent compulsory problems. Transcribe one sentence from the middle as proof you heard the audio. Does it now work as a polished educational Reel? Note remaining material limitations concisely."},{'type':'video_url','video_url':{'url':'data:video/mp4;base64,'+base64.b64encode(file.read_bytes()).decode()}}]
req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps({'model':'google/gemini-3.8-flash','messages':[{'role':'user','content':content}],'max_tokens':2600,'temperature':.25}).encode(),headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY'],'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(req,timeout=240) as r: data=json.load(r)
 text=data['choices'][0]['message']['content'];(root/f'.review/{mode}-review.md').write_text(text);print(text)
except urllib.error.HTTPError as e:
 print(e.code,e.read().decode()[:1500]);raise
