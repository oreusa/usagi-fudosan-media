"""ふるさと納税（/furusato）と値下がりした物（/nesage）を新しい土台で（links/shin/furu.js が出す）。
11/19 owner「ふるさと押したら前のページ飛ぶ」→ 前は燈（関東）の古いページをそのまま中に出していた。
中身は燈が毎日しらべる data/furusato.json・nesage.json（公開リポジトリの main）。読めない時は作らない（前の形のまま）。"""
import json, os, urllib.request

RAW = 'https://raw.githubusercontent.com/oreusa/akari-auto/main/data/'


def get(name):
    p = os.environ.get('AKARI_DATA')
    if p and os.path.exists(os.path.join(p, name)):
        return json.load(open(os.path.join(p, name), encoding='utf-8'))
    with urllib.request.urlopen(RAW + name, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


NAV = lambda first: first + [{'t': 'おかいもの', 'ic': 'yen', 'href': '/okaimono'}]
MENU = lambda cur: {'k': 'Shopping', 'items': [[t, u] + ([1] if u == cur else []) for t, u in
                                               [['日用品の値段くらべ', '/okaimono'], ['ふるさと納税', '/furusato'], ['値下がりした物', '/nesage'], ['開店・閉店', '/kaiten']]]}
FOOT = '値段は楽天市場で調べた時のものです（お店で変わることがあります）。このページの商品へのリンクは広告（PR）です。'


def build(write, URL, region='関西'):
    try:
        f = get('furusato.json')
        cats = [c for c in f['cats'] if c.get('top')]
        IC = {'rice': 'gift', 'tp': 'find', 'water': 'star'}
        cfg = {'nav': NAV([{'t': c['title'] if len(c['title']) <= 5 else 'トイレ', 'ic': IC.get(c['key'], 'gift'), 'a': c['key']} for c in cats][:3]),
               'menu': MENU('/furusato'), 'foot': FOOT,
               'desc': 'ふるさと納税の返礼品（お米・トイレットペーパー・水）を、寄付1万円でもらえる量でくらべました。楽天ふるさと納税を毎日しらべ直しています。'}
        URL['furusato'] = '/furusato'
        write('furusato', 'ふるさと納税 寄付1万円でもらえる量くらべ（お米・トイレットペーパー・水）｜TOWN NOTE', cfg,
              {'kind': 'furu', 'h1': 'ふるさと納税 1万円でもらえる量', 'sub': '楽天ふるさと納税の返礼品を、寄付1万円あたりの量でくらべました。', 'at': f['at'], 'cats': cats}, js='furu')
    except Exception as e:
        print('furu: ふるさと納税を作れなかった', repr(e))
    try:
        n = get('nesage.json')
        cfg = {'nav': NAV([{'t': '値下がり', 'ic': 'down', 'a': 'down'}, {'t': '値上がり', 'ic': 'rank', 'a': 'up'}, {'t': 'ふるさと', 'ic': 'gift', 'href': '/furusato'}]),
               'menu': MENU('/nesage'), 'foot': FOOT,
               'desc': f"楽天市場の日用品{n.get('tracked', '')}品の値段を毎日しらべ、ふだんより安くなっている物を並べています。"}
        URL['nesage'] = '/nesage'
        write('nesage', '値下がりした日用品｜ふだんより安い物（楽天市場を毎日しらべ）｜TOWN NOTE', cfg,
              {'kind': 'nesage', 'h1': '値下がりした物', 'sub': f"楽天市場の日用品{n.get('tracked', '')}品の値段を毎日しらべ、ふだんより安くなっている物を並べています。",
               'at': n['at'], 'since': n.get('since'), 'tracked': n.get('tracked'), 'downs': n.get('downs', []), 'ups': n.get('ups', [])}, js='furu')
    except Exception as e:
        print('furu: 値下がりを作れなかった', repr(e))
