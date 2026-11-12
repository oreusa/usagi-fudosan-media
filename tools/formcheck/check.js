/* 申し込みが本番で最後まで送れるかを、スマホの幅で通しで確かめる（11/12 オーナー「一つ一つ完璧な仕組みにしろ」）。
   本番のページを開き、押す→書く→送信まで実際に動かす。送信の2つの宛先だけは横取りして、本当には送らない（オーナーにメールは行かない・数にも入らない）。
   結果は stats/formcheck.json。台帳（tools/seichou/gakushu.py）が読み、だめなら月の朝の1番目の指令になる。
   使い方: node tools/formcheck/check.js [out.json] [関西のURL] [関東のURL]（手元の確かめは URL に http://localhost:... を渡す） */
const { chromium } = require('playwright'); const fs = require('fs');
const OUT = process.argv[2] || 'stats/formcheck.json';
const SITES = [['kansai', process.argv[3] || 'https://townnote.pages.dev'], ['kanto', process.argv[4] || 'https://lifenote-kanto.pages.dev']];
const step = p => p.evaluate(() => { const b = document.querySelector('.tkst b'); return b ? b.textContent : ''; });
async function run(b, base, name, path, fn) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
  await ctx.addInitScript(() => { try { localStorage.setItem('usagi_owner', '1'); } catch (e) {} });
  const p = await ctx.newPage(); const posts = [], errs = [];
  p.on('pageerror', e => errs.push(String(e.message).slice(0, 120)));
  await p.route(/moushikomi-send|formsubmit\.co/, r => { posts.push(r.request().postData() || ''); r.fulfill({ status: 200, contentType: 'application/json', body: '{"success":"true"}' }); });
  await p.route(/\/c$/, r => r.fulfill({ status: 204, body: '' }));
  const res = { name, path, ok: false, why: '' };
  try {
    await p.goto(base + path, { waitUntil: 'domcontentloaded', timeout: 45000 }); await p.waitForTimeout(2500);
    await fn(p, res);
    if (!res.why) {
      await p.click('#sb'); await p.waitForTimeout(1500);
      const done = await p.isVisible('#done'); const body = posts.join('\n');
      if (!done) res.why = '送信の後に「受け付けました」が出ない：' + (await p.textContent('#er').catch(() => '')).slice(0, 60);
      else if (posts.length < 2) res.why = '送り先が2つ呼ばれていない（' + posts.length + '）';
      else for (const w of res.must || []) if (!body.includes(w)) { res.why = '届く中身に「' + w + '」が無い'; break; }
      if (!res.why) res.ok = true;
    }
  } catch (e) { res.why = '途中で止まった：' + String(e.message).split('\n')[0].slice(0, 140); }
  if (errs.length) res.errs = errs.slice(0, 3);
  delete res.must; await ctx.close(); return res;
}
(async () => {
  const b = await chromium.launch(); const out = { at: new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 16).replace('T', ' '), sites: {} };
  for (const [key, base] of SITES) {
    const rs = [];
    rs.push(await run(b, base, 'ふつうの申し込み（3つの画面）', '/moushikomi', async (p, r) => {
      r.must = ['テスト太郎', '確かめ市', '査定してほしい', '午後'];
      if (await step(p) !== '1') { r.why = '最初の画面が1つ目になっていない'; return; }
      await p.check('input[name=want][value="査定してほしい"]'); await p.waitForTimeout(900);
      if (await step(p) !== '2') { r.why = 'ご希望を押しても次の画面へ進まない'; return; }
      await p.fill('#pl', '確かめ市'); await p.click('.tks.on .tknx'); await p.waitForTimeout(700);
      if (await step(p) !== '3') { r.why = '場所を書いて「次へ」を押しても連絡先の画面へ進まない'; return; }
      await p.fill('#nm', 'テスト太郎'); await p.fill('#tl', '09000000000'); await p.waitForTimeout(300);
      await p.check('input[name=ttime][value="午後"]'); await p.check('#ag');
    }));
    rs.push(await run(b, base, 'かんたん相談（1つの画面）', '/moushikomi?lite=1', async (p, r) => {
      r.must = ['テスト太郎', '確かめ市', 'かんたん相談'];
      await p.fill('#pl', '確かめ市'); await p.fill('#nm', 'テスト太郎'); await p.fill('#tl', '09000000000'); await p.check('#ag');
    }));
    rs.push(await run(b, base, 'ご希望を選んで来た人（2つ目の画面から）', '/moushikomi?want=' + encodeURIComponent('解体の見積り'), async (p, r) => {
      r.must = ['テスト太郎', '確かめ市', '解体'];
      if (await step(p) !== '2') { r.why = 'ご希望つきで来たのに、2つ目の画面から始まらない'; return; }
      await p.fill('#pl', '確かめ市'); await p.click('.tks.on .tknx'); await p.waitForTimeout(700);
      await p.fill('#nm', 'テスト太郎'); await p.fill('#em', 'test@example.com'); await p.check('#ag');
    }));
    out.sites[key] = { base, ok: rs.every(x => x.ok), rows: rs };
  }
  out.ok = Object.values(out.sites).every(s => s.ok);
  fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1)); await b.close();
})();
