"""表紙 v3（11/10 オーナーOK）を links/town-notes.html に当てる。make.py の最後でも呼ぶ（作り直しても消えない）。
見た目と動きは links/assets/cover.css・cover.js、数字は links/assets/cover.json（tools/cover/make.py）。"""
import re, sys, os
V = "3"
def apply(s):
    if 'id="cover3"' in s:
        return s
    s = re.sub(r'<nav class="q3">.*?</nav>', '', s, count=1, flags=re.S)
    lens = ('<div class="today" id="today"></div><div class="lens" id="lens" role="tablist" aria-label="地図で見るもの">'
            '<button type="button" data-l="od" class="on" style="--c:#E39B3A"><small>01</small>おでかけ</button>'
            '<button type="button" data-l="fu" style="--c:#4F7BA8"><small>02</small>街の地価</button>'
            '<button type="button" data-l="jk" style="--c:#5E9E6E"><small>03</small>実家</button>'
            '<button type="button" data-l="ok" style="--c:#C2727F"><small>04</small>おかいもの</button></div>')
    s = s.replace('<p class="pur">', lens + '<p class="pur">', 1)
    jk = ('<a class="ls" href="/jikka/" data-k="入口｜実家・空き家ノート" style="--ac:#5E9E6E;--bg:#EEF6F0;--c:#5E9E6E"><div class="no"><small>PAGE</small>03</div>'
          '<div class="en">JIKKA NOTE</div><h3>実家・空き家ノート</h3><p>相続した家を、売る・片付ける・解体する前に。</p>'
          '<div class="st"><div><span>関西の街</span><b>200</b></div><div><span>やること</span><b>4<small style="font-size:12px">つ</small></b></div><div><span>ご相談</span><b style="font-size:15px">無料</b></div></div>'
          '<div class="go">実家ノートを開く<span>→</span></div></a>')
    s = s.replace('<a class="ls" href="/okaimono"', jk + '<a class="ls" href="/okaimono"', 1)
    s = s.replace('<div class="no"><small>PAGE</small>03</div><div class="en">OKAIMONO LIST', '<div class="no"><small>PAGE</small>04</div><div class="en">OKAIMONO LIST', 1)
    s = s.replace('</head>', '<link id="cover3" rel="stylesheet" href="/assets/cover.css?v=%s"></head>' % V, 1)
    s = s.replace('</body>', '<script src="/assets/cover.js?v=%s" defer></script></body>' % V, 1)
    return s
if __name__ == "__main__":
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "links", "town-notes.html")
    src = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(apply(src))
    print("cover v3 applied")
