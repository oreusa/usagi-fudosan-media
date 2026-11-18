# 11/19 激変版：写真の明るさ（夜の写真か）を先に測って ph/ns.json に書く。hitech2.js の nightScan と同じ式。
# python3 tools/hx/nightscore.py <ph のフォルダ>
import sys, os, json
from PIL import Image
d = sys.argv[1]; out = {}
for f in sorted(os.listdir(d)):
    if not f.endswith(('.webp', '.jpg', '.jpeg', '.png')): continue
    try:
        im = Image.open(os.path.join(d, f)).convert('RGB').resize((24, 24), Image.BILINEAR)
    except Exception:
        continue
    px = list(im.getdata()); t = 0; br = 0
    for r, g, b in px:
        l = (.2126*r + .7152*g + .0722*b) / 255; t += l
        if l > .75: br += 1
    out[f] = round(t/len(px) - min(.08, br/576*.4), 3)
json.dump(out, open(os.path.join(d, 'ns.json'), 'w'), separators=(',', ':'))
print(len(out), sum(1 for v in out.values() if v < .42), 'night')
