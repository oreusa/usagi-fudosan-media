#!/usr/bin/env python3
"""毎朝：写真のない催しに、会場の写真と主催者のインスタを自動で付ける（11/18 owner「今回だけじゃない」）。
1) 一覧のカードから会場名を取り出す（tools/photo/venues.json を作り直す）
2) 写真が無い会場は Commons の会場の分類から一番点の高い写真を取る（名前が合う項目だけ・1日20会場まで）
   → links/assets/ph（大・s・t）＋ tools/new/venue_photos.json（auto:1）
3) 公式ページから主催者のインスタのアカウントを探す（1日40件まで）→ tools/new/ig.json の acc
試した物は tools/new/auto_tried.json に日付つきで残し、30日は同じ物を試さない。
このあと build.py をもう1回走らせると mihon.json に入る。"""
import os, re, sys, json, glob, hashlib, datetime, urllib.request, io
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, "tools/photo"))
os.environ.setdefault("PW", "1200")
import best as B
NEW = os.path.join(R, "tools/new"); PH = os.path.join(R, "links/assets/ph")
def lj(p, d):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return d
def sj(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
k = lambda s: re.sub(r"\s+", "", s)
today = datetime.date.today(); T = today.isoformat()
M = lj(os.path.join(R, "links/assets/mihon.json"), {})
PHOTOS = lj(os.path.join(NEW, "photos.json"), {})
VP = lj(os.path.join(NEW, "venue_photos.json"), {})
IG = lj(os.path.join(NEW, "ig.json"), {})
TR = lj(os.path.join(NEW, "auto_tried.json"), {"v": {}, "ig": {}})
def fresh(d, key): return key in d and (today - datetime.date.fromisoformat(d[key])).days < 30

# 1) 会場
V = {}
for f in [os.path.join(R, "links/index.html")] + glob.glob(os.path.join(R, "links/illumination*.html")) + glob.glob(os.path.join(R, "links/koyo*.html")):
    h = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<a class="card[^"]*".*?</a>', h, re.S):
        c = m.group(0); t = re.search(r'class="t">([^<]+)', c)
        if not t: continue
        mm = re.search(r'class="m">([^<]+)', c); V[k(t.group(1))] = mm.group(1) if mm else ""
ven = {}
for key, o in M.items():
    p = PHOTOS.get(o["n"]) or {}
    if p and not p.get("weak"): continue
    m = V.get(key, "")
    place = m.split("｜")[-1].strip() if "｜" in m else o["n"]
    place = re.sub(r"（[^）]*）|\([^)]*\)", "", place).strip()
    place = re.split(r"ほか|・|、| ", place)[0] or place
    if "。" in m: place = o["n"]   # 場所の欄が説明文の時は、名前そのものが場所（新しい施設など）
    ven.setdefault(place, []).append(key)
sj(os.path.join(R, "tools/photo/venues.json"), ven)

# 2) 会場の写真
def save(url, name):
    from PIL import Image
    b = B.get(url); im = Image.open(io.BytesIO(b)).convert("RGB")
    f = hashlib.md5(name.encode()).hexdigest()[:8] + ".webp"
    im.thumbnail((1200, 1200)); im.save(os.path.join(PH, f), "WEBP", quality=80)
    s = im.copy(); s.thumbnail((480, 480)); os.makedirs(os.path.join(PH, "s"), exist_ok=True); s.save(os.path.join(PH, "s", f), "WEBP", quality=76)
    w, h = im.size; s0 = min(w, h); t = im.crop(((w - s0) // 2, (h - s0) // 2, (w - s0) // 2 + s0, (h - s0) // 2 + s0)).resize((200, 200))
    os.makedirs(os.path.join(PH, "t"), exist_ok=True); t.save(os.path.join(PH, "t", f), "WEBP", quality=74)
    return f
n = 0
AL = lj(os.path.join(R, "tools/photo/venue_alias.json"), {})
for raw in sorted(ven, key=lambda x: -len(ven[x])):
    vn = AL.get(raw, raw)
    if vn in VP or fresh(TR["v"], vn) or len(vn) < 2 or re.search(r"市内|区内|県内|エリア|各駅|か所|周辺|駅前|駅$", vn): continue
    if n >= int(os.environ.get("AUTO_V", "20")): break
    n += 1; TR["v"][vn] = T
    try:
        e = B.entity(vn)
        lab = (e or {}).get("label", "")
        if not e or not (e.get("p18") or e.get("cat")) or not lab or not (k(vn) in k(lab) or k(lab) in k(vn)): print("代表の写真なし", vn, lab); continue
        # 11/21 オーナー「より良い写真を」→ その場所の分類（同じ場所の写真だけ）から、文字の点＋見た目の点（色・くっきり・季節）で一番の1枚。
        # 点が低い・無い時は今まで通り「ウィキデータの代表の写真」（人がその場所の写真として選んだ物）
        th = B.theme_of(" ".join(M[x]["n"] for x in ven[raw] if x in M))
        c = None
        if e.get("cat"):
            try:
                _, cs = B.best(vn, th)
                if cs and cs[0]["score"] >= 70: c = cs[0]
            except Exception as ex: print("ERR best", vn, ex)
        if not c:
            if not e.get("p18"): print("代表の写真なし", vn, lab); continue
            t = "File:" + e["p18"]; ii = (B.info([t]).get(t) or {}).get("ii") or {}
            md = ii.get("extmetadata", {}); lic = md.get("LicenseShortName", {}).get("value", "")
            if not any(lic.startswith(x) for x in B.OK) or ii.get("width", 0) < 800 or ii.get("width", 0) < ii.get("height", 1): print("使えない写真", vn, lic); continue
            c = {"thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"), "license": lic, "artist": re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip(), "title": t}
        f = save(c["thumb"], "venue:" + vn)
        VP[vn] = {"img": f, "cr": f'{(c["artist"] or "撮影者")[:40]}（{c["license"]}・Wikimedia Commons）', "page": c["page"], "auto": 1, "d": T}
        print("会場の写真", vn, "←", lab, c["title"][:50])
    except Exception as ex:
        print("ERR", vn, ex)
sj(os.path.join(NEW, "venue_photos.json"), VP)

# 3) 主催者のインスタ（アカウントだけ。投稿の埋め込みは人が見て選ぶ）
BAD = set(json.load(open(os.path.join(R, "tools/photo/ig_bad.json"), encoding="utf-8")))
UA = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile Safari/604.1"}
ACC = re.compile(r'instagram\.com/([A-Za-z0-9_.]{2,30})/?["\'?#]')
n = 0
for key, o in M.items():
    if o["n"] in IG or not o.get("u", "").startswith("http") or fresh(TR["ig"], o["n"]): continue
    if n >= int(os.environ.get("AUTO_IG", "40")): break
    n += 1; TR["ig"][o["n"]] = T
    try: h = urllib.request.urlopen(urllib.request.Request(o["u"], headers=UA), timeout=15).read(1500000).decode("utf-8", "ignore")
    except Exception: continue
    a = [x for x in dict.fromkeys(m.group(1) for m in ACC.finditer(h)) if x.lower() not in BAD and x not in BAD]
    if a: IG[o["n"]] = {"acc": a[:1], "auto": 1}; print("インスタ", o["n"], a[0])
sj(os.path.join(NEW, "ig.json"), IG); sj(os.path.join(NEW, "auto_tried.json"), TR)
print("会場の写真", len(VP), "・インスタ", len(IG))
