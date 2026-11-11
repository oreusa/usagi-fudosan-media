"""flash.js が撮ったコマを見くらべて、一瞬だけ映る乱れを探す（11/11）。使い方: python3 tools/allcheck/flash.py <FLASH_OUT>"""
import json, os, sys
from PIL import Image, ImageChops
D = sys.argv[1]; bad = 0
def diff(a, b):
    h = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 30 else 0).histogram()
    return h[255] / (a.size[0] * a.size[1])
for e in json.load(open(os.path.join(D, "index.json"), encoding="utf-8")):
    fr = [Image.open(os.path.join(D, f"f-{e['id']}-{j:02d}.png")).convert("RGB") for j in range(e["n"])]
    for i in range(1, len(fr) - 1):
        a, b, ac = diff(fr[i - 1], fr[i]), diff(fr[i], fr[i + 1]), diff(fr[i - 1], fr[i + 1])
        if a > 0.10 and b > 0.10 and ac < 0.03:
            bad += 1; print("× 一瞬の乱れ", e["path"], e["k"], "「" + e["t"] + "」", f"コマ{i}/{len(fr)}", f"{a*100:.0f}%", f"f-{e['id']}-{i:02d}.png"); break
print(f"flash.py: 押した物 {sum(1 for _ in json.load(open(os.path.join(D, 'index.json'), encoding='utf-8')))}／一瞬の乱れ {bad}")
sys.exit(1 if bad else 0)
