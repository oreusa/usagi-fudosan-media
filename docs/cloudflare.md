# Cloudflare（townnote.pages.dev）の設定メモ

- 本番ブランチ: main / 出すフォルダ: links
- Build watch paths の Include paths は `*`（全部）。空だと main の更新が全部とばされる（11/2 19:24〜21:22 に本番が止まった原因）。
- 本番が古いときは、まず Workers & Pages → townnote → Deployments で、いちばん上の Production が最新の main か見る。
