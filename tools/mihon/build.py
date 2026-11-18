"""11/18 今のHPのクオリティアップ（見本）：写真・【地名】の一言・時間・説明を1つの表にまとめる。
links/assets/mihon.json と links/assets/ph/（写真）を作る。mihon.js が今のページ（カード・おすすめ5・1件ページ）に足す。
見本の間は ?mihon=1 を付けた人だけに出る（night.js が読み込む）。"""
import os, re, sys, json, html, hashlib, shutil
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(R, "tools/new"))
NEW = os.path.join(R, "tools/new")
PH = json.load(open(os.path.join(NEW, "photos.json"), encoding="utf-8"))
HK = json.load(open(os.path.join(NEW, "hooks.json"), encoding="utf-8"))
DS = json.load(open(os.path.join(NEW, "desc.json"), encoding="utf-8"))
MORE = {re.sub(r"\s+", "", k): v for k, v in json.load(open(os.path.join(R, "tools/odekake_more.json"), encoding="utf-8"))["rows"].items()}
OUT = os.path.join(R, "links/assets/ph"); os.makedirs(os.path.join(OUT, "t"), exist_ok=True)
SRC = os.path.join(R, "links/new/img") if os.path.isdir(os.path.join(R, "links/new/img")) else OUT


def txt(x): return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", x or ""))).strip()


def area(city):
    c = re.sub(r"^(大阪府|京都府|兵庫県|奈良県|滋賀県|和歌山県)", "", city).strip()
    m = re.match(r"(.+?)市", c)
    if m: return m.group(1)
    m = re.match(r"(?:.+?郡)?(.+?[町村])", c)
    return m.group(1) if m else c[:4]


def hours(t, alt=""):
    m = re.search(r"(日没後?|\d{1,2}:\d\d)(?:ごろ)?〜(\d{1,2}:\d\d)", t)
    if m: return f"{'17:00' if m.group(1).startswith('日没') else m.group(1)}-{m.group(2)}"
    m = re.search(r"(\d{1,2})時(半)?〜(\d{1,2})時(半)?", alt)
    if m: return f"{m.group(1)}:{'30' if m.group(2) else '00'}-{m.group(3)}:{'30' if m.group(4) else '00'}"
    return ""


import glob
src = "".join(open(f, encoding="utf-8").read() for f in [os.path.join(R, "links/index.html")] + sorted(glob.glob(os.path.join(R, "links/illumination*.html"))) + sorted(glob.glob(os.path.join(R, "links/koyo*.html"))))
data = {}
for m in re.finditer(r'<a class="card[^"]*"([^>]*)>(.*?)</a>', src, re.S):
    a = {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+|href)="([^"]*)"', m.group(1))}
    b = m.group(2); t = re.search(r'class="t">(.*?)</div>', b, re.S)
    if not t: continue
    name = txt(t.group(1)); key = re.sub(r"\s+", "", name)
    if key in data: continue
    mm = re.search(r'class="m">(.*?)</div>', b, re.S); city, _, venue = txt(mm.group(1) if mm else "").partition("｜")
    i = hashlib.md5(key.encode()).hexdigest()[:8]
    o = {"n": name, "u": a.get("href", ""), "s": a.get("data-s", ""), "e": a.get("data-e", ""), "p": a.get("data-pref", "")}
    for k2, k3 in (("data-days", "dy"), ("data-cl", "cl")):
        if a.get(k2): o[k3] = a[k2]
    if os.path.exists(os.path.join(R, f"links/o/{i}.html")): o["id"] = i
    ar = area(city.strip()); hk = HK.get(name, "")
    if hk: o["hk"] = hk
    if ar: o["ar"] = ar
    d = DS.get(name, "")
    if d: o["ds"] = d
    h = hours(MORE.get(key, {}).get("time", "") or "", venue + " " + d)
    if h: o["h"] = h
    p = PH.get(name)
    if p:
        f = p["img"]
        for sub in ("", "s/"):
            s = os.path.join(SRC, sub + f); dst = os.path.join(OUT, sub + f)
            if os.path.exists(s) and os.path.abspath(s) != os.path.abspath(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copyfile(s, dst)
        th = os.path.join(OUT, "t", f)
        if not os.path.exists(th):
            from PIL import Image
            im = Image.open(os.path.join(OUT, f)).convert("RGB"); w, hh = im.size; s0 = min(w, hh)
            im = im.crop(((w - s0) // 2, (hh - s0) // 2, (w - s0) // 2 + s0, (hh - s0) // 2 + s0)).resize((200, 200), Image.LANCZOS)
            im.save(th, "WEBP", quality=74)
        o.update(im=f, cr=p["cr"], cu=p.get("page", ""))
    data[key] = o
json.dump(data, open(os.path.join(R, "links/assets/mihon.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("見本の表", len(data), "件・写真", sum(1 for v in data.values() if "im" in v), "・1件ページ", sum(1 for v in data.values() if "id" in v))
