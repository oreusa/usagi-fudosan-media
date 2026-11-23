"""絵本のページの絵を画像AIで描く（11/19 owner「絵だけ画像AIで描く」）。GitHub の仕組みの中で動かす（作業場からは画像AIにつなげない）。
画像AI＝FLUX.1-schnell（Apache-2.0＝商用で使ってよい）を Hugging Face の公開の窓口から呼ぶ。鍵は要らない。
req.json の各絵を seed を変えて何枚か描き、out/ に置く。"""
import json, os, shutil, sys, time
from gradio_client import Client
req = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
style = req['style']; log = []
TOK = (os.environ.get('HF_TOKEN') or '').strip() or None
c = Client(req.get('space', 'black-forest-labs/FLUX.1-schnell'), token=TOK)   # 鍵が無いと1回3枚まで
for it in req['items']:
    for s in it.get('seeds', [1, 2, 3]):
        p = f"{it['prompt']}. {style}"; f = f"{out}/{it['name']}-{s}.webp"
        for k in range(3):
            try:
                kw = dict(prompt=p, seed=s, randomize_seed=False, width=it.get('w', 768), height=it.get('h', 1152), num_inference_steps=it.get('steps', req.get('steps', 4)), api_name='/infer')
                if 'guidance' in req: kw['guidance_scale'] = req['guidance']
                r = c.predict(**kw)
                src = r[0] if isinstance(r, (list, tuple)) else r
                ext = os.path.splitext(src)[1] or '.webp'; f = f"{out}/{it['name']}-{s}{ext}"; shutil.copy(src, f); log.append(f'{f} OK'); break
            except Exception as e:
                log.append(f'{f} 失敗{k} {str(e)[:200]}')
                if 'ZeroGPU' in str(e) and TOK:   # 無料の GPU 枠が切れたら、同じ絵の AI を HF の推論の窓口（毎月の無料分）で
                    try:
                        from huggingface_hub import InferenceClient
                        im = InferenceClient(provider='auto', api_key=TOK).text_to_image(p, model=req.get('model', 'black-forest-labs/FLUX.1-schnell'), width=it.get('w', 768), height=it.get('h', 1152), seed=s, num_inference_steps=kw['num_inference_steps'])
                        f = f"{out}/{it['name']}-{s}.png"; im.save(f); log.append(f'{f} OK（推論の窓口）'); break
                    except Exception as e2:
                        log.append(f'{f} 推論の窓口も失敗 {str(e2)[:200]}'); break
                time.sleep(20)
open(f'{out}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
