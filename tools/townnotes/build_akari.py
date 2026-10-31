"""燈の関東おでかけリスト（akari-auto）用の地図を作る。月の地図と同じ本体（map.src.js）に、関東の設定とつなぎを入れる。
python3 tools/townnotes/build_akari.py <akari-autoの場所>
→ <akari-auto>/site/townnotes/map.js・map-illumi.js と kanto.json（関東の都県・市区町村の形）と grain.png
関東の形は国土数値情報（行政区域）を mapshaper で軽くした物（関西の kansai.json と同じ作り方。東京の島は入れない）"""
import json, os, shutil, sys, hashlib
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(D, '..', '..')); sys.path.insert(0, D)
from assemble import assemble
A = os.path.abspath(sys.argv[1]); out = os.path.join(A, 'site', 'townnotes'); os.makedirs(out, exist_ok=True)
mini = json.load(open(os.path.join(D, 'mini-kanto.json'), encoding='utf-8'))
js = assemble(os.path.join(D, 'region-kanto.js'), os.path.join(D, 'site-akari.js'), mini)
open(os.path.join(out, 'map.js'), 'w', encoding='utf-8').write(js)
# 関東イルミネーションのページ用（本体と関東の設定は同じ、ページとのつなぎだけ site-akari-illumi.js）
open(os.path.join(out, 'map-illumi.js'), 'w', encoding='utf-8').write(assemble(os.path.join(D, 'region-kanto.js'), os.path.join(D, 'site-akari-illumi.js'), mini))
shutil.copy(os.path.join(D, 'kanto.json'), os.path.join(out, 'kanto.json'))
shutil.copy(os.path.join(R, 'links', 'townnotes', 'grain.png'), os.path.join(out, 'grain.png'))  # 地図の紙の手ざわり
print('ok', hashlib.sha1(js.encode('utf-8')).hexdigest()[:8])
