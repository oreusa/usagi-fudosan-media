"""TOWN NOTES（仮）のページを作る: python3 tools/townnotes/build.py
地図はリールと同じ（tools/outing_reel/paths.json）。出力 links/townnotes/index.html"""
import json, os
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, '..', '..')
P = json.load(open(os.path.join(R, 'tools/outing_reel/paths.json')))
JP = {'osaka': '大阪', 'kyoto': '京都', 'hyogo': '兵庫', 'nara': '奈良', 'shiga': '滋賀', 'wakayama': '和歌山'}
mo = ''.join(f'<path class="mo" d="{d}"/>' for k, d in P.items() if k not in JP)
mk = ''.join(f'<path class="mk" id="p_{k}" data-pref="{v}" d="{P[k]}"/>' for k, v in JP.items())
svg = f'<svg id="map" viewBox="200.5 251 60 60" preserveAspectRatio="xMidYMid slice"><g id="base">{mo}{mk}</g><g id="pins"></g></svg>'
h = open(os.path.join(D, 'page.tpl.html'), encoding='utf-8').read().replace('__SVG__', svg)
os.makedirs(os.path.join(R, 'links/townnotes'), exist_ok=True)
open(os.path.join(R, 'links/townnotes/index.html'), 'w', encoding='utf-8').write(h); print('ok')
