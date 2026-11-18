"""お客さんの画面に出してはいけない言葉が、作ったページに無いか調べる（11/9 オーナー「なんか対策ないの」）。
見つかったら 1 で終わる（page.yml ではここで止まり、本番に出さない）。言葉は ngwords.json。
使い方: python3 ngcheck.py ページのフォルダ [ngwords.json]"""
import glob, json, os, re, sys
root = sys.argv[1]
wf = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ngwords.json")
_d = json.load(open(wf))
W = [(re.compile(rx), why) for rx, why in _d["words"]]
ALLOW = _d.get("allow", [])  # 正しい言葉（イベント名など）はここに足す

# 11/18 開店ニュースの店名「茶と食 雫香」が中の名前「雫」に当たり、関東の公開が丸ごと止まった（オーナー「そんなミスダメだろ」）。
# → 外から来た固有の名前（お店・催し・会場の名前）は「中の名前」の点検だけから外す。外すのはその名前の文字列そのものだけで、
#   うちが書いた文（説明・見出し・案内）は今までどおり全部調べる。名前は、ページの JSON-LD（Event・Place・お店など）と
#   集めたデータ（開店ニュース・おでかけ）から機械で取る。ALLOW に毎回手で足さなくてよくなる。
_LD_SKIP = {"WebPage", "WebSite", "Organization", "BreadcrumbList", "ListItem", "Article", "NewsArticle", "ItemList", "FAQPage", "Question", "Answer", "Person", "Offer", "AggregateOffer", "ImageObject", "SiteNavigationElement", "CollectionPage"}
_NAME_KEYS = ("n", "name", "title", "venue", "place", "pl")
EXT = set()
def _walk_ld(o):
    if isinstance(o, list):
        for x in o: _walk_ld(x)
    elif isinstance(o, dict):
        ty = o.get("@type"); ty = ty if isinstance(ty, list) else [ty]
        if not (set(t for t in ty if t) & _LD_SKIP) and isinstance(o.get("name"), str):
            EXT.add(o["name"])
        for v in o.values(): _walk_ld(v)
def _walk_data(o):
    if isinstance(o, list):
        for x in o: _walk_data(x)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in _NAME_KEYS and isinstance(v, str): EXT.add(v)
            else: _walk_data(v)
_repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _rel in _d.get("external_data", []):
    for _p in (os.path.join(_repo, _rel), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), _rel)):
        if os.path.exists(_p):
            try: _walk_data(json.load(open(_p, encoding="utf-8")))
            except Exception: pass
            break
for _f in glob.glob(os.path.join(root, "**", "*.html"), recursive=True):
    for _m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', open(_f, errors="ignore").read(), re.S):
        try: _walk_ld(json.loads(_m.group(1)))
        except Exception: pass
EXT = sorted((e for e in EXT if len(e) >= 2), key=len, reverse=True)
def _ext_off(text):
    for e in EXT:
        text = text.replace(e, " ")
    return text
SKIP = re.compile(r"mihon|preview|-try\.html|_mihon|okaimono-live|otoku|/googl[^/]*\.html$")
bad = []
for f in sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True)):
    if SKIP.search(f):
        continue
    t = open(f, errors="ignore").read()
    if 'name="robots" content="noindex' in t and "/c/" in f:
        continue
    t = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<!--.*?-->", " ", t, flags=re.S)
    attrs = " ".join(re.findall(r'(?:title|alt|content|aria-label|placeholder)="([^"]*)"', t))
    text = re.sub(r"<[^>]+>", " ", t) + " " + attrs
    for a in ALLOW:
        text = text.replace(a, "")
    text_ext = _ext_off(text)
    for rx, why in W:
        src = text_ext if "中の名前" in why else text
        for m in rx.finditer(src):
            s = src[max(0, m.start() - 20):m.end() + 20].replace("\n", " ").strip()
            bad.append(f"{os.path.relpath(f, root)}：{why}：…{s}…")
            break
# 11/9 メニューの「本当に値下がりした物」は JS の中の文だった → JS の文字（"…"・'…'）も調べる
for f in sorted(glob.glob(os.path.join(root, "assets", "*.js"))):
    if SKIP.search(f):
        continue
    t = open(f, errors="ignore").read()
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    t = re.sub(r"(?m)^\s*//.*$", " ", t)
    text = " ".join(m.group(2) for m in re.finditer(r"(['\"])((?:(?!\1)[^\\\n]|\\.)*)\1", t))
    text = re.sub(r"\$\{[^}]*\}", "", text)
    for a in ALLOW:
        text = text.replace(a, "")
    for rx, why in W:
        if why == "壊れた表示":
            continue
        for m in rx.finditer(text):
            s = text[max(0, m.start() - 20):m.end() + 20].replace("\n", " ").strip()
            bad.append(f"{os.path.relpath(f, root)}：{why}：…{s}…")
            break
# 11/9 オーナー「レントラックス登録してないよな？」「記録してないのは管理体制に問題」
# → お金のリンクのASPが台帳（asp.json）に無い・IDが台帳と違う物は赤にする。
_here = os.path.dirname(os.path.abspath(__file__))
_aspf = next((p for p in [os.path.join(_here, "asp.json"), os.path.join(_here, "..", "asp.json")] if os.path.exists(p)), None)
if _aspf:
    A = json.load(open(_aspf))
    reg = {d: a for a in A["asp"] for d in a["domains"]}
    nreg = {d: a for a in A.get("not_registered", []) for d in a["domains"]}
    idpat = {"ck.jp.ap.valuecommerce.com": r"[?&](?:amp;)?sid=(\d+)", "af.moshimo.com": r"[?&](?:amp;)?a_id=(\d+)", "px.a8.net": r"a8mat=([A-Z0-9]+)", "hb.afl.rakuten.co.jp": r"/h[gc]c/([0-9a-f.]+)", "www.amazon.co.jp": r"[?&](?:amp;)?tag=([A-Za-z0-9-]+)"}
    files = [f for f in sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True)) + sorted(glob.glob(os.path.join(root, "assets", "*.js"))) if not SKIP.search(f)]
    seen = set()
    for f in files:
        t = open(f, errors="ignore").read()
        for m in re.finditer(r"https?://([A-Za-z0-9.-]+)([^\s\"'<>]*)", t):
            host, rest = m.group(1).lower(), m.group(2)
            key = None
            if host in nreg or any(host.endswith("." + d) for d in nreg):
                key = f"{os.path.relpath(f, root)}：台帳に無いASP（{(nreg.get(host) or {}).get('name', host)}）：{host}"
            elif host in idpat and host in reg:
                mm = re.search(idpat[host], rest)
                if mm and mm.group(1) not in reg[host].get("ids", []):
                    key = f"{os.path.relpath(f, root)}：台帳に無いID（{reg[host]['name']}）：{mm.group(1)}"
            if key and key not in seen:
                seen.add(key)
                bad.append(key)
# 11/9 おでかけ「高照らすみやこ」が名前違いで2枚あった（リンク点検では見つかっていたのに残った）
# → 1つのページで、同じURLのカードが2枚以上ある物は赤にする（合同の催しは OK_SAME に足す）。
OK_SAME = {"https://hikari-kyoen.com/core/renaissance", "https://www.tsubosaka1300.or.jp/news130.html"}
for f in [os.path.join(root, "index.html")] + sorted(glob.glob(os.path.join(root, "illumination*.html"))) + sorted(glob.glob(os.path.join(root, "koyo*.html"))):
    if not os.path.exists(f):
        continue
    _t = open(f, errors="ignore").read()
    # 紅葉の名所（card ms）は出典の一覧ページを共有することがあり、昼の名所と夜のライトアップで同じ寺も出るので、名所どうしの名前の重なりだけ見る
    hs = re.findall(r'<a class="card(?![^"]* ms)[^"]*"[^>]*?href="([^"]+)"', _t)
    for u, n in __import__("collections").Counter(re.findall(r'<a class="card[^"]* ms"[^>]*?data-map="([^"]+)"', _t)).items():
        if n > 1:
            bad.append(f"{os.path.relpath(f, root)}：同じ名所が{n}枚：{u}")
    for u, n in __import__("collections").Counter(hs).items():
        if n > 1 and u not in OK_SAME:
            bad.append(f"{os.path.relpath(f, root)}：同じ催しが{n}枚：{u}")
# 11/10 オーナー「ライトのとこおかしい」: /sagasu の .mo（あと◯の街ボタン）が昼/夜ボタンの月(.mo)と同じ名前で、ボタンが二重に見えた
# → menu.js を読むページで、昼/夜ボタンの中の名前（su/mo/kn/sp）をページ側の <style> で使っていたら赤にする。
for f in sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True)):
    if SKIP.search(f):
        continue
    _t = open(f, errors="ignore").read()
    if "menu.js" not in _t:
        continue
    _css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", _t, flags=re.S))
    for m in re.finditer(r"(?:^|[},])\s*\.(su|mo|kn|sp)(?![\w-])", _css):
        if "#utheme" in _css[m.end():m.end() + 80].split("{")[0]:  # .mo:not(:where(#utheme *)) のように除けている物はOK
            continue
        bad.append(f"{os.path.relpath(f, root)}：昼/夜ボタンと同じクラス名 .{m.group(1)}（名前を変える）")
        break
# 11/10 夜 #150：おでかけの場所が、書いてある市区町村・府県の形から外れていたら赤（geocheck.py）
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import geocheck
    bad += geocheck.check(root)
except Exception as _ex:
    print("geocheck skipped", _ex)
for b in bad[:80]:
    print("×", b)
print(f"ngcheck: {len(bad)} 件" if bad else "ngcheck: なし")
sys.exit(1 if bad else 0)
