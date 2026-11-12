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
.itg2.itq{background:#3A332E;color:#fff;border:0;border-radius:12px;padding:15px 16px;font-size:15px;font-weight:700;margin-top:12px}
.itg2{display:flex;justify-content:space-between;margin:10px 0 0;padding:11px 14px;border-top:1px solid #E6E6E6;border-bottom:1px solid #E6E6E6;text-decoration:none;color:#5E544D;font-size:13px;text-align:left}.itg2 i{font-style:normal;font-family:Jost;color:#9C8775}
.jmp{display:flex;justify-content:space-between;align-items:center;margin:12px 0 0;padding:13px 16px;border:1px solid #E3E3E3;border-radius:14px;text-decoration:none;color:#2B2622;font-weight:700;font-size:14px;background:#fff}.jmp i{font-style:normal;font-family:Jost;color:#9C8775}.itt{scroll-margin-top:12px}
.itt{margin:30px 0 6px;text-align:center}.itt .en2{font-family:Jost,sans-serif;font-size:11px;letter-spacing:.32em;color:#9C8775}.itt h2{margin:6px 0 14px;padding-left:0;border-left:0;font-size:20px}.itg{display:grid;grid-template-columns:1fr 1fr;gap:10px;text-align:left}.itc{display:flex;flex-direction:column;text-decoration:none;color:#2B2622;border:1px solid #E3E3E3;border-radius:18px;padding:16px 14px;background:#fff}.itc b{font-family:"Shippori Mincho",serif;font-size:17px;font-weight:700;letter-spacing:.06em}.itc span{font-size:12.5px;line-height:1.75;color:#6B6058;margin:8px 0 12px;flex:1}.itc i{font-style:normal;font-weight:700;font-size:13.5px;color:#B5735A}.itc.buy{cursor:default}.itc.buy span{margin-bottom:8px}.itc .yl{display:flex;justify-content:space-between;align-items:center;text-decoration:none;color:#2B2622;font-size:13.5px;font-weight:700;padding:9px 2px;border-top:1px solid #D9DCE1}.itc .yl i{color:#B5735A;font-size:13.5px}.itn{font-size:11.5px;color:#8C7B6E;text-align:left;margin:8px 2px 0}
.uru{display:block;text-decoration:none;color:#2B2622;border:1px solid #2B2622;padding:16px;margin-top:30px;text-align:center}
.uru .k{font-size:11px;letter-spacing:.2em;color:#8C7B6E}.uru .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.08em;margin:6px 0 4px}.uru .m{font-size:12px;color:#6B6058;line-height:1.8}
.uru.buy{position:relative;margin-top:18px;padding:16px 14px 6px}.uru .bx{display:block;text-decoration:none;color:#2B2622;border-top:1px solid #E4E5E8;padding:12px 2px;text-align:left}.uru .k+.ad+.bx{margin-top:10px}.uru .bx b{display:block;font-family:"Shippori Mincho",serif;font-size:15px;font-weight:600}.uru .bx b:after{content:" →";color:#B5735A}.uru .bx span{display:block;font-size:11.5px;color:#6B6058;line-height:1.7;margin-top:3px}.uru .ad{position:absolute;top:6px;right:8px;font-size:10px;color:#8C7B6E}
.back{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}
.ft{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">'
SCRIPTS = '<script src="/assets/night.js?v=29"></script><script src="/assets/menu.js?v=49" defer></script><script src="/assets/v2sub.js?v=12" defer></script>'


def beacon(name, kind="地価ランキング"):
    return ('<script>(function(){var O=(function(){try{return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();'
            'function s(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
            f's({json.dumps("表示：" + name, ensure_ascii=False)});'
            's("表示：'+kind+'"+(document.referrer&&!/usagi-odekake|townnote.pages/.test(document.referrer)?"（外から）":""));'
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

# 11/9 オーナー「動線悪すぎ、Yahoo飛んでまた地名から調べるんだろ？」→ 街ごとの売り出し中の一覧へ直接（全国地方公共団体コード：jis.json、geolonia/japanese-addresses から作成）
JIS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "jis.json"), encoding="utf-8"))
YKIND = [("中古マンション", "used/mansion"), ("中古の一戸建て", "used/house"), ("土地", "land")]


def yahoo_town(p, n, path):
    c = JIS.get(p + "|" + n)
    u = f"https://realestate.yahoo.co.jp/{path}/search/06/{c[:2]}/{c}/" if c else "https://realestate.yahoo.co.jp/"
    return YAHOO_RE.split("&vc_url=")[0] + "&vc_url=" + _q(u, safe="")


def buy_card(p, n):
    rows = "".join(f'<a class="yl" href="{E(yahoo_town(p, n, path))}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜Yahoo!不動産｜{k}｜{E(n)}">{k}<i>→</i></a>' for k, path in YKIND)
    return f'<div class="itc buy"><b>買いたい</b><span>{E(n)}でいま売り出し中の家（Yahoo!不動産）</span>{rows}</div>'

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
    # 11/9 収益化：家を売る・買う人が「◯◯区 土地 相場」「◯◯区 家 売る」で探すので、題にその言葉を入れる（数字は地価公示のまま）
    title = f"{n}の地価・土地相場 2026｜住宅地は{pct(t['r8'])}｜家を売る前・買う前に"
    desc = (f"{pfull}{n}の住宅地の地価は、令和8年地価公示（2026年1月1日時点）で前の年から{pct(t['r8'])}。"
            f"{pfull}の{t['of']}の市区町村で{t['rank']}位です。" + (f"前の年は{pct(t['r7'])}。" if t['r7'] is not None else "") + "家を売る前・買う前に、公式の数字で街の値段の動きを見られます。")
    # 11/9 不動産：検索の説明文に「売れた値段」も（「◯◯区 マンション 売却 相場」で探す人に、開く前から答えが見えるように）
    _sd = sold_of(t)
    _sl = [f"{lb}{man(_sd[k]['価格万円'])}" for k, lb in (("m", "中古マンション"), ("k", "中古一戸建て")) if _sd.get(k) and _sd[k]["価格万円"] and int(_sd[k]["件数"]) >= 10]
    if _sl:
        desc = desc.replace("家を売る前・買う前に、", "2025年度に売れた平均は" + "・".join(_sl) + "（レインズ）。家を売る前・買う前に、")
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
           + (f'<div class="w"><b>{E(trend)}。</b></div>' if trend else '') + '</div>'
           + '<a class="jmp" href="#itt" data-k="街ページ｜売りたい・買いたいへ">この街で 売りたい・買いたい（売り出し中の家）<i>↓</i></a>')

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
    # 11/10 オーナー「実家のやつは不動産リストと完全別に」→ 街ページ⇔実家ノートのリンクは置かない（行き来は MENU のタブだけ）
    # 11/9 オーナーOK（見本3）：街ページの下は「売りたい・買いたい」の2つだけ（売る前に・Yahoo!の箱はここにまとめた）
    itt = (f'<section class="itt" id="itt"><div class="en2">IN THIS TOWN</div><h2>{E(n)}で</h2><div class="itg">'
           f'<a class="itc" href="/uru.html" data-k="この街で｜売りたい｜{E(n)}"><b>売りたい</b><span>いくらで売れそうか、相場から順に（無料）</span><i>手順を見る →</i></a>'
           f'' + buy_card(t["p"], n) + f''
           f'</div>'
           # 11/12 台帳：街ページは外から一番来るのに（7日247回・外から30人）相談へ0回。入口が「手順を見る」と業者さま向けページだけだった → 街の名前入りで、申し込みの2つ目の画面（場所が入った状態）へ直接
           + f'<a class="itg2 itq" href="/moushikomi?lite=1&amp;machi={t["id"]}&amp;want={_q("査定してほしい")}" data-k="この街で｜いくらで売れそうか聞く｜{E(n)}">{E(short(n))}の家、いくらで売れるか無料で聞く <i>→</i></a>'
           + f'<p class="itn" style="text-align:center;margin-top:6px">無料・売るか決めていなくても大丈夫です。メールかお電話、ご希望の方でお返事します。</p>'
           + f'<a class="itg2" href="/moushikomi?machi={t["id"]}&amp;want={_q("相続した家のこと")}" data-k="この街で｜困りごとの相談｜{E(n)}">相続した家・古い家・再建築不可などのご相談 <i>→</i></a>'
           # 11/12 台帳：/kaitai（30秒の目安）は7日で9回しか見られていない。入口が実家ノートにしか無かった → いちばん見られている街ページから1行
           + f'<a class="itg2" href="/kaitai" data-k="この街で｜解体・片付けの費用｜{E(n)}">解体・片付けの費用を、30秒で目安を出す <i>→</i></a>'
           f'<p class="itn">「買いたい」の3つは広告です（Yahoo!不動産のこの街の一覧が開きます）。</p></section>')
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
{beacon("街｜" + n, "街ページ")}</body></html>'''
    return head(title, desc, url, ld) + body


os.makedirs(os.path.join(ROOT, "links/machi"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "links/machi")):
    if f.endswith(".html"):
        os.remove(os.path.join(ROOT, "links/machi", f))
import collections
_DUP = collections.Counter(t['n'] for t in towns)
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
<a class="back" href="/moushikomi?lite=1&amp;want=%E6%9F%BB%E5%AE%9A%E3%81%97%E3%81%A6%E3%81%BB%E3%81%97%E3%81%84" data-k="地価ランキング｜いくらで売れるか聞く" style="display:block;background:#3A332E;color:#fff;border:0;border-radius:12px;padding:15px 16px;margin:18px 0 14px;text-align:center;text-decoration:none;font-weight:700;font-size:15px">お家がいくらで売れるか、無料で聞く</a><a class="back" href="/fudosan-list" data-k="関西不動産リストへ">関西不動産リストを見る</a>
<div class="ft">TOWN NOTE</div></div>
<script>(function(){{function go(k){{var b=document.querySelector('.flt button[data-p="'+k+'"]');if(!b)return;document.querySelectorAll(".flt button,.pane").forEach(function(x){{x.classList.remove("on")}});b.classList.add("on");document.getElementById(k).classList.add("on");}}
document.querySelectorAll(".flt button").forEach(function(b){{b.onclick=function(){{go(b.dataset.p);history.replaceState(null,"","#"+b.dataset.p);}}}});if(location.hash)go(location.hash.slice(1));}})();</script>
{beacon("地価ランキング関西")}</body></html>'''
open(os.path.join(ROOT, "links/chika-kansai.html"), "w", encoding="utf-8").write(rk)
print("ok", len(towns), "towns", "live" if live else "noindex", "rel:", sum(1 for t in towns if related(t)))

# ================= 実家・空き家ノート（11/9 オーナー「つくれ」：提案スレッドの見本 jikka-neyagawa をもとに）
# 相続した家・空き家の持ち主へ：この街で売れた値段・地価 → 迷ったときの順番（公式の出典つき）→ 売却・片付け・解体はオーナーにお申し込み（関西のみ・広告ではない）
J_SRC = [
    ("相続登記を確かめる", "2024年4月1日から、相続で家や土地を受け取ったと知った日から3年以内の相続登記が義務になりました。2024年3月より前の相続も対象で、期限は「2027年3月31日」か「受け取ったと知った日から3年」の、どちらか遅い方です。",
     "法務省「相続登記の申請義務化」", "https://www.moj.go.jp/MINJI/souzokutouki-gimuka/index.html"),
    ("家財を片付ける", "遠方の実家なら、片付け・遺品整理の見積りを先に取ると、売る時期を決めやすくなります。見積りは作業の中身と追加料金を確かめてから頼みましょう。",
     "国民生活センター「遺品整理を頼むときは、事業者選びは慎重に」", "https://www.kokusen.go.jp/mimamori/mj_mailmag/mj-shinsen525.html"),
    ("売るか、解体するか", "古い家は「そのまま売る」「更地にして売る」で値段も費用も変わります。手入れが足りず市から「管理不全空家」として勧告を受けると、土地の固定資産税の軽減（住宅用地特例）が外れます。",
     "国土交通省「空家等対策の推進に関する特別措置法の一部を改正する法律」概要", "https://www.mlit.go.jp/jutakukentiku/house/content/001621960.pdf"),
    ("税金の特例を確かめる", "相続した空き家（1981年5月31日以前に建てた家など）は、「相続から3年目の年の12月31日まで」かつ「2027年12月31日まで」に売ると、売ったもうけから最高3,000万円を差し引けます（相続人が3人以上なら1人2,000万円まで・条件あり）。くわしくは税務署・税理士へ。",
     "国税庁 タックスアンサー No.3306", "https://www.nta.go.jp/taxes/shiraberu/taxanswer/joto/3306.htm"),
]
# 11/10 市の補助（夜が公式ページで確かめた物・2026/11/10 時点）。受付は変わるので「確認日」と公式URLを必ず出す
# 市ごとの「解体の補助金」ページのローマ字（正本は tools/kaitai/city.py の CITY）
import ast as _ast_k, os as _os_k
_kc = open(_os_k.path.join(_os_k.path.dirname(_os_k.path.abspath(__file__)), "..", "kaitai", "city.py"), encoding="utf-8").read()
_ka = _kc.index("CITY = {"); K_SLUG = {k: v[0] for k, v in _ast_k.literal_eval(_kc[_ka + 7:_kc.index("\n}\n", _ka) + 2]).items()}
J_CITY = [
    ("寝屋川市", [("空き家の解体の補助", "解体費の4/5・上限50万円（1年以上空き家の木造住宅など・条件あり）。受付は2027年2月26日まで（予算がなくなりしだい終了）。", "受付中", "https://www.city.neyagawa.osaka.jp/kurashi/sumai_kenchiku/akiyacategory/13013.html"),
                  ("空き家・空き地バンク", "市の空き家バンクがあります。", "", "https://www.city.neyagawa.osaka.jp/kurashi/sumai_kenchiku/akiyabanku/15123.html")]),
    ("大東市", [("古く危ない空き家の解体の補助", "解体費などの4/5・戸建は上限80万円（木造・1年以上空き家などの条件あり）。事前調査は11月30日まで、申し込みは12月28日まで。交付が決まる前に契約・着工しないこと。", "受付中", "https://www.city.daito.lg.jp/site/iju/60868.html")]),
    ("堺市", [("木造住宅の解体の補助", "予算に達したため、受付が止まっています（市のページの更新は2026年11月9日）。", "受付停止", "https://www.city.sakai.lg.jp/kurashi/jutaku/kenchiku/anzen/taishinkaishu/26taisinkaisyuu.html"),
              ("耐震改修の補助（空き家も対象）", "一般の受付は2027年1月29日まで（予算がなくなりしだい終了）。", "受付中", "https://www.city.sakai.lg.jp/kurashi/jutaku/kenchiku/anzen/taishinkaishu/jyuutakuhojyo.html")]),
    ("大阪市", [("耐震性が足りない住宅の解体の補助", "費用の1/3・上限70万円/戸。受付は12月28日まで。", "受付中", "https://www.city.osaka.lg.jp/toshiseibi/page/0000370839.html")]),
    ("東大阪市", [("危険な空き家の解体の補助", "上限50万円/棟（所得などの条件で100万円）。交付が決まる前の着工は対象外。", "受付中", "https://www.city.higashiosaka.lg.jp/0000022525.html")]),
    # 11/11 月が市の公式の手引き・要綱で確かめた物
    ("神戸市", [("古い空き家の解体の補助", "建物の広さで決まる定額で、20万〜60万円（1986年以前に建った、傷みのある空き家など・条件あり）。受付は2027年1月12日まで（予算がなくなりしだい終了）。交付が決まる前の契約・着工は対象外。", "受付中", "https://www.city.kobe.lg.jp/documents/25370/r8_9rokyutebiki.pdf")]),
    ("奈良市", [("特定空家等の解体の補助", "費用の1/2・上限30万円。市が「特定空家等」と判断した建物だけが対象です。受付の期間は、市にお問い合わせください。", "", "https://www.city.nara.lg.jp/uploaded/attachment/192957.pdf")]),
    ("姫路市", [("老朽空家の解体の補助", "個人は工事費の1/3・上限50万円。令和8年度の受付は2026年6月11日に終わりました。来年度に向けた現地調査（対象かどうかの確認）は、いつでも受け付けています。", "受付終了", "https://www.city.himeji.lg.jp/kurashi/0000006739.html")]),
    ("尼崎市", [("特殊空家の解体の補助", "費用の2/3・上限50万円。借地の上の長屋か、道に接していない土地の空き家だけが対象です（世帯の所得900万円以下など）。受付は2026年12月28日まで（予算がなくなりしだい終了）。", "受付中", "https://www.city.amagasaki.hyogo.jp/kurashi/sumai/1021364/1024803.html")]),
    ("和歌山市", [("不良空家の解体の補助", "費用の2/3・上限50万円。先に市の「不良空家」の認定が要ります（1年以上だれも住んでいない等）。予定の件数に達すると締め切りです。", "", "https://www.city.wakayama.wakayama.jp/kurashi/sumai_jyougesuidou/1001110/1010373/1001893.html")]),
    ("豊中市", [("木造住宅の解体の補助（震災対策）", "上限40万円。1981年5月31日以前に建った、耐震性が足りない木造住宅（2階建てまで）が対象です（所得などの条件あり）。契約・着工の前に手続きが要ります。予算に達すると終了です。", "", "https://www.city.toyonaka.osaka.jp/machi/kenchiku_kaihatsu/taisin/jokyaku.html")]),
    ("高槻市", [("木造住宅の解体の補助", "一戸建ては定額40万円（1981年5月31日以前に建った家は45万円）。耐震性が足りない木造住宅が対象です（所得などの条件あり）。申請はその年度の1月末まで、契約・着工の前に。予算に達すると中止です。", "", "https://www.city.takatsuki.osaka.jp/soshiki/49/5868.html")]),
    ("枚方市", [("住宅の解体の補助", "上限20万円/棟。1981年5月31日以前に建った、耐震性が足りない住宅が対象です（世帯の所得256万8千円以下など）。事前相談は12月14日まで、申し込みは12月28日まで（先着順）。", "受付中", "https://www.city.hirakata.osaka.jp/0000002407.html")]),
    ("八尾市", [("木造住宅の解体の補助", "1棟につき40万円。1981年5月31日以前に建った木造住宅（2階建てまで）を、まるごと解体する時が対象です（所有者の所得・預貯金などの条件あり。空き家も条件つきで対象）。2026年4月9日から受付。", "", "https://www.city.yao.osaka.jp/kurashi_tetsuzuki/sumai_kurashi_seikatsu/1002438/1002502/1017006.html")]),
    ("加古川市", [("となりの空き家を買って解体する時の補助", "解体費の1/5・上限25万円。となりの狭い土地にある空き家を買い取り、自分の土地と一体で使う方が対象です（個人のみ・1年以上空き家などの条件あり）。受付は2026年12月25日まで（予算に達した時点で終了）。", "", "https://www.city.kakogawa.lg.jp/soshikikarasagasu/tosi_kekaku/jyutaku/akiya_akichi/1562032385484.html")]),
    ("宇治市", [("老朽空き家の解体の補助", "基準額の1/3・上限30万円（1981年5月31日以前に着工した部分があり、おおむね1年使われていない空き家）。令和8年度は予算に達したため、受付が終わっています（市のページの更新は2026年9月14日）。", "受付終了", "https://www.city.uji.kyoto.jp/soshiki/48/88936.html")]),
    ("橿原市", [("空家の解体の補助", "解体費の4/5以内・上限50万円。先に市の「不良住宅空家」の認定が要ります（1年以上使われていない等）。予算の上限に達すると終了です。", "", "https://www.city.kashihara.nara.jp/soshiki/1009/gyomu/3/1/16182.html")]),
    ("和泉市", [("木造住宅の解体の補助", "解体工事費の80％・最大20万円（原則1棟あたり）。1981年5月31日以前に工事を始めた木造の一戸建て・長屋で、耐震診断で耐震性が足りないと出た建物が対象です（所得が507万円未満などの条件あり。門・塀・庭木の解体は対象外）。申し込みの前に、市へ事前協議書を出します。2026年4月6日から先着順で受付、予算の範囲までです。", "", "https://www.city.osaka-izumi.lg.jp/kakukano/dezainbu/kentikukaihatu/osirase/12470.html")]),
    ("茨木市", [("木造住宅の解体の補助", "解体工事に定額で、課税所得が507万円未満の方は40万円、世帯の月額所得が21万4千円以下の方は60万円（費用がそれより少ない時は費用の額まで）。1981年5月31日以前に建築確認を受けた木造住宅で、耐震診断の評点が0.7未満などの建物を、まるごと取り壊す工事が対象です（法人の持ち物は対象外）。申請は2027年1月29日まで。2026年11月1日の時点で、残りは1戸でした。先に市へご相談ください。", "受付中", "https://www.city.ibaraki.osaka.jp/kurashi_tetsuzuki/sumai_koen/taishin/54298.html")]),
    ("岸和田市", [("木造住宅の解体の補助", "対象の費用の7割・上限40万円（1981年5月31日以前に建った木造の一戸建て・長屋などで、耐震性が足りない建物）。令和8年度は件数の上限に達したため、受付が終わっています（市のページの掲載は2026年9月28日）。", "受付終了", "https://www.city.kishiwada.lg.jp/page/mokuzoujuutaku-jokyaku.html")]),
    ("松原市", [("住宅の解体の補助", "解体工事の費用・一戸建ては1戸あたり上限40万円（1981年5月31日以前に建った住宅や空き家で、耐震性が足りない物）。長屋・共同住宅は別の上限があります。申請の受付は4月1日〜12月末日、予算に達すると受付できません。", "受付中", "https://www.city.matsubara.lg.jp/docs/1342552.html")]),
    ("伊丹市", [("住宅の解体の補助", "安全性の低い住宅を取り壊す工事に、最大60万円（1981年5月31日以前に工事を始めた住宅で、耐震診断の結果、安全性が低いと出た物）。交付が決まる前の契約は対象外です。令和8年度の二期の受付は9月1日〜12月11日、予定数に達すると終わることがあります。", "受付中", "https://www.city.itami.lg.jp/SOSIKI/TOSHIKATSURYOKU/KENTIKUSIDO/JUTAKU_TAISINKA/1569552891805.html")]),
    ("泉佐野市", [("不良住宅の解体の補助", "市が現場を見て「不良住宅」と判定した住宅の解体に、上限80万円。1年以上使われていない場合は上限130万円。貸していない物で、持ち主の所得の条件があります。交付の決定の前に始めた工事は対象外。予算がいっぱいになり次第、受付は終わります。", "", "https://www.city.izumisano.lg.jp/kakuka/toshi/toshi/menu/akiya_taisaku/1522316627916.html"),
                ("空き家の解体の補助", "1年以上使われていない空き家（水道の証明で確かめます）の解体に、1戸あたり上限65万円。上の不良住宅の補助などの対象にならない空き家が対象で、個人の持ち主が申請します。交付の決定の前に始めた工事は対象外。予算がいっぱいになり次第、受付は終わります。", "", "https://www.city.izumisano.lg.jp/kakuka/toshi/toshi/menu/akiya_taisaku/1584955369159.html")]),
    ("羽曳野市", [("木造住宅の解体の補助", "一戸建ては解体工事の費用の2分の1・上限20万円、長屋・共同住宅は1戸あたり20万円で上限100万円（1981年5月31日以前に建った木造住宅で、耐震診断などで弱いと出た物）。先に市へ相談し、契約は交付の決定のあとで。持ち主の所得の条件があります。受付は原則5月上旬〜翌年1月末、予算に達すると終わります。", "", "https://www.city.habikino.lg.jp/soshiki/toshikaihatu/kenjyuka/taishin/jokyaku.html")]),
    ("河内長野市", [("木造住宅の解体の補助", "解体工事の費用の2分の1か、面積から出す基準額の低い方・上限25万円（1981年5月31日以前に建った木造の住宅で、1年以上空き家、耐震診断で倒れる可能性があると出た物）。交付の決定の前に解体の契約をすると出ません。所得の条件があります。令和8年度の申請は12月15日まで、予算に達すると早く終わることがあります。", "受付中", "https://www.city.kawachinagano.lg.jp/soshiki/2/4115.html")]),
    ("草津市", [("不良空き家の解体の補助", "解体工事の費用の5分の4・上限50万円（1年以上使われていない個人の空き家で、市の事前調査で老朽の点数が100点以上の物）。交付が決まる前に始めた工事は対象外で、取り壊した後は更地にします。令和8年度分の受付は終わりました。来年度に向けて、市の事前調査から相談できます。", "受付終了", "https://www.city.kusatsu.shiga.jp/kurashi/sumai/akiya/kenchiku22024.html"),
                ("危険な木造の建物の解体の補助", "幅4m未満の道に面した、1981年5月31日以前に工事を始めた木造の建物で、地震の時に倒れて道をふさぐおそれのある物の解体費用の一部。金額は市のパンフレットで確かめてください。令和8年度分を受け付けています。", "受付中", "https://www.city.kusatsu.shiga.jp/kurashi/sumai/sumai/sumaianzen/kenchiku_taishin.html")]),
    ("生駒市", [("古い住宅の解体の補助", "一戸建ては解体費用の23%・上限50万円、長屋・共同住宅は上限100万円（2000年以前に建った住宅で、耐震診断で倒れるおそれがあると出た物）。解体の契約・工事の前に申請が要ります。令和8年度は約30件で、予算に達して受付を休んでいます（再開の予定は市のページで確かめてください）。", "受付停止", "https://www.city.ikoma.lg.jp/0000009876.html")]),
    ("富田林市", [("木造住宅の解体の補助", "解体工事の費用・1戸あたり上限30万円（1981年5月31日以前に建った木造住宅を、個人の持ち主が取り壊す時）。申請は1月末まで、予算がなくなりしだい終了です。", "", "https://www.city.tondabayashi.lg.jp/soshiki/32/44454.html"),
                  ("老朽危険空家の解体の補助", "解体の実費と国の基準額の低い方の3分の1。市の判定で100点以上の「老朽危険空家」は1戸あたり上限100万円、30点以上100点未満は上限30万円（木造の空き家だけ）。予算がなくなりしだい終了です。", "", "https://www.city.tondabayashi.lg.jp/soshiki/32/1125.html")]),
]

J_DATE = {c: "2026年11月11日" for c in ("神戸市", "奈良市", "姫路市", "尼崎市", "和歌山市", "豊中市", "高槻市", "枚方市", "八尾市", "加古川市", "宇治市", "橿原市")} | {c: "2026年11月12日" for c in ("和泉市", "茨木市", "岸和田市", "富田林市", "松原市", "伊丹市", "草津市", "生駒市", "河内長野市", "泉佐野市", "羽曳野市")}  # 書いていない市は 2026年11月10日


def city_of_town(n):
    for c, rows in J_CITY:
        if n == c or n.startswith(c):
            return c, rows
    return None, None


J_CSS = """.jn{display:grid;grid-template-columns:1fr 1fr;gap:10px}.jn>div{background:#F4F4F6;border-radius:12px;padding:12px 14px}
.jn b{display:block;font-family:Jost,"Zen Kaku Gothic New";font-weight:400;font-size:24px;color:#2B2622;line-height:1.3}.jn b small{font-size:12px}.jn span{display:block;font-size:11.5px;color:#7A6E66;margin-top:2px;line-height:1.6}.jn .no{font-size:12px;color:#7A6E66;line-height:1.7}
.src{font-size:11px;color:#8C7B6E;line-height:1.7;margin:8px 0 0}.src a{color:#8C7B6E}
.mk3{font-family:Jost,sans-serif;font-size:10.5px;letter-spacing:.3em;color:#9C8775;margin:30px 0 0}.jh{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.1em;margin:4px 0 12px;padding:0;border:0}
.st{display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-top:1px solid #ECECEC}.st:last-of-type{border-bottom:1px solid #ECECEC}.st i{font-style:normal;font-family:Jost,sans-serif;font-weight:300;font-size:20px;color:var(--pc);width:26px;flex:none;line-height:1.3}
.st b{display:block;font-size:14.5px}.st p{margin:3px 0 0;font-size:13px;line-height:1.8;color:#4E453F}.st a{display:inline-block;font-size:11px;color:#8C7B6E;margin-top:4px}
.jb{display:block;text-align:center;border-radius:12px;padding:14px 12px;font-size:14.5px;font-weight:700;margin-top:10px;text-decoration:none;color:#2B2622;border:1px solid #2B2622;background:#fff}.jb small{display:block;font-size:11px;font-weight:500;color:#857A70;margin-top:2px}
.jb.b1{background:#2B2622;color:#fff;border-color:#2B2622}.jb.b1 small{color:#D9D2CC}.jp{font-size:11.5px;color:#8C7B6E;text-align:center;margin:8px 0 0;line-height:1.7}
.cy{border-top:1px solid #ECECEC;padding:12px 0}.cy b{font-size:14px}.cy em{font-style:normal;font-size:11px;font-weight:700;margin-left:6px;padding:1px 8px;border-radius:10px;background:#EEF3EC;color:#3F6B3A}.cy em.x{background:#F6EDEA;color:#9A4A33}.cy p{margin:4px 0 0;font-size:13px;line-height:1.8;color:#4E453F}.cy a{font-size:11px;color:#8C7B6E}
.jl{display:flex;justify-content:space-between;margin:14px 0 0;padding:12px 4px;border-top:1px solid #E6E6E6;border-bottom:1px solid #E6E6E6;text-decoration:none;color:#5E544D;font-size:13px}.jl i{font-style:normal;font-family:Jost;color:#9C8775}"""


def has_sold(t):
    sd = sold_of(t)
    return any(sd.get(k) for k in ("k", "m"))


def jikka_page(t):
    pf, fn, en, col, sname, surl, pfull = PI[t["p"]]
    n = t["n"]
    sd = sold_of(t)

    def box(k, lb):
        r = sd.get(k)
        if not r or not r["価格万円"]:
            return f'<div><span>{lb}</span><p class="no">' + (f'2025年度に売れたのは{r["件数"]}件だけのため、平均は出ていません。' if r else '2025年度は、売れた記録がありません。') + '</p></div>'
        few = "・少ないので目安" if int(r["件数"]) < 10 else ""
        return f'<div><b>{int(round(float(r["価格万円"]))):,}<small>万円</small></b><span>{lb}の平均（{int(r["件数"]):,}件{few}）</span></div>'
    sl = [f"{lb}{man(sd[k]['価格万円'])}" for k, lb in (("k", "中古一戸建て"), ("m", "中古マンション")) if sd.get(k) and sd[k]["価格万円"] and int(sd[k]["件数"]) >= 10]
    title = f"{n}{f'（{pfull}）' if _DUP.get(n, 0) > 1 else ''}の実家・空き家｜売る・片付け・解体の前に（売れた相場と順番）"  # 11/11 同じ名前の街（太子町）は府県を付けて題名を分ける
    desc = (f"{pfull}{n}で親の家を相続した・空き家のままの方へ。" + (f"2025年度に売れた平均は{'・'.join(sl)}（レインズ）。" if sl else "")
            + "相続登記の義務、片付け、売るか解体するか、3,000万円の特別控除まで、公式の出典つきで順番に。")
    url = f"{BASE}/jikka/{t['id']}"
    ld = {"@context": "https://schema.org", "@graph": [{"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "TOWN NOTE", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": "実家・空き家ノート", "item": f"{BASE}/jikka/"},
        {"@type": "ListItem", "position": 3, "name": f"{n}の実家・空き家", "item": url}]}]}
    steps = "".join(f'<div class="st"><i>{i:02d}</i><div><b>{E(h)}</b><p>{E(p)}</p><a href="{E(u)}" target="_blank" rel="noopener" data-k="実家｜出典｜{i:02d}">出典：{E(s)}</a></div></div>'
                    for i, (h, p, s, u) in enumerate(J_SRC, 1))
    cn, crows = city_of_town(n)
    city_h = ""
    if crows:
        city_h = (f'<p class="mk3">CITY</p><h2 class="jh">{E(cn)}の補助・空き家バンク</h2>' + "".join(
            f'<div class="cy"><b>{E(h)}</b>' + (f'<em class="{"x" if st in ("受付停止", "受付終了") else ""}">{st}</em>' if st else '') + f'<p>{E(tx)}</p><a href="{E(u)}" target="_blank" rel="noopener" data-k="実家｜市の補助｜{E(cn)}">{E(cn)}の公式ページ →</a></div>' for h, tx, st, u in crows)
            + f'<p class="src">{J_DATE.get(cn, "2026年11月10日")}に市の公式ページで確かめた内容です。受付・条件・上限は変わるので、申し込む前に必ず公式ページで確かめてください。</p>')
        if cn in K_SLUG and any("解体" in h for h, *_ in crows):  # 11/11 市ごとの「解体の補助金」ページ（tools/kaitai/city.py）へ
            city_h += f'<a class="jb2" href="/kaitai-{K_SLUG[cn]}" data-k="実家｜市の解体補助ページ｜{E(cn)}" style="display:block;margin:10px 0 0;font-size:13.5px;font-weight:700;color:inherit">{E(cn)}の解体の補助を、自分で払う目安つきで見る →</a>'
    body = f'''<style>{HEAD_CSS}{J_CSS}</style>{SCRIPTS}</head><body style="--pc:{col}"><div class="wrap">
<div class="head"><img src="/assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ"><div class="en">{en} ─ JIKKA NOTE</div>
<h1>{E(n)}の実家・空き家ノート<span>売る・片付ける・解体する前に</span></h1>
<p class="sub">親の家を相続した・空き家のままになっている。<br>この街で決めるための数字と順番です。</p>
<div class="upd">2026年11月 更新</div></div>
<p class="mk3">SOLD 2025年度</p><h2 class="jh">この街で、2025年度（2025年4月〜2026年3月）に売れた家</h2>
<div class="jn">{box("k", "中古一戸建て")}{box("m", "中古マンション")}</div>
<p class="src">出典：近畿レインズ 2025年度（2025年4月〜2026年3月）市区町村別の成約（平均）。住宅地の地価は前の年から{pct(t["r8"])}（令和8年地価公示・{E(pfull)}{t["of"]}市区町村で{t["rank"]}位）。</p>
<a href="/jikka/shindan/?machi={t["id"]}" data-k="実家｜3問診断へ" style="display:block;margin:22px 0 0;padding:14px 16px;border:1.5px solid #2F7D5B;border-radius:14px;text-decoration:none;color:#231E1B;font-weight:700;font-size:15px;text-align:left">うちの場合は？ 3問でわかる診断へ →<small style="display:block;font-weight:500;font-size:12px;color:#6B6058;margin-top:2px">約30秒・無料・お名前は要りません</small></a>
<p class="mk3" id="steps">STEPS</p><h2 class="jh">迷ったら、この順で</h2>
{steps}
{city_h}<p class="mk3">NEXT</p><h2 class="jh">次にできること</h2>
<a class="jb b1" href="/moushikomi?machi={t["id"]}&amp;want={_q("相続した家のこと")}" data-k="実家｜売却の相談｜{E(n)}">この家の売却を相談する<small>無料・約1分</small></a>
<a class="jb" href="/moushikomi?lite=1&amp;machi={t["id"]}&amp;want={_q("片付け・遺品整理の見積り")}" data-k="実家｜片付けの見積り｜{E(n)}">片付け・遺品整理の見積りを頼む<small>無料・約1分</small></a>
<a class="jb" href="/moushikomi?lite=1&amp;machi={t["id"]}&amp;want={_q("解体の見積り")}" data-k="実家｜解体の見積り｜{E(n)}">解体費用の見積りを頼む<small>無料・約1分</small></a>
<p class="jp">どれも同じお申し込みページです。内容を見て、メールでご連絡します。</p>
<a class="jl" href="/kaitai" data-k="実家｜費用の目安">先に、解体・片付けの費用の目安を見る <i>→</i></a>
<a class="jl" href="/jikka/#{fn}" data-k="実家｜一覧">ほかの街の実家・空き家ノート <i>→</i></a>
<div class="ft">TOWN NOTE</div></div>
{beacon("実家｜" + n, "実家ノート")}</body></html>'''
    return head(title, desc, url, ld) + body


JT = [t for t in towns if has_sold(t)]
os.makedirs(os.path.join(ROOT, "links/jikka"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "links/jikka")):
    if f.endswith(".html"):
        os.remove(os.path.join(ROOT, "links/jikka", f))  # index.html（一覧）も作り直す
for t in JT:
    open(os.path.join(ROOT, "links/jikka", t["id"] + ".html"), "w", encoding="utf-8").write(jikka_page(t))

# 一覧（府県のタブ）
JL_CSS = """.flt{display:flex;flex-wrap:nowrap;justify-content:center;gap:0 13px;margin:24px 0 8px;padding:10px 0;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4;overflow-x:auto}
.flt button{flex:none;border:none;background:none;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:14px;font-weight:700;letter-spacing:.04em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer;opacity:.85}
.flt button.on{opacity:1;border-bottom-color:currentColor}.pane{display:none}.pane.on{display:block}
.jli{list-style:none;margin:0;padding:0}.jli li{border-bottom:1px solid #ECECEC}.jli a{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:12px 2px;text-decoration:none;color:#2B2622;font-weight:700;font-size:14px}
.jli a small{font-size:11.5px;color:#7A6E66;font-weight:500;text-align:right}"""


def jl_li(t):
    sd = sold_of(t)
    r = sd.get("k")
    s = f'一戸建て {int(round(float(r["価格万円"]))):,}万円' if r and r["価格万円"] else ""
    return f'<li><a href="/jikka/{t["id"]}" data-k="実家一覧｜{E(t["n"])}">{E(t["n"])}<small>{s}</small></a></li>'


jpanes = [(fn, pf, [t for t in JT if t["p"] == pf]) for pf, fn, *_ in PREFS]
jdesc = (f"関西6府県・{len(JT)}の市区町村ごとに、相続した実家・空き家を「売る・片付ける・解体する」前に見る数字と順番。"
         "2025年度に売れた家の平均（レインズ）、相続登記の義務、3,000万円の特別控除を公式の出典つきで。")
jl = head(f"関西の実家・空き家ノート｜{len(JT)}の街の売れた相場と、売る・片付け・解体の順番", jdesc, f"{BASE}/jikka/") + f'''<style>{HEAD_CSS}{JL_CSS}</style>{SCRIPTS}</head><body><div class="wrap">
<div class="head"><img src="/assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ"><div class="en">KANSAI ─ JIKKA NOTE</div>
<h1>実家・空き家ノート<span>関西 {len(JT)}の街</span></h1>
<p class="sub">親の家を相続した・空き家のままの方へ。<br>街を選ぶと、売れた相場と順番が見られます。</p>
<div class="upd">2026年11月 更新</div></div>
<style>.jq{{margin:24px 0 6px;padding:14px 16px 16px;background:#F5F4F2;border:1px solid #ECEAE6;border-radius:16px;text-align:center}}.jq b{{display:block;font-size:13px;letter-spacing:.08em;color:#2B2622;margin-bottom:10px}}.jq input{{width:100%;box-sizing:border-box;font:500 16px "Zen Kaku Gothic New",sans-serif;padding:12px 16px;border:1.5px solid #CFC6BC;border-radius:12px;background:#fff;color:#2B2622;-webkit-appearance:none;appearance:none}}.jq input:focus{{outline:none;border-color:#8C7B6E}}#jres{{display:none}}#jres.on{{display:block}}#jres p{{font-size:13px;color:#7A6E66;margin:14px 2px}}html.jq-on .flt,html.jq-on .pane{{display:none!important}}</style><a href="/jikka/shindan/" data-k="実家｜一覧｜3問診断へ" style="display:block;margin:22px 0 0;padding:14px 16px;border:1.5px solid #2F7D5B;border-radius:14px;text-decoration:none;color:#231E1B;font-weight:700;font-size:15px;text-align:left">何から始める？ 3問でわかる診断へ →<small style="display:block;font-weight:500;font-size:12px;color:#6B6058;margin-top:2px">約30秒・無料・お名前は要りません</small></a><div class="jq"><b>街の名前で探す</b><input id="jqi" type="search" placeholder="例：吹田市・西宮市・草津市" enterkeyhint="search" autocomplete="off"></div><div id="jres"></div><nav class="flt">''' + "".join(f'<button data-p="{k}" style="--pc:{PI[pf][3]}"{" class=\"on\"" if i == 0 else ""}>{pf}</button>' for i, (k, pf, _) in enumerate(jpanes)) + '</nav>' + \
    "".join(f'<section class="pane{" on" if i == 0 else ""}" id="{k}"><ul class="jli">{"".join(jl_li(t) for t in ts)}</ul></section>' for i, (k, pf, ts) in enumerate(jpanes)) + f'''
<p class="note">金額は近畿レインズ「2025年度 年刊市況レポート」の中古一戸建ての成約の平均です。1軒ずつの値段ではありません。</p>
<div class="ft">TOWN NOTE</div></div>
<script>(function(){{function go(k){{var b=document.querySelector('.flt button[data-p="'+k+'"]');if(!b)return;document.querySelectorAll(".flt button,.pane").forEach(function(x){{x.classList.remove("on")}});b.classList.add("on");document.getElementById(k).classList.add("on");}}
document.querySelectorAll(".flt button").forEach(function(b){{b.onclick=function(){{go(b.dataset.p);history.replaceState(null,"","#"+b.dataset.p);}}}});if(location.hash)go(location.hash.slice(1));}})();</script>
<script>(function(){{var i=document.getElementById("jqi"),r=document.getElementById("jres"),all=[].slice.call(document.querySelectorAll(".pane .jli li")),tq;function n(s){{return s.replace(/\\s/g,"").replace(/[市区町村]$/,"")}}i.oninput=function(){{var q=n(i.value);r.innerHTML="";document.documentElement.classList.toggle("jq-on",!!q);r.classList.toggle("on",!!q);if(!q)return;var u=document.createElement("ul");u.className="jli";all.forEach(function(li){{if(li.querySelector("a").firstChild.textContent.replace(/\\s/g,"").indexOf(q)>=0)u.appendChild(li.cloneNode(true))}});if(u.children.length)r.appendChild(u);else r.innerHTML="<p>「"+i.value.trim()+"」は見つかりませんでした。府県から選んでください。</p>";clearTimeout(tq);tq=setTimeout(function(){{try{{var b=JSON.stringify({{k:"実家一覧｜検索："+i.value.trim()}});navigator.sendBeacon&&navigator.sendBeacon("/c",b)}}catch(e){{}}}},1500);}};}})();</script>
{beacon("実家一覧", "実家ノート")}</body></html>'''
open(os.path.join(ROOT, "links/jikka/index.html"), "w", encoding="utf-8").write(jl)
print("jikka", len(JT), "towns")
