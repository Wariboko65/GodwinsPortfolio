// Renders motion.html to MP4 with real motion blur: each output frame is the average of
// several sub-frames spread across a 200° shutter, then light film grain is added.
//
// Usage: node video/render-motion.mjs <h|v> <out.mp4> [soundtrack.wav] [--sub 6] [--from 0] [--to 30]
//   h = 16:9 (1920×1080), v = 9:16 (1080×1920)
// Build the soundtrack first: python3 video/build_audio.py soundtrack.wav
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf('--' + name); return i >= 0 ? Number(args[i + 1]) : def; };
const pos = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
const [fmt, out, audio] = pos;
const v = fmt === 'v';
const fps = 30;
const sub = opt('sub', 6);
const shutter = 200 / 360;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: v ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 } });
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
await page.goto(pathToFileURL(path.join(here, 'motion.html')).href + (v ? '?v' : ''));
await page.evaluate(() => window.ready);
const duration = await page.evaluate(() => window.DURATION);
const from = opt('from', 0), to = opt('to', duration);
const f0 = Math.round(from * fps), f1 = Math.round(to * fps);

const vf = `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB),noise=alls=5:allf=t,hqdn3d=1.5:1.5:8:8,format=yuv420p`; // grain, then calm its frame-to-frame flicker so the file stays ~30 MB
const audioIn = audio ? ['-ss', String(from), '-t', String(to - from), '-i', audio] : [];
const audioOut = audio ? ['-map', '0:v', '-map', '1:a', '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9', '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', '-shortest'] : [];
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps * sub), '-c:v', 'mjpeg', '-i', '-',
  ...audioIn, '-vf', vf, '-r', String(fps), ...audioOut,
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });

const started = Date.now();
for (let f = f0; f < f1; f++) {
  for (let j = 0; j < sub; j++) {
    const t = (f + ((j + 0.5) / sub - 0.5) * shutter) / fps;
    await page.evaluate((t) => window.seek(Math.max(0, t)), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  if ((f - f0) % 60 === 0) console.log(`${fmt} frame ${f - f0}/${f1 - f0}  ${((Date.now() - started) / 1000).toFixed(0)}s`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
console.log('wrote', out);
