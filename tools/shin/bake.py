"""11/19 21:50 owner「他も変わってなかったりあるよまだ」
Workers の無料の上限で functions（_middleware.js）が止まると、Pages は functions を通さずに links/*.html をそのまま出す。
すると新しい土台への差し替えも、頭・バーのかぶせも消えて古いページが出ていた。
→ 機械に頼らず、ページのファイルそのものを新しい形にしておく（build.py の最後に毎回）。
  1. 新しい土台で作り直したページは links/_redirects（200＝中身の差し替え）で /shin/* を出す。
     _redirects は functions が動いている時は使われない（いつもは _middleware.js が出す）。止まった時だけ効く。
     元のファイル（index.html・illumination*.html など）は他の機械が毎朝読む元データなので、触らない。
  2. それ以外の今までのページの <head> に、頭・バー・夜空の読み込み（SKIN）を書き込む。
     _middleware.js も同じ物を入れるが、skin.js は2回目を読まない（window.__sk）ので2重にならない。
"""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "links")
SKIN = ('<script>document.documentElement.classList.add("sk");try{if(localStorage.getItem("usagi_theme")==="night")'
        'document.documentElement.classList.add("nt")}catch(e){}</script><link rel="stylesheet" href="/shin/skin.css">'
        '<script src="/shin/skin.js" defer></script>')
MARK = 'href="/shin/skin.css"'
SHINMARK = '/shin/shin.css'
PF = ["osaka", "kyoto", "hyogo", "nara", "shiga", "wakayama"]
# 元の道 → 新しい土台のファイル（functions/_middleware.js の SHIN と functions/*.js と同じ）
MAP = {"index": "cover", "odekake": "odekake", "fudosan-list": "ie", "okaimono": "kau",
       "illumination": "illumination", "illumination-muryo": "illumination-muryo",
       "koyo": "koyo", "hatsumode": "hatsumode", "tomari": "tomari", "ima": "ima", "kaiten": "kaiten", "ranking": "ranking", "uru": "uru", "ikura": "ikura"}
for x in PF:
    MAP["odekake-" + x] = "odekake-" + x
    MAP["illumination-" + x] = "illumination-" + x
    MAP["koyo-" + x] = "koyo-" + x
SKIP_DIR = {"shin", "stats", "c", "wx", "api", "assets", "townnotes"}


def main(root=ROOT):
    root = os.path.abspath(root)
    sh = os.path.join(root, "shin")
    rd = ["# 作り：tools/shin/build.py → bake.py（毎回作り直す。直す時は bake.py の MAP）",
          "# functions が上限で止まった時だけ効く。いつもは functions/_middleware.js と functions/*.js が同じ物を出す。"]
    for old, new in MAP.items():
        if os.path.exists(os.path.join(sh, new + ".html")):
            rd.append(("/" if old == "index" else "/" + old) + " /shin/" + new + " 200")
    open(os.path.join(root, "_redirects"), "w", encoding="utf-8").write("\n".join(rd) + "\n")
    done = {o + ".html" for o in MAP}
    skinned = 0
    for d, dirs, files in os.walk(root):
        rel = os.path.relpath(d, root)
        if rel != "." and rel.split(os.sep)[0] in SKIP_DIR:
            dirs[:] = []
            continue
        for fn in files:
            if not fn.endswith(".html") or (rel == "." and fn in done):
                continue
            p = os.path.join(d, fn)
            with open(p, encoding="utf-8", errors="ignore") as f:
                h = f.read()
            if MARK in h or SHINMARK in h or "</head>" not in h:
                continue
            h = h.replace("</head>", SKIN + "</head>", 1)
            with open(p, "w", encoding="utf-8") as f:
                f.write(h)
            skinned += 1
    print(f"bake: 差し替え {len(rd) - 2} 本・頭とバーを書き込み {skinned} 枚")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT)
