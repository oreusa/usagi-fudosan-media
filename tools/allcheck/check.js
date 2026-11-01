/* 11/1 オーナー「毎日不安で寝れない…HPのミスをずっと確認できてない」→ 月と燈の全ページを毎朝スマホの幅で開いて確かめる。
   本番（townnote.pages.dev と usagi-life-notes.pages.dev）を開き、ページごとに
   ①画面のエラー ②横にはみ出し ③下のバーとメニューがあるか ④終わった日付のカードが見えていないか ⑤ベージュっぽい色 ⑥開けない画像や読み物
   を調べ、全ページを撮る。結果は out/report.md と out/shots/*.jpg（allcheck ブランチに1日分だけ置く）。
   使い方: node tools/allcheck/check.js out */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const OUT = process.argv[2] || "out";
const SITES = [
  { key: "tsuki", name: "月", base: process.env.TSUKI_BASE || "https://townnote.pages.dev",
    extra: ["/odekake", "/ima", "/fudosan", "/fudosan-list", "/chika-kansai", "/chika-osaka", "/uru", "/gyosha", "/machi/osaka-01", "/machi/kyoto-01"] },
  { key: "akari", name: "燈", base: process.env.AKARI_BASE || "https://usagi-life-notes.pages.dev",
    extra: ["/ima", "/nesage", "/kaimawari", "/tanka", "/furusato", "/tomari"] },
];
const T = new Date(Date.now() + 9 * 36e5).toISOString().slice(0, 10);

async function pages(site) {
  let list = ["/"];
  try {
    const r = await fetch(site.base + "/sitemap.xml");
    const x = await r.text();
    for (const m of x.matchAll(/<loc>([^<]+)<\/loc>/g)) list.push(new URL(m[1]).pathname);
  } catch (e) { console.log("sitemap NG", site.base, e.message); }
  list = list.concat(site.extra).map(p => p.replace(/\.html$/, ""));
  return [...new Set(list)];
}

async function one(ctx, site, p) {
  const pg = await ctx.newPage();
  const errs = [], bad = [];
  pg.on("pageerror", e => errs.push("JS: " + e.message.slice(0, 120)));
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
      imgs: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && vis(i)).map(i => i.getAttribute("src")).slice(0, 5),
    };
  }, T).catch(e => ({ title: "", err: e.message }));
  const slug = site.key + "-" + (p.replace(/^\/|\/$/g, "").replace(/[\/]/g, "_") || "top");
  try { await pg.screenshot({ path: path.join(OUT, "shots", slug + ".jpg"), fullPage: true, type: "jpeg", quality: 55 }); } catch (e) {}
  await pg.close();
  const prob = [];
  if (status >= 400 || !status) prob.push("開けない（" + status + "）");
  if (info.over > 1) prob.push("横にはみ出し " + info.over + "px");
  if (!info.bar) prob.push("下のバーがない");
  if (!info.menu) prob.push("メニューがない");
  if (info.bg && !/^rgba?\(255, 255, 255(, 1)?\)$|rgba\(0, 0, 0, 0\)/.test(info.bg)) prob.push("背景が白でない " + info.bg);
  if (info.oldN) prob.push("終わった日付が" + info.oldN + "件見えている（" + info.old.join("／") + "）");
  if (info.beige && info.beige.length) prob.push("ベージュっぽい色: " + info.beige.join("、"));
  if (info.imgs && info.imgs.length) prob.push("出ない画像: " + info.imgs.join(" "));
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
  await ctx.addCookies([{ name: "me", value: "1", domain: "usagi-life-notes.pages.dev", path: "/", secure: true }]);
  const rows = [];
  for (const s of SITES) for (const p of await pages(s)) { const r = await one(ctx, s, p); rows.push(r); console.log(r.site, r.p, r.prob.length ? r.prob.join(" / ") : "OK"); }
  await b.close();
  const ng = rows.filter(r => r.prob.length);
  let md = `# 全ページ点検 ${new Date(Date.now() + 9 * 36e5).toISOString().slice(0, 16).replace("T", " ")}（日本時間）\n\n`;
  md += `見たページ：${rows.length}（月 ${rows.filter(r => r.site === "月").length}・燈 ${rows.filter(r => r.site === "燈").length}）／気になる所があるページ：${ng.length}\n\n`;
  md += ng.length ? "## 気になる所\n" + ng.map(r => `- ${r.site} ${r.p}：${r.prob.join("／")}`).join("\n") + "\n\n" : "## 気になる所\nなし\n\n";
  md += "## 全ページ\n| | ページ | 題名 | 高さ | 写真 |\n|---|---|---|---|---|\n" + rows.map(r => `| ${r.site} | ${r.p} | ${(r.title || "").slice(0, 30)} | ${r.h || ""} | shots/${r.slug}.jpg |`).join("\n") + "\n";
  fs.writeFileSync(path.join(OUT, "report.md"), md);
  fs.writeFileSync(path.join(OUT, "report.json"), JSON.stringify(rows, null, 1));
})();
