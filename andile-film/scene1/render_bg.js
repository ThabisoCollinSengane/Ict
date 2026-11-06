// Renders call-centre background plates: node render_bg.js --shot=N1 --out=DIR [--from=0 --to=100 | --frames=0]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const A = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')));
const W = +(A.w || 1920), H = +(A.h || 1080), shot = A.shot || 'N1', out = A.out;
const frames = A.frames ? A.frames.split(',').map(Number) : Array.from({ length: +A.to - +(A.from || 0) }, (_, i) => i + +(A.from || 0));
const root = path.join(__dirname, '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});
srv.listen(0, '127.0.0.1', async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.log('[page]', m.text().slice(0, 200)); });
  await page.goto(`http://127.0.0.1:${srv.address().port}/scene1/bg.html?shot=${shot}&w=${W}&h=${H}`);
  await page.waitForFunction('window.READY === true', null, { timeout: 300000 });
  fs.mkdirSync(out, { recursive: true });
  const t0 = Date.now();
  for (const f of frames) { await page.evaluate((f) => window.renderAt(f), f); await page.screenshot({ path: path.join(out, `f${String(f).padStart(4, '0')}.png`) }); }
  console.log(`${shot}: ${frames.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  await browser.close(); srv.close();
});
