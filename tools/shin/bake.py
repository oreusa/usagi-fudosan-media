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
       "koyo": "koyo", "hatsumode": "hatsumode", "tomari": "tomari", "ima": "ima", "kaiten": "kaiten", "ranking": "ranking", "uru": "uru", "ikura": "ikura", "furusato": "furusato", "nesage": "nesage"}
for x in PF:
    MAP["odekake-" + x] = "odekake-" + x
    MAP["illumination-" + x] = "illumination-" + x
    MAP["koyo-" + x] = "koyo-" + x
SKIP_DIR = {"shin", "stats", "c", "wx", "api", "assets", "townnotes"}


# 11/19 23:50 owner「頭とバーをかぶせただけは作り直しに数えない」「その他も本気でやり直せ」
# → 前のページの見た目（<style>）は止めて（消さずに media="not all" で眠らせる）、新しい土台の見た目 /shin/kyu.css で描き直す。
#   開く・閉じる・タブなど動きに要る規則（display:none や .on の時の表示）だけは残す。
KYUMARK = 'data-kyu'
KYUV = "3"
import re as _re
_FN = _re.compile(r"\.(on|open|show|active|sel|cur|hide|hidden|is-[\w-]+)\b|\[open\]|:checked|\[hidden\]|\[aria-[\w-]+")


def _keep(css):
    out = []
    css = _re.sub(r"/\*[\s\S]*?\*/", "", css)
    i, n = 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        sel = css[i:j].strip()
        if sel.startswith("@"):
            # @media・@keyframes などは中ごと飛ばす（形の規則なので新しい見た目に任せる）
            d, k = 1, j + 1
            while k < n and d:
                d += {"{": 1, "}": -1}.get(css[k], 0); k += 1
            i = k
            continue
        k = css.find("}", j)
        if k < 0:
            break
        dec = css[j + 1:k]
        dz = dec.replace(" ", "")
        if ("display:none" in dz or "visibility:hidden" in dz or "-9999" in dz or "clip:rect" in dz or "clip-path:inset(50%" in dz
                or ("display" in dz and _FN.search(sel))):
            out.append(sel + "{" + dec + "}")
        i = k + 1
    return "".join(out)


def fam(rel, fn):
    if rel != ".":
        return rel.split(os.sep)[0]
    b = fn[:-5]
    if b.startswith("kaitai") and b != "kaitai-ranking":
        return "kaitai"
    if b.endswith("-ranking") or b.startswith("chika"):
        return "rank"
    if b.startswith("gyosha"):
        return "gyosha"
    return b


def unkyu(h):
    """前に入れた物を外して元に戻す（KYUV を上げた時に入れ直すため）"""
    h = _re.sub(r'(?:<script>document\.documentElement\.dataset\.k="[^"]*"</script>)?<style data-kyu="keep">[\s\S]*?</style><link rel="stylesheet" href="/shin/kyu\.css\?v=[^"]*">', "", h)
    return _re.sub(r'<style data-kyu-old media="not all"', "<style", h)


def kyu(h, k="x"):
    keep = []

    def sleep(m):
        keep.append(_keep(m.group(2)))
        return '<style data-kyu-old media="not all"' + m.group(1) + ">" + m.group(2) + "</style>"
    h2 = _re.sub(r"<style((?:(?!media=)[^>])*)>([\s\S]*?)</style>", sleep, h)
    link = ('<script>document.documentElement.dataset.k="' + k + '"</script><style data-kyu="keep">' + "".join(keep) + '</style><link rel="stylesheet" href="/shin/kyu.css?v=' + KYUV + '">')
    i = h2.find(SKIN[:40]) if SKIN[:40] in h2 else h2.find("</head>")
    return h2[:i] + link + h2[i:]


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
            if SHINMARK in h or "</head>" not in h or ('kyu.css?v=' + KYUV + '"') in h:
                continue
            if KYUMARK in h:
                h = unkyu(h)
            if MARK not in h:
                h = h.replace("</head>", SKIN + "</head>", 1)
            h = kyu(h, fam(rel, fn))
            with open(p, "w", encoding="utf-8") as f:
                f.write(h)
            skinned += 1
    print(f"bake: 差し替え {len(rd) - 2} 本・頭とバーを書き込み {skinned} 枚")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT)
