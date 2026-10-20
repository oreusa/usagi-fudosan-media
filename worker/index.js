// おでかけリストのアクセス数とクリック数を数える（10/20 オーナーOK）。
// ページの表示や各ボタンのリンク先はそのまま（静的ファイルは ASSETS が返す）。
// ページの小さなスクリプトが /c に {k:"見出し"} を送り、日ごと・項目ごとに1つ数える。
// 集計は /stats で JSON を返す（個人の情報は保存しない。数だけ）。
import { DurableObject } from "cloudflare:workers";

const RESET = "2026-10-21";

export class Counter extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS c (day TEXT, k TEXT, n INTEGER, PRIMARY KEY (day, k))");
    // 数え直し：RESET を変えて公開すると、最初の1回だけ数を全部0に戻す（10/21 オーナー：試しに押した分を消す）
    this.sql.exec("CREATE TABLE IF NOT EXISTS m (k TEXT PRIMARY KEY, v TEXT)");
    const done = this.sql.exec("SELECT v FROM m WHERE k = 'reset'").toArray()[0];
    if (!done || done.v !== RESET) {
      this.sql.exec("DELETE FROM c");
      this.sql.exec("INSERT OR REPLACE INTO m VALUES ('reset', ?)", RESET);
    }
  }
  add(day, k) {
    this.sql.exec("INSERT INTO c VALUES (?, ?, 1) ON CONFLICT(day, k) DO UPDATE SET n = n + 1", day, k);
  }
  stats(since) {
    return this.sql.exec("SELECT day, k, n FROM c WHERE day >= ? ORDER BY day DESC, n DESC", since).toArray();
  }
}

const jstDay = (ms) => new Date(ms + 9 * 3600e3).toISOString().slice(0, 10);

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === "/c" && req.method === "POST") {
      let k = "";
      try { k = String(JSON.parse(await req.text()).k || ""); } catch (e) {}
      k = k.replace(/\s+/g, " ").trim().slice(0, 80);
      if (k) await env.COUNTER.get(env.COUNTER.idFromName("main")).add(jstDay(Date.now()), k);
      return new Response(null, { status: 204 });
    }
    if (url.pathname === "/stats") {
      const days = Math.min(Math.max(parseInt(url.searchParams.get("days") || "30", 10) || 30, 1), 365);
      const rows = await env.COUNTER.get(env.COUNTER.idFromName("main")).stats(jstDay(Date.now() - (days - 1) * 864e5));
      const total = {};
      for (const r of rows) total[r.k] = (total[r.k] || 0) + r.n;
      const sorted = Object.fromEntries(Object.entries(total).sort((a, b) => b[1] - a[1]));
      return Response.json({ days, total: sorted, by_day: rows }, { headers: { "cache-control": "no-store" } });
    }
    return env.ASSETS.fetch(req);
  },
};
