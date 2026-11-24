// Reads every animation in explainer.html and prints the sound cues as JSON, so the sound
// effects come from the same numbers that drive the picture.
// Each cue: { t, kind, x (0 = left edge, 1 = right edge, for stereo panning), ... }
// Usage: node video/cues.mjs > cues.json   (build_audio.py runs this itself)
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.join(here, 'explainer.html')).href);
await page.evaluate(() => window.ready);

const cues = await page.evaluate(() => {
  const out = [];
  const W = 1920;
  const sections = [...document.querySelectorAll('.scene')];
  const kindOf = (el) => {
    if (el.matches('#wall img')) return 'tile';
    if (el.matches('.ph, .wph')) return 'photo';
    if (el.matches('li')) return 'item';
    if (el.matches('.node')) return 'node';
    if (el.matches('.card')) return 'card';
    if (el.matches('.half')) return 'panel';
    if (el.matches('#s8 .url')) return 'cta';
    if (el.matches('.plastic')) return 'stat';
    if (el.matches('.big, .kg')) return null; // the counter inside makes the sound
    if (el.matches('h1 span, h2, .name')) return 'title';
    return 'small';
  };
  sections.forEach((sec, si) => {
    const start = +sec.dataset.start;
    const end = +sec.dataset.end;
    window.seek(end - 0.4); // measure positions with everything in place
    const cx = (el) => { const r = el.getBoundingClientRect(); return (r.left + r.width / 2) / W; };
    for (const el of sec.querySelectorAll('[data-in]')) {
      const kind = kindOf(el);
      if (!kind) continue;
      out.push({ t: start + +el.dataset.in, kind, x: cx(el), scene: si, dur: +(el.dataset.dur || 0.7),
        size: el.getBoundingClientRect().height });
    }
    [...sec.querySelectorAll('[data-lit]')].forEach((el, i) =>
      out.push({ t: start + +el.dataset.lit, kind: 'lit', x: cx(el), scene: si, index: i }));
    for (const el of sec.querySelectorAll('[data-line]')) {
      const r = el.getBoundingClientRect();
      out.push({ t: start + +el.dataset.line, kind: 'wire', x: r.left / W, x1: r.right / W, scene: si, dur: 0.5 });
    }
    for (const el of sec.querySelectorAll('[data-count]')) {
      out.push({ t: start + +el.dataset.countIn, kind: 'count', x: cx(el), scene: si, value: +el.dataset.count,
        dec: +(el.dataset.dec || 0), dur: +el.dataset.countDur });
    }
    [...sec.querySelectorAll('[data-bar]')].forEach((el, i) => {
      const r = el.parentElement.getBoundingClientRect();
      out.push({ t: start + +el.dataset.barIn, kind: 'bar', x: r.left / W, x1: (r.left + r.width * +el.dataset.bar / 100) / W,
        scene: si, pct: +el.dataset.bar, dur: 1.2, index: i });
    });
  });
  return out.sort((a, b) => a.t - b.t);
});

console.log(JSON.stringify(cues));
await browser.close();
