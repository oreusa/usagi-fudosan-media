# 11/23 勝尾寺（箕面）の飛び出す絵本リール：短い形

前の回（談山神社・42秒・閉じた本から始まる）から変えた所（11/22 owner「リールも伸びないねぇ」を受けて）：
- 約22秒。1コマ目から見せ場の絵（紅葉の石段に勝ちダルマ）と大きな字「紅葉に、だるまがぎっしり」
- 本の表紙はインスタの並びの絵だけに使う（spec の cover_url ＝ media/reels/2026-11-23-cover.jpg、ig-post-reel.yml が渡す）
- 声は4文。場所の名前は1文目の後ろ、最後は「一緒に行く人に送って、保存してね」

作り方：
1. 絵 `cd paint && node run.js`（ko.js＝この日の筆：daruma・darumaRow・stoneLedge・lantern、H0〜H2）→ `python3 grade.py`
2. 声 tools/voice/katsuoji-1123.json → shots/voice/katsuoji-1123 を a/v0〜v3.wav に
3. `python3 build.py <声のフォルダ>` → `npx --yes hyperframes@0.9.70 render -o hf.mp4` → `bash mix.sh`
4. 表紙 `WORK=<dir> python3 ../../ehon.py ig/reels/2026-11-23.json <dir>/out.mp4 0.02` → `node cvshot.cjs <dir>/ehon.html <dir>/cover.png`（金の絵を勝ちダルマに）→ 1080x1920 の暗い地に置く
