/* 11/1 オーナー「毎日不安で寝れない…HPのミスをずっと確認できてない」→ 月と燈の全ページを毎朝スマホの幅で開いて確かめる。
   本番（townnote.pages.dev と lifenote-kanto.pages.dev）を開き、ページごとに
   ①画面のエラー ②横にはみ出し ③下のバーとメニューがあるか ④終わった日付のカードが見えていないか ⑤ベージュっぽい色 ⑥開けない画像や読み物
   を調べ、全ページを撮る。結果は out/report.md と out/shots/*.jpg（allcheck ブランチに1日分だけ置く）。
   使い方: node tools/allcheck/check.js out */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const OUT = process.argv[2] || "out";
const SITES = [
  { key: "tsuki", name: "月", base: process.env.TSUKI_BASE || "https://townnote.pages.dev",
    extra: ["/odekake", "/ima", "/fudosan", "/fudosan-list", "/chika-kansai", "/chika-osaka", "/uru", "/gyosha", "/machi/osaka-01", "/machi/kyoto-01", "/koe"] },
  { key: "akari", name: "燈", base: process.env.AKARI_BASE || "https://lifenote-kanto.pages.dev",
    extra: ["/odekake", "/okaimono", "/ima", "/nesage", "/kaimawari", "/tanka", "/furusato", "/tomari", "/koyo", "/privacy", "/koe"] },
];
// 11/9 オーナー「燈？」「なんか対策ないの」→ 画面に出た文（JSで出る物も）に、見せてはいけない言葉が無いかも毎朝見る。文は text/ に残す
const NG = (() => { try { const d = JSON.parse(fs.readFileSync(path.join(__dirname, "ngwords.json"), "utf8")); return { w: d.words.map(([rx, why]) => [new RegExp(rx), why]), allow: d.allow || [] }; } catch (e) { return { w: [], allow: [] }; } })();
// 11/9 オーナー「レントラックス登録してないよな？」→ 画面のお金のリンクのASP・IDが台帳（tools/asp.json）に無ければ問題にする
const ASP = (() => { try { const d = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "asp.json"), "utf8")); const reg = {}, nreg = {}; d.asp.forEach(a => a.domains.forEach(h => reg[h] = a)); (d.not_registered || []).forEach(a => a.domains.forEach(h => nreg[h] = a)); return { reg, nreg }; } catch (e) { return null; } })();
const IDP = { "ck.jp.ap.valuecommerce.com": /[?&]sid=(\d+)/, "af.moshimo.com": /[?&]a_id=(\d+)/, "px.a8.net": /a8mat=([A-Z0-9]+)/, "hb.afl.rakuten.co.jp": /\/h[gc]c\/([0-9a-f.]+)/, "www.amazon.co.jp": /[?&]tag=([A-Za-z0-9-]+)/ };
function aspCheck(links) { const out = new Set(); if (!ASP) return []; for (const u of links) { let x; try { x = new URL(u); } catch (e) { continue; } const h = x.hostname.toLowerCase(); const nr = ASP.nreg[h] || Object.entries(ASP.nreg).find(([d]) => h.endsWith("." + d))?.[1]; if (nr) { out.add("台帳に無いASP（" + nr.name + "）"); continue; } const a = ASP.reg[h], rx = IDP[h]; if (a && rx) { const m = u.match(rx); if (m && !(a.ids || []).includes(m[1])) out.add("台帳に無いID（" + a.name + " " + m[1] + "）"); } } return [...out].slice(0, 3); }
const T = new Date(Date.now() + 9 * 36e5).toISOString().slice(0, 10);

async function pages(site) {
  let list = ["/"];
  try {
    const r = await fetch(site.base + "/sitemap.xml");
    const x = await r.text();
    for (const m of x.matchAll(/<loc>([^<]+)<\/loc>/g)) list.push(new URL(m[1]).pathname);
  } catch (e) { console.log("sitemap NG", site.base, e.message); }
  // 11/2 町のページ（/machi/…）は200以上あって20分で終わらない → 形が同じなので extra の見本だけ見る
  // 11/9 夜#154：見本の2街だけでは、草津ほか24街の NaN を見逃した → 街と1件ページは、毎日ちがう 1/10 ずつ回して10日で全部見る
  const day = Math.floor(Date.now() / 864e5), rot = (q, i) => i % 10 === day % 10;
  const mc = list.filter(p => /^\/machi\//.test(p)).filter(rot);
  const o = list.filter(p => /^\/o\//.test(p)).filter(rot);
  list = list.filter(p => !/^\/(machi|o)\//.test(p)).concat(mc, o);
  list = list.concat(site.extra).map(p => p.replace(/\.html$/, ""));
  return [...new Set(list)];
}

async function one(ctx, site, p) {
  const pg = await ctx.newPage();
  const errs = [], bad = [];
  pg.on("pageerror", e => errs.push("JS: " + e.message.slice(0, 120) + ((e.stack || "").split("\n").slice(1, 2).join("").replace(site.base, "").trim().replace(/^at /, " @ ").slice(0, 120))));  // 11/9 どのファイルの何行目かも残す
  pg.on("console", m => { if (m.type() === "error") errs.push("console: " + m.text().slice(0, 120)); });
  pg.on("response", r => { const u = r.url(); if (r.status() >= 400 && !/\/c(\?|$)|google|doubleclick|rakuten/.test(u)) bad.push(r.status() + " " + u.replace(site.base, "")); });
  let status = 0;
  try {
    const r = await pg.goto(site.base + p + (process.env.ADD_HTML && p !== "/" ? ".html" : ""), { waitUntil: "networkidle", timeout: 45000 });
    status = r ? r.status() : 0;
  } catch (e) { errs.push("開けない: " + e.message.slice(0, 80)); }
  await pg.waitForTimeout(1500);
  // 下まで動かして、あとから出る物も出す
  await pg.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 700) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); }).catch(() => {});
  await pg.waitForTimeout(600);
  const info = await pg.evaluate((T) => {
    const vis = e => !!(e.offsetParent || e.getClientRects().length) && getComputedStyle(e).visibility !== "hidden";
    const rgb = s => (s.match(/\d+(\.\d+)?/g) || []).map(Number);
    const beige = [];
    const isBeige = c => { const [r, g, b, a] = rgb(c); if (a === 0 || r === undefined) return false; return r >= 225 && r - b >= 10 && r - b <= 45 && g >= b && g <= r && !(r === 255 && g === 255 && b === 255); };
    document.querySelectorAll("body *").forEach(e => {
      if (!vis(e) || e.closest(".v2c,[style*='--pc'],.st,.lg,svg,img")) return;
      const cs = getComputedStyle(e);
      for (const k of ["backgroundColor", "borderTopColor", "borderBottomColor"]) {
        const v = cs[k]; if (k !== "backgroundColor" && parseFloat(cs[k.replace("Color", "Width")]) === 0) continue;
        if (isBeige(v) && beige.length < 6) beige.push((e.className && typeof e.className === "string" ? "." + e.className.split(" ")[0] : e.tagName.toLowerCase()) + " " + k.replace("Color", "") + " " + v);
      }
    });
    const old = [...document.querySelectorAll("[data-e]")].filter(e => vis(e) && e.dataset.e && e.dataset.e < T && !e.closest(".past,#past,.done,[hidden]")).map(e => (e.querySelector(".t,.nm") || e).textContent.trim().slice(0, 30));
    return {
      title: document.title,
      over: document.documentElement.scrollWidth - innerWidth,
      bar: !!document.getElementById("v2bar"),
      menu: !!document.getElementById("umenu"),
      bg: getComputedStyle(document.body).backgroundColor,
      h: document.body.scrollHeight,
      old: old.slice(0, 5), oldN: old.length, beige,
      // 11/2 燈の入口で「比べた物 0件」が出ていたのを見逃した → 数の欄が 0件・―・NaN・undefined のままなら問題にする
      zero: [...document.querySelectorAll("b,strong,.n,.num")].filter(e => vis(e) && /^(0(件|つ|軒|か所)?|―|-|NaN.*|undefined.*)$/.test(e.textContent.trim())).map(e => ((e.parentElement && e.parentElement.textContent) || "").trim().replace(/\s+/g, " ").slice(0, 20)).slice(0, 5),
      bad: /NaN|undefined|\[object Object\]/.test(document.body.innerText),
      // 11/9 夜#157：開催中なのに「249日後」→ 日付の札が半年より先なら問題にする／#159：LIFE のページの下が TOWN NOTE
      far: [...document.querySelectorAll(".cmb")].map(e => e.textContent.replace(/\s+/g, " ").trim()).filter(t => { const m = t.match(/(\d+)日後/); return m && +m[1] > 150; }).slice(0, 3),
      brand: /lifenote|life-note|usagi-life/.test(location.host) ? [...document.querySelectorAll(".ft")].some(e => /TOWN NOTE/.test(e.textContent)) : [...document.querySelectorAll(".ft")].some(e => /LIFE NOTE/.test(e.textContent) && !/TOWN NOTE/.test(e.textContent)),
      text: document.body.innerText,
      links: [...new Set([...document.querySelectorAll("a[href^='http']")].map(a => a.href))],
      pwa: !!document.querySelector('link[rel="manifest"]'),
      imgs: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && vis(i)).map(i => i.getAttribute("src")).slice(0, 5),
    };
  }, T).catch(e => ({ title: "", err: e.message }));
  const slug = site.key + "-" + (p.replace(/^\/|\/$/g, "").replace(/[\/]/g, "_") || "top");
  if (info.text) {
    fs.mkdirSync(path.join(OUT, "text"), { recursive: true });
    fs.writeFileSync(path.join(OUT, "text", slug + ".txt"), info.title + "\n\n" + info.text);
  }
  try { await pg.screenshot({ path: path.join(OUT, "shots", slug + ".jpg"), fullPage: true, type: "jpeg", quality: 55 }); } catch (e) {}
  await pg.close();
  const prob = [];
  if (status >= 400 || !status) prob.push("開けない（" + status + "）");
  if (info.over > 1) prob.push("横にはみ出し " + info.over + "px");
  if (!info.bar) prob.push("下のバーがない");
  if (!info.menu) prob.push("メニューがない");
  // 夜は body を紺 #141A28 にして画面のふちの白いもやを消している（usagi #330 / akari #369）ので、それも正しい
  const okBg = process.env.THEME === "night" ? /^rgba?\(255, 255, 255(, 1)?\)$|rgba\(0, 0, 0, 0\)|^rgb\(20, 26, 40\)$/ : /^rgba?\(255, 255, 255(, 1)?\)$|rgba\(0, 0, 0, 0\)/;
  if (info.bg && !okBg.test(info.bg)) prob.push("背景が白でない " + info.bg);
  if (info.oldN) prob.push("終わった日付が" + info.oldN + "件見えている（" + info.old.join("／") + "）");
  if (info.beige && info.beige.length) prob.push("ベージュっぽい色: " + info.beige.join("、"));
  if (info.zero && info.zero.length) prob.push("数が0か空のまま: " + info.zero.join("／"));
  if (info.bad) prob.push("NaN・undefined の文字が見えている");
  if (info.far && info.far.length) prob.push("日付の札が半年より先（年のまちがい？）: " + info.far.join("／"));
  if (info.brand) prob.push("ページの下のサイト名がちがう（TOWN と LIFE）");
  if (info.pwa === false) prob.push("ホーム画面に置けない（manifest がない）");
  if (info.imgs && info.imgs.length) prob.push("出ない画像: " + info.imgs.join(" "));
  if (info.text) {
    let tx = info.text; for (const a of NG.allow) tx = tx.split(a).join("");
    for (const [rx, why] of NG.w) { const m = tx.match(rx); if (m) prob.push("言葉: " + why + "（…" + tx.slice(Math.max(0, m.index - 12), m.index + m[0].length + 12).replace(/\s+/g, " ") + "…）"); }
  }
  if (info.links) aspCheck(info.links).forEach(e => prob.push("お金のリンク: " + e));
  errs.slice(0, 3).forEach(e => prob.push(e));
  bad.slice(0, 3).forEach(e => prob.push("読めない: " + e));
  return { site: site.name, p, slug, title: info.title, h: info.h, prob };
}

(async () => {
  fs.mkdirSync(path.join(OUT, "shots"), { recursive: true });
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, locale: "ja-JP", timezoneId: "Asia/Tokyo",
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1 allcheck" });
  // 数に入れない印（月：usagi_owner、燈：クッキー me=1）
  await ctx.addInitScript(() => { try { localStorage.setItem("usagi_owner", "1"); } catch (e) {} });
  // 11/2 オーナー「他のページまだ白モヤ…統一してない」→ 夜の見た目も毎朝撮る（THEME=night で夜にして開く）
  if (process.env.THEME === "night") await ctx.addInitScript(() => { try { localStorage.setItem("usagi_theme", "night"); } catch (e) {} });
  await ctx.addCookies([{ name: "me", value: "1", domain: "lifenote-kanto.pages.dev", path: "/", secure: true }]);
  const rows = [];
  for (const s of SITES) for (const p of await pages(s)) { const r = await one(ctx, s, p); rows.push(r); console.log(r.site, r.p, r.prob.length ? r.prob.join(" / ") : "OK"); }
  await b.close();
  // 11/2 月 /fudosan-list の題名が おでかけ のままだった → 同じサイトで題名が同じページを出す
  for (const r of rows) { const d = rows.filter(x => x !== r && x.site === r.site && x.title && x.title === r.title); if (d.length) r.prob.push("題名がほかのページと同じ（" + d.map(x => x.p).join("・") + "）"); }
  const ng = rows.filter(r => r.prob.length);
  let md = `# 全ページ点検 ${new Date(Date.now() + 9 * 36e5).toISOString().slice(0, 16).replace("T", " ")}（日本時間）\n\n`;
  md += `見たページ：${rows.length}（月 ${rows.filter(r => r.site === "月").length}・燈 ${rows.filter(r => r.site === "燈").length}）／気になる所があるページ：${ng.length}\n\n`;
  md += ng.length ? "## 気になる所\n" + ng.map(r => `- ${r.site} ${r.p}：${r.prob.join("／")}`).join("\n") + "\n\n" : "## 気になる所\nなし\n\n";
  md += "## 全ページ\n| | ページ | 題名 | 高さ | 写真 |\n|---|---|---|---|---|\n" + rows.map(r => `| ${r.site} | ${r.p} | ${(r.title || "").slice(0, 30)} | ${r.h || ""} | shots/${r.slug}.jpg |`).join("\n") + "\n";
  fs.writeFileSync(path.join(OUT, "report.md"), md);
  fs.writeFileSync(path.join(OUT, "report.json"), JSON.stringify(rows, null, 1));
})();
