"""TOWN NOTES（仮）: 今のおでかけリスト（links/index.html）に地図を組み込んだ試作を作る。
python3 tools/townnotes/build.py → links/townnotes/index.html と links/townnotes/map.js
本番にするときは links/index.html に <script src="/townnotes/map.js" defer></script> を足すだけ。"""
import json, os
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(D, '..', '..'))
P = json.load(open(os.path.join(R, 'tools/outing_reel/paths.json')))

import sys; sys.path.insert(0, D)
from assemble import assemble

# 「地図で見る」ボタンの小さい関西の絵（府県の形だけ。大きさはページで測る）
MK = {'hyogo': '兵庫', 'kyoto': '京都', 'shiga': '滋賀', 'osaka': '大阪', 'nara': '奈良', 'wakayama': '和歌山'}
js = assemble(os.path.join(D, 'region-kansai.js'), os.path.join(D, 'site-tsuki.js'), {MK[k]: P[k] for k in MK})

os.makedirs(os.path.join(R, 'links/townnotes'), exist_ok=True)
open(os.path.join(R, 'links/townnotes/map.js'), 'w', encoding='utf-8').write(js)
# イルミネーションのページ用（同じ地図の本体に、ページとのつなぎだけ変える）
open(os.path.join(R, 'links/townnotes/map-illumi.js'), 'w', encoding='utf-8').write(assemble(os.path.join(D, 'region-kansai.js'), os.path.join(D, 'site-illumi.js'), {MK[k]: P[k] for k in MK}))
h = open(os.path.join(R, 'links/index.html'), encoding='utf-8').read()
import re
# 本番のリスト（links/index.html）の地図の読み込みも、新しい版の ?v= にそろえる
v = __import__('hashlib').sha1(js.encode('utf-8')).hexdigest()[:8]
live = re.sub(r'/townnotes/map\.js\?v=[0-9a-f]+', '/townnotes/map.js?v=' + v, h)
if live != h:
    open(os.path.join(R, 'links/index.html'), 'w', encoding='utf-8').write(live)
# 試作ページには本番の読み込みを持ちこまない（下で試作用を足す）
h = re.sub(r'<script src="/townnotes/map\.js[^"]*" defer></script>', '', h)
# 試作は links/townnotes/ にあるので、上の階のファイルは ../ で指す（Cloudflareでも予備のGitHubページでも同じに動く）
for a in ['src="assets/','href="assets/','href="gyosha.html"','href="uru.html"']:
    h = h.replace(a, a.replace('="', '="../'))
# 試作ページは数えない（本番の数字を汚さない）
old = 'return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();'
assert h.count(old) == 1; h = h.replace(old, 'return true;}catch(e){return true;}})();')
h = h.replace('<title>関西おでかけリスト</title>', '<title>関西おでかけリスト（地図つき試作）</title>')
badge = '<div style="position:fixed;top:8px;left:8px;z-index:50;font-family:Jost,sans-serif;font-size:10px;letter-spacing:.2em;background:#2B2622;color:#fff;padding:2px 8px;pointer-events:none">PROTOTYPE</div>'
# 中身が変わるたびに ?v= を変えて、スマホに古い地図が残らないようにする
import hashlib
v = hashlib.sha1(js.encode('utf-8')).hexdigest()[:8]
# 試し（TN_TRY）：試作ページだけで、新しい見せ方を先に試す
h = h.replace('</body></html>', badge + '<script>window.TN_TRY=1</script><script src="map.js?v=' + v + '" defer></script></body></html>')
assert 'src="map.js?v=' in h
open(os.path.join(R, 'links/townnotes/index.html'), 'w', encoding='utf-8').write(h); print('ok')
