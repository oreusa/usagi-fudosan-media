"""Cloudflare の無料枠が切れた日に、同じ絵のAI（FLUX.2 klein 4B・Apache-2.0）を GitHub の機械（CPU）で描く。
使い方: python3 klein_cpu.py 番号 全体の数 req1.json req2.json ...  → out/<名前>/<item>.jpg"""
import json, os, sys, time, gc, torch
from diffusers import Flux2KleinPipeline
k, n = int(sys.argv[1]), int(sys.argv[2]); jobs = []
for p in sys.argv[3:]:
    r = json.load(open(p)); nm = os.path.basename(p)[4:-5]
    for it in r['items']: jobs.append((nm, it, r['style']))
mine = [j for i, j in enumerate(jobs) if i % n == k]
print('mine', [(a, b['name']) for a, b, c in mine], flush=True)
torch.set_num_threads(os.cpu_count()); t = time.time()
pipe = Flux2KleinPipeline.from_pretrained('black-forest-labs/FLUX.2-klein-4B', torch_dtype=torch.bfloat16, token=os.environ.get('HF_TOKEN') or None)
print('load', round(time.time() - t), flush=True)
for nm, it, st in mine:
    t = time.time(); os.makedirs(f'out/{nm}', exist_ok=True)
    with torch.inference_mode():
        im = pipe(prompt=f"{it['prompt']}. {st}", width=it.get('W', 1088), height=it.get('H', 1920), num_inference_steps=4, guidance_scale=1.0, generator=torch.Generator().manual_seed(7)).images[0]
    im.save(f"out/{nm}/{it['name']}.jpg", quality=93); print(nm, it['name'], 'sec', round(time.time() - t), flush=True); gc.collect()
