# 11/21 鶏足寺（滋賀）飛び出す絵本リール
- paint/：鶏足寺だけの絵（切り紙の層）。`node run.js S0 S1 S2 S3` で ../a/ に層の PNG。
- build.py：声の長さ（shots/voice/keisoku-1121）から時刻を決めて index.html を作る（src/tpl.txt が型）。
- `npx hyperframes@0.9.70 render -o hf.mp4` → `mix.sh`（曲を足す）。
- 表紙は ehon.py の html から cvshot.js で撮る（日付行と金のもみじを足す）。
