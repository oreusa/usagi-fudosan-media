"""11/18 新しい関西おでかけ（/new/）を作る。owner「全部任せる・本気で作って」「UI/UX はめちゃくちゃ凄くないとやる必要ない」
「アーチファクトは見本にならない・ちゃんと見本作って」→ 本物のHPの中に、押して確かめられる形で作る（検索には出さない noindex）。
元：links/index.html のカード（毎朝の更新と同じ）＋ tools/new/photos.json（目で選んだ写真）・hooks.json（一言）・desc.json（公式の案内）
＋ tools/odekake_more.json（時間・料金・駐車場）＋ links/kansai-yado.json（近くの宿）＋ tools/kaiten/kansai.json（開店）。
作る物：links/new/index.html・list.html・saved.html・kaiten.html・o/<id>.html・cards.json・assets/new.css・new.js
python3 tools/new/build.py [YYYY-MM-DD]"""
import re, json, html, sys, os, glob, hashlib, datetime, shutil
H = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(H))
OUT = os.path.join(R, "links/new")
TODAY = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
T0 = datetime.date.fromisoformat(TODAY)
W = "月火水木金土日"
PREF = {"大阪": ("osaka", "OSAKA", "大阪府"), "京都": ("kyoto", "KYOTO", "京都府"), "兵庫": ("hyogo", "HYOGO", "兵庫県"),
        "奈良": ("nara", "NARA", "奈良県"), "滋賀": ("shiga", "SHIGA", "滋賀県"), "和歌山": ("wakayama", "WAKAYAMA", "和歌山県")}
G = {"紅葉": "koyo", "イルミ": "illumi", "アート": "art", "まつり": "matsuri", "体験": "taiken", "遊ぶ": "etc"}
GEN = [("紅葉", r"紅葉|もみじ|錦秋|秋の特別|夜もみじ"), ("イルミ", r"イルミ|ライトアップ|光の|ナイト|NIGHT|万灯|灯り|クリスマス|ルミナ"),
       ("アート", r"展$|展\s|展「|展覧|美術|ミュージアム|博物|アート|ART|コレクション|企画展|特別展"),
       ("まつり", r"祭|まつり|フェス|マルシェ|フェア|グランプリ|ミート"), ("体験", r"体験|謎|ナゾ|スタンプ|ラリー|ウォーキング|TRAIN|脱出|狩り|ゲーム")]
ICO = {
 "紅葉": '<path d="M12 3l1.6 3.8 3-1.6-.6 3.6 3.6-.4-2 3 2.6 1.6-4 1 .6 2.4-3-1.2-1.8 3-1.8-3-3 1.2.6-2.4-4-1 2.6-1.6-2-3 3.6.4-.6-3.6 3 1.6z"/><path d="M12 15.5V21"/>',
 "イルミ": '<path d="M10 3C10.6 7.5 11.5 8.4 16 9C11.5 9.6 10.6 10.5 10 15C9.4 10.5 8.5 9.6 4 9C8.5 8.4 9.4 7.5 10 3Z"/><path d="M17.5 13.2c.3 2 .7 2.4 2.5 2.7c-1.8.3-2.2.7-2.5 2.7c-.3-2-.7-2.4-2.5-2.7c1.8-.3 2.2-.7 2.5-2.7Z"/><circle cx="6.5" cy="18.5" r="1"/>',
 "アート": '<rect x="3.5" y="4.5" width="17" height="14" rx="1"/><rect x="6.5" y="7.5" width="11" height="8"/><path d="M6.5 15.5l3.3-3.3 2.4 2.2 2-1.8 3.3 2.9"/><circle cx="14.6" cy="9.8" r=".9"/>',
 "まつり": '<path d="M9.5 3.5h5v2h-5zM9.5 18.5h5v2h-5z"/><ellipse cx="12" cy="12" rx="6.2" ry="6.6"/><path d="M6.2 9.6h11.6M5.8 12h12.4M6.2 14.4h11.6"/>',
 "体験": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/><path d="M8.6 9a2 2 0 1 1 2.6 1.9c-.5.2-.7.6-.7 1.1M10.5 13.6v.01"/>',
 "遊ぶ": '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
 "food": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10"/><path d="M17 21V3c-2 1.5-3 4-3 7h3"/>',
 "shop": '<path d="M4 8h16l-1.2 12H5.2z"/><path d="M8.5 8V6.5a3.5 3.5 0 0 1 7 0V8"/>',
}
SVG = lambda k, cls="": f'<svg viewBox="0 0 24 24" aria-hidden="true"{cls}>{ICO[k]}</svg>'
HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/></svg>'
ARW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>'
e = lambda x: html.escape(str(x or ""), quote=True)


def txt(x): return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", x or ""))).strip()
def dd(s): return datetime.date.fromisoformat(s)
def md(s): d = dd(s); return f"{d.month}/{d.day}({'月火水木金土日'[d.weekday()]})"
def jd(s): d = dd(s); return f"{d.month}月{d.day}日（{W[d.weekday()]}）"
def isd(s): return bool(re.fullmatch(r"\d{4}-\d\d-\d\d", s or ""))


def genre(t, m):
    for g, rx in GEN:
        if re.search(rx, t): return g
    for g, rx in GEN:
        if re.search(rx, m): return g
    return "遊ぶ"


def area(city):
    c = re.sub(r"^(大阪府|京都府|兵庫県|奈良県|滋賀県|和歌山県)", "", city).strip()
    m = re.match(r"(.+?)市", c)
    if m: return m.group(1)
    m = re.match(r"(?:.+?郡)?(.+?[町村])", c)
    return m.group(1) if m else c[:4]


def hours(t, alt=""):
    """「17:30〜21:30」「日没〜20:30」「17時半〜21時」→ "17:30-21:30"（分かる時だけ）"""
    m = re.search(r"(日没後?|\d{1,2}:\d\d)(?:ごろ)?〜(\d{1,2}:\d\d)", t)
    if m:
        a = "17:00" if m.group(1).startswith("日没") else m.group(1)
        return f"{a}-{m.group(2)}"
    m = re.search(r"(\d{1,2})時(半)?〜(\d{1,2})時(半)?", alt)
    if m: return f"{m.group(1)}:{'30' if m.group(2) else '00'}-{m.group(3)}:{'30' if m.group(4) else '00'}"
    return ""


def town(c): return re.sub(r"ほか$", "", re.sub(r"^(大阪府|京都府|兵庫県|奈良県|滋賀県|和歌山県)", "", c)).strip()


# ---- 元のデータ ----
src = open(os.path.join(R, "links/index.html"), encoding="utf-8").read()
PH = json.load(open(os.path.join(H, "photos.json"), encoding="utf-8"))
HK = json.load(open(os.path.join(H, "hooks.json"), encoding="utf-8"))
DS = json.load(open(os.path.join(H, "desc.json"), encoding="utf-8"))
MORE = {re.sub(r"\s+", "", k): v for k, v in json.load(open(os.path.join(R, "tools/odekake_more.json"), encoding="utf-8"))["rows"].items()}
YADO = {re.sub(r"\s+", "", k): v for k, v in json.load(open(os.path.join(R, "links/kansai-yado.json"), encoding="utf-8")).items()} if os.path.exists(os.path.join(R, "links/kansai-yado.json")) else {}
MAPS = {}
for f in glob.glob(os.path.join(R, "links/machi/*.html")):
    h = open(f, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)の地価", h)
    mp = re.search(r'<div class="mp nofilt">(<svg.*?</svg>)', h, re.S)
    if t and mp: MAPS[t.group(1)] = mp.group(1)
sys.path.insert(0, os.path.join(R, "tools"))
import spot_map  # noqa  /o/ と同じ「絵地図」とピン（会場の位置は links/townnotes/geo.json）
# 地図の絵は /o/ と同じ物（odekake_spot.py の tint と nice_map だけを借りる。読み込むと /o/ を作り直すので、関数の所だけ取り出す）
_sp = open(os.path.join(R, "tools/odekake_spot.py"), encoding="utf-8").read()
_ns = {"re": re, "html": html}
try:
    exec(re.search(r"(def tint\(.*?)\ndef town\(", _sp, re.S).group(1), _ns); nice_map = _ns["nice_map"]
except Exception:
    nice_map = None

cards, seen = [], set()
for m in re.finditer(r'<a class="card"([^>]*)>(.*?)</a>', src, re.S):
    a = {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+|href)="([^"]*)"', m.group(1))}
    b = m.group(2)
    t = re.search(r'class="t">(.*?)</div>', b, re.S)
    if not t or a.get("data-pref") not in PREF: continue
    name = txt(t.group(1)); key = re.sub(r"\s+", "", name)
    s0, e0 = a.get("data-s", ""), a.get("data-e", "")
    if not isd(e0) or e0 < TODAY or key in seen: continue
    seen.add(key)
    mm = txt((re.search(r'class="m">(.*?)</div>', b, re.S) or [None, ""])[1] if re.search(r'class="m">(.*?)</div>', b, re.S) else "")
    city, _, venue = mm.partition("｜")
    c = dict(t=name, key=key, id=hashlib.md5(key.encode()).hexdigest()[:8], pref=a["data-pref"], s=s0 if isd(s0) else TODAY, e=e0, url=a.get("href", ""),
             free="無料" in a.get("data-tag", ""), city=city.strip(), venue=venue.strip(), map=a.get("data-map", ""), days=a.get("data-days", ""))
    c["g"] = genre(name, mm)
    c["area"] = area(c["city"])
    c["hook"] = HK.get(name, "")
    c["desc"] = DS.get(name, "")
    c["short"] = re.sub(r"\s*20\d\d.*$|～.*$|〜.*$", "", re.sub(r"^20\d\d\s*", "", name))[:20] or name
    c["hours"] = hours(MORE.get(key, {}).get("time", "") or "", c["venue"] + " " + c["desc"])
    try:
        w = spot_map.where(name, c["city"], c["pref"]); c["ll"] = f"{w[1]:.4f},{w[0]:.4f}" if w else ""
    except Exception: c["ll"] = ""
    if name in PH: c.update(img=PH[name]["img"], cr=PH[name]["cr"], crl=PH[name].get("page", ""))
    cards.append(c)


# 11/18 天気：気象庁の予報（府県ごと・あした）。取れない日は前の値（tools/new/weather.json）。雨の府県は「雨でも行ける」を先に出す
JMA = {"大阪": "270000", "京都": "260000", "兵庫": "280000", "奈良": "290000", "滋賀": "250000", "和歌山": "300000"}
WX_F = os.path.join(H, "weather.json")
WX = json.load(open(WX_F, encoding="utf-8")) if os.path.exists(WX_F) else {}
try:
    import urllib.request
    TM = (T0 + datetime.timedelta(days=1)).isoformat()
    nw = {}
    for p, code in JMA.items():
        d = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json", headers={"User-Agent": "TownNote/1.0"}), timeout=20).read())
        ts = d[0]["timeSeries"][0]; ar = ts["areas"][0]
        i = next(k for k, t in enumerate(ts["timeDefines"]) if t[:10] == TM)
        w = re.sub(r"\s+", " ", ar["weathers"][i]).replace("　", " ")
        pop = None
        for t2 in d[1]["timeSeries"]:
            a2 = t2["areas"][0]
            if "pops" in a2:
                for k, t in enumerate(t2["timeDefines"]):
                    if t[:10] == TM and a2["pops"][k] not in ("", None): pop = int(a2["pops"][k])
        if pop is None:
            ps = [int(x) for t, x in zip(d[0]["timeSeries"][1]["timeDefines"], d[0]["timeSeries"][1]["areas"][0]["pops"]) if t[:10] == TM and x != ""]
            pop = max(ps) if ps else None
        nw[p] = {"day": TM, "w": w, "code": ar["weatherCodes"][i], "pop": pop}
    WX = nw; json.dump(WX, open(WX_F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
except Exception as ex:
    print("天気は前の値", ex)


def wx_icon(w):
    if "雪" in w: return "snow"
    if "雨" in w and not re.search(r"晴|くもり|曇", w.split("時々")[0].split("のち")[0].split("一時")[0]): return "rain"
    if "雨" in w: return "rainy"
    if w.startswith("晴"): return "sun"
    return "cloud"


def we_days():
    d = T0
    while d.weekday() != 5: d += datetime.timedelta(days=1)
    return d.isoformat(), (d + datetime.timedelta(days=1)).isoformat()


WE = we_days()
M30 = (T0 + datetime.timedelta(days=30)).isoformat()


def open_on(c, day):
    """その日にやっているか（data-days の wd: は曜日の数字 0=日）"""
    if not (c["s"] <= day <= c["e"]): return False
    m = re.search(r"wd:(\d+)", c["days"])
    if not m: return True
    wd = (dd(day).weekday() + 1) % 7
    return str(wd) in m.group(1)


for c in cards:
    c["we"] = open_on(c, WE[0]) or open_on(c, WE[1])
    c["today"] = open_on(c, TODAY)
    c["tm"] = open_on(c, (T0 + datetime.timedelta(days=1)).isoformat())
    c["left_s"] = (dd(c["s"]) - T0).days
    c["left_e"] = (dd(c["e"]) - T0).days


def badge(c):
    if c["left_s"] > 0:
        return f'<span class="left st">{"あすから" if c["left_s"] == 1 else "あと" + str(c["left_s"]) + "日で始まる"}</span>' if c["left_s"] <= 7 else ""
    if c["left_e"] <= 14: return f'<span class="left">{"きょうまで" if c["left_e"] == 0 else "あと" + str(c["left_e"]) + "日"}</span>'
    return ""


def indoor(c):
    if c["g"] in ("紅葉", "イルミ") or re.search(r"ローズ|バラ|庭|公園|山|農園|狩り|ウォーキング|ドライブ|スタンプ|周遊", c["t"] + c["venue"]): return False
    return c["g"] == "アート" or bool(re.search(r"館|ミュージアム|ホール|センター|水族館|ギャラリー|美術|博物|ステーションシティ|モール|ハルカス|スカイオ|10hall|ドーム|劇場", c["venue"] + c["t"]))


def per(c): return md(c["e"]) + "まで" if c["s"] <= TODAY else md(c["s"]) + "〜" + md(c["e"])
def title(c): return (f"【{c['area']}】" if c["area"] else "") + (c["hook"] or c["t"])
def gcv(g): return f"var(--g-{G[g]})"
def pcv(p): return f"var(--p-{PREF[p][0]})"


def ph(c, w=720, big=False, eager=False):
    if c.get("img"):
        return f'<img src="/new/img/{"" if big or w > 720 else "s/"}{c["img"]}" alt="{e(c["t"])}" {"" if eager else "loading=\"lazy\" "}decoding="async" width="{w}" height="{round(w*.75)}">'
    return f'<div class="tl" style="--gc:{gcv(c["g"])}">{SVG(c["g"])}<span class="tp">{PREF[c["pref"]][1]}</span><span class="tw">{e(c["short"])}</span></div>'


def card(c, cls="cd"):
    q = " ".join([c["t"], c["hook"], c["pref"], c["city"], c["venue"], c["g"], c["area"], "無料" if c["free"] else ""])
    return (f'<article class="{cls}" data-p="{c["pref"]}" data-g="{c["g"]}" data-s="{c["s"]}" data-e="{c["e"]}" data-free="{int(c["free"])}" data-we="{int(c["we"])}" data-today="{int(c["today"])}" data-tm="{int(c["tm"])}" data-img="{int(bool(c.get("img")))}" data-ll="{c["ll"]}" data-h="{c["hours"]}" data-in="{int(indoor(c))}" data-q="{e(q)}">'
            f'<a href="/new/o/{c["id"]}"><div class="ph">{ph(c)}<span class="lab" style="--gc:{gcv(c["g"])}">{c["g"]}</span></div>'
            f'<h3 class="tt">{e(title(c))}</h3><p class="nm">{e(c["t"])}</p>'
            f'<p class="mt"><span class="num">{per(c)}</span>{badge(c)}<span class="now" hidden></span><span class="dist" hidden></span></p>'
            f'<p class="pl" style="--pc:{pcv(c["pref"])}"><i></i><span>{c["pref"]}・{e(town(c["city"]))}</span>{"<span class=free>無料</span>" if c["free"] else ""}</p></a>'
            f'<button class="hrt" data-heart="{c["id"]}" aria-pressed="false" aria-label="行きたいに入れる">{HEART}</button></article>')


FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@500;700;900&display=swap">'


def head(t, desc, extra=""):
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<meta name="robots" content="noindex,nofollow"><title>{e(t)}</title><meta name="description" content="{e(desc)}">'
            f'<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#121110" media="(prefers-color-scheme: dark)">'
            f'{FONTS}<link rel="stylesheet" href="/new/assets/new.css?v={VER}">{extra}'
            '<script>try{var t=localStorage.getItem("odk-theme");if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){}</script></head><body>')


def top(back=None):
    l = (f'<a class="ib back" href="{back}" aria-label="もどる"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></a>' if back else "")
    return (f'<header class="top"><div class="top-in">{l}<a class="logo" href="/new/"><img data-logo src="/new/img/logo.png" alt="" width="34" height="34"><span><b>関西おでかけ</b><small>KANSAI TOWN NOTE</small></span></a>'
            '<a class="ib" href="/new/list" aria-label="さがす"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg></a>'
            '<button class="ib" id="theme" aria-label="昼と夜を切りかえ"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></button></div></header>')


def bar(cur):
    items = [("list", "/new/list", "さがす", '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>'),
             ("saved", "/new/saved", "行きたい", '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>'),
             ("top", "/new/", "ホーム", '<path d="M4 10.5 12 4l8 6.5V20h-5.5v-5.5h-5V20H4z"/>'),
             ("kaiten", "/new/kaiten", "開店", '<path d="M4 8h16l-1.2 12H5.2z"/><path d="M8.5 8V6.5a3.5 3.5 0 0 1 7 0V8"/>'),
             ("stay", "/tomari", "泊まり", '<path d="M3.5 18.5v-9M3.5 14h17v4.5M20.5 14v-2.5a3 3 0 0 0-3-3H11V14"/><circle cx="7.3" cy="11.3" r="1.8"/>')]
    out = "".join(f'<a href="{u}"{" aria-current=page" if k == cur else ""}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{p}</svg>{t}{"<span class=cnt hidden>0</span>" if k == "saved" else ""}</a>' for k, u, t, p in items)
    return f'<nav class="bar" aria-label="下のメニュー"><div class="bar-in">{out}</div></nav>'


def credits(cs):
    L, seen = [], set()
    for c in cs:
        if c.get("cr") and c["cr"] not in seen:
            seen.add(c["cr"])
            L.append(f'<li>{e(c["t"])}：{e(c["cr"])}' + (f'（<a href="{e(c["crl"])}" rel="nofollow noopener" target="_blank">元の写真</a>）' if c.get("crl") else "") + "</li>")
    return f'<details class="credits"><summary>写真のクレジット（{len(L)}枚）</summary><ol>{"".join(L)}</ol></details>' if L else ""


def foot(cs):
    return (credits(cs) + '<footer class="foot">写真は、撮った人が自由に使えるとした写真（ウィキメディア・コモンズ、Flickr など）と、兵庫県観光連盟の「ひょうご観光写真ライブラリー」の写真です。写真のない催しは、種類の絵で出しています。'
            '日にちや中身は変わることがあります。出かける前に公式ページで確かめてください。<br>宿のリンクの一部は広告です（楽天トラベル）。<br>© 関西おでかけ（TOWN NOTE）</footer>')


END = '<script src="/new/assets/new.js?v={v}" defer></script></body></html>'

# ---- ページを作る ----
shutil.rmtree(os.path.join(OUT, "o"), ignore_errors=True)
os.makedirs(os.path.join(OUT, "o"), exist_ok=True); os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
css = open(os.path.join(H, "new.css"), encoding="utf-8").read(); js = open(os.path.join(H, "new.js"), encoding="utf-8").read()
VER = hashlib.md5((css + js).encode()).hexdigest()[:8]
END = END.format(v=VER)
open(os.path.join(OUT, "assets/new.css"), "w", encoding="utf-8").write(css)
open(os.path.join(OUT, "assets/new.js"), "w", encoding="utf-8").write(js)

act = sorted(cards, key=lambda c: (c["s"] > TODAY, c["e"] if c["s"] <= TODAY else c["s"]))
withimg = [c for c in act if c.get("img")]
cnt = lambda f: sum(1 for c in act if f(c))

# いちばん上のニュース：写真があり、7日以内に始まる紅葉・イルミ（無ければ開催中の紅葉）を、始まりが近い順に3つ
def score(c):
    s = 0
    if c["g"] in ("紅葉", "イルミ"): s += 30
    if 0 < c["left_s"] <= 7: s += 40 - c["left_s"] * 3
    elif c["left_s"] <= 0 and c["left_e"] >= 3: s += 20
    if c["free"]: s += 4
    return s
news = sorted(withimg, key=lambda c: -score(c))[:4]


def news_slide(c, i):
    k = ("あすから" if c["left_s"] == 1 else f"{md(c['s'])}から") if c["left_s"] > 0 else ("開催中")
    lead = (c["desc"][:58] + "…") if len(c["desc"]) > 60 else c["desc"]
    return (f'<a class="hero" href="/new/o/{c["id"]}" data-slide="{i}"{"" if i == 0 else " hidden"}>{ph(c, 1200, eager=i == 0)}'
            f'<div class="tx"><span class="kick"><b>NEWS</b>{c["pref"]}・{e(town(c["city"]))}｜{k}</span><h2>{e(title(c))}</h2><p>{e(lead)}</p></div></a>')


def write(path, s):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)


gchips = "".join(f'<a class="chip" href="/new/list?g={g}" style="--c:{gcv(g)}"><i></i>{g}<em>{cnt(lambda c: c["g"] == g)}</em></a>' for g in G if g != "遊ぶ")
gchips += f'<a class="chip" href="/new/list?free=1" style="--c:var(--ok)"><i></i>無料<em>{cnt(lambda c: c["free"])}</em></a>'
gchips += f'<a class="chip" href="/new/list?w=today"><i style="--c:var(--soon)"></i>きょう行ける<em>{cnt(lambda c: c["today"])}</em></a>'
we = sorted([c for c in act if c["we"] and c not in news], key=lambda c: (not c.get("img"), c["left_e"]))[:6]
pick = sorted([c for c in withimg if c not in news and c not in we], key=lambda c: (c["g"] not in ("紅葉", "イルミ"), -c["left_e"] if c["left_e"] < 60 else 0))[:8]
soon = sorted([c for c in act if c["s"] <= TODAY and c["left_e"] <= 10], key=lambda c: c["e"])[:5]
starting = sorted([c for c in act if 0 < c["left_s"] <= 14], key=lambda c: (not c.get("img"), c["s"]))[:4]


def first_img(f):
    for c in withimg:
        if f(c): return c["img"]
    return withimg[0]["img"] if withimg else ""


pmap = "".join(f'<a class="pt" href="/new/list?p={p}"><img src="/new/img/{first_img(lambda c, p=p: c["pref"] == p)}" alt="" loading="lazy"><span><span class="en">{PREF[p][1]}</span><b>{p}</b><small>{cnt(lambda c, p=p: c["pref"] == p)}件</small></span></a>' for p in PREF)
mat = [("紅葉", "Autumn leaves", "関西の紅葉と<br>ライトアップ", "/new/list?g=紅葉"), ("イルミ", "Illumination", "冬のイルミネーション", "/new/list?g=イルミ"),
       ("無料", "Free", "無料で行ける", "/new/list?free=1"), ("アート", "Art", "美術館・展覧会", "/new/list?g=アート")]
matH = ""
for g, en, t, u in mat:
    f = (lambda c: c["free"]) if g == "無料" else (lambda c, g=g: c["g"] == g)
    matH += f'<a class="mt2" href="{u}"><img src="/new/img/{first_img(f)}" alt="" loading="lazy"><div class="tx"><span class="en">{en}</span><b>{t}</b><small>{cnt(f)}件</small></div></a>'

KAI = json.load(open(os.path.join(R, "tools/kaiten/kansai.json"), encoding="utf-8"))["items"]
KAI = sorted([k for k in KAI if k.get("d", "") >= (T0 - datetime.timedelta(days=14)).isoformat()], key=lambda k: (k["d"] < TODAY, abs((dd(k["d"]) - T0).days)))


def kcat(k):
    return "food" if re.search(r"ラーメン|カフェ|食|焼|寿司|鮨|パン|スイーツ|ベビーカステラ|レストラン|酒|バー|居酒屋|うどん|そば|カレー|肉|丼|菓子|ケーキ|茶|ベーカリー|ピザ|餃子|バーガー", k["n"] + k.get("pt", "")) else "shop"


def kitem(k):
    d0 = dd(k["d"]); g = kcat(k)
    ck = "開店" if k.get("k") == "open" else "新しく"
    lab = "きょう" if k["d"] == TODAY else ("あす" if (d0 - T0).days == 1 else f"{d0.month}/{d0.day}")
    city = (re.match(r"(?:.+?市)?([^市・]+?区)", k.get("pl", "")) or re.match(r"(.+?[市町村])", k.get("pl", "")))
    return (f'<a class="k" href="{e(k["u"])}" target="_blank" rel="noopener"><div class="kt" style="--gc:var(--g-{"food" if g == "food" else "etc"})">{SVG(g)}<b>{d0.month}.{d0.day} {"MON TUE WED THU FRI SAT SUN".split()[d0.weekday()]}</b></div>'
            f'<div><div class="kn">{e(k["n"])}</div><div class="kp">{e(k.get("pt", ""))}</div><div class="kg"><span class="tag2 op">{lab}{ck}</span><span class="tag2">{k["p"]}・{e(city.group(1) if city else "")}</span>{"<span class=tag2>" + e(k["tm"]) + "</span>" if k.get("tm") else ""}</div></div></a>')


WXI = {"sun": '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.5 1.5M17.2 17.2l1.5 1.5M5.3 18.7l1.5-1.5M17.2 6.8l1.5-1.5"/>',
       "cloud": '<path d="M7 18.5h10a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.8 9.4 4.6 4.6 0 0 0 7 18.5z"/>',
       "rainy": '<path d="M7 15.5h10a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.8 6.4 4.6 4.6 0 0 0 7 15.5z"/><path d="M9 18.5l-.8 2M13 18.5l-.8 2"/>',
       "rain": '<path d="M7 14.5h10a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.8 5.4 4.6 4.6 0 0 0 7 14.5z"/><path d="M8 17.5l-1 2.5M12 17.5l-1 2.5M16 17.5l-1 2.5"/>',
       "snow": '<path d="M7 14.5h10a4 4 0 0 0 .4-8A5.5 5.5 0 0 0 6.8 5.4 4.6 4.6 0 0 0 7 14.5z"/><path d="M8 18.5h.01M12 19.5h.01M16 18.5h.01"/>'}
rainy = [p for p in PREF if WX.get(p, {}).get("pop") is not None and WX[p]["pop"] >= 50]
wx_html = ""
if WX:
    tmd = dd(next(iter(WX.values()))["day"])
    wx_html = (f'<section class="sec"><div class="h"><div><span class="en">Tomorrow</span><h2>あした{tmd.month}/{tmd.day}の天気で選ぶ</h2></div><span class="more" style="font-weight:700">気象庁の予報</span></div><div class="wx">'
               + "".join(f'<a href="/new/list?p={p}{"&in=1" if p in rainy else ""}&w=tomorrow" class="{"r" if p in rainy else ""}"><svg viewBox="0 0 24 24" aria-hidden="true">{WXI[wx_icon(WX[p]["w"])]}</svg><b>{p}</b><small>{"雨 " + str(WX[p]["pop"]) + "%" if WX[p].get("pop") is not None else e(WX[p]["w"][:4])}</small></a>' for p in PREF if p in WX) + '</div>')
    if rainy:
        ind = sorted([c for c in act if c["pref"] in rainy and indoor(c) and c["tm"]], key=lambda c: (not c.get("img"), c["left_e"]))[:4]
        wx_html += f'<p class="wxn">あしたは{"・".join(rainy)}で雨になりそうです。屋根の下で楽しめるおでかけをどうぞ。</p><div class="grid">{"".join(card(c) for c in ind)}</div><a class="btn" href="/new/list?in=1&w=tomorrow">雨でも行けるおでかけを全部見る</a>'
    else:
        out = sorted([c for c in act if not indoor(c) and c["tm"]], key=lambda c: (not c.get("img"), c["g"] not in ("紅葉", "イルミ"), c["left_e"]))[:4]
        wx_html += f'<p class="wxn">あしたは関西のどこも雨の心配が少なめ。外のおでかけ日和です。</p><div class="grid">{"".join(card(c) for c in out)}</div>'
    wx_html += '</section>'
dots = '<div class="dots" aria-hidden="true">' + "".join(f'<i{" class=on" if i == 0 else ""}></i>' for i in range(len(news))) + "</div>"
slider_js = ('<script>(function(){var s=[].slice.call(document.querySelectorAll("[data-slide]")),d=[].slice.call(document.querySelectorAll(".dots i")),i=0;if(s.length<2)return;'
             'function go(n){s[i].hidden=true;d[i].className="";i=(n+s.length)%s.length;s[i].hidden=false;d[i].className="on"}'
             'var t=setInterval(function(){go(i+1)},5200),x0=null;var w=document.getElementById("heroW");'
             'w.addEventListener("touchstart",function(e){x0=e.touches[0].clientX},{passive:true});w.addEventListener("touchend",function(e){if(x0==null)return;var dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40){e.preventDefault();clearInterval(t);go(i+(dx<0?1:-1))}x0=null})})()</script>')

top_html = (head("関西おでかけ｜きょう・今週末に行ける関西のおでかけ", "大阪・京都・兵庫・奈良・滋賀・和歌山のイベント・紅葉・イルミネーションを、毎朝公式ページで確かめて更新。") + top() +
            '<main class="wrap">'
            '<form class="search" action="/new/list" role="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><input name="q" type="search" placeholder="紅葉・美術館・地名でさがす" enterkeyhint="search" aria-label="さがす"></form>'
            f'<div class="chips" style="margin-top:12px" aria-label="種類">{gchips}</div>'
            f'<section class="sec" style="margin-top:22px"><div class="h"><div><span class="en">Today’s news</span><h2>きょうのおでかけニュース</h2></div><span class="more num" style="font-family:var(--f-en)">{md(TODAY)}</span></div>'
            f'<div id="heroW">{"".join(news_slide(c, i) for i, c in enumerate(news))}</div>{dots}</section>'
            + wx_html +
            f'<section class="sec"><div class="h"><div><span class="en">This weekend</span><h2>今週末、行ける</h2></div><a class="more" href="/new/list?w=we">{cnt(lambda c: c["we"])}件すべて{ARW}</a></div><div class="grid">{"".join(card(c) for c in we)}</div></section>'
            f'<section class="sec"><div class="h"><div><span class="en">When</span><h2>いつ行く？</h2></div></div><div class="when">'
            + "".join(f'<a href="/new/list?w={k}"><b>{t}</b><small>{n}件</small></a>' for k, t, n in [("today", "きょう", cnt(lambda c: c["today"])), ("tomorrow", "あした", cnt(lambda c: open_on(c, (T0 + datetime.timedelta(days=1)).isoformat()))), ("we", "今週末", cnt(lambda c: c["we"])), ("month", "30日以内", cnt(lambda c: c["s"] <= M30)), ("free", "無料", cnt(lambda c: c["free"])), ("end", "もうすぐ終わる", cnt(lambda c: c["s"] <= TODAY and c["left_e"] <= 7))]) + '</div></section>'
            f'<section class="sec"><div class="h"><div><span class="en">Pick up</span><h2>いま行きたい、ピックアップ</h2></div></div><div class="rail">{"".join(card(c, "cd pk") for c in pick)}</div></section>'
            + (f'<section class="sec"><div class="h"><div><span class="en">Coming soon</span><h2>もうすぐ始まる</h2></div><a class="more" href="/new/list?sort=new">すべて{ARW}</a></div><div class="grid">{"".join(card(c) for c in starting)}</div></section>' if starting else "") +
            f'<section class="sec"><div class="h"><div><span class="en">By prefecture</span><h2>府県からさがす</h2></div></div><div class="pmap">{pmap}</div></section>'
            f'<section class="sec"><div class="h"><div><span class="en">Collections</span><h2>まとめて見る</h2></div></div><div class="rail">{matH}</div></section>'
            f'<section class="sec"><div class="h"><div><span class="en">New shops</span><h2>開店ニュース</h2></div><a class="more" href="/new/kaiten">{len(KAI)}件すべて{ARW}</a></div><div class="kl">{"".join(kitem(k) for k in KAI[:4])}</div></section>'
            f'<section class="sec"><div class="h"><div><span class="en">Last chance</span><h2>もうすぐ終わる</h2></div><a class="more" href="/new/list?sort=end">すべて{ARW}</a></div><div>'
            + "".join(f'<a class="e" href="/new/o/{c["id"]}"><div class="ph">{ph(c)}</div><div><b>{e(title(c))}</b><small>{c["pref"]}・{e(town(c["city"]))}｜{md(c["e"])}まで</small></div><div class="d">{"きょう" if c["left_e"] == 0 else "あと<b>" + str(c["left_e"]) + "</b>日"}</div></a>' for c in soon) +
            '</div></section>'
            '<div class="follow"><b>あしたの朝も、おでかけニュース。</b><p>毎朝、関西の「きょう行ける」を1本の動画でお届けします。</p><div class="fb"><a href="https://www.instagram.com/fudousan_ai_si" target="_blank" rel="noopener">インスタ</a><a href="https://x.com/fudosan_ai_si" target="_blank" rel="noopener">X</a><a href="https://www.threads.com/@fudousan_ai_si" target="_blank" rel="noopener">Threads</a></div></div>'
            + foot(news + we + pick + starting + soon) + '</main>' + bar("top") + slider_js + END)
write("index.html", top_html)

# 一覧
pch = '<button class="chip" data-set="p" data-v="">関西ぜんぶ</button>' + "".join(f'<button class="chip" data-set="p" data-v="{p}" style="--c:{pcv(p)}"><i></i>{p}</button>' for p in PREF)
gch = "".join(f'<button class="chip" data-set="g" data-v="{g}" style="--c:{gcv(g)}"><i></i>{g}</button>' for g in G) + '<button class="chip" data-set="free" data-v="1" style="--c:var(--ok)"><i></i>無料</button><button class="chip" data-set="in" data-v="1" style="--c:var(--g-illumi)"><i></i>雨でも行ける</button>'
wch = "".join(f'<button class="chip" data-set="w" data-v="{k}">{t}</button>' for k, t in [("", "いつでも"), ("today", "きょう行ける"), ("tomorrow", "あした"), ("we", "今週末"), ("month", "30日以内"), ("end", "もうすぐ終わる")])
list_html = (head("関西のおでかけ一覧｜開催中・今週末・これから", "関西のおでかけを、府県・種類・日にちでしぼりこめます。") + top("/new/") +
             '<main class="wrap"><div class="lh"><h1 id="h1">関西のおでかけ</h1><p>公式ページで日にちを確かめた物だけ載せています</p></div>'
             '<form class="search" role="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><input id="q" name="q" type="search" placeholder="紅葉・美術館・地名でさがす" enterkeyhint="search" aria-label="さがす"></form>'
             f'<div class="fbar"><div class="chips">{pch}</div><div class="chips">{gch}</div><div class="chips">{wch}</div></div>'
             '<button class="nearb" id="nearb" type="button"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/></svg>いる場所から近い順に並べる</button>'
             '<div class="lbar"><span><b id="n">0</b> 件</span><label>並び <select class="sel" id="sort"><option value="soon">いま行ける順</option><option value="end">終わりが近い順</option><option value="new">始まりが新しい順</option><option value="near">近い順</option></select></label></div>'
             f'<div class="grid" id="list" data-today="{TODAY}" data-m30="{M30}" data-e7="{(T0 + datetime.timedelta(days=7)).isoformat()}">{"".join(card(c) for c in act)}</div>'
             '<div class="empty" id="empty" hidden>この組み合わせのおでかけは、いまはありません。<br>「いつでも」や「関西ぜんぶ」にすると増えます。</div><button class="btn" id="more" hidden></button>'
             + foot(act) + '</main>' + bar("list") + END)
write("list.html", list_html)

# 行きたい
write("saved.html", head("行きたい｜関西おでかけ", "♡ を押したおでかけ") + top("/new/") +
      '<main class="wrap"><div class="lh"><h1>行きたい</h1><p>♡ を押したおでかけが、ここにたまります（この端末だけ）</p></div><div style="height:18px"></div>'
      '<div class="grid" id="saved"></div><div class="empty" id="sempty" hidden>まだありません。<br>写真の右上の ♡ を押すと、ここに入ります。<br><br><a class="chip" href="/new/list" style="display:inline-flex">おでかけをさがす</a></div>'
      + foot([]) + '</main>' + bar("saved") + END)
json.dump([dict(id=c["id"], html=card(c)) for c in act], open(os.path.join(OUT, "cards.json"), "w", encoding="utf-8"), ensure_ascii=False)

# 開店
write("kaiten.html", head("関西の開店ニュース｜新しいお店", "関西で新しく開くお店を、日にち順に。") + top("/new/") +
      f'<main class="wrap"><div class="lh"><h1>関西の開店ニュース</h1><p>お店や会社の発表（PR TIMES など）で確かめた、新しく開くお店です。{len(KAI)}件</p></div><div style="height:12px"></div>'
      f'<div class="kl">{"".join(kitem(k) for k in KAI)}</div>' + foot([]) + '</main>' + bar("kaiten") + END)


# 1件ずつのページ
def gcal(c, place):
    import urllib.parse as up
    d1 = dd(c["s"]).strftime("%Y%m%d"); d2 = (dd(c["e"]) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    return "https://calendar.google.com/calendar/render?" + up.urlencode({"action": "TEMPLATE", "text": c["t"], "dates": f"{d1}/{d2}", "location": place + " " + c["city"], "details": f"{c['url']}\nhttps://kansai.townnote.app/new/o/{c['id']}"})


def ics(c, place):
    d1 = dd(c["s"]).strftime("%Y%m%d"); d2 = (dd(c["e"]) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    esc = lambda x: x.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")
    return "\r\n".join(["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//TOWN NOTE//kansai//JA", "BEGIN:VEVENT", f"UID:{c['id']}@kansai.townnote.app", f"DTSTAMP:{T0.strftime('%Y%m%d')}T000000Z",
                         f"DTSTART;VALUE=DATE:{d1}", f"DTEND;VALUE=DATE:{d2}", "SUMMARY:" + esc(c["t"]), "LOCATION:" + esc(place + " " + c["city"]), "URL:" + c["url"],
                         "DESCRIPTION:" + esc(f"公式 {c['url']}\n関西おでかけ https://kansai.townnote.app/new/o/{c['id']}"), "END:VEVENT", "END:VCALENDAR", ""])


def detail(c):
    gc = gcv(c["g"]); mo = MORE.get(c["key"], {})
    if c["left_s"] > 0: pill = f'<span class="pill wait">{"あすから" if c["left_s"] == 1 else "あと" + str(c["left_s"]) + "日で始まる"}</span>'
    elif c["left_e"] <= 3: pill = f'<span class="pill end">{"きょうまで" if c["left_e"] == 0 else "あと" + str(c["left_e"]) + "日で終わる"}</span>'
    else: pill = '<span class="pill">開催中</span>' if not c["today"] else '<span class="pill">きょう、やっています</span>'
    when = jd(c["s"]) + ("〜" + jd(c["e"]) if c["e"] != c["s"] else "")
    rows = [("期間", when)] + ([("時間", mo["time"])] if mo.get("time") else []) + ([("料金", mo["price"])] if mo.get("price") else ([("料金", "無料")] if c["free"] else [])) + ([("駐車場", mo["park"])] if mo.get("park") else [])
    place = c["venue"] or c["map"] or c["city"]
    mq = c["map"] or (place + " " + c["city"])
    tw = town(c["city"])
    try: svg = spot_map.render(c["pref"], c["t"], c["city"], (c["venue"] or tw)[:12])
    except Exception: svg = ""
    ya = YADO.get(c["key"], [])[:3]
    near = sorted([x for x in act if x is not c and x["pref"] == c["pref"]], key=lambda x: (x["g"] != c["g"], not x.get("img"), abs(x["left_e"] - c["left_e"])))[:4]
    same = sorted([x for x in act if x is not c and x["g"] == c["g"] and x["pref"] != c["pref"]], key=lambda x: (not x.get("img"), x["left_e"]))[:4]
    toc = [("s1", "どんな催し？")] + ([("s2", "近くの宿")] if ya else []) + [("s3", "場所と地図"), ("s4", "DATA"), ("s5", f"{c['pref']}のほかのおでかけ")]
    share_t = f'{c["t"]} {md(c["s"])}〜{md(c["e"])}'
    cr = (f'<span class="cr">写真：{e(c["cr"])}' + (f'（<a href="{e(c["crl"])}" target="_blank" rel="nofollow noopener">元の写真</a>）' if c.get("crl") else "") + "</span>") if c.get("cr") else ""
    body = (f'<div class="dh"><div class="ph">{ph(c, 1200, eager=True)}<span class="lab big" style="--gc:{gc}">{c["g"]}</span></div></div>{cr}'
            f'<nav class="crumb"><a href="/new/">関西おでかけ</a>›<a href="/new/list?p={c["pref"]}">{c["pref"]}</a>›<a href="/new/list?g={c["g"]}">{c["g"]}</a></nav>'
            f'<div class="d1"><span class="lab2" style="--gc:{gc}">{c["g"]}</span><span class="num" style="font-size:13px;font-weight:700">{md(c["s"])}〜{md(c["e"])}</span><span class="pl" style="--pc:{pcv(c["pref"])};margin:0"><i></i><span>{c["pref"]}・{e(tw)}</span>{"<span class=free>無料</span>" if c["free"] else ""}</span></div>'
            f'<h1 class="dh1">{e(title(c))}</h1><p class="dsub">{e(c["t"])}</p>'
            f'<div class="state" data-h="{c["hours"]}" data-s="{c["s"]}" data-e="{c["e"]}"><div class="s1">{pill}<span class="now" hidden></span><small>{md(TODAY)}の時点</small></div><dl>' + "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in rows) + f'<dt>場所</dt><dd>{e(place)}</dd></dl></div>'
            f'<div class="acts"><a class="act main" href="{e(c["url"])}" target="_blank" rel="noopener">公式ページで確かめる{ARW}</a>'
            f'<button class="act" data-heart="{c["id"]}" aria-pressed="false">{HEART}行きたい</button><button class="act" data-share="{e(share_t)}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V4M7.5 8.5 12 4l4.5 4.5M5 13v6h14v-6"/></svg>だれかに送る</button></div>'
            f'<div class="shr" id="shr"><a href="https://line.me/R/share?text={e(__import__("urllib.parse").parse.quote(share_t + " https://kansai.townnote.app/new/o/" + c["id"]))}" target="_blank" rel="noopener">LINE</a><a href="https://x.com/intent/post?text={e(__import__("urllib.parse").parse.quote(share_t))}&url={e(__import__("urllib.parse").parse.quote("https://kansai.townnote.app/new/o/" + c["id"]))}" target="_blank" rel="noopener">X</a><button data-copy="{e(share_t)}">文をコピー</button></div>'
            f'<div class="cal"><a href="{e(gcal(c, place))}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 9.5h17M8 3v4M16 3v4M12 12.5v5M9.5 15h5"/></svg>Googleカレンダーに入れる</a><a href="/new/ics/{c["id"]}.ics" download>iPhoneの予定に入れる</a></div>'
            f'<div class="toc"><b>このページの目次</b><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc) + '</ol></div>'
            f'<section class="ds" id="s1" style="--gc:{gc}"><h2>どんな催し？<span class="en">About</span></h2><p class="lead">{e(c["desc"] or c["t"])}<small>公式ページの案内をもとにまとめました（{md(TODAY)}に確かめました）</small></p></section>'
            + (f'<section class="ds" id="s2" style="--gc:{gc}"><h2>近くの宿<span class="en">Stay</span></h2><p class="adl">広告（楽天トラベル）</p><ul class="yl">' + "".join(
                f'<li><a href="{e(y["u"])}" target="_blank" rel="noopener sponsored"><b>{e(y["n"])}</b><small>会場から約{y.get("km", "?")}km・★{y.get("r", "-")}（{y.get("rc", 0)}件）</small><em>{y.get("min", 0):,}<span>円〜</span></em></a></li>' for y in ya) + '</ul></section>' if ya else "")
            + f'<section class="ds" id="s3" style="--gc:{gc}"><h2>場所と地図<span class="en">Access</span></h2><div class="mapw">{svg or ""}<div class="mapb"><div><b>{e(place)}</b><small>{c["pref"]}・{e(tw)}</small></div><a href="https://www.google.com/maps/search/?api=1&query={e(__import__("urllib.parse").parse.quote(mq))}" target="_blank" rel="noopener">地図で開く</a></div></div></section>'
            f'<section class="ds" id="s4" style="--gc:{gc}"><h2>DATA</h2><table class="data"><tbody><tr><th>名前</th><td>{e(c["t"])}</td></tr>' + "".join(f"<tr><th>{k}</th><td>{e(v)}</td></tr>" for k, v in rows) +
            f'<tr><th>場所</th><td>{e(place)}（{c["pref"]}・{e(tw)}）</td></tr><tr><th>公式</th><td><a href="{e(c["url"])}" target="_blank" rel="noopener">{e(re.sub(r"^https?://(www\.)?", "", c["url"]).split("/")[0])}</a></td></tr></tbody></table>'
            f'<p class="src">日にち・時間・料金は、公式ページで{md(TODAY)}に確かめた物です。変わることがあるので、出かける前に公式ページを見てください。</p></section>'
            f'<section class="ds" id="s5" style="--gc:{gc}"><h2>{c["pref"]}のほかのおでかけ<span class="en">Nearby</span></h2><div class="grid">{"".join(card(x) for x in near)}</div></section>'
            + (f'<section class="ds" style="--gc:{gc}"><h2>ほかの府県の{c["g"]}<span class="en">More</span></h2><div class="grid">{"".join(card(x) for x in same)}</div></section>' if same else ""))
    cta = (f'<div class="sticky-cta"><div><button class="hrt" data-heart="{c["id"]}" aria-pressed="false" aria-label="行きたいに入れる">{HEART}</button>'
           f'<span style="min-width:0"><b>{e(c["t"])}</b><small>{md(c["s"])}〜{md(c["e"])}</small></span><a href="{e(c["url"])}" target="_blank" rel="noopener">公式</a></div></div>')
    og = "<style>" + spot_map.night_css() + "</style>" + (f'<meta property="og:title" content="{e(title(c))}"><meta property="og:image" content="https://kansai.townnote.app/new/img/{c["img"]}">' if c.get("img") else "")
    return (head(f'{title(c)}｜{c["t"]} {md(c["s"])}〜{md(c["e"])}｜関西おでかけ', (c["desc"] or c["t"])[:110], og) + top("/new/list") +
            '<main class="wrap">' + body + foot([c] + near + same) + '</main>' + cta + bar("") + END)


shutil.rmtree(os.path.join(OUT, "ics"), ignore_errors=True)
for c in act:
    write(f'o/{c["id"]}.html', detail(c))
    write(f'ics/{c["id"]}.ics', ics(c, c["venue"] or c["map"] or c["city"]))
print("おでかけ", len(act), "写真あり", len(withimg), "ニュース", [c["t"] for c in news], "開店", len(KAI))
