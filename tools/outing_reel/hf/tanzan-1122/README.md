# 11/22 談山神社（奈良）飛び出す絵本リール
- paint/tz.js：談山神社だけの絵（十三重塔 昼/夜・朱の社殿・石灯籠・もみじの木）。`cd paint && node run.js H0 H1 H2 H3` で ../a/ に層の PNG → `python3 grade.py a/H?-*.png`。
- a/ の素材（字・gsap・cover.png・hp1/hp2）は ehon.py を `WORK=<作業> python3 ehon.py ig/reels/2026-11-22.json x.mp4 0.02` で作って写す。表紙は `node cvshot.cjs <作業>/ehon.html a/cvface.png`（金の絵＝十三重塔）。
- `python3 build.py shots/voice/tanzan-1122` → `npx hyperframes@0.9.70 render -o hf.mp4` → `bash mix.sh`。
