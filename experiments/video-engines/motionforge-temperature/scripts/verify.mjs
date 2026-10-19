import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const files = ['deliverables/final.mp4', 'deliverables/preview.mp4', 'deliverables/contact-sheet.jpg'];
const result = { checkedAt: new Date().toISOString(), files: {} };
for (const file of files) {
  const p = path.join(ROOT, file);
  if (!fs.existsSync(p)) throw new Error(`missing ${file}`);
  const probe = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=index,codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels', '-of', 'json', p], { encoding: 'utf8' });
  result.files[file] = JSON.parse(probe);
}
execFileSync('ffmpeg', ['-v', 'error', '-xerror', '-i', path.join(ROOT, 'deliverables/final.mp4'), '-f', 'null', '-'], { stdio: 'pipe' });
result.decode = 'ffmpeg -xerror decode passed';
fs.writeFileSync(path.join(ROOT, 'assets', 'qa.json'), `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
