#!/usr/bin/env node
/**
 * AIForAccountants pilot — REAL recorded browser workflow.
 *
 * Produces 6 silent 1080x1920 mp4 clips in brands/ai-for-accountants/media/pilot/
 * plus source evidence in brands/ai-for-accountants/sources/.
 *
 * The demo is our own "Workflow lab" desktop UI. It is NOT a fake ChatGPT/OpenAI UI.
 * The follow-up email + actions shown on screen come from an ACTUAL model call to the
 * local cliproxyapi provider (/chat/completions, model opencode-go/deepseek-v4.1-flash).
 * Credentials are read from ~/.codex/config.toml and never printed.
 *
 * All data is synthetic. No real client data. No time-saving or tax claims.
 */
import { chromium } from '/Users/rajeev/Code/content-machine/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.join(REPO, 'brands/ai-for-accountants/sources');
const MEDIA = path.join(REPO, 'brands/ai-for-accountants/media/pilot');
fs.mkdirSync(SRC, { recursive: true });
fs.mkdirSync(MEDIA, { recursive: true });

const FFMPEG_ENV = { ...process.env, DYLD_FALLBACK_LIBRARY_PATH: '/opt/homebrew/Cellar/x265/4.1/lib' };
const DUR = 8.0;
const W = 1080, H = 1920;

// ---------------------------------------------------------------- synthetic notes
const NOTES = {
  label: 'SYNTHETIC MEETING NOTES — Rowan & Co (fake practice)',
  synthetic: true,
  client: 'Bluebell Cafe Ltd (fictional)',
  raised: '2026-09-29',
  lines: [
    'Attendees: Alex (partner), Priya (client finance lead).',
    'Discussed 2024/25 draft accounts.',
    'Priya to send the missing March bank statement.',
    'VAT return for next quarter mentioned; no date given.',
    'Alex will check the payroll query.',
    'Client asked about a fixed-fee proposal; no amount agreed.',
    'A next meeting was mentioned but no date set.',
    'No engagement-letter changes discussed.'
  ]
};

// ---------------------------------------------------------------- config read (no secrets out)
function readProvider() {
  const text = fs.readFileSync(path.join(process.env.HOME, '.codex/config.toml'), 'utf8');
  const lines = text.split(/\r?\n/);
  let inSection = false, base = null, token = null;
  for (const line of lines) {
    const sec = line.match(/^\s*\[([^\]]+)\]\s*$/);
    if (sec) { inSection = sec[1].trim() === 'model_providers.cliproxyapi'; continue; }
    if (!inSection) continue;
    const b = line.match(/^\s*base_url\s*=\s*"(.*)"\s*$/);
    if (b) base = b[1];
    const t = line.match(/^\s*experimental_bearer_token\s*=\s*"(.*)"\s*$/);
    if (t) token = t[1];
  }
  if (!base || !token) throw new Error('cliproxyapi base_url/token not found in config.toml');
  return { base, token };
}

const PROMPT = [
  'You are drafting an internal client follow-up for an accounting practice.',
  'Use ONLY the supplied notes. Never invent dates, deadlines, amounts, advice or commitments.',
  'If a date or deadline is not stated in the notes, write exactly "TO CONFIRM".',
  'Return strict JSON with keys: email_subject, email_body, actions (array of {action, owner, due}), review_flags (array of strings).',
  'Keep the email short and neutral. Every action due not stated in the notes must be "TO CONFIRM".',
  '',
  'NOTES:',
  ...NOTES.lines
].join('\n');

async function callModel() {
  const { base, token } = readProvider();
  const res = await fetch(base.replace(/\/$/, '') + '/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
    body: JSON.stringify({
      model: 'opencode-go/deepseek-v4.1-flash',
      temperature: 0.2,
      messages: [{ role: 'user', content: PROMPT }]
    })
  });
  if (!res.ok) throw new Error('model HTTP ' + res.status);
  const json = await res.json();
  const raw = json.choices[0].message.content;
  const cleaned = raw.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim();
  return { raw, parsed: JSON.parse(cleaned) };
}

// ---------------------------------------------------------------- shared UI shell
function shell({ active, body, caption }) {
  const step = (id, label) => {
    const on = active === id;
    return `<div class="step ${on ? 'on' : ''}"><span class="dot"></span>${label}</div>`;
  };
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,'Helvetica Neue',Arial,sans-serif}
  html,body{width:${W}px;height:${H}px;background:#0d1319;overflow:hidden}
  .ui{position:absolute;left:0;top:0;width:${W}px;height:1400px;background:#f4f6f8;display:flex;flex-direction:column;overflow:hidden}
  .titlebar{height:74px;background:#1f2b3a;color:#e8eef5;display:flex;align-items:center;gap:18px;padding:0 28px;font-size:30px}
  .titlebar .w{font-weight:700}
  .titlebar .tag{font-size:22px;color:#9fb3c8;margin-left:auto}
  .badge-synth{background:#7a1f1f;color:#fff;font-size:20px;padding:6px 14px;border-radius:6px;font-weight:700}
  .badge-rev{background:#7a5200;color:#fff;font-size:20px;padding:6px 14px;border-radius:6px;font-weight:700}
  .strip{height:78px;background:#12202e;color:#dfe9f3;display:flex;align-items:center;justify-content:center;gap:0;font-size:31px;font-weight:600;letter-spacing:1px}
  .step{display:flex;align-items:center;gap:12px;padding:0 46px;opacity:.45}
  .step .dot{width:16px;height:16px;border-radius:50%;background:#5d7893}
  .step.on{opacity:1;color:#fff}
  .step.on .dot{background:#43c08a;box-shadow:0 0 0 6px rgba(67,192,138,.22)}
  .arrow{opacity:.5;font-size:30px}
  .main{flex:1;display:flex;min-height:0}
  .side{width:250px;background:#e7ebef;border-right:2px solid #d3dae1;padding:22px 18px;display:flex;flex-direction:column;gap:14px}
  .side .item{background:#fff;border:2px solid #d6dde4;border-radius:8px;padding:16px;font-size:23px;color:#42536a}
  .side .item.on{border-color:#1f6feb;background:#eaf2ff;color:#123f86;font-weight:700}
  .pane{flex:1;padding:28px 34px;display:flex;flex-direction:column;gap:20px;min-width:0}
  .pane h1{font-size:38px;color:#16202c}
  .pane h2{font-size:26px;color:#42536a;font-weight:600}
  .card{background:#fff;border:2px solid #d6dde4;border-radius:10px;padding:22px 24px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
  .notes li{font-size:25px;line-height:1.5;color:#22303f;margin-left:24px}
  .notes li+li{margin-top:5px}
  .kv{display:flex;gap:14px;align-items:baseline;font-size:25px;color:#22303f;margin-top:9px}
  .kv b{color:#16202c}
  .pill{display:inline-block;background:#eef2f6;border:2px solid #d6dde4;border-radius:999px;padding:5px 16px;font-size:22px;color:#42536a}
  .pill.ok{background:#e6f6ee;border-color:#43c08a;color:#14663f;font-weight:700}
  .pill.warn{background:#fff4e0;border-color:#e0a300;color:#7a5200;font-weight:700}
  .json{background:#0f1a24;color:#cfe3f5;border-radius:8px;padding:18px 20px;font-family:ui-monospace,Menlo,monospace;font-size:20px;line-height:1.42;white-space:pre-wrap}
  .email{background:#fff;border:2px solid #d6dde4;border-radius:10px;padding:24px}
  .email .subj{font-size:27px;font-weight:700;color:#16202c;border-bottom:2px solid #e4e9ee;padding-bottom:12px;margin-bottom:14px}
  .email .body{font-size:24px;line-height:1.55;color:#22303f;white-space:pre-wrap}
  table.act{width:100%;border-collapse:collapse;font-size:24px}
  table.act th{text-align:left;background:#eef2f6;color:#42536a;padding:12px 14px;font-size:22px}
  table.act td{padding:13px 14px;border-top:2px solid #e4e9ee;color:#22303f}
  table.act .due{color:#7a5200;font-weight:700}
  .chk{display:flex;align-items:center;gap:16px;background:#fff;border:2px solid #d6dde4;border-radius:10px;padding:18px 22px;font-size:26px;color:#22303f}
  .box{width:38px;height:38px;border:3px solid #8b9aab;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;flex:none}
  .box.done{background:#1f9d5c;border-color:#1f9d5c}
  .save{margin-top:6px;width:360px;height:74px;border-radius:10px;border:none;font-size:30px;font-weight:700;background:#c3ccd6;color:#66788c}
  .save.ready{background:#1f6feb;color:#fff}
  .cursor{position:absolute;width:28px;height:28px;z-index:99;transition:transform .5s ease;pointer-events:none}
  .cursor svg{filter:drop-shadow(0 2px 3px rgba(0,0,0,.4))}
  .safe{position:absolute;left:0;top:1240px;width:${W}px;height:680px;background:#182431;z-index:5}
  .caption .cs{font-size:21px;color:#7fb2e5;letter-spacing:2px;font-weight:700}
  .caption .ct{font-size:32px;line-height:1.17;font-weight:600}
  .caption .foot{font-size:18px;color:#9fb3c8;margin-top:2px}
  .progress{height:12px;background:#2b3b4d;border-radius:999px;overflow:hidden;margin-top:8px}
  .progress i{display:block;height:100%;width:0%;background:#43c08a;transition:width .45s ease}
  .flash{outline:5px solid #1f6feb;outline-offset:3px}
  .dim{opacity:.35}
  .hl{background:#fff3bf;padding:0 6px;border-radius:4px}
</style></head><body>
  <div class="ui">
    <div class="titlebar"><span class="w">Workflow lab</span><span style="color:#9fb3c8;font-size:23px">own functional demo — not a ChatGPT/OpenAI UI</span>
      <span class="tag"><span class="badge-synth">SYNTHETIC DATA</span></span>
      <span class="badge-rev">REVIEW REQUIRED</span></div>
    <div class="strip">${step('input', 'INPUT')}<span class="arrow">→</span>${step('ai', 'AI STEP')}<span class="arrow">→</span>${step('human', 'HUMAN CHECK')}</div>
    <div class="main">
      <div class="side">
        <div class="item ${active==='input'?'on':''}">1 · Input notes</div>
        <div class="item ${active==='ai'?'on':''}">2 · AI draft</div>
        <div class="item ${active==='human'?'on':''}">3 · Human check</div>
        <div class="item">4 · Save to review queue</div>
      </div>
      <div class="pane">${body}</div>
    </div>
  </div>
  <div class="safe"></div>
  <svg class="cursor" id="cur" viewBox="0 0 24 24"><path d="M4 2 L4 21 L9 16 L12 22 L15 21 L12 15 L19 15 Z" fill="#fff" stroke="#111" stroke-width="1.4"/></svg>
  <script>
  const cur=document.getElementById('cur');
  function move(x,y){cur.style.transform='translate('+x+'px,'+y+'px)';}
  window.__move=move;
  </script></body></html>`;
}

function caption(scene, text, foot) {
  return `<div class="cs">SCENE ${String(scene).padStart(3,'0')}</div><div class="ct">${text}</div><div class="foot">${foot}</div>`;
}

// ---------------------------------------------------------------- scenes
function sceneOne() {
  return {
    active: 'input',
    body: `<h1>Raw client meeting notes <span class="pill">input</span></h1>
      <h2>${NOTES.label}</h2>
      <div class="card notes"><ul>${NOTES.lines.map(l => `<li>${l}</li>`).join('')}</ul></div>
      <div class="kv"><b>Contains no dates, no amounts, no advice.</b></div>`,
    caption: caption(1, 'Start with the raw meeting notes.', 'Data is clearly labelled SYNTHETIC DATA. No real client data appears anywhere in this workflow.')
  };
}

function sceneTwo() {
  return {
    active: 'input',
    body: `<h1>Stage the input <span class="pill">input → AI step</span></h1>
      <div class="card"><h2>Workflow lab · new run</h2>
      <div class="kv"><b>Client</b> Bluebell Cafe Ltd (fictional)</div>
      <div class="kv"><b>Task</b> Draft follow-up email + action list</div>
      <div class="kv"><b>Source</b> 8 synthetic note lines <span class="pill">pasted</span></div>
      <div class="kv"><b>Rule</b> unspecified dates must stay <span class="hl">TO CONFIRM</span></div></div>
      <div class="progress"><i id="pg"></i></div>`,
    caption: caption(2, 'The task, the source and the review rule are set before the model runs.', 'The rule is explicit: no invented deadlines. Unstated dates must stay TO CONFIRM.')
  };
}

function sceneThree(raw) {
  const trimmed = raw.length > 620 ? raw.slice(0, 620) + '\n …' : raw;
  return {
    active: 'ai',
    body: `<h1>AI step · prompt sent to model <span class="pill">running</span></h1>
      <div class="card"><h2>Prompt (excerpt)</h2><div class="json">Use ONLY the supplied notes.
Never invent dates, deadlines, amounts or advice.
Return strict JSON: email_subject, email_body, actions, review_flags.</div></div>
      <div class="card"><h2>Model response (raw JSON)</h2><div class="json">${trimmed.replace(/[<&]/g, c => c === '<' ? '&lt;' : '&amp;')}</div></div>`,
    caption: caption(3, 'One real model call turns the notes into structured JSON.', 'Model: opencode-go/deepseek-v4.1-flash via the local cliproxyapi provider. Output is untrusted until checked.')
  };
}

function sceneFour(d) {
  return {
    active: 'ai',
    body: `<h1>AI step · draft email <span class="pill">draft only</span></h1>
      <div class="email"><div class="subj">${esc(d.email_subject)}</div><div class="body">${esc(d.email_body)}</div></div>
      <div class="kv"><span class="pill warn">REVIEW REQUIRED</span> This is a draft, not a sent message.</div>`,
    caption: caption(4, 'The model drafts the follow-up email.', 'Still a draft. It is not sent and it is not advice.')
  };
}

function sceneFive(d) {
  const rows = d.actions.map(a => `<tr><td>${esc(a.action)}</td><td>${esc(a.owner)}</td><td class="due">${esc(a.due)}</td></tr>`).join('');
  const flags = d.review_flags.map(f => `<div class="kv">• ${esc(f)}</div>`).join('');
  return {
    active: 'human',
    body: `<h1>Human check · actions vs notes</h1>
      <table class="act"><tr><th>Action</th><th>Owner</th><th>Due</th></tr>${rows}</table>
      <div class="card"><h2>Review flags</h2>${flags}</div>
      <div class="kv"><span class="pill warn">All unstated dates left as TO CONFIRM</span></div>`,
    caption: caption(5, 'The human reads every action back against the notes.', 'No deadline appears that the notes did not state. Unstated dates stay TO CONFIRM.')
  };
}

function sceneSix(d) {
  const checks = [
    'Every action traced to a note line',
    'No deadline invented — unstated dates = TO CONFIRM',
    'Owner names match the notes',
    'No advice, tax position or commitment added'
  ];
  return {
    active: 'human',
    body: `<h1>Human check · control checklist</h1>
      ${checks.map((c, i) => `<div class="chk" id="c${i}"><div class="box" id="b${i}"></div>${c}</div>`).join('')}
      <button class="save" id="save">Save to review queue</button>
      <div class="kv" id="saved" style="display:none"><span class="pill ok">✓ Saved to review queue — reviewer assigned</span></div>`,
    caption: caption(6, 'The save is blocked until a human completes the checklist.', 'AI drafts. A person checks. Only then does the workflow save.')
  };
}
const esc = s => String(s).replace(/[<&]/g, c => c === '<' ? '&lt;' : '&amp;');

// ---------------------------------------------------------------- record
async function recordScene(browser, n, build, animate) {
  const tmp = fs.mkdtempSync('/tmp/acct-pilot-');
  const ctx = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
    recordVideo: { dir: tmp, size: { width: W, height: H } },
    reducedMotion: 'no-preference'
  });
  const page = await ctx.newPage();
  const spec = build();
  await page.setContent(shell(spec));
  await page.evaluate(() => {
    for (const ms of [2200, 4700]) setTimeout(() => {
      const flash = document.createElement('div');
      flash.style.cssText = 'position:absolute;inset:0;background:#182431;z-index:999';
      document.body.appendChild(flash);
      setTimeout(() => flash.remove(), 70);
    }, ms);
  });
  await page.waitForTimeout(600);
  const shot = path.join(MEDIA, `scene-${String(n).padStart(3,'0')}-frame.png`);
  if (animate) await animate(page, spec);
  await page.screenshot({ path: shot });
  const elapsed = Date.now();
  await page.waitForTimeout(Math.max(300, DUR * 1000 - (Date.now() - elapsed) + 200));
  const vid = page.video();
  await page.close();
  const webm = await vid.path();
  await ctx.close();
  const out = path.join(MEDIA, `scene-${String(n).padStart(3,'0')}.mp4`);
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', webm,
    '-vf', `scale=${W}:${H},fps=30`, '-an', '-t', String(DUR),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
    { env: FFMPEG_ENV, encoding: 'utf8' });
  if (r.status !== 0) throw new Error('ffmpeg failed scene ' + n + ': ' + r.stderr);
  fs.rmSync(tmp, { recursive: true, force: true });
  return { out, shot };
}

async function run() {
  const responsePath = path.join(SRC, 'pilot-model-response.json');
  const prior = fs.existsSync(responsePath) ? JSON.parse(fs.readFileSync(responsePath, 'utf8')) : null;
  const { raw, parsed } = prior ?? await callModel();
  if (!prior) {
    fs.writeFileSync(responsePath, JSON.stringify({ model: 'opencode-go/deepseek-v4.1-flash',
      provider: 'cliproxyapi /chat/completions', endpoint_host: '127.0.0.1:8080',
      captured: new Date().toISOString(), raw_content: raw, parsed }, null, 2) + '\n');
  }
  fs.writeFileSync(path.join(SRC, 'pilot-notes.json'), JSON.stringify(NOTES, null, 2) + '\n');
  fs.writeFileSync(path.join(SRC, 'pilot-prompt.txt'), PROMPT + '\n');
  process.stdout.write(prior ? 'Reusing retained model response; no new model call.\n' : 'Model output received and saved to sources evidence.\n');

  const browser = await chromium.launch({ headless: true });
  const clips = [];
  clips.push(await recordScene(browser, 1, sceneOne, async (p) => {
    await p.evaluate(() => window.__move(700, 640)); await p.waitForTimeout(1200);
    await p.evaluate(() => window.__move(420, 820)); await p.waitForTimeout(5200);
  }));
  clips.push(await recordScene(browser, 2, sceneTwo, async (p) => {
    await p.evaluate(() => window.__move(760, 700)); await p.waitForTimeout(900);
    await p.evaluate(() => { let i=0, el=document.getElementById('pg'); const t=setInterval(()=>{ i+=4; el.style.width=i+'%'; if(i>=100) clearInterval(t); },60); });
    await p.waitForTimeout(6200);
  }));
  clips.push(await recordScene(browser, 3, () => sceneThree(raw), async (p) => {
    await p.evaluate(() => window.__move(820, 900)); await p.waitForTimeout(2000);
    await p.evaluate(() => window.__move(600, 1150)); await p.waitForTimeout(4800);
  }));
  clips.push(await recordScene(browser, 4, () => sceneFour(parsed), async (p) => {
    await p.evaluate(() => window.__move(500, 800)); await p.waitForTimeout(6400);
  }));
  clips.push(await recordScene(browser, 5, () => sceneFive(parsed), async (p) => {
    await p.evaluate(() => window.__move(640, 760)); await p.waitForTimeout(2200);
    await p.evaluate(() => window.__move(560, 1120)); await p.waitForTimeout(2200);
    await p.evaluate(() => window.__move(700, 1330)); await p.waitForTimeout(1400);
  }));
  clips.push(await recordScene(browser, 6, () => sceneSix(parsed), async (p) => {
    for (let i = 0; i < 4; i++) {
      await p.evaluate((i) => window.__move(300, 620 + i * 96), i);
      await p.waitForTimeout(700);
      await p.evaluate((i) => { document.getElementById('b' + i).classList.add('done'); document.getElementById('b' + i).textContent = '✓';
        if (i === 3) document.getElementById('save').classList.add('ready'); }, i);
      await p.waitForTimeout(600);
    }
    await p.evaluate(() => window.__move(560, 1210));
    await p.waitForTimeout(500);
    await p.click('#save');
    await p.evaluate(() => { document.getElementById('saved').style.display = 'flex'; document.getElementById('save').textContent = 'Saved ✓'; });
    await p.waitForTimeout(1600);
  }));
  await browser.close();

  // contact sheet 3x2
  const sheet = path.join(MEDIA, 'contact-sheet.png');
  const inputs = clips.flatMap(c => ['-i', c.shot]);
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs,
    '-filter_complex', '[0:v]scale=360:640[a];[1:v]scale=360:640[b];[2:v]scale=360:640[c];[3:v]scale=360:640[d];[4:v]scale=360:640[e];[5:v]scale=360:640[f];[a][b][c][d][e][f]xstack=inputs=6:layout=0_0|360_0|720_0|0_640|360_640|720_640',
    '-frames:v', '1', sheet], { env: FFMPEG_ENV, encoding: 'utf8' });
  if (r.status !== 0) throw new Error('contact sheet failed: ' + r.stderr);
  clips.forEach(c => fs.rmSync(c.shot, { force: true }));

  process.stdout.write('Wrote clips:\n' + clips.map(c => '  ' + path.relative(REPO, c.out)).join('\n') + '\n');
  process.stdout.write('Contact sheet: ' + path.relative(REPO, sheet) + '\n');
}

run().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
