#!/usr/bin/env python3
"""管制室（簡易版）に入れる今週の数字を1つのJSONにする。
使い方: python3 tools/seichou/latest.py 出力先.json  → ArtifactData set seichou/latest（file_path）"""
import json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
d = json.load(open(os.path.join(R, "stats", "seichou.json"), encoding="utf-8"))
for k in ("pages", "ext0", "no_ask"): d.pop(k, None)
d["date"] = d["day"]
json.dump(d, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
print(d["date"], "外から", d["ext7"], "弱い所", d["weak"])
