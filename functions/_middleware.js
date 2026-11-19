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
    return ctx.env.ASSETS.fetch(new Request(u.toString(), request));
  }
  const res = await ctx.next();
  // 11/19 owner「他ページもぜんぶ」→ 新しい土台で作り直していない今までのページに、新しい土台の 頭・下のバー・MENU・文字・夜空 をかぶせる（links/shin/skin.*）。
  // 戻す時はこの if から下の3行を消す（ページの中身は何も変えていない）。
  if (request.method === "GET" && !NOSKIN.has(p) && !/^\/(shin|stats|c|wx|api)(\/|$)/.test(p) && (res.headers.get("content-type") || "").includes("text/html")) {
    return new HTMLRewriter().on("head", { element(e) { e.append(SKIN, { html: true }); } }).transform(res);
  }
  return res;
}
const SKIN = '<script>document.documentElement.classList.add("sk");try{if(localStorage.getItem("usagi_theme")==="night")document.documentElement.classList.add("nt")}catch(e){}</script><link rel="stylesheet" href="/shin/skin.css"><script src="/shin/skin.js" defer></script>';
const PF = ["osaka", "kyoto", "hyogo", "nara", "shiga", "wakayama"];
const SHIN = new Set([
  ...PF.map(x => "/odekake-" + x), "/illumination", "/illumination-muryo", ...PF.map(x => "/illumination-" + x),
  "/koyo", ...PF.map(x => "/koyo-" + x),
  "/hatsumode", "/tomari", "/ima", "/kaiten", "/ranking", "/uru", "/ikura",
]);
// 新しい土台のページ（functions/*.js が /shin を出す所）にはかぶせない
const NOSKIN = new Set(["", "/odekake", "/okaimono", "/fudosan-list", ...SHIN]);
