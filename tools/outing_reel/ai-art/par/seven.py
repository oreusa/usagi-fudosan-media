# 11/24 夜 owner「絵適当に流しすぎ」：案内ページで声2文（時間・行き方）を止めた絵の上で読んでいた。
# 声7文目（時間・料金）にも絵のページを1枚足し、案内ページは最後の1文（行き方）だけにする。
# python3 seven.py <hfディレクトリ> 'LABEL|1行目|2行目|小さい字'   （build-3d.py が作った index.html を書き換える。1回だけ）
import json, re, subprocess, sys
D_, CAP = sys.argv[1], sys.argv[2].split('|')
H = open(f'{D_}/index.html').read()
assert 'id="s8"' not in H, 'もう7ページ版'
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())
D = [dur(f'{D_}/a/w{i}.wav') for i in range(9)]
def plan(extra):
    v = [1.8]; T = []
    for k in range(7):
        T.append(round(v[k] + D[k] + .45 + extra, 2)); v.append(round(T[-1] + .6, 2))
    T.append(round(v[7] + D[7] + .9, 2)); v.append(round(T[-1] + .7, 2))
    return v, T, round(v[8] + D[8] + 2.0, 2)
lo, hi = 0.0, 3.0
for _ in range(30):
    mid = (lo + hi) / 2; e = plan(mid)[2]; lo, hi = (mid, hi) if e < 63.0 else (lo, mid)
v, T, END = plan(round(lo, 2)); END = 63.0 if END < 63 else END
print('END', END, 'T', T, 'v', v)
# ページの付け替え：リスト s7→s8、案内 s6→s7、新しい s6（声6）
H = H.replace('id="s7" style="z-index:0"', 'id="s8" style="z-index:0"').replace('id="s6" style="z-index:1"', 'id="s7" style="z-index:1"')
s5 = re.search(r'  <div class="sc" id="s5".*?</div><div class="bk"></div></div>\n', H, re.S).group(0)
cap = f'<div class="cap"><span class="w lb">{CAP[0]}</span><span class="w">{CAP[1]}</span><br><span class="w">{CAP[2]}</span><i class="ul"></i><small class="w">{CAP[3]}</small></div>'
s6 = re.sub(r'<div class="cap">.*?</small></div>', cap, s5, flags=re.S).replace('id="s5" style="z-index:3"', 'id="s6" style="z-index:2"').replace('id="e5"', 'id="e6"').replace('a/v5.mp4', 'a/v6.mp4')
H = H.replace('  <div class="sc" id="s7"', s6 + '  <div class="sc" id="s7"', 1)
# 映像の出る時間
def setclip(k, st, du):
    global H
    H = re.sub(rf'(src="a/v{k}\.mp4" muted data-start=")[0-9.]+(" data-duration=")[0-9.]+', rf'\g<1>{st}\g<2>{du}', H)
for k in range(7):
    st = 0.8 if k == 0 else T[k - 1]; setclip(k, st, round(T[k] + .7 - st, 2))
H = re.sub(r'(src="a/vvi\.mp4" muted data-start=")[0-9.]+(" data-duration=")[0-9.]+', rf'\g<1>{T[6]}\g<2>{round(T[7] + 1.2 - T[6], 2)}', H)
# 声とめくりの音
for i in range(9):
    H = re.sub(rf'(<audio id="v{i}" src="a/w{i}\.wav" data-start=")[0-9.]+', rf'\g<1>{v[i]}', H)
H = re.sub(r' <audio id="flip\d+"[^\n]*\n', '', H)
fl = ''.join(f' <audio id="flip{j}" src="a/flip.wav" data-start="{t}" data-duration="0.6" data-volume="0.7"></audio>\n' for j, t in enumerate(T))
H = H.replace(' <audio id="v8"', fl + ' <audio id="v8"', 1) if False else re.sub(r'( <audio id="v8"[^\n]*\n)', lambda m: m.group(1) + fl, H, 1)
# JS
H = re.sub(r'const T=\[[^\]]*\],V=\[[^\]]*\],END=[0-9.]+;', f'const T={json.dumps(T)},V={json.dumps(v)},END={END};', H)
j0 = H.index('<script>', H.index('const T=') - 400) if False else H.index('const T=')
js = H[j0:]
js = js.replace('T[6]', 'T[@7]').replace('T[5]', 'T[6]').replace('T[@7]', 'T[7]')
js = js.replace('const turns=[0,1,2,3,4,5,6]', 'const turns=[0,1,2,3,4,5,6,7]').replace('[0,1,2,3,4,5].', '[0,1,2,3,4,5,6].')
js = js.replace('#s6 .info', '#s7 .info').replace('if(k<6){', 'if(k<7){').replace('T.slice(0,6)', 'T.slice(0,7)')
H = H[:j0] + js
H = H.replace('data-duration="63.0"', f'data-duration="{END}"', 1)
open(f'{D_}/index.html', 'w').write(H)
sp = [round((T[k] + .7) - (0.8 if k == 0 else T[k - 1]), 2) for k in range(7)]
json.dump(sp, open(f'{D_}/spans.json', 'w')); json.dump(dict(END=END, T=T, v=v), open(f'{D_}/times.json', 'w'))
print('spans', sp, 'left', re.findall(r'\[0,1,2,3,4,5\]', js))
