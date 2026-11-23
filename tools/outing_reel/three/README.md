# 3D のおでかけリール（11/23〜）

オーナー 11/23「リアルなのは綺麗だし好き」「3D感がすごい」で、絵本の中の場面を three.js の3Dに替えた。表紙から開く・ページめくり・案内・おでかけリストの流れはそのまま。

- 場面の絵：`*.html`（three.js 0.170、`npm i three@0.170.0` をこのフォルダで）。`?mode=…&dur=秒&w=1080&h=1662`
  - momiji-room.html：床もみじ（room / floor / garden / umb / side / night）。nob=1 でピントのぼかし無し、rk=.0005 で床の映り込みくっきり
  - city-illumi.html：光の並木（blvd / up / gold / blue / mix / drone）
  - winter-tests.html：イルミのトンネル・クリスマスマーケット・雪の温泉街（3秒の試し）
- 撮る：`SCN=city-illumi.html node shot.cjs "w=1080&h=1662&mode=blvd&dur=9" 出力 0 9 15` → ffmpeg で 30fps の mp4（1枚1〜2秒）
- 組み立て：hf/houtokuji-1123d/build-3d.py（声9文の長さから、目標63秒に合わせて場面の長さを決める）→ hyperframes render → mix.sh
- 画素は 1080 幅（480幅は「解像度低すぎ」と言われた）。並べて同時に撮ると遅くなるので1本ずつ
