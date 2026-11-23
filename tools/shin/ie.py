"""新しいHP：家と土地（/shin/ie）。役目＝自分の街の家と土地がいくらか、すぐ分かる。
データ：links/assets/towns.json（地価の動き・順位・位置）＋ tools/fudosan_list/reins/*.csv（近畿レインズ 2025年度の成約）＋ toukei.json（国勢調査・住宅土地統計）＋ 各街ページ links/machi/<id>.html のリンク（買いたい・売りたい）。"""
import json, os, csv, re, html

try:
    from yari import sell_cfg  # 関西 tools/shin/yari.py
except ImportError:
    from shin_yari import sell_cfg  # 関東 scripts/shin_yari.py

def build(write, MAP, L, R):
    towns = json.load(open(os.path.join(L, 'assets/towns.json'), encoding='utf-8'))
    tk = json.load(open(os.path.join(R, 'tools/fudosan_list/toukei.json'), encoding='utf-8'))
    jis = json.load(open(os.path.join(R, 'tools/fudosan_list/jis.json'), encoding='utf-8'))
    PF = {'大阪': '大阪府', '京都': '京都府', '兵庫': '兵庫県', '奈良': '奈良県', '滋賀': '滋賀県', '和歌山': '和歌山県'}
    PJ = {'大阪': '27000', '京都': '26000', '兵庫': '28000', '奈良': '29000', '滋賀': '25000', '和歌山': '30000'}
    def rd(f):
        out = {}
        for r in csv.DictReader(open(os.path.join(R, f'tools/fudosan_list/reins/{f}_2025.csv'), encoding='utf-8')):
            if r['市区町村']: out[(r['府県'], ('' if r['地域見出し'].endswith('他') else r['地域見出し']) + r['市区町村'])] = r
        return out
    M, K, T = rd('mansion'), rd('kodate'), rd('tochi')
    f = lambda v: float(v) if v not in (None, '') else None
    def pavg(tbl, pref, col):
        r = tbl.get((pref, '合計'))
        return f(r[col]) if r and f(r[col]) else None
    PA = {p: {'m': pavg(M, PF[p], '価格万円'), 'h': pavg(K, PF[p], '価格万円'), 't': pavg(T, PF[p], '㎡単価万円')} for p in PF}
    for p in PF:
        t = tk.get(PJ[p], {})
        PA[p]['pop'] = round((t['p25'] / t['p20'] - 1) * 100, 1) if t.get('p20') else None
        PA[p]['ak'] = round(t['a23'] / t['j23'] * 100, 1) if t.get('j23') else None
    out = []
    for t in towns:
        key = (PF[t['p']], t['n'])
        x = {'id': t['id'], 'p': t['p'], 'n': t['n'], 's': t['s'], 'k': t.get('k', ''), 'r7': t.get('r7'), 'r8': t.get('r8'), 'rk': t.get('rk'), 'of': t.get('of')}
        if key in M and f(M[key]['件数']) and f(M[key]['価格万円']): r = M[key]; x['m'] = [int(f(r['件数'])), f(r['価格万円']), f(r['専有面積']), f(r['築年']), f(r['㎡単価万円'])]
        if key in K and f(K[key]['件数']) and f(K[key]['価格万円']): r = K[key]; x['h'] = [int(f(r['件数'])), f(r['価格万円']), f(r['土地面積']), f(r['建物面積']), f(r['築年'])]
        if key in T and f(T[key]['件数']) and f(T[key]['㎡単価万円']): r = T[key]; x['t'] = [int(f(r['件数'])), f(r['㎡単価万円']), f(r['価格万円']), f(r['土地面積'])]
        c = jis.get(t['p'] + '|' + t['n'])
        s = tk.get(c or '', {})
        if s.get('p20'): x['pop'] = [s['p25'], round((s['p25'] / s['p20'] - 1) * 100, 1)]
        if s.get('o25'): x['o'] = s['o25']
        if s.get('j23'): x['ak'] = round(s['a23'] / s['j23'] * 100, 1)
        if t.get('la'):
            X, Y = (t['lo'] - 134) * 82.2, (36 - t['la']) * 100; x['xy'] = [round(X, 2), round(Y, 2)]
        pg = os.path.join(L, 'machi', t['id'] + '.html')
        if os.path.exists(pg):
            h = open(pg, encoding='utf-8').read()
            buy = [html.unescape(u) for u, lab in re.findall(r'<a [^>]*href="(https://ck\.jp\.ap\.valuecommerce[^"]+)"[^>]*>(.*?)</a>', h, re.S)]
            if buy: x['buy'] = buy[:3]
            kt = re.search(r'href="(/kaitai-[a-z]+)"', h)
            if kt: x['kt'] = kt.group(1)
        out.append(x)
    print('ie towns', len(out), 'mansion', sum('m' in x for x in out), 'kodate', sum('h' in x for x in out), 'pop', sum('pop' in x for x in out))
    cfg = {'nav': [{'t': '街をさがす', 'ic': 'find', 'a': 'find'}, {'t': 'ランキング', 'ic': 'rank', 'href': '/ranking'}, {'t': '売りたい', 'ic': 'sell', 'href': '/uru'}, {'t': 'いくら？', 'ic': 'yen', 'href': '/ikura'}],
           'menu': {'k': 'Home & Land', 'items': [['家と土地の相場', '/fudosan-list', 1], ['家を売る前に', '/uru'], ['いくらで売れる？', '/ikura'], ['実家・空き家', '/jikka/'], ['解体の費用と補助金', '/kaitai'], ['地価ランキング', '/chika-kansai']]},
           'foot': '地価：国土交通省・各府県「令和8年地価公示」。売れた家の値段：近畿レインズ「2025年度 年刊市況レポート」。人口・空き家：総務省統計局。<br>どれも街の平均で、1軒ずつの値段ではありません。「買いたい」のリンクは広告です（Yahoo!不動産）。'}
    cfg['sell'] = sell_cfg(0)
    cfg['desc'] = '関西205の街の、中古マンション・中古一戸建て・土地が実際に売れた値段（レインズ）と、地価の動き・人口を、街ごとにまとめました。府県の平均とも比べられます。'
    write('ie', '関西の家と土地の相場｜205の街の売れた値段と地価｜TOWN NOTE', cfg, {'towns': out, 'pa': PA, 'map': MAP})
