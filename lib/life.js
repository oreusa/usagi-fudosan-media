// 11/7 オーナー「違うページ飛ぶし使いにくい」→ くらべたおかいものリスト（燈の LIFE NOTE にある）を、TOWN NOTE の中で同じタブのまま開く。
// 中身は燈のページを毎回そのまま読み、TOWN NOTE の名前・メニュー・昼夜に入れ替えるだけ（作り直しは燈の page.yml 1か所）。
export const LIFE = "https://lifenote-kanto.pages.dev";
export function toTown(t, isHtml) {
  // 燈の部品は /life-assets/ から（TOWN の /assets/ と名前がぶつかるため）。メニューと昼夜は TOWN の物を使う
  t = t.replace(/(["'(])\/assets\/(?!menu\.js|night\.js)/g, "$1/life-assets/");
  t = t.replace(/\/assets\/menu\.js\?v=\d+/g, "/assets/menu.js?v=49");
  // 押された数は今までどおり燈の数え場所へ
  t = t.replace(/(["'])\/c(["'?])/g, "$1" + LIFE + "/c$2");
  if (isHtml) {
    t = t.replace(/<title>([^<]*)LIFE NOTE<\/title>/, "<title>$1TOWN NOTE</title>");
    t = t.replace(/>LIFE NOTE</g, ">TOWN NOTE<");
    t = t.replace(/href="logo\.png"/g, 'href="/assets/logo.png"');
    // 11/11 買い時・セール・ふるさとの頭のロゴが出ていなかった（logo-s.png は TOWN では /assets/ にある）。名前も TOWN NOTE に
    t = t.replace(/src="\/?logo-s\.png"/g, 'src="/assets/logo-s.png?v=2"');
    t = t.replace(/alt="[^"]*LIFE NOTES? のロゴ"/g, 'alt="TOWN NOTE のロゴ"');
    t = t.replace(/(<meta (?:property|name)="(?:og|twitter):title" content="[^"]*)LIFE NOTE"/g, '$1TOWN NOTE"');
    // 11/7 オーナーOK で本番。同じ中身が2つにならないよう canonical は燈のまま
  }
  return t;
}
export async function page(request) {
  const u = new URL(request.url);
  let r;
  try { r = await fetch(LIFE + u.pathname + u.search); } catch (e) { r = null; }
  if (!r || !r.ok) return Response.redirect(LIFE + u.pathname + u.search, 302);
  return new Response(toTown(await r.text(), true), {
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=0, s-maxage=300" } });
}
export async function asset(request, path) {
  let r;
  try { r = await fetch(LIFE + path); } catch (e) { r = null; }
  if (!r || !r.ok) return new Response("", { status: 404 });
  const ct = r.headers.get("content-type") || "";
  const h = { "content-type": ct, "cache-control": "public, max-age=0, s-maxage=600" };
  if (/javascript|css|json/.test(ct)) return new Response(toTown(await r.text(), false), { headers: h });
  return new Response(r.body, { headers: h });
}
