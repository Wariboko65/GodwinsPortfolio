// Saves one PNG per given time, for checking layout: node video/stills.mjs outdir 2 8 15 ...
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const here = path.dirname(fileURLToPath(import.meta.url));
const [dir, ...times] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.join(here, 'explainer.html')).href);
await page.evaluate(() => window.ready);
for (const t of times) { await page.evaluate((t) => window.seek(t), +t); await page.screenshot({ path: path.join(dir, `t${t}.png`) }); }
await browser.close();
