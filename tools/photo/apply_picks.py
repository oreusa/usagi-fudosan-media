#!/usr/bin/env python3
"""目で選んだ会場の写真を venue_photos.json に入れる。
使い方: apply_picks.py <probe の出力フォルダ(best.json)> <選んだ表.tsv: 会場名<TAB>番号<TAB>候補>"""
import sys, os, json, hashlib, re, datetime
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D, P = sys.argv[1], sys.argv[2]
PH = os.environ.get("PHDIR") or os.path.join(R, "links/assets/ph"); VPF = os.environ.get("VPFILE") or os.path.join(R, "tools/new/venue_photos.json")  # 関東(燈)にも使う
VP = json.load(open(VPF)); B = json.load(open(os.path.join(D, "best.json")))
T = datetime.date.today().isoformat()
for ln in open(P, encoding="utf-8"):
    if not ln.strip() or ln.startswith("#"): continue
    vn, i, k = ln.rstrip("\n").split("\t"); c = B[int(i)]["cand"][int(k)]
    im = Image.open(os.path.join(D, c["file"])).convert("RGB")
    f = hashlib.md5(("venue:" + vn).encode()).hexdigest()[:8] + ".webp"
    im.thumbnail((1200, 1200)); im.save(os.path.join(PH, f), "WEBP", quality=80)
    s = im.copy(); s.thumbnail((480, 480)); s.save(os.path.join(PH, "s", f), "WEBP", quality=76)
    w, h = im.size; s0 = min(w, h); im.crop(((w - s0) // 2, (h - s0) // 2, (w - s0) // 2 + s0, (h - s0) // 2 + s0)).resize((200, 200)).save(os.path.join(PH, "t", f), "WEBP", quality=74)
    a = re.sub(r"\s+", " ", c.get("artist") or "撮影者").strip()[:40]
    VP[vn] = {"img": f, "cr": f'{a}（{c["license"]}・Wikimedia Commons）', "page": c["page"], "d": T}
    print(vn, f, im.size, c["title"][5:60])
json.dump(VP, open(VPF, "w"), ensure_ascii=False, indent=1)
