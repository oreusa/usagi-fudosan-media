# 11/25 owner「キラキラしてて見てて楽しい何か」→ par5.html（明かりが灯る・光の瞬き・水面のきらめき・舞う葉・光のぼけ）。
# インスタ版（4場面）と TikTok/YouTube 版（8場面・2場面目は地図 map6）の場面表を作る。python3 mk8.py <dd> <出力先>
import json, os, sys
A = '/home/user/akari-auto/shots/ai-art'; DD, OUT = sys.argv[1], sys.argv[2]; HF = '/home/user/usagi-fudosan-media/tools/outing_reel/hf'
F = '-flux-2-klein-4b.jpg'
def M(**k):
    m = dict(z0=0, z1=0, cx=.5, cy=.5, b0=1.06, b1=1.06, wind=.004, st=.3, shk=.004); m.update(k); return m
DAY = dict(spk=.3, lf=.8, bok=0)                 # 昼：葉が舞う・光る所が少し瞬く
NIGHT = dict(spk=1, lf=.35, bok=.7, wind=.003)    # 夜：光が瞬く・暖かい光のぼけ
LIGHTUP = dict(lu0=.12, lu1=1, lut=2.4)           # 「明かりがともる」文：暗い所から灯る
def S(img, dep, m, w=1.0): return dict(img=f'{A}/{img}{F}', dep=f'{DD}/{dep}.png', dur=0, m=m, tr='fade', ease='io', w=w)
I = {  # 絵ごとの動き
 'tunnel': S('hogonin1/02-tunnel', 'hogonin-02', M(z1=.30, cy=.45, **DAY)),
 'rock': S('hogonin2/03-shishiiwa', 'hogonin-03', M(z1=.22, cx=.42, cy=.55, px0=.02, px1=-.02, **DAY)),
 'shakkei': S('hogonin1/04-shakkei', 'hogonin-04', M(z1=.06, py0=.05, py1=-.04, b0=1.12, b1=1.12, **dict(DAY, lf=.5))),
 'canopy': S('hogonin1/01-canopy', 'hogonin-01', M(z1=.10, cy=.35, wind=.009, ray=.35, rx=.55, ry=.05, spk=.5, lf=1)),
 'mossfall': S('hogonin3/08-moss-fall-b', 'hogonin-08', M(z1=.16, cy=.6, px0=-.015, px1=.015, spk=.3, lf=1.2)),
 'night': S('hogonin1/05-night-garden', 'hogonin-05', M(z1=.32, cx=.55, cy=.6, **NIGHT, **LIGHTUP)),
 'nleaves': S('hogonin2/06-night-leaves', 'hogonin-06', M(z1=.12, py0=.03, py1=-.03, b0=1.1, b1=1.1, **NIGHT)),
 'hgvi': S('hogonin1/07-night-gate', 'hogonin-07', M(z1=.12, **NIGHT)),
 'pond': S('hasedera1/02-pond', 'hasedera-02', M(z1=.08, px0=.025, px1=-.025, wy=.56, **NIGHT)),
 'grounds': S('hasedera3/06-grounds', 'hasedera-06', M(z1=.30, cx=.55, cy=.62, **NIGHT, **LIGHTUP)),
 'dusk': S('hasedera4/08-dusk-b', 'hasedera-08', M(z1=.10, px0=.02, px1=-.02, wy=.62, **dict(NIGHT, spk=.7))),
 'steps': S('hasedera1/03-steps', 'hasedera-03', M(z1=.35, cy=.4, **NIGHT)),
 'kannon': S('hasedera2/04-kannondo', 'hasedera-04', M(z1=.10, py0=.03, py1=-.02, b0=1.1, b1=1.1, **NIGHT)),
 'view': S('hasedera4/07-view', 'hasedera-07', M(z1=.10, py0=-.03, py1=.03, b0=1.1, b1=1.1, **dict(NIGHT, spk=1.3, lf=.3))),
 'ginkgo': S('hasedera1/05-ginkgo', 'hasedera-05', M(z1=.12, py0=-.03, py1=.03, b0=1.1, b1=1.1, wind=.003, spk=.5, lf=1, ly=1, bok=.5)),
 'hsvi': S('hasedera2/01-gate-night', 'hasedera-01', M(z1=.12, **NIGHT)),
}
import copy
SETS = {  # キー: (hf ディレクトリ, 場面ごとの絵, 案内の後ろの絵)  'MAP' は地図（ここでは作らない）
 'hgI': ('hogonin-1126', [['rock'], ['shakkei'], ['canopy'], ['night']], 'hgvi'),
 'hsI': ('hasedera-1126', [['pond'], ['grounds'], [('steps', 1.1), ('kannon', 1)], ['ginkgo']], 'hsvi'),
 'hgT': ('hogonin-1126t', [['tunnel'], 'MAP', ['shakkei'], ['rock'], ['canopy'], ['mossfall'], ['night'], ['nleaves']], 'hgvi'),
 'hsT': ('hasedera-1126t', [['pond'], 'MAP', ['grounds'], ['dusk'], ['steps'], ['kannon'], ['view'], ['ginkgo']], 'hsvi'),
}
only = sys.argv[3:] or list(SETS)
for key in only:
    d, L, vi = SETS[key]
    sp = json.load(open(f'{HF}/{d}/spans.json')); T = json.load(open(f'{HF}/{d}/times.json'))['T']; NS = len(L)
    for k, sc in enumerate(L):
        if sc == 'MAP': json.dump(dict(dur=round(sp[k] + .3, 2)), open(f'{OUT}/{key}{k}.map.json', 'w')); continue
        sh = []
        for it in sc:
            nm, w = (it if isinstance(it, tuple) else (it, 1.0)); s = copy.deepcopy(I[nm]); s['w'] = w; s['m']['sd'] = k * 1.7; sh.append(s)
        tot = sp[k] + .3 + .3 * (len(sh) - 1); W = sum(s['w'] for s in sh)
        for s in sh: s['dur'] = round(tot * s['w'] / W, 3)
        json.dump(sh, open(f'{OUT}/{key}{k}.json', 'w'))
    v = copy.deepcopy(I[vi]); v['dur'] = round(T[NS] + 1.2 - T[NS - 1] + .5, 2); json.dump([v], open(f'{OUT}/{key}vi.json', 'w'))
    print(key, NS, [round(x, 2) for x in sp])
