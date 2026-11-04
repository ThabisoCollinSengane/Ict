// Deterministic frame renderer: node render.js --w=1280 --h=720 --out=frames/16x9 [--from=0 --to=720 | --frames=1,2,3]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const A = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')));
const W = +(A.w || 1280), H = +(A.h || 720), SS = +(A.ss || 1), out = A.out || 'frames/16x9';
const frames = A.frames ? A.frames.split(',').map(Number) : Array.from({ length: (+(A.to ?? 720)) - (+(A.from || 0)) }, (_, i) => i + (+(A.from || 0)));
const root = __dirname;
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(root, p);
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
srv.listen(0, '127.0.0.1', async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SS });
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) console.log('[page]', m.text().slice(0, 300)); });
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${srv.address().port}/index.html?w=${W}&h=${H}&ss=${SS}`);
  await page.waitForFunction('window.READY === true', null, { timeout: 300000 });
  fs.mkdirSync(out, { recursive: true });
  const t0 = Date.now();
  for (const [i, f] of frames.entries()) {
    await page.evaluate((f) => window.renderAt(f), f);
    await page.screenshot({ path: path.join(out, `f${String(f).padStart(4, '0')}.png`) });
    if (i % 24 === 0) console.log(`frame ${f} (${i + 1}/${frames.length}) ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
  console.log(`done ${frames.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await browser.close(); srv.close();
});
