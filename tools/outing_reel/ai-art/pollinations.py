"""画像AI（FLUX）を公開の無料の窓口 pollinations で呼ぶ（11/20 HF の無料枠が切れた時の代わり）。req.json の形は gen.py と同じ。"""
import json, os, sys, time, urllib.parse, urllib.request
d = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); log = []
for it in d['items']:
    for s in it.get('seeds', [1]):
        u = 'https://image.pollinations.ai/prompt/' + urllib.parse.quote(it['prompt'] + '. ' + d['style']) + f"?width={it.get('w',768)}&height={it.get('h',1152)}&seed={s}&nologo=true&model=flux"
        for k in range(3):
            try:
                b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'townnote-reel'}), timeout=240).read()
                f = f"{out}/{it['name']}-{s}.jpg"; open(f, 'wb').write(b); log.append(f'{f} OK {len(b)}'); break
            except Exception as e:
                log.append(f"{it['name']}-{s} 失敗{k} {str(e)[:160]}"); time.sleep(15)
open(f'{out}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
