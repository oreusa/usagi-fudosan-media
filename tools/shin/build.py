"""新しいHP（11/19 owner「良かった所は持って行って、それ以外は月の頭脳で新しくHP・UI/UXを作り上げて」）。
今の作り（links/index.html に何枚も上から貼る形）とは別に、1から作る新しい土台。
データ：links/index.html のカード（府県・期間・場所・公式URL）＋ links/assets/mihon.json（写真・一言・説明・会場）＋ phh.json（ぼかし色）。
出す物：links/shin/odekake.html（データを中に持つ。見た目と動きは links/shin/shin.css・shin.js）。
python3 tools/shin/build.py"""
import json, os, re, html, hashlib
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
L = os.path.join(R, 'links')
src = open(os.path.join(L, 'index.html'), encoding='utf-8').read()
mh = json.load(open(os.path.join(L, 'assets/mihon.json'), encoding='utf-8'))
phh = json.load(open(os.path.join(L, 'assets/phh.json'), encoding='utf-8'))
opages = {f[:-5] for f in os.listdir(os.path.join(L, 'o')) if f.endswith('.html')}
norm = lambda s: re.sub(r'[\s　・／/「」『』]', '', s or '')
byn = {norm(v['n']): v for v in mh.values()}
byu = {}
for v in mh.values(): byu.setdefault(v['u'], v)
# 種類（カードの絵と同じ決め方＝cardmark.js の R をそのまま使う）
cm = open(os.path.join(L, 'assets/cardmark.js'), encoding='utf-8').read()
icons = dict(re.findall(r"^(\w+):'(<[^']+)',?$", cm[cm.find('var I={'):cm.find('};', cm.find('var I={'))], re.M))
rules = re.findall(r"\[/(.+?)/(i?),'(\w+)'\]", cm[cm.find('var R=['):cm.find('var PCM')])
def kind(t, m):
    for txt in (t, m):
        for pat, fl, k in rules:
            if re.search(pat.replace('\\/', '/'), txt, re.I if fl else 0): return k
    return 'spot'
T = lambda s: html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
items, seen = [], set()
for attrs, body in re.findall(r'<a class="card"([^>]*)>(.*?)</a>', src, re.S):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
    t = T((re.search(r'class="t">(.*?)</div>', body, re.S) or [None, ''])[1])
    m = T((re.search(r'class="m">(.*?)</div>', body, re.S) or [None, ''])[1])
    d = T((re.search(r'class="d">(.*?)</div>', body, re.S) or [None, ''])[1])
    u = html.unescape(a.get('href', ''))
    key = (t, a.get('data-s'))
    if not t or key in seen or not a.get('data-e'): continue
    seen.add(key)
    v = byn.get(norm(t)) or byu.get(u) or {}
    area, _, ven = m.partition('｜')
    it = {'t': t, 'u': u, 'p': a.get('data-pref', ''), 's': a.get('data-s', ''), 'e': a.get('data-e', ''),
          'a': area.strip(), 'v': (v.get('vn') or ven).strip(), 'd': d, 'k': kind(t, m)}
    if a.get('data-tag') == '無料': it['f'] = 1
    for src_k, dst in (('hk', 'hk'), ('ds', 'ds'), ('h', 'h'), ('cr', 'cr'), ('cu', 'cu'), ('im', 'im')):
        if v.get(src_k): it[dst] = v[src_k]
    if v.get('im') and v['im'] in phh: it['th'] = phh[v['im']]
    if v.get('id') in opages: it['o'] = v['id']
    items.append(it)
data = json.dumps({'items': items, 'icons': icons}, ensure_ascii=False, separators=(',', ':'))
ver = lambda f: hashlib.sha1(open(os.path.join(L, 'shin', f), 'rb').read()).hexdigest()[:8]
page = open(os.path.join(R, 'tools/shin/odekake.tpl.html'), encoding='utf-8').read()
page = page.replace('__DATA__', data.replace('</', '<\\/')).replace('__CV__', ver('shin.css')).replace('__JV__', ver('shin.js'))
open(os.path.join(L, 'shin/odekake.html'), 'w', encoding='utf-8').write(page)
print(len(items), 'items', sum('im' in i for i in items), 'photos', len(page) // 1024, 'KB')
