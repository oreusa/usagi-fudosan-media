"""絵本を開く型のリール見本（11/12 月）。
使い方: python3 ehon.py spec.json out.mp4 [静止画の時刻 "1,3,8"]   声: VDIR=shots/voice/<name> SP=20（無ければ声なし）
1080x1920・30fps。render(t) で1コマずつ描いて ffmpeg でつなぐ（tools/outing_reel/make.py と同じ流れ）。"""
import json, os, subprocess, sys, wave

ROOT = os.environ.get('ROOT', '/home/user/usagi-fudosan-media')
spec = json.load(open(sys.argv[1])); OUT = os.path.abspath(sys.argv[2]); STILL = sys.argv[3] if len(sys.argv) > 3 else ''
W = os.path.abspath(os.environ.get('WORK', 'ehon-work')); os.makedirs(W + '/fr', exist_ok=True)
VDIR = os.environ.get('VDIR', ''); SP = os.environ.get('SP', '20')
T = spec['text']
N = 5


def dur(n):
    p = f'{VDIR}/{SP}-{n:02d}.wav'
    if not VDIR or not os.path.exists(p): return 2.6
    w = wave.open(p); return w.getnframes() / w.getframerate()


VD = [dur(n) for n in range(N)]
OPEN = 2.7          # 表紙が開ききる時刻
TURN = 0.95         # めくる長さ
LEAD = 0.45         # ページが見えてから声まで
ST = []; t = OPEN
for n in range(N):
    ST.append(t); t += max(3.3, LEAD + VD[n] + 0.75) + (0.6 if n in (2, 4) else 0)
TOTAL = t + 0.8
F = ROOT + '/tools/fonts'
d = T['date']
info = T.get('info', [])
PAGE = dict(
    t1=T.get('ehon1', ['奈良の山の上に、', '十三重の塔が', 'たっています。']),
    t2=T.get('ehon2', ['秋になると、', '塔のまわりは', 'まっ赤に染まります。']),
    t4=T.get('ehon4', ['夜になると、', 'あかりが', 'ともります。']),
    fes=T.get('date_title', '紅葉まつり'), place=T.get('place', ''), d=d, night=T.get('ehon_night', ['11.14', 'SAT', 'から', '日没〜20時半']),
    info=info, note=T.get('info_note', ''), title=T['title'], corner=T.get('corner', ''),
)
html = r"""<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:M;src:url(file://%F%/ShipporiMincho-Medium.ttf)}
@font-face{font-family:MB;src:url(file://%F%/ShipporiMincho-Bold.ttf)}
@font-face{font-family:G;src:url(file://%F%/ZenKakuGothicNew-Medium.ttf)}
@font-face{font-family:J;src:url(file://%F%/Jost-VF.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#2b211c}
#desk{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 42%,#5a463a 0%,#3a2c25 55%,#211813 100%)}
#tint{position:absolute;inset:0;opacity:0}
#pat{position:absolute;inset:0;width:1080px;height:1920px;opacity:.16}
#bk circle{filter:blur(14px)}
#deco{position:absolute;inset:0;width:1080px;height:1920px;pointer-events:none}
#grain{position:absolute;inset:0;opacity:.35;mix-blend-mode:overlay;pointer-events:none}
#top{position:absolute;left:0;right:0;top:92px;text-align:center;font:500 25px J;letter-spacing:.42em;color:#d9c39a}
#top b{display:block;font:500 30px M;letter-spacing:.3em;margin-top:10px;color:#efe2c6}
#pg{position:absolute;left:0;right:0;top:1640px;text-align:center;font:500 26px M;letter-spacing:.5em;color:#cdb890}
#cam{position:absolute;inset:0;transform-origin:540px 900px}
#book{position:absolute;left:84px;top:232px;width:920px;height:1380px;perspective:2600px;perspective-origin:20% 50%}
#shadow{position:absolute;left:-18px;top:14px;width:960px;height:1392px;border-radius:10px;background:rgba(0,0,0,.5);filter:blur(26px)}
#block{position:absolute;left:6px;top:8px;width:926px;height:1380px;border-radius:4px 10px 10px 4px;background:repeating-linear-gradient(90deg,#efe5cf 0 2px,#d8ccb0 2px 3px)}
.pg{position:absolute;inset:0;transform-origin:0 50%;transform-style:preserve-3d;will-change:transform}
.face{position:absolute;inset:0;backface-visibility:hidden;border-radius:3px 9px 9px 3px;overflow:hidden;background:#f6efdf}
.back{transform:rotateY(180deg);background:linear-gradient(90deg,#efe6d2,#f7f1e3 30%,#e9dfc8)}
.face svg{position:absolute;inset:0;width:100%;height:100%}
.gut{position:absolute;left:0;top:0;bottom:0;width:70px;background:linear-gradient(90deg,rgba(60,35,20,.34),rgba(60,35,20,0));pointer-events:none}
.shade{position:absolute;inset:0;background:#1a0f0a;opacity:0;pointer-events:none}
.vt{position:absolute;writing-mode:vertical-rl;font-family:M;color:#4a3328;letter-spacing:.2em;line-height:1.9;white-space:nowrap}
.vt span{display:inline-block;opacity:0}
.cover{background:linear-gradient(100deg,#5d1f1b,#7c2a22 18%,#742620 70%,#5a1c18);border-radius:4px 12px 12px 4px}
.cover:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px),repeating-linear-gradient(90deg,rgba(0,0,0,.05) 0 2px,transparent 2px 5px)}
.cover .spine{position:absolute;left:0;top:0;bottom:0;width:46px;background:linear-gradient(90deg,rgba(0,0,0,.35),rgba(0,0,0,0))}
.gold{color:#e3c88c}
.fr1{position:absolute;inset:54px 50px 54px 70px;border:2px solid #d8b874;border-radius:4px}
.fr2{position:absolute;inset:68px 64px 68px 84px;border:1px solid rgba(216,184,116,.7);border-radius:2px}
.sheen{position:absolute;inset:0;pointer-events:none;opacity:0;background:linear-gradient(90deg,rgba(255,255,255,0) 20%,rgba(255,255,255,.5) 52%,rgba(40,20,10,.35) 64%,rgba(40,20,10,0) 86%)}
.pop{transform-box:fill-box;transform-origin:50% 100%}
#ribbon{position:absolute;left:650px;top:1372px;width:30px;height:150px;background:linear-gradient(90deg,#8e2a22,#b53a2c 45%,#8a261f);clip-path:polygon(0 0,100% 0,100% 100%,50% 86%,0 100%);transform-origin:50% 0;box-shadow:0 0 6px rgba(0,0,0,.4)}
#lamp{position:absolute;inset:0;pointer-events:none;background:radial-gradient(70% 45% at 24% 16%,rgba(255,214,160,.2),rgba(255,214,160,0) 70%),radial-gradient(120% 90% at 50% 46%,rgba(0,0,0,0) 55%,rgba(0,0,0,.42) 100%)}
#foil{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;background:linear-gradient(115deg,rgba(255,240,200,0) 40%,rgba(255,240,200,.55) 50%,rgba(255,240,200,0) 60%);background-size:300% 100%;opacity:.8}
#seal{position:absolute;right:104px;top:1120px;width:104px;height:104px;border-radius:14px;background:#b5332a;color:#f8ecd8;font:700 40px MB;writing-mode:vertical-rl;display:flex;align-items:center;justify-content:center;letter-spacing:.08em;opacity:0;box-shadow:inset 0 0 0 3px rgba(248,236,216,.55)}
.num{font-family:J;font-weight:300;letter-spacing:.02em}
.row{position:absolute;left:150px;right:120px;display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid rgba(110,80,60,.35);padding-bottom:16px;font:500 40px M;color:#4a3328;letter-spacing:.12em;opacity:0}
.row b{font:500 46px M;letter-spacing:.06em}
</style>
<div id="desk"></div><div id="tint"></div>
<svg id="pat" viewBox="0 0 1080 1920"><defs><pattern id="sp" width="96" height="96" patternUnits="userSpaceOnUse"><g fill="none" stroke="#e3c88c" stroke-width="1.6"><circle cx="48" cy="48" r="48"/><circle cx="0" cy="0" r="48"/><circle cx="96" cy="0" r="48"/><circle cx="0" cy="96" r="48"/><circle cx="96" cy="96" r="48"/></g></pattern>
<radialGradient id="pm" cx=".5" cy=".47" r=".75"><stop offset=".35" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></radialGradient><mask id="pmk"><rect width="1080" height="1920" fill="url(#pm)"/></mask></defs><rect width="1080" height="1920" fill="url(#sp)" mask="url(#pmk)"/></svg>
<svg id="bk" style="position:absolute;inset:0;width:1080px;height:1920px" viewBox="0 0 1080 1920"></svg>
<div id="top">KANSAI ─ ODEKAKE<b>関西おでかけリスト</b></div>
<div id="cam"><div id="book"><div id="shadow"></div><div id="ribbon"></div><div id="block"></div><div id="pages"></div></div></div>
<svg id="deco" viewBox="0 0 1080 1920"></svg><div id="pg"></div><div id="lamp"></div>
<svg id="grain"><filter id="gn"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 .55 0"/></filter><rect width="100%" height="100%" filter="url(#gn)"/></svg>
<script>
const P=%PAGE%,ST=%ST%,OPEN=%OPEN%,TURN=%TURN%,TOTAL=%TOTAL%,N=5;
const $=s=>document.querySelector(s);
function rng(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,eo=x=>1-Math.pow(1-x,3),sm=(t,a,b)=>cl((t-a)/(b-a));
const DEFS=`<defs>
<filter id="wc" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".018" numOctaves="3" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="16"/></filter>
<filter id="wc2" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="11" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="9"/></filter>
<filter id="pap"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="4" seed="3"/><feColorMatrix values="0 0 0 0 .42  0 0 0 0 .3  0 0 0 0 .2  0 0 0 .5 -.12"/></filter>
<filter id="fib"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .22  0 0 0 0 .15  0 0 0 .32 -.05"/></filter>
<filter id="wc3" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="2" seed="5" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="5"/></filter><filter id="bl"><feGaussianBlur stdDeviation="26"/></filter><filter id="bl2"><feGaussianBlur stdDeviation="7"/></filter>
</defs>`;
const PAPER=`<rect width="920" height="1380" filter="url(#pap)" opacity=".5"/><rect width="920" height="1380" filter="url(#fib)" opacity=".55"/>`;
function hill(y,amp,seed,x0=-40,x1=960){const r=rng(seed);const a=r()*6,b=r()*6,c=r()*6;let s=`M${x0},1400 L${x0},${y}`;
  for(let x=x0;x<=x1;x+=20){const u=x/920;s+=` L${x},${(y-amp*(.55*Math.sin(u*3.1+a)+.3*Math.sin(u*7.3+b)+.15*Math.sin(u*13+c))).toFixed(1)}`}return s+` L${x1},1400Z`}
function hy(y,amp,seed,x){const r=rng(seed);const a=r()*6,b=r()*6,c=r()*6;const u=x/920;return y-amp*(.55*Math.sin(u*3.1+a)+.3*Math.sin(u*7.3+b)+.15*Math.sin(u*13+c))}
function trees(seed,n,x0,x1,yf,sz,cols,op=.92){const r=rng(seed);let s='';const L=[];
  for(let i=0;i<n;i++){const x=x0+(x1-x0)*r();L.push([x,yf(x)+r()*26-8,sz*(.65+r()*.7),cols[Math.floor(r()*cols.length)],r()])}
  L.sort((a,b)=>a[1]-b[1]);
  for(const[x,y,z,c,q]of L){s+=`<g class="pop" data-d="${(q*.55+(1380-y)/1380*.25).toFixed(2)}" opacity="${op}"><rect x="${x-z*.045}" y="${y-z*.25}" width="${z*.09}" height="${z*.5}" fill="#4b3226" opacity=".7"/>`;
    for(let k=0;k<5;k++){const a=k*1.3+q*6,rr=z*(.32+.12*((k*37%10)/10));s+=`<ellipse cx="${(x+Math.cos(a)*z*.3).toFixed(1)}" cy="${(y-z*.55+Math.sin(a)*z*.22).toFixed(1)}" rx="${rr.toFixed(1)}" ry="${(rr*.82).toFixed(1)}" fill="${c}" opacity=".78"/>`}
    s+=`<ellipse cx="${x-z*.12}" cy="${y-z*.72}" rx="${z*.2}" ry="${z*.13}" fill="#fff" opacity=".13"/></g>`}
  return s}
function tower(cx,by,k,night){let s='';const roof=night?'#15121c':'#3b2a24',body=night?'#3a2420':'#7b4a33',lit='#ffd27a';
  s+=`<path d="M${cx-150*k},${by} L${cx+150*k},${by} L${cx+132*k},${by-26*k} L${cx-132*k},${by-26*k}Z" fill="${night?'#22202c':'#8d857a'}"/>`;
  let y=by-26*k;
  for(let i=0;i<13;i++){const w=(i==0?300:262-i*13)*k,h=(i==0?64:15)*k,bw=(i==0?150:(92-i*4.2))*k,rh=(i==0?26:19)*k;
    s+=`<rect x="${cx-bw/2}" y="${y-h}" width="${bw}" height="${h}" fill="${body}"/>`;
    if(i==0){s+=`<rect x="${cx-bw/2+14*k}" y="${y-h+12*k}" width="${bw-28*k}" height="${h-12*k}" fill="${night?lit:'#5a3526'}" opacity="${night?.95:.8}"/>`;
      for(let j=1;j<4;j++)s+=`<line x1="${cx-bw/2+14*k+(bw-28*k)*j/4}" y1="${y-h+12*k}" x2="${cx-bw/2+14*k+(bw-28*k)*j/4}" y2="${y}" stroke="${body}" stroke-width="${3*k}"/>`}
    else if(night)s+=`<rect x="${cx-bw/2+5*k}" y="${y-h+3*k}" width="${bw-10*k}" height="${h-5*k}" fill="${lit}" opacity=".75"/>`;
    y-=h;
    s+=`<path d="M${cx-w/2-10*k},${y-2*k} Q${cx-w/2+16*k},${y+3*k} ${cx-w*.28},${y-rh*.55} L${cx-bw*.42},${y-rh} L${cx+bw*.42},${y-rh} L${cx+w*.28},${y-rh*.55} Q${cx+w/2-16*k},${y+3*k} ${cx+w/2+10*k},${y-2*k} Q${cx+w/2-10*k},${y+9*k} ${cx+w*.3},${y+7*k} L${cx-w*.3},${y+7*k} Q${cx-w/2+10*k},${y+9*k} ${cx-w/2-10*k},${y-2*k}Z" fill="${roof}"/>`;
    if(!night)s+=`<path d="M${cx-w*.3},${y-rh*.5} L${cx+w*.3},${y-rh*.5}" stroke="#fff" stroke-width="${1.6*k}" opacity=".16"/>`;
    y-=rh}
  s+=`<line x1="${cx}" y1="${y}" x2="${cx}" y2="${y-74*k}" stroke="${night?'#c9a45a':'#5b4a2c'}" stroke-width="${5*k}"/>`;
  for(let j=0;j<5;j++)s+=`<ellipse cx="${cx}" cy="${y-12*k-j*11*k}" rx="${(13-j*1.6)*k}" ry="${3.2*k}" fill="${night?'#c9a45a':'#5b4a2c'}"/>`;
  return s}
function leafPath(R){const L=[1,.9,.7,.42],pts=[];const P=(r,d)=>{const a=(d-90)*Math.PI/180;pts.push((Math.cos(a)*r*R).toFixed(3)+','+(Math.sin(a)*r*R+.12*R).toFixed(3))};
  for(let k=-3;k<=3;k++){const c=k*40,l=L[Math.abs(k)];P(.2,c-20);P(l*.5,c-7);P(l*.62,c-13);P(l*.8,c-4);P(l,c);P(l*.8,c+4);P(l*.62,c+13);P(l*.5,c+7)}
  P(.2,140);P(.1,172);P(.62,177);P(.62,183);P(.1,188);return 'M'+pts.join('L')+'Z'}
const LP=leafPath(1);
function vtext(lines,x,y,size,ex,id){return `<div class="vt" id="${id}" style="right:${x}px;top:${y}px;font-size:${size}px;${ex||''}">`+lines.map(l=>[...l].map(c=>`<span>${c}</span>`).join('')).join('<br>')+`</div>`}
function scene(mode){ // 0 昼 1 秋 2 夜
  const sky=[['#f7f0df','#f3e3bf'],['#fbeede','#f6cfa0'],['#10152f','#343a6c']][mode];
  const far=['#c3cfc0','#e0b08c','#1b2142'][mode],mid=['#9db794','#cf7f55','#171a36'][mode],near=['#7c9f6c','#b9513a','#11132a'][mode];
  const tc=[['#5f8a55','#7da35f','#93b068','#b8bf6a','#55794f'],['#b5332a','#d4552d','#e8862e','#f0b23a','#c9402b','#9e2a2a'],['#7c2622','#a8382a','#c4552b','#8f2d2a','#d9772e']][mode];
  const fy=x=>hy(880,60,21,x),ny=x=>hy(1120,46,33,x);
  let s=`<svg viewBox="0 0 920 1380">${DEFS}<defs><linearGradient id="sk${mode}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${sky[0]}"/><stop offset="1" stop-color="${sky[1]}"/></linearGradient>
  <linearGradient id="ms${mode}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${mode==2?'#5a6aa8':'#fff8ea'}" stop-opacity="0"/><stop offset=".55" stop-color="${mode==2?'#5a6aa8':'#fff8ea'}" stop-opacity="${mode==2?.28:.5}"/><stop offset="1" stop-color="${mode==2?'#5a6aa8':'#fff8ea'}" stop-opacity="0"/></linearGradient><radialGradient id="gl${mode}"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".95"/><stop offset=".5" stop-color="#ff9a4a" stop-opacity=".35"/><stop offset="1" stop-color="#ff9a4a" stop-opacity="0"/></radialGradient></defs>
  <rect width="920" height="1380" fill="url(#sk${mode})"/>`;
  if(mode==2){const r=rng(5);for(let i=0;i<70;i++)s+=`<circle class="star" cx="${(r()*920).toFixed(0)}" cy="${(r()*640).toFixed(0)}" r="${(1+r()*2.2).toFixed(1)}" fill="#fff6dc" opacity="${(.35+r()*.6).toFixed(2)}"/>`;
    s+=`<circle cx="235" cy="250" r="150" fill="#fff3c9" opacity=".12" filter="url(#bl)"/><circle cx="235" cy="250" r="62" fill="#fff1c4"/><circle cx="262" cy="236" r="58" fill="#1b2147" opacity=".0"/>`}
  else s+=`<circle cx="225" cy="270" r="${mode?92:78}" fill="${mode?'#f3a65a':'#fbe7b0'}" opacity="${mode?.6:.85}" filter="url(#wc2)"/>`;
  s+=`<g class="ly" data-a="6"><g filter="url(#wc)"><path d="${hill(760,90,3)}" fill="${far}" opacity=".8"/></g></g><g class="ly" data-a="14"><g filter="url(#wc)"><path d="${hill(880,60,21)}" fill="${mid}"/></g>`;
  s+=`<g filter="url(#wc2)">${trees(40+mode,16,-10,930,x=>fy(x)+26,96,tc,.9)}</g></g><rect x="-40" y="770" width="1000" height="260" fill="url(#ms${mode})"/>`;
  if(mode==2)s+=`<ellipse class="glow" cx="390" cy="800" rx="360" ry="420" fill="url(#gl2)" opacity=".55"/>`;
  s+=`<g class="ly" data-a="22"><g class="tw pop" data-d=".15" data-slow="1">${tower(390,980,1.06,mode==2)}</g></g>`;
  s+=`<g class="ly" data-a="38"><g filter="url(#wc)"><path d="${hill(1120,46,33)}" fill="${near}"/></g>`;
  s+=`<g filter="url(#wc2)">${trees(60+mode,7,-20,330,x=>ny(x)-60,170,tc)}${trees(70+mode,7,600,940,x=>ny(x)-60,170,tc)}${trees(80+mode,12,-20,940,x=>ny(x)+70,150,tc)}</g>`;
  if(mode==2){for(let i=0;i<5;i++){const x=120+i*170;s+=`<path class="beam" d="M${x-10},1250 L${x-90},820 L${x+90},820 L${x+10},1250Z" fill="#ffc97a" opacity=".0" filter="url(#bl2)"/>`}for(let i=0;i<9;i++){const x=70+i*98,y=1262+Math.sin(i*1.7)*16;s+=`<circle class="lan" cx="${x}" cy="${y}" r="46" fill="url(#gl2)" opacity=".8"/><rect x="${x-7}" y="${y-10}" width="14" height="20" rx="3" fill="#ffe2a0"/>`}}
  s+=`</g><g class="lv"></g>${PAPER}</svg>`;return s}
const NUMS=['一','二','三','四','五'];
function build(){
  const pages=[];
  // 表紙
  pages.push(`<div class="face cover"><div class="spine"></div><div class="fr1"></div><div class="fr2"></div>
   <div class="gold" style="position:absolute;left:0;right:0;top:138px;text-align:center;font:400 24px J;letter-spacing:.5em">${P.corner}</div>
   ${vtext(P.title,372,250,82,'font-family:MB;color:#e8cf96;line-height:1.75;letter-spacing:.16em','ct')}
   <svg viewBox="0 0 920 1380" style="opacity:.92"><g transform="translate(300,1210)" fill="#e3c88c">${tower(0,0,.5,false).replace(/fill="#[0-9a-f]{6}"/g,'fill="#e3c88c"').replace(/stroke="#[0-9a-f]{3,6}"/g,'stroke="#7c2a22"')}</g>
   <g transform="translate(250,1010) scale(22) rotate(18)"><path d="${LP}" fill="#e3c88c" opacity=".8"/></g></svg>
   <div style="position:absolute;right:108px;bottom:200px;width:216px;height:216px;border-radius:50%;background:#f6efdf;box-shadow:0 0 0 3px #d8b874,0 0 0 10px rgba(216,184,116,.28),0 6px 18px rgba(0,0,0,.35);display:flex;align-items:center;justify-content:center"><img src="file://%LOGO%" style="width:166px;height:166px"></div>
   <div class="gold" style="position:absolute;left:0;right:0;bottom:118px;text-align:center;font:500 30px M;letter-spacing:.16em;font-size:23px;line-height:1.7;bottom:104px">関西の不動産屋が、街の調査で見つけた<br>おでかけリスト</div><div id="foil"></div></div>`);
  pages.push(`<div class="face">${scene(0)}${vtext(P.t1,84,120,58,'','t0')}</div>`);
  pages.push(`<div class="face">${scene(1)}${vtext(P.t2,84,120,58,'','t1')}</div>`);
  // 日付
  pages.push(`<div class="face" style="background:#f6efdf"><svg viewBox="0 0 920 1380">${DEFS}<g filter="url(#wc3)"><g transform="translate(270,1010) scale(250) rotate(-16)"><path d="${LP}" fill="#d4552d" opacity=".82"/></g><g transform="translate(470,1150) scale(130) rotate(24)"><path d="${LP}" fill="#e8862e" opacity=".8"/></g><g transform="translate(130,1230) scale(86) rotate(60)"><path d="${LP}" fill="#f0b23a" opacity=".8"/></g></g><g class="lv"></g>${PAPER}</svg>
   ${vtext([P.fes],96,120,96,'font-family:MB;letter-spacing:.24em','t2')}
   <div id="d1" style="position:absolute;left:96px;top:150px;color:#4a3328;opacity:0"><div class="num" style="font-size:60px;letter-spacing:.06em;color:#8a6a55">${P.d[0]} <span style="font-size:30px;letter-spacing:.3em">${P.d[1]}</span></div><div style="width:2px;height:70px;background:#8a6a55;margin:22px 0 10px 60px"></div></div>
   <div id="d2" style="position:absolute;left:84px;top:330px;color:#3d2a22;opacity:0"><div class="num" style="font-size:230px;line-height:1">${P.d[2]}</div><div style="font:500 44px M;letter-spacing:.3em;margin:18px 0 0 10px"><span class="num" style="font-size:44px;letter-spacing:.3em">${P.d[3]}</span>　まで</div></div>
   <div id="seal">紅葉</div><div id="d3" style="position:absolute;left:96px;top:700px;font:500 38px M;letter-spacing:.22em;color:#6b4a3a;opacity:0">${P.place}</div></div>`);
  pages.push(`<div class="face">${scene(2)}${vtext(P.t4,84,120,58,'color:#f4e6c4','t3')}
   <div id="n1" style="position:absolute;left:560px;top:560px;color:#f4e6c4;opacity:0"><div class="num" style="font-size:92px;line-height:1">${P.night[0]}</div><div style="font:500 34px M;letter-spacing:.3em;margin-top:14px"><span class="num" style="font-size:34px;letter-spacing:.3em">${P.night[1]}</span>　${P.night[2]}</div><div style="font:500 40px M;letter-spacing:.2em;margin-top:26px">${P.night[3]}</div></div></div>`);
  // 案内
  pages.push(`<div class="face" style="background:#f6efdf"><svg viewBox="0 0 920 1380">${DEFS}<g filter="url(#wc3)" opacity=".9"><g transform="translate(760,170) scale(70) rotate(20)"><path d="${LP}" fill="#d4552d" opacity=".85"/></g><g transform="translate(660,120) scale(40) rotate(-40)"><path d="${LP}" fill="#f0b23a" opacity=".85"/></g></g><g transform="translate(460,1310)" opacity=".85">${tower(0,0,.28,false)}</g><g class="lv"></g>${PAPER}</svg>
   <div style="position:absolute;left:150px;top:150px;font:500 30px J;letter-spacing:.42em;color:#8a6a55">INFORMATION</div>
   <div style="position:absolute;left:150px;top:206px;font:700 62px MB;letter-spacing:.16em;color:#3d2a22" id="it">${P.place.split('｜')[0]}</div>
   ${P.info.map((r,i)=>`<div class="row" id="r${i}" style="top:${340+i*112}px"><span>${r[0]}</span><b>${r[1]}</b></div>`).join('')}
   <div id="nt" style="position:absolute;left:150px;right:110px;top:${340+P.info.length*112+6}px;font:500 28px M;letter-spacing:.1em;line-height:1.8;color:#7a5b4a;opacity:0">${P.note}</div>
   <div id="end" style="position:absolute;left:0;right:0;top:925px;text-align:center;opacity:0"><div style="font:500 44px M;letter-spacing:.24em;color:#3d2a22">つづきは、</div><div style="font:700 50px MB;letter-spacing:.2em;color:#a5332a;margin-top:18px">プロフィールのリンクから</div></div></div>`);
  $('#pages').innerHTML=pages.map((f,i)=>`<div class="pg" id="p${i}" style="z-index:${20-i}">${f}<div class="face back"></div>${i?'<div class="gut"></div>':''}<div class="shade"></div><div class="sheen"></div></div>`).reverse().join('');
  // まわりの飾り：もみじと光の粒
  {const r=rng(77),cols=['#c9402b','#e8862e','#f0b23a','#d4552d','#b5332a'];let s='<defs><filter id="ds" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="5" dy="9" stdDeviation="7" flood-color="#000" flood-opacity=".45"/></filter></defs>';
   const spots=[[70,150,58,-28],[168,96,34,40],[985,128,50,24],[905,70,30,-50],[52,1700,44,62],[150,1790,64,-18],[262,1850,32,30],[1010,1690,56,-36],[905,1800,40,18],[790,1862,30,-64],[1040,930,34,80],[30,1000,30,-80]];
   spots.forEach((q,i)=>{s+=`<g class="dl" data-i="${i}" data-x="${q[0]}" data-y="${q[1]}" data-z="${q[2]}" data-r="${q[3]}" filter="url(#ds)"><path d="${LP}" fill="${cols[i%5]}"/><path d="M0,.9 L0,-.8 M0,.2 L-.5,-.35 M0,.2 L.5,-.35" stroke="rgba(90,30,15,.45)" stroke-width=".035" fill="none"/></g>`});
   $('#deco').innerHTML=s;let b='';for(let i=0;i<16;i++)b+=`<circle data-x="${(r()*1080).toFixed(0)}" data-y="${(r()*1920).toFixed(0)}" data-p="${(r()*6).toFixed(2)}" r="${(10+r()*26).toFixed(0)}" fill="#ffdc9a"/>`;$('#bk').innerHTML=b}
  // 葉
  document.querySelectorAll('.lv').forEach((g,gi)=>{const r=rng(100+gi);let s='';const cols=['#c9402b','#e8862e','#f0b23a','#d4552d','#b5332a'];
    for(let i=0;i<16;i++)s+=`<g class="lf" data-x="${(r()*920).toFixed(0)}" data-s="${(.05+r()*.07).toFixed(3)}" data-p="${r().toFixed(3)}" data-z="${(14+r()*20).toFixed(0)}" data-w="${(r()*6).toFixed(2)}"><path d="${LP}" fill="${cols[i%5]}" opacity=".9"/></g>`;g.innerHTML=s});
}
function chars(id,t,t0,step=.07){const el=document.getElementById(id);if(!el)return;el.querySelectorAll('span').forEach((c,i)=>{const k=eo(sm(t,t0+i*step,t0+i*step+.45));c.style.opacity=k;c.style.transform=`translateY(${(1-k)*14}px)`})}
function fade(id,t,t0,d=.6,dy=18){const el=document.getElementById(id);if(!el)return;const k=eo(sm(t,t0,t0+d));el.style.opacity=k;el.style.transform=`translateY(${(1-k)*dy}px)`}
function render(t){
  // めくる
  const ang=[];ang[0]=eio(sm(t,OPEN-1.25,OPEN))*178;
  for(let i=1;i<=N;i++)ang[i]=i<N?eio(sm(t,ST[i]-TURN,ST[i]))*178:0;
  for(let i=0;i<=N;i++){const p=document.getElementById('p'+i),a=ang[i];
    p.style.transform=`rotateY(${-a}deg)`;p.style.visibility=a>=177.5?'hidden':'visible';
    p.querySelector('.shade').style.opacity=a>0&&a<178?.28*Math.sin(a/178*Math.PI):0;p.querySelector('.sheen').style.opacity=a>0&&a<90?.75*Math.sin(a/90*Math.PI):0;
    // 下のページに落ちる影
    if(i<N){const q=document.getElementById('p'+(i+1));const sh=q.querySelector('.shade');if(a>0&&a<178&&ang[i+1]==0)sh.style.opacity=.32*(1-a/178)}}
  // カメラ
  const z=t<OPEN?1.0+.05*eio(sm(t,0,OPEN)):1.05+.012*Math.sin(t*.5);
  $('#cam').style.transform=`scale(${z}) translateY(${t<OPEN?(1-eio(sm(t,0,OPEN)))*10:0}px) rotate(${(-.9+1.5*sm(t,0,TOTAL)).toFixed(3)}deg)`;$('#foil').style.backgroundPosition=(120-170*sm(t,.3,1.7))+'% 0';$('#ribbon').style.transform=`rotate(${(2.2*Math.sin(t*1.3)).toFixed(2)}deg)`;
  document.querySelectorAll('.dl').forEach(l=>{const d=l.dataset,i=+d.i,k=1;
    l.setAttribute('transform',`translate(${(+d.x+Math.sin(t*.6+i)*3).toFixed(1)},${(+d.y-(1-k)*120+Math.cos(t*.5+i*2)*2).toFixed(1)}) rotate(${(+d.r+(1-k)*90+Math.sin(t*.7+i)*3).toFixed(1)}) scale(${d.z})`);l.style.opacity=k});
  document.querySelectorAll('#bk circle').forEach(c=>{const d=c.dataset;c.setAttribute('cx',(+d.x+Math.sin(t*.25+ +d.p)*40).toFixed(1));c.setAttribute('cy',(((+d.y-t*14)%1920+1920)%1920).toFixed(1));c.style.opacity=(.07+.07*Math.sin(t*.8+d.p*3)).toFixed(3)});
  {const tn=$('#tint');const a=sm(t,ST[1]-TURN,ST[1]),b=sm(t,ST[2]-TURN,ST[2]),c=sm(t,ST[3]-TURN,ST[3]),e=sm(t,ST[4]-TURN,ST[4]);
   if(c>0&&e<1){tn.style.background='radial-gradient(120% 80% at 50% 42%,#2b3463,#121630)';tn.style.opacity=.85*c*(1-e)}else{tn.style.background='radial-gradient(120% 80% at 50% 42%,#7a3524,#3a1712)';tn.style.opacity=.6*a*(1-b)}}
  chars('ct',t,-9,.0);$('#top').style.opacity=1-.75*sm(t,OPEN-1.2,OPEN);
  // ページごと
  let cur=-1;for(let i=0;i<N;i++)if(t>=ST[i]-TURN*.5)cur=i;
  $('#pg').textContent=cur<0?'':NUMS[cur]+'　／　'+NUMS[N-1];
  for(let i=0;i<N;i++){const u=t-ST[i]+TURN*.55;const pg=document.getElementById('p'+(i+1));
    const svg=pg.querySelector('svg');const end=i<N-1?ST[i+1]:TOTAL;const k=sm(t,ST[i]-TURN,end);
    if(svg)svg.style.transform=`scale(${1.05-.03*k})`;
    pg.querySelectorAll('.ly').forEach(l=>l.setAttribute('transform',`translate(${((k-.5)*-l.dataset.a).toFixed(2)},0)`));
    pg.querySelectorAll('.pop').forEach(e=>{const d=+e.dataset.d,sl=e.dataset.slow?1.1:.65,x=sm(u,d,d+sl),c1=1.4,kk=x<=0?0:1+(c1+1)*Math.pow(x-1,3)+c1*Math.pow(x-1,2);e.style.transform=`scale(${(.92+.08*kk).toFixed(3)},${Math.max(0,kk).toFixed(3)})`});
    pg.querySelectorAll('.beam').forEach((b,j)=>b.style.opacity=(.16*eo(sm(u,1.0+j*.18,1.9+j*.18))*(.8+.2*Math.sin(t*1.7+j))).toFixed(3));
    pg.querySelectorAll('.lf').forEach(l=>{const d=l.dataset,ph=((t*d.s*1.0+ +d.p)%1+1)%1;const x=+d.x+Math.sin(t*.9+ +d.w)*46+ph*60,y=-60+ph*1500;
      l.setAttribute('transform',`translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${(t*40*(d.z%2?1:-1)+d.w*57).toFixed(1)}) scale(${d.z},${(d.z*(.55+.45*Math.cos(t*2.2+ +d.w))).toFixed(2)})`);
      l.style.opacity=(i==0||i==3)?0:(i==4?.55:1)});
    if(i==3){pg.querySelectorAll('.star').forEach((s,j)=>s.style.opacity=.35+.5*(.5+.5*Math.sin(t*2.1+j*1.7)));
      const g=pg.querySelector('.glow');if(g)g.style.opacity=.2+.5*eo(sm(u,.3,2.2))+.04*Math.sin(t*3);
      pg.querySelectorAll('.lan').forEach((s,j)=>s.style.opacity=.85*eo(sm(u,.5+j*.14,1.1+j*.14)));
      chars('t3',t,ST[i]-.1,.075);fade('n1',t,ST[i]+1.7,.7)}
    if(i==0)chars('t0',t,ST[i]-.15,.075);
    if(i==1)chars('t1',t,ST[i]-.15,.075);
    if(i==2){chars('t2',t,ST[i]-.15,.11);fade('d1',t,ST[i]+.25);fade('d2',t,ST[i]+.6,.8,26);fade('d3',t,ST[i]+1.3);const sl=document.getElementById('seal'),sk=sm(t,ST[i]+1.9,ST[i]+2.15);sl.style.opacity=sk;sl.style.transform=`rotate(-6deg) scale(${1.5-.5*eo(sk)})`}
    if(i==4){P.info.forEach((r,j)=>fade('r'+j,t,ST[i]+.05+j*.22,.6,14));fade('nt',t,ST[i]+1.1);fade('end',t,ST[i]+1.9,.8,20)}}
}
build();render(0);
</script>"""
html = (html.replace('%F%', F).replace('%LOGO%', ROOT + '/tools/brand/logo.png').replace('%PAGE%', json.dumps(PAGE, ensure_ascii=False)).replace('%ST%', json.dumps(ST))
        .replace('%OPEN%', str(OPEN)).replace('%TURN%', str(TURN)).replace('%TOTAL%', f'{TOTAL:.3f}'))
open(f'{W}/ehon.html', 'w').write(html)
open(f'{W}/rec.js', 'w').write(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.on('pageerror',e=>console.log('ERR',e.message));await p.goto('file://{W}/ehon.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{W}/c-'+t+'.jpg',type:'jpeg',quality:85}});}}await b.close();return}}
for(let i=0;i<30*{TOTAL:.3f};i++){{await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:'{W}/fr/'+String(i).padStart(4,'0')+'.jpg',type:'jpeg',quality:92}});}}await b.close()}})();""")
print('場面', [round(x, 2) for x in ST], '全体', round(TOTAL, 1), '声', [round(x, 2) for x in VD])
if STILL:
    subprocess.run(['node', f'{W}/rec.js', STILL], check=True); sys.exit()
subprocess.run(['node', f'{W}/rec.js'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/tools/brand/reel_bgm.m4a', '-t', f'{TOTAL + 1:.2f}', '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '48000', f'{W}/bgm.wav'], check=True)
enc = ['-c:v', 'libx264', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT]
if not (VDIR and os.path.exists(f'{VDIR}/{SP}-00.wav')):
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg', '-i', f'{W}/bgm.wav', '-map', '0:v', '-map', '1:a', '-af', f'afade=t=in:d=0.4,afade=t=out:st={TOTAL-2.2}:d=2.2', '-t', f'{TOTAL:.2f}'] + enc, check=True)
    print(OUT, '（声なし）'); sys.exit()
ins = []; flt = []
for n in range(N):
    ins += ['-i', f'{VDIR}/{SP}-{n:02d}.wav']; flt.append(f'[{n+2}:a]aresample=48000,adelay={int((ST[n]+LEAD)*1000)}:all=1[v{n}]')
flt.append(''.join(f'[v{n}]' for n in range(N)) + f'amix=inputs={N}:normalize=0:duration=longest,volume={os.environ.get("VVOL", "1.7")},asplit=2[vo][sc]')
flt.append(f'[1:a]afade=t=in:d=0.4,afade=t=out:st={TOTAL-2.2}:d=2.2[bg0]')
flt.append('[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=600:makeup=1[bg]')
flt.append('[bg][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg', '-i', f'{W}/bgm.wav'] + ins +
               ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[a]', '-t', f'{TOTAL:.2f}'] + enc, check=True)
print(OUT)
