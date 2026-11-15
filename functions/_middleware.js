// 11/15 独自ドメイン townnote.app（オーナーが購入）。townnote.pages.dev に直に来た人は kansai.townnote.app へ引っ越し（301）。
// kansai.townnote.app の入口（akari の gate/ Worker）から取り次がれた分は x-tn-host が付くので、そのまま返す。
export async function onRequest(ctx) {
  const { request } = ctx;
  const url = new URL(request.url);
  if (url.hostname === "townnote.pages.dev" && !request.headers.get("x-tn-host") && (request.method === "GET" || request.method === "HEAD")) {
    return Response.redirect("https://kansai.townnote.app" + url.pathname + url.search, 301);
  }
  return ctx.next();
}
