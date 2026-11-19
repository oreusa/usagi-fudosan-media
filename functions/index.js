// 11/1 オーナー「入口必要じゃない？」：一番上（/）は TOWN NOTE の入口。
// 11/19 owner「全部！」→ 新しい土台の表紙（links/shin/cover.html）を出す。今までの表紙 town-notes.html は残している。戻す時は "/shin/cover" を "/town-notes" に。
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/shin/cover";
  return env.ASSETS.fetch(new Request(u.toString(), request));
}
