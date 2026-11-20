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
cap = lambda lb, a, b, sm: f'<div class="cap"><span class="w lb">{lb}</span><span class="w">{a}</span><br><span class="w">{b}</span><i class="ul"></i><small class="w">{sm}</small></div>'
# 11/20 作り直し：4場面とも H（光と空気で描いた絵）。層は奥から起き上がる
def pop(k, layers, extra=''):
    h = f'<img class="pl kb" src="a/H{k}-b.png">'
    for name, org, cls in layers:
        h += f'<img class="pl {cls}" id="S{k}{name}" src="a/H{k}-{name}.png" style="transform-origin:50% {org}">'
    return f'<div class="pop">{h}{extra}</div>'
S0 = pop(0, [('m', '830px', 'up'), ('n', '1425px', 'up'), ('f', '0px', 'fl')])
S1 = pop(1, [('m', '1425px', 'up'), ('n', '1425px', 'up'), ('f', '1425px', 'fl')])
S2 = pop(2, [('m', '1425px', 'up'), ('n', '980px', 'drop'), ('f', '0px', 'lt')])
S3 = pop(3, [('m', '1425px', 'up'), ('n', '1425px', 'up'), ('f', '0px', 'fl')])
html = open(HERE + "/src/tpl.txt").read()
R = {'@S0@': S0 + cap('SHIGA — KEISOKU-JI', '真っ赤な', '石段をのぼる', '滋賀・長浜 鶏足寺　12月3日まで'),
     '@S1@': S1 + cap('LOOK UP', '見上げれば、', 'もみじの天井', '約200本のもみじの古木'),
     '@S2@': S2 + cap('AT YOUR FEET', '苔の緑に、', '散った赤', '見頃は11月下旬からの予想'),
     '@S3@': S3 + cap('MORNING LIGHT', '朝のうちに、', '光の参道へ', '混むのは晴れた土日祝の10〜14時'),
     '@END@': str(END), '@T@': json.dumps(T), '@V@': json.dumps(v)}
aud = '\n'.join(f' <audio id="v{i}" src="a/v{i}.wav" data-start="{v[i]}" data-duration="{round(D[i], 2)}" data-volume="1.7"></audio>' for i in range(6))
aud += '\n' + '\n'.join(f' <audio id="flip{j}" src="a/flip.wav" data-start="{t}" data-duration="0.6" data-volume="0.7"></audio>' for j, t in enumerate(T))
R['@AUDIO@'] = aud
import random; rr = random.Random(1121)
R['@DUST@'] = ''.join(f'<i style="left:{rr.uniform(20,900):.0f}px;top:{rr.uniform(300,1500):.0f}px;width:{(s:=rr.uniform(8,26)):.0f}px;height:{s:.0f}px" data-d="{rr.uniform(160,520):.0f}" data-x="{rr.uniform(-80,80):.0f}"></i>' for _ in range(26))
for a, b in R.items():
    assert html.count(a) >= 1, a; html = html.replace(a, b)
open(HERE + "/index.html", "w").write(html)
json.dump(dict(END=END, T=T, v=v), open(HERE + "/times.json", "w"))
