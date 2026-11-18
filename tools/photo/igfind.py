#!/usr/bin/env python3
"""公式ページの中から、主催者のインスタ投稿・アカウントを探す（埋め込み用）。
使い方: igfind.py 表.tsv(名前<TAB>公式URL) 出す先フォルダ → out.json"""
import sys, re, json, os, urllib.request, urllib.parse
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile Safari/604.1'}
POST = re.compile(r'instagram\.com/(?:[A-Za-z0-9_.]+/)?(p|reel)/([A-Za-z0-9_-]{6,})')
ACC = re.compile(r'instagram\.com/([A-Za-z0-9_.]{2,30})/?["\'?#]')
BAD = {'p','reel','explore','accounts','about','developer','legal','share','tv','stories','sharer','intent'}
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
        return r.read(1500000).decode('utf-8', 'ignore'), r.geturl()
    except Exception as e:
        return '', ''
res = {}
for line in open(src, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 2 or not p[1].startswith('http'): continue
    name, url = p[0], p[1]
    h, fin = get(url)
    posts = []; [posts.append(m.group(1)+'/'+m.group(2)) for m in POST.finditer(h) if m.group(1)+'/'+m.group(2) not in posts]
    accs = []
    for m in ACC.finditer(h):
        a = m.group(1)
        if a.lower() not in BAD and a not in accs: accs.append(a)
    # 公式の一つ上（トップ）にもアカウントが書かれていることが多い
    if not accs and h:
        top = urllib.parse.urljoin(fin or url, '/')
        if top != url:
            h2, _ = get(top)
            for m in ACC.finditer(h2):
                a = m.group(1)
                if a.lower() not in BAD and a not in accs: accs.append(a)
            for m in POST.finditer(h2):
                k = m.group(1)+'/'+m.group(2)
                if k not in posts: posts.append(k)
    res[name] = {'u': url, 'ok': bool(h), 'posts': posts[:6], 'acc': accs[:3]}
    print(name, len(posts), accs[:2], flush=True)
json.dump(res, open(os.path.join(out, 'out.json'), 'w'), ensure_ascii=False, indent=1)
print('done', len(res), sum(1 for v in res.values() if v['posts']), 'with posts', sum(1 for v in res.values() if v['acc']), 'with acc')
