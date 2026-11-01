// TOWN NOTE（pages.dev）の数え方：表示・クリックの数は、今までと同じ所（usagi-odekake のカウンター）に送る。
// 数の置き場所を1つのままにして、URLが変わっても 管制室 の数字が続くようにする。
const OLD = "https://usagi-odekake.usagi-fudosan.workers.dev";
export async function onRequestPost({ request }) {
  try { await fetch(OLD + "/c", { method: "POST", body: await request.text() }); } catch (e) {}
  return new Response(null, { status: 204 });
}
