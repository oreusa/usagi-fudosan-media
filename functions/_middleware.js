// 11/15 独自ドメイン townnote.app（オーナーが購入）。townnote.pages.dev に直に来た人は kansai.townnote.app へ引っ越し（301）。
// kansai.townnote.app の入口（akari の gate/ Worker）から取り次がれた分は x-tn-host が付くので、そのまま返す。
export async function onRequest(ctx) {
  const { request } = ctx;
  const url = new URL(request.url);
  if (url.hostname === "townnote.pages.dev" && !request.headers.get("x-tn-host") && (request.method === "GET" || request.method === "HEAD")) {
    return Response.redirect("https://kansai.townnote.app" + url.pathname + url.search, 301);
  }
  // 11/19 owner「全部！」→ 府県・イルミ・紅葉のページも新しい土台（links/shin/*.html）を出す。
  // 今までのページ（links/*.html）は消さずに残している。戻す時はこの SHIN の行を消す。
  const p = url.pathname.replace(/\.html$/, "").replace(/\/$/, "");
  if ((request.method === "GET" || request.method === "HEAD") && SHIN.has(p)) {
    const u = new URL(request.url); u.pathname = "/shin" + p;
    return look(await ctx.env.ASSETS.fetch(new Request(u.toString(), request)));
  }
  // 11/20 owner「月が決めていいよ」→ 街のページ（/machi/<id>）は新しい形（links/shin/machi/<id>.html・tools/shin/machi2.py）。無ければ前のページ
  if ((request.method === "GET" || request.method === "HEAD") && /^\/((machi|jikka)\/[a-z]+-\d+|kaitai(-[a-z]+)?|o\/[0-9a-f]+|kaiten\/\d{8}-[0-9a-f]+|kaimawari)$/.test(p)) {
    const u = new URL(request.url); u.pathname = "/shin" + p;
    const r2 = await ctx.env.ASSETS.fetch(new Request(u.toString(), request));
    if (r2.ok) return look(r2);
  }
  const res = await ctx.next();
  // 11/19 owner「他ページもぜんぶ」→ 新しい土台で作り直していない今までのページに、新しい土台の 頭・下のバー・MENU・文字・夜空 をかぶせる（links/shin/skin.*）。
  // 戻す時はこの if から下の3行を消す（ページの中身は何も変えていない）。
  if (request.method === "GET" && !NOSKIN.has(p) && !/^\/(shin|stats|c|wx|api)(\/|$)/.test(p) && (res.headers.get("content-type") || "").includes("text/html")) {
    return new HTMLRewriter().on("head", { element(e) { e.append(SKIN + LOOK, { html: true }); } }).transform(res);
  }
  return look(res);
}
// 11/20 19:54 owner「月のおすすめで」→ 見た目 D（オーロラとガラス＋箱並べ・links/shin/look.css）を全部のページに。頭で読む＝白い画面が一瞬出ない。
// ?look=0 で前の見た目（その端末で覚える）。戻す時は LOOK を "" にする。
function look(res) {
  if (!(res.headers.get("content-type") || "").includes("text/html")) return res;
  return new HTMLRewriter().on("head", { element(e) { e.append(LOOK, { html: true }); } }).transform(res);
}
const LOOK = '<script>try{if(localStorage.getItem("tn_ty2")!=="0"&&!/[?&]ty=0/.test(location.search))document.documentElement.classList.add("lk-t1")}catch(e){}try{var v=localStorage.getItem("tn_lk2")||"f",m=location.search.match(/[?&]look=([abcdef0])/);if(m){v=m[1];localStorage.setItem("tn_lk2",v)}if(v!=="0"){var h=document.documentElement;h.classList.add("lk","lk-"+v);if(v==="d"||v==="e"||v==="f")h.classList.add("lk-a","lk-d");if(v==="f")h.classList.add("lk-e")}}catch(e){}</script><link rel="stylesheet" href="/shin/look.css?v=37" id="lkcss"><script src="/shin/look.js?v=37" defer></script>';
const SKIN = '<script>document.documentElement.classList.add("sk");try{if(localStorage.getItem("usagi_theme")==="night")document.documentElement.classList.add("nt")}catch(e){}</script><link rel="stylesheet" href="/shin/skin.css"><script src="/shin/skin.js" defer></script>';
const PF = ["osaka", "kyoto", "hyogo", "nara", "shiga", "wakayama"];
const SHIN = new Set([
  ...PF.map(x => "/odekake-" + x), "/illumination", "/illumination-muryo", ...PF.map(x => "/illumination-" + x),
  "/koyo", ...PF.map(x => "/koyo-" + x),
  "/hatsumode", "/tomari", "/ima", "/kaiten", "/ranking", "/uru", "/ikura", "/furusato", "/nesage", "/chika-kansai", "/chika-osaka", "/sagasu", "/jikka", "/jikka/shindan", "/akiya-ranking", "/moushikomi", "/koe", "/otoku", "/gyosha", "/gyosha-jikka", "/gyosha-kyoyu", "/gyosha-saikenchiku", "/gyosha-shakuchi", "/gyosha-urenokori",
]);
// 新しい土台のページ（functions/*.js が /shin を出す所）にはかぶせない
const NOSKIN = new Set(["", "/odekake", "/okaimono", "/fudosan-list", ...SHIN]);
