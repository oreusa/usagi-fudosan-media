"""声の読みの答え合わせ（11/12 月。オーナー「漢字読み間違いって直せないの？」）。
11/12 のリールで「まっ赤」を「まっあか」、「山の神社」を「やまのかみしゃ」と読んだまま出した。二度としないための仕組み。
  1. yomi.json の fix（読み間違えた言葉 → ひらがな）を、声の台本に先に当てる。間違いを見つけたら、ここに足していく。
  2. spec の voice_yomi（台本を書いた人が、行ごとにひらがなで書いた正しい読み）と、VOICEVOX が実際に読む音をくらべる。
     1文字でも違えば動画を作らずに止まる（どの行の、どこが違うかを出す）。"""
import json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = json.load(open(HERE + '/yomi.json', encoding='utf-8')).get('fix', {})
VW = {'ア': 'アカサタナハマヤラワガザダバパャァ', 'イ': 'イキシチニヒミリギジヂビピィ', 'ウ': 'ウクスツヌフムユルグズヅブプュゥヴ', 'エ': 'エケセテネヘメレゲゼデベペェ', 'オ': 'オコソトノホモヨロヲゴゾドボポョォ'}


def fix(line):
    for a, b in FIX.items(): line = line.replace(a, b)
    return line


def canon(s):
    """くらべる用にそろえる：カタカナにして、記号を取り、伸ばす音・助詞の「は／へ／を」・「づ／ぢ」の書き方の違いを消す。"""
    s = unicodedata.normalize('NFKC', s)
    s = ''.join(chr(ord(c) + 96) if 'ぁ' <= c <= 'ゖ' else c for c in s)
    s = re.sub(r"[^ァ-ヶー]", '', s)
    s = s.replace('ヲ', 'オ').replace('ヅ', 'ズ').replace('ヂ', 'ジ').replace('ハ', 'ワ').replace('ヘ', 'エ')
    out = ''; pv = ''
    for c in s:
        v = next((x for x, row in VW.items() if c in row), '')
        if c == 'ー' or (c in 'アイウエオ' and pv and (v == pv or (c == 'ウ' and pv == 'オ') or (c == 'イ' and pv == 'エ'))): continue   # 伸ばす音は書かない形にそろえる
        out += c
        if v: pv = v
        elif c not in 'ッン': pv = ''
        if c in 'ッン': pv = ''
    return out


def check(lines, yomi, kana):
    """lines=台本、yomi=正しい読み（ひらがな）、kana=VOICEVOX の読み。違う行の説明の並びを返す（空なら合格）。"""
    bad = []
    if len(yomi) != len(lines): return [f'voice_yomi は voice と同じ {len(lines)} 行で書く（いま {len(yomi)} 行）']
    for n, (l, y, k) in enumerate(zip(lines, yomi, kana)):
        if re.search(r'[0-9０-９一-龥]', y): bad.append(f'{n+1}行目の voice_yomi に数字か漢字がある（全部ひらがなで書く）：{y}'); continue
        a, b = canon(y), canon(k)
        if a != b:
            i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
            bad.append(f'{n+1}行目の読みが違う：台本「{l}」\n   正しい読み {a[:i]}【{a[i:i+6]}】…\n   機械の読み {b[:i]}【{b[i:i+6]}】…\n   → 台本のその言葉をひらがなで書く。直ったら tools/outing_reel/yomi.json の fix にも足す')
    return bad
