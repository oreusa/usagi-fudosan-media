# 絵の奥行き（白＝手前・黒＝奥）を Depth Anything V2 Large で。par3.html の dp に入れると、手前と奥が別々に動く。
import sys, os, urllib.request, io
import numpy as np
from PIL import Image, ImageFilter
from transformers import pipeline
lst, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
pipe = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Large-hf', device='cpu')
for line in open(lst):
    p = line.split()
    if len(p) < 2 or p[0].startswith('#'): continue
    name, url = p[0], p[1]
    im = Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert('RGB')
    r = pipe(im)['depth']  # PIL, 白＝近い
    a = np.asarray(r.resize(im.size, Image.BICUBIC), dtype=np.float32)
    lo, hi = np.percentile(a, 1), np.percentile(a, 99); a = np.clip((a - lo) / max(hi - lo, 1e-3), 0, 1)
    Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)).save(f'{out}/{name}.png')
    print('ok', name, im.size)
