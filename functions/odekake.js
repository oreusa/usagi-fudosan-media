// 関西おでかけリストは /odekake。11/19 owner「入れ替える」→ 新しい土台のページ（links/shin/odekake.html・tools/shin/build.py が毎朝作る）を出す。
// 今までのページ（links/index.html）は消さずに残している（戻す時はここの "/shin/odekake" を "/" に）。
// 11/9 題に「2026年11月」を入れる（検索で今月の一覧だと分かる）。
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/shin/odekake";
  const res = await env.ASSETS.fetch(new Request(u.toString(), request));
  if (!res.ok || !(res.headers.get("content-type") || "").includes("text/html")) return res;
  const d = new Date(Date.now() + 9 * 3600e3);
  const ym = `${d.getUTCFullYear()}年${d.getUTCMonth() + 1}月`;
  let h = await res.text();
  h = h.replace("<title>関西おでかけリスト｜", `<title>関西おでかけリスト【${ym}】｜`);
  const hd = new Headers(res.headers); hd.delete("content-length"); hd.delete("etag");
  return new Response(h, { status: res.status, headers: hd });
}
