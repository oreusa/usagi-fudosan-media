"""関西まちランキング（/ranking）を作る。11/11 経営方針の柱1（人気）：Threads でいちばん見られている「地元の順位＋数字」の投稿を、
HPで全部読める場所にする（投稿の2本目の行き先・連載のまとめ・検索の入口）。
形は関西の初詣ページ（links/hatsumode.html）を借りる。元は tools/ranking/data.json（投稿スレッドが足す）。
使い方: python3 tools/ranking/build.py 2026-11-11"""
import datetime, html, json, os, re, sys
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
BASE = "https://townnote.pages.dev/"
E = html.escape
items = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))["items"]
towns = json.load(open(os.path.join(ROOT, "links", "assets", "towns.json"), encoding="utf-8"))
towns = towns.get("towns", towns) if isinstance(towns, dict) else towns
NAME = sorted(((t["n"], t["id"]) for t in towns), key=lambda x: -len(x[0]))
EMO = re.compile("[\U0001F000-\U0001FAFF☀-➿️⛩]+")
KIND = [("eki", "駅の順位", "乗る人の数でくらべた駅", r"駅"), ("ie", "家と土地の順位", "住宅地の値段・上がり幅・売れた値段", r"住宅地|商業地|地価|売れた|基準地"),
        ("hito", "人口の順位", "増えた街・若い世代の多い街", r"人口|割合"), ("hoka", "そのほかの順位", "観光地など", r".")]


def body(text):
    ls = text.split("\n")[1:]; out = []; ul = False
    def close():
        nonlocal ul
        if ul: out.append("</ul>"); ul = False
    para = []
    def flush():
        if para: out.append("<p>" + "".join(E(x) for x in para) + "</p>"); para.clear()
    for l in ls:
        l = EMO.sub("", l).rstrip()
        s = l.strip()
        if not s: flush(); continue
        if s.startswith("◎"): flush(); close(); out.append('<p class="rk-l">' + E(s[1:].strip()) + "</p>")
        elif s.startswith("✦"): flush(); close(); out.append("<h4>" + E(s[1:].strip()) + "</h4>")
        elif s.startswith("⊹") or re.match(r"\d+位[ \u3000]", s):
            flush()
            if not ul: out.append("<ul>"); ul = True
            out.append("<li>" + E(s.lstrip("⊹").strip()) + "</li>")
        elif s.startswith("✧"): flush(); close(); out.append('<p class="rk-n">' + E(s[1:].strip()) + "</p>")
        else: close(); para.append(s)
    flush(); close()
    return "".join(out)


def machi(text):
    seen = []; t = text
    for n, i in NAME:
        if n in t and i not in [x[1] for x in seen]:
            seen.append((n, i)); t = t.replace(n, "")
    return seen[:6]


groups = {k[0]: [] for k in KIND}
allr = []
for no, it in enumerate(sorted(items, key=lambda x: x["day"]), 1):
    first = it["text"].split("\n")[0]
    title = EMO.sub("", first).strip().strip("【】").replace("｜", "　")
    kind = next(k[0] for k in KIND if re.search(k[3], first))
    d = datetime.date.fromisoformat(it["day"])
    ms = machi(it["text"])
    links = "".join(f'<a href="/machi/{i}" data-k="ランキング｜街 {E(n)}">{E(n)}</a>' for n, i in ms)
    src = f'<p class="rk-s"><a href="{E(it["src"])}" target="_blank" rel="noopener">出どころの公式ページ</a></p>' if it.get("src") else ""
    blk = (f'<details class="rk" id="r{no}"><summary><span class="rk-no">No.{no}</span><span class="rk-t">{E(title)}</span><span class="rk-d">{d.month}月{d.day}日</span></summary>'
           f'<div class="rk-b">{body(it["text"])}{src}' + (f'<div class="rk-m"><small>この順位に出てくる街</small>{links}</div>' if links else "") + "</div></details>")
    groups[kind].append((no, blk)); allr.append((no, title, d))
secs = ""
for k, name, sub, _ in KIND:
    g = sorted(groups[k], key=lambda x: -x[0])
    if not g: continue
    secs += f'<section id="{k}" class="ps" style="--c:#4F7BA8"><h2>{name}<small>{len(g)}本</small></h2><p class="rk-sub">{sub}</p>' + "".join(b for _, b in g) + "</section>"
N = len(allr); last = max(x[2] for x in allr)
s = open(os.path.join(ROOT, "links", "hatsumode.html"), encoding="utf-8").read()
title = f"関西まちランキング｜駅・地価・人口の順位を公式の数字で（{N}本）"
desc = f"関西6府県の街を、駅の乗る人の数・住宅地の値段・人口などの公式の数字で順位にしました。{N}本の順位を、街ごとのページとあわせて読めます。{TODAY.month}月{TODAY.day}日更新。"
ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関西まちランキング", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t, "url": f"{BASE}ranking#r{no}"} for i, (no, t, _) in enumerate(sorted(allr, key=lambda x: -x[0]))]},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "関西不動産リスト", "item": BASE + "fudosan-list"}, {"@type": "ListItem", "position": 2, "name": "関西まちランキング", "item": BASE + "ranking"}]}]
s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
CSS = ("<style>.rk{background:#fff;border-radius:2px;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);margin-bottom:12px}"
       ".rk summary{list-style:none;cursor:pointer;padding:14px 40px 14px 16px;position:relative;display:grid;grid-template-columns:auto 1fr;gap:2px 10px;align-items:baseline}"
       ".rk summary::-webkit-details-marker{display:none}.rk summary::after{content:'＋';position:absolute;right:14px;top:14px;color:#8C7B6E;font-size:15px}.rk[open] summary::after{content:'－'}"
       ".rk-no{font-family:Jost;font-size:11px;letter-spacing:.14em;color:var(--c)}.rk-t{font-family:'Shippori Mincho',serif;font-weight:600;font-size:15px;line-height:1.6;letter-spacing:.03em}"
       ".rk-d{grid-column:2;font-size:11px;color:#8A7F76}.rk-b{padding:0 16px 16px;font-size:13.5px;line-height:1.95;color:#3A332E}"
       ".rk-b h4{margin:14px 0 4px;font-size:13px;letter-spacing:.06em;color:var(--c)}.rk-b ul{margin:0;padding-left:1.2em}.rk-b p{margin:10px 0 0}"
       ".rk-l{font-weight:700}.rk-n,.rk-s{font-size:12px;color:#7A6E66}.rk-s a{color:inherit}.rk-sub{font-size:12px;color:#7A6E66;margin:-6px 0 12px}"
       ".rk-m{margin-top:14px;padding-top:12px;border-top:1px solid #E6E7EA}.rk-m small{display:block;font-size:11px;letter-spacing:.14em;color:#8A7F76;margin-bottom:6px}"
       ".rk-m a{display:inline-block;margin:0 8px 8px 0;padding:6px 12px;border:1px solid #D9D2CB;border-radius:99px;color:#2B2622;text-decoration:none;font-size:12.5px}"
       "</style>")
s = s.replace("</head>", CSS + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
    s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + "関西まちランキング 駅・地価・人口の順位", s, count=1)
s = s.replace(BASE + 'hatsumode"', BASE + 'ranking"')
s = s.replace('<body data-kind="初詣">', '<body data-kind="関西まちランキング">', 1)
s = re.sub(r'<div class="en">[^<]*</div>', '<div class="en">KANSAI TOWN RANKING</div>', s, count=1)
s = re.sub(r"<h1>.*?</h1>", "<h1>関西まちランキング<span>駅・地価・人口を公式の数字で</span></h1>", s, count=1, flags=re.S)
s = re.sub(r'<p class="sub">.*?</p>', f'<p class="sub">関西の街を、公式の数字で順位にしました。<br>題を押すと、くわしい順位が開きます。</p>', s, count=1, flags=re.S)
s = re.sub(r'<div class="upd">.*?</div>', f'<div class="upd">{TODAY.year}年{TODAY.month}月{TODAY.day}日 更新・{N}本</div>', s, count=1, flags=re.S)
s = re.sub(r'<div class="flt" id="flt">.*?</div>', "", s, count=1, flags=re.S)
a = s.index('<section id="'); b = s.index('<section class="faq">'); e = s.index("</section>", b) + len("</section>")
s = s[:a] + secs + s[e:]
s = re.sub(r'<p class="note">.*?</p>', '<p class="note">数字は、鉄道会社・国・府県・市町村が出している統計です（それぞれの順位の中に、何の数字かを書いています）。順位は調べた日のもので、新しい発表で変わることがあります。街の名前を押すと、その街の地価や人口のページが開きます。</p>', s, count=1, flags=re.S)
s = re.sub(r'<nav class="also".*?</nav>', '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/chika-kansai" data-k="あわせて：地価ランキング">関西205の街の地価ランキング</a><a href="/jikka/shindan/" data-k="あわせて：3問診断">実家・空き家の3問診断</a><a href="/uru" data-k="あわせて：家を売りたい">家を売りたい</a></nav>', s, count=1, flags=re.S)
s = re.sub(r'<a class="back" href="/odekake">.*?</a>', '<a class="back" href="/moushikomi?want=%E6%9F%BB%E5%AE%9A%E3%81%97%E3%81%A6%E3%81%BB%E3%81%97%E3%81%84" data-k="ランキング｜いくらで売れるか聞く" style="display:block;background:#3A332E;color:#fff;border:0;border-radius:12px;padding:15px 16px;margin:18px 0 14px;text-align:center;text-decoration:none;font-weight:700;font-size:15px">お家がいくらで売れるか、無料で聞く</a><a class="back" href="/fudosan-list">関西不動産リストを見る</a>', s, count=1, flags=re.S)
# 借りた形の、初詣用のスクリプト（カードの日付・数え方・地図・宿）を外し、このページの数え方だけ入れる
def _sc(m):
    a, b = m.group(1), m.group(2)
    if "ld+json" in a or "night.js" in a or "menu.js" in a or "v2sub.js" in a: return m.group(0)
    return ""
s = re.sub(r"<script([^>]*)>(.*?)</script>", _sc, s, flags=re.S)
JS = ('<script>(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1";}catch(e){}'
      'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
      'c("表示：関西まちランキング"+(document.referrer&&!/townnote\\.pages/.test(document.referrer)?"（外から）":""));'
      'document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("[data-k]"):null;if(a)c("クリック：関西まちランキング｜"+a.getAttribute("data-k"));});'
      'document.querySelectorAll("details.rk").forEach(function(d){d.addEventListener("toggle",function(){if(d.open)c("ランキング｜開いた｜"+d.id);});});'
      'var h=location.hash.slice(1),t=h&&document.getElementById(h);if(t&&t.tagName==="DETAILS"){t.open=true;t.scrollIntoView();}'
      'else{document.querySelectorAll("section.ps").forEach(function(s){var d=s.querySelector("details.rk");if(d)d.open=true;});}})();</script>')
s = s.replace("</body>", JS + "</body>", 1)
s = re.sub(r"/\*.*?\*/", lambda m: "" if "初詣" in m.group(0) else m.group(0), s, flags=re.S)
# 夜の画面は night.js が全体の色を反転して作る。ページ側で html.night の色を書くと二重に反転して読めなくなる
assert "html.night .rk" not in s, "ページ側に夜の色を書かない"
assert "初詣" not in s, "初詣の言葉が残っている: " + s[max(0, s.index("初詣") - 80):s.index("初詣") + 60]
open(os.path.join(ROOT, "links", "ranking.html"), "w", encoding="utf-8").write(s)
print("ranking", N, "items", {k: len(v) for k, v in groups.items()})
