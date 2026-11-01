// /stats も今までと同じ数を返す
const OLD = "https://usagi-odekake.usagi-fudosan.workers.dev";
export async function onRequestGet({ request }) {
  const u = new URL(request.url);
  const r = await fetch(OLD + "/stats" + u.search);
  return new Response(r.body, { status: r.status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
}
