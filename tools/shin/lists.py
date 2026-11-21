"""新しいHP：一覧の形のページ（links/shin/list.js）。11/19 owner「全部！」。
初詣・泊まり・いまから行ける・開店閉店・まちランキング を、おでかけと同じ土台で作る。build.py の odekake() の最後から呼ばれる。"""
import copy, datetime, hashlib, html, json, os, re, runpy, tempfile

PREFS = ['大阪', '京都', '兵庫', '奈良', '滋賀', '和歌山']
EMO = re.compile('[\U0001F000-\U0001FAFF☀-➿️⛩]+')
ODE_NAV = lambda cur: [dict(n, **({'cur': 1} if n['href'] == cur else {})) for n in [
    {'t': '開催中', 'ic': 'now', 'href': '/odekake'}, {'t': '今週末', 'ic': 'we', 'href': '/odekake?w=we'},
    {'t': 'いまから', 'ic': 'map', 'href': '/ima'}, {'t': '泊まり', 'ic': 'inn', 'href': '/tomari'}]]
ALSO = [['関西のおでかけ・イベント', '/odekake'], ['関西のイルミネーション', '/illumination'], ['関西の紅葉', '/koyo'],
        ['いまから行けるおでかけ', '/ima'], ['泊まりで行くおでかけ', '/tomari'], ['関西の初詣', '/hatsumode']]


def build(write, URL, L, R, cfg, items, il, ky, fin, icons, norm, MAP=None):
    TD = datetime.date.today().isoformat()

    def ode(name, url, title, desc, page, its, cur):
        c = copy.deepcopy(cfg); c['desc'] = desc; c['nav'] = ODE_NAV(cur)
        c['menu']['items'] = [[t, u] + ([1] if u == cur else []) for t, u, *_ in c['menu']['items']]
        page.setdefault('also', [a for a in ALSO if a[1] != cur])
        URL[name] = url
        write(name, title, c, {'items': its, 'icons': icons, 'page': page}, js='list')

    # ---------- 初詣 ----------
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(R, 'tools/hatsumode/data.tsv'), encoding='utf-8') if l.strip() and not l.startswith('#')]
    hm = []
    for p, n, city, tm, tr, yr, url in rows:
        it = {'t': n, 'p': p, 'a': city, 'k': 'hatsu', 'u': url, 'ub': '公式の案内を見る', 'id': hashlib.sha1(n.encode()).hexdigest()[:6],
              'bg': '2027年の案内' if yr == '2027年' else ('昨年の案内' if yr == '昨年' else '例年の案内'), 'bgc': '' if yr == '2027年' else 'off',
              'rows': [['時間', tm]] + ([['車・混雑', tr]] if tr not in ('', '—') else []) + [['案内', ('2027年の案内' if yr == '2027年' else f'{yr}の案内（2027年の案内が出たら書き換えます）')]],
              'd': '大晦日〜三が日', 'mq': f'{n} {city}'}
        fin(it, n); it.pop('o', None)
        hm.append(it)
    n27 = sum(1 for r in rows if r[5] == '2027年')
    ode('hatsumode', '/hatsumode', f'関西の初詣2027｜大晦日・三が日の時間と交通規制（{len(hm)}か所）｜TOWN NOTE',
        f'関西6府県の初詣{len(hm)}か所の、大晦日と三が日の参拝時間・交通規制・駐車場を、各神社の公式ページからまとめました。',
        {'h1': '関西の初詣', 'sub': f'2027年・大晦日と三が日・{len(hm)}か所', 'dl': f'2027年の案内が出た所 <b>{n27}</b>か所',
         'K': {'hatsu': ['初詣', '#A23B3B']}, 'cnt': 'か所', 'unit': '初詣',
         'note': '時間と交通規制は、各神社の公式ページの案内です。2027年の案内がまだの所は、昨年・例年の案内を載せ、出たら書き換えます。出かける前に公式で確かめてください。'}, hm, '/hatsumode')

    # ---------- 泊まり（遠いおでかけ＋近くの評価の高い宿3軒） ----------
    yado = json.load(open(os.path.join(L, 'kansai-yado.json'), encoding='utf-8'))
    Y = {re.sub(r'\s+', '', k): v for k, v in yado.items() if v}
    tm, seen = [], set()
    for src in (items, il, ky):
        for x in src:
            k = re.sub(r'\s+', '', x['t'])
            if k not in Y or k in seen or x['e'] < TD: continue
            seen.add(k)
            hs = []
            for h in sorted(Y[k][:3], key=lambda h: h.get('km', 99)):
                nm = re.sub(r'\s*(<[^<>]*>|\^)\s*$', '', h.get('n', '')).strip()
                meta = '・'.join(v for v in [(f"★{h['r']:.2f}".rstrip('0').rstrip('.') + (f"（口コミ{h['rc']:,}件）" if h.get('rc') else '')) if h.get('r') else '',
                                             'すぐそば' if h.get('km', 9) < 0.1 else f"ここから{h['km']}km"] if v)
                hs.append([nm, h['u'], meta, f"{int(h['min']):,}円〜" if h.get('min') else ''])
            it = dict(x); it['links'] = hs; it['lh'] = '近くの宿（評価の高い順から3軒・近い順）'
            it['lnote'] = '宿は楽天トラベルの評価3.5以上・口コミ10件以上。値段は1泊の最安の目安で、日や人数で変わります。宿のリンクは広告（PR）です。'
            it['hk'] = f'近くの宿 {len(hs)}軒・' + (hs[0][3] if hs and hs[0][3] else '')
            it['hk'] = it['hk'].rstrip('・')
            it.pop('o', None)
            tm.append(it)
    nin = sum(len(x['links']) for x in tm)
    ode('tomari', '/tomari', '泊まりで行く関西のおでかけ｜近くの評価の高い宿つき｜TOWN NOTE',
        f'関西の少し遠いおでかけ{len(tm)}か所と、近くの評価の高い宿をまとめました。宿は楽天トラベルの評価と口コミの数から選んでいます。',
        {'h1': '泊まりで行くおでかけ', 'sub': f'少し遠いおでかけ {len(tm)}か所と、近くの宿 {nin}軒', 'K': cfg_kinds(items, icons), 'cnt': 'か所', 'unit': '宿つき',
         'note': '梅田・なんば・京都駅・三宮から20km以上はなれた、泊まりで行きたいおでかけです。押すと近くの宿が3軒出ます。'}, tm, '/tomari')

    # ---------- いまから行ける（いる場所から近い順・きょう開いている所） ----------
    im, seen = [], set()
    for src in (items, il, ky):
        for x in src:
            if not x.get('xy') or x['s'] > TD or x['e'] < TD: continue
            k = norm(x['t'])
            if k in seen: continue
            seen.add(k)
            it = dict(x); it['ll'] = [round(36 - x['xy'][1] / 100, 4), round(x['xy'][0] / 82.2 + 134, 4)]
            im.append(it)
    ode('ima', '/ima', 'いまから行ける関西のおでかけ｜近い順・きょう開いている所｜TOWN NOTE',
        'いる場所といまの時刻から、きょう開いている関西のおでかけを近い順に並べます。30分・1時間・1時間半で行ける所がすぐ分かります。',
        {'h1': 'いまから行けるおでかけ', 'sub': 'きょう開いている所を、近い順に', 'near': 1, 'K': cfg_kinds(items, icons), 'cnt': 'か所', 'seg': False,
         'none': 'この時間で行ける所は見つかりませんでした。「1時間半」「すべて」でもう少し遠くまで探せます。',
         'note': 'かかる時間は直線距離から出した目安です（電車と歩きを合わせたおおよその時間）。本当の行き方は「行き方」から Google マップで。開いている時間は出かける前に公式で確かめてください。'}, im, '/ima')

    # ---------- 開店・閉店（tools/kaiten/build.py の決まりをそのまま使う：ジャンル・初出店・場所の写真） ----------
    tmp = tempfile.mkdtemp()
    os.environ['KAITEN_OUT'] = os.path.join(tmp, 'k.html'); os.environ['KAITEN_SP_DIR'] = tempfile.mkdtemp()
    import sys as _s
    av = _s.argv; _s.argv = [av[0]]
    try:
        K = runpy.run_path(os.path.join(R, 'tools/kaiten/build.py'))
    finally:
        _s.argv = av; os.environ.pop('KAITEN_OUT'); os.environ.pop('KAITEN_SP_DIR')
    sp = {K['slug'](x) for x in K['SP']}
    GC = {'カフェ': '#8A5A3B', 'パン・スイーツ': '#C2557A', 'ごはん': '#C0532B', 'スーパー・コンビニ': '#2E8B6E', 'ドラッグ・薬': '#2F7D9A', '服・雑貨': '#5B4B8A',
          '美容・からだ': '#B7862A', '遊び・体験': '#3B5BA5', '車・家電': '#4F6681', '施設': '#6F8C68', 'その他': '#6E6E73'}
    kt = []
    for x in sorted(K['live'], key=lambda x: x['d']):
        b = K['bucket'](x); g, _ = K['genre'](x); h = K['hatsu'](x); v = K['vphoto'](x); d = datetime.date.fromisoformat(x['d'])
        lab = {'open': '開店', 'pop': '期間限定', 'close': '閉店'}[x['k']]
        it = {'t': x['n'], 'p': x['p'], 'a': x.get('pl') or '', 'k': g, 'w': b, 'u': x['u'], 'ub': '公式の発表を見る', 'id': K['slug'](x),
              'd': f"{d.month}/{d.day}（{'月火水木金土日'[d.weekday()]}）{lab}", 'hk': x.get('pt', ''),
              'bg': (h or lab) if b != 'close' else '閉店', 'bgc': 'off' if b == 'close' else ('pop' if not h else ''),
              'rows': [r for r in [['日', f"{d.month}月{d.day}日（{'月火水木金土日'[d.weekday()]}）{lab}" + (f"〜{x['end']}" if x.get('end') else '')], ['場所', x.get('pl') or x['p']], ['時間', x.get('tm') or '']] if r[1]],
              'mq': (x.get('pl') or '') + ' ' + x['n'], 'big': ('あと' + str((d - datetime.date.today()).days) + '日で' + lab if d.isoformat() > TD else ('きょう' + lab if d.isoformat() == TD else ''))}
        if it['id'] in sp: it['sp'] = '/kaiten/' + it['id']
        if v: it.update({'im': v['img'], 'cr': v['cr'], 'cu': v.get('page', '')})
        kt.append(it)
    kt.reverse()
    cn = {k: sum(1 for x in kt if x['w'] == k) for k in ('soon', 'done', 'close')}
    gk = {g: [g, GC.get(g, '#6E6E73')] for g in GC if any(x['k'] == g for x in kt)}
    c = copy.deepcopy(cfg)
    c['nav'] = [{'t': 'これから', 'ic': 'now', 'a': 'w=soon'}, {'t': '開いた', 'ic': 'we', 'a': 'w=done'}, {'t': '閉まる', 'ic': 'down', 'a': 'w=close'}, {'t': '保存', 'ic': 'star', 'a': 'fav'}]
    c['menu'] = {'k': 'New Shops', 'items': [['関西の開店・閉店', '/kaiten', 1]]}
    c['foot'] = '各社の公式の発表（プレスリリース・お店のお知らせ）から集めています。写真はお店の入る建物・場所の写真で、撮影者を各ページに書いています（ウィキメディア・コモンズ ほか）。'
    c['desc'] = f'関西6府県の新しいお店・閉まるお店を、各社の公式の発表から毎日集めています。これから{cn["soon"]}件・開いた{cn["done"]}件・閉まる{cn["close"]}件。'
    URL['kaiten'] = '/kaiten'
    write('kaiten', f'関西の開店・閉店ニュース｜新しいお店・閉まるお店を公式の発表で｜TOWN NOTE', c,
          {'items': kt, 'icons': icons, 'page': {'h1': '関西の開店・閉店', 'sub': '新しいお店・閉まるお店を、公式の発表で', 'view': 'list', 'K': gk, 'fav': 1, 'id': 'kaiten',
                                                 'dl': f'毎日更新・<b>{len(kt)}</b>件', 'tabs': [['soon', f'これから {cn["soon"]}', 'w', 'soon'], ['done', f'開いた {cn["done"]}', 'w', 'done'], ['close', f'閉まる {cn["close"]}', 'w', 'close']]}}, js='list')

    # ---------- まちランキング ----------
    rk = json.load(open(os.path.join(R, 'tools/ranking/data.json'), encoding='utf-8'))['items']
    towns = json.load(open(os.path.join(L, 'assets', 'towns.json'), encoding='utf-8'))
    towns = towns.get('towns', towns) if isinstance(towns, dict) else towns
    NAME = sorted(((t['n'], t['id']) for t in towns), key=lambda x: -len(x[0]))
    KIND = [('eki', '駅', '#3B5BA5', r'駅'), ('ie', '家と土地', '#C0532B', r'住宅地|商業地|地価|売れた|基準地'), ('hito', '人口', '#2E8B6E', r'人口|割合'), ('hoka', 'そのほか', '#6E6E73', r'.')]
    rl = []
    for it0 in sorted(rk, key=lambda x: (x['day'], int((re.search(r'No\.(\d+)', x['text']) or [0, 0])[1])), reverse=True):
        first = it0['text'].split('\n')[0]
        title = EMO.sub('', first).strip().strip('【】').replace('｜', '　')
        no = (re.search(r'No\.(\d+)', first) or [None, ''])[1]
        title = re.sub(r'^関西まちランキング\s*No\.\d+\s*', '', title).strip() or title
        k = next(k for k in KIND if re.search(k[3], first + ('駅' if '🚃' in first else '') + it0['text'][:200]))
        body = '\n'.join(EMO.sub('', l).rstrip().replace('✦ ', '■ ').replace('⊹ ', '・').replace('✧ ', '※ ').replace('◎ ', '') for l in it0['text'].split('\n')[1:]).strip()
        body = re.sub(r'\n{3,}', '\n\n', body)
        t, seen2 = it0['text'], []
        for n, i in NAME:
            if n in t and i not in [s[1] for s in seen2]: seen2.append((n, i)); t = t.replace(n, '')
        d = datetime.date.fromisoformat(it0['day'])
        p = next((p for p in PREFS if p in first), '関西')
        rl.append({'t': title, 'p': p, 'k': k[0], 'd': (f'No.{no}・' if no else '') + f'{d.month}/{d.day}', 'body': body, 'u': it0.get('src', ''), 'ub': '出どころの公式ページ', 'nomap': 1,
                   'id': it0['day'] + '-' + hashlib.sha1(first.encode()).hexdigest()[:4],
                   'links': [[n, '/machi/' + i, 'この街の家と土地の値段', ''] for n, i in seen2[:6]], 'lh': '出てくる街のくわしいページ', 'lnote': ''})
    c = copy.deepcopy(cfg)
    c['nav'] = [{'t': '街をさがす', 'ic': 'find', 'href': '/fudosan-list'}, {'t': 'ランキング', 'ic': 'rank', 'a': 'top', 'cur': 1}, {'t': '売りたい', 'ic': 'sell', 'href': '/uru'}, {'t': 'いくら？', 'ic': 'yen', 'href': '/ikura'}]
    c['menu'] = {'k': 'Home & Land', 'items': [['家と土地の相場', '/fudosan-list'], ['まちランキング', '/ranking', 1], ['家を売る前に', '/uru'], ['いくらで売れる？', '/ikura'], ['実家・空き家', '/jikka/'], ['地価ランキング', '/chika-kansai']]}
    c['foot'] = '数字はどれも国・府県・鉄道会社などの公式の発表です。街の平均で、1軒ずつの値段ではありません。'
    c['desc'] = f'関西の街を、駅の乗る人の数・地価・人口など公式の数字で順位にしました（{len(rl)}本）。'
    URL['ranking'] = '/ranking'
    write('ranking', f'関西まちランキング｜駅・地価・人口の順位を公式の数字で（{len(rl)}本）｜TOWN NOTE', c,
          {'items': rl, 'page': {'h1': '関西まちランキング', 'sub': f'駅・地価・人口の順位を、公式の数字で・{len(rl)}本', 'view': 'list', 'cnt': '本',
                                 'K': {k[0]: [k[1], k[2]] for k in KIND if any(x['k'] == k[0] for x in rl)},
                                 'note': '数字は国土交通省・各府県・鉄道会社などの公式の発表です。押すと順位の全部と、出どころの公式ページが出ます。'}}, js='list')

    global COVER
    def COVER():
        # ---------- 表紙（/）：ie・kau を作った後に build.py の最後から呼ぶ ----------
        def dj(name):
            t = open(os.path.join(L, 'shin', name + '.html'), encoding='utf-8').read()
            return json.loads(html.unescape(re.search(r'id="d" type="application/json">(.*?)</script>', t, re.S).group(1)).replace('<\\/', '</'))
        now = [x for x in items if x['s'] <= TD <= x['e']]
        pc = {p: sum(1 for x in now if x['p'] == p) for p in PREFS}
        ph = [x for x in sorted(now, key=lambda x: ((1 if (x.get('k') == 'light' and not x.get('nt')) or (x.get('k') == 'koyo' and not x.get('wm')) else 0), -(x.get('vb') or 0) // 6, x['e'])) if x.get('im')]  # 11/21 表紙の顔：中身に合う・きれいな写真を先に
        top, used = [], set()
        while len(top) < 8 and ph:
            for p in PREFS:
                c_ = next((x for x in ph if x['p'] == p and x['t'] not in used), None)
                if c_ and len(top) < 8: top.append({k: c_[k] for k in ('t', 'p', 'e', 'im', 'th', 'o') if k in c_}); used.add(c_['t'])
            if all(x['t'] in used for x in ph): break
        ie = dj('ie'); kau = dj('kau')
        go = [{'t': '関西のおでかけ・イベント', 's': '開催中・今週末・まもなく終わる', 'n': str(len(now)), 'nu': '開催中', 'u': '/odekake', 'ic': 'now'},
              {'t': '家と土地の相場', 's': f"{len(ie['towns'])}の街の売れた値段と地価", 'n': str(len(ie['towns'])), 'nu': '街', 'u': '/fudosan-list', 'ic': 'find'},
              {'t': '日用品の値段くらべ', 's': '楽天・Yahoo!・Amazon を1つの画面で', 'n': str(len(kau['cats'])), 'nu': '種類', 'u': '/okaimono', 'ic': 'yen'},
              {'t': '開店・閉店', 's': '新しいお店・閉まるお店', 'n': str(cn['soon']), 'nu': 'これから開く', 'u': '/kaiten', 'ic': 'buy'}]
        more = [['関西のイルミネーション', '/illumination'], ['関西の紅葉', '/koyo'], ['いまから行けるおでかけ', '/ima'], ['泊まりで行くおでかけ', '/tomari'],
                ['関西の初詣', '/hatsumode'], ['関西まちランキング', '/ranking'], ['実家・空き家', '/jikka/'], ['ふるさと納税', '/furusato']]
        c = copy.deepcopy(cfg)
        c['nav'] = [{'t': 'おでかけ', 'ic': 'now', 'href': '/odekake'}, {'t': '家と土地', 'ic': 'find', 'href': '/fudosan-list'}, {'t': 'おかいもの', 'ic': 'yen', 'href': '/okaimono'}, {'t': '地図', 'ic': 'map', 'a': 'map'}]
        c['menu'] = {'k': 'Town Note', 'items': [['トップ', '/', 1], ['おでかけ', '/odekake'], ['家と土地', '/fudosan-list'], ['おかいもの', '/okaimono'], ['開店・閉店', '/kaiten']], 'rel': []}
        c['foot'] = 'おでかけの券・宿と、おかいものリストのリンクには広告（PR）があります。'
        c['desc'] = '関西の不動産屋が、街を調べて見つけたことをまとめています。開催中のおでかけ・イベント、205の街の家と土地の値段、日用品の値段くらべ、開店・閉店を、公式の発表と数字で。'
        URL['cover'] = '/'
        write('cover1', 'TOWN NOTE（タウンノート）｜関西のおでかけと、家と土地の値段（前の表紙）', c,
              {'pc': pc, 'top': top, 'go': go, 'more': more, 'map': MAP,
               'sns': [['Instagram', 'https://www.instagram.com/fudousan_ai_si/'], ['Threads', 'https://www.threads.com/@fudousan_ai_si'], ['X', 'https://x.com/fudosan_ai_si']]}, js='cover')
        # 11/19 23:16 owner「表紙ほぼおでかけじゃん」「地図も変」「全然お洒落でもAppleっぽくもない」→ apple.com の表紙の形：
        # 分野ごとに同じ大きさの面（見出し・1行・ボタン2つ・大きい絵）を縦に並べる。地図は表紙に置かない（おでかけのページにある）。
        def pick_ph(f, n):
            r, u = [], set()
            RK = {'koyo': 0, 'flower': 1, 'spot': 2, 'animal': 3, 'play': 4}
            for x in sorted(now, key=lambda x: (RK.get(x.get('k'), 9), (1 if (x.get('k') == 'light' and not x.get('nt')) or (x.get('k') == 'koyo' and not x.get('wm')) else 0), -(x.get('vb') or 0) // 6, x['e'])):  # 11/21 きれいな写真を先に（6点ごとの段・同じ段は終わりが近い順）
                if x.get('im') and f(x) and x['im'] not in u: r.append({k: x[k] for k in ('t', 'p', 'e', 'im', 'th', 'o') if k in x}); u.add(x['im'])
                if len(r) >= n: break
            return r
        tw = sorted([t_ for t_ in ie['towns'] if t_.get('r8') is not None], key=lambda t_: -t_['r8'])[:3]
        KS = {c_['k']: c_ for c_ in kau['cats']}
        ks = [{'k': k, 'nm': KS[k]['nm'], 'unit': KS[k]['unit'], 'u': KS[k]['o'][0]['u'], 'ic': kau['ic'].get(k, '')} for k in ('rice', 'water', 'tissue') if k in KS and KS[k].get('o')]
        if len(ks) < 3: ks = [{'k': c_['k'], 'nm': c_['nm'], 'unit': c_['unit'], 'u': c_['o'][0]['u'], 'ic': kau['ic'].get(c_['k'], '')} for c_ in kau['cats'][:3] if c_.get('o')]
        ka = next(({k: x[k] for k in ('t', 'a', 'd', 'im', 'big', 'sp', 'p') if k in x} for x in reversed(kt) if x['w'] == 'soon' and x.get('im')), None)
        c2 = copy.deepcopy(c)
        c2['nav'] = [{'t': 'おでかけ', 'ic': 'now', 'href': '/odekake'}, {'t': '家と土地', 'ic': 'find', 'href': '/fudosan-list'}, {'t': 'おかいもの', 'ic': 'yen', 'href': '/okaimono'}, {'t': '開店閉店', 'ic': 'buy', 'href': '/kaiten'}]
        c2['menu'] = {'k': 'Town Note', 'items': [['トップ', '/', 1], ['おでかけ', '/odekake'], ['家と土地', '/fudosan-list'], ['おかいもの', '/okaimono'], ['開店・閉店', '/kaiten']], 'rel': []}
        D2 = {'od': {'n': len(now), 'ph': pick_ph(lambda x: True, 5)},
               'ie': {'n': len(ie['towns']), 'tw': [{'n': t_['n'], 'r': t_['r8'], 'id': t_['id']} for t_ in tw]},
               'kau': {'n': len(kau['cats']), 'ks': ks},
               'kai': {'n': cn['soon'], 'x': ka},
               'ko': (pick_ph(lambda x: x.get('k') == 'koyo' and x.get('im') not in {q['im'] for q in pick_ph(lambda x: True, 5)}, 1) or pick_ph(lambda x: x.get('k') == 'koyo', 1) or [None])[0],
               'ft': [['おでかけ', [['関西のおでかけ', '/odekake'], ['イルミネーション', '/illumination'], ['紅葉', '/koyo'], ['いまから行ける', '/ima'], ['泊まりで行く', '/tomari'], ['初詣', '/hatsumode']]],
                      ['家と土地', [['家と土地の相場', '/fudosan-list'], ['地価ランキング', '/chika-kansai'], ['まちランキング', '/ranking'], ['家を売る前に', '/uru'], ['いくらで売れる？', '/ikura'], ['家を買いたい', '/sagasu'], ['実家・空き家ノート', '/jikka/'], ['3問でわかる実家の診断', '/jikka/shindan/'], ['解体・片付けの費用', '/kaitai'], ['解体の補助金', '/kaitai-ranking'], ['空き家が多い街', '/akiya-ranking']]],
                      ['おかいもの', [['日用品の値段くらべ', '/okaimono'], ['値下がりした物', '/nesage'], ['ふるさと納税', '/furusato'], ['開店・閉店ニュース', '/kaiten']]],
                      ['このサイト', [['相談・申し込み', '/moushikomi'], ['リクエスト・感想', '/koe'], ['プライバシーポリシー', '/privacy']]]],
               'sns': [['Instagram', 'https://www.instagram.com/fudousan_ai_si/'], ['Threads', 'https://www.threads.com/@fudousan_ai_si'], ['X', 'https://x.com/fudosan_ai_si']]}
        # 11/19 23:15 owner「朝9時には反映」→ この形を表紙（/）に。前の表紙は /shin/cover1 に残す
        write('cover', 'TOWN NOTE（タウンノート）｜関西のおでかけと、家と土地の値段', c2, D2, js='cover2')
        write('cover2', 'TOWN NOTE（タウンノート）｜関西のおでかけと、家と土地の値段', c2, D2, js='cover2')


def cfg_kinds(items, icons):
    G = {'art': ['アート・展示', '#3B5BA5'], 'light': ['光・イルミ', '#B7862A'], 'koyo': ['紅葉', '#C0532B'], 'flower': ['花', '#C2557A'], 'fes': ['まつり', '#B23A2E'],
         'quest': ['謎とき', '#5B4B8A'], 'play': ['あそぶ', '#2E8B6E'], 'spot': ['スポット', '#2F7D9A'], 'food': ['グルメ', '#C9702A'], 'animal': ['いきもの', '#6F7F33'],
         'xmas': ['クリスマス', '#2F7A4F'], 'hallo': ['ハロウィン', '#B45F1F'], 'shop': ['マーケット', '#8A6A3F']}
    return G
