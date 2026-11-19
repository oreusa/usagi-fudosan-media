# 11/21 鶏足寺：声の長さから場面の時刻を決めて index.html を作る（好古園 11/20 の型を土台に）
# 上げた所：本の中の絵を「切り紙の飛び出す層」に（層ごとに起き上がる・紙の縁と影）、場面の中で物が動く（バス・歩く二人・色づく古木）、最後の止まりを短く
import subprocess, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); VD = sys.argv[1]
def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())
D = [dur(f"{VD}/20-{i:02d}.wav") for i in range(6)]
v = [1.8]; T = []
for k in range(5):
    T.append(round(v[k] + D[k] + .35, 2)); v.append(round(T[-1] + .6, 2))
END = round(v[5] + D[5] + 1.2, 2)
print("END", END, "T", T, "v", v)
# バスの道（b に描いた道の中心線）
def bz(t, P):
    a = 1 - t; return [a**3*P[0][i] + 3*a*a*t*P[1][i] + 3*a*t*t*P[2][i] + t**3*P[3][i] for i in (0, 1)]
P = [(250, 1425), (400, 1150), (520, 900), (461, 692)]
bus = []
for k in range(9):
    t = 1 - k / 8 * .62; x, y = bz(t, P); s = .07 + (y - 692) / (1425 - 692) * .9
    bus.append(dict(x=round(x - 120, 1), y=round(y - 210, 1), scale=round(s, 3)))
cap = lambda dk, a, b, sm: f'<div class="cap{" dk" if dk else ""}"><span class="w">{a}</span><span class="w">{b}</span><i class="ul"></i><small class="w">{sm}</small></div>'
def pop(sid, layers):
    h = f'<img class="pl" src="a/{sid}-b.png">'
    for name, org in layers:
        h += f'<img class="pl up" id="{sid}{name}" src="a/{sid}-{name}.png" style="transform-origin:50% {org}">'
    return f'<div class="pop">{h}</div>'
S0 = pop('S0', [('m', '830px'), ('n', '1425px'), ('f', '1425px')])
S1 = '<div class="pop"><img class="pl" src="a/S1-b.png"><img class="pl up" id="S1m" src="a/S1-m.png" style="transform-origin:50% 760px"><img id="bus" src="a/S1-bus.png"><img class="pl up" id="S1n" src="a/S1-n.png" style="transform-origin:50% 1240px"><img class="pl up" id="S1f" src="a/S1-f.png" style="transform-origin:50% 1425px"></div>'
S2 = '<div class="pop"><img class="pl" src="a/S2-b.png"><img id="ppl" src="a/S2-ppl.png"><img class="pl up" id="S2m" src="a/S2-m.png" style="transform-origin:50% 1165px"><img class="pl up" id="S2n" src="a/S2-n.png" style="transform-origin:50% 1425px"><img class="pl dn" id="S2f" src="a/S2-f.png" style="transform-origin:50% 0px"></div>'
S3 = '<div class="pop"><img class="pl" src="a/S3-b.png"><img class="pl up" id="S3m0" src="a/S3-m0.png" style="top:60px;transform-origin:50% 930px"><img class="pl" id="S3m1" src="a/S3-m1.png" style="top:60px;opacity:0;transform-origin:50% 930px"><img class="pl up" id="S3n" src="a/S3-n.png" style="transform-origin:50% 1160px"><img class="pl up" id="S3f" src="a/S3-f.png" style="transform-origin:50% 1425px"><div id="sun"></div></div>'
html = open(HERE + "/src/tpl.txt").read()
R = {'@S0@': S0 + cap(0, '石段が、', 'もみじの赤い道に', '滋賀・長浜 鶏足寺　12月3日まで'),
     '@S1@': S1 + cap(1, '駅からバス、', '古橋から歩いて', 'JR木ノ本駅からバスで約10分'),
     '@S2@': S2 + cap(0, '大門跡から見る、', 'もみじの参道', '約200本のもみじの古木が並ぶ'),
     '@S3@': S3 + cap(1, '見頃は', '11月下旬から', '19日は色づき始め・混むのは土日祝の10〜14時'),
     '@END@': str(END), '@T@': json.dumps(T), '@V@': json.dumps(v), '@BUS@': json.dumps(bus)}
aud = '\n'.join(f' <audio id="v{i}" src="a/v{i}.wav" data-start="{v[i]}" data-duration="{round(D[i], 2)}" data-volume="1.7"></audio>' for i in range(6))
aud += '\n' + '\n'.join(f' <audio id="flip{j}" src="a/flip.wav" data-start="{t}" data-duration="0.6" data-volume="0.7"></audio>' for j, t in enumerate(T))
R['@AUDIO@'] = aud
for a, b in R.items():
    assert html.count(a) >= 1, a; html = html.replace(a, b)
open(HERE + "/index.html", "w").write(html)
json.dump(dict(END=END, T=T, v=v), open(HERE + "/times.json", "w"))
