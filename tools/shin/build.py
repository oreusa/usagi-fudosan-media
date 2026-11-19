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
# 11/19 owner「入れ替える」：新しいページは今の URL（/odekake・/fudosan-list・/okaimono）で出す（functions/ が /shin/* を読む）
URL = {'odekake': '/odekake', 'ie': '/fudosan-list', 'kau': '/okaimono'}
REL = [['おでかけ', '/odekake'], ['家と土地', '/fudosan-list'], ['おかいもの', '/okaimono'], ['トップへ', '/']]
SITE = 'https://kansai.townnote.app'

def write(name, title, cfg, data, js=None):
    js = js or name
    cfg['menu']['rel'] = [r for r in REL if r[1] != URL.get(name)]
    desc = cfg.pop('desc', '')
    head = (f'<meta name="description" content="{html.escape(desc)}">' if desc else '') + \
        f'<link rel="canonical" href="{SITE}{URL.get(name, "/shin/" + name)}"><meta property="og:title" content="{html.escape(title.split("｜")[0])}"><meta property="og:image" content="{SITE}/assets/ogp.png"><meta property="og:url" content="{SITE}{URL.get(name, "/shin/" + name)}">'
    page = (TPL.replace('__TITLE__', html.escape(title)).replace('__HEAD__', head).replace('__CFG__', J(cfg)).replace('__DATA__', J(data))
            .replace('__CV__', ver('shin.css')).replace('__JV__', ver('shin.js')).replace('__PAGE__', js).replace('__PV__', ver(js + '.js')))
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
           'menu': {'k': 'Odekake', 'items': [['関西おでかけ', '/odekake', 1], ['イルミネーション', '/illumination'], ['紅葉', '/koyo'], ['いまから行ける', '/ima'], ['泊まり', '/tomari'], ['初詣', '/hatsumode']]},
           'foot': '情報は各公式サイトで確かめてから出かけてください。写真の撮影者は各ページに書いています（ウィキメディア・コモンズ ほか）。<br>券・宿のリンクの一部は広告です。'}
    cfg['desc'] = '大阪・京都・兵庫・奈良・滋賀・和歌山のおでかけ・イベントを、開催中・今週末・まもなく終了に分けて、公式ページつきでまとめています。写真と地図で探せて、毎朝更新しています。'
    write('odekake', '関西おでかけリスト｜開催中・今週末のイベント（大阪・京都・兵庫・奈良・滋賀・和歌山）｜TOWN NOTE', cfg, {'items': items, 'icons': icons, 'map': MAP})

    # ---------- 府県・イルミ・紅葉：同じ形のページ（11/19 owner「全部！」） ----------
    def fin(it, name):
        v = byn.get(norm(name)) or byu.get(it['u']) or {}
        for k in ('hk', 'ds', 'cr', 'cu', 'im'):
            if v.get(k) and k not in it: it[k] = v[k]
        if v.get('h') and 'h' not in it: it['h'] = v['h']
        if it.get('im') and it['im'] in phh: it['th'] = phh[it['im']]
        if v.get('id') in opages: it['o'] = v['id']
        g = gn.get(norm(name)) or gn.get(norm(v.get('n', '')))
        if g and g[0] is not None:
            x, y = proj((g[1], g[0])); it['xy'] = [round(x, 2), round(y, 2)]
        return it
    PFULL = {'大阪': '大阪府', '京都': '京都府', '兵庫': '兵庫県', '奈良': '奈良県', '滋賀': '滋賀県', '和歌山': '和歌山県'}
    SLUG = {'大阪': 'osaka', '京都': 'kyoto', '兵庫': 'hyogo', '奈良': 'nara', '滋賀': 'shiga', '和歌山': 'wakayama'}
    import copy, datetime, sys as _s
    def page(name, url, title, desc, page, its, cur):
        c = copy.deepcopy(cfg); c['desc'] = desc
        c['menu']['items'] = [[t, u] + ([1] if u == cur else []) for t, u, *_ in c['menu']['items']]
        URL[name] = url
        write(name, title, c, {'items': its, 'icons': icons, 'map': MAP, 'page': page}, 'odekake')
    for p_ in SLUG:
        n = sum(1 for i in items if i['p'] == p_)
        page('odekake-' + SLUG[p_], '/odekake-' + SLUG[p_], f'{p_}のおでかけ・イベント（{PFULL[p_]}）｜開催中・今週末｜TOWN NOTE',
             f'{PFULL[p_]}のおでかけ・イベントを、開催中・今週末・まもなく終了に分けて、公式ページつきでまとめています。写真と地図で探せて、毎朝更新しています。',
             {'h1': f'{p_}のおでかけ・イベント', 'sub': f'{PFULL[p_]}・{n}件', 'p': p_}, items, '/odekake')
    _s.path.insert(0, os.path.join(R, 'tools/illumi'))
    from data import ITEMS as IL, KOYO as KY, MEISHO as MS
    TD = datetime.date.today().isoformat()
    il = []
    for row in IL:
        p_, n, m, s_, e_, free, url = row[:7]
        if not s_: continue
        e_ = e_ or '2027-03-31'
        if e_ < TD: continue
        city, _, ven = m.partition('｜')
        il.append(fin({'t': n, 'u': url, 'p': p_, 's': s_, 'e': e_, 'a': city, 'v': ven, 'k': 'light', **({'f': 1} if free else {})}, n))
    ky = []
    for row in KY:
        p_, n, m, s_, e_, od, hrs, fee, url = row[:9]
        if not s_: continue
        e_ = e_ or s_
        if e_ < TD: continue
        city, _, ven = m.partition('｜')
        it = {'t': n, 'u': url, 'p': p_, 's': s_, 'e': e_, 'a': city, 'v': ven, 'k': 'koyo', 'h': hrs}
        if fee: it['fe'] = fee
        if fee and fee.startswith('無料'): it['f'] = 1
        ky.append(fin(it, n))
    def prange(t):
        mm = re.findall(r'(\d+)月(上旬|初旬|中旬|下旬|末)', t)
        if not mm: return None
        today = datetime.date.today()
        def d(mo, k, end):
            mo = int(mo); y = today.year if mo >= 6 or today.month < 6 else today.year + 1
            a, b = {'上旬': (1, 10), '初旬': (1, 10), '中旬': (11, 20), '下旬': (21, 0), '末': (21, 0)}[k]
            if end and b == 0: return datetime.date(y + mo // 12, mo % 12 + 1, 1) - datetime.timedelta(days=1)
            return datetime.date(y, mo, b if end else a)
        return d(*mm[0], False), d(*mm[-1], True)
    for p_, n, city, peak, fee, url, note in MS:
        r = prange(peak)
        if not r or r[1].isoformat() < TD: continue
        it = {'t': n, 'u': url, 'p': p_, 's': r[0].isoformat(), 'e': r[1].isoformat(), 'a': city, 'v': '', 'k': 'koyo', 'pk': peak}
        if fee: it['fe'] = fee
        if fee.startswith('無料') or not fee: it['f'] = 1 if fee.startswith('無料') else it.get('f', 0)
        if note: it['hk'] = note
        if not it.get('f'): it.pop('f', None)
        ky.append(fin(it, n))
    print('illumination', len(il), 'photos', sum('im' in i for i in il), '/ koyo', len(ky), 'photos', sum('im' in i for i in ky))
    page('illumination', '/illumination', '関西イルミネーション2026-2027｜開催中・無料・今週末（大阪・京都・兵庫・奈良・滋賀・和歌山）｜TOWN NOTE',
         f'関西のイルミネーション{len(il)}か所を、開催中・これから・無料に分けて、公式ページつきでまとめています。地図と写真で探せて、毎朝更新しています。',
         {'h1': '関西のイルミネーション', 'sub': f'2026-2027・{len(il)}か所', 'st': 'pref'}, il, '/illumination')
    page('illumination-muryo', '/illumination-muryo', '関西の無料イルミネーション2026-2027｜TOWN NOTE',
         '関西の無料で見られるイルミネーションを、開催中・これからに分けてまとめています。',
         {'h1': '関西の無料イルミネーション', 'sub': f'2026-2027・{sum(1 for i in il if i.get("f"))}か所', 'st': 'pref', 'free': 1}, il, '/illumination')
    page('koyo', '/koyo', '関西の紅葉2026｜見頃とライトアップ（大阪・京都・兵庫・奈良・滋賀・和歌山）｜TOWN NOTE',
         f'関西の紅葉の名所と夜のライトアップ{len(ky)}か所を、見頃の時期・料金・時間つきでまとめています。地図と写真で探せて、毎朝更新しています。',
         {'h1': '関西の紅葉', 'sub': f'見頃とライトアップ・{len(ky)}か所', 'st': 'pref'}, ky, '/koyo')
    for p_ in SLUG:
        ni = sum(1 for i in il if i['p'] == p_); nk = sum(1 for i in ky if i['p'] == p_)
        page('illumination-' + SLUG[p_], '/illumination-' + SLUG[p_], f'{p_}のイルミネーション2026-2027（{PFULL[p_]}）｜TOWN NOTE',
             f'{PFULL[p_]}のイルミネーション{ni}か所を、開催中・これから・無料に分けてまとめています。', {'h1': f'{p_}のイルミネーション', 'sub': f'2026-2027・{ni}か所', 'p': p_, 'st': 'pref'}, il, '/illumination')
        page('koyo-' + SLUG[p_], '/koyo-' + SLUG[p_], f'{p_}の紅葉2026｜見頃とライトアップ（{PFULL[p_]}）｜TOWN NOTE',
             f'{PFULL[p_]}の紅葉の名所とライトアップ{nk}か所を、見頃の時期つきでまとめています。', {'h1': f'{p_}の紅葉', 'sub': f'見頃とライトアップ・{nk}か所', 'p': p_, 'st': 'pref'}, ky, '/koyo')
    # ---------- 初詣・泊まり・いまから・開店閉店・ランキング（links/shin/list.js） ----------
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location('lists', os.path.join(R, 'tools/shin/lists.py')); _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
    global LISTS; LISTS = _m
    _m.build(write, URL, L, R, cfg, items, il, ky, fin, icons, norm, MAP)

odekake()
if os.path.exists(os.path.join(L, 'shin/ie.js')):
    import importlib.util
    sp = importlib.util.spec_from_file_location('ie', os.path.join(R, 'tools/shin/ie.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    m.build(write, MAP, L, R)
if os.path.exists(os.path.join(L, 'shin/kau.js')):
    sp = importlib.util.spec_from_file_location('kau', os.path.join(R, 'tools/shin/kau.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    m.build(write, L, R)
# 11/19 23時 owner「その他も本気でやり直せ」：売る前に・いくら？ など読む・入れるページ（tools/shin/docs.py・links/shin/doc.js）
if os.path.exists(os.path.join(L, 'shin/doc.js')):
    sp = importlib.util.spec_from_file_location('docs', os.path.join(R, 'tools/shin/docs.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    m.build(write, L, R, URL)
LISTS.COVER()

# ---------- 今までのページにかぶせる見た目（links/shin/skin.css）：shin.css の 頭・下のバー・MENU・夜空 を .sk の中だけに効く形にして＋skin.tail.css ----------
def skin():
    src = re.sub(r'/\*.*?\*/', '', open(os.path.join(L, 'shin', 'shin.css'), encoding='utf-8').read(), flags=re.S)
    KEYS = ('.top', '.brand', '.tg', '.nav', '#nav', '.mn', '.mu', '#tb', '.tw', '.shoot', '#stars', '#sky', '#logo', '.vtt', 'view-transition')
    BAD = ('.tw h2', '.tw .acts', '.vn .mn', '#sky .a', '#sky .gr', '#sky .fade', '#sky .au')
    def blocks(t):
        out, i, n = [], 0, len(t)
        while i < n:
            j = t.find('{', i)
            if j < 0: break
            sel = t[i:j].strip(); d, k = 1, j + 1
            while d and k < n:
                d += {'{': 1, '}': -1}.get(t[k], 0); k += 1
            out.append((sel, t[j + 1:k - 1])); i = k
        return out
    def scope(sel):
        r = []
        for x in sel.split(','):
            x = x.strip()
            if x.startswith('::view-transition') or x.startswith('html.vtt') or x.startswith('html.tbon'):
                r.append(x); continue
            m = re.match(r'(html(?:\.nt|:not\(\.nt\))?)\s+(.*)', x)
            r.append((m.group(1) + ' .skc ' + m.group(2)) if m else '.skc ' + x)
        return ','.join(r)
    def take(sel):
        return any(k in sel for k in KEYS) and not any(b in sel for b in BAD)
    css, used, kf = [], set(), {}
    for sel, body in blocks(src):
        if sel.startswith('@keyframes'):
            kf[sel.split()[1]] = '%s{%s}' % (sel, body); continue
        if sel.startswith('@media') or sel.startswith('@supports'):
            inner = [(a, b) for a, b in blocks(body) if take(a)]
            if inner: css.append(sel + '{' + ''.join(scope(a) + '{' + b + '}' for a, b in inner) + '}')
            for a, b in inner: used.update(re.findall(r'animation(?:-name)?:\s*([\w-]+)', b))
            continue
        if sel in (':root', 'html.nt', 'html'):
            v = ';'.join(d.strip() for d in body.split(';') if d.strip().startswith('--'))
            if v: css.append(('html.nt .skc' if sel == 'html.nt' else '.skc') + '{' + v + '}')
            continue
        if take(sel):
            css.append(scope(sel) + '{' + body + '}'); used.update(re.findall(r'animation(?:-name)?:\s*([\w-]+)', body))
    css += [kf[k] for k in sorted(used) if k in kf]
    tail = open(os.path.join(R, 'tools/shin/skin.tail.css'), encoding='utf-8').read()
    open(os.path.join(L, 'shin', 'skin.css'), 'w', encoding='utf-8').write('/* 作り：tools/shin/build.py skin()。直す時は shin.css か tools/shin/skin.tail.css を直す */\n' + '\n'.join(css) + '\n' + tail)
    print('skin.css', len(css), 'rules')
skin()
# 11/19 functions が上限で止まっても新しい形が出るように（bake.py）
import importlib.util as _iu
_s = _iu.spec_from_file_location('bake', os.path.join(R, 'tools/shin/bake.py')); _b = _iu.module_from_spec(_s); _s.loader.exec_module(_b); _b.main(L)
