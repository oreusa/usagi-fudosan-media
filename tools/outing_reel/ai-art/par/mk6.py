# 11/24 夜 owner「絵適当に流しすぎやろ2つとも」への直し（mk5→mk6：コマを減らした版）
# ・声の1文ごとに、その文が言っている物が写った絵だけを並べる（方丈の庭・灯籠など言っていない物は出さない）
# ・絵ごとに見せ方を決める：橋の中は奥へ深く進む／谷は下から橋へ見上げる／見下ろす景色は上から下へ／葉は寄りから引く
# ・もやと光の筋は朝と夜の絵だけ。ほかはかけない（白くぼやけて見えるため）
# ・大事な絵は長く、添えの絵は短く（重みで秒を分ける）
# python3 mk5.py → tf0..6/tfvi.json・rk0..6/rkvi.json（seven.py で7ページ版にした後の spans.json を使う）
import json, os
U = '/home/user/usagi-fudosan-media/shots'; HF = '/home/user/usagi-fudosan-media/tools/outing_reel/hf'
FLAT = os.path.abspath('flat.png')
def S(set_, name, mv, w=1.0): return dict(img=f'{U}/ai-art/{set_}/{name}.jpg', dep=FLAT, dur=0, m=mv, tr='fade', ease='soft', w=w)
def M(**k):
    m = dict(z0=0, z1=.08, cx=.5, cy=.45, b0=1.12, b1=1.12, ray=0, mist=0, rx=.5, ry=.1, wind=.0045); m.update(k); return m
DEEP = lambda **k: M(**{**dict(z0=0, z1=.30, cy=.42, b0=1.04, b1=1.10), **k})           # 通路・門の奥へ進む
PUSH = lambda **k: M(**{**dict(z0=0, z1=.14, b0=1.04, b1=1.12), **k})                    # ゆっくり寄る
UP = lambda **k: M(**{**dict(z0=0, z1=.04, py0=.06, py1=-.06, b0=1.2, b1=1.2), **k})     # 下から上へ見上げる
DOWN = lambda **k: M(**{**dict(z0=0, z1=.04, py0=-.06, py1=.06, b0=1.2, b1=1.2), **k})   # 上から下へ見下ろす
PULL = lambda **k: M(**{**dict(z0=.20, z1=0, b0=1.16, b1=1.05), **k})                   # 寄りから引いて見せる
LR = lambda d=1, **k: M(**{**dict(z0=0, z1=.05, px0=.05 * d, px1=-.05 * d, b0=1.2, b1=1.22), **k})  # 横に流す
T, R = 'tofukuji1', 'rikugien1'
NIGHT = dict(wind=.003)
# 11/24 20:05 owner「コマが多すぎるんじゃない？無駄に」→ 声1文に絵1〜2枚。1枚を長く見せる
tf = [
 [S(T, '15-autumn-wide', PUSH(), 1)],                                                         # 京都・東福寺 紅葉が見頃（地図のあと）
 [S(T, '08-ravine', UP(), 1), S(T, '03-inside', DEEP(cy=.5), 1)],                              # 谷にかかる屋根のある橋
 [S(T, '01-sea', M(z0=.12, z1=0, py0=-.05, py1=.05, b0=1.2, b1=1.14), 1)],                                                                  # 橋から見下ろす もみじの海
 [S(T, '11-backlit', PULL(ray=.25, rx=.75, ry=.1), 1), S(T, '04-golden', PULL(cy=.4), 1)],     # 三つに分かれる黄金色の通天もみじ
 [S(T, '20-arch', DEEP(), 1), S(T, '16-leaves-wood', LR(1, wind=.002), 1)],  # 混む時期 橋の上の撮影（橋の入口・橋の手すり）
 [S(T, '19-morning', PUSH(ray=.45, mist=.3, rx=.5, ry=.05), 1), S(T, '05-gate', UP(ray=.2, mist=.1, rx=.7), 1)],  # 早朝の特別拝観
 [S(T, '17-hall', UP(), 1), S(T, '13-veranda', DEEP(cy=.5), 1)],                                                                   # 朝8時半から 通天橋・開山堂
]
tvi = [S(T, '09-path', M(z0=0, z1=.12))]                                                      # 案内（行き方）の後ろ
rk = [
 [S(R, '17-overview-night', PUSH(**NIGHT), 1)],                                               # 東京・駒込 六義園 ライトアップ
 [S(R, '10-day-pond', LR(1), 1), S(R, '11-day-maple', LR(-1), 1)],                             # 柳沢吉保の大名庭園
 [S(R, '04-storehouse', PUSH(**NIGHT), 1), S(R, '05-bamboo', UP(**NIGHT), 1)],                 # 土蔵と竹林に光の映像
 [S(R, '06-lightstream', DOWN(**NIGHT), 1)],                                                   # 水香江 流れを光で
 [S(R, '03-teahouse', PUSH(**NIGHT), 1), S(R, '09-matcha', PULL(wind=0), 1)],                  # 吹上茶屋 抹茶と和菓子
 [S(R, '20-leaves-close', PULL(**NIGHT), 1), S(R, '08-mountain', UP(**NIGHT), 1)],               # 約560本が色づく
 [S(R, '19-dusk', PUSH(**NIGHT), 1), S(R, '16-lantern-night', PUSH(**NIGHT), 1)],              # 12/6まで 夜6時〜8時半
]
rvi = [S(R, '14-gate', M(z0=0, z1=.12))]                                                      # 案内（正門だけ）の後ろ
X = .3
for key, L, vi, d in (('tf', tf, tvi, 'tofukuji-1125'), ('rk', rk, rvi, 'rikugien-1125')):
    sp = json.load(open(f'{HF}/{d}/spans.json')); Tm = json.load(open(f'{HF}/{d}/times.json'))
    assert len(sp) == 7, 'seven.py を先に'
    used = [s['img'] for sc in L for s in sc] + [vi[0]['img']]; assert len(used) == len(set(used)), key
    miss = [os.path.basename(u) for u in used if not os.path.exists(u)]; print(key, 'missing', miss)
    L = [[s for s in sc if os.path.exists(s['img'])] for sc in L]
    for k, sh in enumerate(L):
        need = sp[k] + .3
        if k == 0: need = need - 4.2 + .4
        W = sum(s['w'] for s in sh); tot = need + X * (len(sh) - 1)
        for s in sh: s['dur'] = round(tot * s['w'] / W, 3)
        json.dump(sh, open(f'{key}{k}.json', 'w')); print(key, k, [(os.path.basename(s['img'])[:-4], s['dur']) for s in sh])
    T5, T6 = Tm['T'][6], Tm['T'][7]; vi[0]['dur'] = round(T6 + 1.2 - T5 + .5, 2); json.dump(vi, open(f'{key}vi.json', 'w'))
    print(key, 'images', len(used) - len(miss))
