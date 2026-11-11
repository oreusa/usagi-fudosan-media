/* 一瞬だけ映る乱れ（黒い四角・違う画面が一瞬出る・がたつき）を機械で探す。11/11 オーナー「変なのが一瞬映るとか全部確認。客に出すものだ」
   使い方: node tools/allcheck/flash.js http://localhost:8778 [night]   （links/ か akari の site/ を http.server で出してから）
   やる事: スマホ幅で各ページを開き、押せる物を1つずつ押して、押した直後 0.9 秒を 30ms ごとに撮る。
   「前後のコマは似ているのに、その1コマだけ大きく違う」＝一瞬の乱れ、として報告する。押した時の影（タップの印）が残っている部品も数える。 */
const {chromium} = require('playwright');
const BASE = process.argv[2] || 'http://localhost:8778', NIGHT = process.argv[3] === 'night';
const PAGES = (process.argv[4] ? process.argv[4].split(',') : ['/town-notes.html', '/index.html', '/fudosan-list.html', '/uru.html', '/kaitai.html', '/jikka/index.html', '/jikka/shindan/index.html', '/moushikomi.html', '/illumination.html', '/koyo.html', '/ima.html', '/tomari.html', '/ranking.html', '/chika-kansai.html', '/sagasu.html', '/koe.html']);
const SEL = 'button, [role=button], [role=tab], summary, label, svg .pf path, a[href^="#"], .chip, [data-k]:not(a[href^="http"]):not(a[href^="/"])';
function diff(a, b) { let n = 0; const L = Math.min(a.length, b.length); for (let i = 0; i < L; i += 16) { if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]) > 90) n++; } return n / (L / 16); }
(async () => {
  const b = await chromium.launch(); let bad = 0, taps = 0, hl = 0;
  for (const path of PAGES) {
    const c = await b.newContext({viewport: {width: 390, height: 844}, deviceScaleFactor: 1, hasTouch: true, isMobile: true});
    await c.addInitScript(n => { try { localStorage.setItem('usagi_theme', n ? 'night' : 'day'); localStorage.setItem('usagi_owner', '1'); } catch (e) {} }, NIGHT);
    const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**/c', r => r.fulfill({status: 204, body: ''}));
    const ok = await p.goto(BASE + path).then(r => r && r.status() < 400).catch(() => false);
    if (!ok) { console.log('－ 開けない', path); await c.close(); continue; }
    await p.waitForTimeout(1500);
    const cdp = await c.newCDPSession(p);
    const els = await p.evaluate(sel => { const out = []; const seen = new Set();
      document.querySelectorAll(sel).forEach((e, i) => { const r = e.getBoundingClientRect(); if (r.width < 8 || r.height < 8 || r.top < 0 || r.bottom > innerHeight || r.left < 0 || r.right > innerWidth) return;
        const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
        const k = e.tagName + '.' + (e.getAttribute('class') || '').split(' ')[0]; const n = (seen[k] = (seen[k] || 0) + 1); if (n > 2) return;
        const th = cs.webkitTapHighlightColor || cs.getPropertyValue('-webkit-tap-highlight-color');
        out.push({x: r.left + r.width / 2, y: r.top + r.height / 2, k, t: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 14), hl: th && !/rgba\(0, 0, 0, 0\)|transparent/.test(th)}); });
      return out; }, SEL);
    for (const e of els.slice(0, 14)) {
      if (e.hl) { hl++; console.log('△ 押した時の影が残る', path, e.k, e.t); }
      const frames = []; let on = true;
      const grab = (async () => { while (on) { try { const r = await cdp.send('Page.captureScreenshot', {format: 'jpeg', quality: 30}); frames.push(Buffer.from(r.data, 'base64')); } catch (x) { break; } await new Promise(r => setTimeout(r, 25)); } })();
      await p.waitForTimeout(120); const url0 = p.url();
      await p.touchscreen.tap(e.x, e.y).catch(() => {}); taps++;
      await p.waitForTimeout(900); on = false; await grab;
      // JPEG を生の点に直して、前後とくらべる
      const raw = await p.evaluate(async fs => { const out = []; for (const f of fs) { const im = await createImageBitmap(new Blob([Uint8Array.from(atob(f), ch => ch.charCodeAt(0))], {type: 'image/jpeg'})); const cv = new OffscreenCanvas(98, 211); const g = cv.getContext('2d'); g.drawImage(im, 0, 0, 98, 211); out.push(Array.from(g.getImageData(0, 0, 98, 211).data)); } return out; }, frames.map(f => f.toString('base64'))).catch(() => []);
      for (let i = 1; i + 1 < raw.length; i++) { const a = diff(raw[i - 1], raw[i]), d2 = diff(raw[i], raw[i + 1]), ac = diff(raw[i - 1], raw[i + 1]);
        if (a > 0.12 && d2 > 0.12 && ac < 0.03) { bad++; console.log('× 一瞬の乱れ', path, e.k, '「' + e.t + '」', 'コマ' + i, (a * 100).toFixed(0) + '%'); require('fs').writeFileSync((process.env.FLASH_OUT || '/tmp') + '/flash-' + bad + '.jpg', frames[i]); break; } }
      if (p.url() !== url0) { await p.goto(BASE + path).catch(() => {}); await p.waitForTimeout(1200); }
      else { await p.keyboard.press('Escape').catch(() => {}); await p.evaluate(() => { const x = document.querySelector('.msheet.on .x, .mclose, [data-close]'); if (x) x.click(); }).catch(() => {}); await p.waitForTimeout(250); }
    }
    if (errs.length) { bad++; console.log('× 動きのエラー', path, errs[0].slice(0, 120)); }
    await c.close();
  }
  await b.close(); console.log(`flash: 押した数 ${taps}／一瞬の乱れ ${bad}／影が残る部品 ${hl}`); process.exit(bad ? 1 : 0);
})();
