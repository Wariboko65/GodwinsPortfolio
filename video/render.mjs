// Renders explainer.html to an MP4, frame by frame.
// Usage: node video/render.mjs [output.mp4] [fps] [soundtrack.wav]
// Needs Playwright (Chromium) and ffmpeg. Fonts come from node_modules, so run `npm install` first.
// Build the soundtrack (and timeline.js, which sets the scene timings) first with build_audio.py.
// With a soundtrack, the audio is normalised to -16 LUFS and muxed in as AAC.
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const out = process.argv[2] || path.join(here, 'portfolio-explainer.mp4');
const fps = Number(process.argv[3] || 30);
const audio = process.argv[4];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(here, 'explainer.html')).href);
await page.evaluate(() => window.ready);
const duration = await page.evaluate(() => window.DURATION);
const frames = Math.round(duration * fps);

const audioArgs = audio
  ? ['-i', audio, '-map', '0:v', '-map', '1:a', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest']
  : [];
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
  ...audioArgs, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });

for (let f = 0; f < frames; f++) {
  await page.evaluate((t) => window.seek(t), f / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (f % (fps * 5) === 0) console.log(`frame ${f}/${frames}`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
console.log('wrote', out);
