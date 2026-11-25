# 11/26 宝厳院・長谷寺：1場面1枚を奥行きで動かす（pv4.cjs＋par4.html）。owner「絵をどんどん足すだけでなく、1枚を動かして」
import json, os, sys
A = '/home/user/akari-auto/shots/ai-art'; DD = sys.argv[1]; HF = '/home/user/usagi-fudosan-media/tools/outing_reel/hf'
def S(img, dep, m, w=1.0): return dict(img=f'{A}/{img}', dep=f'{DD}/{dep}.png', dur=0, m=m, tr='fade', ease='io', w=w)
def M(**k):
    m = dict(z0=0, z1=0, cx=.5, cy=.5, b0=1.06, b1=1.06, ray=0, mist=0, rx=.5, ry=.1, wind=.004, st=.3, shk=.004); m.update(k); return m
F = '-flux-2-klein-4b.jpg'
H = [[S('hogonin2/03-shishiiwa' + F, 'hogonin-03', M(z1=.22, cx=.42, cy=.55, px0=.02, px1=-.02))],          # 苔の中の大岩へ寄る（手前の苔が流れる）
     [S('hogonin1/04-shakkei' + F, 'hogonin-04', M(z1=.06, py0=.05, py1=-.04, b0=1.12, b1=1.12))],           # 庭から奥の嵐山へ見上げる
     [S('hogonin1/01-canopy' + F, 'hogonin-01', M(z1=.10, cx=.5, cy=.35, wind=.009, ray=.35, rx=.55, ry=.05))],  # 真上の紅葉が風で揺れ、光が差す
     [S('hogonin1/05-night-garden' + F, 'hogonin-05', M(z1=.32, cx=.55, cy=.6, wind=.003))]]                 # 夜の飛び石を奥へ
HV = S('hogonin1/07-night-gate' + F, 'hogonin-07', M(z1=.12))
K = [[S('hasedera1/02-pond' + F, 'hasedera-02', M(z1=.08, px0=.025, px1=-.025, wind=.003, wy=.56))],          # 池の映り込みがゆらぐ
     [S('hasedera3/06-grounds' + F, 'hasedera-06', M(z1=.30, cx=.55, cy=.62, wind=.003))],                     # 明かりの参道を奥へ
     [S('hasedera1/03-steps' + F, 'hasedera-03', M(z1=.35, cy=.4, wind=.003), 1.1), S('hasedera2/04-kannondo' + F, 'hasedera-04', M(z1=.10, py0=.03, py1=-.02, b0=1.1, b1=1.1, wind=.003), 1)],  # 石段をのぼる→青い観音堂
     [S('hasedera1/05-ginkgo' + F, 'hasedera-05', M(z1=.12, py0=-.03, py1=.03, b0=1.1, b1=1.1, wind=.003))]]   # 足もとの黄色い落ち葉へ
KV = S('hasedera2/01-gate-night' + F, 'hasedera-01', M(z1=.12))
for key, L, vi, d in (('hg', H, HV, 'hogonin-1126'), ('hs', K, KV, 'hasedera-1126')):
    sp = json.load(open(f'{HF}/{d}/spans.json')); Tm = json.load(open(f'{HF}/{d}/times.json'))
    for k, sh in enumerate(L):
        tot = sp[k] + .3 + .3 * (len(sh) - 1); W = sum(s['w'] for s in sh)
        for s in sh: s['dur'] = round(tot * s['w'] / W, 3)
        json.dump(sh, open(f'{key}{k}.json', 'w')); print(key, k, [(os.path.basename(s['img'])[:12], s['dur']) for s in sh])
    T = Tm['T']; vi['dur'] = round(T[4] + 1.2 - T[3] + .5, 2); json.dump([vi], open(f'{key}vi.json', 'w'))
