// 関西おでかけリストは /odekake（中身は今までの index.html のまま。毎日の点検やリールは links/index.html を直す）
// 11/9 オーナー「mybest…全て奪え」→ 題に「2026年11月」を入れる（検索で今月の一覧だと分かる）。月は出すときに日本時間で入れるので、ファイルを毎月直さなくてよい
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/";
  const res = await env.ASSETS.fetch(new Request(u.toString(), request));
  if (!res.ok || !(res.headers.get("content-type") || "").includes("text/html")) return res;
  const d = new Date(Date.now() + 9 * 3600e3);
  const ym = `${d.getUTCFullYear()}年${d.getUTCMonth() + 1}月`;
  let h = await res.text();
  h = h.replace("<title>関西おでかけリスト｜", `<title>関西おでかけリスト【${ym}】｜`)
       .replace('<meta property="og:title" content="関西おでかけリスト">', `<meta property="og:title" content="関西おでかけリスト【${ym}】">`);
  const hd = new Headers(res.headers); hd.delete("content-length"); hd.delete("etag");
  return new Response(h, { status: res.status, headers: hd });
}
