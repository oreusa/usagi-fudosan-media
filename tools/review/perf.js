// 11/27 owner「全体的に動作スムーズじゃない気する」：本番をスマホと同じ条件（CPU 4倍遅い・4G）で開いて、重い所を数字で出す。
// 使い方: node tools/review/perf.js 一覧.txt 出力フォルダ   （一覧は1行1URL。タブ区切りの1列目だけ使う）
// 出す物: perf.json（ページごと：表示までの時間 LCP・押せるまでの固まり TBT・ずれ CLS・JS/CSS/画像の量・数・下へ流した時のカクつき）
const {chromium, devices} = require('playwright');
const fs = require('fs');
const [list, out] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const urls = fs.readFileSync(list, 'utf8').split('\n').map(l => l.split('\t')[0].trim()).filter(u => /^https?:/.test(u));
(async () => {
  const b = await chromium.launch();
  const res = [];
  for (const u of urls) {
    const c = await b.newContext({...devices['iPhone 13']});
    const p = await c.newPage();
    const cdp = await c.newCDPSession(p);
    await cdp.send('Emulation.setCPUThrottlingRate', {rate: 4});
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', {offline: false, latency: 150, downloadThroughput: 1.6e6 / 8, uploadThroughput: 750e3 / 8});
    const bytes = {js: 0, css: 0, img: 0, font: 0, other: 0}, cnt = {js: 0, css: 0, img: 0, font: 0, other: 0}, big = [];
    p.on('response', async r => {
      try {
        const t = r.request().resourceType(), k = t === 'script' ? 'js' : t === 'stylesheet' ? 'css' : t === 'image' ? 'img' : t === 'font' ? 'font' : 'other';
        const l = +(r.headers()['content-length'] || 0) || (await r.body().catch(() => Buffer.alloc(0))).length;
        bytes[k] += l; cnt[k]++; if (l > 150e3) big.push([Math.round(l / 1e3), r.url().slice(0, 140)]);
      } catch (e) {}
    });
    await p.addInitScript(() => {
      window.__lcp = 0; window.__cls = 0; window.__lt = [];
      new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime }).observe({type: 'largest-contentful-paint', buffered: true});
      new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value }).observe({type: 'layout-shift', buffered: true});
      new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push([Math.round(e.startTime), Math.round(e.duration)]) }).observe({type: 'longtask', buffered: true});
    });
    const t0 = Date.now(); let err = '';
    try { await p.goto(u, {waitUntil: 'load', timeout: 60000}) } catch (e) { err = e.message.slice(0, 120) }
    const loadMs = Date.now() - t0;
    await p.waitForTimeout(3000);
    const m1 = await p.evaluate(() => ({lcp: Math.round(window.__lcp), cls: +window.__cls.toFixed(3), lt: window.__lt.slice(), dom: document.getElementsByTagName('*').length, imgs: document.images.length}));
    // 下へ流した時のカクつき：1秒に60回の絵のうち、50ms以上あいた回数
    const jank = await p.evaluate(async () => {
      const gaps = []; let last = performance.now(), run = true;
      const f = t => { gaps.push(t - last); last = t; if (run) requestAnimationFrame(f) }; requestAnimationFrame(f);
      for (let i = 0; i < 12; i++) { window.scrollBy(0, 500); await new Promise(r => setTimeout(r, 160)) }
      run = false; await new Promise(r => setTimeout(r, 100));
      const g = gaps.slice(2);
      return {frames: g.length, slow: g.filter(x => x > 50).length, worst: Math.round(Math.max(0, ...g))};
    });
    const tbt = m1.lt.reduce((s, x) => s + Math.max(0, x[1] - 50), 0);
    const r = {url: u, err, loadMs, lcp: m1.lcp, tbt, cls: m1.cls, longtasks: m1.lt.length, worstTask: Math.max(0, ...m1.lt.map(x => x[1])),
      kb: Object.fromEntries(Object.entries(bytes).map(([k, v]) => [k, Math.round(v / 1e3)])), cnt, dom: m1.dom, imgs: m1.imgs, scroll: jank, big: big.sort((a, b) => b[0] - a[0]).slice(0, 6)};
    res.push(r);
    console.log(JSON.stringify({u: u.replace(/^https:\/\//, ''), lcp: r.lcp, tbt, cls: r.cls, js: r.kb.js, img: r.kb.img, dom: r.dom, slow: jank.slow + '/' + jank.frames, worst: jank.worst}));
    await c.close();
  }
  fs.writeFileSync(out + '/perf.json', JSON.stringify(res, null, 1));
  await b.close();
})();
