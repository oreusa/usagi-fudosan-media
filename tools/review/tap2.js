// 11/20 新しい土台の見回り：ページの中のリンクを全部ひらいて確かめ（404・前の見た目のページ）、下のバー・MENU・タブを実際に押して、戻るで元に戻るかを見る
// node tools/review/tap2.js <URLの一覧ファイル>  → 1行ずつ（✗ が直す所）
const {chromium, devices} = require('playwright');
const fs = require('fs');
(async () => {
  const L = fs.readFileSync(process.argv[2], 'utf8').split('\n').map(s => s.trim()).filter(Boolean)
    .map(s => { const a = s.split('\t'); return a.length > 1 ? [a[0], a[1]] : [a[0], a[0]]; });
  const b = await chromium.launch();
  const c = await b.newContext({...devices['iPhone 13'], deviceScaleFactor: 1});
  const seen = new Map(); let bad = 0;
  const W = ms => new Promise(r => setTimeout(r, ms));
  const chk = async u => {
    if (seen.has(u)) return seen.get(u);
    let r;
    try {
      const x = await c.request.get(u, {timeout: 20000, maxRedirects: 5});
      const ct = x.headers()['content-type'] || '';
      const t = x.status() < 400 && /text\/html/.test(ct) ? await x.text() : '';
      r = {s: x.status(), old: !!t && !/\/shin\/(shin|kyu)\.css|data-kyu|skin\.js|id="sk"/.test(t)};
    } catch (e) { r = {s: 'ERR ' + String(e).slice(0, 60)}; }
    seen.set(u, r); return r;
  };
  for (const [nm, url] of L) {
    const p = await c.newPage(); const err = [];
    p.on('pageerror', e => { if (!/Transition was (aborted|skipped)/.test(String(e))) err.push(String(e).slice(0, 120)); });
    const o = []; const X = m => { o.push('  ✗ ' + m); bad++; };
    try { await p.goto(url, {waitUntil: 'load', timeout: 40000}); } catch (e) { X('開けない ' + e); }
    await W(1500);
    const home = new URL(p.url()).pathname; const origin = new URL(url).origin;
    // 1 ページの中のリンクを全部
    const hrefs = await p.$$eval('a[href]', as => [...new Set(as.map(a => a.href))]);
    const inn = [...new Set(hrefs.filter(h => h.startsWith(origin)).map(h => h.split('#')[0]))].slice(0, +(process.env.MAXL || 80));
    for (const h of inn) {
      const r = await chk(h);
      if (r.s !== 200) X('リンク ' + r.s + ' ' + h.replace(origin, ''));
      else if (r.old) X('前の見た目のページ ' + h.replace(origin, ''));
    }
    o.push('  リンク ' + inn.length + '本（外 ' + hrefs.filter(h => !h.startsWith(origin)).length + '本）');
    // 2 下のバー
    const nav = await p.$$eval('#nav a[href]', as => as.map(a => a.getAttribute('href')));
    for (const h of nav) {
      await p.goto(url, {waitUntil: 'load'}).catch(() => {}); await W(900);
      const e = await p.$(`#nav a[href="${h}"]`);
      if (!e || !(await e.isVisible())) { X('バーの ' + h + ' が見えない'); continue; }
      const tok = await Promise.all([p.waitForNavigation({timeout: 10000}).catch(() => {}), e.tap({timeout: 8000}).then(() => 1, () => 0)]); await W(1200);
      if (!tok[1]) { X('バーの ' + h + ' が押せない（他の物が上に重なっている）'); continue; }
      const to = new URL(p.url());
      if (!(await p.$('#nav'))) X('バー ' + h + ' の先に下のバーが無い ' + to.pathname);
      await p.goBack().catch(() => {}); await W(1000);
      const back = new URL(p.url()).pathname;
      if (back !== home && to.pathname !== home) X('バー ' + h + ' から戻るで元に戻らない（' + back + '）');
    }
    if (nav.length) o.push('  下のバー ' + nav.length + '個を押した');
    // 3 MENU
    await p.goto(url, {waitUntil: 'load'}).catch(() => {}); await W(900);
    const mb = await p.$('#mnb');
    if (mb) {
      await mb.tap({timeout: 8000}).catch(() => X('MENU が押せない（他の物が上に重なっている）')); await W(800);
      const vis = await p.evaluate(() => {
        const m = document.getElementById('mu'); if (!m) return 0;
        const pn = m.querySelector('.pn') || m; const r = pn.getBoundingClientRect();
        return r.width > 0 && r.bottom > 0 && r.top < innerHeight && getComputedStyle(m).visibility !== 'hidden' ? m.querySelectorAll('a[href]').length : 0;
      });
      if (!vis) X('MENU を押しても開かない'); else o.push('  MENU 開く・中のリンク ' + vis + '本');
    } else X('MENU が無い');
    // 4 タブ
    await p.goto(url, {waitUntil: 'load'}).catch(() => {}); await W(900);
    const tabs = await p.$$('[role=tab]:not([aria-selected=true])'); let nt = 0;
    for (const t of tabs.slice(0, 8)) { if (await t.isVisible()) { await t.tap().catch(() => {}); await W(350); nt++; } }
    if (nt) o.push('  タブ ' + nt + '個を押した');
    // 5 横にはみ出し・JSのエラー
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (ov > 1) X('横にはみ出し ' + ov + 'px');
    if (err.length) X('JSのエラー ' + [...new Set(err)].join(' | '));
    console.log('■ ' + nm + ' ' + url + (o.some(x => x.includes('✗')) ? '' : '  ✓') + '\n' + o.join('\n'));
    await p.close();
  }
  console.log('✗ の数 ' + bad); await b.close();
})();
