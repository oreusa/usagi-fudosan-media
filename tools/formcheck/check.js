/* 申し込みが本番で最後まで送れるかを、スマホの幅で通しで確かめる（11/12 オーナー「一つ一つ完璧な仕組みにしろ」）。
   本番のページを開き、押す→書く→送信まで実際に動かす。送信の2つの宛先だけは横取りして、本当には送らない（オーナーにメールは行かない・数にも入らない）。
   結果は stats/formcheck.json。台帳（tools/seichou/gakushu.py）が読み、だめなら月の朝の1番目の指令になる。
   使い方: node tools/formcheck/check.js [out.json] [関西のURL] [関東のURL]（手元の確かめは URL に http://localhost:... を渡す） */
const { chromium } = require('playwright'); const fs = require('fs');
const OUT = process.argv[2] || 'stats/formcheck.json';
const SITES = [['kansai', process.argv[3] || 'https://kansai.townnote.app'], ['kanto', process.argv[4] || 'https://kanto.townnote.app']];
// 11/20：新しい見た目（/shin/skin.js）で丸・四角の入力そのものは透明になり、人はその文字（label）を押す。input を直に押すと「止まって見えない」で30秒待って落ちていた（11/19 18時〜）。人と同じく label を押し、無ければ force で押す。
const tick = (p, sel) => p.click('label:has(' + sel + ')', { timeout: 8000 }).catch(() => p.check(sel, { force: true }));
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
    // 11/23 owner「収益化が何一つ上手くいってない」→ 1画面目を3問（ご用件・お家の場所・ご連絡先）に。お名前・種類・内容は「ほかにも書く（任意）」。
    const MP = process.env.MK_PATH || '/moushikomi';
    rs.push(await run(b, base, 'ふつうの申し込み（1画面・3問）', MP, async (p, r) => {
      r.must = ['確かめ市', '査定してほしい', '午後', 'お名前なし'];
      for (const s of ['input[name=want][value="査定してほしい"]', '#pl', '#tl']) if (!(await p.isVisible(s.startsWith('input') ? 'label:has(' + s + ')' : s))) { r.why = '1画面目に「' + s + '」が見えない'; return; }
      if (await p.isVisible('#nm')) { r.why = 'お名前が1画面目に出ている（3問のはず）'; return; }
      await tick(p, 'input[name=want][value="査定してほしい"]');
      await p.fill('#pl', '確かめ市'); await p.fill('#tl', '09000000000'); await p.waitForTimeout(300);
      await tick(p, 'input[name=ttime][value="午後"]'); await tick(p, '#ag');
    }));
    rs.push(await run(b, base, 'ほかにも書く（お名前あり）', MP, async (p, r) => {
      r.must = ['テスト太郎', '確かめ市', '一戸建て'];
      await tick(p, 'input[name=want][value="売るか迷っている"]'); await p.fill('#pl', '確かめ市'); await p.fill('#em', 'test@example.com');
      await p.click('#kw summary'); await p.fill('#nm', 'テスト太郎'); await tick(p, 'input[name=kind][value="一戸建て"]'); await tick(p, '#ag');
    }));
    rs.push(await run(b, base, 'かんたん相談（1つの画面）', MP + '?lite=1', async (p, r) => {
      r.must = ['確かめ市', 'かんたん相談'];
      await p.fill('#pl', '確かめ市'); await p.fill('#tl', '09000000000'); await tick(p, '#ag');
    }));
    rs.push(await run(b, base, 'ご希望を選んで来た人', MP + '?want=' + encodeURIComponent('解体の見積り'), async (p, r) => {
      r.must = ['確かめ市', '解体'];
      if (!(await p.isChecked('input[name=want][value="解体の見積り"]'))) { r.why = 'ご希望つきで来たのに、ご希望が選ばれていない'; return; }
      await p.fill('#pl', '確かめ市'); await p.fill('#em', 'test@example.com'); await tick(p, '#ag');
    }));
    out.sites[key] = { base, ok: rs.every(x => x.ok), rows: rs };
  }
  out.ok = Object.values(out.sites).every(s => s.ok);
  fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1)); await b.close();
})();
