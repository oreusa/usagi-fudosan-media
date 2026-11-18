"""写真のおでかけニュース（11/18 月の見本。オーナー「本気のリール」「ニュースみたいなのが素敵」）。
使い方: python3 news.py spec.json out.mp4 [静止画の時刻 "1,5,9"]
・本物の会場の写真を画面いっぱいに（ゆっくりズームしながら場面ごとに見る所が動く）。写真は Wikimedia Commons の元の大きな写真を取りに行く（機械の中だけ）。
・声は VOICEVOX（もち子）。声の読みの答え合わせ（yomi.py）と数字の答え合わせ（factcheck.py）は絵本の型と同じ。
・字幕は声に合わせて1文字ずつ色が変わる（VOICEVOX の音の長さ＝モーラの時刻から。文字起こしの機械は使わない＝ずれない）。
spec は絵本の型と同じ欄（voice・voice_yomi・facts・text.title・text.corner・text.place）に、写真と札を足す：
  "photo": {"venue": "永観堂"}  … tools/new/venue_photos.json の会場（写真と撮った人の名前）
  "text": {"cards": [[], [["期間","11/20〜12/6"],["受付","夜5時半〜8時半"]], ...]}  … 声の行ごとの札（無い行は字幕だけ）
1080x1920・30fps。render(t) で1コマずつ描いて ffmpeg でつなぐ（ehon.py と同じ流れ）。"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request, wave, datetime

ROOT = os.environ.get('ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/tools/outing_reel')
import yomi, factcheck
spec = json.load(open(sys.argv[1])); OUT = os.path.abspath(sys.argv[2]); STILL = sys.argv[3] if len(sys.argv) > 3 else ''
T = spec.get('text', {}); VO = spec.get('voice') or []
N = len(VO)
if N < 3: sys.exit('voice が足りない（3行以上）')
_fb, _fn = factcheck.run(spec, offline=not os.environ.get('GITHUB_ACTIONS'))
for _n in _fn: print('数字の答え合わせ：' + _n)
if _fb: sys.exit('数字の答え合わせで止めた：\n - ' + '\n - '.join(_fb))
_vlen = sum(len(re.sub(r'[、。！？\s]', '', v)) for v in VO)
if _vlen > 150: sys.exit(f'声が長すぎる：{_vlen}字（150字まで）')
W = os.path.abspath(os.environ.get('WORK', 'news-work')); os.makedirs(W + '/fr', exist_ok=True)
SP = os.environ.get('SP', '20'); VDIR = os.environ.get('VDIR', '')
VQ = dict(speedScale=1.0, intonationScale=1.15, pitchScale=-0.03, pauseLengthScale=0.7, prePhonemeLength=0.05, postPhonemeLength=0.1)

# ---- 写真 ----
VP = json.load(open(ROOT + '/tools/new/venue_photos.json', encoding='utf-8'))
ven = (spec.get('photo') or {}).get('venue', '')
if ven not in VP: sys.exit(f'写真：venue_photos.json に「{ven}」が無い')
V = VP[ven]; CREDIT = re.sub(r'（.*', '', V['cr']); LIC = (re.search(r'（([^・）]+)', V['cr']) or [None, ''])[1]
PH = f'{ROOT}/links/assets/ph/{V["img"]}'
def big_photo():
    """Commons の元の写真を縦2400pxで取る（手元の写真は横1200px＝縦の画面いっぱいだと粗い）。取れなければ手元の写真。"""
    m = re.search(r'/wiki/(File:[^?#]+)', V.get('page', ''))
    if not m: return PH
    try:
        api = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|size&iiurlheight=2400&titles=' + urllib.parse.quote(urllib.parse.unquote(m.group(1)))
        H = {'User-Agent': 'town-note-reel/1.0'}
        j = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers=H), timeout=30).read())
        ii = next(iter(j['query']['pages'].values()))['imageinfo'][0]
        u = ii.get('thumburl') or ii['url']
        b = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60).read()
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(b)).convert('RGB'); im.save(f'{W}/photo.jpg', quality=93)
        print('写真（元の大きさ）', im.size, u[:90]); return f'{W}/photo.jpg'
    except Exception as e:
        print('写真：元の写真が取れないので手元の写真', e); return PH
PHOTO = big_photo() if os.environ.get('GITHUB_ACTIONS') else PH

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
FIRST = 1.3      # 写真と見出しを先に見せる
GAP = 0.55
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
END = ST[-1]     # 最後の行（あしたも〜）から、終わりの札
TOTAL = t + 1.6
SUB = [{'segs': segs(VO[n]), 'tm': timing(n)} for n in range(N)]
WD = '日月火水木金土'
try:
    d = datetime.date.fromisoformat(spec.get('date', '')[:10]); DATE = f'{d.month}/{d.day}', WD[(d.weekday() + 1) % 7]
except ValueError: DATE = ('', '')
KANTO = spec.get('brand') == 'kanto'
P = dict(title=T.get('title', ['', ''])[-1], corner=T.get('corner', ''), place=T.get('place', ''), cards=T.get('cards', []), sub=SUB, st=ST, end=END, total=TOTAL,
         date=DATE[0], wd=DATE[1], credit=f'写真'+(spec.get('photo') or {}).get('note','')+f'：{CREDIT}（{LIC}・Wikimedia Commons）', site='LIFE NOTE' if KANTO else 'TOWN NOTE',
         list='関東おでかけリスト' if KANTO else '関西おでかけリスト', tab=spec.get('tab', ''), focus=(spec.get('photo') or {}).get('focus', [50, 50]))
F = ROOT + '/tools/fonts'
LOGO = ROOT + ('/tools/outing_reel/kanto/logo.png' if KANTO else '/tools/brand/logo.png')
html = r"""<!doctype html><html lang="ja"><meta charset="utf-8"><style>
@font-face{font-family:M;src:url(file://%F%/ShipporiMincho-Bold.ttf)}
@font-face{font-family:G;src:url(file://%F%/ZenKakuGothicNew-Bold.ttf)}
@font-face{font-family:GB;src:url(file://%F%/ZenKakuGothicNew-Black.ttf)}
@font-face{font-family:J;src:url(file://%F%/Jost-VF.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#120e0b;color:#fff}
#ph{position:absolute;inset:0;overflow:hidden}
#ph img{position:absolute;left:50%;top:50%;height:1920px;width:auto;min-width:1080px;object-fit:cover;will-change:transform}
#sh1{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,7,5,.62) 0%,rgba(10,7,5,0) 22%,rgba(10,7,5,0) 46%,rgba(10,7,5,.55) 66%,rgba(10,7,5,.9) 100%)}
#bar{position:absolute;left:64px;right:64px;top:118px;display:flex;align-items:center;gap:18px}
#tag{font:900 34px GB;letter-spacing:.08em;background:#C0563C;color:#fff;padding:14px 26px 15px;border-radius:10px;box-shadow:0 10px 30px -10px rgba(0,0,0,.6)}
#dt{font:500 34px J;letter-spacing:.08em;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.5)}#dt b{font:700 30px G;margin-left:8px}
#live{margin-left:auto;display:flex;align-items:center;gap:12px;font:500 24px J;letter-spacing:.3em;color:rgba(255,255,255,.88)}
#live i{width:14px;height:14px;border-radius:50%;background:#ff5a4a;box-shadow:0 0 0 0 rgba(255,90,74,.6)}
#cr{position:absolute;right:40px;top:206px;font:500 19px G;color:rgba(255,255,255,.72);text-shadow:0 1px 6px rgba(0,0,0,.6);max-width:560px;text-align:right}
#hd{position:absolute;left:64px;right:64px;top:1010px}
#hd .k{font:500 26px J;letter-spacing:.34em;color:#F1C9A8;margin-bottom:22px;display:flex;align-items:center;gap:18px}#hd .k:after{content:"";height:2px;width:80px;background:#F1C9A8}
#hd h1{font:700 104px/1.22 M;letter-spacing:.04em;text-shadow:0 4px 30px rgba(0,0,0,.45)}
#hd .pl{font:700 32px G;color:rgba(255,255,255,.9);margin-top:22px;letter-spacing:.04em}
#cd{position:absolute;left:64px;right:64px;top:1080px;display:flex;flex-direction:column;gap:16px}
.cd{display:flex;align-items:baseline;gap:26px;padding:26px 34px;border-radius:22px;background:rgba(22,16,12,.5);backdrop-filter:blur(22px) saturate(1.2);-webkit-backdrop-filter:blur(22px);border:1.5px solid rgba(255,255,255,.22);box-shadow:0 20px 50px -20px rgba(0,0,0,.6)}
.cd span{font:700 30px G;color:#F1C9A8;min-width:96px;letter-spacing:.06em}.cd b{font:900 52px/1.25 GB;letter-spacing:.02em}
.cd.note b{font:700 40px/1.45 G}
#sb{position:absolute;left:56px;right:56px;top:1500px;min-height:240px;display:flex;align-items:flex-start}
#sb p{font:900 54px/1.5 GB;word-break:auto-phrase;line-break:strict;letter-spacing:.02em;text-shadow:0 2px 14px rgba(0,0,0,.6)}
#sb p i{font-style:normal;color:rgba(255,255,255,.5)}#sb p i.on{color:#fff}#sb p i.now{color:#FFD86B}
#endc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(14,10,8,.72);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);opacity:0}
#endc img{width:220px;height:220px;border-radius:50%;background:#fff;object-fit:contain;padding:18px}
#endc .s{font:500 64px J;letter-spacing:.32em;margin-top:44px}#endc .l{font:700 40px M;letter-spacing:.3em;margin-top:18px;color:#F1C9A8}
#endc .b{margin-top:70px;font:900 40px GB;background:#fff;color:#2B2622;border-radius:999px;padding:26px 56px;letter-spacing:.04em}
#endc .n{font:700 30px G;color:rgba(255,255,255,.8);margin-top:34px;letter-spacing:.06em}
#prog{position:absolute;left:64px;right:64px;top:96px;height:5px;border-radius:3px;background:rgba(255,255,255,.22);overflow:hidden}#prog i{display:block;height:100%;background:#fff;transform-origin:0 50%}
</style>
<div id="ph"><img id="im" src="file://%PHOTO%"></div><div id="sh1"></div>
<div id="prog"><i id="pb"></i></div>
<div id="bar"><div id="tag">おでかけニュース</div><div id="dt"></div><div id="live"><i id="lv"></i>NEWS</div></div>
<div id="cr"></div>
<div id="hd"><div class="k" id="hk"></div><h1 id="h1"></h1><div class="pl" id="hp"></div></div>
<div id="cd"></div>
<div id="sb"><p id="sp"></p></div>
<div id="endc"><img src="file://%LOGO%"><div class="s" id="es"></div><div class="l" id="el"></div><div class="b">日付と地図でさがせます</div><div class="n">プロフィールのリンクから</div></div>
<script>
const P=%P%;const $=i=>document.getElementById(i);
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)),sm=(t,a,b)=>cl((t-a)/(b-a),0,1),eo=x=>1-Math.pow(1-x,3),eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,spr=x=>x>=1?1:1-Math.exp(-6*x)*Math.cos(9*x);
$('dt').innerHTML=P.date+'<b>（'+P.wd+'）</b>';$('cr').textContent=P.credit;$('hk').textContent=P.corner;$('h1').textContent=P.title;$('hp').textContent=P.place;
$('es').textContent=P.site;$('el').textContent=P.list;
// 字幕：区切りごとに1文字ずつ <i>
function subHTML(n){return P.sub[n].segs.map((s,k)=>'<span style="display:block">'+[...s].map((c,j)=>'<i data-k="'+k+'" data-j="'+j+'">'+c+'</i>').join('')+'</span>').join('')}
let curN=-1;const IM=$('im');
function render(t){
  // 写真：全体でゆっくりズーム＋場面ごとに見る所が少し動く（同じ写真でも止まって見えない）
  const z=1.06+0.16*(t/P.total),n=P.st.filter(s=>t>=s-0.25).length-1;
  const pans=[[0,0],[-3,-2],[3,-1],[-2,2],[2,1],[0,-2],[-3,1],[2,-2]];
  let px=0,py=0;for(let i=0;i<pans.length;i++){const s=i?P.st[i-1]||P.total:0;const k=eio(sm(t,s-.2,s+1.4));px+= (pans[i][0]-(i?pans[i-1][0]:0))*k;py+=(pans[i][1]-(i?pans[i-1][1]:0))*k}
  IM.style.transform=`translate(calc(-50% + ${px}%),calc(-50% + ${py}%)) scale(${z.toFixed(4)})`;IM.style.objectPosition=P.focus[0]+'% '+P.focus[1]+'%';
  $('pb').style.transform=`scaleX(${(t/P.total).toFixed(4)})`;
  $('lv').style.opacity=(0.55+0.45*Math.abs(Math.sin(t*2.4))).toFixed(2);
  // 見出し：最初の行だけ
  const h=eo(sm(t,0.25,1.05))*(1-sm(t,P.st[1]-0.35,P.st[1]+0.1));const hd=$('hd');hd.style.opacity=h;hd.style.transform=`translateY(${(1-eo(sm(t,0.25,1.05)))*40}px)`;
  // 札：その行の札（ガラスの板）が下から出る
  const cn=n>=1&&n<P.st.length-1?n:-1;const cd=$('cd');
  if(cd.dataset.n!=String(cn)){cd.dataset.n=cn;const c=P.cards[cn]||[];cd.innerHTML=c.map(r=>r[0]?'<div class="cd"><span>'+r[0]+'</span><b>'+r[1]+'</b></div>':'<div class="cd note"><b>'+r[1]+'</b></div>').join('')}
  if(cn>=0){[...cd.children].forEach((e,i)=>{const k=spr(sm(t,P.st[cn]-0.1+i*0.12,P.st[cn]+0.75+i*0.12)),o=1-sm(t,(P.st[cn+1]||P.total)-0.35,(P.st[cn+1]||P.total)-0.05);e.style.opacity=(Math.min(1,k)*o).toFixed(3);e.style.transform=`translateY(${((1-k)*50).toFixed(1)}px)`})}
  // 字幕：声に合わせて1文字ずつ白→黄（いま読んでいる区切り）
  const sn=P.st.filter(s=>t>=s-0.15).length-1;const sp=$('sp');
  if(sn<0||sn>=P.sub.length-1&&t>P.end+0.2){sp.style.opacity=sn>=P.sub.length-1?Math.max(0,1-sm(t,P.end+0.2,P.end+0.6)):0}
  else sp.style.opacity=1;
  if(sn>=0){if(curN!==sn){curN=sn;sp.innerHTML=subHTML(sn)}const lt=t-P.st[sn],tm=P.sub[sn].tm,L=P.sub[sn].segs.map(s=>[...s].length);
    sp.querySelectorAll('i').forEach(e=>{const k=+e.dataset.k,j=+e.dataset.j,a=tm[k][0],b=tm[k][1],f=(j+0.5)/L[k],tt=a+(b-a)*f;e.className=lt>=tt?(lt<b+0.05&&lt>=a?'now':'on'):''})}
  // 終わりの札（最後の行の声と一緒に）
  const e=eo(sm(t,P.end-0.1,P.end+0.6));const ec=$('endc');ec.style.opacity=e;ec.style.transform=`scale(${(1.04-0.04*e).toFixed(4)})`;
  $('sb').style.zIndex=5;
}
render(0);
</script>"""
html = html.replace('%F%', F).replace('%PHOTO%', PHOTO).replace('%LOGO%', LOGO).replace('%P%', json.dumps(P, ensure_ascii=False))
open(f'{W}/news.html', 'w').write(html)
open(f'{W}/rec.js', 'w').write(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.setDefaultTimeout(240000);p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://{W}/news.html',{{timeout:240000}});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
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
enc = ['-c:v', 'libx264', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-crf', '19', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT]
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
