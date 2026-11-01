// 関西おでかけリストは /odekake（中身は今までの index.html のまま。毎日の点検やリールは links/index.html を直す）
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/";
  return env.ASSETS.fetch(new Request(u.toString(), request));
}
