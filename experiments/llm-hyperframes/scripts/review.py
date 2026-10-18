"""Optional actual-video clarity/listening review; never needed for rendering."""
from pathlib import Path
import os,json,sys,urllib.request,base64
root=Path(__file__).resolve().parents[1];stage=sys.argv[1]
p=root/('.review/first-cut.mp4' if stage=='first' else 'deliverables/preview.mp4')
prompt='Watch and listen to this 45-second beginner explainer. The previous version overwhelmed the viewer with diagrams, numbers and jargon; this one should be much simpler. Assess whether a complete beginner can follow the cup-of-tea example, training-versus-answering distinction, next-piece loop and caveat. Identify actual visual/timing/audio defects, misleading explanations, and any remaining overload. Inspect the actual video, not just the script. Give 3 highest-value improvements only if needed. Briefly transcribe a middle sentence as listening proof. Do not mistake deliberate quiet holds or white space for bugs. Stage: '+stage
payload={'model':'google/gemini-3.8-flash','messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'video_url','video_url':{'url':'data:video/mp4;base64,'+base64.b64encode(p.read_bytes()).decode()}}]}],'max_tokens':2000,'temperature':.2}
r=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY'],'Content-Type':'application/json'})
with urllib.request.urlopen(r,timeout=180) as z:text=json.load(z)['choices'][0]['message']['content']
(root/f'.review/{stage}-review.md').write_text(text);print(text)
