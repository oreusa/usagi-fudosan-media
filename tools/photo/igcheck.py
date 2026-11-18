#!/usr/bin/env python3
"""インスタ投稿の埋め込みページを開いて、文・日付・写真を取る（合っているか人が見る用）。
使い方: igcheck.py 表.tsv(名前<TAB>p/CODE) 出す先"""
import sys, re, json, os, html, urllib.request
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
def get(u, b=False):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read(3000000)
        return r if b else r.decode('utf-8', 'ignore')
    except Exception as e:
        return b'' if b else ''
res = {}
for i, line in enumerate(open(src, encoding='utf-8')):
    p = line.rstrip('\n').split('\t')
    if len(p) < 2: continue
    name, code = p[0], p[1]
    h = get(f'https://www.instagram.com/{code}/embed/captioned/')
    cap = re.search(r'class="Caption"[^>]*>(.*?)<div class="CaptionComments"', h, re.S)
    cap = re.sub(r'<[^>]+>', ' ', cap.group(1)) if cap else ''
    cap = html.unescape(re.sub(r'\s+', ' ', cap)).strip()[:400]
    im = re.search(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', h) or re.search(r'<img[^>]+class="[^"]*EmbeddedMediaImage[^"]*"[^>]*src="([^"]+)"', h)
    f = ''
    if im:
        b = get(html.unescape(im.group(1)), True)
        if b: f = f'{i:03d}.jpg'; open(os.path.join(out, f), 'wb').write(b)
    acc = re.search(r'class="UsernameText"[^>]*>([^<]+)<', h)
    res[name + ' ' + code] = {'code': code, 'len': len(h), 'acc': acc.group(1) if acc else '', 'cap': cap, 'img': f}
    print(name, code, len(h), bool(cap), f, flush=True)
json.dump(res, open(os.path.join(out, 'out.json'), 'w'), ensure_ascii=False, indent=1)
