# 11/23 勝尾寺：短い形（約20秒）。声の長さから時刻を決めて index.html を作る
# 前の回（談山神社 42秒）から変えた所：最初の1コマから見せ場の絵と大きな字・本は開いた状態で始める・3場面＋最後の紹介を短く
import subprocess, json, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__)); VD = sys.argv[1]
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())
D = [dur(f"{VD}/20-{i:02d}.wav") for i in range(4)]
v = [0.3]; T = []
for k in range(3):
    T.append(round(v[k] + D[k] + .3, 2)); v.append(round(T[-1] + .45, 2))
END = round(v[3] + D[3] + .9, 2)
print("END", END, "T", T, "v", v)
cap = lambda lb, a, b, sm: f'<div class="cap"><span class="w lb">{lb}</span><span class="w">{a}</span><br><span class="w">{b}</span><i class="ul"></i><small class="w">{sm}</small></div>'
def pop(k, layers):
    h = f'<img class="pl kb" src="a/H{k}-b.png">'
    for name, org, cls in layers:
        h += f'<img class="pl {cls}" id="S{k}{name}" src="a/H{k}-{name}.png" style="transform-origin:50% {org}">'
    return f'<div class="pop">{h}<div class="fx" id="fx{k}"></div></div>'
S0 = pop(0, [('m', '1425px', 'up'), ('n', '1425px', 'up'), ('f', '0px', 'fl')])
S1 = pop(1, [('m', '1425px', 'up'), ('n', '1425px', 'up'), ('f', '0px', 'fl')])
S2 = pop(2, [('m', '1425px', 'up'), ('n', '0px', 'lt'), ('f', '1425px', 'up')])
html = open(HERE + "/src/tpl.txt").read()
R = {'@S0@': S0 + cap('OSAKA — KATSUO-JI', '紅葉に、', 'だるまがぎっしり', '大阪・箕面 勝尾寺　いま見頃'),
     '@S1@': S1 + cap('MOMIJI TUNNEL', '本堂への参道は、', '紅葉のトンネル', '拝観 8時〜17時（土曜は18時まで）'),
     '@S2@': S2 + cap('LIGHT UP', '11月29日までの', '土日祝は、夜も', '日没〜20時30分（受付は20時まで）'),
     '@END@': str(END), '@T@': json.dumps(T), '@V@': json.dumps(v)}
aud = '\n'.join(f' <audio id="v{i}" src="a/v{i}.wav" data-start="{v[i]}" data-duration="{round(D[i], 2)}" data-volume="1.7"></audio>' for i in range(4))
aud += '\n' + '\n'.join(f' <audio id="flip{j}" src="a/flip.wav" data-start="{t}" data-duration="0.6" data-volume="0.7"></audio>' for j, t in enumerate(T))
R['@AUDIO@'] = aud
rr = random.Random(1123)
R['@DUST@'] = ''.join(f'<i style="left:{rr.uniform(20,900):.0f}px;top:{rr.uniform(300,1500):.0f}px;width:{(s:=rr.uniform(8,24)):.0f}px;height:{s:.0f}px" data-d="{rr.uniform(160,480):.0f}" data-x="{rr.uniform(-80,80):.0f}"></i>' for _ in range(22))
for a, b in R.items():
    assert html.count(a) >= 1, a; html = html.replace(a, b)
open(HERE + "/index.html", "w").write(html)
json.dump(dict(END=END, T=T, v=v), open(HERE + "/times.json", "w"))
