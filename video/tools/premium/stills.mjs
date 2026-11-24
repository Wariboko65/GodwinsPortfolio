// node stills.mjs <port> <outdir> t1 t2 ...  (serve this folder on <port> first)
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [port, dir, ...times] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
await page.goto(`http://127.0.0.1:${port}/bread.html`);
await page.evaluate(() => window.ready);
for (const t of times) { await page.evaluate(async (t) => { await window.seek(t); }, +t); await page.screenshot({ path: `${dir}/s-${t}.png` }); }
await browser.close();
