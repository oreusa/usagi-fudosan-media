#!/usr/bin/env python3
"""コモンズのファイルを言葉で探す（ウィキデータの項目が無い会場・町の写真用）。候補4枚を残し、最後は人が目で見て選ぶ。
使い方: csearch.py 表.tsv(名前<TAB>言葉1|言葉2) 出す先   → best.json と NNN-k.jpg（best.py と同じ形）"""
import sys, os, json, re, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PW", "1200")
import best as B
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
res = []
for i, ln in enumerate(open(src, encoding="utf-8")):
    if "\t" not in ln: continue
    name, qs = ln.rstrip("\n").split("\t"); cand = []
    for q in [x for x in qs.split("|") if x]:
        try:
            d = B.js(B.API + urllib.parse.urlencode({"action": "query", "format": "json", "list": "search", "srsearch": q + " filetype:bitmap", "srnamespace": 6, "srlimit": 20}))
            titles = [h["title"] for h in d.get("query", {}).get("search", [])]
            if not titles: continue
            inf = B.info(titles)
            for t in titles:
                o = inf.get(t) or {}; ii = o.get("ii") or {}
                md = ii.get("extmetadata", {}); lic = md.get("LicenseShortName", {}).get("value", "")
                if not any(lic.startswith(x) for x in B.OK): continue
                w, h = ii.get("width", 0), ii.get("height", 1)
                if w < 1000 or w < h * 1.15: continue
                if re.search(r"map|地図|logo|sign|駅名標|時刻表|timetable|diagram|plan", t, re.I): continue
                cand.append({"title": t, "page": ii.get("descriptionurl"), "thumb": ii.get("thumburl"), "license": lic, "artist": re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()[:80], "w": w, "h": h, "q": q})
        except Exception as ex:
            print("ERR", q, ex)
        if len(cand) >= 4: break
        time.sleep(0.5)
    cand = cand[:4]
    for k, r in enumerate(cand):
        fn = f"{i:03d}-{k}.jpg"
        try: open(os.path.join(out, fn), "wb").write(B.get(r["thumb"])); r["file"] = fn
        except Exception as ex: print("ERR img", ex)
    res.append({"name": name, "cand": cand})
    print(i, name, len(cand), flush=True)
json.dump(res, open(os.path.join(out, "best.json"), "w"), ensure_ascii=False, indent=1)
