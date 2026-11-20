// 鶏足寺の4場面。各場面＝層（b＝ページに描く奥、m・n・f＝起き上がる切り紙）
const VX=468,VY=600;
function steps(x,seed,{y0=H,y1=VY+20,w0=760,w1=70,n=26,carpet=1,cx=VX}={}){const r=rng(seed);
 // 段の位置：手前ほど間が広い
 const ys=[];for(let i=0;i<=n;i++){const k=i/n;ys.push(y1+(y0-y1)*Math.pow(k,1.9))}
 const wAt=y=>w1+(w0-w1)*((y-y1)/(y0-y1));
 for(let i=0;i<n;i++){const ya=ys[i],yb=ys[i+1],wa=wAt(ya),wb=wAt(yb);const rise=(yb-ya)*.32;
  // 踏み面
  x.fillStyle=mix('#9a9282','#6e675a',r()*.5);x.beginPath();x.moveTo(cx-wa/2,ya);x.lineTo(cx+wa/2,ya);x.lineTo(cx+wb/2,yb-rise);x.lineTo(cx-wb/2,yb-rise);x.closePath();x.fill();
  // 蹴上げ（影）
  x.fillStyle=mix('#4e483e','#3a342c',r());x.beginPath();x.moveTo(cx-wb/2,yb-rise);x.lineTo(cx+wb/2,yb-rise);x.lineTo(cx+wb/2,yb);x.lineTo(cx-wb/2,yb);x.closePath();x.fill();
  // 石の継ぎ目
  x.strokeStyle=rgba('#2a2620',.5);x.lineWidth=1;const k=Math.floor(2+r()*3);for(let j=1;j<k;j++){const u=j/k+(r()-.5)*.08;x.beginPath();x.moveTo(cx-wb/2+wb*u,yb-rise);x.lineTo(cx-wb/2+wb*u,yb);x.stroke()}
  // 散り紅葉のじゅうたん（端ほど厚い・手前ほど大きい）
  const s=2+((ya-y1)/(y0-y1))*11;const cnt=Math.floor((wb/s)*(yb-ya)/s*.9*carpet);
  for(let j=0;j<cnt;j++){const v=r(),yy=ya+(yb-rise-ya)*v,ww=wa+(wb-wa)*v;let u=r();if(r()<.4)u=r()<.5?u*.25:1-u*.25;
   leaf(x,cx-ww/2+ww*u,yy,s*(.7+r()*.6),r()*6,mix(AKA[Math.floor(r()*AKA.length)],r()<.3?'#f6b04a':'#5a1410',r()*.35),r()<.5?7:5)}
  // 段の縁に落ちた葉
  for(let j=0;j<cnt*.15;j++){const u=r();leaf(x,cx-wb/2+wb*u,yb-rise+(r()-.3)*rise,s*.8,r()*6,AKA[Math.floor(r()*AKA.length)])}}
 return ys}
function S0(){const L={};const R=rng(11);
 // b：奥（光る参道の先・遠い木々・石段）
 {const c=cv(),x=c.getContext('2d');sky(x,'#f7dca0','#e9b878',0,H);
  // 光の芯
  const g=x.createRadialGradient(VX,VY-40,0,VX,VY-40,520);g.addColorStop(0,'rgba(255,246,214,1)');g.addColorStop(.35,'rgba(255,214,150,.6)');g.addColorStop(1,'rgba(255,200,130,0)');x.fillStyle=g;x.fillRect(0,0,W,H);
  // 遠いもみじの霞
  for(let k=0;k<3;k++)canopy(x,VX+(k-1)*260,VY-170+k*20,300,180,AKA.map(c=>mix(c,'#f4cf96',.45-k*.1)),40+k,500,[.5,.2],[5,9]);
  canopy(x,130,VY-60,240,260,AKA.map(c=>mix(c,'#e8b080',.35)),47,700,[.8,.2],[6,11]);canopy(x,820,VY-60,240,260,AKA.map(c=>mix(c,'#e8b080',.35)),48,700,[.3,.2],[6,11]);
  // 地面：遠くは光にとける・手前は苔と落ち葉の森の土
  {const g=x.createLinearGradient(0,VY-20,0,H);g.addColorStop(0,'rgba(214,170,110,0)');g.addColorStop(.06,'#b88a58');g.addColorStop(.3,'#6a5236');g.addColorStop(1,'#3a3020');x.fillStyle=g;x.fillRect(0,VY-20,W,H-VY+20)}
  const r=rng(5);for(let i=0;i<200;i++){const y=VY+Math.pow(r(),.7)*(H-VY);x.fillStyle=rgba(AO[i%4],.35);x.beginPath();x.ellipse(r()*W,y,20+r()*60,6+r()*14,0,0,7);x.fill()}
  for(let i=0;i<3200;i++){const y=VY+10+Math.pow(r(),.8)*(H-VY);const s=1.5+(y-VY)/(H-VY)*11;leaf(x,r()*W,y,s,r()*6,r()<.15?mix(KI[i%4],'#6a5a20',.3):mix(AKA[i%AKA.length],'#3a1008',r()*.4))}
  steps(x,7,{w0:640,n:20,carpet:1.7});
  rays(x,VX+60,VY-120,9,9,'#fff0c8',.09);
  // 木もれ日
  {const q=rng(91);x.save();x.globalCompositeOperation='soft-light';for(let i=0;i<70;i++){const y=VY+40+Math.pow(q(),.9)*(H-VY-40),k=(y-VY)/(H-VY);x.fillStyle='rgba(255,236,180,.55)';x.beginPath();x.ellipse(VX+(q()-.5)*(80+k*600),y,6+k*40,2+k*10,0,0,7);x.fill()}x.restore()}
  L.b=finish(c,101,{rim:false,blot:.05})}
 // m：中ほどの古木の列と、上をおおう紅葉（起き上がる）
 {const c=cv(),x=c.getContext('2d');
  const tr=[[352,VY+70,14,-1],[588,VY+70,14,1],[250,VY+190,26,-1],[690,VY+190,26,1]];
  tr.forEach(([tx,ty,w,sd],i)=>{trunk(x,[[tx,ty],[tx-sd*10,ty-90],[tx+sd*6,ty-200],[tx-sd*28,ty-330],[tx-sd*70,ty-430]],w,w*.5,'#4a3426',20+i);
   trunk(x,[[tx-sd*2,ty-180],[tx+sd*30,ty-250],[tx+sd*60,ty-310],[tx+sd*110,ty-340]],w*.4,w*.12,'#4a3426',30+i)});
  canopy(x,VX,330,560,230,AKA,61,4200,[.62,.2],[6,12],(u,v)=>v<.75-Math.abs(u)*.2+Math.sin(u*9)*.08&&v>-1+Math.abs(u)*.15);
  canopy(x,120,520,180,170,AKA,62,1100,[.8,.2],[6,12]);canopy(x,810,520,180,170,AKA,63,1100,[.3,.2],[6,12]);
  L.m=finish(c,102)}
 // n：手前の苔むした石垣と、大きな古木（左右）
 {const c=cv(),x=c.getContext('2d');
  // 参道の両わきの低い石垣：参道の縁から立ち上がる面（手前ほど高い）・その外は苔の土手
  const PL=VX-320,PR=VX+320;
  for(const sd of[-1,1]){const ex=sd<0?-80:W+80;x.fillStyle='#55602c';x.beginPath();x.moveTo(VX+sd*36,VY+14);x.lineTo(VX+sd*120,VY+4);x.lineTo(ex,H-380);x.lineTo(ex,H);x.lineTo(VX+sd*320+sd*-40,H-250);x.closePath();x.fill();
   const g=x.createLinearGradient(0,VY,0,H);g.addColorStop(0,'rgba(240,200,140,.5)');g.addColorStop(.4,'rgba(0,0,0,0)');x.fillStyle=g;x.fill();
   x.save();x.clip();const q=rng(sd>0?81:82);for(let i=0;i<900;i++){const y=VY+Math.pow(q(),.8)*(H-VY),k=(y-VY)/(H-VY);x.fillStyle=rgba(['#3e4a1e','#6a7a32','#7e8c3a','#2e3a16','#8a9a42'][i%5],.5);x.beginPath();x.ellipse(q()*W,y,4+k*26,2+k*9,0,0,7);x.fill()}x.restore()}
  ishigaki(x,[[VX-34,VY+24],[VX-36,VY+14],[PL-40,H-250],[PL-10,H]],31,24,16,'#8a8270',.6);
  ishigaki(x,[[VX+34,VY+24],[VX+36,VY+14],[PR+40,H-250],[PR+10,H]],32,24,16,'#8a8270',.6);
  // 石垣の上の苔と落ち葉
  const r=rng(33);for(let i=0;i<2400;i++){const k=Math.pow(r(),1.2),side=i%2;const ex=side?W+80:-80;const ax=VX+(side?36:-36),ay=VY+14,bx=ex,by=H-380+k*0;const t=r();const px=ax+(VX+(side?280:-280)-ax)*k+(ex-ax)*t*k*.9,py=ay+(H-250-ay)*k-t*k*120;leaf(x,px,py,2+k*10,r()*6,r()<.45?mix(AO[i%4],'#2a3410',r()*.4):AKA[i%9])}
  trunk(x,[[40,H-300],[60,H-560],[30,H-800],[80,H-1040],[170,H-1250]],92,40,'#3e2a1e',41);
  trunk(x,[[W-40,H-300],[W-70,H-600],[W-40,H-860],[W-110,H-1100],[W-200,H-1290]],96,42,'#3e2a1e',42);
  L.n=finish(c,103)}
 // f：手前にかかる枝の紅葉と、足もとの落ち葉の山
 {const c=cv(),x=c.getContext('2d');
  canopy(x,90,170,260,170,AKA,71,2200,[.9,.2],[8,15],(u,v)=>u*u*.8+v*v<1);
  canopy(x,W-80,120,280,160,AKA.concat(KI.slice(0,2)),72,2200,[.2,.2],[8,15]);
  const r=rng(74);for(let i=0;i<900;i++){const u=r(),y=H-Math.pow(r(),2)*120;leaf(x,u*W,y,14+r()*12,r()*6,mix(AKA[i%9],'#ffd9a0',r()*.2))}
  L.f=finish(c,104)}
 return L}
window.SCN={S0};
// ===== S1 行き方：里山の道とバス停「古橋」（朝） =====
function S1(){const L={};const HZ=700;
 {const c=cv(),x=c.getContext('2d');sky(x,'#bcd3df','#f3e6cc',0,HZ+40);
  // 薄い雲
  const q=rng(3);for(let i=0;i<9;i++){const cx=q()*W,cy=120+q()*360;x.fillStyle='rgba(255,255,255,.45)';x.beginPath();x.ellipse(cx,cy,90+q()*120,14+q()*10,0,0,7);x.fill()}
  // 遠い山なみ（3重）
  const ridge=(y,amp,col,seed,spk)=>{const r=rng(seed);x.fillStyle=col;x.beginPath();x.moveTo(0,H);let px=0,py=y;x.lineTo(0,y);for(let X=0;X<=W;X+=18){const yy=y-amp*(.5+.5*Math.sin(X/160+seed))-amp*.4*Math.sin(X/57+seed*2)-r()*6;x.lineTo(X,yy)}x.lineTo(W,H);x.closePath();x.fill();
   if(spk){x.save();x.clip();for(let i=0;i<spk;i++){x.fillStyle=rgba([AKA[i%9],KI[i%4],AO[i%4]][i%3],.5);x.beginPath();x.arc(r()*W,y-amp*.6+r()*(amp*1.6+120),2+r()*4,0,7);x.fill()}x.restore()}};
  ridge(560,130,'#9fb0bd',2,0);ridge(620,110,'#8a9a8a',5,900);ridge(680,70,'#7a7a52',9,1800);
  // 田んぼ（刈り取りのあと）とあぜ
  {const g=x.createLinearGradient(0,HZ,0,H);g.addColorStop(0,'#c8a868');g.addColorStop(1,'#9a7a44');x.fillStyle=g;x.fillRect(0,HZ-20,W,H-HZ+20)}
  const r=rng(12);for(let i=0;i<14;i++){const y=HZ-10+Math.pow(i/14,1.8)*(H-HZ);x.strokeStyle=rgba('#6a5a2a',.55);x.lineWidth=1+i*.35;x.beginPath();x.moveTo(0,y);x.lineTo(W,y+(r()-.5)*10);x.stroke()}
  for(let i=0;i<2600;i++){const y=HZ+Math.pow(r(),1.4)*(H-HZ),k=(y-HZ)/(H-HZ);x.strokeStyle=rgba(r()<.5?'#e8cc88':'#7a6430',.6);x.lineWidth=1;const xx=r()*W;x.beginPath();x.moveTo(xx,y);x.lineTo(xx+(r()-.5)*2,y-2-k*9);x.stroke()}
  // 道：手前から山の方へ
  x.fillStyle='#8a8478';x.beginPath();x.moveTo(380,H);x.bezierCurveTo(470,1150,560,900,470,HZ-8);x.lineTo(452,HZ-8);x.bezierCurveTo(500,900,320,1150,120,H);x.closePath();x.fill();
  x.strokeStyle='rgba(255,255,255,.7)';x.lineWidth=3;x.setLineDash([26,22]);x.beginPath();x.moveTo(250,H);x.bezierCurveTo(400,1150,520,900,461,HZ-8);x.stroke();x.setLineDash([]);
  L.b=finish(c,201,{rim:false,blot:.05})}
 // m：中ほどの林と集落（瓦屋根）
 {const c=cv(),x=c.getContext('2d');const MIX=AKA.slice(0,4).concat(KI,AO.slice(0,2));
  for(let i=0;i<9;i++)canopy(x,40+i*110,690+(i%2)*14,80,60,i%3==1?AO.concat(KI.slice(0,1)):MIX,300+i,500,[.4,.2],[4,8]);
  const house=(hx,hy,w,h,seed)=>{// 入母屋の瓦屋根の農家
   x.fillStyle='#efe6d0';x.fillRect(hx,hy,w,h);x.fillStyle='#6a4a34';x.fillRect(hx,hy+h*.55,w,h*.45);x.fillStyle='#3a2a20';for(let k=0;k<4;k++)x.fillRect(hx+w*(.08+k*.24),hy+h*.2,w*.1,h*.3);
   const rt=hy-h*.9;x.fillStyle='#4a4e58';x.beginPath();x.moveTo(hx-w*.16,hy+4);x.lineTo(hx+w*.08,rt+h*.35);x.lineTo(hx+w*.92,rt+h*.35);x.lineTo(hx+w*1.16,hy+4);x.closePath();x.fill();
   x.fillStyle='#5a5e68';x.beginPath();x.moveTo(hx+w*.08,rt+h*.35);x.lineTo(hx+w*.22,rt);x.lineTo(hx+w*.78,rt);x.lineTo(hx+w*.92,rt+h*.35);x.closePath();x.fill();
   x.fillStyle='#2e3038';x.fillRect(hx+w*.18,rt-5,w*.64,7);x.strokeStyle='rgba(255,255,255,.18)';x.lineWidth=1;for(let k=1;k<5;k++){const yy=hy+4-(hy+4-rt-h*.35)*k/5;x.beginPath();x.moveTo(hx-w*.16+w*.24*k/5,yy);x.lineTo(hx+w*1.16-w*.24*k/5,yy);x.stroke()}};
  house(560,744,90,44,3);house(800,736,104,52,2);house(650,718,150,70,1);
  canopy(x,880,690,70,70,AKA,331,500,[.3,.2],[5,9]);
  L.m=finish(c,202)}
 // n：柿の木と、バス停「古橋」
 {const c=cv(),x=c.getContext('2d');
  trunk(x,[[150,1240],[140,1100],[170,980],[130,880]],36,16,'#4a3628',51);trunk(x,[[150,1060],[230,990],[300,960]],16,6,'#4a3628',52);
  canopy(x,170,860,170,130,['#5a7a2a','#7a8a32','#a89a3a','#c8a040'],53,1100,[.6,.2],[6,11]);
  const q=rng(54);for(let i=0;i<34;i++){const a=q()*7,rr=q();const fx=170+Math.cos(a)*150*rr,fy=870+Math.sin(a)*110*rr;x.fillStyle='#e8701c';x.beginPath();x.arc(fx,fy,9,0,7);x.fill();x.fillStyle='rgba(255,220,160,.8)';x.beginPath();x.arc(fx-3,fy-3,3,0,7);x.fill()}
  // バス停：丸い看板の標柱と小さな屋根
    x.fillStyle='#7a7a7a';x.fillRect(616,960,10,240);x.fillStyle='#f8f4ea';x.beginPath();x.arc(621,940,52,0,7);x.fill();x.strokeStyle='#2a6a9a';x.lineWidth=8;x.stroke();
  x.fillStyle='#2a6a9a';x.font='700 30px MB';x.textAlign='center';x.fillText('古橋',621,952);
  L.n=finish(c,203)}
 // f：手前のすすき
 {const c=cv(),x=c.getContext('2d');const q=rng(61);
  for(let i=0;i<70;i++){const bx=(i<35?q()*260:W-q()*260),by=H+10,hh=220+q()*260,lean=(q()-.5)*90+(i<35?30:-30);x.strokeStyle=mix('#a89a6a','#5a5a2a',q());x.lineWidth=2+q()*2;x.beginPath();x.moveTo(bx,by);x.quadraticCurveTo(bx+lean*.3,by-hh*.6,bx+lean,by-hh);x.stroke();
   if(q()<.6){x.fillStyle=rgba('#f4ead0',.85);for(let k=0;k<14;k++){x.beginPath();x.ellipse(bx+lean+(q()-.5)*14+k*lean*.012,by-hh+k*5,3,9,lean/200,0,7);x.fill()}}}
  L.f=finish(c,204)}
 // バス（前から見た形・行き先の字は入れない）
 {const c=cv(240,220),x=c.getContext('2d');x.fillStyle='#f4f2ea';x.beginPath();x.roundRect(10,20,220,180,18);x.fill();x.fillStyle='#2a6a9a';x.fillRect(10,150,220,16);
  x.fillStyle='#2a3440';x.beginPath();x.roundRect(26,40,188,80,8);x.fill();x.fillStyle='rgba(255,255,255,.25)';x.beginPath();x.moveTo(40,44);x.lineTo(90,44);x.lineTo(60,116);x.lineTo(30,116);x.fill();
  x.fillStyle='#1a1a1a';x.fillRect(66,24,108,14);x.fillStyle='#ffe9a8';x.beginPath();x.arc(42,176,11,0,7);x.arc(198,176,11,0,7);x.fill();x.fillStyle='#222';x.fillRect(20,196,40,18);x.fillRect(180,196,40,18);
  L.bus=finish(c,205,{g:8})}
 return L}
// ===== S2 大門跡から見上げる参道（もみじのトンネル・二人が歩く） =====
function S2(){const L={};const vx=470,vy=520;
 {const c=cv(),x=c.getContext('2d');sky(x,'#fbe6b4','#e2b070',0,H);
  const g=x.createRadialGradient(vx,vy-30,0,vx,vy-30,600);g.addColorStop(0,'rgba(255,250,224,1)');g.addColorStop(.4,'rgba(255,220,160,.5)');g.addColorStop(1,'rgba(255,200,130,0)');x.fillStyle=g;x.fillRect(0,0,W,H);
  for(let k=0;k<4;k++)canopy(x,vx+(k-1.5)*200,vy-120,200,120,AKA.concat(KI).map(c=>mix(c,'#f8d8a0',.5)),500+k,400,[.5,.2],[4,7]);
  // 地面
  {const g2=x.createLinearGradient(0,vy,0,H);g2.addColorStop(0,'#c89a60');g2.addColorStop(.25,'#7a5a34');g2.addColorStop(1,'#4a3a22');x.fillStyle=g2;x.fillRect(0,vy-6,W,H-vy+6)}
  const r=rng(15);for(let i=0;i<3000;i++){const y=vy+Math.pow(r(),.85)*(H-vy);const s=1.2+(y-vy)/(H-vy)*9;leaf(x,r()*W,y,s,r()*6,r()<.2?mix(AO[i%4],'#3a4a1a',.2):r()<.3?KI[i%4]:AKA[i%9])}
  // ゆるやかな参道（長い・細い段）
  steps(x,17,{y0:H-150,y1:vy+8,w0:420,w1:30,n:30,carpet:1.5,cx:vx});
  rays(x,vx,vy-80,12,19,'#fff4d0',.12);
  L.b=finish(c,301,{rim:false,blot:.05})}
 // m：参道の両側に並ぶ古木（奥へ小さく）
 {const c=cv(),x=c.getContext('2d');
  for(let i=5;i>=0;i--){const k=Math.pow(i/5,1.5);for(const sd of[-1,1]){const tx=vx+sd*(40+k*400),ty=vy+30+k*(H-260-vy),w=6+k*44,h=(ty-200)*1.0;
   trunk(x,[[tx,ty],[tx+sd*w*.15,ty-h*.3],[tx-sd*w*.1,ty-h*.6],[tx-sd*w*.6,ty-h*.85],[tx-sd*w*1.6,ty-h]],w,w*.4,mix('#4a3426','#b08a68',(1-k)*.55),700+i*2+(sd>0));
   }}
  canopy(x,vx,250,640,300,AKA.concat(['#f08a2c','#e8a42c']),710,5200,[.6,.2],[6,12],(u,v)=>v<.8-Math.abs(u)*.15+Math.sin(u*7)*.07&&v>-1.2);
  L.m=finish(c,302)}
 // n：大門跡（礎石と低い石段）
 {const c=cv(),x=c.getContext('2d');const r=rng(71);
  for(const sd of[-1,1]){const bx=vx+sd*330,by=H-110;// 大門の礎石（平たい石）
   x.fillStyle='#6a6458';x.beginPath();x.moveTo(bx-90,by);x.lineTo(bx+90,by);x.lineTo(bx+100,by+46);x.lineTo(bx-100,by+46);x.closePath();x.fill();
   x.fillStyle='#a49e8e';x.beginPath();x.moveTo(bx-70,by-26);x.lineTo(bx+74,by-24);x.lineTo(bx+90,by);x.lineTo(bx-90,by);x.closePath();x.fill();
   x.fillStyle='rgba(110,130,50,.85)';for(let i=0;i<18;i++){x.beginPath();x.ellipse(bx+(r()-.5)*150,by-12+(r()-.5)*20,6+r()*10,3+r()*3,0,0,7);x.fill()}
   for(let i=0;i<26;i++)leaf(x,bx+(r()-.5)*170,by-16+(r()-.5)*24,8+r()*6,r()*6,AKA[i%9])}
  x.fillStyle='#857e6e';x.fillRect(vx-240,H-70,480,30);x.fillStyle='#5a5448';x.fillRect(vx-240,H-40,480,40);for(let i=0;i<120;i++)leaf(x,vx-240+r()*480,H-72+r()*30,8+r()*7,r()*6,AKA[i%9]);
  L.n=finish(c,303)}
 // f：手前に垂れる枝
 {const c=cv(),x=c.getContext('2d');
  canopy(x,40,80,260,190,AKA,801,2000,[.9,.2],[8,14],(u,v)=>u*u*.7+v*v<1);canopy(x,W-30,40,240,170,AKA.concat(KI.slice(0,2)),802,1900,[.2,.2],[8,14]);
  L.f=finish(c,304)}
 // 二人（うしろ姿）
 {const c=cv(120,170),x=c.getContext('2d');const p=(px,s,coat,hat)=>{x.fillStyle=coat;x.beginPath();x.moveTo(px-14*s,150);x.lineTo(px-17*s,70*s+40);x.quadraticCurveTo(px,55*s+20,px+17*s,70*s+40);x.lineTo(px+14*s,150);x.closePath();x.fill();x.fillStyle='#2a2420';x.fillRect(px-11*s,150,8*s,16);x.fillRect(px+3*s,150,8*s,16);
   x.fillStyle='#3a2a20';x.beginPath();x.arc(px,40+(1-s)*30,13*s,0,7);x.fill();if(hat){x.fillStyle=hat;x.beginPath();x.ellipse(px,32+(1-s)*30,16*s,6*s,0,0,7);x.fill()}};
  p(40,1,'#5a6a7a','#c8b080');p(84,.85,'#b84a3a');L.ppl=finish(c,305,{g:6})}
 return L}
// ===== S3 色づく古木と苔の石垣（朝の光） =====
function S3(){const L={};const HZ=860;
 {const c=cv(),x=c.getContext('2d');sky(x,'#f6e2b8','#eac690',0,HZ);
  const g=x.createRadialGradient(170,240,0,170,240,700);g.addColorStop(0,'rgba(255,250,226,1)');g.addColorStop(.3,'rgba(255,232,180,.6)');g.addColorStop(1,'rgba(255,220,160,0)');x.fillStyle=g;x.fillRect(0,0,W,H);
  for(let k=0;k<5;k++)canopy(x,k*230,HZ-150,200,150,AO.concat(KI).map(c=>mix(c,'#f2dcb0',.5)),900+k,400,[.3,.2],[4,7]);
  {const g2=x.createLinearGradient(0,HZ-40,0,H);g2.addColorStop(0,'#7a8a3a');g2.addColorStop(1,'#3e4a1e');x.fillStyle=g2;x.fillRect(0,HZ-40,W,H)}
  const r=rng(21);for(let i=0;i<1400;i++){const y=HZ-30+Math.pow(r(),.9)*(H-HZ+30),k=(y-HZ)/(H-HZ);x.fillStyle=rgba(['#3e4a1e','#6a7a32','#8a9a42','#2e3a16'][i%4],.55);x.beginPath();x.ellipse(r()*W,y,4+k*20,2+k*7,0,0,7);x.fill()}
  for(let i=0;i<500;i++){const y=HZ+Math.pow(r(),.9)*(H-HZ);leaf(x,r()*W,y,3+(y-HZ)/(H-HZ)*9,r()*6,AKA[i%9])}
  rays(x,150,200,10,23,'#fff6d8',.07);
  L.b=finish(c,401,{rim:false,blot:.05})}
 // 苔の石垣（横に長い）
 {const c=cv(),x=c.getContext('2d');ishigaki(x,[[0,HZ+40],[W,HZ+10],[W,HZ+250],[0,HZ+300]],411,48,30,'#8a8270',.75);
  x.fillStyle='#5a6a2a';x.beginPath();x.moveTo(0,HZ+50);x.quadraticCurveTo(W/2,HZ-10,W,HZ+20);x.lineTo(W,HZ+6);x.quadraticCurveTo(W/2,HZ-40,0,HZ+30);x.fill();
  L.n=finish(c,402)}
 // 古木（色づき始め／見頃）：同じ形で色だけ違う2枚
 const tree=(pal,seed,lite)=>{const c=cv(),x=c.getContext('2d');
  const sh=(u,v)=>((u*u*1.0+v*v*2.2)<1)||(((u+.45)**2)*2.6+((v-.25)**2)*5<1)||(((u-.5)**2)*2.6+((v-.2)**2)*5<1)||(((u)**2)*3+((v+.35)**2)*4<1);
  canopy(x,500,HZ-520,450,230,pal,seed,6200,[.25,.2],[7,13],sh);
  // 太い幹が三つの枝に分かれて、茂みを支える
  trunk(x,[[520,HZ+70],[500,HZ-40],[530,HZ-150],[505,HZ-250]],120,70,'#3e2a1e',601);
  trunk(x,[[505,HZ-230],[430,HZ-320],[330,HZ-390],[200,HZ-430]],46,14,'#3e2a1e',602);
  trunk(x,[[520,HZ-240],[600,HZ-330],[710,HZ-400],[820,HZ-430]],44,14,'#3e2a1e',603);
  trunk(x,[[505,HZ-250],[510,HZ-360],[490,HZ-460]],40,14,'#3e2a1e',604);
  // 枝の上にかかる葉（幹が茂みの中へ消える）
  canopy(x,500,HZ-450,380,90,pal,seed+5,1500,[.25,.2],[7,12],(u,v)=>u*u+v*v*3<1&&v<.3);
  return finish(c,610)};
 L.m0=tree(AO.concat(KI,['#e8702e']),620);L.m1=tree(AKA,620);
 // f：手前の苔と落ち葉の土手
 {const c=cv(),x=c.getContext('2d');const r=rng(31);x.fillStyle='#4a5a22';x.beginPath();x.moveTo(0,H);x.lineTo(0,H-120);x.quadraticCurveTo(300,H-170,560,H-110);x.quadraticCurveTo(760,H-70,W,H-130);x.lineTo(W,H);x.fill();
  for(let i=0;i<400;i++){const xx=r()*W,y=H-r()*120;x.fillStyle=rgba(['#6a7a32','#8a9a42','#3e4a1e'][i%3],.8);x.beginPath();x.ellipse(xx,y,8+r()*16,4+r()*6,0,0,7);x.fill()}
  for(let i=0;i<260;i++)leaf(x,r()*W,H-r()*110,10+r()*8,r()*6,AKA[i%9]);
  L.f=finish(c,404)}
 return L}
window.SCN={S0,S1,S2,S3};
