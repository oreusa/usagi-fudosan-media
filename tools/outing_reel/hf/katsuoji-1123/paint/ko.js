// 11/23 勝尾寺（箕面）だけの描き下ろし：紅葉の中にぎっしりの勝ちダルマ／紅葉のトンネルの参道／夜の宵詣り
// だるま：赤い胴・白い顔・太い眉とひげ・金の「勝」
function daruma(x,cx,cy,s,o={}){const night=!!o.night;const lit=o.lit??1;x.save();x.translate(cx,cy);x.rotate(o.rot||0);
 // 影
 x.fillStyle='rgba(20,6,4,.35)';x.beginPath();x.ellipse(s*.05,s*.98,s*.8,s*.16,0,0,7);x.fill();
 // 胴
 const g=x.createRadialGradient(-s*.3,-s*.35,s*.1,0,0,s*1.15);const R=o.col||'#c8161c';
 g.addColorStop(0,mix(R,'#ff9a7a',.45*lit));g.addColorStop(.55,R);g.addColorStop(1,mix(R,'#2a0204',.6));
 x.fillStyle=g;x.beginPath();x.moveTo(0,-s);x.bezierCurveTo(s*.72,-s,s*.95,-s*.2,s*.9,s*.4);x.bezierCurveTo(s*.85,s*.95,-s*.85,s*.95,-s*.9,s*.4);x.bezierCurveTo(-s*.95,-s*.2,-s*.72,-s,0,-s);x.fill();
 // 顔
 x.fillStyle=night?'#f3dcc0':'#f8efe2';x.beginPath();x.ellipse(0,-s*.28,s*.5,s*.4,0,0,7);x.fill();
 x.strokeStyle='rgba(90,40,20,.25)';x.lineWidth=s*.03;x.stroke();
 // 目（両目が入った勝ちダルマ）
 for(const sd of[-1,1]){x.fillStyle='#fff';x.beginPath();x.arc(sd*s*.2,-s*.3,s*.12,0,7);x.fill();x.fillStyle='#141010';x.beginPath();x.arc(sd*s*.2,-s*.29,s*.075,0,7);x.fill();
  x.fillStyle='#fff';x.beginPath();x.arc(sd*s*.2-s*.025,-s*.32,s*.02,0,7);x.fill();
  // 眉（筆の太い線）
  x.strokeStyle='#141010';x.lineCap='round';x.lineWidth=s*.07;x.beginPath();x.moveTo(sd*s*.08,-s*.5);x.quadraticCurveTo(sd*s*.22,-s*.6,sd*s*.36,-s*.48);x.stroke()}
 // ひげ
 x.lineWidth=s*.045;x.beginPath();x.moveTo(-s*.25,-s*.08);x.quadraticCurveTo(-s*.12,-s*.18,0,-s*.12);x.quadraticCurveTo(s*.12,-s*.18,s*.25,-s*.08);x.stroke();
 x.lineWidth=s*.03;for(const sd of[-1,1]){x.beginPath();x.moveTo(sd*s*.1,-s*.04);x.lineTo(sd*s*.16,s*.02);x.stroke()}
 // 金の模様と「勝」
 x.strokeStyle=night?'rgba(255,214,120,.95)':'rgba(240,196,90,.9)';x.lineWidth=s*.035;x.beginPath();x.arc(0,s*.36,s*.42,Math.PI*1.15,Math.PI*1.85);x.stroke();
 if(s>18){x.fillStyle=night?'#ffd878':'#f0c45a';x.font=`700 ${Math.round(s*.42)}px "Shippori Mincho","Noto Serif JP",serif`;x.textAlign='center';x.textBaseline='middle';x.fillText('勝',0,s*.42)}
 // つや
 x.fillStyle='rgba(255,255,255,.28)';x.beginPath();x.ellipse(-s*.5,-s*.45,s*.1,s*.22,-.5,0,7);x.fill();
 x.restore()}
// だるまをぎっしり並べた段（奥の段ほど小さく）
function darumaRow(x,x0,x1,y,s,seed,o={}){const q=rng(seed);let xx=x0;while(xx<x1){const ss=s*(.85+q()*.3);daruma(x,xx,y-ss*.9+(q()-.5)*s*.1,ss,{...o,rot:(q()-.5)*.12,col:q()<.12?'#e9e2d6':(q()<.1?'#d4a020':o.col)});xx+=ss*1.55+q()*s*.2}}
function stoneLedge(x,y,h,col,seed){const q=rng(seed);x.fillStyle=col;x.fillRect(0,y,W,h);for(let i=0;i<W/30;i++){x.fillStyle=rgba(q()<.5?'#ffffff':'#000000',.06+q()*.05);x.fillRect(i*30+q()*10,y+q()*h*.6,24+q()*20,h*.3)}x.fillStyle='rgba(255,240,210,.35)';x.fillRect(0,y,W,2);
 for(let i=0;i<W/14;i++){x.fillStyle=rgba(AO[i%4],.6);x.beginPath();x.ellipse(q()*W,y+2,6+q()*14,3,0,0,7);x.fill()}}
function lantern(x,cx,cy,s,lit){x.fillStyle='#2a1a12';x.fillRect(cx-s*.06,cy-s*.95,s*.12,s*.15);const g=x.createLinearGradient(0,cy-s*.8,0,cy+s*.5);
 g.addColorStop(0,lit?'#fff0c0':'#e8dcc8');g.addColorStop(1,lit?'#ffb050':'#c8b8a0');x.fillStyle=g;x.beginPath();x.ellipse(cx,cy-s*.15,s*.4,s*.65,0,0,7);x.fill();x.fillStyle='#2a1a12';x.fillRect(cx-s*.3,cy+s*.45,s*.6,s*.1);x.fillRect(cx-s*.3,cy-s*.82,s*.6,s*.1)}

// ===== H0 見せ場：紅葉の下、石垣の段にぎっしり並ぶ勝ちダルマ（右上から日の光） =====
function H0(){const L={};const LT=[760,140,1250];
 {const c=cv(),x=c.getContext('2d');sky(x,'#fff3d8','#f2c890',0,700);glow(x,LT[0],LT[1],700,.9,'255,248,226');
  const far=cv(),fx=far.getContext('2d');for(let r=0;r<3;r++)for(let i=0;i<8;i++)leafCloud(fx,(i/7)*W+(r%2)*40-20,140+r*170,170,130,1600,12,PALM,500+r*10+i,{light:LT});
  x.drawImage(layerBlur(far,6),0,0);fx.globalCompositeOperation='source-over';
  {const hz=x.createLinearGradient(0,300,0,760);hz.addColorStop(0,'rgba(255,240,214,0)');hz.addColorStop(1,'rgba(255,236,206,.5)');x.fillStyle=hz;x.fillRect(0,300,W,460)}
  L.b=finish(c,2101,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 奥から手前へ石垣の段：段ごとにだるま
  const rows=[[560,26,'#9a8a72'],[700,34,'#958470'],[860,44,'#8a7862'],[1050,56,'#7e6c58']];
  rows.forEach(([y,s,col],i)=>{ishigaki(x,[[0,y],[W,y],[W,y+ (i<3?rows[i+1][0]-y:H-y+10)],[0,y+(i<3?rows[i+1][0]-y:H-y+10)]],700+i,30+i*8,18+i*5,col,.35);stoneLedge(x,y-6,10+i*3,mix(col,'#c8c0b0',.3),710+i);darumaRow(x,-s,W+s,y-4,s,720+i,{lit:1});const q=rng(760+i);for(let k=0;k<60;k++)leaf(x,q()*W,y+4+q()*(12+i*4),4+i*2.5,q()*6,PALM[k%PALM.length],7)});
  // 木もれ日
  x.save();x.globalCompositeOperation='source-atop';const q2=rng(77);for(let k=0;k<26;k++){const xx=q2()*W,yy=520+q2()*800,r=30+q2()*90;const gg=x.createRadialGradient(xx,yy,0,xx,yy,r);gg.addColorStop(0,'rgba(255,226,160,.4)');gg.addColorStop(1,'rgba(255,226,160,0)');x.fillStyle=gg;x.beginPath();x.ellipse(xx,yy,r,r*.45,0,0,7);x.fill()}x.restore();
  L.m=finish(c,2102,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 上をおおう紅葉の枝と、手前の大きなだるま
  hangBranch(x,[[W+30,120],[W-120,90],[W-260,120],[W-420,95],[W-560,130]],PAL,731,{light:LT});
  hangBranch(x,[[-30,60],[110,40],[240,70],[360,50]],PALM,732,{light:LT});
  leafCloud(x,-10,560,120,330,2600,11,PAL,733,{light:LT});leafCloud(x,W+10,520,120,300,2400,11,PALM,734,{light:LT});
  daruma(x,250,1290,150,{lit:1});daruma(x,700,1330,120,{lit:1,rot:.06});
  L.n=finish(c,2103,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,40,H-60,220,140,50,46,PAL,741);leafCloud(sx,W-30,H-30,200,130,40,46,PAL,742);L.f=layerBlur(s,7)}
 return L}

// ===== H1 本堂へ続く、紅葉のトンネルの参道（奥に光） =====
function H1(){const L={};const vx=W/2,vy=640;const LT=[vx,vy-60,900];
 {const c=cv(),x=c.getContext('2d');const g=x.createRadialGradient(vx,vy-40,10,vx,vy-40,900);g.addColorStop(0,'#fff8e0');g.addColorStop(.15,'#ffd98e');g.addColorStop(.45,'#e07a34');g.addColorStop(1,'#5a160c');x.fillStyle=g;x.fillRect(0,0,W,H);
  // 奥の多宝塔（光の中の影）
  x.fillStyle='rgba(120,60,40,.5)';x.fillRect(vx-22,vy-150,44,90);x.beginPath();x.moveTo(vx-70,vy-150);x.lineTo(vx,vy-190);x.lineTo(vx+70,vy-150);x.fill();x.beginPath();x.moveTo(vx-56,vy-100);x.lineTo(vx,vy-125);x.lineTo(vx+56,vy-100);x.fill();x.fillRect(vx-2,vy-240,4,55);
  L.b=finish(c,2201,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 参道（石畳）と両側の紅葉のアーチ
  x.fillStyle='#5a3a26';x.beginPath();x.moveTo(vx-30,vy);x.lineTo(vx+30,vy);x.lineTo(W*.82,H);x.lineTo(W*.18,H);x.fill();
  const q=rng(9);for(let i=0;i<600;i++){const k=Math.pow(q(),1.4),y=vy+k*(H-vy),w=60+k*(W*.64-60);leaf(x,vx-w/2+q()*w,y,2+k*12,q()*6,PALM[i%PALM.length],7)}
  for(let i=0;i<7;i++){const k=i/6;const y=vy-40+Math.pow(k,1.6)*(H-vy+80);const sp=40+Math.pow(k,1.5)*560;
   leafCloud(x,vx-sp,y-120-k*340,90+k*260,120+k*360,1500+k*4000,7+k*7,PALM,800+i,{light:LT});leafCloud(x,vx+sp,y-120-k*340,90+k*260,120+k*360,1500+k*4000,7+k*7,PALM,820+i,{light:LT})}
  leafCloud(x,vx,120,620,240,9000,10,PAL,840,{light:LT});
  for(const sd of[-1,1])for(let i=0;i<5;i++){const k=i/4;daruma(x,vx+sd*(50+k*300),vy+30+Math.pow(k,1.5)*560,8+k*44,{lit:1})}
  L.m=finish(c,2202,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');trunk(x,[[10,H],[70,H-400],[40,H-760],[120,H-1100],[240,H-1300]],64,16,'#3a2418',851);trunk(x,[[W-10,H],[W-80,H-420],[W-50,H-780],[W-130,H-1110],[W-250,H-1310]],64,16,'#3a2418',852);
  L.n=finish(c,2203,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,W-40,40,240,170,50,46,PALM,861);leafCloud(sx,40,H-40,230,150,50,46,PAL,862);L.f=layerBlur(s,7)}
 return L}

// ===== H2 夜の宵詣り：灯籠の灯りに浮かぶだるまと紅葉 =====
function H2(){const L={};const LT=[W/2,820,620];const OP={light:LT,dark:'#0c0208',hi:'#ffc070'};
 {const c=cv(),x=c.getContext('2d');const g=x.createLinearGradient(0,0,0,H);g.addColorStop(0,'#070a22');g.addColorStop(.6,'#151a3c');g.addColorStop(1,'#1e1430');x.fillStyle=g;x.fillRect(0,0,W,H);
  const q=rng(3);for(let i=0;i<240;i++){x.fillStyle=`rgba(255,250,235,${.3+q()*.6})`;x.beginPath();x.arc(q()*W,q()*600,q()*1.7+.3,0,7);x.fill()}
  L.b=finish(c,2301,{rim:false,g:6,blot:.02})}
 {const c=cv(),x=c.getContext('2d');
  maple(x,140,860,620,PAL,901,OP);maple(x,W-130,860,640,PAL,902,{...OP,lean:-.1});
  const rows=[[820,30],[960,40],[1120,52]];rows.forEach(([y,s],i)=>{x.fillStyle=mix('#2a2230','#3a3038',i*.3);x.fillRect(0,y-4,W,H-y);x.fillStyle='rgba(255,190,120,.35)';x.fillRect(0,y-4,W,2);darumaRow(x,-s,W+s,y,s,910+i,{night:true,lit:.8})});
  [[160,760,70],[W-160,760,70],[90,1000,90],[W-90,1000,90]].forEach(([lx,ly,s])=>lantern(x,lx,ly,s,true));
  L.m=finish(c,2302,{rim:false,g:5,blot:0})}
 {const c=cv(),x=c.getContext('2d');x.globalCompositeOperation='lighter';[[160,760,70],[W-160,760,70],[90,1000,90],[W-90,1000,90]].forEach(([lx,ly,s])=>{glow(x,lx,ly-s*.15,s*1.4,.8,'255,200,120');glow(x,lx,ly,s*3.4,.25,'255,160,80')});glow(x,W/2,980,420,.25,'255,180,100');L.n=c}
 {const c=cv(),x=c.getContext('2d');daruma(x,300,1330,140,{night:true,lit:.9});daruma(x,690,1360,110,{night:true,lit:.9,rot:-.05});
  x.globalCompositeOperation='source-atop';const g=x.createLinearGradient(0,1180,0,H);g.addColorStop(0,'rgba(255,180,100,.25)');g.addColorStop(1,'rgba(20,4,8,.35)');x.fillStyle=g;x.fillRect(0,1150,W,300);L.f=c}
 return L}
window.SCN=Object.assign(window.SCN||{},{H0,H1,H2});
