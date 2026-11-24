// node render.mjs <port> <out.mp4> <soundtrack.wav> [--sub 3] [--from s] [--to s]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
const { chromium } = createRequire(import.meta.url)('playwright');
const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? Number(args[i + 1]) : d; };
const [port, out, audio] = args;
const fps = 30, sub = opt('sub', 3), shutter = 0.5;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
await page.goto(`http://127.0.0.1:${port}/bread.html`);
await page.evaluate(() => window.ready);
const duration = await page.evaluate(() => window.DURATION);
const from = opt('from', 0), to = opt('to', duration);
const f0 = Math.round(from * fps), f1 = Math.round(to * fps);
const vf = `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB),format=yuv420p`;
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps * sub), '-c:v', 'mjpeg', '-i', '-',
  '-ss', String(from), '-t', String(to - from), '-i', audio, '-vf', vf, '-r', String(fps),
  '-map', '0:v', '-map', '1:a', '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', '-shortest',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-tune', 'animation', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const t0 = Date.now();
for (let f = f0; f < f1; f++) {
  for (let j = 0; j < sub; j++) {
    const t = (f + ((j + 0.5) / sub - 0.5) * shutter) / fps;
    await page.evaluate(async (t) => { await window.seek(Math.max(0, t)); }, t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  if ((f - f0) % 150 === 0) console.log(`frame ${f - f0}/${f1 - f0} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
console.log('wrote', out);
