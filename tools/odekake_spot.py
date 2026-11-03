"""おでかけ1件ごとのページ（/o/xxxxxxxx）を links/index.html のカードから作る。
11/4 オーナー「色んな記事ある中で検索なんでも引っかかって欲しい」→ 「〇〇 イルミ 2026 日程」のように
1つの名前で調べた人にも届くよう、1件1ページにする。中身はリストに書いてある事実だけ（日程・場所・無料・公式リンク・前売り券・近くの宿）。
毎朝 link-stats.yml で odekake_pref.py のあとに作り直す（終わった物のページは消す）。
python3 tools/odekake_spot.py [YYYY-MM-DD]"""
import re, json, html, sys, datetime, hashlib, os, glob
TODAY = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
BASE = "https://townnote.pages.dev"
FU = {"大阪": "大阪府", "京都": "京都府", "兵庫": "兵庫県", "奈良": "奈良県", "滋賀": "滋賀県", "和歌山": "和歌山県"}
SLUG = {"大阪": "osaka", "京都": "kyoto", "兵庫": "hyogo", "奈良": "nara", "滋賀": "shiga", "和歌山": "wakayama"}
PC = {"大阪": "#B97A62", "京都": "#8E7CA8", "兵庫": "#5E8CA8", "奈良": "#7E9A6A", "滋賀": "#5A9A9A", "和歌山": "#C29A4E"}
W = "月火水木金土日"
s = open("links/index.html", encoding="utf-8").read()
# 府県の色はおでかけリストと同じ物を使う（あれば）
for p in FU:
    m = re.search(r'\[data-pref="' + p + r'"\][^{]*\{[^}]*--pc:\s*(#[0-9A-Fa-f]{6})', s)
    if m: PC[p] = m.group(1)
yado = json.load(open("links/kansai-yado.json", encoding="utf-8")) if os.path.exists("links/kansai-yado.json") else {}
yado = {re.sub(r"\s+", "", k): v for k, v in yado.items()}
yjs = open("links/assets/yado.js", encoding="utf-8").read()
m = re.search(r"var T=(\{.*?\]\]\});", yjs, re.S)
TK = json.loads(m.group(1)) if m else {}
# 街のページ（地価）: 市区町村の名前 → /machi/xxx
MACHI = {}
for f in glob.glob("links/machi/*.html"):
    t = re.search(r"<title>(.*?)の地価", open(f, encoding="utf-8").read())
    if t: MACHI[t.group(1)] = "/machi/" + os.path.basename(f)[:-5]


def txt(x): return html.unescape(re.sub("<[^>]+>", "", x)).strip()
def jd(d):
    d = datetime.date.fromisoformat(d); return f"{d.month}月{d.day}日（{W[d.weekday()]}）"
def e(x): return html.escape(x, quote=True)


spots, seen = [], set()
for m in re.finditer(r'<a class="card"([^>]*)>(.*?)</a>', s, re.S):
    a = {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+|href)="([^"]*)"', m.group(1))}
    b = m.group(2)
    t = re.search(r'class="t">(.*?)</div>', b, re.S)
    if not t: continue
    name = txt(t.group(1)); key = re.sub(r"\s+", "", name)
    st, en = a.get("data-s", ""), a.get("data-e", "")
    if re.fullmatch(r"\d{4}-\d\d-\d\d", en) and en < TODAY: continue
    if key in seen or a.get("data-pref") not in FU: continue
    seen.add(key)
    mm = re.search(r'class="m">(.*?)</div>', b, re.S); dd = re.search(r'class="d">(.*?)</div>', b, re.S)
    parts = txt(mm.group(1)).split("｜") if mm else [""]
    spots.append(dict(name=name, key=key, pref=a["data-pref"], st=st, en=en, url=a.get("href", ""), free="無料" in a.get("data-tag", ""),
                      city=(lambda c, r: r if len(r) > 1 else c)(parts[0].strip(), re.sub(r"^(大阪府|京都府|兵庫県|奈良県|滋賀県|和歌山県)", "", parts[0].strip())), place=parts[-1].strip() if len(parts) > 1 else "", dline=txt(dd.group(1)) if dd else "",
                      map=a.get("data-map", ""), id=hashlib.md5(key.encode()).hexdigest()[:8]))

d0 = datetime.date.fromisoformat(TODAY); upd = f"{d0.year}年{d0.month}月{d0.day}日"
CSS = open(glob.glob("links/machi/*.html")[0], encoding="utf-8").read()
CSS = re.search(r"<style>(.*?)</style>", CSS, re.S).group(1)
CSS += """.act{display:grid;gap:8px;margin:22px 0 0}.act a{display:block;text-align:center;text-decoration:none;padding:13px;font-size:14px;font-weight:700;border-radius:12px}
.act .o{background:#3A2F28;color:#fff}.act .g{border:1px solid #D5D8DD;color:#2B2622;background:#fff}
.lead{font-size:14px;line-height:2;color:#3A3330;margin:22px 0 0}
.yl{list-style:none;margin:0;padding:0}.yl li{border-bottom:1px solid #ECECEC}.yl a{display:flex;justify-content:space-between;gap:10px;padding:12px 2px;text-decoration:none;color:#2B2622;font-size:13.5px;font-weight:700}
.yl a span{font-size:11.5px;color:#8C7B6E;font-weight:500;white-space:nowrap}.pr{font-size:11px;color:#8C7B6E;margin:6px 0 0}.wrap{padding-bottom:120px}"""

os.makedirs("links/o", exist_ok=True)
for f in glob.glob("links/o/*.html"): os.remove(f)
for sp in spots:
    p = sp["pref"]; fu = FU[p]; pc = PC[p]; nm = sp["name"]; yr = (sp["st"] or TODAY)[:4]
    when, stat = "", ""
    if re.fullmatch(r"\d{4}-\d\d-\d\d", sp["st"]):
        when = jd(sp["st"]) + ("〜" + jd(sp["en"]) if re.fullmatch(r"\d{4}-\d\d-\d\d", sp["en"]) and sp["en"] != sp["st"] else "")
        if sp["st"] > TODAY: stat = f"あと{(datetime.date.fromisoformat(sp['st']) - d0).days}日ではじまります"
        elif re.fullmatch(r"\d{4}-\d\d-\d\d", sp["en"]):
            left = (datetime.date.fromisoformat(sp["en"]) - d0).days
            stat = "きょうまで" if left == 0 else f"開催中・あと{left}日"
        else: stat = "開催中"
    when = when or sp["dline"] or "公式ページで"
    where = (sp["city"] + ("の" + sp["place"] if sp["place"] and sp["place"] != sp["city"] else "")) or fu
    lead = f"{nm}は、{'' if where.startswith(fu) else fu}{where}で" + (f"、{jd(sp['st'])}から{jd(sp['en'])}まで開かれます。" if sp["st"] and sp["en"] and sp["en"] != sp["st"] else (f"、{jd(sp['st'])}に開かれます。" if sp["st"] else "楽しめます。"))
    if sp["free"]: lead += "入場は無料です。"
    title = f"{nm if yr in nm else nm + " " + yr}｜日程・場所・{'入場無料' if sp['free'] else 'アクセス'}（{sp['city'] if sp['city'].startswith(fu) else fu + sp['city']}）｜TOWN NOTE"
    desc = f"{nm}（{fu}{where}）の{yr}年の日程は{when}。{'入場無料。' if sp['free'] else ''}公式ページ、地図、近くの宿をまとめました。{upd}確認。"
    canon = f"{BASE}/o/{sp['id']}"
    ev = {"@type": "Event", "name": nm, "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled",
          "location": {"@type": "Place", "name": sp["place"] or sp["city"], "address": fu + sp["city"]}, "url": sp["url"]}
    if sp["st"]: ev["startDate"] = sp["st"]
    if re.fullmatch(r"\d{4}-\d\d-\d\d", sp["en"]): ev["endDate"] = sp["en"]
    if sp["free"]: ev["isAccessibleForFree"] = True
    bc = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "関西おでかけリスト", "item": BASE + "/odekake"},
        {"@type": "ListItem", "position": 2, "name": f"{p}おでかけリスト", "item": f"{BASE}/odekake-{SLUG[p]}"},
        {"@type": "ListItem", "position": 3, "name": nm, "item": canon}]}
    ld = json.dumps({"@context": "https://schema.org", "@graph": [ev, bc]}, ensure_ascii=False).replace("</", "<\\/")
    big = f'<div class="w"><span>日程</span><b>{e(when)}</b></div>'
    big += f'<div><span>いまは</span><b style="color:{pc};font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700">{e(stat or "公式ページで")}</b></div>'
    big += f'<div><span>入場</span><b style="color:#2B2622;font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700">{"無料" if sp["free"] else "公式ページで"}</b></div>'
    big += f'<div class="w"><span>場所</span><b>{e(where if where.startswith(fu) else fu + where)}</b></div>'
    q = sp["map"] or (sp["place"] + " " + sp["city"])
    act = f'<a class="o" href="{e(sp["url"])}" target="_blank" rel="noopener">公式ページで最新の情報を見る</a>'
    act += f'<a class="g" href="https://www.google.com/maps/search/?api=1&amp;query={e(q)}" target="_blank" rel="noopener">地図で場所を見る</a>'
    ads = False
    for x in TK.get(nm, []):
        act += f'<a class="g" href="{e(x[1])}" target="_blank" rel="noopener sponsored">{e(x[0])}を見る</a>'; ads = True
    yh = ""
    if yado.get(sp["key"]):
        ads = True
        li = "".join(f'<li><a href="{e(h["u"])}" target="_blank" rel="noopener sponsored">{e(h["n"])}<span>{"すぐそば" if h["km"] < 0.1 else str(h["km"]) + "km"}{"・★" + str(h["r"]) if h.get("r") else ""}{"・" + format(int(h["min"]), ",") + "円〜" if h.get("min") else ""}</span></a></li>' for h in yado[sp["key"]][:3])
        yh = f'<h2>近くの宿</h2><p class="cap">楽天トラベルの評価3.5以上を、ここからの近さで選びました（PR）</p><ul class="yl">{li}</ul>'
    near = [o for o in spots if o is not sp and o["pref"] == p and o["city"] == sp["city"]][:4]
    near += [o for o in spots if o is not sp and o["pref"] == p and o not in near][:6 - len(near)]
    nh = "".join(f'<a class="fc" href="/o/{o["id"]}"><small>{e(o["city"])}{"｜" + e(o["place"]) if o["place"] else ""}</small><b>{e(o["name"])}</b><span>{e(jd(o["st"]) + ("〜" + jd(o["en"]) if o["en"] and o["en"] != o["st"] else "") if o["st"] else o["dline"])}</span></a>' for o in near)
    mh = f'<a class="fc" href="{MACHI[sp["city"]]}"><small>街のこと</small><b>{e(sp["city"])}の地価 2026</b><span>国の地価公示の数字で、住宅地の1年の動きを見ます。</span></a>' if sp["city"] in MACHI else ""
    page = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:url" content="{canon}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{BASE}/assets/ogp.png"><meta name="twitter:card" content="summary"><link rel="icon" href="/assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script><style>{CSS}</style>
<script src="/assets/night.js?v=18"></script><script src="/assets/menu.js?v=14" defer></script><script src="/assets/v2sub.js?v=9" defer></script></head>
<body style="--pc:{pc}"><div class="wrap"><div class="head"><img src="/assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ">
<div class="en">{SLUG[p].upper()} ─ ODEKAKE</div><h1>{e(nm)}<span>{yr} 日程・場所</span></h1><p class="sub">{e(where if where.startswith(fu) else fu + where)}</p><div class="upd">{upd} 確認</div></div>
<div class="big">{big}</div><p class="lead">{e(lead)}</p><div class="act">{act}</div>{yh}
<h2>{e(p)}のほかのおでかけ</h2>{nh}{mh}
<a class="back" href="/odekake-{SLUG[p]}">{e(p)}おでかけリストへ</a><a class="back" href="/odekake" style="margin-top:14px">関西おでかけリストへ</a>
<div class="note">日程や料金は変わることがあります。出かける前に、必ず公式ページで確かめてください。{"<br>「前売り券」「近くの宿」のリンクは広告です。" if ads else ""}</div>
<div class="ft">TOWN NOTE ─ 関西おでかけリスト</div></div></body></html>
"""
    open(f"links/o/{sp['id']}.html", "w", encoding="utf-8").write(page)

# サイトの地図：/o/ を全部入れかえる
sm = open("links/sitemap.xml", encoding="utf-8").read()
sm = re.sub(r"<url><loc>https://townnote\.pages\.dev/o/[^<]*</loc>.*?</url>\n?", "", sm)
add = "".join(f"<url><loc>{BASE}/o/{sp['id']}</loc><lastmod>{TODAY}</lastmod></url>\n" for sp in spots)
sm = sm.replace("</urlset>", add + "</urlset>")
open("links/sitemap.xml", "w", encoding="utf-8").write(sm)
print(len(spots), "spot pages")
