// Saves PNG stills of motion.html at given times: node video/stills-motion.mjs outdir h|v t1 t2 ...
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const [dir, fmt, ...times] = process.argv.slice(2);
const v = fmt === 'v';
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: v ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 } });
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
await page.goto(pathToFileURL(path.join(here, 'motion.html')).href + (v ? '?v' : ''));
await page.evaluate(() => window.ready);
for (const t of times) { await page.evaluate((t) => window.seek(t), +t); await page.screenshot({ path: path.join(dir, `${fmt}-${t}.png`) }); }
await browser.close();
