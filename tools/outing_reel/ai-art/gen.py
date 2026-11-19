"""絵本のページの絵を画像AIで描く（11/19 owner「絵だけ画像AIで描く」）。GitHub の仕組みの中で動かす（作業場からは画像AIにつなげない）。
req.json の各絵を、seed を変えて何枚か描き、out/ に置く。"""
import json, os, sys, time, urllib.parse, urllib.request
req = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
style = req['style']; log = []
for it in req['items']:
    for s in it.get('seeds', [1, 2, 3]):
        p = f"{it['prompt']}, {style}"
        q = urllib.parse.urlencode({'width': it.get('w', 920), 'height': it.get('h', 1380), 'seed': s, 'model': req.get('model', 'flux'), 'nologo': 'true', 'enhance': 'false'})
        url = 'https://image.pollinations.ai/prompt/' + urllib.parse.quote(p) + '?' + q
        f = f"{out}/{it['name']}-{s}.jpg"
        for k in range(4):
            try:
                r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'ehon-art'}), timeout=180)
                b = r.read(); open(f, 'wb').write(b); log.append(f'{f} {len(b)} {r.headers.get("content-type")}'); break
            except Exception as e:
                log.append(f'{f} 失敗{k} {e}'); time.sleep(12)
        time.sleep(4)
open(f'{out}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
