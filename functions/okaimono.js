// 11/19 owner「入れ替える」→ /okaimono は新しい土台のおかいもの（links/shin/kau.html：楽天・Yahoo!・Amazon を1つで見比べ）。
// 今までの「くらべたおかいものリスト」（燈の LIFE NOTE を読む lib/life.js）に戻す時は、下を `return page(request)` に。
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/shin/kau"; u.search = "";
  return env.ASSETS.fetch(new Request(u.toString(), request));
}
