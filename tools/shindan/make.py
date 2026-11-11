#!/usr/bin/env python3
"""実家・空き家の3問診断（links/jikka/shindan/index.html）を作る。
街の名前は links/assets/towns.json、売れた平均は links/jikka/<id>.html（近畿レインズ 2025年度）から取る。
使い方: python3 tools/shindan/make.py"""
import json, re, pathlib
R = pathlib.Path(__file__).resolve().parents[2]
L = R / "links"
towns = json.load(open(L / "assets/towns.json", encoding="utf-8"))
D = []
for t in towns:
    f = L / "jikka" / (t["id"] + ".html")
    if not f.exists():
        continue
    s = f.read_text(encoding="utf-8")
    i = s.find("SOLD 2025年度")
    blk = s[i:i + 900] if i >= 0 else ""
    def pick(kind):
        m = re.search(r"<b>([\d,]+)<small>万円</small></b><span>" + kind + r"の平均（(\d+)件", blk)
        return [int(m.group(1).replace(",", "")), int(m.group(2))] if m else None
    D.append({"i": t["id"], "p": t["p"], "n": t["n"], "k": t.get("k", ""), "h": pick("中古一戸建て"), "m": pick("中古マンション")})
tpl = (pathlib.Path(__file__).parent / "tpl.html").read_text(encoding="utf-8")
out = tpl.replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":")))
(L / "jikka/shindan").mkdir(parents=True, exist_ok=True)
(L / "jikka/shindan/index.html").write_text(out, encoding="utf-8")
# 前のURL（/shindan）は新しい場所へ送る
(L / "shindan.html").write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>実家・空き家の3問診断｜TOWN NOTE</title><script>location.replace("/jikka/shindan/"+location.search)</script><a href="/jikka/shindan/">実家・空き家の3問診断へ</a>', encoding="utf-8")
print("towns", len(D), "with price", sum(1 for d in D if d["h"] or d["m"]), "bytes", len(out.encode()))
