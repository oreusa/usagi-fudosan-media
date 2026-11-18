"""11/18 月：コモンズに無い写真を Openverse（Flickr などの自由な写真をまとめて探せる検索・鍵なし）から探す。
11/18 owner「めんどい・俺居なきゃむりじゃん」→ 1枚ずつ申し込む写真集（大阪観光局）はやめ、機械だけで回る道。
使い方: python3 tools/photo/openverse.py <一覧.tsv> <保存先>   一覧＝「名前<TAB>探す言葉1|言葉2」
商用OK・改変OKの物だけ（CC0・PDM・CC BY・CC BY-SA）。横長・幅1200以上。1件に候補3枚。最後は目で見て決める。"""
import json, os, re, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "TownNotePhotoBot/1.0 (https://kansai.townnote.app/)"}
BAD = r"station|parking|sign|map|ticket|poster|logo|document|screenshot"


def get(u, n=3):
    for i in range(n):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        except Exception:
            if i == n - 1: raise
            time.sleep(4 + i * 4)


def search(q):
    p = {"q": q, "license_type": "commercial,modification", "aspect_ratio": "wide", "page_size": 20, "mature": "false"}
    d = json.loads(get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(p)))
    out = []
    for r in d.get("results", []):
        w, h = r.get("width") or 0, r.get("height") or 0
        if w and (w < 1000 or w < h * 1.2): continue
        txt = (r.get("title") or "") + " " + " ".join(t.get("name", "") for t in (r.get("tags") or []))
        s = 10 - 6 * bool(re.search(BAD, txt, re.I))
        out.append({"title": r.get("title"), "page": r.get("foreign_landing_url"), "thumb": r.get("thumbnail") or r.get("url"), "url": r.get("url"),
                    "license": ((r.get("license") or "").upper() + " " + (r.get("license_version") or "")).strip(), "artist": r.get("creator") or "", "src": r.get("source"), "w": w, "h": h, "score": s, "tags": txt[:200]})
    out.sort(key=lambda x: -x["score"])
    return out


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    res = []
    for i, ln in enumerate(open(src, encoding="utf-8")):
        if "\t" not in ln: continue
        name, qs = ln.rstrip("\n").split("\t"); cand = []
        for q in [x for x in qs.split("|") if x]:
            try: cand = search(q)[:3]
            except Exception as ex: print("ERR", q, ex)
            time.sleep(2)
            if cand: break
        for k, r in enumerate(cand):
            fn = f"{i:03d}-{k}.jpg"
            try: open(os.path.join(out, fn), "wb").write(get(r["thumb"])); r["file"] = fn
            except Exception as ex: print("ERR img", ex)
        res.append({"name": name, "cand": cand})
        print(i, name, "→", [(r["title"] or "")[:30] for r in cand])
    json.dump(res, open(os.path.join(out, "best.json"), "w"), ensure_ascii=False, indent=1)
    print("候補あり", sum(1 for r in res if r["cand"]), "/", len(res))
