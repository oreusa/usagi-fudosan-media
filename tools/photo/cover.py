"""11/18 月：おでかけ1件ずつに「その場所の自由に使える写真」があるかを数える（コモンズ）。
python3 tools/photo/cover.py <一覧.tsv> <保存先>  一覧＝「名前<TAB>探す言葉1|言葉2」
1件に1枚（横長・CC0/CC BY/CC BY-SA）の小さい絵と、撮った人・決まりを cover.json に残す。"""
import json, os, sys, time, urllib.parse, urllib.request, re
sys.path.insert(0, os.path.dirname(__file__))
OK = ("CC0", "Public domain", "CC BY 2.0", "CC BY 2.1", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0", "CC BY-SA 2.0", "CC BY-SA 2.1", "CC BY-SA 2.5", "CC BY-SA 3.0", "CC BY-SA 4.0")
UA = {"User-Agent": "TownNotePhotoBot/1.0 (https://kansai.townnote.app/)"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
def find(q):
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 15,
         "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 480}
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99))
    for pg in pages:
        ii = (pg.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "")
        if not any(lic.startswith(o) for o in OK): continue
        if ii.get("width", 0) < ii.get("height", 1) * 1.2: continue
        art = re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
        return {"title": pg["title"], "page": ii.get("descriptionurl"), "thumb": ii.get("thumburl"), "license": lic, "artist": art[:80], "q": q}
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
res = []
for i, ln in enumerate(open(src, encoding="utf-8")):
    if "\t" not in ln: continue
    name, qs = ln.rstrip("\n").split("\t")
    hit = None
    for q in [x for x in qs.split("|") if x]:
        try: hit = find(q)
        except Exception as e: print("ERR", q, e)
        time.sleep(0.5)
        if hit: break
    if hit:
        fn = f"{i:03d}.jpg"
        try: open(os.path.join(out, fn), "wb").write(get(hit["thumb"])); hit["file"] = fn
        except Exception as e: print("ERR img", e)
    res.append({"name": name, "hit": hit})
    print(i, name, "→", (hit or {}).get("title", "なし"))
json.dump(res, open(os.path.join(out, "cover.json"), "w"), ensure_ascii=False, indent=1)
print("写真あり", sum(1 for r in res if r["hit"]), "/", len(res))
