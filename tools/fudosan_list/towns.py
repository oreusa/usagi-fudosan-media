"""関西不動産リスト：関西6府県の市・区・町ぜんぶの「住宅地の地価」を、街ごとのページ・ランキング・地図用のデータにする。
11/1 オーナー「街少なすぎだろ」「俺に言われそうな事全部先立ってやれよ」→ 全部の街を入れる。
数字は各府県・国土交通省が出した令和8年地価公示（2026年1月1日時点）の「住宅地の対前年平均変動率」。
元の数字: tools/fudosan_list/towns/*.csv（名前,R7,R8[,平均価格]）
使い方: python3 tools/fudosan_list/towns.py [--live]
出力: links/assets/towns.json（検索・地図用）, links/machi/<id>.html（街ごとのページ）, links/chika-kansai.html（ランキング）
"""
import html, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = os.path.join(ROOT, "tools/fudosan_list/towns")
live = "--live" in sys.argv
E = html.escape
BASE = "https://townnote.pages.dev"
TODAY = "2026年11月1日"

PREFS = [  # (府県, csv, 英字, 色, 出典の名前, 出典URL, 府県の言い方)
    ("大阪", "osaka", "OSAKA", "#B97A62", "大阪府「令和8年地価公示 報道資料」p.5 市区町村別対前年平均変動率", "https://www.pref.osaka.lg.jp/documents/125605/houdour8_1.pdf", "大阪府"),
    ("京都", "kyoto", "KYOTO", "#8A7495", "京都府「令和8年地価公示の概要」6 市区町村別平均変動率", "https://www.pref.kyoto.jp/youchi/documents/r8tikakouzigaiyou.pdf", "京都府"),
    ("兵庫", "hyogo", "HYOGO", "#4F6681", "兵庫県「令和8年地価公示 価格の概要」市区町別 住宅地の変動率の推移", "https://web.pref.hyogo.lg.jp/ks21/documents/r8chikakojikakaku.pdf", "兵庫県"),
    ("奈良", "nara", "NARA", "#6F8C68", "国土交通省「令和8年地価公示」市の対前年平均変動率（大阪圏）", "https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/content/001986144.pdf", "奈良県"),
    ("滋賀", "shiga", "SHIGA", "#5F8F98", "滋賀県「令和8年地価公示（滋賀県）結果概要」第4-1表 市町別平均価格および平均変動率", "https://www.pref.shiga.lg.jp/file/attachment/5598454.pdf", "滋賀県"),
    ("和歌山", "wakayama", "WAKAYAMA", "#C4925A", "和歌山県「令和8年地価公示 市町別平均価格及び対前年平均変動率」", "https://www.pref.wakayama.lg.jp/prefg/022200/tochi/tikatyousa/r4kouji/d00221878_d/fil/r8-1_heikinhendouritsu.pdf", "和歌山県"),
]
PI = {p[0]: p for p in PREFS}

# ---- 地図の形（links/townnotes/kansai.json：国土数値情報を加工した物）
K = json.load(open(os.path.join(ROOT, "links/townnotes/kansai.json"), encoding="utf-8"))


def full(pr):
    c = pr.get("c") or ""
    return pr["n"] if c.endswith("郡") or not c else c + pr["n"]


LAB = {(f["properties"]["p"], full(f["properties"])): f["geometry"]["coordinates"] for f in K["lab"]["features"]}
SHAPE = {}
for f in K["muni"]["features"]:
    SHAPE.setdefault((f["properties"]["p"], full(f["properties"])), []).append(f["geometry"])

# ---- 数字を読む
towns = []
for pf, fn, en, col, sname, surl, pfull in PREFS:
    rows = [l.strip().split(",") for l in open(os.path.join(T, fn + ".csv"), encoding="utf-8") if l.strip()]
    for i, r in enumerate(rows):
        name = r[0]
        r7 = float(r[1]) if r[1] != "" else None
        r8 = float(r[2])
        price = int(r[3]) if len(r) > 3 and r[3] else None
        ll = LAB.get((pf, name))
        assert ll, (pf, name)
        towns.append({"id": f"{fn}-{i + 1:02d}", "p": pf, "n": name, "r7": r7, "r8": r8, "price": price,
                      "lon": ll[0], "lat": ll[1]})

# 府県ごとの順位（同じ数字は同じ順位）
for pf in PI:
    ts = sorted([t for t in towns if t["p"] == pf], key=lambda t: -t["r8"])
    prev, pr = None, 0
    for n, t in enumerate(ts, 1):
        if t["r8"] != prev:
            pr = n
        prev = t["r8"]
        t["rank"], t["of"] = pr, len(ts)
# 関西ぜんぶの順位
ts = sorted(towns, key=lambda t: -t["r8"])
prev, pr = None, 0
for n, t in enumerate(ts, 1):
    if t["r8"] != prev:
        pr = n
    prev = t["r8"]
    t["krank"] = pr


def pct(v):
    if v is None:
        return "―"
    return ("+" if v > 0 else "−" if v < 0 else "±") + f"{abs(v):.1f}%"


def short(n):
    """検索用の短い名前（大阪市北区→北区、西宮市→西宮）"""
    s = re.sub(r"^(大阪|堺|京都|神戸)市", "", n)
    return s


FACTS = json.load(open(os.path.join(ROOT, "tools/fudosan_list/facts.json"), encoding="utf-8"))


def related(t):
    s = short(t["n"])
    key = re.sub(r"(市|町|村)$", "", s) if not s.endswith("区") else s
    if len(key) < 2:
        return []
    out = []
    for o in FACTS:
        if o["pref"] != t["p"]:
            continue
        txt = o["t"] + o["m"]
        if s.endswith("区"):
            sakai = t["n"].startswith("堺市")
            if s in txt and (("堺" in txt) == sakai):
                out.append(o)
        elif key in txt:
            out.append(o)
    return out[:4]


# ---- 府県の小さな地図（SVG、この街だけ色をつける）
def proj(lon, lat, b):
    x0, y0, x1, y1 = b
    k = math.cos(math.radians((y0 + y1) / 2))
    w = (x1 - x0) * k
    h = y1 - y0
    s = 300 / max(w, h)
    return ((lon - x0) * k * s, (y1 - lat) * s)


def rings(g):
    if g["type"] == "Polygon":
        return g["coordinates"]
    return [r for poly in g["coordinates"] for r in poly]


def pref_svg(pf, hi):
    # 政令市の区は、市の中だけを大きく描く（府県全体だと区が小さすぎて見えない）
    city = re.match(r"^(大阪市|堺市|京都市|神戸市)", hi)
    keys = [k for k in SHAPE if k[0] == pf and (not city or k[1].startswith(city.group(1)))]
    xs, ys = [], []
    for k in keys:
        for g in SHAPE[k]:
            for r in rings(g):
                for x, y in r:
                    xs.append(x)
                    ys.append(y)
    b = (min(xs), min(ys), max(xs), max(ys))
    W, H = proj(b[2], b[1], b)
    col = PI[pf][3]
    ps = []
    for k in keys:
        d = ""
        for g in SHAPE[k]:
            for r in rings(g):
                pts = [proj(x, y, b) for x, y in r]
                d += "M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z"
        on = k[1] == hi
        ps.append(f'<path d="{d}" fill="{col if on else "#F1F2F4"}" stroke="#fff" stroke-width="{0.8 if not on else 1.2}"/>')
    # 色をつけた街を最後に描く（線が上に来るように）
    ps.sort(key=lambda s: col in s)
    # 小さい街でも場所がわかるように、街の中心に輪をつける
    pin_s = ""
    if (pf, hi) in LAB:
        cx, cy = proj(*LAB[(pf, hi)], b)
        # 11/4 オーナーが20案から選んだ「ネオン」：線だけのしずくに家の絵。夜は明るい線が光る（night.js）
        nl = "#" + "".join("%02x" % round(int(col[i:i + 2], 16) * .5 + 255 * .5) for i in (1, 3, 5))
        pin_s = (f'<g class="neo" transform="translate({cx:.0f},{cy:.0f}) scale(.8)" style="color:{col};--nl:{nl};filter:drop-shadow(0 1.5px 1.5px rgba(0,0,0,.2))"><ellipse class="nsh" cx="0" cy="1" rx="6" ry="2.2" fill="#2B2622" opacity=".2"/>'
                  f'<path class="nh" d="M0 0C-3-7-12-12-12-22a12 12 0 0 1 24 0C12-12 3-7 0 0Z" fill="none" stroke="{col}" stroke-width="6.8" stroke-opacity="0" stroke-linejoin="round"/>'
                  f'<path class="nb" d="M0 0C-3-7-12-12-12-22a12 12 0 0 1 24 0C12-12 3-7 0 0Z" fill="#fff" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>'
                  f'<path class="ni" d="M-4.6 -21.2L0 -25.4L4.6 -21.2V-17.4H-4.6Z" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/><path class="ni" d="M-1.3 -17.4V-20H1.3V-17.4" fill="none" stroke="{col}" stroke-width="1.3"/></g>')
    # 11/1 オーナー「地図はちゃんと地名まで入れる」→ まわりの街の名前も、重ならない所に置く
    area = {}
    for k in keys:
        xs2 = [x for g in SHAPE[k] for r in rings(g) for x, _ in r]
        ys2 = [y for g in SHAPE[k] for r in rings(g) for _, y in r]
        area[k] = (max(xs2) - min(xs2)) * (max(ys2) - min(ys2))
    labs, grp = [], {}
    for k in keys:
        if k not in LAB:
            continue
        cty = re.match(r"^(大阪市|堺市|京都市|神戸市)", k[1])
        if cty and not city:
            g = grp.setdefault(cty.group(1), [])
            g.append(proj(*LAB[k], b))
            continue
        nm = k[1][len(city.group(1)):] if city else k[1]
        x, y = proj(*LAB[k], b)
        labs.append((1e9 if k[1] == hi else area[k], x, y, nm, k[1] == hi))
    for cn, pts in grp.items():
        labs.append((1e8, sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), cn, False))
    labs.sort(key=lambda l: -l[0])
    boxes, tx = [], []
    for _, x, y, nm, on in labs:
        fs = 15 if on else 10.5
        w, h = len(nm) * fs * 1.02, fs * 1.2
        for dx, dy in ([(0, 19), (0, -30), (w * .6 + 8, 0), (-w * .6 - 8, 0), (w * .6 + 8, -14), (-w * .6 - 8, -14)] if on else [(0, 0), (0, -h), (0, h)]):
            bx = (x + dx - w / 2, y + dy - h / 2, x + dx + w / 2, y + dy + h / 2)
            if bx[0] < -4 or bx[2] > W + 4 or bx[1] < -4 or bx[3] > H + 4:
                continue
            if any(bx[0] < o[2] and bx[2] > o[0] and bx[1] < o[3] and bx[3] > o[1] for o in boxes):
                continue
            boxes.append(bx)
            tx.append(f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" font-size="{fs}" font-weight="{700 if on else 500}" fill="{"#2B2622" if on else "#5C5048"}">{E(nm)}</text>')
            break
        else:
            if on:  # 自分の街の名前は必ず出す（はみ出す時は内側へ寄せる）
                cx2 = min(max(x, w / 2), W - w / 2)
                cy2 = min(max(y - 16, h / 2), H - h / 2)
                tx.append(f'<text x="{cx2:.0f}" y="{cy2:.0f}" font-size="{fs}" font-weight="700" fill="#2B2622">{E(nm)}</text>')
    ps.append('<g style="font-family:\'Zen Kaku Gothic New\',sans-serif;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round;text-anchor:middle;dominant-baseline:central">' + "".join(tx) + '</g>')
    ps.append(pin_s)  # しずくは名前より上に描く
    return f'<svg viewBox="-4 -4 {W + 8:.0f} {H + 8:.0f}" role="img" aria-label="{E(PI[pf][6])}の地図。{E(hi)}の場所">{"".join(ps)}</svg>'


def scope_name(t):
    m = re.match(r"^(大阪市|堺市|京都市|神戸市)", t["n"])
    return m.group(1) if m else PI[t["p"]][6]


def near(t, n=6):
    def dist(a):
        return (a["lat"] - t["lat"]) ** 2 + ((a["lon"] - t["lon"]) * 0.82) ** 2
    return sorted([a for a in towns if a is not t], key=dist)[:n]


HEAD_CSS = """body{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}
.wrap{max-width:440px;margin:0 auto;padding:0 16px 40px}
.head{text-align:center;margin:0 -16px;padding:30px 16px 22px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px)}
.head img{width:60px;height:60px}
.en{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}
h1{font-family:"Shippori Mincho",serif;font-weight:600;font-size:23px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:14px 0 8px;font-feature-settings:"palt"}
h1 span{display:block;font-size:14px;letter-spacing:.2em;color:#6B6058;margin-top:4px}
.sub{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}
.upd{font-size:11px;color:#8C7B6E;margin-top:8px}
h2{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:30px 0 8px;padding-left:10px;border-left:3px solid var(--pc,#B97A62)}
.cap{font-size:11.5px;color:#8C7B6E;margin:0 0 10px;line-height:1.7}
.faq details{background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);margin-bottom:8px;padding:12px 16px}
.faq summary{font-weight:700;font-size:14px;line-height:1.6;cursor:pointer}.faq p{font-size:13px;line-height:1.9;color:#5E544D;margin:8px 0 0}
.note{font-size:12px;line-height:1.9;color:#7A6E66;background:#F5F5F5;padding:14px 16px;margin-top:30px;word-break:break-all}.note a{color:#7A6E66}
.itt{margin:30px 0 6px;text-align:center}.itt .en2{font-family:Jost,sans-serif;font-size:11px;letter-spacing:.32em;color:#9C8775}.itt h2{margin:6px 0 14px;padding-left:0;border-left:0;font-size:20px}.itg{display:grid;grid-template-columns:1fr 1fr;gap:10px;text-align:left}.itc{display:flex;flex-direction:column;text-decoration:none;color:#2B2622;border:1px solid #E3E3E3;border-radius:18px;padding:16px 14px;background:#fff}.itc b{font-family:"Shippori Mincho",serif;font-size:17px;font-weight:700;letter-spacing:.06em}.itc span{font-size:12.5px;line-height:1.75;color:#6B6058;margin:8px 0 12px;flex:1}.itc i{font-style:normal;font-weight:700;font-size:13.5px;color:#B5735A}.itn{font-size:11.5px;color:#8C7B6E;text-align:left;margin:8px 2px 0}
.uru{display:block;text-decoration:none;color:#2B2622;border:1px solid #2B2622;padding:16px;margin-top:30px;text-align:center}
.uru .k{font-size:11px;letter-spacing:.2em;color:#8C7B6E}.uru .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.08em;margin:6px 0 4px}.uru .m{font-size:12px;color:#6B6058;line-height:1.8}
.uru.buy{position:relative;margin-top:18px;padding:16px 14px 6px}.uru .bx{display:block;text-decoration:none;color:#2B2622;border-top:1px solid #E4E5E8;padding:12px 2px;text-align:left}.uru .k+.ad+.bx{margin-top:10px}.uru .bx b{display:block;font-family:"Shippori Mincho",serif;font-size:15px;font-weight:600}.uru .bx b:after{content:" →";color:#B5735A}.uru .bx span{display:block;font-size:11.5px;color:#6B6058;line-height:1.7;margin-top:3px}.uru .ad{position:absolute;top:6px;right:8px;font-size:10px;color:#8C7B6E}
.back{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}
.ft{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">'
SCRIPTS = '<script src="/assets/night.js?v=22"></script><script src="/assets/menu.js?v=36" defer></script><script src="/assets/v2sub.js?v=10" defer></script>'


def beacon(name):
    return ('<script>(function(){var O=(function(){try{return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();'
            'function s(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
            f's({json.dumps("表示：" + name, ensure_ascii=False)});'
            'document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a");if(!a)return;'
            f's({json.dumps("クリック：" + name + "｜", ensure_ascii=False)}+(a.getAttribute("data-k")||a.textContent.trim().slice(0,30)));}},true);}})();</script>')


def head(title, desc, url, ld=None):
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><meta name="description" content="{E(desc)}">'
            + ('' if live else '<meta name="robots" content="noindex">') + (f'<link rel="canonical" href="{url}">' if live else '')
            + f'<meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">'
            f'<meta property="og:image" content="{BASE}/assets/ogp.png"><meta name="twitter:card" content="summary">'
            f'<link rel="icon" href="/assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">{FONTS}'
            + (f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''))


# 家を探す方へ（バリューコマース Yahoo!不動産 流通領域・関西おでかけリスト sid 3786315 で提携済み）
from urllib.parse import quote as _q
YAHOO_RE = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3786315&pid=892742459&vc_url=" + _q("https://realestate.yahoo.co.jp/", safe="")
# 11/8 オーナー「アフェリエイト通った全部」→ タウンライフ不動産購入・住まいサーフィン（同じ sid の自由テキスト）
TOWNLIFE_RE = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3786315&pid=892742460"
SUMAI_RE = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3786315&pid=892742461"
# 11/9 夜の試験：タウンライフ・住まいサーフィンのリンクは「無効の広告」ページに進む（ミス帳#134・#135）→ 使えると確かめるまで出さない
VC_EXTRA_ON = False

# ---- 売れた家の値段（近畿レインズ 年刊市況レポート 2025年度 表19・表20 市区町村別成約状況）
REINS_URL = "https://www.kinkireins.or.jp/webkanri/kanri/wp-content/uploads/2026/09/4aa7279bc826c2683d1525bd813d9696.pdf"
REINS_URL2 = "https://www.kinkireins.or.jp/webkanri/kanri/wp-content/uploads/2026/09/120a1802d9600c553a3dfbfc913812fd.pdf"
REINS_NAME = "近畿レインズ「2025年度 年刊市況レポート」表19 中古マンション・表20 中古戸建住宅の市区町村別成約状況"
PFULL = {"大阪": "大阪府", "京都": "京都府", "兵庫": "兵庫県", "奈良": "奈良県", "滋賀": "滋賀県", "和歌山": "和歌山県"}
ALIAS = {("兵庫県", "丹波篠山市"): ("兵庫県", "篠山市")}  # 表では旧名「篠山市」
SOLD, SOLD_PREF = {}, {}
import csv as _csv
for _k, _fn in (("m", "mansion_2025"), ("k", "kodate_2025")):
    for _r in _csv.DictReader(open(os.path.join(T, "../reins", _fn + ".csv"), encoding="utf-8")):
        _nm = _r["市区町村"]
        if _nm == "合計" and not _r["地域見出し"]:
            SOLD_PREF.setdefault(_r["府県"], {})[_k] = _r
            continue
        if not _nm or _nm == "合計":
            continue
        if _r["地域見出し"] in ("大阪市", "京都市", "神戸市"):
            _nm = _r["地域見出し"] + _nm
        SOLD.setdefault((_r["府県"], _nm), {})[_k] = _r


def sold_of(t):
    key = (PFULL[t["p"]], t["n"])
    return SOLD.get(ALIAS.get(key, key), {})


def man(v):
    v = int(round(float(v)))
    return f"{v // 10000}億{v % 10000:,}万円" if v >= 10000 else f"{v:,}万円"

# ================= 街ごとのページ
TOWN_CSS = """.big{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:20px 0 0}
.big div{background:#F5F5F5;padding:12px 14px}.big b{display:block;font-family:Jost;font-size:24px;font-weight:500;color:var(--pc)}.big span{font-size:11px;color:#7A6E66;letter-spacing:.04em}
.big .w{grid-column:1/3}.big .w b{font-size:15px;font-family:"Zen Kaku Gothic New";font-weight:700;color:#2B2622;line-height:1.7}
.mp{margin:14px 0 0;padding:14px;background:#fff;border:1px solid #ECECEC}.mp svg{display:block;width:100%;height:auto;max-height:280px}
.mp p{font-size:11px;color:#8C7B6E;margin:8px 0 0;text-align:center}
.nb{list-style:none;margin:0;padding:0}.nb li{border-bottom:1px solid #ECECEC}
.nb a{display:flex;justify-content:space-between;align-items:center;padding:12px 2px;text-decoration:none;color:#2B2622;font-weight:700;font-size:14px}
.nb a b{font-family:Jost;font-weight:500;font-size:15px}.nb a small{font-size:11px;color:#8C7B6E;font-weight:500;margin-left:6px}
.fc{display:block;text-decoration:none;color:#2B2622;background:#fff;border-left:3px solid var(--pc);box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);padding:12px 14px;margin-bottom:10px}
.fc small{display:block;font-size:11px;color:#8C7B6E}.fc b{display:block;font-size:14.5px;line-height:1.6;margin:3px 0}.fc span{font-size:12.5px;color:#5E544D;line-height:1.7}
.sold{display:grid;grid-template-columns:1fr 1fr;gap:10px}.sold>div{background:#fff;border:1px solid #ECECEC;border-top:3px solid var(--pc);padding:12px 14px}
.sold .k{font-size:11.5px;color:#7A6E66;font-weight:700}.sold b{display:block;font-family:Jost,"Zen Kaku Gothic New";font-size:23px;font-weight:500;color:#2B2622;margin:2px 0 4px;line-height:1.3}
.sold ul{list-style:none;margin:0;padding:0;font-size:12px;color:#5E544D;line-height:1.75}.sold .vs{font-size:11.5px;color:#7A6E66;margin-top:4px}.sold .few{font-size:11px;color:#B26A00;margin-top:4px}
.sold .no{font-size:12.5px;color:#7A6E66;line-height:1.7}
@media(max-width:380px){.sold{grid-template-columns:1fr}}
.sell{display:block;text-decoration:none;color:#fff;background:#3A2F28;border-radius:12px;padding:14px 16px;margin:12px 0 0}.sell small{display:block;font-size:11.5px;opacity:.8}.sell b{display:block;font-size:15px;margin-top:2px}
.rq{display:block;width:100%;margin:10px 0 0;padding:13px;border:0;border-radius:12px;background:#3A2F28;color:#fff;font-family:"Zen Kaku Gothic New",sans-serif;font-size:13.5px;font-weight:700;cursor:pointer}.rq:disabled{background:#8C7B6E}"""


def town_page(t):
    pf, fn, en, col, sname, surl, pfull = PI[t["p"]]
    n = t["n"]
    up = t["r8"] > 0
    word = "上がりました" if t["r8"] > 0 else "下がりました" if t["r8"] < 0 else "変わりませんでした"
    trend = ""
    if t["r7"] is not None:
        d = round(t["r8"] - t["r7"], 1)
        trend = "前の年より上がり幅が大きくなりました" if d > 0 and up else "前の年より上がり幅が小さくなりました" if d < 0 and up else \
            "前の年より下がり幅が小さくなりました" if d > 0 and t["r8"] < 0 else "前の年より下がり幅が大きくなりました" if d < 0 and t["r8"] < 0 else \
            "前の年と同じ動きでした" if d == 0 else ""
    title = f"{n}の地価 2026｜住宅地は{pct(t['r8'])}（令和8年地価公示）"
    desc = (f"{pfull}{n}の住宅地の地価は、令和8年地価公示（2026年1月1日時点）で前の年から{pct(t['r8'])}。"
            f"{pfull}の{t['of']}の市区町村で{t['rank']}位です。" + (f"前の年は{pct(t['r7'])}。" if t['r7'] is not None else ""))
    rel = related(t)
    nb = near(t)
    faq = [(f"{n}の住宅地の地価は上がっていますか？",
            f"令和8年地価公示（2026年1月1日時点）で、{n}の住宅地は前の年から平均{pct(t['r8'])}{'で' if True else ''}、{word}。" + (f"前の年（令和7年）は{pct(t['r7'])}でした。" if t["r7"] is not None else "")),
           (f"{n}は{pfull}で何位ですか？",
            f"住宅地の上がり幅で、{pfull}の{t['of']}の市区町村のうち{t['rank']}位です（このページで比べた市区町村の中での順位）。"),
           ("この数字で、わが家の値段がわかりますか？",
            "わかりません。街の中の調査地点の平均の動きで、1軒ずつの値段ではありません。家の値段は、場所・広さ・築年数などで大きく変わります。")]
    url = f"{BASE}/machi/{t['id']}"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Dataset", "name": f"{n}の住宅地の地価の変動率（令和8年地価公示）", "description": desc, "isBasedOn": surl,
         "temporalCoverage": "2026-01-01", "spatialCoverage": f"{pfull}{n}"},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "関西不動産リスト", "item": f"{BASE}/fudosan-list"},
            {"@type": "ListItem", "position": 2, "name": "関西 地価ランキング", "item": f"{BASE}/chika-kansai"},
            {"@type": "ListItem", "position": 3, "name": f"{n}の地価", "item": url}]}]}
    big = (f'<div class="big"><div><span>住宅地 1年の動き</span><b style="color:{col if t["r8"] > 0 else "#6B6058"}">{pct(t["r8"])}</b></div>'
           f'<div><span>{pfull}での順位</span><b style="color:#2B2622">{t["rank"]}<small style="font-size:13px">位／{t["of"]}</small></b></div>'
           + (f'<div><span>前の年（令和7年）</span><b style="color:#6B6058">{pct(t["r7"])}</b></div>' if t["r7"] is not None else '')
           + (f'<div><span>住宅地の平均価格（1㎡）</span><b style="color:#6B6058">{t["price"] / 10000:.2f}万円</b></div>' if t["price"] else '')
           + (f'<div class="w"><b>{E(trend)}。</b></div>' if trend else '') + '</div>')

    sd = sold_of(t)
    sp = SOLD_PREF.get(PFULL[t["p"]], {})

    def card(kind, label):
        r = sd.get(kind)
        if not r or not r["価格万円"]:
            msg = f"2025年度に売れたのは{r['件数']}件だけのため、平均の値段は出ていません。" if r else "2025年度は、売れた記録がありません。"
            return f'<div><div class="k">{label}</div><p class="no">{msg}</p></div>'
        pr, pp = float(r["価格万円"]), sp.get(kind)
        vs = ""
        if pp and pp["価格万円"]:
            d = pr - float(pp["価格万円"])
            vs = f'{E(PFULL[t["p"]])}の平均（{man(pp["価格万円"])}）より{man(abs(d))}{"高い" if d > 0 else "安い"}' if abs(d) >= 1 else f'{E(PFULL[t["p"]])}の平均と同じくらい'
        if kind == "m":
            li = f'<li>1㎡あたり {float(r["㎡単価万円"]):.1f}万円</li><li>広さ {float(r["専有面積"]):.0f}㎡・築{float(r["築年"]):.0f}年</li>'
        else:
            li = f'<li>土地 {float(r["土地面積"]):.0f}㎡・建物 {float(r["建物面積"]):.0f}㎡</li><li>築{float(r["築年"]):.0f}年</li>'
        few = '<div class="few">売れた数が少ないので目安です</div>' if int(r["件数"]) < 10 else ""
        return (f'<div><div class="k">{label}</div><div class="vs">{int(r["件数"]):,}件の平均</div><b>{man(pr)}</b><ul>{li}</ul>'
                + (f'<div class="vs">{vs}</div>' if vs else '') + few + '</div>')

    sold_h = (f'<h2>この街で売れた家の値段</h2><p class="cap">2025年度に{E(n)}で実際に売れた（成約した）中古の家の平均です。不動産会社が登録する「レインズ」の数字です。</p>'
              f'<div class="sold">{card("m", "中古マンション")}{card("k", "中古の一戸建て")}</div>')
    # 11/9 オーナーOK（見本3）：街ページの下は「売りたい・買いたい」の2つだけ（売る前に・Yahoo!の箱はここにまとめた）
    itt = (f'<section class="itt"><div class="en2">IN THIS TOWN</div><h2>{E(n)}で</h2><div class="itg">'
           f'<a class="itc" href="/uru.html" data-k="この街で｜売りたい｜{E(n)}"><b>売りたい</b><span>いくらで売れそうか、相場から順に（無料）</span><i>手順を見る →</i></a>'
           f'<a class="itc" href="{E(YAHOO_RE)}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜Yahoo!不動産｜{E(n)}"><b>買いたい</b><span>Yahoo!不動産で地域を選んで、売り出し中の家を見る</span><i>物件を探す →</i></a>'
           f'</div><p class="itn">「物件を探す」は広告です（Yahoo!不動産のトップが開きます）。</p></section>')
    rel_h = ""
    if rel:
        rel_h = '<h2>この街で調べた数字</h2>' + "".join(
            f'<a class="fc" href="{E(o["url"])}" data-k="関連｜{E(o["t"][:20])}"><small>{E(o["src"])}</small><b>{E(o["t"].replace("｜", "　"))}</b><span>{E(o["m"])}</span></a>' for o in rel)
    nb_h = '<h2>近くの街</h2><ul class="nb">' + "".join(
        f'<li><a href="/machi/{a["id"]}" data-k="近くの街｜{E(a["n"])}">{E(a["n"])}<small>{E(a["p"])}</small><b style="color:{PI[a["p"]][3]}">{pct(a["r8"])}</b></a></li>' for a in nb) + '</ul>'
    tl_a = (f'<a class="bx" href="{E(TOWNLIFE_RE)}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜タウンライフ｜{E(n)}"><b>希望を1回送って、物件を提案してもらう</b><span>タウンライフ不動産。予算や駅を送ると、何社かから物件のご提案が届きます（無料）</span></a>' if VC_EXTRA_ON else '')
    su_a = (f'<a class="bx" href="{E(SUMAI_RE)}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜住まいサーフィン｜{E(n)}"><b>新築マンションが割高か調べる</b><span>住まいサーフィン。値段が割高か割安かを、無料の会員登録で</span></a>' if VC_EXTRA_ON else '')
    body = f'''<style>{HEAD_CSS}{TOWN_CSS}</style>{SCRIPTS}</head><body style="--pc:{col}"><div class="wrap">
<div class="head"><img src="/assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ"><div class="en">{en} ─ LAND PRICE</div>
<h1>{E(n)}の地価<span>2026 住宅地の1年の動き</span></h1>
<p class="sub">国の地価公示の数字で、<br>{E(pfull)}{E(n)}の住宅地の動きを見ます。</p>
<div class="upd">2026年1月1日時点の数字（{TODAY} 作成）</div></div>
{big}
<div class="mp nofilt">{pref_svg(t["p"], n)}<p>{E(scope_name(t))}の中の{E(short(n) if scope_name(t) != pfull else n)}</p></div>
{sold_h}
{itt}
{rel_h}
{nb_h}
<a class="back" href="/chika-kansai#{fn}" data-k="{E(pfull)}のランキング" style="margin-top:18px">{E(pfull)}の街をランキングで見る</a>
<h2>この街をもっと調べてほしい</h2><p class="cap">駅ごとの地価や人口など、もっと細かく知りたい方はボタンを押してください。押された街から順に調べて、このリストに足します。</p>
<button class="rq" type="button" data-n="{E(n)}">{E(n)}をもっと調べてほしい</button>
<section class="faq"><h2>よくある質問</h2>
{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}
</section>
<p class="note">出典：{E(sname)}（価格時点 2026年1月1日）<br><a href="{E(surl)}" data-k="出典">{E(surl)}</a><br>数字は街の中の調査地点の平均の変動率で、1軒ずつの値段ではありません。<br>売れた家の値段：{E(REINS_NAME)}<br>表19 <a href="{REINS_URL}" data-k="出典｜レインズ">{REINS_URL}</a><br>表20 <a href="{REINS_URL2}" data-k="出典｜レインズ">{REINS_URL2}</a><br>平均の値段で、1軒ずつの値段ではありません。広さ・築年数・駅からの近さで大きく変わります。</p>
<a class="back" href="/fudosan-list" data-k="関西不動産リストへ">関西不動産リストを見る</a>
<div class="ft">TOWN NOTE</div></div>
<script>(function(){{var b=document.querySelector(".rq");if(!b)return;b.onclick=function(){{try{{if(localStorage.getItem("usagi_owner")!=="1"){{var d=JSON.stringify({{k:"調べてほしい："+b.dataset.n}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",d)))fetch("/c",{{method:"POST",body:d,keepalive:true}});}}}}catch(e){{}}b.disabled=true;b.textContent="受け付けました。調べて、このリストに足します";}};}})();</script>
{beacon("街｜" + n)}</body></html>'''
    return head(title, desc, url, ld) + body


os.makedirs(os.path.join(ROOT, "links/machi"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "links/machi")):
    if f.endswith(".html"):
        os.remove(os.path.join(ROOT, "links/machi", f))
for t in towns:
    open(os.path.join(ROOT, "links/machi", t["id"] + ".html"), "w", encoding="utf-8").write(town_page(t))

# ================= 検索・地図用のデータ
# 11/6 夜「すいた・にしのみや とひらがなで探すと見つからない」→ 読み（kana.json：Code for FUKUI localgovjp の citykana）を k に入れる
KANA = json.load(open(os.path.join(ROOT, "tools/fudosan_list/kana.json"), encoding="utf-8"))
json.dump([{"id": t["id"], "p": t["p"], "n": t["n"], "s": short(t["n"]), "r7": t["r7"], "r8": t["r8"], "rk": t["rank"], "of": t["of"],
            "la": round(t["lat"], 4), "lo": round(t["lon"], 4), "k": KANA.get(t["n"], "").replace(" ", "")} for t in towns],
          open(os.path.join(ROOT, "links/assets/towns.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ================= 関西ランキング
RK_CSS = """.sum{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:20px 0 0}
.sum div{background:#F5F5F5;padding:12px 14px}.sum b{display:block;font-family:Jost;font-size:20px;font-weight:500;color:#B97A62}.sum span{font-size:11px;color:#7A6E66;letter-spacing:.04em}.sum em{font-style:normal;display:block;font-size:13px;font-weight:700;color:#2B2622}
.flt{display:flex;flex-wrap:nowrap;justify-content:center;gap:0 13px;margin:24px 0 8px;padding:10px 0;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4;overflow-x:auto}
.flt button{flex:none;border:none;background:none;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:14px;font-weight:700;letter-spacing:.04em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer;opacity:.85}
.flt button.on{opacity:1;border-bottom-color:currentColor}
ol{list-style:none;margin:0;padding:0}
.r a{display:grid;grid-template-columns:30px 1fr auto;align-items:center;column-gap:10px;row-gap:5px;padding:11px 2px;border-bottom:1px solid #ECECEC;text-decoration:none;color:#2B2622}
.no{font-family:Jost;font-size:14px;color:#9C9187;text-align:center;grid-row:1/3}
.top .no{color:#fff;background:var(--c);border-radius:50%;width:24px;height:24px;line-height:24px;font-size:13px;justify-self:center}
.nm{grid-column:2;grid-row:1;font-weight:700;font-size:14px;letter-spacing:.04em}.nm small{font-size:11px;color:#8C7B6E;font-weight:500;margin-left:6px}
.bar{grid-column:2/4;grid-row:2;height:6px;background:#F1F2F4;position:relative}.bar i{position:absolute;top:0;bottom:0;background:var(--c);opacity:.55}.top .bar i{opacity:1}.bar .z{position:absolute;top:-3px;bottom:-3px;width:1px;background:#B9B9B9}
.v{grid-column:3;grid-row:1;font-family:Jost;font-weight:500;font-size:16px;text-align:right}
.pane{display:none}.pane.on{display:block}
.ilk{display:block;width:max-content;max-width:100%;margin:14px auto 0;color:#2B2622;text-decoration:none;font-family:"Shippori Mincho",serif;font-weight:600;font-size:14px;letter-spacing:.08em;border-bottom:1px solid #2B2622;padding-bottom:3px}"""


def rk_list(ts, show_pref):
    mx = max(abs(t["r8"]) for t in ts) or 1
    mn = min(t["r8"] for t in ts)
    zero = (-min(mn, 0)) / (max(t["r8"] for t in ts) - min(mn, 0) or 1) * 100
    span = (max(t["r8"] for t in ts) - min(mn, 0)) or 1
    out, prev, pr = [], None, 0
    for i, t in enumerate(sorted(ts, key=lambda t: -t["r8"]), 1):
        if t["r8"] != prev:
            pr = i
        prev = t["r8"]
        c = PI[t["p"]][3]
        w = abs(t["r8"]) / span * 100
        left = zero if t["r8"] >= 0 else zero - w
        out.append(f'<li class="r{" top" if pr <= 3 else ""}" style="--c:{c}"><a href="/machi/{t["id"]}" data-k="ランキング｜{E(t["n"])}">'
                   f'<span class="no">{pr}</span><span class="nm">{E(t["n"])}' + (f'<small>{t["p"]}</small>' if show_pref else '') + '</span>'
                   f'<span class="bar"><b class="z" style="left:{zero:.1f}%"></b><i style="left:{left:.1f}%;width:{w:.1f}%"></i></span>'
                   f'<span class="v" style="color:{c if t["r8"] > 0 else "#7A6E66"}">{pct(t["r8"])}</span></a></li>')
    return "\n".join(out)


top = sorted(towns, key=lambda t: -t["r8"])[0]
ups = sum(1 for t in towns if t["r8"] > 0)
desc = (f"関西6府県（大阪・京都・兵庫・奈良・滋賀・和歌山）の{len(towns)}の市区町村の住宅地の地価を、令和8年地価公示の数字で上がり幅の順に並べました。"
        f"1位は{top['n']}（{pct(top['r8'])}）。府県ごとにも見られます。")
panes = [("all", "関西", "関西ぜんぶ", towns, True)] + [(p[1], p[0], p[6], [t for t in towns if t["p"] == p[0]], False) for p in PREFS]
srcs = "<br>".join(f'{E(p[4])}<br><a href="{E(p[5])}" data-k="出典">{E(p[5])}</a>' for p in PREFS)
faq = [("関西で住宅地の地価がいちばん上がった街は？",
        f"令和8年地価公示（2026年1月1日時点）で比べると、{top['n']}（{top['p']}）の{pct(top['r8'])}がいちばん大きい上がり幅でした。"),
       ("上がった街はいくつありますか？",
        f"このページで比べた{len(towns)}の市区町村のうち、住宅地の平均が上がったのは{ups}、変わらなかったのは{sum(1 for t in towns if t['r8'] == 0)}、下がったのは{sum(1 for t in towns if t['r8'] < 0)}でした。"),
       ("のっていない町や村があるのはなぜ？",
        "住宅地の調査地点がない町や村、府県の資料に住宅地の平均が出ていない町や村はのせていません。奈良県は国の資料にある12の市だけです。")]
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Dataset", "name": "関西の市区町村 住宅地の地価ランキング（令和8年地価公示）", "description": desc, "temporalCoverage": "2026-01-01", "spatialCoverage": "関西"},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}
rk = head(f"関西 地価ランキング2026｜{len(towns)}の市区町村の住宅地（令和8年地価公示）", desc, f"{BASE}/chika-kansai", ld) + f'''<style>{HEAD_CSS}{RK_CSS}</style>{SCRIPTS}</head><body><div class="wrap">
<div class="head"><img src="/assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ"><div class="en">KANSAI ─ LAND PRICE</div>
<h1>関西 地価ランキング<span>2026 住宅地の1年の動き</span></h1>
<p class="sub">6府県・{len(towns)}の市区町村を、<br>国の地価公示の数字で並べました。</p>
<div class="upd">2026年1月1日時点の数字（{TODAY} 作成）</div></div>
<div class="sum"><div><span>関西の1位</span><em>{E(top["n"])}</em><b>{pct(top["r8"])}</b></div><div><span>上がった街</span><em>{len(towns)}の街のうち</em><b>{ups}</b></div></div>
<nav class="flt">''' + "".join(f'<button data-p="{k}" style="--pc:{PI[pf][3] if pf in PI else "#2B2622"}"{" class=\"on\"" if k == "all" else ""}>{"すべて" if k == "all" else pf}</button>' for k, pf, _, _, _ in panes) + '</nav>' + \
    "".join(f'<section class="pane{" on" if k == "all" else ""}" id="{k}"><h2 style="--pc:{PI[pf][3] if pf in PI else "#B97A62"}">{E(nm)}の住宅地</h2><p class="cap">上がり幅の順です（値段の順ではありません）。押すと、その街のページが開きます。</p><ol>{rk_list(ts, sp)}</ol>'
            + ('<a class="ilk" href="/chika-osaka" data-k="大阪市24区の商業地も">大阪市24区は、商業地のランキングも →</a>' if k == "osaka" else '') + '</section>' for k, pf, nm, ts, sp in panes) + f'''
<section class="faq"><h2>よくある質問</h2>
{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}
</section>
<a class="uru" href="/uru.html" data-k="お家を売る前に大事なこと"><div class="k">お家を売る・持ち続ける前に</div><div class="t">お家を売る前に大事なこと</div><div class="m">売るか、持ち続けるか。<br>迷ったときに読むページです。</div></a>
<p class="note">出典（価格時点 2026年1月1日）<br>{srcs}<br>数字は街の中の調査地点の平均の変動率で、1軒ずつの値段ではありません。</p>
<a class="back" href="/fudosan-list" data-k="関西不動産リストへ">関西不動産リストを見る</a>
<div class="ft">TOWN NOTE</div></div>
<script>(function(){{function go(k){{var b=document.querySelector('.flt button[data-p="'+k+'"]');if(!b)return;document.querySelectorAll(".flt button,.pane").forEach(function(x){{x.classList.remove("on")}});b.classList.add("on");document.getElementById(k).classList.add("on");}}
document.querySelectorAll(".flt button").forEach(function(b){{b.onclick=function(){{go(b.dataset.p);history.replaceState(null,"","#"+b.dataset.p);}}}});if(location.hash)go(location.hash.slice(1));}})();</script>
{beacon("地価ランキング関西")}</body></html>'''
open(os.path.join(ROOT, "links/chika-kansai.html"), "w", encoding="utf-8").write(rk)
print("ok", len(towns), "towns", "live" if live else "noindex", "rel:", sum(1 for t in towns if related(t)))
