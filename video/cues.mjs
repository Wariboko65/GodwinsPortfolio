// Prints the sound cues registered by motion.html (each with its time, kind and on-screen
// x position for panning) plus the music timeline, as JSON. build_audio.py runs this.
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.join(here, 'motion.html')).href);
await page.evaluate(() => window.ready);
const data = await page.evaluate(() => ({ timeline: window.TIMELINE, cues: window.resolveCues() }));
console.log(JSON.stringify(data));
await browser.close();
