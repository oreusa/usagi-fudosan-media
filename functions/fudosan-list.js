// 11/19 owner「入れ替える」→ /fudosan-list は新しい土台の家と土地の相場（links/shin/ie.html）。
// 今までのページ（links/fudosan-list.html）は消さずに残している。戻す時はこのファイルを消す。
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url); u.pathname = "/shin/ie";
  return env.ASSETS.fetch(new Request(u.toString(), request));
}
