/* 一瞬だけ映る乱れ（黒い四角・違う画面が一瞬出る・がたつき）を機械で探す。11/11 オーナー「変なのが一瞬映るとか全部確認。客に出すものだ」
   使い方: node tools/allcheck/flash.js http://localhost:8778 [day|night] [/a.html,/b.html]   （links/ か akari の site/ を http.server で出してから）
   やる事: スマホ幅で各ページを開き、押せる物を1つずつ押して、押した直後の約1秒を続けて撮る。
   「前後のコマは似ているのに、その1コマだけ大きく違う」＝一瞬の乱れ、として報告する（コマは FLASH_OUT に残し、続けて python3 tools/allcheck/flash.py <FLASH_OUT> で見くらべる）。動きのエラーも報告する。
   注意: これは Chromium の点検。iPhone の Safari だけで出る物（押した時の影など）は tech.css の決まりで消している。 */
const {chromium} = require('playwright'); const fs = require('fs'); const idx = [];
const BASE = process.argv[2] || 'http://localhost:8778', NIGHT = process.argv[3] === 'night';
const PAGES = process.argv[4] ? process.argv[4].split(',') : ['/town-notes.html', '/index.html', '/fudosan-list.html', '/uru.html', '/kaitai.html', '/jikka/index.html', '/jikka/shindan/index.html', '/moushikomi.html', '/illumination.html', '/koyo.html', '/ima.html', '/tomari.html', '/ranking.html', '/chika-kansai.html', '/sagasu.html', '/koe.html'];
const OUT = process.env.FLASH_OUT || '/tmp';
(async () => {
  const b = await chromium.launch(); let bad = 0, taps = 0;
  for (const path of PAGES) {
    const c = await b.newContext({viewport: {width: 390, height: 844}, deviceScaleFactor: 0.25, hasTouch: true, isMobile: true});
    await c.addInitScript(n => { try { localStorage.setItem('usagi_theme', n ? 'night' : 'day'); localStorage.setItem('usagi_owner', '1'); } catch (e) {} window.open = () => null; }, NIGHT);
    c.on('page', np => { if (c.pages().length > 1) np.close().catch(() => {}); });
    let p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**/c', r => r.fulfill({status: 204, body: ''}));
    const open = async () => { const r = await p.goto(BASE + path).catch(() => null); await p.waitForTimeout(1300).catch(() => {}); return r && r.status() < 400; };
    if (!await open()) { console.log('－ 開けない', path); await c.close(); continue; }
    const list = () => p.evaluate(() => { const out = [], seen = {};
      document.querySelectorAll('button,[role=button],[role=tab],summary,label,select,svg .pf path,a[href^="#"]').forEach(e => { const r = e.getBoundingClientRect(); if (r.width < 8 || r.height < 8 || r.top < 0 || r.bottom > innerHeight || r.left < 0 || r.right > innerWidth) return;
        const cs = getComputedStyle(e); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
        const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (!top || !(e === top || e.contains(top) || top.contains(e))) return;
        const k = e.tagName.toLowerCase() + '.' + (e.getAttribute('class') || '').split(' ')[0]; seen[k] = (seen[k] || 0) + 1; if (seen[k] > 2) return;
        out.push({x: r.left + r.width / 2, y: r.top + r.height / 2, k, t: (e.textContent || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 14)}); });
      return out; }).catch(() => []);
    const els = (await list()).slice(0, 10); console.log('・', path, '押す物', els.length);
    for (const e of els) {
      try {
        const frames = []; const t0 = Date.now(); let tapped = false;
        while (Date.now() - t0 < 1300 && frames.length < 26) { frames.push(await p.screenshot({type: 'png'}));
          if (!tapped && Date.now() - t0 > 150) { tapped = true; taps++; p.touchscreen.tap(e.x, e.y).catch(() => {}); } }
        const id = path.replace(/\W/g, '') + '-' + els.indexOf(e); frames.forEach((f, j) => fs.writeFileSync(`${OUT}/f-${id}-${String(j).padStart(2, '0')}.png`, f)); idx.push({id, path, k: e.k, t: e.t, n: frames.length});
      } catch (x) { console.log('－ 押せなかった', path, e.k, String(x.message).slice(0, 60)); }
      if (p.isClosed()) { p = await c.newPage(); await p.route('**/c', r => r.fulfill({status: 204, body: ''})); }
      await open();
    }
    if (errs.length) { bad++; console.log('× 動きのエラー', path, errs[0].slice(0, 140)); }
    await c.close().catch(() => {});
  }
  await b.close(); fs.writeFileSync(OUT + '/index.json', JSON.stringify(idx)); console.log(`flash: 押した数 ${taps}／動きのエラー ${bad}（コマの見くらべは flash.py）`);
})();
