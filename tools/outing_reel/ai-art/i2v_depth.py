"""絵の奥行き（手前・奥）を Depth Anything V2（Apache-2.0 の Small）で読む＋衛星写真のタイル（EOX Sentinel-2 cloudless 2016、CC BY 4.0）を取る。GPU なしで動く。"""
import glob, io, json, math, os, sys, urllib.request
from PIL import Image
out = sys.argv[1]; SRC = sys.argv[2] if len(sys.argv) > 2 else 'shots/ai-art/jingoji-img'; LL = sys.argv[3] if len(sys.argv) > 3 else '35.0437,135.6727'; os.makedirs(out, exist_ok=True); log = []
try:
    from transformers import pipeline
    pipe = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf', device=-1)
    for f in sorted((glob.glob(SRC + '/*.webp') + glob.glob(SRC + '/*.jpg'))):
        im = Image.open(f).convert('RGB'); d = pipe(im)['depth']
        n = os.path.basename(f).rsplit('.', 1)[0]; d.resize(im.size).save(f'{out}/{n}-depth.png'); log.append(f'{n} 奥行きOK')
except Exception as e:
    log.append(f'奥行き 失敗 {str(e)[:300]}')
# 衛星写真タイル：日本全体 z5 → 高雄 z13 まで、各段で中心の周り
LAT, LON = map(float, LL.split(',')) if LL != 'none' else (0.0, 0.0)
def tile(z):
    n = 2 ** z; x = (LON + 180) / 360 * n; y = (1 - math.log(math.tan(math.radians(LAT)) + 1 / math.cos(math.radians(LAT))) / math.pi) / 2 * n; return x, y
for layer in ([] if LL == 'none' else ['s2cloudless_3857']):
    for z, R in [(4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2), (13, 2)]:
        cx, cy = tile(z); ok = 0
        for dx in range(-R, R + 1):
            for dy in range(-R, R + 1):
                x, y = int(cx) + dx, int(cy) + dy; p = f'{out}/sat/{z}/{x}_{y}.jpg'; os.makedirs(os.path.dirname(p), exist_ok=True)
                u = f'https://tiles.maps.eox.at/wmts/1.0.0/{layer}/default/g/{z}/{y}/{x}.jpg'
                try:
                    with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (reel map)'}), timeout=30) as r: open(p, 'wb').write(r.read()); ok += 1
                except Exception as e: log.append(f'{u} {str(e)[:100]}')
        log.append(f'衛星 z{z} {ok}枚 中心 {cx:.3f},{cy:.3f}')
open(f'{out}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
