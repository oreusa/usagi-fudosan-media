# 11/25 owner「キラキラしてて見てて楽しい何か」→ par5.html（明かりが灯る・光の瞬き・水面のきらめき・舞う葉・光のぼけ）。
# インスタ版（4場面）と TikTok/YouTube 版（8場面・2場面目は地図 map6）の場面表を作る。python3 mk8.py <dd> <出力先>
import json, os, sys
A = '/home/user/akari-auto/shots/ai-art'; DD, OUT = sys.argv[1], sys.argv[2]; HF = '/home/user/usagi-fudosan-media/tools/outing_reel/hf'
F = '-flux-2-klein-4b.jpg'
def M(**k):
    m = dict(z0=0, z1=0, cx=.5, cy=.5, b0=1.06, b1=1.06, wind=.004, st=.3, shk=.004); m.update(k); return m
DAY = dict(spk=.5, lf=.7, bok=0)                 # 昼：葉が舞う・光る所が少し瞬く
NIGHT = dict(spk=.8, lf=.3, bok=0, wind=.003)    # 夜：光が瞬く・暖かい光のぼけ
LIGHTUP = dict(lu0=.12, lu1=1, lut=2.4)           # 「明かりがともる」文：暗い所から灯る
def S(img, dep, m, w=1.0): return dict(img=f'{A}/{img}{F}', dep=f'{DD}/{dep}.png', dur=0, m=m, tr='fade', ease='io', w=w)
I = {  # 絵ごとの動き
 'tunnel': S('hogonin1/02-tunnel', 'hogonin-02', M(z1=.30, cy=.45, **DAY)),
 'rock': S('hogonin2/03-shishiiwa', 'hogonin-03', M(z1=.22, cx=.42, cy=.55, px0=.02, px1=-.02, **DAY)),
 'shakkei': S('hogonin1/04-shakkei', 'hogonin-04', M(z1=.06, py0=.05, py1=-.04, b0=1.12, b1=1.12, **dict(DAY, lf=.5))),
 'canopy': S('hogonin1/01-canopy', 'hogonin-01', M(z1=.10, cy=.35, wind=.009, ray=.35, rx=.55, ry=.05, spk=.5, lf=.9)),
 'mossfall': S('hogonin3/08-moss-fall-b', 'hogonin-08', M(z1=.16, cy=.6, px0=-.015, px1=.015, spk=.5, lf=1.1)),
 'night': S('hogonin1/05-night-garden', 'hogonin-05', M(z1=.32, cx=.55, cy=.6, **NIGHT, **LIGHTUP)),
 'nleaves': S('hogonin2/06-night-leaves', 'hogonin-06', M(z1=.12, py0=.03, py1=-.03, b0=1.1, b1=1.1, **NIGHT)),
 'hgvi': S('hogonin1/06-night-leaves', 'hogonin-06', M(z1=.12, **NIGHT)),
 'pond': S('hasedera1/02-pond', 'hasedera-02', M(z1=.08, px0=.025, px1=-.025, wy=.56, **NIGHT)),
 'grounds': S('hasedera3/06-grounds', 'hasedera-06', M(z1=.30, cx=.55, cy=.62, **NIGHT, **LIGHTUP)),
 'dusk': S('hasedera4/08-dusk-b', 'hasedera-08', M(z1=.10, px0=.02, px1=-.02, wy=.62, **dict(NIGHT, spk=.6))),
 'steps': S('hasedera1/03-steps', 'hasedera-03', M(z1=.35, cy=.4, **NIGHT)),
 'kannon': S('hasedera2/04-kannondo', 'hasedera-04', M(z1=.24, cy=.55, px0=.025, px1=-.025, py0=.02, py1=-.02, b0=1.1, b1=1.1, **NIGHT)),
 'view': S('hasedera4/07-view', 'hasedera-07', M(z1=.10, py0=-.03, py1=.03, b0=1.1, b1=1.1, **dict(NIGHT, spk=.9, lf=.3))),
 'ginkgo': S('hasedera1/05-ginkgo', 'hasedera-05', M(z1=.12, py0=-.03, py1=.03, b0=1.1, b1=1.1, wind=.003, spk=.5, lf=.8, ly=1, bok=0)),
 'hsvi': S('hasedera2/01-gate-night', 'hasedera-01', M(z1=.12, **NIGHT)),
 'rock0': S('ishiyama1/01-rock', 'ishiyama-01', M(z1=.26, cy=.42, **NIGHT)),
 'sando': S('ishiyama1/02-sando', 'ishiyama-02', M(z1=.34, cy=.5, **NIGHT, **LIGHTUP)),
 'irock': S('ishiyama1/04-rockclose-b', 'ishiyama-04', M(z1=.14, py0=.03, py1=-.03, b0=1.1, b1=1.1, **NIGHT)),
 'tahoto': S('ishiyama1/03-tahoto-b', 'ishiyama-03', M(z1=.18, cy=.4, py0=.02, py1=-.02, b0=1.1, b1=1.1, **NIGHT)),
 'ihondo': S('ishiyama2/05-hondo-b', 'ishiyama-05', M(z1=.12, px0=.025, px1=-.025, b0=1.1, b1=1.1, **NIGHT)),
 'tsukimi': S('ishiyama2/06-river', 'ishiyama-06', M(z1=.08, px0=-.02, px1=.02, wy=.62, **dict(NIGHT, spk=.6))),
 'ilantern': S('ishiyama2/07-fallen-b', 'ishiyama-07', M(z1=.30, cy=.5, **NIGHT)),
 'isvi': S('ishiyama1/02-sando-b', 'ishiyama-02b', M(z1=.12, **NIGHT)),
 'steps0': S('oyama1/01-steps', 'oyama-01', M(z1=.32, cy=.42, **NIGHT)),
 'cable': S('oyama1/02-cable-b', 'oyama-02', M(z1=.22, cy=.5, **NIGHT)),
 'ohondo': S('oyama1/03-hondo', 'oyama-03', M(z1=.14, cy=.45, py0=.02, py1=-.02, b0=1.1, b1=1.1, **NIGHT)),
 'arch': S('oyama1/04-lantern-b', 'oyama-04', M(z1=.30, cy=.4, **NIGHT, **LIGHTUP)),
 'shrine': S('oyama2/05-shrine-b', 'oyama-05', M(z1=.12, px0=.025, px1=-.025, b0=1.1, b1=1.1, **NIGHT)),
 'oview': S('oyama2/06-view', 'oyama-06', M(z1=.10, py0=-.03, py1=.03, b0=1.1, b1=1.1, **dict(NIGHT, spk=.9, lf=.3))),
 'ofree': S('oyama2/07-fallen', 'oyama-07', M(z1=.30, cy=.45, **NIGHT)),
 'hall0': S('kodaiji/01-hall', 'kodaiji-01', M(z1=.24, cy=.45, **NIGHT)),
 'klane': S('kodaiji/02-lane-b', 'kodaiji-02', M(z1=.32, cy=.5, **NIGHT)),
 'kaisan': S('kodaiji/03-kaisan', 'kodaiji-03', M(z1=.14, px0=.025, px1=-.025, b0=1.1, b1=1.1, **NIGHT)),
 'kgarden': S('kodaiji/04-garden', 'kodaiji-04', M(z1=.10, px0=-.02, px1=.02, wy=.62, **NIGHT)),
 'ksand': S('kodaiji/05-sand', 'kodaiji-05', M(z1=.16, cy=.6, **NIGHT)),
 'kmaple': S('kodaiji/06-maple-b', 'kodaiji-06', M(z1=.12, py0=.03, py1=-.03, b0=1.1, b1=1.1, **NIGHT)),
 'kpath': S('kodaiji/07-path', 'kodaiji-07', M(z1=.32, cy=.5, **NIGHT)),
 'kdvi': S('kodaiji/04-garden', 'kodaiji-04', M(z1=.10, **NIGHT)),
 'river0': S('nagatoro/01-river', 'nagatoro-01', M(z1=.12, px0=-.02, px1=.02, wy=.52, **NIGHT)),
 'npark': S('nagatoro/02-park', 'nagatoro-02', M(z1=.30, cy=.5, **NIGHT)),
 'nlit': S('nagatoro/03-lit', 'nagatoro-03', M(z1=.14, cy=.45, **NIGHT, **LIGHTUP)),
 'ncliff': S('nagatoro/04-cliff', 'nagatoro-04', M(z1=.10, py0=-.03, py1=.03, b0=1.1, b1=1.1, wy=.70, **NIGHT)),
 'nreflect': S('nagatoro/05-reflect', 'nagatoro-05', M(z1=.10, px0=.02, px1=-.02, wy=.55, **NIGHT)),
 'nshrine': S('nagatoro/06-shrine', 'nagatoro-06', M(z1=.14, cy=.5, py0=.02, py1=-.02, b0=1.1, b1=1.1, **NIGHT)),
 'npath': S('nagatoro/07-path', 'nagatoro-07', M(z1=.30, cy=.5, **NIGHT)),
 'ngvi': S('nagatoro/05-reflect', 'nagatoro-05', M(z1=.10, **NIGHT)),
 'kb0': S('kitano/01-bridge-b', 'kitano-01b', M(z1=.22, cy=.45, **NIGHT)),
 'kodoi': S('kitano/02-odoi-b', 'kitano-02b', M(z1=.30, cy=.55, **NIGHT)),
 'kmitsu': S('kitano/03-mitsumata-b', 'kitano-03b', M(z1=.12, py0=.03, py1=-.03, b0=1.1, b1=1.1, **NIGHT, **LIGHTUP)),
 'kriver': S('kitano/04-river', 'kitano-04', M(z1=.12, px0=-.02, px1=.02, wy=.60, **NIGHT)),
 'kbridge': S('kitano/01-bridge', 'kitano-01', M(z1=.16, cy=.6, **NIGHT)),
 'khonden': S('kitano/06-honden', 'kitano-06', M(z1=.10, px0=.025, px1=-.025, b0=1.1, b1=1.1, **NIGHT)),
 'ktea': S('kitano/05-teahouse', 'kitano-05', M(z1=.14, cy=.55, **NIGHT)),
 'ktvi': S('kitano/07-path', 'kitano-07', M(z1=.10, **NIGHT)),
 'og0': S('ootaguro/01-gate-b', 'ootaguro-01b', M(z1=.24, cy=.5, **NIGHT)),
 'oginkgo': S('ootaguro/02-ginkgo', 'ootaguro-02', M(z1=.32, cy=.5, **NIGHT)),
 'opond': S('ootaguro/03-pond', 'ootaguro-03', M(z1=.10, px0=-.02, px1=.02, wy=.62, **NIGHT)),
 'ostream': S('ootaguro/04-stream', 'ootaguro-04', M(z1=.20, cy=.6, wy=.70, **NIGHT)),
 'ohouse': S('ootaguro/05-house-b', 'ootaguro-05b', M(z1=.14, cy=.55, **NIGHT, **LIGHTUP)),
 'omaple': S('ootaguro/06-maple', 'ootaguro-06', M(z1=.12, py0=.03, py1=-.03, b0=1.1, b1=1.1, **NIGHT)),
 'opath': S('ootaguro/07-path', 'ootaguro-07', M(z1=.30, cy=.5, **NIGHT)),
 'ogvi': S('ootaguro/03-pond-b', 'ootaguro-03b', M(z1=.10, **NIGHT)),
 'oyvi': S('oyama1/01-steps-b', 'oyama-01b', M(z1=.12, **NIGHT)),
}
import copy
SETS = {  # キー: (hf ディレクトリ, 場面ごとの絵, 案内の後ろの絵)  'MAP' は地図（ここでは作らない）
 'hgI': ('hogonin-1126', [['rock'], ['shakkei'], ['canopy'], ['night']], 'hgvi'),
 'hsI': ('hasedera-1126', [['pond'], ['grounds'], [('steps', 1.1), ('kannon', 1)], ['ginkgo']], 'hsvi'),
 'hgT': ('hogonin-1126t', [['tunnel'], 'MAP', ['shakkei'], ['rock'], ['canopy'], ['mossfall'], ['night'], ['nleaves']], 'hgvi'),
 'isN': ('ishiyama-1126n', [['rock0'], 'MAP', ['sando'], ['irock'], ['tahoto'], ['ihondo'], ['tsukimi'], ['ilantern']], 'isvi'),
 'kdN': ('kodaiji-1127n', [['hall0'], 'MAP', ['klane'], ['kaisan'], ['kgarden'], ['ksand'], ['kmaple'], ['kpath']], 'kdvi'),
 'ngN': ('nagatoro-1127n', [['river0'], 'MAP', ['npark'], ['nlit'], ['ncliff'], ['nreflect'], ['nshrine'], ['npath']], 'ngvi'),
 'oyN': ('oyama-1126n', [['steps0'], 'MAP', ['cable'], ['ohondo'], ['arch'], ['shrine'], ['oview'], ['ofree']], 'oyvi'),
 'ktN': ('kitano-1128n', [['kb0'], 'MAP', ['kodoi'], ['kmitsu'], ['kriver'], ['kbridge'], ['khonden'], ['ktea']], 'ktvi'),
 'ogN': ('ootaguro-1128n', [['og0'], 'MAP', ['oginkgo'], ['opond'], ['ostream'], ['ohouse'], ['omaple'], ['opath']], 'ogvi'),
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
