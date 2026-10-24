// Serve site/ and capture frames from video.html with headless Chromium.
//   node scripts/capture.mjs frames OUT_DIR FPS T0 T1      every frame in [T0, T1)
//   node scripts/capture.mjs stills OUT_DIR t1 t2 ...       named stills (t-<time>.png)
//   node scripts/capture.mjs insta OUT_DIR design ...       Instagram stills from insta.html (<design>.png)
//   node scripts/capture.mjs ads OUT_DIR 1 2 ... | all     static ads from ads.html (ad-NN.png)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { playwright = require(require.resolve('playwright', { paths: ['/usr/local/lib/node_modules', '/opt/node22/lib/node_modules'] })); }

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'site');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf', '.bin': 'application/octet-stream' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const [mode, out, ...rest] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const browser = await playwright.chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
if (mode === 'ads') {
  const ns = rest[0] === 'all' ? Array.from({ length: Number(process.env.ADS || 34) }, (_, i) => i + 1) : rest.map(Number);
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.log('[pageerror]', e.message));
  for (const n of ns) {
    await p.goto(`http://127.0.0.1:${port}/ads.html?n=${n}`);
    await p.waitForFunction('window.__ready === true', null, { timeout: 300000 });
    const { W, H } = await p.evaluate(() => window.STAGE);
    await p.screenshot({ path: path.join(out, `ad-${String(n).padStart(2, '0')}.png`), clip: { x: 0, y: 0, width: W, height: H } });
  }
  console.log('wrote', ns.length, 'ads');
  await browser.close();
  server.close();
  process.exit(0);
}
if (mode === 'insta') {
  for (const d of rest) {
    const [w, h] = d.startsWith('story') ? [1080, 1920] : d.startsWith('square') ? [1080, 1080] : [1080, 1350];
    const p = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    p.on('pageerror', e => console.log('[pageerror]', e.message));
    await p.goto(`http://127.0.0.1:${port}/insta.html?d=${d}`);
    await p.waitForFunction('window.__ready === true', null, { timeout: 300000 });
    await p.screenshot({ path: path.join(out, `${d}.png`) });
    await p.close();
    console.log('wrote', d);
  }
  await browser.close();
  server.close();
  process.exit(0);
}
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.goto(`http://127.0.0.1:${port}/${process.env.PAGE || 'video.html'}`);   // PAGE=promo.html for the v2 film
await page.waitForFunction('window.__ready === true', null, { timeout: 300000 });

const shot = async (t, file) => {
  await page.evaluate(t => window.renderAt(t), t);
  await page.screenshot({ path: file, type: file.endsWith('.jpg') ? 'jpeg' : 'png', quality: file.endsWith('.jpg') ? 95 : undefined });
};

const t0 = Date.now();
if (mode === 'frames') {
  const [fps, a, b] = rest.map(Number);
  const n0 = Math.round(a * fps), n1 = Math.round(b * fps);
  for (let n = n0; n < n1; n++) {
    await shot(n / fps, path.join(out, `f${String(n).padStart(5, '0')}.png`));
    if (n % 30 === 0) console.log(`frame ${n}/${n1} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
} else {
  for (const t of rest.map(Number)) await shot(t, path.join(out, `t-${t.toFixed(2)}.png`));
}
console.log(`done in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
await browser.close();
server.close();
