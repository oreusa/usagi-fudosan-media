"""テクノロジーの型（11/19 月の見本。オーナー「めちゃくちゃテクノロジーなhpと動画」「使える物を組み合わせて」）。
使い方: python3 tech.py spec.json out.mp4 [静止画の時刻 "1,5,9"]
・1本で5か所。始まりは関西の地図が光る線で描かれ、いま開いている数が数え上がる（d3-interpolate の考え方＝数字・色をなめらかに）。
・場所ごとに：本物の写真が画面いっぱい（ゆっくりズーム）＋グリッチで切り替わる＋右上の小さな地図に印＋期間のバーが伸びる＋01/05。
・下に BGM の波形（audiowaveform の考え方。librosa で音の大きさを30分の1秒ごとに取る）。拍で場面が変わる（librosa）。
・声は VOICEVOX（もち子）。読みの答え合わせ（yomi.py）・数字の答え合わせ（factcheck.py）は ニュースの型 と同じ。
・催しの名前・期間・時間・写真は links/assets/mihon.json（毎朝の表＝公式ページから）から取る。台本に数字は書かない。
spec: {"date","brand":"kansai","title":["今週末の関西","行くならここ"],"items":[{"id":"a972a667"},…5つ],"voice":[7行],"voice_yomi":[7行]}
  voice は 1行目＝始まり、2〜6行目＝場所ごと、7行目＝終わり。
1080x1920・30fps。render(t) で1コマずつ描いて ffmpeg でつなぐ（Remotion・HyperFrames と同じ考え方）。"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request, wave, datetime

ROOT = os.environ.get('ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/tools/outing_reel')
import yomi, factcheck
spec = json.load(open(sys.argv[1])); OUT = os.path.abspath(sys.argv[2]); STILL = sys.argv[3] if len(sys.argv) > 3 else ''
T = spec.get('text', {}); VO = spec.get('voice') or []
N = len(VO)
KANTO = spec.get('brand') == 'kanto'
A = ROOT + ('/../akari-auto/site/assets' if KANTO else '/links/assets')
MJ = json.load(open(A + '/mihon.json', encoding='utf-8')); BYID = {o['id']: o for o in MJ.values() if o.get('id')}
IT = [BYID[x['id']] for x in spec.get('items', []) if x.get('id') in BYID]
if len(IT) != len(spec.get('items', [])): sys.exit('items の id が mihon.json に無い')
if N != len(IT) + 2: sys.exit(f'voice は 始まり＋場所{len(IT)}＋終わり＝{len(IT)+2}行')
_fb, _fn = factcheck.run(spec, offline=not os.environ.get('GITHUB_ACTIONS'))
for _n in _fn: print('数字の答え合わせ：' + _n)
if _fb: sys.exit('数字の答え合わせで止めた：\n - ' + '\n - '.join(_fb))
_vlen = sum(len(re.sub(r'[、。！？\s]', '', v)) for v in VO)
if _vlen > 170: sys.exit(f'声が長すぎる：{_vlen}字（170字まで）')
W = os.path.abspath(os.environ.get('WORK', 'tech-work')); os.makedirs(W + '/fr', exist_ok=True)
SP = os.environ.get('SP', '20'); VDIR = os.environ.get('VDIR', '')
VQ = dict(speedScale=1.08, intonationScale=1.15, pitchScale=-0.03, pauseLengthScale=0.6, prePhonemeLength=0.05, postPhonemeLength=0.1)

# ---- 声（機械の中）。行ごとの音の時刻（モーラ）も取る ----
VU = os.environ.get('VOICE_URL', '')
MORA = []   # 行ごとに [[区切りの文字数, [(開始, 長さ), ...]], ...]
def segs(line):
    """字幕の区切り：「、」「。」で分ける（VOICEVOX の息つぎ＝pause_mora と同じ所）"""
    return [s for s in re.split(r'(?<=[、。！？])', line) if s]
if VU and not STILL:
    lines = [yomi.fix(l) for l in VO]
    def vreq(path, data=None):
        r = urllib.request.Request(VU + path, data=data, method='POST' if data is not None else 'GET', headers={'Content-Type': 'application/json'})
        return urllib.request.urlopen(r, timeout=120).read()
    for i in range(150):
        try: vreq('/version'); break
        except Exception: time.sleep(2)
    VDIR = W + '/voice'; os.makedirs(VDIR, exist_ok=True); kana = []
    for n, line in enumerate(lines):
        q = json.loads(vreq(f'/audio_query?speaker={SP}&text=' + urllib.parse.quote(line), b''))
        q.update(VQ); kana.append(q.get('kana', ''))
        open(f'{VDIR}/{SP}-{n:02d}.wav', 'wb').write(vreq(f'/synthesis?speaker={SP}', json.dumps(q).encode()))
        json.dump(q, open(f'{VDIR}/{SP}-{n:02d}.json', 'w'), ensure_ascii=False)
    print('声の読み', json.dumps(kana, ensure_ascii=False))
    bad = yomi.check(lines, spec.get('voice_yomi') or [], kana)
    if bad: sys.exit('声の読みの答え合わせで止めた（動画は作っていない）\n' + '\n'.join(bad))


def timing(n):
    """その行の字幕の区切りごとに、声の始まりと終わり（秒・行の頭から）。息つぎ（pause_mora）で区切りを分ける。"""
    p = f'{VDIR}/{SP}-{n:02d}.json' if VDIR else ''
    sg = segs(VO[n])
    if not p or not os.path.exists(p):
        # 声が無い時（手元）：1文字0.13秒で仮に
        out, t = [], 0.1
        for s in sg: d = len(s) * 0.13; out.append([t, t + d]); t += d + 0.15
        return out
    q = json.load(open(p)); t = q.get('prePhonemeLength', 0.1); groups = [[t, t]]
    for ap in q['accent_phrases']:
        for m in ap['moras']: t += (m.get('consonant_length') or 0) + m['vowel_length']
        groups[-1][1] = t
        if ap.get('pause_mora'):
            t += ap['pause_mora']['vowel_length'] * q.get('pauseLengthScale', 1)
            groups.append([t, t])
    groups = [g for g in groups if g[1] > g[0]]
    # 区切りの数が合わない時は、全体を文字数で分ける
    if len(groups) != len(sg):
        a, b = groups[0][0], groups[-1][1]; tot = sum(len(s) for s in sg); out = []; c = a
        for s in sg: d = (b - a) * len(s) / tot; out.append([c, c + d]); c += d
        return out
    return groups


def dur(n):
    p = f'{VDIR}/{SP}-{n:02d}.wav'
    if not VDIR or not os.path.exists(p): return timing(n)[-1][1] + 0.2
    w = wave.open(p); return w.getnframes() / w.getframerate()


VD = [dur(n) for n in range(N)]
FIRST = 0.9      # 地図の線を先に見せる
GAP = 0.45
ST = []; t = FIRST
for n in range(N): ST.append(t); t += VD[n] + GAP
# 11/18 BGMの拍（librosa）に場面の頭を合わせる：声の頭を「次の拍」まで少し待たせる（最大0.35秒）。拍で絵が変わると気持ちいい
try:
    import librosa
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{t + 6:.1f}', '-ac', '1', '-ar', '22050', f'{W}/beat.wav'], check=True)
    _y, _sr = librosa.load(f'{W}/beat.wav', sr=22050)
    _, _bt = librosa.beat.beat_track(y=_y, sr=_sr); BEATS = [float(x) for x in librosa.frames_to_time(_bt, sr=_sr)]
    sh = 0; ST2 = []
    for n in range(N):
        s0 = ST[n] + sh; nb = [b for b in BEATS if s0 <= b <= s0 + 0.35]
        if nb: sh += nb[0] - s0; s0 = nb[0]
        ST2.append(s0)
    print('拍に合わせた', [round(a - b, 2) for a, b in zip(ST2, ST)]); t += sh; ST = ST2
except Exception as e: print('拍：使わない', str(e)[:80])

END = ST[-1]
TOTAL = t + 1.8
SUB = [{'segs': segs(VO[n]), 'tm': timing(n)} for n in range(N)]
# ---- BGM の波形（30分の1秒ごとの音の大きさ 0〜1、48本の帯に分ける） ----
WAVE = []
try:
    import librosa, numpy as np
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{TOTAL + 1:.1f}', '-ac', '1', '-ar', '22050', f'{W}/wv.wav'], check=True)
    y, sr = librosa.load(f'{W}/wv.wav', sr=22050)
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=735))   # 735 = 22050/30 → 1コマに1列
    mel = librosa.feature.melspectrogram(S=S**2, sr=sr, n_mels=24)
    db = librosa.power_to_db(mel, ref=np.max); v = np.clip((db + 60) / 60, 0, 1)
    WAVE = [[round(float(x), 2) for x in v[:, i]] for i in range(v.shape[1])]
    print('波形', len(WAVE), 'コマ')
except Exception as e: print('波形：使わない', str(e)[:80])
WD = '日月火水木金土'
try:
    d = datetime.date.fromisoformat(spec.get('date', '')[:10]); DATE = d.strftime('%Y.%m.%d'), ['MON','TUE','WED','THU','FRI','SAT','SUN'][d.weekday()]
except ValueError: d = datetime.date.today(); DATE = ('', '')
TD = d.isoformat()
LIVE = sum(1 for o in BYID.values() if o.get('s') and o['s'] <= TD and (not o.get('e') or o['e'] >= TD))
PF = {'大阪': 'osaka', '京都': 'kyoto', '兵庫': 'hyogo', '奈良': 'nara', '滋賀': 'shiga', '和歌山': 'wakayama'}
PATHS = json.load(open(ROOT + '/tools/outing_reel/paths.json')) if not KANTO else {}
MAP = {k: PATHS[v] for k, v in PF.items() if v in PATHS}
def md(s): return f'{int(s[5:7])}/{int(s[8:10])}' if s else ''
items = []
for o in IT:
    s, e = o.get('s', ''), o.get('e', '')
    left = (datetime.date.fromisoformat(e) - d).days if e else None
    frac = 0
    if s and e and e > s: frac = max(0, min(1, (d - datetime.date.fromisoformat(s)).days / (datetime.date.fromisoformat(e) - datetime.date.fromisoformat(s)).days))
    st = (md(s) + 'から') if s and s > TD else ('きょうまで' if left == 0 else f'あと{left}日' if left is not None and left <= 14 else '開催中')
    vp = bool(o.get('vn') and o['vn'] not in o['n'])
    items.append(dict(n=o['n'], hk=o.get('hk', ''), p=o['p'], per=(md(s) + '〜' + md(e)) if s and e and s != e else md(s or e), st=st, frac=round(frac, 3),
                      h=(o.get('h') or '').replace('-', '〜'), vn=o.get('vn', ''), vp=vp, im=f'{A}/ph/{o["im"]}', cr=re.sub(r'（.*', '', o.get('cr', '')),
                      lic=(re.search(r'（([^・）]+)', o.get('cr', '')) or [None, ''])[1]))
P = dict(title=T.get('title', ['', '']), items=items, sub=SUB, st=ST, end=END, total=TOTAL, date=DATE[0], wd=DATE[1], live=LIVE, map=MAP, wave=WAVE,
         site='LIFE NOTE' if KANTO else 'TOWN NOTE', list='関東おでかけリスト' if KANTO else '関西おでかけリスト', region='KANTO' if KANTO else 'KANSAI')
F = ROOT + '/tools/fonts'
LOGO = ROOT + ('/tools/outing_reel/kanto/logo.png' if KANTO else '/tools/brand/logo.png')

html = r"""<!doctype html><html lang="ja"><meta charset="utf-8"><style>
@font-face{font-family:M;src:url(file://%F%/ShipporiMincho-Bold.ttf)}
@font-face{font-family:G;src:url(file://%F%/ZenKakuGothicNew-Bold.ttf)}
@font-face{font-family:GB;src:url(file://%F%/ZenKakuGothicNew-Black.ttf)}
@font-face{font-family:J;src:url(file://%F%/Jost-VF.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#04060A;color:#fff}
:root{--c:#7FE6FF;--w:#FFC46B;--y:#FFE07A}
#grid{position:absolute;inset:-200px;background:
 linear-gradient(rgba(127,230,255,.08) 2px,transparent 2px) 0 0/90px 90px,
 linear-gradient(90deg,rgba(127,230,255,.08) 2px,transparent 2px) 0 0/90px 90px;mask-image:radial-gradient(ellipse 60% 50% at 50% 40%,#000 30%,transparent 75%);-webkit-mask-image:radial-gradient(ellipse 60% 50% at 50% 40%,#000 30%,transparent 75%)}
#glow{position:absolute;inset:0;background:radial-gradient(ellipse 70% 40% at 50% 38%,rgba(60,140,200,.28),transparent 70%)}
.ph{position:absolute;inset:0;overflow:hidden;opacity:0}
.ph img{position:absolute;left:50%;top:50%;height:1920px;width:auto;min-width:1080px;object-fit:cover;will-change:transform;filter:contrast(1.08) saturate(1.1) brightness(.92)}
#shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,6,10,.7) 0%,rgba(4,6,10,0) 20%,rgba(4,6,10,0) 40%,rgba(4,6,10,.6) 58%,rgba(4,6,10,.92) 100%);opacity:0}
#scan{position:absolute;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,var(--c),transparent);box-shadow:0 0 24px 6px rgba(127,230,255,.6);opacity:0}
#lines{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px);pointer-events:none}
.br{position:absolute;width:70px;height:70px;border:3px solid rgba(255,255,255,.75)}
#b1{left:40px;top:40px;border-right:0;border-bottom:0}#b2{right:40px;top:40px;border-left:0;border-bottom:0}#b3{left:40px;bottom:40px;border-right:0;border-top:0}#b4{right:40px;bottom:40px;border-left:0;border-top:0}
#top{position:absolute;left:72px;right:72px;top:78px;display:flex;align-items:center;gap:18px;font:500 26px J;letter-spacing:.28em}
#top i{width:16px;height:16px;border-radius:50%;background:#FF4D4D;box-shadow:0 0 16px #FF4D4D}
#top b{font-weight:600}#top span{margin-left:auto;font:500 26px J;letter-spacing:.12em;color:rgba(255,255,255,.85)}#top em{font-style:normal;color:var(--c);margin-left:14px}
#seg{position:absolute;left:72px;right:72px;top:136px;display:flex;gap:10px}#seg i{flex:1;height:6px;border-radius:3px;background:rgba(255,255,255,.2);overflow:hidden}#seg i b{display:block;height:100%;width:0;background:#fff}
/* 始まり */
#intro{position:absolute;inset:0}
#map{position:absolute;left:90px;top:250px;width:900px;height:900px}
#map path{fill:rgba(127,230,255,0);stroke:var(--c);stroke-width:1.4;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 6px rgba(127,230,255,.8))}
.pin{position:absolute;transform:translate(-50%,-50%)}
.pin i{display:block;width:30px;height:30px;border-radius:50%;background:var(--w);box-shadow:0 0 24px var(--w),0 0 0 6px rgba(255,196,107,.25)}
.pin u{position:absolute;left:50%;top:50%;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid var(--w)}
.pin b{position:absolute;left:44px;top:-22px;white-space:nowrap;font:700 34px G;letter-spacing:.06em;text-shadow:0 2px 12px #000}.pin b small{font:500 26px J;color:var(--w);margin-right:10px;letter-spacing:.1em}
#cnt{position:absolute;left:72px;right:72px;top:1180px;display:flex;align-items:flex-end;gap:26px}
#cnt b{font:300 230px/0.82 J;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:#fff;text-shadow:0 0 40px rgba(127,230,255,.45)}
#cnt span{font:700 38px/1.45 G;padding-bottom:18px}#cnt span small{display:block;font:500 24px J;letter-spacing:.3em;color:var(--c)}
#ttl{position:absolute;left:72px;right:72px;top:1420px}
#ttl div{font:700 112px/1.25 M;letter-spacing:.04em;overflow:hidden;white-space:nowrap}
#ttl div span{display:inline-block}
#ttl div:nth-child(2){color:var(--w)}
/* 場所ごと */
#idx{position:absolute;left:72px;top:190px;font:200 190px/1 J;letter-spacing:-.02em}#idx small{font:400 48px J;color:rgba(255,255,255,.6);margin-left:10px}
#mini{position:absolute;right:72px;top:200px;width:300px;height:300px;border-radius:28px;background:rgba(6,10,16,.55);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:2px solid rgba(127,230,255,.35);overflow:hidden}
#mini svg{position:absolute;inset:16px;width:268px;height:268px}#mini path{fill:rgba(255,255,255,.16);stroke:rgba(127,230,255,.6);stroke-width:1;vector-effect:non-scaling-stroke}#mini path.on{fill:rgba(255,196,107,.75);stroke:var(--w)}
#mini .pin i{width:20px;height:20px}#mini .pin u{width:20px;height:20px;margin:-10px 0 0 -10px}
#mini em{position:absolute;left:18px;bottom:12px;font:500 20px J;letter-spacing:.24em;color:var(--c);font-style:normal}
#hd{position:absolute;left:72px;right:72px;top:840px}
#hd .tg{display:inline-flex;gap:14px;align-items:center;font:900 30px GB;background:var(--w);color:#1a1208;border-radius:999px;padding:12px 26px;margin-bottom:28px;letter-spacing:.06em}
#hd h1{font:700 86px/1.32 M;letter-spacing:.03em;text-shadow:0 4px 30px rgba(0,0,0,.6)}
#hd h1 span{display:inline-block}
#hd .nm{font:700 36px/1.5 G;margin-top:22px;color:rgba(255,255,255,.9)}
#dp{position:absolute;left:72px;right:72px;top:1285px;padding:30px 36px;border-radius:28px;background:rgba(8,12,18,.55);backdrop-filter:blur(22px) saturate(1.3);-webkit-backdrop-filter:blur(22px);border:2px solid rgba(255,255,255,.18)}
#dp .r{display:flex;align-items:baseline;justify-content:space-between;font:500 30px J;letter-spacing:.06em;color:rgba(255,255,255,.75)}
#dp .r b{font:900 54px GB;color:#fff;letter-spacing:.02em}#dp .r b.lv{color:#7CF0A6}
#dp .tr{position:relative;height:12px;border-radius:6px;background:rgba(255,255,255,.14);margin:22px 0 4px;overflow:visible}
#dp .tr i{position:absolute;left:0;top:0;bottom:0;border-radius:6px;background:linear-gradient(90deg,var(--c),var(--w));box-shadow:0 0 18px rgba(127,230,255,.6)}
#dp .tr u{position:absolute;top:-10px;width:6px;height:32px;margin-left:-3px;border-radius:3px;background:#fff;box-shadow:0 0 14px #fff}
#dp .h{margin-top:18px;font:700 30px G;color:rgba(255,255,255,.85)}#dp .h span{font:500 30px J;color:var(--c);margin-left:12px;letter-spacing:.06em}
#sb{position:absolute;left:64px;right:64px;top:1575px;min-height:200px}
#sb p{font:900 50px/1.5 GB;word-break:auto-phrase;letter-spacing:.02em;text-shadow:0 2px 14px rgba(0,0,0,.8)}
#sb p i{font-style:normal;color:rgba(255,255,255,.45)}#sb p i.on{color:#fff}#sb p i.now{color:var(--y);text-shadow:0 0 18px rgba(255,224,122,.6)}
#cr{position:absolute;right:72px;top:518px;max-width:520px;font:500 19px G;color:rgba(255,255,255,.7);text-align:right;text-shadow:0 1px 6px #000}
#wv{position:absolute;left:72px;right:72px;bottom:70px;height:70px;display:flex;align-items:center;gap:6px}
#wv i{flex:1;border-radius:3px;background:linear-gradient(180deg,var(--c),var(--w));box-shadow:0 0 12px rgba(127,230,255,.5);min-height:4px}
/* 終わり */
#endc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(4,6,10,.86);opacity:0}
#endc img{width:200px;height:200px;border-radius:50%;background:#fff;object-fit:contain;padding:16px;box-shadow:0 0 60px rgba(127,230,255,.35)}
#endc .s{font:500 62px J;letter-spacing:.32em;margin-top:44px}#endc .l{font:700 40px M;letter-spacing:.3em;margin-top:18px;color:var(--w)}
#endc .b{margin-top:64px;font:900 40px GB;background:#fff;color:#0a0d12;border-radius:999px;padding:26px 56px;letter-spacing:.04em;box-shadow:0 0 40px rgba(255,255,255,.25)}
#endc .n{font:700 30px G;color:rgba(255,255,255,.8);margin-top:32px;letter-spacing:.06em}
#flash{position:absolute;inset:0;background:#fff;opacity:0;mix-blend-mode:overlay}
</style>
<svg width="0" height="0" style="position:absolute"><filter id="rgb" x="-5%" y="0" width="110%" height="100%">
<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="r"/><feOffset in="r" id="ofr" dx="0" result="r2"/>
<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0" result="g"/>
<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0" result="b"/><feOffset in="b" id="ofb" dx="0" result="b2"/>
<feBlend in="r2" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b2" mode="screen"/></filter></svg>
<div id="grid"></div><div id="glow"></div>
<div id="phs"></div><div id="shade"></div>
<div id="intro"><svg id="map"></svg><div id="pins"></div><div id="cnt"><b id="cn">0</b><span><small>LIVE NOW</small>きょう開催中の<br>おでかけ</span></div><div id="ttl"><div id="t1"></div><div id="t2"></div></div></div>
<div id="item" style="opacity:0"><div id="idx"></div><div id="mini"><svg id="msvg"></svg><div id="mpin"></div><em id="mpf"></em></div>
<div id="hd"><div class="tg" id="htg"></div><h1 id="hh"></h1><div class="nm" id="hn"></div></div>
<div id="dp"><div class="r"><span id="dpa"></span><b id="dps"></b></div><div class="tr"><i id="dpi"></i><u id="dpu"></u></div><div class="h" id="dph"></div></div>
<div id="cr"></div></div>
<div id="sb"><p id="sp"></p></div>
<div id="endc"><img src="file://%LOGO%"><div class="s" id="es"></div><div class="l" id="el"></div><div class="b">日付と地図でさがせます</div><div class="n">プロフィールのリンクから</div></div>
<div id="lines"></div><div id="scan"></div><div id="flash"></div>
<div class="br" id="b1"></div><div class="br" id="b2"></div><div class="br" id="b3"></div><div class="br" id="b4"></div>
<div id="top"><i id="lv"></i><b id="brand"></b><span><span id="dt"></span><em id="clk"></em></span></div>
<div id="seg"></div><div id="wv"></div>
<script>
const P=%P%;const $=i=>document.getElementById(i);const NS='http://www.w3.org/2000/svg';
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)),sm=(t,a,b)=>cl((t-a)/(b-a),0,1),eo=x=>1-Math.pow(1-x,3),eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,spr=x=>x>=1?1:1-Math.exp(-6*x)*Math.cos(9*x);
const lerp=(a,b,k)=>a+(b-a)*k;
$('brand').textContent=P.site+' / '+P.region;$('dt').textContent=P.date+' '+P.wd;$('es').textContent=P.site;$('el').textContent=P.list;
const NI=P.items.length;$('seg').innerHTML=P.items.map(()=>'<i><b></b></i>').join('');
// 地図（大きい・小さい）
const PF=Object.keys(P.map);
function mkmap(svg){PF.forEach(k=>{const p=document.createElementNS(NS,'path');p.setAttribute('d',P.map[k]);p.dataset.p=k;svg.appendChild(p)});const bb=svg.getBBox();const pad=bb.width*.04;svg.setAttribute('viewBox',[bb.x-pad,bb.y-pad,bb.width+pad*2,bb.height+pad*2].join(' '));return bb}
const MS=$('map'),ms=$('msvg');mkmap(MS);mkmap(ms);
const LEN=[...MS.querySelectorAll('path')].map(p=>{const l=p.getTotalLength();p.style.strokeDasharray=l;p.style.strokeDashoffset=l;return l});
function ctr(svg,k,box,size){const p=svg.querySelector('path[data-p="'+k+'"]');if(!p)return[size/2,size/2];const b=p.getBBox(),vb=svg.viewBox.baseVal,s=Math.min(size/vb.width,size/vb.height),ox=(size-vb.width*s)/2,oy=(size-vb.height*s)/2;return[ox+(b.x+b.width/2-vb.x)*s,oy+(b.y+b.height/2-vb.y)*s]}
// 同じ府県の印が重ならないよう少しずらす
const seen={};$('pins').innerHTML=P.items.map((o,i)=>{let [x,y]=ctr(MS,o.p,0,900);const c=seen[o.p]=(seen[o.p]||0)+1;y+=(c-1)*70;return '<div class="pin" style="left:'+(90+x)+'px;top:'+(250+y)+'px"><u></u><i></i><b><small>0'+(i+1)+'</small>'+o.p+'</b></div>'}).join('');
// 写真
$('phs').innerHTML=P.items.map(o=>'<div class="ph"><img src="file://'+o.im+'"></div>').join('');
const PH=[...document.querySelectorAll('.ph')];
// 題の字
function chars(el,s,wrap){let a=[...s],br=-1;if(wrap&&a.length>9){const m=a.length/2;let best=99;a.forEach((c,i)=>{if(i<3||i>a.length-3)return;const sc=('、'===c?0:'のをがにでは'.includes(c)?1:9)*10+Math.abs(i+1-m);if(sc<best){best=sc;br=i}})}el.innerHTML=a.map((c,i)=>'<span>'+(c===' '?'&nbsp;':c)+'</span>'+(i===br?'<br>':'')).join('')}
chars($('t1'),P.title[0]||'');chars($('t2'),P.title[1]||'');
// 波形
$('wv').innerHTML=Array.from({length:48},()=>'<i></i>').join('');const WV=[...$('wv').children];
function subHTML(n){return P.sub[n].segs.map((s,k)=>'<span>'+[...s].map((c,j)=>'<i data-k="'+k+'" data-j="'+j+'">'+c+'</i>').join('')+'</span>').join('')}
let curN=-1,curI=-1;
function setItem(i){const o=P.items[i];$('idx').innerHTML=String(i+1).padStart(2,'0')+'<small>/'+String(NI).padStart(2,'0')+'</small>';
  ms.querySelectorAll('path').forEach(p=>p.classList.toggle('on',p.dataset.p===o.p));const [x,y]=ctr(ms,o.p,0,268);$('mpin').innerHTML='<div class="pin" style="left:'+(16+x)+'px;top:'+(16+y)+'px"><u></u><i></i></div>';$('mpf').textContent=o.p.toUpperCase?o.p:'';
  $('htg').textContent=o.p+'  '+o.st;chars($('hh'),o.hk||o.n,1);$('hn').textContent=o.hk?o.n:'';
  $('dpa').textContent=o.per;$('dps').textContent=o.st;$('dps').className=/あと|きょう/.test(o.st)?'':'lv';$('dph').innerHTML=o.h?'時間<span>'+o.h+'</span>':(o.vn?'場所<span style="font-family:G">'+o.vn+'</span>':'');
  $('cr').textContent=(o.vp?'会場の写真　':'')+'写真：'+o.cr+(o.lic?'（'+o.lic+'）':'')}
function render(t){
  const S=P.st,n=S.filter(s=>t>=s-0.2).length-1;           // いまの声の行
  const it=n>=1&&n<=NI?n-1:(n>NI?NI-1:-1);                  // 場所の番号
  // 時計・LIVE
  const sec=7*3600+30*60+Math.floor(t);$('clk').textContent=[Math.floor(sec/3600),Math.floor(sec/60)%60,sec%60].map(v=>String(v).padStart(2,'0')).join(':');
  $('lv').style.opacity=(0.4+0.6*Math.abs(Math.sin(t*3))).toFixed(2);
  // 区切りのバー
  [...$('seg').children].forEach((e,i)=>{const a=S[i+1],b=S[i+2]||P.end;e.firstChild.style.width=(100*sm(t,a-0.2,b-0.2)).toFixed(1)+'%'});
  // 始まり：地図の線→府県が光る→印→数字→題
  const I=$('intro'),io=1-sm(t,S[1]-0.5,S[1]-0.1);I.style.opacity=io;$('grid').style.opacity=0.4+0.6*io;$('glow').style.opacity=io;
  $('grid').style.transform='translateY('+((t*40)%90)+'px)';
  if(io>0){[...MS.querySelectorAll('path')].forEach((p,i)=>{const k=eio(sm(t,0.05+i*0.08,1.1+i*0.08));p.style.strokeDashoffset=(LEN[i]*(1-k)).toFixed(1);p.style.fill='rgba(127,230,255,'+(0.10*sm(t,1.0+i*0.06,1.6+i*0.06)).toFixed(3)+')'});
    [...$('pins').children].forEach((e,i)=>{const k=spr(sm(t,1.1+i*0.16,1.7+i*0.16));e.style.opacity=Math.min(1,k*2);e.style.transform='translate(-50%,-50%) scale('+Math.max(0,k).toFixed(3)+')';const u=e.querySelector('u'),ph=((t-1.1-i*0.16)%1.2+1.2)%1.2/1.2;u.style.transform='scale('+(1+ph*2.4).toFixed(2)+')';u.style.opacity=(1-ph).toFixed(2)});
    const ck=eo(sm(t,0.5,1.9));$('cn').textContent=Math.round(lerp(0,P.live,ck));$('cnt').style.opacity=sm(t,0.4,0.7);
    ['t1','t2'].forEach((id,r)=>[...$(id).children].forEach((s,j)=>{const k=eo(sm(t,1.3+r*0.3+j*0.045,1.8+r*0.3+j*0.045));s.style.transform='translateY('+((1-k)*110).toFixed(1)+'%)';s.style.opacity=k}))}
  // スキャンの線（始まりと場面の頭）
  let sc=-1;if(t<1.4)sc=sm(t,0.1,1.4);else if(it>=0){const a=S[it+1]-0.2;if(t<a+0.5)sc=sm(t,a,a+0.5)}
  $('scan').style.opacity=sc>=0&&sc<1?0.9:0;$('scan').style.top=(sc*1920).toFixed(0)+'px';
  // 場所ごと
  const IT=$('item');
  if(it>=0&&t<P.end+0.4){if(curI!==it){curI=it;setItem(it)}IT.style.opacity=1-sm(t,P.end-0.1,P.end+0.4);$('shade').style.opacity=1;
    const a=S[it+1]-0.2,b=(S[it+2]||P.end)-0.2,lt=t-a;
    PH.forEach((p,i)=>{const on=i===it,prev=i===it-1;p.style.opacity=on?1:(prev?1-sm(t,a,a+0.25):0);if(on||prev){const z=1.05+0.12*sm(t,on?a:a-5,on?b+0.3:a+0.3),dx=(i%2?-1:1)*2*sm(t,a,b);p.firstChild.style.transform='translate(calc(-50% + '+dx.toFixed(2)+'%),-50%) scale('+z.toFixed(4)+')'}});
    // グリッチ（色ずれ）：場面の頭 0.35 秒
    const g=1-sm(t,a,a+0.35),amp=g>0?(Math.sin(t*90)*0.5+0.5)*40*g:0;PH[it].style.filter=g>0.02?'url(#rgb)':'none';$('ofr').setAttribute('dx',amp.toFixed(1));$('ofb').setAttribute('dx',(-amp).toFixed(1));
    PH[it].style.clipPath=g>0.3?'inset('+(Math.round((Math.sin(t*53)*0.5+0.5)*30))+'% 0 0 0)':'none';
    $('flash').style.opacity=(0.5*(1-sm(t,a,a+0.18))*(t>=a?1:0)).toFixed(3);
    const k1=eo(sm(lt,0.15,0.6));$('idx').style.opacity=k1;$('idx').style.transform='translateX('+((1-k1)*-40).toFixed(1)+'px)';
    const k2=spr(sm(lt,0.25,0.95));$('mini').style.opacity=Math.min(1,k2);$('mini').style.transform='scale('+(0.85+0.15*k2).toFixed(3)+')';
    const mp=$('mpin').querySelector('u');if(mp){const ph=(lt%1.2)/1.2;mp.style.transform='scale('+(1+ph*2.2).toFixed(2)+')';mp.style.opacity=(1-ph).toFixed(2)}
    $('htg').style.opacity=eo(sm(lt,0.2,0.5));[...$('hh').children].forEach((s,j)=>{const k=eo(sm(lt,0.3+j*0.035,0.75+j*0.035));s.style.opacity=k;s.style.transform='translateY('+((1-k)*40).toFixed(1)+'px)';s.style.filter='blur('+((1-k)*10).toFixed(1)+'px)'});
    $('hn').style.opacity=eo(sm(lt,0.7,1.1));
    const k3=spr(sm(lt,0.55,1.3));$('dp').style.opacity=Math.min(1,k3);$('dp').style.transform='translateY('+((1-k3)*60).toFixed(1)+'px)';
    const fr=P.items[it].frac*eio(sm(lt,0.9,2.0));$('dpi').style.width=(fr*100).toFixed(2)+'%';$('dpu').style.left=(fr*100).toFixed(2)+'%';
    $('cr').style.opacity=sm(lt,0.6,1)}
  else{IT.style.opacity=0;if(t<S[1])$('shade').style.opacity=0;PH.forEach(p=>p.style.opacity=t>P.end?p.style.opacity:0)}
  // 字幕：声に合わせて1文字ずつ
  const sn=S.filter(s=>t>=s-0.15).length-1,sp=$('sp');
  sp.style.opacity=sn<=0?0:(sn>=P.sub.length-1?1-sm(t,P.end+0.3,P.end+0.6):1);
  if(sn>=0){if(curN!==sn){curN=sn;sp.innerHTML=subHTML(sn)}const lt=t-S[sn],tm=P.sub[sn].tm,L=P.sub[sn].segs.map(s=>[...s].length);
    sp.querySelectorAll('i').forEach(e=>{const k=+e.dataset.k,j=+e.dataset.j,a=tm[k][0],b=tm[k][1],f=(j+0.5)/L[k],tt=a+(b-a)*f;e.className=lt>=tt?(lt<b+0.05&&lt>=a?'now':'on'):''})}
  // 波形
  const fi=Math.min(P.wave.length-1,Math.round(t*30));const wv=P.wave[fi]||[];
  WV.forEach((e,i)=>{const m=i<24?23-i:i-24,v=wv[m]!=null?wv[m]:0.15+0.1*Math.sin(t*6+i);e.style.height=(6+v*v*64).toFixed(1)+'px';e.style.opacity=(0.45+v*0.55).toFixed(2)});
  // 終わり
  const e=eo(sm(t,P.end-0.1,P.end+0.6));const ec=$('endc');ec.style.opacity=e;ec.style.transform='scale('+(1.04-0.04*e).toFixed(4)+')';
}
render(0);
</script>"""
html = html.replace('%F%', F).replace('%LOGO%', LOGO).replace('%P%', json.dumps(P, ensure_ascii=False))
open(f'{W}/tech.html', 'w').write(html)

open(f'{W}/rec.js', 'w').write(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.setDefaultTimeout(240000);p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://{W}/tech.html',{{timeout:240000}});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{W}/c-'+t+'.jpg',type:'jpeg',quality:85}});}}await b.close();return}}
const fs=require('fs');const A=+(process.env.FR0||0),B=+(process.env.FR1||1e9);for(let i=A;i<30*{TOTAL:.3f}&&i<B;i++){{if(fs.existsSync('{W}/fr/'+String(i).padStart(4,'0')+'.jpg'))continue;await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:'{W}/fr/'+String(i).padStart(4,'0')+'.jpg',type:'jpeg',quality:92}});}}await b.close()}})();""")
print('場面', [round(x, 2) for x in ST], '全体', round(TOTAL, 1), '声', [round(x, 2) for x in VD])
if STILL:
    subprocess.run(['node', f'{W}/rec.js', STILL], check=True); sys.exit()
NF = int(30 * TOTAL) + 1; K = int(os.environ.get('EHON_WORKERS', '3')); ps = []
for i in range(K):
    ps.append(subprocess.Popen(['node', f'{W}/rec.js'], env=dict(os.environ, FR0=str(NF * i // K), FR1=str(NF * (i + 1) // K))))
if any(p.wait() for p in ps): sys.exit('コマを撮れない')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{TOTAL + 1:.2f}', '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '48000', f'{W}/bgm.wav'], check=True)
enc = ['-c:v', 'libx264', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-crf', '21', '-maxrate', '10M', '-bufsize', '20M', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT]
if not (VDIR and os.path.exists(f'{VDIR}/{SP}-00.wav')):
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg', '-i', f'{W}/bgm.wav', '-map', '0:v', '-map', '1:a', '-af', f'afade=t=in:d=0.4,afade=t=out:st={TOTAL-2.2}:d=2.2', '-t', f'{TOTAL:.2f}'] + enc, check=True)
    print(OUT, '（声なし）'); sys.exit()
ins = []; flt = []
for n in range(N):
    ins += ['-i', f'{VDIR}/{SP}-{n:02d}.wav']; flt.append(f'[{n+2}:a]aresample=48000,adelay={int(ST[n]*1000)}:all=1[v{n}]')
flt.append(''.join(f'[v{n}]' for n in range(N)) + f'amix=inputs={N}:normalize=0:duration=longest,volume={os.environ.get("VVOL", "1.7")},apad=whole_dur={TOTAL + 1:.2f},asplit=2[vo][sc]')
flt.append(f'[1:a]afade=t=in:d=0.4,afade=t=out:st={TOTAL-2.2}:d=2.2[bg0]')
flt.append('[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=600:makeup=1[bg]')
flt.append('[bg][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg', '-i', f'{W}/bgm.wav'] + ins +
               ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[a]', '-t', f'{TOTAL:.2f}'] + enc, check=True)
print(OUT)
if os.environ.get('STILLS'): subprocess.run(['node', f'{W}/rec.js', os.environ['STILLS']], check=False)
