import json, os
D = os.path.dirname(os.path.abspath(__file__))

def assemble(region, site, mini):
    """地図の本体（map.src.js）に、地域の設定（region-*.js）とページとのつなぎ（site-*.js）を入れる。
    mini = 「地図で見る」ボタンの小さい絵（府県名 → 形のpath）"""
    core = open(os.path.join(D, 'map.src.js'), encoding='utf-8').read()
    reg = open(region, encoding='utf-8').read()
    reg = reg[reg.index('{'):].replace('__MINI__', json.dumps(mini, ensure_ascii=False, separators=(',', ':')))
    st = open(site, encoding='utf-8').read()
    assert core.count('__REGION__') == 1 and core.count('/*@SITE*/') == 1
    return core.replace('__REGION__', reg.strip()).replace('/*@SITE*/', st.strip())
