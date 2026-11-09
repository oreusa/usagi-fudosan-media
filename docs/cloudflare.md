# Cloudflare（townnote.pages.dev）の設定メモ

- 本番ブランチ: main / 出すフォルダ: links
- Build watch paths の Include paths は `*`（全部）。空だと main の更新が全部とばされる（11/2 19:24〜21:22 に本番が止まった原因）。
- 本番が古いときは、まず Workers & Pages → townnote → Deployments で、いちばん上の Production が最新の main か見る。

## 11/9 20:10 本番が f79100f で止まった
- #504（区切り）・#505（終わった催し）の main への反映でビルドが作られず、Preview（claude/ ブランチ）だけ作られていた。
- 本番が古いときは、Cloudflare のデプロイ一覧で「main の行が最新のコミットか」を見る。無ければ main に小さな変更を1つ入れてビルドを起こす。
