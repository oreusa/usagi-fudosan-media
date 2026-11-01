// 11/1 オーナー「入口必要じゃない？」：一番上（/）は TOWN NOTE の入口を出す（中身は town-notes.html）
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/town-notes";
  return env.ASSETS.fetch(new Request(u.toString(), request));
}
