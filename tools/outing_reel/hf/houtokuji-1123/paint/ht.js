// 11/23 群馬・宝徳寺だけの描き下ろし：床もみじ（磨いた床に紅葉がうつる）・庭のカエデ・傘の空・夜の床もみじ
const FY=700; // 窓の下の線＝床の始まり
// 窓の外の紅葉（明るい）。night は灯りで下から照らす
function outside(night){const c=cv(),x=c.getContext('2d');const LT=night?[W/2,FY+40,700]:[W*.55,140,900];
 if(night){const g=x.createLinearGradient(0,0,0,FY);g.addColorStop(0,'#0c0610');g.addColorStop(1,'#3a1208');x.fillStyle=g;x.fillRect(0,0,W,FY+10)}else{sky(x,'#fff6e2','#ffe2b0',0,FY);glow(x,LT[0],LT[1],700,.85,'255,250,232')}
 const pal=night?AKA.concat(['#ff8a3a','#ffb04a']):AKA.concat(AKA,['#e8702e','#f0a03a']);
 const op=night?{light:LT,dark:'#12020a',hi:'#ffc070'}:{light:LT};
 // 奥：やわらかい黄と緑のかすみ
 const far=cv(),fx=far.getContext('2d');for(let i=0;i<9;i++)leafCloud(fx,(i/8)*W,200+Math.sin(i*1.7)*60,150,120,900,9,night?['#3a1a14','#4a2416']:KI.concat(AO),4050+i,{light:LT});x.drawImage(layerBlur(far,5),0,0);
 // 木の後ろも紅葉で埋める（すき間の白・黒い穴をなくす。奥はやわらかく）
 const mid=cv(),mx=mid.getContext('2d');const dp=pal.map(c=>mix(c,night?'#1a0608':'#5a1a10',.45));for(let r=0;r<4;r++)for(let i=0;i<9;i++)leafCloud(mx,(i/8)*W+(r%2)*50-25,300+r*110,150,100,1100,9,dp,4070+r*10+i+(night?500:0),{});x.drawImage(layerBlur(mid,6),0,0);
 // もみじの木（幹が見えて、木と木の間から光）
 [[120,FY+30,700,-.05],[470,FY+40,760,.02],[810,FY+30,700,.08]].forEach(([bx,by,h,l],i)=>maple(x,bx,by,h,pal,4100+i*7+(night?500:0),{...op,lean:l}));
 for(let i=0;i<7;i++)leafCloud(x,(i/6)*W,FY-70+Math.sin(i*2.1)*20,150,90,1600,11,pal,4140+i+(night?500:0),op);
 if(night){x.globalCompositeOperation='lighter';glow(x,W/2,FY,520,.35,'255,170,90');x.globalCompositeOperation='source-over'}
 return c}
// 床：外の絵を上下さかさにうつす（つやのある黒い床）
function floorRef(src,night){const c=cv(),x=c.getContext('2d');x.fillStyle=night?'#050306':'#120a08';x.fillRect(0,FY,W,H-FY);
 x.save();x.globalAlpha=night?.92:.9;x.translate(0,FY*2);x.scale(1,-1);x.filter='blur(2.5px)';x.drawImage(src,0,0,W,FY,0,0,W,FY);x.restore();x.filter='none';
 // 奥ほど明るく、手前ほど暗い床のつや
 const g=x.createLinearGradient(0,FY,0,H);g.addColorStop(0,'rgba(10,4,4,0)');g.addColorStop(.6,'rgba(10,4,4,.18)');g.addColorStop(1,'rgba(6,2,2,.62)');x.fillStyle=g;x.fillRect(0,FY,W,H-FY);
 // 床板の目（細い横線）と、光の筋
 for(let i=0;i<24;i++){const y=FY+Math.pow(i/24,1.7)*(H-FY);x.fillStyle='rgba(0,0,0,.18)';x.fillRect(0,y,W,1+i*.08)}
 const q=rng(7);for(let i=0;i<5;i++){const xx=80+q()*760;const g2=x.createLinearGradient(xx-30,0,xx+30,0);g2.addColorStop(0,'rgba(255,240,220,0)');g2.addColorStop(.5,`rgba(255,240,220,${night?.05:.09})`);g2.addColorStop(1,'rgba(255,240,220,0)');x.fillStyle=g2;x.fillRect(xx-30,FY,60,H-FY)}
 return c}
// 部屋のわく：天井の梁・柱・敷居（手前の黒い額縁）
function room(night,front){const c=cv(),x=c.getContext('2d');const wood=night?'#100806':'#24140e',hi=night?'rgba(255,170,90,.25)':'rgba(255,230,190,.18)';
 if(front){x.fillStyle=wood;x.fillRect(0,0,W,96);x.fillStyle=hi;x.fillRect(0,94,W,2);
  [[0,74],[W-74,74]].forEach(([px,w])=>{x.fillStyle=wood;x.fillRect(px,0,w,H);x.fillStyle=hi;x.fillRect(px+(px?2:w-4),96,2,FY-96)});
  // 手前の床の縁（光る線）
  x.fillStyle=night?'rgba(255,170,90,.35)':'rgba(255,236,200,.45)';x.fillRect(0,FY,W,3)}
 else{[W*.36,W*.64].forEach(px=>{x.fillStyle=wood;x.fillRect(px-11,96,22,FY-96);x.fillStyle=hi;x.fillRect(px+6,96,2,FY-96)});
  x.fillStyle=wood;x.fillRect(0,96,W,26);x.fillRect(0,FY-14,W,16);
  // 床に柱がうつる
  x.globalAlpha=.55;[W*.36,W*.64].forEach(px=>{const g=x.createLinearGradient(0,FY,0,FY+520);g.addColorStop(0,wood);g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.fillRect(px-11,FY,22,520)});x.globalAlpha=1}
 return c}
function YUKA(night){const L={};const o=outside(night);
 {const c=cv(),x=c.getContext('2d');x.drawImage(o,0,0,W,FY,0,0,W,FY);x.drawImage(floorRef(o,night),0,0);L.b=finish(c,night?4301:4201,{rim:false,g:6,blot:.02})}
 L.m=finish(room(night,false),night?4302:4202,{rim:false,g:5,blot:0});
 L.n=finish(room(night,true),night?4303:4203,{rim:false,g:5,blot:0});
 {const c=cv(),x=c.getContext('2d');if(night){x.globalCompositeOperation='lighter';glow(x,W/2,FY,420,.3,'255,190,110');glow(x,W/2,FY+300,520,.18,'255,150,80')}else{const s=cv(),sx=s.getContext('2d');leafCloud(sx,W-10,40,170,110,60,40,AKA,4211);L.f=layerBlur(s,6);return L}L.f=c}
 return L}
function H0(){return YUKA(false)}
function H3(){return YUKA(true)}
// ===== H1 庭：100本をこえるカエデと枯山水 =====
function H1(){const L={};const LT=[W*.7,120,1100];
 {const c=cv(),x=c.getContext('2d');sky(x,'#d8ecf4','#fff0d8',0,500);glow(x,LT[0],LT[1],600,.7,'255,250,232');
  for(let r=0;r<3;r++)for(let i=0;i<8;i++)leafCloud(x,(i/7)*W+(r%2)*50-25,240+r*120+Math.sin(i+r)*40,160,130,2000,10+r,AKA.concat(KI,AKA),4400+r*10+i,{light:LT});
  L.b=finish(c,4401,{rim:false,g:6,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 白い砂の庭（波の線）と石
  x.fillStyle='#ece4d4';x.fillRect(0,760,W,H-760);
  x.strokeStyle='rgba(150,130,110,.45)';x.lineWidth=2;for(let i=0;i<34;i++){const y=770+i*20+i*i*.3;x.beginPath();for(let xx=0;xx<=W;xx+=10)x.lineTo(xx,y+Math.sin(xx*.012+i*.3)*4);x.stroke()}
  [[260,980,90,46],[640,900,60,32],[720,1180,120,58]].forEach(([sx,sy,rx,ry])=>{x.strokeStyle='rgba(150,130,110,.45)';for(let k=1;k<5;k++){x.beginPath();x.ellipse(sx,sy+ry*.4,rx+k*18,ry+k*10,0,0,7);x.stroke()}
   const g=x.createRadialGradient(sx-rx*.3,sy-ry*.4,4,sx,sy,rx);g.addColorStop(0,'#8a8478');g.addColorStop(1,'#4a463e');x.fillStyle=g;x.beginPath();x.ellipse(sx,sy,rx,ry,0,0,7);x.fill()});
  const q=rng(4410);for(let i=0;i<180;i++)leaf(x,q()*W,780+q()*640,4+q()*8,q()*6,AKA[i%AKA.length],7);
  // 手前のカエデ（左右から）
  maple(x,90,860,560,AKA.concat(AKA,KI),4420,{light:LT});maple(x,W-60,840,600,AKA.concat(KI),4421,{light:LT,lean:-.1});
  for(let i=0;i<9;i++)leafCloud(x,(i/8)*W,790+Math.sin(i*1.9)*14,90,46,700,8,i%3?AKA:KI,4440+i,{light:LT});
  L.m=finish(c,4402,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 本堂の軒（上から）
  x.fillStyle='#4a3428';x.beginPath();x.moveTo(-20,0);x.lineTo(W*.62,0);x.quadraticCurveTo(W*.4,120,-20,150);x.fill();x.strokeStyle='rgba(20,10,6,.5)';x.lineWidth=3;for(let k=1;k<9;k++){const t=k/9;x.beginPath();x.moveTo(-20+t*(W*.62+20)*.0,150*(1-t));x.quadraticCurveTo(W*.4*t,120*(1-t)+0,W*.62*t,0);x.stroke()}x.fillStyle='rgba(255,236,200,.4)';x.beginPath();x.moveTo(-20,150);x.quadraticCurveTo(W*.4,120,W*.62,0);x.lineTo(W*.62,6);x.quadraticCurveTo(W*.4,128,-20,158);x.fill();
  L.n=finish(c,4403,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,40,H-60,220,140,50,46,AKA,4431);L.f=layerBlur(s,7)}
 return L}
// ===== H2 傘の空：紅葉の上に色とりどりの傘 =====
function umbrella(x,cx,cy,r,col,tilt){x.save();x.translate(cx,cy);x.rotate(tilt);x.scale(1,.42);
 const n=8;for(let i=0;i<n;i++){const a0=i/n*Math.PI*2,a1=(i+1)/n*Math.PI*2;x.fillStyle=i%2?col:mix(col,'#ffffff',.18);x.beginPath();x.moveTo(0,0);x.lineTo(Math.cos(a0)*r,Math.sin(a0)*r);x.quadraticCurveTo(Math.cos((a0+a1)/2)*r*.9,Math.sin((a0+a1)/2)*r*.9,Math.cos(a1)*r,Math.sin(a1)*r);x.closePath();x.fill()}
 x.restore();x.fillStyle='rgba(40,30,20,.6)';x.fillRect(cx-1.5,cy-r*.9,3,r*.9)}
function H2(){const L={};const LT=[W/2,80,1000];
 {const c=cv(),x=c.getContext('2d');sky(x,'#cfe6f2','#fff3dc',0,H);glow(x,LT[0],LT[1],700,.8,'255,250,235');L.b=finish(c,4501,{rim:false,g:5,blot:.02})}
 {const c=cv(),x=c.getContext('2d');
  // 両側の紅葉と、まん中の石の道
  {const g=x.createLinearGradient(0,820,0,H);g.addColorStop(0,'#d8c8a8');g.addColorStop(1,'#9a8466');x.fillStyle=g;x.beginPath();x.moveTo(W*.42,820);x.lineTo(W*.58,820);x.lineTo(W*.8,H);x.lineTo(W*.2,H);x.fill();const q=rng(4515);for(let i=0;i<260;i++){const t=Math.pow(q(),1.3),y=820+t*(H-820),w=W*.16+t*W*.44;leaf(x,W/2-w/2+q()*w,y,3+t*9,q()*6,AKA[i%AKA.length],7)}}
  for(let s of[-1,1])for(let i=0;i<5;i++){const k=i/4;leafCloud(x,W/2+s*(160+k*260),700+k*420,120+k*140,170+k*160,2600,10+k*5,AKA.concat(KI,AKA),4510+i+(s>0?20:0),{light:LT})}
  L.m=finish(c,4502,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 傘：道の上の空に、奥は小さく手前は大きく
  const cols=['#f06a8a','#f7c548','#5ab4e6','#8bd17c','#c48ae8','#ff9a4a','#f2f0ea','#e84a4a'];const q=rng(4520);
  x.strokeStyle='rgba(60,40,30,.35)';x.lineWidth=1.2;for(let k=0;k<5;k++){x.beginPath();x.moveTo(0,120+k*110);x.quadraticCurveTo(W/2,180+k*110,W,120+k*110);x.stroke()}
  for(let k=0;k<5;k++){const n=4+k*1.2;for(let i=0;i<n;i++){const xx=(i+.5)/n*W+(q()-.5)*40,yy=150+k*110+Math.sin(xx/W*Math.PI)*60*(k/5)+q()*20;umbrella(x,xx,yy,26+k*16,cols[Math.floor(q()*cols.length)],(q()-.5)*.25)}}
  L.n=finish(c,4503,{rim:false,g:4,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,W-40,H-60,220,140,50,46,AKA,4531);leafCloud(sx,30,H-30,180,120,40,46,KI,4532);L.f=layerBlur(s,7)}
 return L}
window.SCN=Object.assign(window.SCN||{},{H0,H1,H2,H3});
