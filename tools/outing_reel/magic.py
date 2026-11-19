"""魔法の絵本ニュース（11/19 owner「写真じゃなくて作られへんの？ 絵本式にするんじゃなかった？」「めちゃくちゃお洒落な魔法の絵本のように」「お前が作れ」）。
写真も GPT も使わず、場面の絵はすべて ehon3.js（canvas の水彩）で描く。声・拍・字幕の流れは news2.py と同じ。
使い方: WORK=... VDIR=shots/voice/news2-eikando SP=20 python3 magic.py spec.json out.mp4 ["t1,t2" 静止画]"""
import json, os, re, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = json.load(open(sys.argv[1])); OUT = os.path.abspath(sys.argv[2]); STILL = sys.argv[3] if len(sys.argv) > 3 else ''
W = os.path.abspath(os.environ.get('WORK', '/tmp/news2-work')); os.makedirs(W + '/fr', exist_ok=True)
VDIR = os.environ.get('VDIR', ''); SP = os.environ.get('SP', '20')
F = ROOT + '/tools/fonts'
voice = spec['voice']; N = len(voice)


def dur(n):
    p = f'{VDIR}/{SP}-{n:02d}.wav'
    if not os.path.exists(p): return 3.2
    w = wave.open(p); return w.getnframes() / w.getframerate()


VD = [dur(n) for n in range(N)]
# 曲の拍（librosa）
BEATS = []
try:
    import librosa
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', '60', '-ac', '1', '-ar', '22050', f'{W}/bgm_mono.wav'], check=True)
    y, sr = librosa.load(f'{W}/bgm_mono.wav', sr=22050); _, bf = librosa.beat.beat_track(y=y, sr=sr)
    BEATS = [float(x) for x in librosa.frames_to_time(bf, sr=sr)]
except Exception as e: print('拍なし', e)
def snap(x, lo=-.2, hi=.35):
    c = [b for b in BEATS if x + lo <= b <= x + hi]
    return min(c, key=lambda b: abs(b - x)) if c else x
# 声の置き場所：行の間 0.28 秒
VDL = []; t = 0.3
for n in range(N): VDL.append(t); t += VD[n] + 0.28
# カットの時刻：spec の cuts は「何行目の声の、どこから」（line, at＝0〜1）で始まる。拍に合わせる
cuts = spec['cuts']; CT = []
for c in cuts:
    x = VDL[c['line']] + c.get('at', 0) * VD[c['line']] - (0.3 if c.get('at', 0) == 0 and c['line'] > 0 else 0)
    CT.append(0.0 if not CT else snap(x))
TOTAL = VDL[-1] + VD[-1] + 1.6
for i, c in enumerate(cuts): c['t0'] = round(CT[i], 3); c['t1'] = round(CT[i + 1] if i + 1 < len(cuts) else TOTAL, 3)
print('カット', [(c['k'], c['t0']) for c in cuts], '全体', round(TOTAL, 1))
# 字幕（声の1音ずつの長さ *.q.json で、「、」「。」ごとに出す）
CAP = []
def moras(n):
    qp = f'{VDIR}/{SP}-{n:02d}.q.json'
    if not os.path.exists(qp): return None
    q = json.load(open(qp)); sc = q.get('speedScale', 1) or 1; tm = [q.get('prePhonemeLength', .05) / sc]
    for ap in q['accent_phrases']:
        for m in ap['moras']: tm.append(tm[-1] + ((m.get('consonant_length') or 0) + m['vowel_length']) / sc)
        if ap.get('pause_mora'): tm[-1] += ap['pause_mora']['vowel_length'] / sc
    return tm
sp_ = lambda x: [c for c in re.split(r'(?<=[、。！？])', x) if c.strip()]
for n, (v, vy) in enumerate(zip(voice, spec['voice_yomi'])):
    if n in spec.get('nocap', []): continue
    a, b = sp_(v), sp_(vy)
    if len(a) != len(b): a, b = [v], [vy]
    tm = moras(n); tot = sum(len(re.sub('[、。！？ー]', '', x)) for x in b) or 1; acc = 0
    for ca, cb in zip(a, b):
        f0 = acc / tot; acc += len(re.sub('[、。！？ー]', '', cb)); f1 = acc / tot
        s0, s1 = (tm[round(f0 * (len(tm) - 1))], tm[round(f1 * (len(tm) - 1))]) if tm else (f0 * VD[n], f1 * VD[n])
        CAP.append(dict(t0=round(VDL[n] + s0, 3), t1=round(VDL[n] + s1, 3), x=ca.rstrip('、。')))
for i in range(len(CAP) - 1): CAP[i]['t1'] = min(CAP[i]['t1'] + .3, CAP[i + 1]['t0'] - .02)
if CAP: CAP[-1]['t1'] += .4

html = r"""<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:MB;src:url(file://%F%/ShipporiMincho-Bold.ttf)}
@font-face{font-family:MS;src:url(file://%F%/ShipporiMincho-SemiBold.ttf)}
@font-face{font-family:GB;src:url(file://%F%/ZenKakuGothicNew-Bold.ttf)}
@font-face{font-family:J;src:url(file://%F%/Jost-VF.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#05040c}
#cv{position:absolute;inset:0}
.cut{position:absolute;inset:0;visibility:hidden;pointer-events:none}
/* 金の箔の字 */
.gold{font-family:MB;background:linear-gradient(180deg,#fff6d8 0%,#f3d58e 38%,#c99a3e 52%,#f6e2a8 70%,#d9ac52 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 18px rgba(255,190,90,.55)) drop-shadow(0 4px 10px rgba(0,0,0,.6))}
.ch{display:inline-block;opacity:0}
.t{position:absolute;left:0;right:0;text-align:center;white-space:nowrap}
/* 紙の札（ふちがちぎれた紙・金の二重線） */
.paper{position:absolute;opacity:0;background:#f5ecd6;color:#3a2418;box-shadow:0 30px 70px rgba(0,0,0,.55);padding:46px 52px}
.paper::before{content:"";position:absolute;inset:16px;border:2px solid #c9a35a;outline:1px solid rgba(201,163,90,.6);outline-offset:-8px;pointer-events:none}
.paper::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,rgba(255,255,255,0) 55%,rgba(150,100,40,.22));pointer-events:none}
.lab{font:34px MS;letter-spacing:.3em;color:#9a6a2a;text-align:center}
.ink{font-family:MB;color:#3a2418}
.red{color:#b0302a}
#chip{position:absolute;z-index:20;left:50%;top:100px;transform:translateX(-50%);display:flex;align-items:center;gap:18px;height:64px;padding:0 34px;white-space:nowrap;
 background:linear-gradient(90deg,rgba(20,12,30,0),rgba(20,12,30,.72) 12%,rgba(20,12,30,.72) 88%,rgba(20,12,30,0));border-top:1.5px solid rgba(233,200,122,.55);border-bottom:1.5px solid rgba(233,200,122,.55)}
#chip b{font:36px MB;letter-spacing:.14em;color:#f6e2a8}
#chip i{width:9px;height:9px;transform:rotate(45deg);background:#e9c87a;box-shadow:0 0 10px #ffd27a}
#chip span{font:34px MB;letter-spacing:.06em;color:#fff4e0}
#bar{position:absolute;z-index:21;left:0;top:0;height:6px;background:linear-gradient(90deg,#f6e2a8,#d9ac52);box-shadow:0 0 12px rgba(255,200,110,.8)}
#cap{position:absolute;z-index:22;left:70px;right:150px;top:1330px;display:flex;justify-content:center}
#capt{position:relative;padding:18px 40px 20px;background:rgba(245,236,214,.94);font:46px/1.35 MB;letter-spacing:.05em;color:#3a2418;text-align:center;opacity:0;box-shadow:0 14px 34px rgba(0,0,0,.45)}
#capt::before{content:"";position:absolute;inset:7px;border:1.5px solid #c9a35a;pointer-events:none}
#capt em{font-style:normal;color:#b0302a}
</style>
<canvas id="cv" width="1080" height="1920"></canvas><div id="stage"></div>
<div id="chip"><b>おでかけニュース</b><i></i><span>%CHIP%</span></div><div id="bar"></div><div id="cap"><div id="capt"></div></div>
<script src="file://%JS%"></script>
<script>
const C=%CUTS%,CAP=%CAP%,TOTAL=%TOTAL%;
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),sm=(t,a,b)=>cl((t-a)/(b-a)),eo=x=>1-Math.pow(1-x,3),eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,
 back=x=>{const c1=1.7,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)},$=s=>document.querySelector(s);
const chars=s=>[...s].map(c=>`<span class="ch gold">${c}</span>`).join('');
// ちぎれた紙のふち
function deckle(seed){const r=R_(seed);const p=[];const n=26;for(let i=0;i<=n;i++)p.push(`${(i/n*100).toFixed(1)}% ${(r()*1.6).toFixed(2)}%`);for(let i=0;i<=n*1.6;i++)p.push(`${(100-r()*1.2).toFixed(2)}% ${(i/(n*1.6)*100).toFixed(1)}%`);for(let i=n;i>=0;i--)p.push(`${(i/n*100).toFixed(1)}% ${(100-r()*1.6).toFixed(2)}%`);for(let i=n*1.6;i>=0;i--)p.push(`${(r()*1.2).toFixed(2)}% ${(i/(n*1.6)*100).toFixed(1)}%`);return `clip-path:polygon(${p.join(',')})`}
const lanternSvg=`<svg width="120" height="170" viewBox="0 0 120 170"><path d="M20 40 L60 14 L100 40Z" fill="currentColor" opacity=".55"/><rect class="lb" x="30" y="44" width="60" height="62" rx="6" fill="currentColor"/><rect x="52" y="106" width="16" height="50" fill="currentColor" opacity=".55"/><rect x="34" y="154" width="52" height="10" fill="currentColor" opacity=".55"/></svg>`;
function build(){const st=$('#stage');C.forEach((c,i)=>{const d=document.createElement('div');d.className='cut';d.id='c'+i;let h='';
 if(c.k=='hook')h+=`<div class="t" style="top:250px;font-size:64px;letter-spacing:.5em;padding-left:.5em">${chars(c.h0)}</div><div class="t" style="top:340px;font-size:132px;letter-spacing:.08em">${chars(c.h1)}</div><div class="t" style="top:500px;font-size:150px;letter-spacing:.08em">${chars(c.h2)}</div>`;
 if(c.k=='date')h+=`<div class="paper" style="left:120px;right:200px;top:520px;${deckle(3)}"><div class="lab">${c.lab}</div>
  <div style="display:flex;justify-content:center;align-items:flex-end;gap:14px;margin-top:26px"><div style="text-align:center"><div class="ink num" style="font:500 112px/1 J;color:#3a2418">${c.a}</div><div class="ink" style="font-size:36px;margin-top:6px">${c.aw}</div></div>
  <div class="ink" style="font:400 64px J;color:#c9a35a;padding-bottom:62px">—</div><div style="text-align:center"><div class="ink" style="font:500 112px/1 J;color:#b0302a">${c.b}</div><div class="ink" style="font-size:36px;margin-top:6px">${c.bw}</div></div></div>
  <svg width="100%" height="40" viewBox="0 0 600 40" style="margin-top:26px"><path class="vine" d="M10 20 C 120 0, 180 40, 300 20 S 480 0, 590 20" fill="none" stroke="#b0302a" stroke-width="4" stroke-dasharray="640" stroke-dashoffset="640"/></svg>
  <div class="ink" style="text-align:center;font-size:44px;margin-top:8px;letter-spacing:.2em">${c.note}</div></div>`;
 if(c.k=='time')h+=`<div class="paper" style="left:160px;right:240px;top:470px;text-align:center;${deckle(5)}"><div class="lab">${c.lab}</div>
  <svg width="330" height="330" viewBox="0 0 330 330" style="margin:18px auto 0;display:block"><circle cx="165" cy="165" r="150" fill="#fbf5e6" stroke="#c9a35a" stroke-width="6"/><circle cx="165" cy="165" r="136" fill="none" stroke="#c9a35a" stroke-width="1.5"/>
  ${[...Array(12)].map((_,j)=>{const a=j/12*Math.PI*2;return `<line x1="${165+Math.sin(a)*118}" y1="${165-Math.cos(a)*118}" x2="${165+Math.sin(a)*(j%3?126:132)}" y2="${165-Math.cos(a)*(j%3?126:132)}" stroke="#3a2418" stroke-width="${j%3?3:6}"/>`}).join('')}
  <path class="arc" fill="rgba(240,150,60,.28)" d=""/><line class="hh" x1="165" y1="165" x2="165" y2="88" stroke="#3a2418" stroke-width="11" stroke-linecap="round"/><line class="mh" x1="165" y1="165" x2="165" y2="50" stroke="#b0302a" stroke-width="6" stroke-linecap="round"/><circle cx="165" cy="165" r="12" fill="#c9a35a"/></svg>
  <div style="display:flex;justify-content:center;align-items:baseline;gap:16px;margin-top:22px"><span class="ink" style="font:500 92px J">${c.a}</span><span class="ink" style="font:400 50px J;color:#c9a35a">〜</span><span class="ink red" style="font:500 92px J">${c.b}</span></div></div>`;
 if(c.k=='split')h+=`<div class="paper tagp" style="left:110px;top:300px;padding:16px 34px;font:54px MB;color:#3a2418">昼の拝観</div><div class="paper tagp" style="left:600px;top:300px;padding:16px 34px;font:54px MB;color:#3a2418">夜の拝観</div>
  <div class="paper" style="left:250px;right:250px;top:900px;text-align:center;padding:34px 30px;${deckle(8)}"><div class="ink" style="font-size:82px;letter-spacing:.06em">入れ替え制</div><div class="ink" style="font-size:34px;margin-top:6px;color:#7a5a3a">昼と夜は 別の券</div></div>`;
 if(c.k=='stamp')h+=`<div class="paper tk" style="left:150px;right:230px;top:430px;text-align:center;padding:50px 40px 54px;${deckle(11)}"><div class="lab">${c.lab}</div><div class="ink" style="font-size:52px;margin-top:14px">永観堂 夜の拝観</div>
  <div style="height:2px;margin:26px 30px 0;background:repeating-linear-gradient(90deg,#c9a35a 0 14px,transparent 14px 26px)"></div><div style="height:350px;position:relative">
  <div class="hanko" style="position:absolute;left:50%;top:22px;width:310px;height:310px;margin-left:-155px;border-radius:50%;border:12px solid #c0302a;color:#c0302a;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;mix-blend-mode:multiply;background:rgba(192,48,42,.07)"><span style="font:76px/1.1 MB">${c.a}</span><span style="font:112px/1.05 MB">${c.a2}</span></div></div>
  <div class="ink" style="font-size:40px;color:#7a5a3a">${c.b}</div></div>`;
 if(c.k=='route')h+=`<div class="t ink lb1" style="top:300px;font-size:62px;letter-spacing:.2em;opacity:0;color:#3a2418">永観堂への道</div>`;
 if(c.k=='meter')h+=`<div class="paper" style="left:110px;right:190px;top:430px;text-align:center;${deckle(14)}"><div class="lab">${c.lab}</div><div class="ink" style="font-size:72px;margin-top:14px">${c.a}</div>
  <div style="display:flex;justify-content:center;gap:4px;margin-top:26px">${[0,1,2,3,4].map(j=>`<span class="ln" style="color:#d8cdb6">${lanternSvg}</span>`).join('')}</div>
  <div style="display:flex;justify-content:space-between;font:32px MS;color:#7a5a3a;margin:6px 20px 0"><span>すいている</span><span class="red">とても混む</span></div></div>`;
 if(c.k=='end')h+=`<div class="t" style="top:330px;font-size:84px;letter-spacing:.04em">${chars(c.h1)}</div>
  <div class="paper" style="left:170px;right:170px;top:620px;text-align:center;padding:40px 30px;${deckle(17)}"><div class="lab" style="letter-spacing:.4em">TOWN NOTE</div><div class="ink" style="font-size:58px;margin-top:10px">関西おでかけリスト</div><div class="ink" style="font-size:32px;margin-top:10px;color:#7a5a3a">日付と地図でさがせる</div></div>
  <div class="paper sv" style="left:300px;right:300px;top:960px;text-align:center;padding:24px;background:#b0302a;color:#fff6e0;font:44px MB;letter-spacing:.2em">保存しておく</div>`;
 d.innerHTML=h;st.appendChild(d)})}
// ---- 地図（羊皮紙の上にインクで描く） ----
const MAP=cv_(),MG=MAP.getContext('2d');const RP=[[230,1230],[300,1080],[470,1000],[520,830],[700,760],[790,600]];
function buildMap(){const c=MG;const g=c.createRadialGradient(540,900,200,540,960,1200);g.addColorStop(0,'#f6ecd2');g.addColorStop(1,'#d9c294');c.fillStyle=g;c.fillRect(0,0,SW,SH);
 c.save();c.globalCompositeOperation='multiply';c.globalAlpha=.35;c.drawImage(paper(),0,0,SW,SH);c.restore();
 const r=R_(21);c.save();c.globalAlpha=.08;for(let i=0;i<30;i++){c.fillStyle=r()<.5?'#8a5a20':'#5a3a10';c.filter='blur(20px)';c.beginPath();c.arc(r()*SW,r()*SH,40+r()*120,0,7);c.fill()}c.restore();
 // 東山（右上に山）
 c.save();for(let i=0;i<5;i++){const x=640+i*90,y=470+i*40;c.fillStyle=mix('#8fa078','#5e7050',i/5);c.globalAlpha=.75;c.beginPath();c.moveTo(x-110,y+60);c.quadraticCurveTo(x-40,y-80,x,y-70);c.quadraticCurveTo(x+50,y-80,x+120,y+60);c.closePath();c.fill();c.globalAlpha=.6;c.strokeStyle='#3a2a18';c.lineWidth=2;c.stroke()}c.restore();
 // 鴨川
 c.save();c.strokeStyle='rgba(90,140,170,.55)';c.lineWidth=34;c.lineCap='round';c.beginPath();c.moveTo(430,300);c.bezierCurveTo(400,700,470,1000,410,1600);c.stroke();c.strokeStyle='rgba(60,100,130,.5)';c.lineWidth=2;c.stroke();c.restore();
 c.save();c.font='34px MS';c.fillStyle='rgba(50,80,100,.85)';['鴨','川'].forEach((ch,i)=>c.fillText(ch,368,560+i*40));c.restore();
 // 小さなもみじの木を点々と
 for(let i=0;i<26;i++){const x=560+r()*440,y=380+r()*520;c.fillStyle=['#c8341f','#e0582a','#ef8a2e'][i%3];leaf(c,x,y,12+r()*8,r()*6)}
 // 方位
 c.save();c.translate(180,470);c.strokeStyle='#3a2418';c.fillStyle='#3a2418';c.lineWidth=2;c.beginPath();c.arc(0,0,62,0,7);c.stroke();c.beginPath();c.moveTo(0,-80);c.lineTo(14,0);c.lineTo(0,80);c.lineTo(-14,0);c.closePath();c.fill();c.font='34px MB';c.textAlign='center';c.fillText('北',0,-96);c.restore();
 // 京都駅
 c.save();c.fillStyle='#3a2418';c.fillRect(120,1250,220,70);c.fillStyle='#f5ecd6';for(let i=0;i<6;i++)c.fillRect(132+i*35,1264,22,26);c.fillStyle='#3a2418';c.fillRect(100,1318,260,10);c.font='54px MB';c.textAlign='center';c.fillText('京都駅',230,1395);c.restore();
 // 永観堂（多宝塔の印）
 c.save();c.translate(790,600);c.scale(.9,.9);c.translate(-790,-600);tahoto(c,790,600,120,0,0);c.restore();c.save();c.font='56px MB';c.fillStyle='#b0302a';c.textAlign='center';c.fillText('永観堂',800,690);c.restore();
 c.save();c.strokeStyle='rgba(58,36,24,.35)';c.lineWidth=3;c.strokeRect(50,230,980,1330);c.lineWidth=1.2;c.strokeRect(62,242,956,1306);c.restore()}
function rpath(c){c.beginPath();c.moveTo(...RP[0]);for(let i=1;i<RP.length;i++){const p=RP[i-1],q=RP[i];c.quadraticCurveTo(p[0]+(q[0]-p[0])*.1+40,q[1]+(p[1]-q[1])*.6,q[0],q[1])}}
let RL=null;function routeLen(){if(RL)return RL;const pts=[];const c=document.createElement('canvas').getContext('2d');  // 道の点を細かく
 const seg=[];for(let i=1;i<RP.length;i++){const p=RP[i-1],q=RP[i],k=[p[0]+(q[0]-p[0])*.1+40,q[1]+(p[1]-q[1])*.6];for(let j=0;j<=40;j++){const u=j/40;pts.push([(1-u)*(1-u)*p[0]+2*(1-u)*u*k[0]+u*u*q[0],(1-u)*(1-u)*p[1]+2*(1-u)*u*k[1]+u*u*q[1]])}}
 let L=[0];for(let i=1;i<pts.length;i++)L.push(L[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));return RL={pts,L,tot:L[L.length-1]}}
function at(q){const R=routeLen(),d=q*R.tot;let i=R.L.findIndex(v=>v>=d);if(i<1)i=1;const a=R.pts[i-1],b=R.pts[i];return[b[0],b[1],Math.atan2(b[1]-a[1],b[0]-a[0])]}
function drawMap(c,a,t){c.drawImage(MAP,0,0);const R=routeLen();const q=eio(sm(a,.35,2.0));
 c.save();c.setLineDash([2,22]);c.lineCap='round';c.strokeStyle='#b0302a';c.lineWidth=14;c.beginPath();const n=Math.floor(q*(R.pts.length-1));c.moveTo(...R.pts[0]);for(let i=1;i<=n;i++)c.lineTo(...R.pts[i]);c.stroke();c.restore();
 // バス
 if(a>.2){const[x,y,ang]=at(q);c.save();c.translate(x,y-34);c.fillStyle='rgba(0,0,0,.2)';c.beginPath();c.ellipse(0,40,70,12,0,0,7);c.fill();c.fillStyle='#2f8a5a';c.beginPath();c.roundRect(-70,-34,140,68,16);c.fill();c.fillStyle='#f5ecd6';for(let i=0;i<4;i++)c.fillRect(-58+i*28,-22,20,22);c.fillStyle='#f6c64a';c.beginPath();c.arc(48,-10,15,0,7);c.fill();c.fillStyle='#2f8a5a';c.font='22px J';c.textAlign='center';c.fillText('5',48,-2);
  c.fillStyle='#222';c.beginPath();c.arc(-40,34,12,0,7);c.arc(40,34,12,0,7);c.fill();c.restore()}
 c.save();c.globalAlpha=sm(a,.5,.9);c.font='44px MB';c.fillStyle='#2f6a4a';c.fillText('市バス 5系統',560,1080);c.restore();
 if(q>=.99){c.save();c.globalCompositeOperation='lighter';gl(c,790,560,160*(1+.1*Math.sin(t*6)),'255,200,110',.6);c.restore()}
 // 車は×
 const k=sm(a,2.2,2.5);if(k>0){c.save();c.translate(250,1490);c.globalAlpha=k;c.fillStyle='#4a4a58';c.beginPath();c.roundRect(-80,-30,160,56,14);c.fill();c.beginPath();c.roundRect(-50,-62,100,40,12);c.fill();c.fillStyle='#222';c.beginPath();c.arc(-46,28,15,0,7);c.arc(46,28,15,0,7);c.fill();
  const s=1+(1-eo(sm(a,2.3,2.55)))*1.5;c.scale(s,s);c.strokeStyle='#c0302a';c.lineWidth=16;c.lineCap='round';c.beginPath();c.moveTo(-70,-70);c.lineTo(70,50);c.moveTo(70,-70);c.lineTo(-70,50);c.stroke();c.restore();
  c.save();c.globalAlpha=k;c.font='48px MB';c.fillStyle='#c0302a';c.fillText('車は 乗り入れ',380,1470);c.fillText('できません',380,1530);c.restore()}}
// ---- 魔法の切り替え：光の輪が広がる（iris）／金の光が斜めに走る（sweep） ----
const SCN=()=>({T2:scTemple(2),T0:scTemple(0),B:scBranch(),P1:scPond(1),P2:scPond(2)});let S=null;
const cvx=()=>$('#cv').getContext('2d');
function camAt(c,u){const f=c.cam||[1,0,0,1,0,0];const e=eio(u)*.6+u*.4;return{s:f[0]+(f[3]-f[0])*e,x:f[1]+(f[4]-f[1])*e,y:f[2]+(f[5]-f[2])*e,ds:.12,par:1}}
function paint(ctx,c,a,u,t){   // 1つのカットを ctx に描く
 if(c.sc=='MAP'){drawMap(ctx,a,t);return}
 const cam=camAt(c,u);const o={leaves:c.k=='branch'?46:c.k=='hook'||c.k=='end'?28:18,dust:c.k=='end'?150:c.k=='hook'?90:60,seed:C.indexOf(c),lit:1};
 if(c.crowd)o.crowd=6+40*eo(sm(a,.2,2.6));
 if(c.k=='time'){const q=sm(a,.4,1.8);drawScene(S.P1,t,cam,{leaves:12,lit:.25,dust:0});ctx.drawImage(OUT,0,0);ctx.save();ctx.globalAlpha=eio(q);drawScene(S.P2,t,cam,{leaves:12,lit:q*1.25,dust:50});ctx.drawImage(OUT,0,0);ctx.restore();return}
 if(c.k=='date'){o.lit=.25;o.dust=30}
 if(c.k=='split'){const p=1080*(1-.5*eio(sm(a,0,.8)));drawScene(S.T0,t,cam,{leaves:14});ctx.drawImage(OUT,0,0);drawScene(S.T2,t,cam,{leaves:14,dust:40});ctx.save();ctx.beginPath();ctx.rect(p,0,1080-p,1920);ctx.clip();ctx.drawImage(OUT,0,0);ctx.restore();
  ctx.save();ctx.globalCompositeOperation='lighter';ctx.fillStyle='rgba(255,236,190,.95)';ctx.fillRect(p-3,0,6,1920);gl(ctx,p,960,160,'255,210,130',.35);const r=R_(3);for(let i=0;i<40;i++){const y=r()*1920,tw=Math.max(0,Math.sin(t*5+i*2));ctx.fillStyle=`rgba(255,230,160,${tw})`;ctx.beginPath();ctx.arc(p+(r()-.5)*40,y,1.5+r()*3,0,7);ctx.fill()}ctx.restore();return}
 drawScene(S[c.sc],t,cam,o);if(c.blur){ctx.save();ctx.filter=`blur(${c.blur}px)`;ctx.drawImage(OUT,0,0);ctx.restore();ctx.fillStyle='rgba(10,6,20,.25)';ctx.fillRect(0,0,1080,1920)}else ctx.drawImage(OUT,0,0)}
const BUF=cv_(),BG=BUF.getContext('2d');
function render(t){if(!S)S=SCN();const ctx=cvx();const D=.28;
 $('#bar').style.width=(1080*cl(t/TOTAL)).toFixed(1)+'px';
 let i=C.findIndex(c=>t>=c.t0&&t<c.t1);if(i<0)i=C.length-1;const c=C[i];const a=t-c.t0;const u=cl((t-c.t0+D)/(c.t1-c.t0+2*D));
 paint(ctx,c,a,u,t);
 // 次のカットが魔法で入る（切り替わる前の D 秒から）
 const n=C[i+1];if(n&&t>n.t0-D&&n.tr!='none'){const q=sm(t,n.t0-D,n.t0+.04);const an=t-n.t0,un=cl((t-n.t0+D)/(n.t1-n.t0+2*D));BG.clearRect(0,0,1080,1920);paint(BG,n,an,un,t);trans(ctx,n,eio(q),t)}
 if(c.tr&&c.tr!='none'&&a<.12&&i>0){const prev=C[i-1];}  // 入った後はそのまま
 // 光の粒の噴き出し（字が出る時）
 C.forEach((cc,j)=>{const aa=t-cc.t0;if(cc.k=='hook'||cc.k=='end'){if(aa>-.1&&aa<1.4)burst(ctx,540,cc.k=='hook'?470:400,aa,j)}});
 C.forEach((cc,j)=>{const el=document.getElementById('c'+j);const on=j==i||(j==i+1&&t>cc.t0-D*.5);el.style.visibility=on?'visible':'hidden';if(!on)return;ov(el,cc,t-cc.t0,t);el.style.opacity=j==i&&C[i+1]&&C[i+1].tr!='none'?(1-sm(t,cc.t1-D,cc.t1-D*.2)).toFixed(3):1});
 caption(t)}
function trans(ctx,n,q,t){ctx.save();if(n.tr=='iris'){const R=q*2300;ctx.beginPath();ctx.arc(n.ix,n.iy,R,0,7);ctx.clip();ctx.drawImage(BUF,0,0);ctx.restore();
  ctx.save();ctx.globalCompositeOperation='lighter';ctx.strokeStyle=`rgba(255,226,160,${.9*(1-q)})`;ctx.lineWidth=10;ctx.shadowColor='rgba(255,200,110,1)';ctx.shadowBlur=40;ctx.beginPath();ctx.arc(n.ix,n.iy,R,0,7);ctx.stroke();ctx.shadowBlur=0;
  const r=R_(9);for(let i=0;i<90;i++){const a=r()*6.283,d=R+(r()-.5)*60;ctx.fillStyle=`rgba(255,236,190,${(1-q)*r()})`;ctx.beginPath();ctx.arc(n.ix+Math.cos(a)*d,n.iy+Math.sin(a)*d,1.5+r()*4,0,7);ctx.fill()}ctx.restore();return}
 // sweep：左下から右上へ、金の光の帯
 const k=-600+q*3400;ctx.beginPath();ctx.moveTo(-200,1920+200);ctx.lineTo(-200,k+1100);ctx.lineTo(1280,k-400);ctx.lineTo(1280,2200);ctx.closePath();ctx.clip();ctx.drawImage(BUF,0,0);ctx.restore();
 ctx.save();ctx.globalCompositeOperation='lighter';ctx.translate(540,k+350);ctx.rotate(-Math.atan2(1500,1480));const g=ctx.createLinearGradient(0,-90,0,90);g.addColorStop(0,'rgba(255,220,150,0)');g.addColorStop(.5,`rgba(255,236,190,${.9*Math.sin(Math.PI*q)})`);g.addColorStop(1,'rgba(255,220,150,0)');ctx.fillStyle=g;ctx.fillRect(-1600,-90,3200,180);
 const r=R_(5);for(let i=0;i<70;i++){ctx.fillStyle=`rgba(255,240,200,${Math.sin(Math.PI*q)*r()})`;ctx.beginPath();ctx.arc((r()-.5)*2000,(r()-.5)*200,1.5+r()*4,0,7);ctx.fill()}ctx.restore()}
function burst(ctx,x,y,a,seed){const r=R_(40+seed);ctx.save();ctx.globalCompositeOperation='lighter';for(let i=0;i<70;i++){const ang=r()*6.283,v=200+r()*600,d=v*eo(cl(a/1.2)),f=1-cl(a/1.4);const px=x+Math.cos(ang)*d*1.3,py=y+Math.sin(ang)*d*.6;const s=1+r()*3.5;
 ctx.fillStyle=`rgba(255,232,170,${f*(.4+.6*r())})`;ctx.beginPath();ctx.arc(px,py,s,0,7);ctx.fill();if(s>3.4){ctx.strokeStyle=`rgba(255,240,200,${f})`;ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(px-s*4,py);ctx.lineTo(px+s*4,py);ctx.moveTo(px,py-s*4);ctx.lineTo(px,py+s*4);ctx.stroke()}}ctx.restore()}
function ov(el,c,a,t){el.querySelectorAll('.ch').forEach((s,j)=>{const st=(c.k=='hook'?-.3:.15)+j*.07;const q=sm(a,st,st+.45);s.style.opacity=q;s.style.transform=`translateY(${(1-eo(q))*30}px) scale(${(.8+.2*eo(q)).toFixed(3)})`;s.style.filter=`blur(${((1-q)*10).toFixed(1)}px)`});
 el.querySelectorAll('.paper').forEach((p,j)=>{const st=c.k=='split'?[.6,.75,1.2][j]:.15+j*.35;const q=sm(a,st,st+.55);const r=(j%2?3:-3)*(1-eo(q));p.style.opacity=eo(cl(q*1.6));p.style.transform=`translateY(${(1-eo(q))*90}px) rotate(${(r+(j%2?.6:-.8)).toFixed(2)}deg) scale(${(.92+.08*back(q)).toFixed(3)})`});
 el.querySelectorAll('.vine').forEach(v=>v.setAttribute('stroke-dashoffset',(640*(1-eio(sm(a,.7,1.6)))).toFixed(0)));
 if(c.k=='time'){const q=eio(sm(a,.4,1.8));const hr=17.5+3*q;const ha=(hr%12)/12*360,ma=(hr*60%60)/60*360+360*3*q*0;el.querySelector('.hh').setAttribute('transform',`rotate(${ha.toFixed(1)} 165 165)`);el.querySelector('.mh').setAttribute('transform',`rotate(${((hr*360)%360).toFixed(1)} 165 165)`);
  const a0=(17.5%12)/12*Math.PI*2,a1=(hr%12)/12*Math.PI*2;const P=(an)=>`${(165+Math.sin(an)*130).toFixed(1)} ${(165-Math.cos(an)*130).toFixed(1)}`;el.querySelector('.arc').setAttribute('d',q>0?`M165 165 L${P(a0)} A130 130 0 ${a1-a0>Math.PI?1:0} 1 ${P(a1)}Z`:'')}
 
 if(c.k=='stamp'){const h=el.querySelector('.hanko');const q=sm(a,.55,.75);h.style.opacity=q>0?1:0;h.style.transform=`rotate(-12deg) scale(${(1+(1-eo(q))*1.6).toFixed(3)})`;const tk=el.querySelector('.tk');if(a>.75&&a<.95)tk.style.transform+=` translate(${(Math.sin(a*90)*6).toFixed(1)}px,${(Math.cos(a*70)*4).toFixed(1)}px)`}
 if(c.k=='route')el.querySelector('.lb1').style.opacity=sm(a,.1,.5);
 if(c.k=='meter')el.querySelectorAll('.ln').forEach((p,j)=>{const q=sm(a,.7+j*.22,.9+j*.22);p.style.color=q>0?(j>=3?'#d0402a':'#e8a23a'):'#d8cdb6';p.style.filter=q>0?`drop-shadow(0 0 ${(14*q).toFixed(0)}px ${j>=3?'rgba(255,90,60,.9)':'rgba(255,190,90,.9)'})`:'none';p.style.display='inline-block';p.style.transform=`scale(${(.85+.15*back(q)).toFixed(3)})`});
 if(c.k=='end'){const sv=el.querySelector('.sv');if(a>1.6)sv.style.transform=`scale(${(1+.04*Math.sin((a-1.6)*6)).toFixed(3)})`}}
function caption(t){const el=$('#capt');const cc=C.find(c=>t>=c.t0&&t<c.t1);if(cc&&cc.k=='route'){el.style.opacity=0;return}let ci=-1;for(let i=0;i<CAP.length;i++)if(t>=CAP[i].t0-.06&&t<CAP[i].t1)ci=i;let out=1;
 if(ci<0){for(let i=0;i<CAP.length;i++)if(CAP[i].t1<=t)ci=i;if(ci<0){el.style.opacity=0;return}out=1-sm(t,CAP[ci].t1,CAP[ci].t1+.2)}
 const K=CAP[ci],q=cl((t-K.t0)/Math.max(.2,K.t1-K.t0-.25)),n=Math.round(q*K.x.length);el.innerHTML='<em>'+K.x.slice(0,n)+'</em>'+K.x.slice(n);el.style.opacity=eo(sm(t,K.t0-.06,K.t0+.1))*out}
build();buildMap();
</script>"""
html = (html.replace('%F%', F).replace('%JS%', ROOT + '/tools/outing_reel/ehon3.js').replace('%CUTS%', json.dumps(cuts, ensure_ascii=False))
        .replace('%CAP%', json.dumps(CAP, ensure_ascii=False)).replace('%TOTAL%', f'{TOTAL:.3f}').replace('%CHIP%', spec.get('chip', '')))
open(f'{W}/magic.html', 'w').write(html)
open(f'{W}/rec.js', 'w').write(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.setDefaultTimeout(600000);p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://{W}/magic.html');await p.evaluate(()=>document.fonts.ready);await p.evaluate(()=>render(0));await p.waitForTimeout(300);
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{W}/c-'+t+'.jpg',type:'jpeg',quality:88}});}}await b.close();return}}
const fs=require('fs');const A=+(process.env.FR0||0),B=+(process.env.FR1||1e9);for(let i=A;i<30*{TOTAL:.3f}&&i<B;i++){{const f='{W}/fr/'+String(i).padStart(4,'0')+'.jpg';if(fs.existsSync(f))continue;await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:f,type:'jpeg',quality:92}});}}await b.close()}})();""")
if STILL:
    subprocess.run(['node', f'{W}/rec.js', STILL], check=True); sys.exit()
NF = int(30 * TOTAL) + 1; K = int(os.environ.get('WORKERS', '4')); ps = []
for i in range(K): ps.append(subprocess.Popen(['node', f'{W}/rec.js'], env=dict(os.environ, FR0=str(NF * i // K), FR1=str(NF * (i + 1) // K))))
if any(p.wait() for p in ps): sys.exit('コマを撮れない')
# 音：曲＋声（声の間は曲を下げる）＋切り替えの「鈴（きらきら）」＋判子の「とん」＋最後に -14 LUFS
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{TOTAL + 1:.2f}', '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '48000', f'{W}/bgm.wav'], check=True)
bell = '0.22*sin(2*PI*1568*t)*exp(-5*t)+0.16*sin(2*PI*2349*(t-0.07))*exp(-6*(t-0.07))*gte(t,0.07)+0.13*sin(2*PI*3136*(t-0.14))*exp(-6*(t-0.14))*gte(t,0.14)+0.1*sin(2*PI*4186*(t-0.2))*exp(-7*(t-0.2))*gte(t,0.2)'
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f"aevalsrc='{bell}':s=48000:d=1.4", '-af', 'aecho=0.8:0.6:60|120:0.3|0.2', f'{W}/bell.wav'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', "aevalsrc='0.9*sin(2*PI*(90-40*t)*t)*exp(-14*t)':s=48000:d=0.5", f'{W}/thud.wav'], check=True)
ins = ['-i', f'{W}/bgm.wav']; flt = []; k = 2
for n in range(N):
    ins += ['-i', f'{VDIR}/{SP}-{n:02d}.wav']; flt.append(f'[{k}:a]aresample=48000,adelay={int(VDL[n] * 1000)}:all=1[v{n}]'); k += 1
flt.append(''.join(f'[v{n}]' for n in range(N)) + f'amix=inputs={N}:normalize=0,volume=1.7,apad=whole_dur={TOTAL + 1:.2f},asplit=2[vo][sc]')
wx = []
ev = [(max(0, c['t0'] - .3), 'bell', .5) for c in cuts[1:] if c.get('tr', 'iris') != 'none'] + [(0.0, 'bell', .6)]
ev += [(c['t0'] + .55, 'thud', .8) for c in cuts if c['k'] == 'stamp'] + [(c['t0'] + 2.3, 'thud', .5) for c in cuts if c['k'] == 'route']
for (tt, nm, vol) in ev:
    ins += ['-i', f'{W}/{nm}.wav']; flt.append(f'[{k}:a]adelay={int(tt * 1000)}:all=1,volume={vol}[w{k}]'); wx.append(f'[w{k}]'); k += 1
flt.append(''.join(wx) + f'amix=inputs={len(wx)}:normalize=0,apad=whole_dur={TOTAL + 1:.2f}[fx]')
flt.append(f'[1:a]afade=t=in:d=0.3,afade=t=out:st={TOTAL - 1.8:.2f}:d=1.8[bg0]')
flt.append('[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=500:makeup=1[bg]')
flt.append('[bg][vo][fx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]')
flt.append("[0:v]format=gbrp,noise=alls=2:allf=t,format=yuv420p[vv]")
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg'] + ins + ['-filter_complex', ';'.join(flt), '-map', '[vv]', '-map', '[a]', '-t', f'{TOTAL:.2f}',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', OUT], check=True)
print(OUT, round(TOTAL, 1), '秒')
