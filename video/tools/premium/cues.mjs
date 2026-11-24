import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto(`http://127.0.0.1:${process.argv[2]}/bread.html`);
await page.evaluate(() => window.ready);
console.log(JSON.stringify(await page.evaluate(() => ({ duration: window.DURATION, cues: window.CUES }))));
await browser.close();
