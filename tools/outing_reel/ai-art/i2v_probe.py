"""写真から動画を作るAI（Hugging Face の無料の窓口）で5秒の動画ができるか試す。鍵ありと鍵なしの両方。"""
import json, os, shutil, sys, traceback
from gradio_client import Client, handle_file
out = sys.argv[1]; img = sys.argv[2]; os.makedirs(out, exist_ok=True); log = []
TOK = (os.environ.get('HF_TOKEN') or '').strip() or None
P = "slow smooth cinematic dolly forward up the stone stairs, red maple leaves gently falling, sunlight rays flickering through leaves, realistic, no people"
SPACES = ['zerogpu-aoti/wan2-2-fp8da-aoti-faster', 'Lightricks/ltx-video-distilled', 'multimodalart/wan2-1-fast']
for sp in SPACES:
    for tok in (None, TOK):
        tag = sp.split('/')[-1] + ('-tok' if tok else '-anon')
        try:
            c = Client(sp, token=tok)
            api = c.view_api(return_format='dict', print_info=False)
            eps = list((api.get('named_endpoints') or {}).keys()); log.append(f'{tag} endpoints {eps}')
            for ep, d in (api.get('named_endpoints') or {}).items():
                log.append(f'  {ep} params ' + json.dumps([(p.get("parameter_name"), p.get("python_type", {}).get("type"), p.get("parameter_default")) for p in d.get('parameters', [])], ensure_ascii=False)[:900])
        except Exception as e:
            log.append(f'{tag} 接続失敗 {str(e)[:200]}'); continue
        # よくある名前で呼んでみる
        tried = False
        for ep, d in (api.get('named_endpoints') or {}).items():
            names = [p.get('parameter_name') for p in d.get('parameters', [])]
            if not any(n and 'image' in n for n in names) or not any(n and 'prompt' in n for n in names): continue
            kw = {}
            for p in d.get('parameters', []):
                n = p.get('parameter_name')
                if n is None: continue
                if 'image' in n and 'input' in n or n in ('image', 'input_image', 'image_in'): kw[n] = handle_file(img)
                elif n in ('prompt', 'prompt_input', 'text_prompt'): kw[n] = P
            try:
                tried = True; r = c.predict(api_name=ep, **kw)
                log.append(f'{tag} {ep} 結果 {str(r)[:300]}')
                src = r[0] if isinstance(r, (list, tuple)) else r
                if isinstance(src, dict): src = src.get('video') or src.get('path') or src.get('value')
                if isinstance(src, dict): src = src.get('path')
                if src and os.path.exists(src): shutil.copy(src, f'{out}/{tag}.mp4'); log.append(f'{tag} OK 動画')
                break
            except Exception as e:
                log.append(f'{tag} {ep} 失敗 {str(e)[:300]}'); break
        if not tried: log.append(f'{tag} 呼べる窓口が見つからない')
        if os.path.exists(f'{out}/{tag}.mp4'): break
open(f'{out}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
