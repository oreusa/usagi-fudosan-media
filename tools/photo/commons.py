"""11/18 月：場所の写真を、ウィキメディア・コモンズの「自由に使える写真」から集める（撮った人の名前と使ってよい決まりも一緒に保存）。
Actions で動かす（作業環境からはつながらない）。python3 tools/photo/commons.py <保存先> 言葉1 言葉2 ..."""
import json, os, sys, time, urllib.parse, urllib.request, re
OK = ("CC0", "Public domain", "CC BY 2.0", "CC BY 2.1", "CC BY 3.0", "CC BY 4.0", "CC BY-SA 2.0", "CC BY-SA 2.1", "CC BY-SA 3.0", "CC BY-SA 4.0")
UA = {"User-Agent": "TownNotePhotoBot/1.0 (https://kansai.townnote.app/)"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
res = {}
for q in sys.argv[2:]:
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 12,
         "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 900}
    try:
        d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
    except Exception as e:
        print("ERR", q, e); continue
    pages = sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99))
    got = []
    for pg in pages:
        ii = (pg.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "")
        if not any(lic.startswith(o) for o in OK): continue
        if ii.get("width", 0) < ii.get("height", 1): continue  # 横長だけ
        art = re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
        fn = re.sub(r"[^\w.-]", "_", q) + f"-{len(got)}.jpg"
        try:
            open(os.path.join(out, fn), "wb").write(get(ii["thumburl"]))
        except Exception as e:
            print("ERR img", e); continue
        got.append({"file": fn, "title": pg["title"], "page": ii.get("descriptionurl"), "license": lic, "artist": art[:80]})
        time.sleep(1)
        if len(got) >= 3: break
    res[q] = got; print(q, len(got))
json.dump(res, open(os.path.join(out, "credits.json"), "w"), ensure_ascii=False, indent=1)
