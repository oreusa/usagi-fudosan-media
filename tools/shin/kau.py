"""新しいHP：おかいもの（/shin/kau）。役目＝Amazon・楽天・Yahoo! を1つの画面で見比べる。こだわり＝いちばん安いお店が光る。
値段は燈（akari-auto）が毎日作る okai-shin.json。ここで作る時点の物を入れておき、ページを開くたびに新しい物を取りに行く。"""
import json, os, sys, urllib.request

LIVE = 'https://kanto.townnote.app/okai-shin.json'
GROUPS = [('赤ちゃん', ['diaper', 'wipes']), ('紙・日用品', ['tp', 'tissue', 'trash', 'mask', 'battery']),
          ('洗濯・お風呂', ['detergent', 'softener', 'shampoo', 'bodysoap', 'dish']),
          ('飲み物・食べ物', ['water', 'tea', 'soda', 'coffee', 'beans', 'rice', 'pasta']), ('ペット', ['dogfood', 'catfood'])]


def load(R):
    p = os.path.join(os.path.dirname(R), 'akari-auto', 'site', 'okai-shin.json')
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    # 11/20 GitHub の機械からは kanto.townnote.app が 403 を返す日がある → 燈のリポジトリの物 → 前に作った物の順で使う（止めない）
    for u in (LIVE, 'https://raw.githubusercontent.com/oreusa/akari-auto/main/site/okai-shin.json'):
        try:
            q = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (townnote build)'})
            with urllib.request.urlopen(q, timeout=20) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            print('kau: 取れない', u, e)
    raise RuntimeError('okai-shin.json が取れない')


def build(write, L, R):
    d = load(R)
    sys.path.insert(0, os.path.join(os.path.dirname(R), 'akari-auto', 'scripts'))
    try:
        from okai_home import ICON
    except Exception:
        ICON = json.load(open(os.path.join(R, 'tools/shin/kau_icons.json'), encoding='utf-8'))
    have = {c['k'] for c in d['cats']}
    d['ic'] = {k: v for k, v in ICON.items() if k in have}
    d['groups'] = [[g, [k for k in ks if k in have]] for g, ks in GROUPS]
    d['live'] = LIVE
    cfg = {'nav': [{'t': '品物', 'ic': 'find', 'a': 'find'}, {'t': '値下がり', 'ic': 'down', 'a': 'drop'}, {'t': 'いつもの物', 'ic': 'star', 'a': 'my'}, {'t': 'ふるさと納税', 'ic': 'gift', 'href': '/furusato'}],
           'menu': {'k': 'Shopping', 'items': [['日用品の値段くらべ', '/okaimono', 1], ['ふるさと納税', '/furusato'], ['値下がりした物の一覧', '/nesage'], ['今までのおかいものの画面', '/okaimono']]},
           'foot': '値段：楽天市場・Yahoo!ショッピングで調べた送料込みの値段（調べた時のもの。お店で変わることがあります）。Amazonは値段を自動で調べられないため、押すとAmazonの検索が開きます。<br>このページのお店へのリンクは広告（PR）です。'}
    cfg['desc'] = 'ティッシュ・トイレットペーパー・おむつ・洗剤・水・お米など21種類を、楽天とYahoo!ショッピングの送料込みの値段で、1Lあたり・1枚あたりに直して比べています。Amazonも同じ画面から見られます。広告（PR）を含みます。'
    write('kau', '日用品の値段くらべ（楽天・Yahoo!・Amazon）｜TOWN NOTE', cfg, d)
    print('kau', len(d['cats']), '種類', sum(len(c['o']) for c in d['cats']), '件')
