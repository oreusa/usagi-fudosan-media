// TOWN NOTE（pages.dev）の数え方：表示・クリックの数は、今までと同じ所（usagi-odekake のカウンター）に送る。
// 数の置き場所を1つのままにして、URLが変わっても 管制室 の数字が続くようにする。
const OLD = "https://usagi-odekake.usagi-fudosan.workers.dev";
export async function onRequestPost({ request }) {
  // 11/12 機械（検索のロボット）が全ページを開くと、表示の数が1日で205も増えていた（11/9・11/12）。人の数からは外し、
  // 代わりに「機械：Googlebot」のように数える（Google や Bing が見に来ているかが分かる）。
  const ua = request.headers.get("user-agent") || "";
  const m = /(Googlebot|Google-InspectionTool|bingbot|BingPreview|Applebot|GPTBot|OAI-SearchBot|ChatGPT-User|ClaudeBot|PerplexityBot|YandexBot|AhrefsBot|SemrushBot|HeadlessChrome|[a-z]*bot|crawler|spider)/i.exec(ua);
  try {
    if (m) {
      const t = await request.text();
      if (/"表示：/.test(t)) await fetch(OLD + "/c", { method: "POST", body: JSON.stringify({ k: "機械：" + m[1].slice(0, 24) }) });
    } else await fetch(OLD + "/c", { method: "POST", body: await request.text() });
  } catch (e) {}
  return new Response(null, { status: 204 });
}
