"""新しいHP（11/19 owner「良かった所は持って行って、それ以外は月の頭脳で新しくHP・UI/UXを作り上げて」）。
今の作り（links/index.html に何枚も上から貼る形）とは別に、1から作る新しい土台。URL は /shin/〜。
共通の土台＝links/shin/shin.css・shin.js（空・頭・下のバー・MENU・板）。ページの中身＝links/shin/<page>.js。
python3 tools/shin/build.py"""
import json, os, re, html, hashlib, csv, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
L = os.path.join(R, 'links')
TPL = open(os.path.join(R, 'tools/shin/page.tpl.html'), encoding='utf-8').read()
sys.path.insert(0, os.path.join(R, 'tools/shin'))
from ix import ix_html as IX, pre_html as PRE
ver = lambda f: hashlib.sha1(open(os.path.join(L, 'shin', f), 'rb').read()).hexdigest()[:8]
J = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
# 11/19 owner「入れ替える」：新しいページは今の URL（/odekake・/fudosan-list・/okaimono）で出す（functions/ が /shin/* を読む）
URL = {'odekake': '/odekake', 'ie': '/fudosan-list', 'kau': '/okaimono'}
REL = [['おでかけ', '/odekake'], ['家と土地', '/fudosan-list'], ['おかいもの', '/okaimono'], ['開店・閉店', '/kaiten'], ['トップへ', '/']]
SEC = {'Odekake': '/odekake', 'Home & Land': '/fudosan-list', 'Shopping': '/okaimono', 'New Shops': '/kaiten'}
SITE = 'https://kansai.townnote.app'
# 11/20 今週末のおすすめに出してよい写真（月が目で選んだ・行きたくなる写真だけ）
PHOK = set(json.load(open(os.path.join(R, 'tools/shin/photo_ok.json'), encoding='utf-8'))['ok'])
PHHR = set(json.load(open(os.path.join(R, 'tools/shin/photo_ok.json'), encoding='utf-8')).get('hero', []))
# 11/20 owner「出来上がったあとに本気で確認して改善」：イルミのページに昼の建物、紅葉のページに夏の緑の写真が先に出ていた。
# 写真ごとに 明るさ・赤や橙の多さ・緑の多さ を量って（tools/shin/photo_m.json に残す）、ページに合う写真を先に出す
_PMF = os.path.join(R, 'tools/shin/photo_m.json')
try: _PM = json.load(open(_PMF, encoding='utf-8'))
except Exception: _PM = {}
# 11/20 暗い昼の写真（木陰の寺など）を「夜の写真」と取り違えていた → 暗い所の割合・上の方（空）の暗さ・青空の割合も量る
def NIGHT(px):
    lum = [0.299*r + 0.587*g + 0.114*b for r, g, b in px]; top = lum[:64*12]
    return [round(sum(v < 35 for v in lum)/len(lum), 2), round(sum(v < 40 for v in top)/len(top), 2),
            round(sum(1 for r, g, b in px[:64*12] if b > r + 15 and b > 110)/len(top), 2)]
def IS_NIGHT(m):
    return (m[4] >= .5 or (m[5] >= .35 and m[6] < .2)) if len(m) > 6 else m[0] < 75
def PHM(f):
    if f in _PM and len(_PM[f]) > 6: return _PM[f]
    try:
        import colorsys
        from PIL import Image
        im = Image.open(os.path.join(L, 'assets/ph', f)).convert('RGB').resize((64, 48)); px = list(im.getdata())
        lum = sum(0.299*r + 0.587*g + 0.114*b for r, g, b in px) / len(px); w = gr = 0
        for r, g, b in px:
            h, sa, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            if sa > .35 and v > .25 and (h < .11 or h > .95): w += 1
            if sa > .25 and v > .2 and .17 < h < .45: gr += 1
        _PM[f] = [round(lum), round(w/len(px), 2), round(gr/len(px), 2), Image.open(os.path.join(L, 'assets/ph', f)).size[0]]
        _PM[f] += NIGHT(px)
        json.dump(_PM, open(_PMF, 'w', encoding='utf-8'))
        return _PM[f]
    except Exception:
        return _PM.get(f)
# 11/21 owner「HPもっと綺麗に見せたい」：表（今週の顔・ストーリーの丸）には一番きれいな写真を出す。
# 写真ごとの見た目の点（色の鮮やかさ・くっきり・明るさ・くもり空）を tools/photo/best.py の visual_im で量り tools/shin/photo_b.json に残す
_PBF = os.path.join(R, 'tools/shin/photo_b.json')
try: _PB = json.load(open(_PBF, encoding='utf-8'))
except Exception: _PB = {}
def PHB(f):
    if f in _PB: return _PB[f]
    try:
        import sys; sys.path.insert(0, os.path.join(R, 'tools/photo'))
        from best import visual_im
        from PIL import Image
        _PB[f] = visual_im(Image.open(os.path.join(L, 'assets/ph', f)))[0]
        json.dump(_PB, open(_PBF, 'w', encoding='utf-8'))
    except Exception:
        _PB[f] = 0
    return _PB[f]
def FIT(it, kind):
    """ok：2＝このページに合う写真、1＝目で選んだ写真、-1＝合わない（後ろへ）"""
    it = dict(it); m = PHM(it['im']) if it.get('im') else None
    if not m: return it
    lum, warm, green = m[:3]
    if kind == 'illumination':
        it['ok'] = 2 if IS_NIGHT(m) else -1
    elif kind == 'koyo':
        it['ok'] = 2 if warm >= .2 else (-1 if green >= .3 and warm < .1 else (1 if it.get('ok') else 0))
    if not it.get('ok'): it.pop('ok', None)
    return it
# 11/20 人気順：この30日に押された数（カード）＋♡の数×3。毎朝 link-stats が数え直す
try: _LT = json.load(open(os.path.join(R, 'stats/link-30.json'), encoding='utf-8'))['total']
except Exception: _LT = {}
def POP(t):
    n = 0
    for k, v in _LT.items():
        tail = k.split('｜')[-1]
        if k.startswith('♡：'): tail = k[2:]
        if len(tail) >= 4 and t[:len(tail)] == tail and (k.startswith('クリック') or k.startswith('♡：')):
            n += v * (3 if k.startswith('♡：') else 1)
    return n

# 11/20 owner「統一されてない・整理されてない」：MENU の項目と並び順は分野ごとにここ1か所だけ（skin.js の FUD・ODE・OKA・KAI も同じ順）
MENUS = {
    'Odekake': [['関西おでかけ', '/odekake'], ['イルミネーション', '/illumination'], ['紅葉', '/koyo'], ['いまから行ける', '/ima'], ['泊まり', '/tomari'], ['初詣', '/hatsumode']],
    'Home & Land': [['家と土地の相場', '/fudosan-list'], ['地価ランキング', '/chika-kansai'], ['まちランキング', '/ranking'], ['家を売る前に', '/uru'], ['いくらで売れる？', '/ikura'], ['実家・空き家', '/jikka/'], ['解体の費用と補助金', '/kaitai']],
    'Shopping': [['日用品の値段くらべ', '/okaimono'], ['本当に安い？', '/nesage'], ['お得な物', '/otoku'], ['ふるさと納税', '/furusato']],
    'New Shops': [['関西の開店・閉店', '/kaiten']],
}

def write(name, title, cfg, data, js=None):
    js = js or name
    m = cfg['menu']
    if m.get('k') in MENUS:
        cur = next((x[1] for x in m['items'] if len(x) > 2 and x[2]), None)
        m['items'] = [[t, u] + ([1] if u == cur else []) for t, u in MENUS[m['k']]]
    # 11/20 表紙の MENU は分野の入口そのものなので、下の重なるボタンは出さない
    # MENU の下のボタンは「ほかの分野＋トップへ」をどのページでも同じ順で（自分の分野は出さない）
    cfg['menu']['rel'] = [] if name.startswith('cover') else [r for r in REL if r[1] != SEC.get(m.get('k'), URL.get(name))]
    desc = cfg.pop('desc', '')
    head = (f'<meta name="description" content="{html.escape(desc)}">' if desc else '') + \
        f'<link rel="canonical" href="{SITE}{URL.get(name, "/shin/" + name)}"><meta property="og:title" content="{html.escape(title.split("｜")[0])}"><meta property="og:image" content="{SITE}/assets/ogp.png"><meta property="og:url" content="{SITE}{URL.get(name, "/shin/" + name)}">'
    page = (TPL.replace('__TITLE__', html.escape(title)).replace('__HEAD__', head).replace('__CFG__', J(cfg)).replace('__DATA__', J(data))
            .replace('__CV__', ver('shin.css')).replace('__JV__', ver('shin.js')).replace('__PAGE__', js).replace('__PV__', ver(js + '.js')))
    # 11/20 検索の機械にも中身とリンクが見えるように、ページの下の「一覧」を HTML のまま（tools/shin/ix.py）
    page = page.replace('<div id="app"></div>', '<div id="app">' + PRE(data) + '</div>' + IX(name, data, L), 1)
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
        if v.get('im') in PHOK: it['ok'] = 1
        if v.get('im'): it['vb'] = PHB(v['im'])
        if v.get('im') and PHM(v['im']) and IS_NIGHT(PHM(v['im'])): it['nt'] = 1
        if v.get('im') and (PHM(v['im']) or [0, 0])[1] >= .2: it['wm'] = 1
        if v.get('im') in PHHR: it['hr'] = 1
        if v.get('im') and (PHM(v['im']) or [0, 0, 0, 9999])[3] < 900: it['lo'] = 1
        if POP(t): it['pp'] = POP(t)
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
        if it.get('im') in PHOK: it['ok'] = 1
        if it.get('im'): it['vb'] = PHB(it['im'])
        if it.get('im') and PHM(it['im']) and IS_NIGHT(PHM(it['im'])): it['nt'] = 1
        if it.get('im') and (PHM(it['im']) or [0, 0])[1] >= .2: it['wm'] = 1
        if it.get('im') in PHHR: it['hr'] = 1
        if it.get('im') and (PHM(it['im']) or [0, 0, 0, 9999])[3] < 900: it['lo'] = 1
        if POP(name): it['pp'] = POP(name)
        if v.get('id') in opages: it['o'] = v['id']
        g = gn.get(norm(name)) or gn.get(norm(v.get('n', '')))
        if not g:
            # 11/20 名所（永観堂（禅林寺）・東福寺 など）は名前が地図の場所の名前と少し違って地図に出ていなかった
            #  →（）の中を外した名前・同じ府県で その名前から始まる場所（例：永観堂 秋の寺宝展 夜間拝観）を使う。2つ以上の場所に当たる時は使わない
            base_ = norm(re.sub(r'[（(].*?[）)]', '', name))
            if len(base_) >= 2:
                hit = {tuple(vv[:2]) for kk, vv in gn.items() if kk.startswith(base_) and vv and vv[0] is not None}
                if len(hit) == 1: g = list(next(iter(hit)))
        if g and g[0] is not None:
            x, y = proj((g[1], g[0])); it['xy'] = [round(x, 2), round(y, 2)]
        return it
    PFULL = {'大阪': '大阪府', '京都': '京都府', '兵庫': '兵庫県', '奈良': '奈良県', '滋賀': '滋賀県', '和歌山': '和歌山県'}
    SLUG = {'大阪': 'osaka', '京都': 'kyoto', '兵庫': 'hyogo', '奈良': 'nara', '滋賀': 'shiga', '和歌山': 'wakayama'}
    import copy, datetime, sys as _s
    def page(name, url, title, desc, page, its, cur):
        if name.startswith(('illumination', 'koyo')): its = [FIT(x, 'koyo' if name.startswith('koyo') else 'illumination') for x in its]
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
    try:  # 11/20 おかいものの値段が取れなくても、ほかのページと bake（頭とバー・新しい見た目）は必ず最後まで作る
        m.build(write, L, R)
    except Exception as e:
        print('kau: 作り直さず前の物のまま', e)
# 11/19 23時 owner「その他も本気でやり直せ」：売る前に・いくら？ など読む・入れるページ（tools/shin/docs.py・links/shin/doc.js）
if os.path.exists(os.path.join(L, 'shin/doc.js')):
    sp = importlib.util.spec_from_file_location('docs', os.path.join(R, 'tools/shin/docs.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    m.build(write, L, R, URL)
    # 11/23 owner「全部やり変えて」：地価ランキング（tools/shin/chika.py・links/shin/rk.js。関東と同じ）
    try:
        sp2 = importlib.util.spec_from_file_location('chika', os.path.join(R, 'tools/shin/chika.py')); m2 = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(m2)
        m2.build(write, L, R, URL, m.cfg)
    except Exception as e:
        print('chika: 作り直さず前の物のまま', repr(e))
    # 11/23 前のページを新しい土台で作り直す（tools/shin/yari.py。関東と同じ）
    sp3 = importlib.util.spec_from_file_location('yari', os.path.join(R, 'tools/shin/yari.py')); Y = importlib.util.module_from_spec(sp3); sp3.loader.exec_module(Y)
    for _nm, _fn in [('sagasu', lambda: Y.sagasu(os.path.join(L, 'sagasu.html'), [['家と土地の相場', '/fudosan-list', '街ごとの売れた値段'], ['地価ランキング', '/chika-kansai', '住宅地の1年の動き'], ['まちランキング', '/ranking', '駅・人口の順位も'], ['実家・空き家', '/jikka/', '売る・片付ける前に']]))]:
        try:
            _d = _fn()
            if not _d: continue
            URL[_nm] = '/' + _nm
            write(_nm, {'sagasu': 'その予算で、どの街に住める？｜関西205の街を実際に売れた値段で｜TOWN NOTE'}[_nm], dict(m.cfg('/' + _nm, {'sagasu': '関西205の市区町村を、中古マンション・一戸建て・土地の実際に売れた値段（近畿レインズ）で予算から選べます。'}[_nm])), _d, js={'sagasu': 'sg'}[_nm])
        except Exception as e:
            print(_nm + ': 作り直さず前の物のまま', repr(e))
# 11/19 ふるさと納税・値下がり（燈のデータ）を新しい土台で
try:
    _sf = __import__('importlib.util').util.spec_from_file_location('furu', os.path.join(R, 'tools/shin/furu.py')); _mf = __import__('importlib.util').util.module_from_spec(_sf); _sf.loader.exec_module(_mf); _mf.build(write, URL)
except Exception as e:
    print('furu: 読み込めなかった', repr(e))
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
            m = re.match(r'(html(?:\.nt|\.iro|:not\(\.nt\))*(?:\[[^\]]*\])?)\s+(.*)', x)
            r.append((m.group(1) + ' .skc ' + m.group(2)) if m else '.skc ' + x)
        return ','.join(r)
    def take(sel):
        return any(k in sel for k in KEYS) and not any(b in sel for b in BAD)
    css, used, kf = [], set(), {}
    for sel, body in blocks(src):
        if sel.startswith('@property'):
            css.append('%s{%s}' % (sel, body)); continue  # 11/20 MENU の回る光が前の形のページで止まっていた（--ra の登録が無いと角度が一気に飛ぶ）
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
# 11/20 19:07 owner「月が決めていいよ・使いやすさ→デザイン」→ 街のページ（/machi/<id>）を新しい形に。links/machi は前のまま残し、
# links/shin/machi/<id>.html を作る（functions/_middleware.js が /machi/<id> で出す）。作り：tools/shin/machi2.py・machi2.css
try:
    import shutil as _sh
    _sh.copy(os.path.join(R, 'tools/shin/machi2.css'), os.path.join(L, 'shin', 'machi2.css'))
    _s2 = _iu2 = None
    import importlib.util as _iu2
    _s2 = _iu2.spec_from_file_location('machi2', os.path.join(R, 'tools/shin/machi2.py')); _m2 = _iu2.module_from_spec(_s2); _s2.loader.exec_module(_m2)
    _m2.batch(os.path.join(L, 'machi'), os.path.join(L, 'shin', 'machi'))
except Exception as _e:
    print('machi2: 作れなかった', _e)
# 11/19 functions が上限で止まっても新しい形が出るように（bake.py）
import importlib.util as _iu
_s = _iu.spec_from_file_location('bake', os.path.join(R, 'tools/shin/bake.py')); _b = _iu.module_from_spec(_s); _s.loader.exec_module(_b); _b.main(L)
# 11/19 owner「その他も本気でやり直せ」：おでかけ1件のページ（/o/*）の一番上に、その催しの写真（撮影者つき）を入れる。
def _ophoto():
    import html as _h
    t = open(os.path.join(L, 'shin', 'odekake.html'), encoding='utf-8').read()
    d = json.loads(_h.unescape(re.search(r'id="d" type="application/json">(.*?)</script>', t, re.S).group(1)).replace('<\\/', '</'))
    n = 0
    for x in d['items']:
        if not (x.get('o') and x.get('im')): continue
        p = os.path.join(L, 'o', x['o'] + '.html')
        if not os.path.exists(p): continue
        h = open(p, encoding='utf-8').read()
        if 'class="kph"' in h or '<div class="big">' not in h: continue
        src = x['im'] if '/' in x['im'] else '/assets/ph/' + x['im']
        cr = (' 写真：' + (f'<a href="{_h.escape(x["cu"])}" target="_blank" rel="noopener">{_h.escape(x["cr"])}</a>' if x.get('cu') else _h.escape(x['cr']))) if x.get('cr') else ''
        fig = f'<figure class="kph"><img src="{src}" alt="" fetchpriority="high" decoding="async"><figcaption>{cr}</figcaption></figure>'
        h = h.replace('<div class="big">', fig + '<div class="big">', 1)
        open(p, 'w', encoding='utf-8').write(h); n += 1
    print('o ページに写真', n, '枚')
try:
    _ophoto()
except Exception as e:
    print('o 写真：入れられなかった', repr(e))
# 開店・閉店の1店のページ（/kaiten/*）にも、その場所の写真（撮影者つき）を題の下に入れる。
def _kphoto():
    import html as _h
    t = open(os.path.join(L, 'shin', 'kaiten.html'), encoding='utf-8').read()
    d = json.loads(_h.unescape(re.search(r'id="d" type="application/json">(.*?)</script>', t, re.S).group(1)).replace('<\\/', '</'))
    n = 0
    for x in d['items']:
        if not (x.get('sp') and x.get('im')): continue
        p = os.path.join(L, x['sp'].strip('/') + '.html')
        if not os.path.exists(p): continue
        h = open(p, encoding='utf-8').read()
        if 'class="sp-ph"' in h or '<div class="sp-when"' not in h: continue
        src = x['im'] if '/' in x['im'] else '/assets/ph/' + x['im']
        cr = (' 写真：' + (f'<a href="{_h.escape(x["cu"])}" target="_blank" rel="noopener">{_h.escape(x["cr"])}</a>' if x.get('cu') else _h.escape(x['cr']))) if x.get('cr') else ''
        h = h.replace('<div class="sp-when"', f'<figure class="sp-ph"><img src="{src}" alt="" fetchpriority="high" decoding="async"><figcaption>{cr}</figcaption></figure><div class="sp-when"', 1)
        open(p, 'w', encoding='utf-8').write(h); n += 1
    print('開店閉店の1店に写真', n, '枚')
try:
    _kphoto()
except Exception as e:
    print('開店閉店 写真：入れられなかった', repr(e))
