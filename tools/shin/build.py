"""新しいHP（11/19 owner「良かった所は持って行って、それ以外は月の頭脳で新しくHP・UI/UXを作り上げて」）。
今の作り（links/index.html に何枚も上から貼る形）とは別に、1から作る新しい土台。URL は /shin/〜。
共通の土台＝links/shin/shin.css・shin.js（空・頭・下のバー・MENU・板）。ページの中身＝links/shin/<page>.js。
python3 tools/shin/build.py"""
import json, os, re, html, hashlib, csv
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
L = os.path.join(R, 'links')
TPL = open(os.path.join(R, 'tools/shin/page.tpl.html'), encoding='utf-8').read()
ver = lambda f: hashlib.sha1(open(os.path.join(L, 'shin', f), 'rb').read()).hexdigest()[:8]
J = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
REL = [['おでかけ', '/shin/odekake'], ['家と土地', '/shin/ie'], ['おかいもの', '/okaimono'], ['トップへ', '/']]

def write(name, title, cfg, data):
    cfg['menu']['rel'] = [r for r in REL if r[1] != '/shin/' + name]
    page = (TPL.replace('__TITLE__', title).replace('__CFG__', J(cfg)).replace('__DATA__', J(data))
            .replace('__CV__', ver('shin.css')).replace('__JV__', ver('shin.js')).replace('__PAGE__', name).replace('__PV__', ver(name + '.js')))
    open(os.path.join(L, 'shin', name + '.html'), 'w', encoding='utf-8').write(page)
    print(name, len(page) // 1024, 'KB')

# ---------- 地図の形（府県・まわりの県） ----------
def proj(c): return ((c[0] - 134) * 82.2, (36 - c[1]) * 100)
def path(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    out = []
    for poly in polys:
        for ring in poly:
            s, last = [], None
            for c in ring:
                x, y = proj(c); p = (round(x, 1), round(y, 1))
                if p != last: s.append(p); last = p
            if len(s) >= 4: out.append('M' + 'L'.join(f'{x:g} {y:g}' for x, y in s) + 'Z')
    return ''.join(out)
kj = json.load(open(os.path.join(L, 'townnotes/kansai.json'), encoding='utf-8'))
MAP = {'pref': {f['properties']['p']: path(f['geometry']) for f in kj['pref']['features']},
       'nb': [path(f['geometry']) for f in kj['nb']['features']]}

# ---------- おでかけ ----------
def odekake():
    src = open(os.path.join(L, 'index.html'), encoding='utf-8').read()
    mh = json.load(open(os.path.join(L, 'assets/mihon.json'), encoding='utf-8'))
    phh = json.load(open(os.path.join(L, 'assets/phh.json'), encoding='utf-8'))
    geo = json.load(open(os.path.join(L, 'townnotes/geo.json'), encoding='utf-8'))
    opages = {f[:-5] for f in os.listdir(os.path.join(L, 'o')) if f.endswith('.html')}
    norm = lambda s: re.sub(r'[\s　・／/「」『』]', '', s or '')
    byn = {norm(v['n']): v for v in mh.values()}
    byu = {}
    for v in mh.values(): byu.setdefault(v['u'], v)
    gn = {norm(k): v for k, v in geo.items()}
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
        u = html.unescape(a.get('href', ''))
        key = (t, a.get('data-s'))
        if not t or key in seen or not a.get('data-e'): continue
        seen.add(key)
        v = byn.get(norm(t)) or byu.get(u) or {}
        area, _, ven = m.partition('｜')
        it = {'t': t, 'u': u, 'p': a.get('data-pref', ''), 's': a.get('data-s', ''), 'e': a.get('data-e', ''),
              'a': area.strip(), 'v': (v.get('vn') or ven).strip(), 'k': kind(t, m)}
        if a.get('data-tag') == '無料': it['f'] = 1
        for k in ('hk', 'ds', 'h', 'cr', 'cu', 'im'):
            if v.get(k): it[k] = v[k]
        if v.get('im') and v['im'] in phh: it['th'] = phh[v['im']]
        if v.get('id') in opages: it['o'] = v['id']
        g = gn.get(norm(t)) or gn.get(norm(v.get('n', '')))
        if g and g[0] is not None:
            x, y = proj((g[1], g[0])); it['xy'] = [round(x, 2), round(y, 2)]
        items.append(it)
    print('odekake items', len(items), 'photos', sum('im' in i for i in items), 'map', sum('xy' in i for i in items))
    cfg = {'nav': [{'t': '開催中', 'ic': 'now', 'a': 'now'}, {'t': '今週末', 'ic': 'we', 'a': 'we'}, {'t': '地図', 'ic': 'map', 'a': 'map'}, {'t': '泊まり', 'ic': 'inn', 'href': '/tomari'}],
           'menu': {'k': 'Odekake', 'items': [['関西おでかけ', '/shin/odekake', 1], ['イルミネーション', '/illumination'], ['紅葉', '/koyo'], ['いまから行ける', '/ima'], ['泊まり', '/tomari'], ['初詣', '/hatsumode']]},
           'foot': '情報は各公式サイトで確かめてから出かけてください。写真の撮影者は各ページに書いています（ウィキメディア・コモンズ ほか）。<br>券・宿のリンクの一部は広告です。'}
    write('odekake', '関西おでかけ｜TOWN NOTE', cfg, {'items': items, 'icons': icons, 'map': MAP})

odekake()
if os.path.exists(os.path.join(L, 'shin/ie.js')):
    import importlib.util
    sp = importlib.util.spec_from_file_location('ie', os.path.join(R, 'tools/shin/ie.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    m.build(write, MAP, L, R)
