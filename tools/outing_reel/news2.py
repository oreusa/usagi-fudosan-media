"""おでかけニュース 作り直し版（11/19 owner「映像、内容を元に一から作り直したら？？」「まんまやん」）。
絵本の絵・本・机は使わず、本物の写真（コモンズ・作者と許可を画面に出す）＋動く見出し・日付・地図の道・混み具合で作る縦動画。
インスタ・TikTok・YouTube ショート共通（9:16・字は TikTok の右のボタンと下の説明文にかからない位置）。
調べた決まり（JNTO の縦型ショートの事例・制作会社の記事・旅の上位動画）：1カット2〜3秒／同じ画面5秒以上は離れる／冒頭は一番の見せ場／曲の拍で切り替え／字は少なく大きく。
使い方: python3 news2.py spec.json out.mp4 [静止画の時刻 "0.5,3"]   声は VDIR（voice.yml で作った shots/voice/<名前>）、SP=20。
1080x1920・30fps。render(t) で1コマずつ描き、ffmpeg でつなぐ（ehon.py と同じ流れ）。"""
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
PH = {k: dict(v, src='file://' + os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), v['file']))) for k, v in spec['photos'].items()}

html = r"""<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:G9;src:url(file://%F%/ZenKakuGothicNew-Black.ttf)}
@font-face{font-family:GB;src:url(file://%F%/ZenKakuGothicNew-Bold.ttf)}
@font-face{font-family:GM;src:url(file://%F%/ZenKakuGothicNew-Medium.ttf)}
@font-face{font-family:J;src:url(file://%F%/Jost-VF.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#07090f}
.cut{position:absolute;inset:0;overflow:hidden;visibility:hidden;will-change:transform}
.ph{position:absolute;left:0;top:0;height:1920px;transform-origin:0 0}
.shade{position:absolute;inset:0;pointer-events:none}
.ov{position:absolute;inset:0}
#chip{position:absolute;z-index:20;left:50%;top:104px;transform:translateX(-50%);display:flex;align-items:center;gap:16px;height:60px;padding:0 30px 0 26px;border-radius:30px;background:rgba(8,10,18,.55);backdrop-filter:blur(12px);box-shadow:0 6px 24px rgba(0,0,0,.35),inset 0 0 0 1.5px rgba(255,236,200,.22);white-space:nowrap}
#chip i{width:16px;height:16px;border-radius:50%;background:#e0392b;box-shadow:0 0 14px #ff5a40}
#chip b{font:31px G9;letter-spacing:.1em;color:#fff4e0}
#chip span{font:30px GB;letter-spacing:.04em;color:#f3d9a8;padding-left:16px;border-left:1.5px solid rgba(255,236,200,.35)}
#bar{position:absolute;z-index:21;left:0;top:0;height:8px;background:linear-gradient(90deg,#ffcf6b,#ff8a3d);box-shadow:0 0 12px rgba(255,190,90,.7)}
#cred{position:absolute;z-index:20;right:150px;top:182px;font:20px GM;color:rgba(255,255,255,.72);text-shadow:0 1px 4px rgba(0,0,0,.8);letter-spacing:.02em}
#cap{position:absolute;z-index:22;left:80px;right:160px;top:1300px;display:flex;justify-content:center}
#capt{padding:16px 30px 18px;border-radius:16px;background:rgba(6,8,14,.72);font:46px/1.35 GB;letter-spacing:.04em;color:#fff;text-align:center;opacity:0;box-shadow:0 10px 30px rgba(0,0,0,.4)}
#capt em{font-style:normal;color:#ffcf6b}
#flash{position:absolute;inset:0;z-index:30;background:#fff;opacity:0;pointer-events:none}
.hl{position:absolute;left:70px;right:150px;font-family:G9;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.65)}
.hl span{display:inline-block;opacity:0}
.card{position:absolute;left:70px;right:150px;border-radius:30px;background:rgba(8,10,18,.72);backdrop-filter:blur(18px);box-shadow:0 20px 60px rgba(0,0,0,.5),inset 0 0 0 1.5px rgba(255,236,200,.18);padding:44px 48px;color:#fff;opacity:0}
.lab{font:30px GB;letter-spacing:.14em;color:#ffcf6b}
.big{font:500 150px/1 J;letter-spacing:-.01em}
.wk{font:34px GB;color:#f3d9a8;letter-spacing:.06em}
.jp{font:64px/1.25 G9}
</style>
<div id="stage"></div><div id="chip"><i></i><b>おでかけニュース</b><span>%CHIP%</span></div><div id="bar"></div><div id="cred"></div><div id="cap"><div id="capt"></div></div><div id="flash"></div>
<script>
const C=%CUTS%,PH=%PH%,CAP=%CAP%,TOTAL=%TOTAL%;
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),sm=(t,a,b)=>cl((t-a)/(b-a)),eo=x=>1-Math.pow(1-x,3),eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,
 back=x=>{const c1=1.7,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)},$=s=>document.querySelector(s);
const chars=s=>[...s].map(c=>`<span>${c}</span>`).join('');
function photo(k){const p=PH[k];return `<img class="ph" src="${p.src}" data-w="${p.w}" data-h="${p.h}">`}
function build(){const st=$('#stage');C.forEach((c,i)=>{const d=document.createElement('div');d.className='cut';d.id='c'+i;let h='';
  if(c.img)h+=photo(c.img);if(c.k=='split')h+=`<div class="ov" style="clip-path:inset(0 0 0 50%)" id="s${i}">${photo(c.img2)}</div>`;
  h+=`<div class="shade" style="background:${c.shade||'linear-gradient(180deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)'}"></div><div class="ov">`;
  if(c.k=='hook')h+=`<div class="hl" style="top:300px;left:56px;right:56px;font-size:100px;line-height:1.2">${chars(c.h1)}</div><div class="hl" style="top:430px;left:56px;right:40px;font-size:${Math.min(124,Math.floor(960/[...c.h2].length))}px;line-height:1.15;color:#ffcf6b;white-space:nowrap">${chars(c.h2)}</div>`;
  if(c.k=='date')h+=`<div class="card" style="top:560px"><div class="lab">${c.lab}</div><div style="display:flex;align-items:flex-end;gap:26px;margin-top:22px"><div><div class="big">${c.a}</div><div class="wk">${c.aw}</div></div><div style="font:500 80px J;color:#ffcf6b;padding-bottom:40px">→</div><div><div class="big">${c.b}</div><div class="wk">${c.bw}</div></div></div><div style="margin-top:34px;height:12px;border-radius:6px;background:rgba(255,255,255,.15);overflow:hidden"><div class="fill" style="height:100%;width:0;background:linear-gradient(90deg,#ffcf6b,#ff7a3d)"></div></div><div class="wk" style="margin-top:14px;font-size:30px">${c.note||''}</div></div>`;
  if(c.k=='time')h+=`<div class="card" style="top:600px;display:flex;align-items:center;gap:40px"><svg width="220" height="220" viewBox="0 0 220 220"><circle cx="110" cy="110" r="92" fill="none" stroke="rgba(255,255,255,.15)" stroke-width="16"/><circle class="arc" cx="110" cy="110" r="92" fill="none" stroke="#ffcf6b" stroke-width="16" stroke-linecap="round" transform="rotate(-90 110 110)" stroke-dasharray="578" stroke-dashoffset="578"/><line class="hand" x1="110" y1="110" x2="110" y2="42" stroke="#fff" stroke-width="8" stroke-linecap="round"/><circle cx="110" cy="110" r="10" fill="#fff"/></svg><div><div class="lab">${c.lab}</div><div style="font:500 104px/1.05 J;margin-top:12px">${c.a}</div><div style="font:500 60px J;color:#f3d9a8">〜 ${c.b}</div></div></div>`;
  if(c.k=='split')h+=`<div id="dv${i}" style="position:absolute;top:0;bottom:0;left:540px;width:6px;margin-left:-3px;background:#fff;box-shadow:0 0 24px rgba(255,255,255,.8)"></div><div class="hl tag" style="top:330px;left:60px;font-size:60px">昼の拝観</div><div class="hl tag" style="top:330px;left:600px;right:auto;font-size:60px;color:#ffcf6b">夜の拝観</div><div class="card stamp" style="top:880px;left:200px;right:270px;text-align:center;padding:30px"><div class="jp" style="font-size:72px">入れ替え制</div><div class="wk" style="margin-top:8px;font-size:32px">続けては見られません</div></div>`;
  if(c.k=='stamp')h+=`<div class="card" style="top:640px;text-align:center"><div class="lab">${c.lab}</div><div class="jp" style="margin-top:14px;font-size:84px">${c.a}</div><div class="wk" style="margin-top:10px">${c.b}</div></div>`;
  if(c.k=='route')h+=`<div class="card" style="top:430px;padding:50px 48px 46px"><div class="lab">行き方</div><svg viewBox="0 0 780 520" width="100%" style="margin-top:20px;overflow:visible"><path class="rt" d="M60 470 C 200 470, 210 300, 360 280 S 600 120, 700 70" fill="none" stroke="#ffcf6b" stroke-width="12" stroke-linecap="round" stroke-dasharray="1000" stroke-dashoffset="1000"/><circle cx="60" cy="470" r="22" fill="#fff"/><circle class="dst" cx="700" cy="70" r="26" fill="#e0392b" stroke="#fff" stroke-width="6" opacity="0"/><g class="bus"><rect x="-40" y="-26" width="80" height="52" rx="12" fill="#2f7d4f" stroke="#fff" stroke-width="4"/><text x="0" y="12" text-anchor="middle" font-family="J" font-weight="600" font-size="34" fill="#fff">5</text></g><text x="60" y="530" text-anchor="middle" font-family="GB" font-size="34" fill="#fff">京都駅</text><text class="dsl" x="700" y="20" text-anchor="end" font-family="GB" font-size="36" fill="#fff" opacity="0">永観堂</text></svg><div style="display:flex;gap:18px;margin-top:30px;flex-wrap:wrap"><div style="font:40px G9">市バス 5系統</div><div class="wk" style="font-size:36px;align-self:center">南禅寺・永観堂道 下車 徒歩3分</div></div><div class="nocar" style="display:flex;align-items:center;gap:20px;margin-top:26px;opacity:0"><svg width="84" height="84" viewBox="0 0 84 84"><circle cx="42" cy="42" r="36" fill="none" stroke="#e0392b" stroke-width="8"/><path d="M22 50 h40 v-8 l-6 -12 h-28 l-6 12 z" fill="#fff"/><circle cx="30" cy="54" r="6" fill="#fff"/><circle cx="54" cy="54" r="6" fill="#fff"/><line x1="17" y1="67" x2="67" y2="17" stroke="#e0392b" stroke-width="8"/></svg><div style="font:44px G9">車の乗り入れ停止</div></div></div>`;
  if(c.k=='meter')h+=`<div class="card" style="top:560px"><div class="lab">${c.lab}</div><div class="jp" style="margin-top:14px;font-size:76px">${c.a}</div><div style="display:flex;gap:18px;margin-top:34px">${[0,1,2,3,4].map(j=>`<svg class="pp" width="110" height="140" viewBox="0 0 110 140"><circle cx="55" cy="34" r="26" fill="currentColor"/><path d="M12 136 q0-70 43-70 q43 0 43 70z" fill="currentColor"/></svg>`).join('')}</div><div style="display:flex;justify-content:space-between;margin-top:10px" class="wk"><span>すいている</span><span style="color:#ff7a5a">とても混む</span></div></div>`;
  if(c.k=='end')h+=`<div class="hl" style="top:420px;font-size:84px;line-height:1.25;text-align:center;left:60px;right:60px">${chars(c.h1)}</div><div class="card" style="top:760px;left:150px;right:150px;text-align:center;padding:36px"><div class="lab">TOWN NOTE</div><div class="jp" style="font-size:56px;margin-top:10px">関西おでかけリスト</div><div class="wk" style="margin-top:12px;font-size:32px">日付と地図でさがせる・プロフィールのリンクから</div></div><div class="card sv" style="top:1080px;left:250px;right:250px;text-align:center;padding:26px;background:#ffcf6b;color:#1a1208"><div style="font:46px G9">保存して、おでかけ前に</div></div>`;
  h+='</div>';d.innerHTML=h;st.appendChild(d)})}
function kb(img,c,u){const W=+img.dataset.w,H=+img.dataset.h,sw=1920*W/H;const f=c.kb||[1.06,.5,1.0,.4];  // [始めの大きさ, 始めの横の位置0〜1, 終わりの大きさ, 終わりの位置]
  const s=f[0]+(f[2]-f[0])*u,px=f[1]+(f[3]-f[1])*u;const ww=sw*s,hh=1920*s;const x=-(ww-1080)*px,y=-(hh-1920)*.5;img.style.width=sw+'px';img.style.transform=`translate(${x}px,${y}px) scale(${s})`}
function render(t){const D=.22;
  $('#bar').style.width=(1080*cl(t/TOTAL)).toFixed(1)+'px';let cur=null;
  C.forEach((c,i)=>{const el=document.getElementById('c'+i);const on=t>=c.t0-D&&t<c.t1+D;el.style.visibility=on?'visible':'hidden';if(!on)return;
    const u=cl((t-c.t0+D)/(c.t1-c.t0+2*D));el.querySelectorAll(':scope > .ph').forEach(im=>kb(im,c,u));if(c.k=='split'){const im=el.querySelector('#s'+i+' .ph');kb(im,Object.assign({},c,{kb:c.kb2||c.kb}),u)}
    // 切り替え：拍の上で、次の絵が右から速く入る（ぶれ）
    let x=0,bl=0;if(i>0&&t<c.t0+D){const q=sm(t,c.t0-D,c.t0+D);x=(1-eio(q))*1080;bl=Math.sin(Math.PI*q)*18}
    if(i<C.length-1&&t>c.t1-D){const q=sm(t,c.t1-D,c.t1+D);x=-eio(q)*1080;bl=Math.sin(Math.PI*q)*18}
    el.style.transform=`translateX(${x.toFixed(1)}px)`;el.style.filter=bl>.5?`blur(${bl.toFixed(1)}px)`:'none';el.style.zIndex=i;
    const a=t-c.t0;if(t>=c.t0&&t<c.t1)cur=c;
    el.querySelectorAll('.hl span').forEach((s,j)=>{const q=i==0?sm(a,-.25+j*.04,.05+j*.04):sm(a,.05+j*.045,.35+j*.045);s.style.opacity=q;s.style.transform=`translateY(${(1-eo(q))*40}px) scale(${.6+.4*back(q)})`});
    el.querySelectorAll('.card').forEach((cd,j)=>{const q=sm(a,.12+j*.25,.5+j*.25);cd.style.opacity=eo(q);cd.style.transform=`translateY(${(1-eo(q))*60}px) scale(${.94+.06*back(q)})`});
    el.querySelectorAll('.fill').forEach(f=>f.style.width=(100*eio(sm(a,.5,1.6)))+'%');
    el.querySelectorAll('.arc').forEach(f=>f.setAttribute('stroke-dashoffset',(578*(1-.5*eio(sm(a,.4,1.5)))).toFixed(1)));
    el.querySelectorAll('.hand').forEach(f=>f.setAttribute('transform',`rotate(${(-150+180*eio(sm(a,.4,1.5))).toFixed(1)} 110 110)`));
    if(c.k=='split'){const q=eio(sm(a,0,.8));const p=1080*(1-.5*q);el.querySelector('#s'+i).style.clipPath=`inset(0 0 0 ${p}px)`;document.getElementById('dv'+i).style.left=p+'px';el.querySelectorAll('.tag').forEach((g,j)=>g.style.opacity=sm(a,.5+j*.15,.8+j*.15))}
    if(c.k=='route'){const q=eio(sm(a,.45,1.9));const pth=el.querySelector('.rt');pth.setAttribute('stroke-dashoffset',(1000*(1-q)).toFixed(1));const L=pth.getTotalLength(),pt=pth.getPointAtLength(L*q);el.querySelector('.bus').setAttribute('transform',`translate(${pt.x},${pt.y})`);
      const d=sm(a,1.8,2.1);el.querySelector('.dst').setAttribute('opacity',d);el.querySelector('.dsl').setAttribute('opacity',d);el.querySelector('.nocar').style.opacity=eo(sm(a,1.9,2.3))}
    if(c.k=='meter')el.querySelectorAll('.pp').forEach((p,j)=>{const q=sm(a,.5+j*.16,.7+j*.16);p.style.color=q>0?(j>=3?'#ff6a4a':'#ffcf6b'):'rgba(255,255,255,.2)';p.style.transform=`scale(${.8+.2*back(q)})`});
    if(c.k=='end'){const sv=el.querySelector('.sv');if(a>1.6)sv.style.transform=`scale(${(1+.04*Math.sin((a-1.6)*6)).toFixed(3)})`}
  });
  const pc=cur&&PH[cur.img];$('#cred').textContent=pc?`写真：${pc.artist}（${pc.license}）`+(cur.k=='split'&&PH[cur.img2]?` ／ ${PH[cur.img2].artist}（${PH[cur.img2].license}）`:''):'';
  const fl=C.some(c=>c.flash&&Math.abs(t-c.t0)<.18);$('#flash').style.opacity=fl?(.5*(1-Math.min(...C.filter(c=>c.flash).map(c=>Math.abs(t-c.t0)))/.18)).toFixed(3):0;
  const el=$('#capt');let ci=-1;for(let i=0;i<CAP.length;i++)if(t>=CAP[i].t0-.06&&t<CAP[i].t1)ci=i;let out=1;
  if(ci<0){for(let i=0;i<CAP.length;i++)if(CAP[i].t1<=t)ci=i;if(ci<0){el.style.opacity=0;return}out=1-sm(t,CAP[ci].t1,CAP[ci].t1+.2)}
  const K=CAP[ci],q=cl((t-K.t0)/Math.max(.2,K.t1-K.t0-.25)),n=Math.round(q*K.x.length);el.innerHTML='<em>'+K.x.slice(0,n)+'</em>'+K.x.slice(n);el.style.opacity=eo(sm(t,K.t0-.06,K.t0+.1))*out}
build();
</script>"""
html = (html.replace('%F%', F).replace('%CUTS%', json.dumps(cuts, ensure_ascii=False)).replace('%PH%', json.dumps(PH, ensure_ascii=False))
        .replace('%CAP%', json.dumps(CAP, ensure_ascii=False)).replace('%TOTAL%', f'{TOTAL:.3f}').replace('%CHIP%', spec.get('chip', '')))
open(f'{W}/news2.html', 'w').write(html)
open(f'{W}/rec.js', 'w').write(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.setDefaultTimeout(240000);p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://{W}/news2.html');await p.evaluate(()=>document.fonts.ready);await p.evaluate(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>0))));await p.waitForTimeout(300);
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{W}/c-'+t+'.jpg',type:'jpeg',quality:88}});}}await b.close();return}}
const fs=require('fs');const A=+(process.env.FR0||0),B=+(process.env.FR1||1e9);for(let i=A;i<30*{TOTAL:.3f}&&i<B;i++){{const f='{W}/fr/'+String(i).padStart(4,'0')+'.jpg';if(fs.existsSync(f))continue;await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:f,type:'jpeg',quality:92}});}}await b.close()}})();""")
if STILL:
    subprocess.run(['node', f'{W}/rec.js', STILL], check=True); sys.exit()
NF = int(30 * TOTAL) + 1; K = int(os.environ.get('WORKERS', '4')); ps = []
for i in range(K): ps.append(subprocess.Popen(['node', f'{W}/rec.js'], env=dict(os.environ, FR0=str(NF * i // K), FR1=str(NF * (i + 1) // K))))
if any(p.wait() for p in ps): sys.exit('コマを撮れない')
# 音：曲＋声（声の間は曲を下げる）＋切り替えの「シュッ」（作った音）＋最後に -14 LUFS
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{TOTAL + 1:.2f}', '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '48000', f'{W}/bgm.wav'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'anoisesrc=d=0.45:c=pink:a=0.6', '-af', 'highpass=f=900,lowpass=f=7000,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.25,volume=0.9', '-ar', '48000', f'{W}/whoosh.wav'], check=True)
ins = ['-i', f'{W}/bgm.wav']; flt = []; k = 2
for n in range(N):
    ins += ['-i', f'{VDIR}/{SP}-{n:02d}.wav']; flt.append(f'[{k}:a]aresample=48000,adelay={int(VDL[n] * 1000)}:all=1[v{n}]'); k += 1
flt.append(''.join(f'[v{n}]' for n in range(N)) + f'amix=inputs={N}:normalize=0,volume=1.7,apad=whole_dur={TOTAL + 1:.2f},asplit=2[vo][sc]')
wx = []
for c in cuts[1:]:
    ins += ['-i', f'{W}/whoosh.wav']; flt.append(f'[{k}:a]adelay={int(max(0, c["t0"] - .25) * 1000)}:all=1,volume=.45[w{k}]'); wx.append(f'[w{k}]'); k += 1
flt.append(''.join(wx) + f'amix=inputs={len(wx)}:normalize=0,apad=whole_dur={TOTAL + 1:.2f}[fx]')
flt.append(f'[1:a]afade=t=in:d=0.3,afade=t=out:st={TOTAL - 1.8:.2f}:d=1.8[bg0]')
flt.append('[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=500:makeup=1[bg]')
flt.append('[bg][vo][fx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]')
flt.append("[0:v]format=gbrp,eq=contrast=1.04:saturation=1.08,vignette=angle=PI/6,noise=alls=2:allf=t,format=yuv420p[vv]")
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg'] + ins + ['-filter_complex', ';'.join(flt), '-map', '[vv]', '-map', '[a]', '-t', f'{TOTAL:.2f}',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', OUT], check=True)
print(OUT, round(TOTAL, 1), '秒')
