"""TOWN NOTES（仮）: 今のおでかけリスト（links/index.html）に地図を組み込んだ試作を作る。
python3 tools/townnotes/build.py → links/townnotes/index.html と links/townnotes/map.js
本番にするときは links/index.html に <script src="/townnotes/map.js" defer></script> を足すだけ。"""
import json, os
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(D, '..', '..'))
P = json.load(open(os.path.join(R, 'tools/outing_reel/paths.json')))
js = open(os.path.join(D, 'map.src.js'), encoding='utf-8').read().replace('__PATHS__', json.dumps(P, separators=(',', ':')))
os.makedirs(os.path.join(R, 'links/townnotes'), exist_ok=True)
open(os.path.join(R, 'links/townnotes/map.js'), 'w', encoding='utf-8').write(js)
h = open(os.path.join(R, 'links/index.html'), encoding='utf-8').read()
h = h.replace('<head><meta charset="utf-8">', '<head><meta charset="utf-8"><base href="/">', 1)
# 試作ページは数えない（本番の数字を汚さない）
old = 'return localStorage.getItem("usagi_owner")==="1";}catch(e){return false;}})();'
assert h.count(old) == 1; h = h.replace(old, 'return true;}catch(e){return true;}})();')
h = h.replace('<title>関西おでかけリスト</title>', '<title>関西おでかけリスト（地図つき試作）</title>')
badge = '<div style="position:fixed;top:8px;left:8px;z-index:50;font-family:Jost,sans-serif;font-size:10px;letter-spacing:.2em;background:#2B2622;color:#fff;padding:2px 8px;pointer-events:none">PROTOTYPE</div>'
# 中身が変わるたびに ?v= を変えて、スマホに古い地図が残らないようにする
import hashlib
v = hashlib.sha1(js.encode('utf-8')).hexdigest()[:8]
h = h.replace('</body></html>', badge + '<script src="/townnotes/map.js?v=' + v + '" defer></script></body></html>')
assert 'townnotes/map.js' in h
open(os.path.join(R, 'links/townnotes/index.html'), 'w', encoding='utf-8').write(h); print('ok')
