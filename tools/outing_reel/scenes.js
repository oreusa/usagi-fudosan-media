let SCB=null;function scBlur(c,px,fn){if(!SCB)SCB=xmCanvas(XW,XH);const g=SCB.getContext('2d');g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.filter='none';g.globalCompositeOperation='source-over';g.clearRect(0,0,XW,XH);fn(g);c.save();c.filter=`blur(${px}px)`;c.drawImage(SCB,0,0);c.restore()}
// 11/16 絵本の景色（canvas・3層でページから立ち上がる）。xmas.js の道具（wash・wob・glow・xmPerson など）を使う。
// scene 'momiji'＝社ともみじの苑（昼の楼門／もみじの谷と朱の橋とお茶の席／夜のライトアップ）
// scene 'hama'＝白い砂浜と海（昼の浜／夕焼けと円い穴の島／夜の光のパレード）
function scSky(c,cols,y1){const g=c.createLinearGradient(0,0,0,y1||XH);cols.forEach((q,i)=>g.addColorStop(i/(cols.length-1),q));c.fillStyle=g;c.fillRect(0,0,XW,XH);
 c.save();c.globalCompositeOperation='multiply';c.globalAlpha=.06;c.drawImage(xmNoise(),0,0);c.restore()}
function scClouds(c,seed,n,y0,y1,col,a){const r=XR(seed);c.save();c.filter='blur(16px)';for(let i=0;i<n;i++){const x=r()*XW,y=y0+r()*(y1-y0),w=120+r()*240;c.globalAlpha=a;c.fillStyle=col;c.beginPath();c.ellipse(x,y,w,w*.15,0,0,7);c.fill()}c.restore()}

// ---------- もみじ ----------
function mjLeaf(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);c.beginPath();
 for(let i=0;i<7;i++){const a=-Math.PI/2+(i-3)*.62,L=i==3?1:i==2||i==4?.9:i==1||i==5?.66:.38;const a0=a-.2,a1=a+.2;
  c.lineTo(Math.cos(a0)*s*L*.42,Math.sin(a0)*s*L*.42);c.lineTo(Math.cos(a)*s*L,Math.sin(a)*s*L);c.lineTo(Math.cos(a1)*s*L*.42,Math.sin(a1)*s*L*.42)}
 c.lineTo(0,s*.25);c.closePath();c.fill();c.restore()}
// 楼門（朱の柱・白い壁・二重の屋根）
function mjGate(c,cx,by,w,mode,L){const night=mode==2,h=w*.95;const ver=night?'#5a1a14':mode==1?'#b2382a':'#c8402e',roof=night?'#0e0d12':'#2c2a30',wall=night?'#3a3236':'#f2ece0';
 const st=by-h*.08;wash(c,g=>wob(g,[[cx-w*.56,st],[cx+w*.56,st],[cx+w*.6,by],[cx-w*.6,by]],1.2,3),night?'#2a2628':'#9a948a',{edge:.3,gr:.3});
 // 柱
 for(const k of[-.42,-.14,.14,.42]){wash(c,g=>wob(g,[[cx+w*k-w*.03,st-h*.42],[cx+w*k+w*.03,st-h*.42],[cx+w*k+w*.03,st],[cx+w*k-w*.03,st]],.8,7),ver,{edge:.45,gr:.25})}
 // 下の屋根
 const roofShape=(y,ww,hh,sd)=>wash(c,g=>{g.moveTo(cx-ww*.62,y);g.quadraticCurveTo(cx-ww*.5,y-hh*.25,cx-ww*.38,y-hh);g.lineTo(cx+ww*.38,y-hh);g.quadraticCurveTo(cx+ww*.5,y-hh*.25,cx+ww*.62,y);g.quadraticCurveTo(cx,y-hh*.18,cx-ww*.62,y)},roof,{edge:.5,gr:.3,ec:'#000000'});
 wash(c,g=>wob(g,[[cx-w*.46,st-h*.5],[cx+w*.46,st-h*.5],[cx+w*.46,st-h*.42],[cx-w*.46,st-h*.42]],1,9),ver,{edge:.4});
 roofShape(st-h*.46,w*1.05,h*.15,1);
 // 上の階
 wash(c,g=>wob(g,[[cx-w*.34,st-h*.78],[cx+w*.34,st-h*.78],[cx+w*.34,st-h*.56],[cx-w*.34,st-h*.56]],1,11),wall,{edge:.4,gr:.25});
 for(const k of[-.33,-.11,.11,.33]){c.fillStyle=ver;c.fillRect(cx+w*k-w*.018,st-h*.78,w*.036,h*.22)}
 c.strokeStyle=ver;c.lineWidth=2;for(let i=0;i<6;i++){c.beginPath();c.moveTo(cx-w*.34,st-h*.58-i*3);c.lineTo(cx+w*.34,st-h*.58-i*3);c.stroke()}
 roofShape(st-h*.76,w*.9,h*.2,2);
 // 金の飾り
 c.fillStyle='#d9b45a';for(const k of[-.4,.4])c.beginPath(),c.arc(cx+w*k*.9,st-h*.9,3,0,7),c.fill();
 if(night&&L){L.push({x:cx,y:st-h*.25,r:w*.7,c:'255,160,90',a:.35,p:0,sp:.2,soft:1});for(const k of[-.28,.28])L.push({x:cx+w*k,y:st-h*.36,r:28,c:'255,190,110',a:.9,p:k*9,sp:2.4,dot:2.4})}}
// 朱の橋（反り橋・手すり・擬宝珠）
function mjBridge(c,x0,x1,y,arch,mode,L){const night=mode==2;const ver=night?'#6a2016':'#c23c2a';const m=(x0+x1)/2;
 const deck=u=>y-arch*Math.sin(Math.PI*u);
 wash(c,g=>{g.moveTo(x0,y);for(let i=0;i<=20;i++){const u=i/20;g.lineTo(x0+(x1-x0)*u,deck(u))}for(let i=20;i>=0;i--){const u=i/20;g.lineTo(x0+(x1-x0)*u,deck(u)+16)}g.closePath()},ver,{edge:.5,gr:.25});
 // 橋げた
 c.strokeStyle=night?'#2a0d08':'#7a2418';c.lineWidth=5;for(let i=1;i<6;i++){const u=i/6,x=x0+(x1-x0)*u;c.beginPath();c.moveTo(x,deck(u)+16);c.lineTo(x,y+40);c.stroke()}
 // 手すり
 c.strokeStyle=ver;c.lineWidth=3.5;c.beginPath();for(let i=0;i<=20;i++){const u=i/20;c.lineTo(x0+(x1-x0)*u,deck(u)-26)}c.stroke();c.lineWidth=2;c.beginPath();for(let i=0;i<=20;i++){const u=i/20;c.lineTo(x0+(x1-x0)*u,deck(u)-12)}c.stroke();
 for(let i=0;i<=8;i++){const u=i/8,x=x0+(x1-x0)*u;c.lineWidth=4;c.beginPath();c.moveTo(x,deck(u)-30);c.lineTo(x,deck(u));c.stroke();if(i==0||i==8||i==4){c.fillStyle='#c9a24e';c.beginPath();c.arc(x,deck(u)-34,5,0,7);c.fill()}}
 if(night&&L)for(let i=0;i<=8;i+=2){const u=i/8;L.push({x:x0+(x1-x0)*u,y:deck(u)-20,r:22,c:'255,150,90',a:.4,p:i,sp:.3,soft:1})}}
function mjStream(c,y0,y1,mode){const P=[['#9cc4c4','#6e9e9e'],['#7e8f84','#4e5f56'],['#151a2a','#0a0d18']][mode];
 wash(c,g=>{g.moveTo(-20,y0);g.bezierCurveTo(300,y0-20,600,y0+30,XW+20,y0-10);g.lineTo(XW+20,y1);g.bezierCurveTo(600,y1+20,300,y1-30,-20,y1);g.closePath()},P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,y1);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.2,gr:.3,light:false});
 const r=XR(9);c.strokeStyle=mode==2?'rgba(255,170,110,.25)':'rgba(255,255,255,.45)';c.lineWidth=1.3;for(let i=0;i<40;i++){const x=r()*XW,y=y0+8+r()*(y1-y0-16),l=10+r()*40;c.beginPath();c.moveTo(x,y);c.lineTo(x+l,y);c.stroke()}}
function mjLantern(c,x,by,s,mode,L){const night=mode==2;const st=night?'#2e2c34':'#8f8a80';
 wash(c,g=>wob(g,[[x-s*.12,by-s*.55],[x+s*.12,by-s*.55],[x+s*.08,by],[x-s*.08,by]],.6,1),st,{edge:.4,gr:.3});
 wash(c,g=>wob(g,[[x-s*.24,by-s*.62],[x+s*.24,by-s*.62],[x+s*.18,by-s*.55],[x-s*.18,by-s*.55]],.6,2),st,{edge:.4});
 c.fillStyle=night?'#ffd28a':'#e8dcc0';c.fillRect(x-s*.13,by-s*.84,s*.26,s*.22);c.strokeStyle=st;c.lineWidth=2;c.strokeRect(x-s*.13,by-s*.84,s*.26,s*.22);
 wash(c,g=>{g.moveTo(x-s*.3,by-s*.84);g.quadraticCurveTo(x,by-s*1.02,x+s*.3,by-s*.84);g.closePath()},st,{edge:.4});c.fillStyle=st;c.beginPath();c.arc(x,by-s*1.02,s*.05,0,7);c.fill();
 if(L)L.push({x,y:by-s*.73,r:s*1.1,c:'255,190,110',a:night?.9:.15,p:x,sp:2,dot:night?2.6:0})}
function mjBench(c,x,by,w,mode,L){const night=mode==2;
 // 野点傘
 const ux=x+w*.7,uy=by-w*1.25;c.strokeStyle=night?'#1a1010':'#5a3a26';c.lineWidth=4;c.beginPath();c.moveTo(ux,uy);c.lineTo(ux-w*.05,by);c.stroke();
 wash(c,g=>{g.moveTo(ux-w*.75,uy+w*.26);g.quadraticCurveTo(ux,uy-w*.2,ux+w*.75,uy+w*.26);g.quadraticCurveTo(ux,uy+w*.12,ux-w*.75,uy+w*.26)},night?'#6a1810':'#c8302a',{edge:.5,gr:.25});
 c.strokeStyle='rgba(255,230,210,.35)';c.lineWidth=1;for(let i=-4;i<=4;i++){c.beginPath();c.moveTo(ux,uy-w*.02);c.lineTo(ux+i*w*.17,uy+w*.2+Math.abs(i)*w*.012);c.stroke()}
 // 床几と毛氈
 wash(c,g=>wob(g,[[x,by-w*.3],[x+w,by-w*.3],[x+w,by-w*.22],[x,by-w*.22]],.8,4),night?'#5a1410':'#b8281f',{edge:.4});
 c.strokeStyle=night?'#1a1010':'#4a3022';c.lineWidth=3;for(const k of[.06,.94]){c.beginPath();c.moveTo(x+w*k,by-w*.22);c.lineTo(x+w*k,by);c.stroke()}
 // 茶碗とお菓子
 c.fillStyle='#2e5a3e';c.beginPath();c.ellipse(x+w*.3,by-w*.34,w*.06,w*.04,0,0,7);c.fill();c.fillStyle='#f4ead8';c.beginPath();c.ellipse(x+w*.48,by-w*.33,w*.07,w*.025,0,0,7);c.fill();c.fillStyle='#d97a8a';c.beginPath();c.arc(x+w*.48,by-w*.36,w*.028,0,7);c.fill();
 if(L&&night)L.push({x:ux,y:uy+w*.3,r:w*.6,c:'255,140,80',a:.3,p:0,sp:.3,soft:1})}
function mjGround(c,y0,mode){const P=[['#b8ad8c','#8a805e'],['#8a7a5a','#5a4a34'],['#1c1a1e','#0c0b0e']][mode];
 wash(c,g=>wob(g,[[-20,y0],[XW+20,y0],[XW+20,XH+20],[-20,XH+20]],3,21),P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,XH);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.1,gr:.35,light:false});
 // 苔と落ち葉
 const r=XR(31);c.save();c.filter='blur(3px)';for(let i=0;i<30;i++){c.fillStyle=mode==2?'rgba(40,50,30,.3)':'rgba(90,110,60,.28)';c.beginPath();c.ellipse(r()*XW,y0+r()*(XH-y0),40+r()*80,8+r()*12,0,0,7);c.fill()}c.restore();
 const pal=mode==2?['#7a1a12','#a02c18','#5a120c']:['#c8402c','#e0662f','#ea8a34','#b3301f'];for(let i=0;i<260;i++){c.fillStyle=pal[i%pal.length];c.globalAlpha=.8;mjLeaf(c,r()*XW,y0+10+Math.pow(r(),.7)*(XH-y0),5+r()*7,r()*6.3)}c.globalAlpha=1}
function mjBuild(mode){const B=xmLayer(),T=xmLayer(),F=xmLayer();let c=B.c,L=B.L;
 if(mode==0){scSky(c,['#b9d0dc','#e9eee8','#f6ecd8'],900);scClouds(c,4,6,120,520,'#ffffff',.5);
  c.save();c.globalCompositeOperation='screen';glow(c,300,420,500,'255,230,190',.4);c.restore();
  mjMaple(c,-40,980,520,0,11,L,{n:900});mjMaple(c,960,960,540,0,12,L,{n:900});
  mjGround(c,960,0);
  // 石の道
  wash(c,g=>{g.moveTo(400,960);g.lineTo(520,960);g.lineTo(760,XH);g.lineTo(160,XH);g.closePath()},'#d8d0bc',{edge:.2,gr:.35,light:false});
  mjGate(T.c,460,1010,420,0,T.L);T.ax=460;T.ay=1010;T.d=.1;
  mjLantern(F.c,180,1180,150,0,F.L);mjLantern(F.c,740,1180,150,0,F.L);
  mjMaple(F.c,-60,1420,620,0,21,F.L,{n:700,wide:.6});mjMaple(F.c,1000,1440,560,0,22,F.L,{n:600,wide:.6});
  xmPerson(F.c,430,1250,110,'#4a4a5e',0,31,0);xmPerson(F.c,470,1256,100,'#7a4a3a',0,32,1);F.ax=460;F.ay=1300;F.d=.4;
 }else if(mode==1){scSky(c,['#e8c9a6','#f3dcc0','#f6e6d0'],700);
  c.save();c.globalCompositeOperation='screen';glow(c,700,300,520,'255,210,160',.45);c.restore();
  mjMaple(c,120,820,560,1,41,L,{n:1100,wide:1});mjMaple(c,560,800,600,1,42,L,{n:1100,wide:1});mjMaple(c,900,830,520,1,43,L,{n:900,wide:.9});
  mjGround(c,880,1);mjStream(c,960,1080,1);
  mjBridge(T.c,170,750,1010,70,1,T.L);mjMaple(T.c,-80,1160,700,1,44,T.L,{n:900,wide:.7});T.ax=460;T.ay=1100;T.d=.1;
  mjBench(F.c,520,1290,300,1,F.L);xmPerson(F.c,480,1300,120,'#5a5a6e',1,36,0);
  mjMaple(F.c,980,1500,620,1,45,F.L,{n:700,wide:.6});F.ax=600;F.ay=1300;F.d=.4;
 }else{scSky(c,['#05070f','#0d1124','#1b1830'],900);xmStars(c,9);xmMoon(c,220,230,46);
  mjMaple(c,120,860,560,2,41,L,{n:1100,wide:1});mjMaple(c,560,840,600,2,42,L,{n:1100,wide:1});mjMaple(c,900,860,520,2,43,L,{n:900,wide:.9});
  mjGround(c,900,2);mjStream(c,980,1110,2);
  L.push({x:460,y:1040,rx:520,ry:70,c:'255,120,60',a:.3,p:0,sp:0,soft:1,ell:1});
  mjBridge(T.c,170,750,1030,70,2,T.L);mjMaple(T.c,-80,1180,700,2,44,T.L,{n:900,wide:.7});T.ax=460;T.ay=1120;T.d=.1;
  for(let i=0;i<4;i++)mjLantern(F.c,120+i*230,1290+(i%2)*30,120,2,F.L);
  mjMaple(F.c,1000,1520,620,2,45,F.L,{n:700,wide:.6});xmPerson(F.c,560,1330,110,'#3a3a4a',2,38,0);xmPerson(F.c,592,1334,98,'#4a2a30',2,39,1);F.ax=520;F.ay=1330;F.d=.4;
 }
 return scFinish(mode,B,T,F,[960,880,900][mode])}
function scFinish(mode,B,T,F,gy){T.sh=xmShadowOf(T.cv);F.sh=xmShadowOf(F.cv);
 const V=xmCanvas(XW,XH),v=V.getContext('2d');const vg=v.createRadialGradient(460,660,320,460,700,1020);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,mode==2?'rgba(0,0,0,.45)':'rgba(80,50,30,.2)');v.fillStyle=vg;v.fillRect(0,0,XW,XH);
 return{B,T,F,V,gy}}

// ---------- 白い砂浜 ----------
function hmIsland(c,cx,by,w,mode){const night=mode==2,col=night?'#0a0c18':mode==1?'#3a2430':'#6a7a6a';
 // 円月島：上に木、まん中に円い穴
 c.save();wash(c,g=>{g.moveTo(cx-w*.5,by);g.quadraticCurveTo(cx-w*.48,by-w*.5,cx-w*.2,by-w*.62);g.quadraticCurveTo(cx+w*.1,by-w*.72,cx+w*.36,by-w*.55);g.quadraticCurveTo(cx+w*.5,by-w*.4,cx+w*.5,by);g.closePath()},col,{edge:.3,gr:.3});
 c.globalCompositeOperation='destination-out';c.beginPath();c.ellipse(cx,by-w*.12,w*.15,w*.17,0,0,7);c.fill();c.restore();
 const r=XR(5);c.fillStyle=night?'#05060c':mode==1?'#2a1a22':'#4a6a4a';for(let i=0;i<40;i++){const x=cx-w*.3+r()*w*.62,y=by-w*.6+Math.abs(x-cx)*.25-r()*14;c.beginPath();c.arc(x,y,4+r()*7,0,7);c.fill()}}
function hmPine(c,x,by,h,mode,seed){const r=XR(seed);const night=mode==2;c.strokeStyle=night?'#100c10':'#4a3426';c.lineCap='round';c.lineWidth=h*.035;c.beginPath();c.moveTo(x,by);c.bezierCurveTo(x+h*.12,by-h*.4,x-h*.1,by-h*.6,x+h*.08,by-h*.9);c.stroke();
 const G=night?['#0a1410','#10201a']:mode==1?['#2a3a2a','#3a4a32']:['#2e5a3e','#3e7048','#4e8456'];
 for(let k=0;k<5;k++){const yy=by-h*(.55+k*.1),xx=x+(k%2?-1:1)*h*.12+h*.02*k,ww=h*(.32-k*.04);for(let i=0;i<70;i++){c.fillStyle=G[i%G.length];c.globalAlpha=.85;c.beginPath();c.ellipse(xx+(r()-.5)*ww,yy+(r()-.5)*h*.05,ww*.12,h*.012,(r()-.5)*.3,0,7);c.fill()}}c.globalAlpha=1}
function hmSand(c,y0,mode){const P=[['#f8f3e8','#ece2cc'],['#e8c9b0','#c49a86'],['#26243a','#141224']][mode];
 wash(c,g=>{g.moveTo(-20,y0+40);g.bezierCurveTo(250,y0-10,640,y0+10,XW+20,y0-30);g.lineTo(XW+20,XH+20);g.lineTo(-20,XH+20);g.closePath()},P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,XH);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.15,gr:.25,light:false});
 c.strokeStyle=mode==2?'rgba(180,200,255,.25)':'rgba(255,255,255,.9)';c.lineWidth=5;c.beginPath();c.moveTo(-20,y0+40);c.bezierCurveTo(250,y0-10,640,y0+10,XW+20,y0-30);c.stroke();
 c.lineWidth=1.5;c.strokeStyle=mode==2?'rgba(180,200,255,.12)':'rgba(255,255,255,.6)';c.beginPath();c.moveTo(-20,y0+58);c.bezierCurveTo(250,y0+8,640,y0+28,XW+20,y0-12);c.stroke()}
function hmHotels(c,y,mode,L){const r=XR(17);const night=mode==2;for(let i=0;i<7;i++){const x=470+i*70+r()*20,w=50+r()*40,h=60+r()*110;
 wash(c,g=>wob(g,[[x,y-h],[x+w,y-h],[x+w,y],[x,y]],1,i),night?'#1a1c2c':mode==1?'#c8a8a0':'#e8e4dc',{edge:.3,gr:.2,light:false});
 for(let yy=y-h+8;yy<y-6;yy+=10)for(let xx=x+5;xx<x+w-5;xx+=9){const lit=night&&r()<.6;c.fillStyle=night?(lit?'#ffd08a':'#2a2a3a'):'rgba(90,110,140,.5)';c.fillRect(xx,yy,4,5);if(lit&&L&&r()<.15)L.push({x:xx,y:yy,r:10,c:'255,200,130',a:.5,p:r()*6,sp:.3,soft:1})}}}
function hmBuild(mode){const B=xmLayer(),T=xmLayer(),F=xmLayer();let c=B.c,L=B.L;
 if(mode==0){scSky(c,['#8fc0e0','#cfe4ee','#f2f2ea'],800);scClouds(c,6,7,140,560,'#ffffff',.6);
  xmGulls(c,6,6);xmSea(c,780,980,0);
  c.save();const g=c.createLinearGradient(0,780,0,980);g.addColorStop(0,'rgba(80,190,200,.0)');g.addColorStop(1,'rgba(80,200,200,.35)');c.fillStyle=g;c.fillRect(0,780,XW,200);c.restore();
  hmIsland(c,170,800,170,0);hmHotels(c,790,0,L);
  hmSand(c,960,0);
  hmPine(T.c,780,1120,520,0,3);hmPine(T.c,880,1160,430,0,4);T.ax=830;T.ay=1150;T.d=.1;
  xmPerson(F.c,330,1260,110,'#3e5a7e',0,31,0);xmPerson(F.c,366,1266,100,'#c08a5a',0,32,1);xmPerson(F.c,400,1272,76,'#e2b84a',0,33,2);F.ax=360;F.ay=1280;F.d=.4;
 }else if(mode==1){scSky(c,['#3a3a7a','#b0608a','#f2a070','#f8d098'],820);
  c.save();c.globalCompositeOperation='screen';glow(c,520,770,420,'255,190,120',.7);c.restore();
  c.fillStyle='#fff0c8';c.beginPath();c.arc(520,778,46,Math.PI,0);c.fill();
  xmSea(c,780,990,1);c.save();c.globalCompositeOperation='lighter';const r=XR(8);for(let i=0;i<60;i++){const y=790+r()*190,x=520+(r()-.5)*(60+(y-780)*1.2);c.fillStyle=`rgba(255,200,120,${.2+r()*.4})`;c.fillRect(x,y,8+r()*30,2)}c.restore();
  hmSand(c,980,1);
  hmIsland(T.c,240,860,230,1);T.ax=240;T.ay=860;T.d=.05;
  hmPine(F.c,820,1300,560,1,3);xmPerson(F.c,560,1300,120,'#3a3a5a',1,36,0);xmPerson(F.c,596,1306,104,'#6a3a3a',1,37,1);F.ax=700;F.ay=1300;F.d=.4;
  L.push({x:520,y:778,r:180,c:'255,200,140',a:.5,p:0,sp:0,soft:1});
 }else{scSky(c,['#04050d','#0a0e24','#181a3a'],820);xmStars(c,9);xmMoon(c,200,220,44);
  xmSea(c,780,960,2);hmIsland(c,170,800,170,2);hmHotels(c,790,2,L);
  hmSand(c,940,2);
  // 光のパレードの舞台：砂浜に並ぶ光
  const cols=['255,110,170','110,190,255','255,210,110','170,130,255','120,255,200'];
  for(let i=0;i<22;i++){const x=40+i*40,y=1010+Math.sin(i*.7)*16;L.push({x,y,r:30,c:cols[i%5],a:.85,p:i*.6,sp:3,dot:2.4})}
  for(let i=0;i<14;i++){const x=60+i*62,y=1120+Math.cos(i*.9)*20;L.push({x,y,r:40,c:cols[(i+2)%5],a:.8,p:i,sp:2.2,dot:2.6})}
  L.push({x:460,y:1080,rx:520,ry:110,c:'150,140,255',a:.3,p:0,sp:0,soft:1,ell:1});
  hmPine(T.c,820,1180,500,2,3);T.ax=820;T.ay=1180;T.d=.1;
  xmPerson(F.c,380,1320,110,'#2a2a3a',2,38,0);xmPerson(F.c,414,1326,98,'#3a2228',2,39,1);xmPerson(F.c,446,1330,74,'#2a3a4a',2,40,2);F.ax=420;F.ay=1330;F.d=.4;
 }
 return scFinish(mode,B,T,F,[960,980,940][mode])}

// ---------- 絵の中の動き ----------
// もみじ：葉が舞う。夜は光る葉がゆっくり浮かび上がる
function mjFx(c,mode,t,u){const r=XR(600+mode);c.save();
 if(mode<2){for(let i=0;i<34;i++){const x0=r()*XW,sp=40+r()*60,ph=r()*7,y0=r()*(XH+80),s=7+r()*9;const y=((y0+t*sp)%(XH+80))-40,x=x0+Math.sin(t*.9+ph)*36;
   c.fillStyle=['#c8402c','#e0662f','#ea8a34','#b3301f'][i%4];c.globalAlpha=.9;mjLeaf(c,x,y,s,t*1.5*(i%2?1:-1)+ph)}}
 else{c.globalCompositeOperation='lighter';for(let i=0;i<26;i++){const T=5+r()*3,p=((t/T+r())%1),x=60+r()*800+Math.sin(t*.7+i)*30,y=1150-p*(700+r()*300),s=8+r()*8;const a=Math.sin(Math.PI*p);
   glow(c,x,y,s*3,'255,140,70',a*.35);c.globalAlpha=a*.9;c.fillStyle='#ffb070';mjLeaf(c,x,y,s,t*.8+i)}}
 c.restore();c.globalAlpha=1}
// 浜：昼はかもめ、夕方は流れ星、夜は光の帯が砂浜をなめるように動き、光の玉が浮かび上がる
function hmFx(c,mode,t,u){c.save();
 if(mode==1&&typeof xmShoot=='function')xmShoot(c,u);
 if(mode==2){c.globalCompositeOperation='lighter';const cols=['255,110,170','110,190,255','255,210,110','170,130,255','120,255,200'];
  for(let k=0;k<6;k++){const a=-Math.PI/2+Math.sin(t*1.1+k*1.3)*.7,x=80+k*150,y=1040;c.save();c.filter='blur(10px)';const g=c.createLinearGradient(x,y,x+Math.cos(a)*700,y+Math.sin(a)*700);g.addColorStop(0,`rgba(${cols[k%5]},.35)`);g.addColorStop(1,`rgba(${cols[k%5]},0)`);c.fillStyle=g;c.beginPath();c.moveTo(x,y);c.lineTo(x+Math.cos(a-.06)*700,y+Math.sin(a-.06)*700);c.lineTo(x+Math.cos(a+.06)*700,y+Math.sin(a+.06)*700);c.closePath();c.fill();c.restore()}
  const r=XR(77);for(let i=0;i<30;i++){const T=4+r()*3,p=((t/T+r())%1),x=40+r()*840+Math.sin(t+i)*20,y=1080-p*(600+r()*300);glow(c,x,y,10+r()*10,cols[i%5],Math.sin(Math.PI*p)*.7)}}
 c.restore();c.globalAlpha=1}

// ================= 11/16 本格版：ここから下が新しい景色（上の古い組み立てを上書きする） =================
const SC_ZONE=(x,y)=>x>500&&y<690; // 字の場所（右上）。ここには細かい物を置かない
function scBlob(c,x,y,R,cin,cmid,cout,lx,ly,a){const g=c.createRadialGradient(x+lx*R,y+ly*R,R*.05,x,y,R);g.addColorStop(0,cin);g.addColorStop(.55,cmid);g.addColorStop(1,cout);c.globalAlpha=a==null?.92:a;c.fillStyle=g;c.beginPath();c.ellipse(x,y,R,R*.82,0,0,7);c.fill();c.globalAlpha=1}
function scFog(c,y,h,rgb,a){const g=c.createLinearGradient(0,y-h,0,y+h);g.addColorStop(0,`rgba(${rgb},0)`);g.addColorStop(.5,`rgba(${rgb},${a})`);g.addColorStop(1,`rgba(${rgb},0)`);c.fillStyle=g;c.fillRect(0,y-h,XW,h*2)}
function scGrain(c,y0,y1,cols,n,seed,sz){const r=XR(seed);for(let i=0;i<n;i++){c.fillStyle=cols[i%cols.length];const y=y0+Math.pow(r(),.8)*(y1-y0);c.globalAlpha=.25+r()*.4;c.fillRect(r()*XW,y,(sz||1.6)*(.6+(y-y0)/(y1-y0)),(sz||1.6)*.7)}c.globalAlpha=1}
// もみじの木（本格版）：枝→葉のかたまり（光の当たる側が明るい）→何百枚の葉。夜は下から照らす
function mjTree(c,cx,by,h,mode,seed,L,o){o=o||{};const r=XR(seed);const night=mode==2;const w=h*(o.wide||.8);const lean=o.lean||0;
 const bark=night?'#170d0c':'#3e2a20',barkL=night?'#4a2418':'#7a5a44';c.lineCap='round';
 const ccx=cx+lean*h*.5,ccy=by-h*.64,rx=w*.5,ry=h*.3;
 // 幹と枝（かたまりの中へ向かって伸びる）
 const grow=(x,y,a,len,wd,d)=>{const x2=x+Math.cos(a)*len,y2=y+Math.sin(a)*len,mx=(x+x2)/2+(r()-.5)*len*.25,my=(y+y2)/2;
  if(d<3&&((x2-ccx)/rx)**2+((y2-ccy)/ry)**2>.92)return;   // 11/16 葉のかたまりの外へ出る細い枝は描かない（字の近くに黒い枝が飛び出した）
  c.strokeStyle=bark;c.lineWidth=wd;c.beginPath();c.moveTo(x,y);c.quadraticCurveTo(mx,my,x2,y2);c.stroke();
  if(wd>5){c.strokeStyle=barkL;c.globalAlpha=.4;c.lineWidth=wd*.28;c.beginPath();c.moveTo(x-wd*.22,y);c.quadraticCurveTo(mx-wd*.22,my,x2-wd*.2,y2);c.stroke();c.globalAlpha=1}
  if(d<=0)return;const sp=.45+r()*.3;grow(x2,y2,a-sp,len*.72,wd*.62,d-1);grow(x2,y2,a+sp,len*.72,wd*.62,d-1)};
 const ta=Math.atan2(ccy-by,ccx-cx);grow(cx,by,ta,h*.34,h*.06,4);
 const pal=o.pal||(mode==0?{L:'#f6b24a',M:'#e0662f',D:'#a8301e',X:'#6e1a12',leaf:['#c8402c','#e0662f','#ea8a34','#b3301f','#f0b040','#d4552d','#e8a23a']}:
  mode==1?{L:'#f39a48',M:'#d4452a',D:'#96241a',X:'#5a120c',leaf:['#b52a20','#d4402a','#e86a2e','#9c2018','#f09a3a','#c63326']}:
  {L:'#ffb466',M:'#c4401f',D:'#5e140e',X:'#22060a',leaf:['#7a1a12','#9e2a18','#c4401f','#d86a2a','#f0904a','#b8361c']});
 // 葉のかたまり：ドームの中を埋める＋ふちをでこぼこに（下側は少しあけて幹を見せる）
 const cl=[];const N=o.cl||30;for(let i=0;i<N;i++){const a=r()*6.283,rr=Math.sqrt(r())*.8;cl.push([ccx+Math.cos(a)*rr*rx,ccy+Math.sin(a)*rr*ry*.9-ry*.05,h*(.075+r()*.05)])}
 for(let a=-Math.PI;a<Math.PI;a+=.32+r()*.12){if(a>.5&&a<2.6)continue;cl.push([ccx+Math.cos(a)*rx*.92,ccy+Math.sin(a)*ry*.95,h*(.055+r()*.04)])}
 const vis=cl.filter(([x,y])=>!(o.zone&&SC_ZONE(x,y)));
 scBlur(c,6,g=>{g.globalAlpha=.75;g.fillStyle=pal.X;for(const[x,y,R]of vis){g.beginPath();g.ellipse(x+R*.1,y+R*.25,R*1.05,R*.9,0,0,7);g.fill()}});
 const ly=night?.5:-.45,lx=night?0:-.35;scBlur(c,2.5,g=>{for(const[x,y,R]of vis)scBlob(g,x,y,R,pal.L,pal.M,pal.D,lx,ly,.85)});
 // 葉：かたまりの外側ほど大きめで、ふちがギザギザに見える
 const per=Math.round((o.n||1300)/Math.max(1,cl.length));
 for(const[x,y,R]of vis){for(let i=0;i<per;i++){const a=r()*6.283,d=Math.pow(r(),.55)*R*1.15;const px=x+Math.cos(a)*d,py=y+Math.sin(a)*d*.85;if(o.zone&&SC_ZONE(px,py))continue;
  const gy=(py-ccy)/ry,gx=(px-ccx)/rx;const lit=night?Math.max(0,gy*.8+.2):Math.max(0,-(gy*.75+gx*.35));let col=pal.leaf[Math.floor(r()*pal.leaf.length)];
  col=lit>.25?xmMix(col,pal.L,Math.min(.6,.5*lit)):xmMix(col,pal.X,.4*(1-lit)*Math.min(1,d/R));c.fillStyle=col;c.globalAlpha=.92;mjLeaf(c,px,py,h*(.015+r()*.012)*(d>R*.8?1.3:1),r()*6.3)}}
 c.globalAlpha=1;
 if(L&&night&&!o.noLight){for(let i=0;i<4;i++)L.push({x:ccx+(r()-.5)*rx*1.4,y:ccy+ry*(.3+r()*.4),r:h*.18,c:'255,120,60',a:.08,p:r()*6,sp:.3,soft:1});L.push({x:cx,y:by-6,rx:w*.55,ry:h*.05,c:'255,150,80',a:.35,p:0,sp:0,soft:1,ell:1})}
 return cl}
// 奥の山のもみじ：小さな木のかたまりを何列も（遠いほど霞む）
function mjForest(c,y0,y1,mode,seed,haze,L){const r=XR(seed);const night=mode==2;
 const P=mode==0?['#d2552e','#e8823a','#c23a24','#f0a844','#b8452a','#de6a30']:mode==1?['#b83222','#d4502a','#9a2618','#ea7a34','#c4402a','#a83020']:['#5a140e','#7a2014','#9a3018','#3a0c0a','#6a1c12','#802416'];
 const EG=night?'#0a0e0c':mode==1?'#4a5040':'#56704e';
 for(let row=0;row<4;row++){const k=row/3,y=y0+(y1-y0)*k*.85,R=14+row*11,hz=(1-k)*(haze==null?.5:haze);const sky=mode==0?'#dfe6e8':'#efd8c0';
  // 杉の木（ところどころ）
  for(let x=r()*200;x<XW;x+=160+r()*260){const hh=R*3.2;c.fillStyle=night?EG:xmMix(EG,sky,hz);c.beginPath();c.moveTo(x,y-hh);c.lineTo(x+R*.9,y+R*.4);c.lineTo(x-R*.9,y+R*.4);c.closePath();c.fill()}
  scBlur(c,row<2?2.4:1.2,g=>{
  for(let x=-30;x<XW+40;x+=R*(.55+r()*.35)){const yy=y+(r()-.5)*R*.9+Math.sin(x*.012+row*2)*12;const base=P[Math.floor(r()*P.length)];
   const col=night?base:xmMix(base,sky,hz);const RR=R*(.75+r()*.6);
   scBlob(g,x,yy,RR,xmMix(col,night?'#ff9a50':'#fff0c8',night?.18:.28),col,xmMix(col,'#000000',.28),night?0:-.3,night?.5:-.4,.96)}
});
  if(row>=1){const nl=row*260;for(let i=0;i<nl;i++){const x=r()*XW,yy=y+(r()-.5)*R*1.6+Math.sin(x*.012+row*2)*12;const col=night?P[i%P.length]:xmMix(P[i%P.length],sky,hz*.8);c.fillStyle=xmMix(col,i%3?'#ffd890':'#3a0c08',night?.1:.22);c.globalAlpha=.8;mjLeaf(c,x,yy,3+row*1.6,r()*6)}c.globalAlpha=1}
  if(night&&L&&row>=1)for(let x=40;x<XW;x+=140+r()*80)L.push({x,y:y+R*.6,r:R*3.4,c:'255,120,60',a:.08+row*.025,p:r()*6,sp:.3,soft:1})}}
// 楼門（本格版）：組物・瓦の線・額・金具
function mjGate2(c,cx,by,w,mode,L){const night=mode==2,h=w*.95;const ver=night?'#5a1a14':'#c8402e',verD=night?'#3a0e0a':'#8e2a1e',roof=night?'#0e0d12':'#34323a',wall=night?'#3a3236':'#f2ece0';
 const st=by-h*.06;
 wash(c,g=>wob(g,[[cx-w*.58,st],[cx+w*.58,st],[cx+w*.62,by],[cx-w*.62,by]],1.2,3),night?'#2a2628':'#a49e92',{edge:.3,gr:.3});
 for(let i=0;i<3;i++){c.fillStyle=night?'#1a1618':'#8a847a';c.fillRect(cx-w*.58+i*4,st+i*(by-st)/3,w*1.16-i*8,1.5)}
 for(const k of[-.42,-.14,.14,.42]){const x=cx+w*k;wash(c,g=>wob(g,[[x-w*.032,st-h*.42],[x+w*.032,st-h*.42],[x+w*.032,st],[x-w*.032,st]],.6,7),ver,{edge:.45,gr:.25});
  c.fillStyle=verD;c.globalAlpha=.5;c.fillRect(x+w*.012,st-h*.42,w*.02,h*.42);c.globalAlpha=1;c.fillStyle=night?'#222':'#2a2622';c.fillRect(x-w*.038,st-h*.03,w*.076,h*.03)}
 // 中の扉の暗がり
 c.fillStyle=night?'rgba(10,6,6,.7)':'rgba(60,30,24,.5)';c.fillRect(cx-w*.11,st-h*.38,w*.22,h*.38);
 // 貫と組物
 const beam=(y,ww,hh)=>wash(c,g=>wob(g,[[cx-ww,y],[cx+ww,y],[cx+ww,y+hh],[cx-ww,y+hh]],.6,9),ver,{edge:.4});
 beam(st-h*.46,w*.48,h*.04);beam(st-h*.36,w*.46,h*.02);
 c.fillStyle=night?'#2a2420':'#e8d8b0';for(let i=-8;i<=8;i++){const x=cx+i*w*.055;c.fillRect(x-4,st-h*.5,8,h*.04);c.fillStyle=verD;c.fillRect(x-6,st-h*.515,12,4);c.fillStyle=night?'#2a2420':'#e8d8b0'}
 const roofShape=(y,ww,hh)=>{wash(c,g=>{g.moveTo(cx-ww*.64,y+hh*.05);g.quadraticCurveTo(cx-ww*.5,y-hh*.2,cx-ww*.36,y-hh);g.lineTo(cx+ww*.36,y-hh);g.quadraticCurveTo(cx+ww*.5,y-hh*.2,cx+ww*.64,y+hh*.05);g.quadraticCurveTo(cx,y-hh*.12,cx-ww*.64,y+hh*.05)},roof,{edge:.5,gr:.35,ec:'#000000'});
  c.strokeStyle=night?'rgba(255,255,255,.05)':'rgba(255,255,255,.14)';c.lineWidth=1.4;for(let i=-24;i<=24;i++){const x=cx+i*ww*.026;c.beginPath();c.moveTo(x*1,y-hh*.95);c.lineTo(cx+(x-cx)*1.32,y-hh*.06+Math.abs(x-cx)/ww*-hh*.1);c.stroke()}
  c.fillStyle=night?'#1a1820':'#4a4850';c.fillRect(cx-ww*.37,y-hh*1.06,ww*.74,hh*.1);
  c.fillStyle='#c9a24e';for(const s of[-1,1]){c.beginPath();c.arc(cx+s*ww*.63,y+hh*.02,4,0,7);c.fill()}};
 roofShape(st-h*.46,w*1.06,h*.16);
 wash(c,g=>wob(g,[[cx-w*.35,st-h*.8],[cx+w*.35,st-h*.8],[cx+w*.35,st-h*.58],[cx-w*.35,st-h*.58]],1,11),wall,{edge:.4,gr:.25});
 for(const k of[-.34,-.12,.12,.34]){c.fillStyle=ver;c.fillRect(cx+w*k-w*.018,st-h*.8,w*.036,h*.22)}
 c.strokeStyle=ver;c.lineWidth=2;for(let i=0;i<6;i++){c.beginPath();c.moveTo(cx-w*.35,st-h*.6-i*3);c.lineTo(cx+w*.35,st-h*.6-i*3);c.stroke()}
 // 額
 c.fillStyle=night?'#1a1410':'#2a2018';c.fillRect(cx-w*.06,st-h*.76,w*.12,h*.1);c.strokeStyle='#c9a24e';c.lineWidth=2;c.strokeRect(cx-w*.06,st-h*.76,w*.12,h*.1);
 c.fillStyle='#d9b45a';for(let i=0;i<3;i++)c.fillRect(cx-3,st-h*.74+i*h*.028,6,h*.016);
 roofShape(st-h*.78,w*.92,h*.21);
 // 屋根の上の飾り
 c.fillStyle=night?'#0a0a0e':'#2a282e';c.fillRect(cx-w*.33,st-h*1.0,w*.66,h*.03);
 if(L){if(night){L.push({x:cx,y:st-h*.25,r:w*.8,c:'255,160,90',a:.3,p:0,sp:.2,soft:1});L.push({x:cx,y:st-h*.62,r:w*.5,c:'255,170,100',a:.25,p:1,sp:.2,soft:1})}
  for(const k of[-.28,.28]){L.push({x:cx+w*k,y:st-h*.4,r:night?30:14,c:'255,190,110',a:night?.9:.25,p:k*9,sp:2.4,dot:night?2.2:0})}}
 // 吊り灯籠
 for(const k of[-.28,.28]){const x=cx+w*k,y=st-h*.42;c.strokeStyle=night?'#222':'#3a3028';c.lineWidth=1.5;c.beginPath();c.moveTo(x,y-h*.04);c.lineTo(x,y-8);c.stroke();c.fillStyle=night?'#ffd08a':'#c9a24e';c.fillRect(x-6,y-8,12,14);c.fillStyle=night?'#3a2a18':'#5a4020';c.fillRect(x-8,y-10,16,3)}}
// 小川（映り込みつき）：B の今の絵を上下反転して水に映す
function mjStream2(c,cv,y0,y1,mode,extra){const top=(x)=>y0+Math.sin(x*.008)*10,bot=(x)=>y1+Math.sin(x*.006+1)*14;
 const path=g=>{g.moveTo(-20,top(-20));for(let x=0;x<=XW+20;x+=20)g.lineTo(x,top(x));for(let x=XW+20;x>=-20;x-=20)g.lineTo(x,bot(x));g.closePath()};
 const snap=xmCanvas(XW,XH);snap.getContext('2d').drawImage(cv,0,0);
 const W=[['#8fb4b0','#5e8a86'],['#7a7c70','#4a5048'],['#0e1222','#06080f']][mode];
 c.save();c.beginPath();path(c);c.clip();const g=c.createLinearGradient(0,y0,0,y1);g.addColorStop(0,W[0]);g.addColorStop(1,W[1]);c.fillStyle=g;c.fillRect(0,y0-30,XW,y1-y0+60);
 c.globalAlpha=mode==2?.65:.5;c.filter='blur(3px)';c.translate(0,y0*2-6);c.scale(1,-1);c.drawImage(snap,0,0);if(extra)c.drawImage(extra,0,0);c.restore();
 // 水面のゆらぎ
 const r=XR(9);c.save();c.beginPath();path(c);c.clip();c.strokeStyle=mode==2?'rgba(255,170,110,.3)':'rgba(255,255,255,.5)';for(let i=0;i<70;i++){const x=r()*XW,y=y0+6+r()*(y1-y0),l=8+r()*44;c.lineWidth=.8+r();c.beginPath();c.moveTo(x,y);c.lineTo(x+l,y);c.stroke()}
 c.fillStyle='rgba(0,0,0,.18)';c.fillRect(0,y0-20,XW,14);c.restore();
 // 岸の石
 for(let x=-10;x<XW+20;x+=18+r()*46){const y=bot(x)+2+r()*8,R=6+r()*16;c.save();c.translate(x,y);c.scale(1+r()*.8,.55+r()*.25);scBlob(c,0,0,R,mode==2?'#3a3438':'#b8b0a0',mode==2?'#24202a':'#8a8276',mode==2?'#100c12':'#4a443a',-.3,-.5,.95);c.restore();if(mode<2&&r()<.5){c.fillStyle='rgba(90,110,60,.6)';c.beginPath();c.ellipse(x,y-R*.3,R*.7,R*.2,0,0,7);c.fill()}}
 return path}
function mjGround2(c,y0,mode){const P=[['#c8b896','#a08a62'],['#8a8a5a','#5e5a38'],['#1e1a20','#0c0a0e']][mode];
 wash(c,g=>wob(g,[[-20,y0],[XW+20,y0],[XW+20,XH+20],[-20,XH+20]],3,21),P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,XH);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.1,gr:.35,light:false});
 const r=XR(31);c.save();c.filter='blur(4px)';for(let i=0;i<40;i++){c.fillStyle=mode==2?'rgba(30,40,24,.35)':'rgba(84,104,56,.3)';c.beginPath();c.ellipse(r()*XW,y0+r()*(XH-y0),40+r()*90,8+r()*14,0,0,7);c.fill()}c.restore();
 scGrain(c,y0,XH,mode==2?['#2a2430','#100c14']:['#f0e6d0','#6a5a40','#8a7a5a'],2400,33,1.8);
 // 落ち葉のじゅうたん
 const pal=mode==2?['#6a160e','#8e2414','#4a0e0a','#a83a18']:['#c8402c','#e0662f','#ea8a34','#b3301f','#d4552d','#f0a040'];
 for(let i=0;i<1600;i++){const y=y0+6+Math.pow(r(),.6)*(XH-y0);const s=(3+r()*4)*(.6+(y-y0)/(XH-y0)*1.2);c.fillStyle=pal[i%pal.length];c.globalAlpha=.75+r()*.25;mjLeaf(c,r()*XW,y,s,r()*6.3)}c.globalAlpha=1}
function mjBench2(c,x,by,w,mode,L){const night=mode==2;const ux=x+w*.66,uy=by-w*1.2;
 // 野点傘：骨と和紙の透け
 c.strokeStyle=night?'#1a1010':'#5a3a26';c.lineWidth=5;c.beginPath();c.moveTo(ux,uy-w*.04);c.lineTo(ux-w*.06,by+4);c.stroke();
 const rim=(g)=>{g.moveTo(ux-w*.8,uy+w*.3);g.quadraticCurveTo(ux-w*.4,uy-w*.04,ux,uy-w*.1);g.quadraticCurveTo(ux+w*.4,uy-w*.04,ux+w*.8,uy+w*.3);g.quadraticCurveTo(ux,uy+w*.17,ux-w*.8,uy+w*.3)};
 wash(c,rim,night?'#7a1c12':'#cc2e26',{grad:g=>{const q=g.createLinearGradient(ux-w*.8,0,ux+w*.8,0);q.addColorStop(0,night?'#5a140e':'#e04a36');q.addColorStop(.5,night?'#a0281a':'#d23a2c');q.addColorStop(1,night?'#4a100a':'#a8241c');return q},edge:.5,gr:.25});
 c.strokeStyle=night?'rgba(255,190,140,.25)':'rgba(255,236,220,.5)';c.lineWidth=1.1;for(let i=-7;i<=7;i++){c.beginPath();c.moveTo(ux,uy-w*.09);c.quadraticCurveTo(ux+i*w*.07,uy+w*.02,ux+i*w*.112,uy+w*.24+Math.abs(i)*w*.006);c.stroke()}
 c.fillStyle=night?'#2a1a10':'#f4e6c8';c.beginPath();c.arc(ux,uy-w*.1,w*.025,0,7);c.fill();
 // 縁台と毛氈
 wash(c,g=>wob(g,[[x-w*.05,by-w*.32],[x+w*1.05,by-w*.32],[x+w*1.08,by-w*.22],[x-w*.08,by-w*.22]],.8,4),night?'#6a1610':'#c42a20',{edge:.4,gr:.3});
 c.fillStyle=night?'#3a0c08':'#8e1c16';c.fillRect(x-w*.08,by-w*.22,w*1.16,w*.05);
 c.strokeStyle=night?'#1a1010':'#4a3022';c.lineWidth=4;for(const k of[.04,.96]){c.beginPath();c.moveTo(x+w*k,by-w*.18);c.lineTo(x+w*k,by);c.stroke()}
 // お盆：抹茶と和菓子
 c.fillStyle='#3a2a1e';c.beginPath();c.ellipse(x+w*.38,by-w*.33,w*.16,w*.035,0,0,7);c.fill();
 c.fillStyle='#e8dcc4';c.beginPath();c.ellipse(x+w*.3,by-w*.36,w*.055,w*.04,0,0,Math.PI);c.fill();c.fillStyle='#5a8a3a';c.beginPath();c.ellipse(x+w*.3,by-w*.37,w*.05,w*.012,0,0,7);c.fill();
 c.fillStyle='#f4ead8';c.beginPath();c.ellipse(x+w*.46,by-w*.35,w*.05,w*.016,0,0,7);c.fill();c.fillStyle='#e8909a';c.beginPath();c.arc(x+w*.45,by-w*.375,w*.022,0,7);c.fill();c.fillStyle='#f6c0c4';c.beginPath();c.arc(x+w*.47,by-w*.378,w*.018,0,7);c.fill();
 if(L)L.push({x:ux,y:uy+w*.25,r:w*.7,c:night?'255,120,70':'255,150,110',a:night?.35:.12,p:0,sp:.3,soft:1})}
function mjBuild(mode){const B=xmLayer(),T=xmLayer(),F=xmLayer();const c=B.c,L=B.L;
 if(mode==0){scSky(c,['#9ec4dc','#d6e4e6','#f4e8d0'],820);scClouds(c,4,8,120,560,'#ffffff',.55);
  c.save();c.globalCompositeOperation='screen';glow(c,330,560,520,'255,226,180',.45);c.restore();
  wash(c,g=>{g.moveTo(-20,760);g.bezierCurveTo(200,690,420,720,600,700);g.bezierCurveTo(760,690,860,720,XW+20,705);g.lineTo(XW+20,860);g.lineTo(-20,860);g.closePath()},'#9aa8b0',{edge:.1,gr:.25,light:false,a:.6});
  mjForest(c,730,930,0,5,.55,L);scFog(c,760,40,'240,236,228',.35);
  mjGround2(c,940,0);
  // 参道
  wash(c,g=>{g.moveTo(330,960);g.lineTo(430,960);g.lineTo(640,XH+10);g.lineTo(120,XH+10);g.closePath()},'#ddd4c0',{grad:g=>{const q=g.createLinearGradient(0,960,0,XH);q.addColorStop(0,'#e6dfcc');q.addColorStop(1,'#c8bea6');return q},edge:.2,gr:.4,light:false});
  {const r=XR(44);c.strokeStyle='rgba(120,100,70,.35)';c.lineWidth=1.2;for(let y=980;y<XH;y+=14+(y-960)*.05){const k=(y-960)/(XH-960),x0=330-210*k,x1=430+210*k;c.beginPath();c.moveTo(x0,y);c.lineTo(x1,y);c.stroke();for(let x=x0+r()*30;x<x1;x+=30+k*40){c.beginPath();c.moveTo(x,y);c.lineTo(x,y+12+k*20);c.stroke()}}
   for(let i=0;i<120;i++){const y=960+Math.pow(r(),.7)*(XH-960),k=(y-960)/(XH-960),x=330-210*k+r()*(100+420*k);c.fillStyle=['#c8402c','#e0662f','#ea8a34'][i%3];c.globalAlpha=.85;mjLeaf(c,x,y,4+k*6,r()*6)}c.globalAlpha=1}
  mjTree(c,40,1020,640,0,11,L,{n:1500,wide:.95,lean:.12,zone:1});mjTree(c,880,1010,320,0,12,L,{n:600,wide:.9,zone:1});
  mjGate2(T.c,380,1000,400,0,T.L);T.ax=380;T.ay=1000;T.d=.1;
  mjLantern(F.c,150,1190,150,0,F.L);mjLantern(F.c,650,1190,150,0,F.L);
  mjTree(F.c,-120,1560,560,0,21,F.L,{n:900,wide:.7,lean:.3});mjTree(F.c,1060,1580,500,0,22,F.L,{n:800,wide:.7,lean:-.3});
  xmPerson(F.c,352,1110,64,'#5a4a5e',0,51,0);xmPerson(F.c,404,1116,60,'#6a5a3a',0,52,1);
  xmPerson(F.c,300,1250,104,'#4a4a5e',0,31,0);xmPerson(F.c,336,1256,96,'#7a4a3a',0,32,1);xmPerson(F.c,500,1290,112,'#8a5a4a',0,34,0);xmPerson(F.c,534,1298,80,'#e2b84a',0,35,2);
  F.ax=420;F.ay=1290;F.d=.4;
 }else{const n=mode==2;
  if(n){scSky(c,['#04060f','#0b1022','#1e1530'],820);xmStars(c,9);xmMoon(c,190,210,42)}
  else{scSky(c,['#e8c6a0','#f4dcc0','#f6e6cc'],760);scClouds(c,7,6,160,520,'#fff4e4',.5);c.save();c.globalCompositeOperation='screen';glow(c,700,420,560,'255,214,160',.5);c.restore()}
  wash(c,g=>{g.moveTo(-20,740);g.bezierCurveTo(240,660,480,700,700,672);g.bezierCurveTo(820,660,880,690,XW+20,690);g.lineTo(XW+20,880);g.lineTo(-20,880);g.closePath()},n?'#120e1a':'#b8a088',{edge:.1,gr:.25,light:false,a:n?.9:.55});
  mjForest(c,710,900,mode,6,n?0:.4,L);if(!n)scFog(c,730,40,'250,232,210',.4);else scFog(c,900,50,'255,110,60',.12);
  mjGround2(c,880,mode);
  // 橋の映り込み用に、橋だけを先に描く
  const br=xmCanvas(XW,XH),bc=br.getContext('2d');mjBridge(bc,200,760,1000,72,mode,null);
  mjStream2(c,B.cv,960,1080,mode,br);
  if(n){L.push({x:460,y:1020,rx:520,ry:60,c:'255,120,60',a:.25,p:0,sp:0,soft:1,ell:1})}
  mjTree(c,70,960,720,mode,41,L,{n:1900,wide:.82,lean:.12,zone:1});
  mjBridge(T.c,200,760,1000,72,mode,T.L);T.ax=480;T.ay=1000;T.d=.1;
  if(n){mjLantern(F.c,110,1250,130,2,F.L);mjLantern(F.c,700,1300,120,2,F.L);for(const l of F.L){l.r*=.55;l.a*=.75}
   xmPerson(F.c,380,1300,112,'#3a3a4a',2,38,0);xmPerson(F.c,414,1306,100,'#4a2a30',2,39,1);xmPerson(F.c,520,1330,90,'#2a3a4a',2,40,0);}
  else{mjBench2(F.c,480,1310,330,1,F.L);xmPerson(F.c,430,1312,118,'#5a5a6e',1,36,0);xmPerson(F.c,330,1300,110,'#7a4a3a',1,37,1)}
  mjTree(F.c,-140,1600,620,mode,45,F.L,{n:900,wide:.7,lean:.35,noLight:1});F.ax=520;F.ay=1300;F.d=.4;
 }
 return scFinish(mode,B,T,F,[940,880,880][mode])}

// ---------- 白良浜（本格版） ----------
const HM_SHORE=x=>1000-x*.06+Math.sin(x*.007)*16;
function hmIsland2(c,cx,by,w,mode,sunHole){const night=mode==2;const tc=xmCanvas(XW,XH),t=tc.getContext('2d');
 const col=night?'#010207':mode==1?'#2e1c2a':'#8a8270';
 wash(t,g=>wob(g,[[cx-w*.56,by],[cx-w*.5,by-w*.22],[cx-w*.44,by-w*.4],[cx-w*.3,by-w*.5],[cx-w*.12,by-w*.58],[cx+w*.06,by-w*.66],[cx+w*.2,by-w*.62],[cx+w*.32,by-w*.5],[cx+w*.4,by-w*.36],[cx+w*.5,by-w*.2],[cx+w*.6,by-w*.06],[cx+w*.66,by]],4,13),col,{edge:.35,gr:night?0:mode==1?.2:.4,light:!night,a:night?1:.92});
 // 地層の線と光の当たる面
 const r=XR(5);t.save();t.globalCompositeOperation='source-atop';t.strokeStyle=night?'rgba(120,130,200,.12)':mode==1?'rgba(255,170,120,.18)':'rgba(60,50,40,.3)';t.lineWidth=2;
 for(let i=0;i<26;i++){const x=cx-w*.5+r()*w,y=by-r()*w*.55;t.lineWidth=1+r()*2;t.beginPath();t.moveTo(x,y);t.lineTo(x+(r()-.5)*10,y+10+r()*30);t.stroke()}for(let i=0;i<5;i++){const y=by-w*.08-i*w*.1;t.lineWidth=1.4;t.beginPath();t.moveTo(cx-w*.6,y+r()*10);t.bezierCurveTo(cx-w*.2,y-14*r(),cx+w*.2,y+14*r(),cx+w*.6,y-r()*10);t.stroke()}
 const lg=t.createLinearGradient(cx-w*.5,0,cx+w*.5,0);lg.addColorStop(0,mode==0?'rgba(255,250,230,.25)':'rgba(0,0,0,0)');lg.addColorStop(1,mode==1?'rgba(255,150,100,.0)':'rgba(0,0,0,.25)');t.fillStyle=lg;t.fillRect(0,0,XW,XH);t.restore();
 // 上の木
 const G=night?['#04060a','#0a0e14']:mode==1?['#1c121a','#2a1a22']:['#3e5e3e','#4e7046','#2e4a32'];
 for(let i=0;i<70;i++){const x=cx-w*.36+r()*w*.7,y=by-w*.6+Math.abs(x-cx)*.3-r()*16;t.fillStyle=G[i%G.length];t.beginPath();t.arc(x,y,4+r()*8,0,7);t.fill()}
 // 円い穴
 t.globalCompositeOperation='destination-out';t.beginPath();t.ellipse(cx,by-w*.13,w*.14,w*.17,0,0,7);t.fill();t.globalCompositeOperation='source-over';
 t.strokeStyle=night?'rgba(0,0,0,.5)':'rgba(30,20,20,.4)';t.lineWidth=3;t.beginPath();t.ellipse(cx,by-w*.13,w*.14,w*.17,0,0,7);t.stroke();
 c.drawImage(tc,0,0)}
function hmPalm(c,x,by,h,mode,seed,lean){const r=XR(seed);const night=mode==2;const tr=night?'#0c0a10':mode==1?'#2a1a20':'#7a6048';
 const tx=x+lean*h,ty=by-h;const pts=[];for(let i=0;i<=24;i++){const u=i/24;pts.push([x+(tx-x)*u+Math.sin(u*Math.PI)*lean*h*.3,by+(ty-by)*u])}
 for(let i=0;i<24;i++){const[a0,b0]=pts[i],[a1,b1]=pts[i+1];const wd=h*(.05-.022*i/24);c.strokeStyle=tr;c.lineWidth=wd;c.beginPath();c.moveTo(a0,b0);c.lineTo(a1,b1+1);c.stroke();
  c.strokeStyle=night?'rgba(255,255,255,.04)':'rgba(30,20,10,.35)';c.lineWidth=1.2;c.beginPath();c.moveTo(a0-wd/2,b0);c.lineTo(a0+wd/2,b0-2);c.stroke()}
 const G=night?['#05080a','#0a1012','#0e1416']:mode==1?['#160f14','#22161c','#2c1c24']:['#24503a','#2e6444','#3e7a4e','#4e8c58','#5e9a62'];
 const fr=[];for(let k=0;k<15;k++){const a=-Math.PI/2+(k-7)*.27+(r()-.5)*.12;fr.push([a,h*(.3+r()*.12),.6+r()*.7])}fr.sort((p,q)=>Math.abs(q[0]+Math.PI/2)-Math.abs(p[0]+Math.PI/2));
 for(const[a,len,droop]of fr){const ex=tx+Math.cos(a)*len,ey=ty+Math.sin(a)*len*.5+len*droop*.5,mx=tx+Math.cos(a)*len*.55,my=ty+Math.sin(a)*len*.55-len*.08;
  const bez=u=>[(1-u)*(1-u)*tx+2*(1-u)*u*mx+u*u*ex,(1-u)*(1-u)*ty+2*(1-u)*u*my+u*u*ey];
  for(let i=2;i<=26;i++){const u=i/27;const[px,py]=bez(u),[qx,qy]=bez(u+.03);const dx=qx-px,dy=qy-py,dl=Math.hypot(dx,dy)||1;const nx=-dy/dl,ny=dx/dl;
   const ll=len*.26*Math.sin(Math.PI*Math.min(1,u*1.05))*(1-u*.25);
   for(const sd of[-1,1]){const tx2=px+(nx*sd*.55+dx/dl*.5)*ll,ty2=py+(ny*sd*.55+dy/dl*.5)*ll+ll*.55;c.fillStyle=G[(i+(sd>0?2:0)+Math.floor(r()*2))%G.length];
    c.beginPath();c.moveTo(px,py);c.quadraticCurveTo((px+tx2)/2+nx*sd*3,(py+ty2)/2-2,tx2,ty2);c.lineTo(qx,qy);c.closePath();c.fill()}}
  c.strokeStyle=night?'#0e1416':mode==1?'#2a1c22':'#2e5a3a';c.lineWidth=2.6;c.beginPath();c.moveTo(tx,ty);c.quadraticCurveTo(mx,my,ex,ey);c.stroke()}
 c.fillStyle=night?'#100c08':'#6a4a2a';for(let i=0;i<5;i++){c.beginPath();c.arc(tx+(r()-.5)*14,ty+8+r()*8,5,0,7);c.fill()}}
function hmHill(c,mode,L){const night=mode==2;const r=XR(17);
 wash(c,g=>{g.moveTo(470,800);g.bezierCurveTo(540,730,640,712,740,716);g.bezierCurveTo(820,718,880,700,XW+20,708);g.lineTo(XW+20,802);g.closePath()},night?'#0a0e16':mode==1?'#3a2a3a':'#5e7a5a',{edge:.2,gr:.35,light:false});
 for(let i=0;i<160;i++){const x=480+r()*450,y=716+r()*80;if(y<800-(x<540?(x-470)*1.1:90))continue;c.fillStyle=night?'#060a10':mode==1?['#2a1e2a','#3e2e3a'][i%2]:['#4a6a4a','#6a8a62','#3e5a40'][i%3];c.beginPath();c.arc(x,y,4+r()*6,0,7);c.fill()}
 for(let i=0;i<9;i++){const x=520+i*44+r()*12,w=30+r()*30,h=34+r()*44,y=796-r()*30;if(y-h<690)continue;
  wash(c,g=>wob(g,[[x,y-h],[x+w,y-h],[x+w,y],[x,y]],.8,i),night?'#1a1e30':mode==1?'#c09a9a':'#f0ece4',{edge:.3,gr:.15,light:false});
  c.fillStyle=night?'#12141e':mode==1?'#8a6a70':'#c8c2b6';c.fillRect(x+w*.7,y-h,w*.3,h);
  for(let yy=y-h+5;yy<y-4;yy+=6)for(let xx=x+3;xx<x+w-3;xx+=5){const lit=night?r()<.55:mode==1&&r()<.12;c.fillStyle=lit?'#ffd590':night?'#22263a':'rgba(80,100,130,.45)';c.fillRect(xx,yy,2.6,3);if(lit&&L&&r()<.05)L.push({x:xx,y:yy,r:12,c:'255,200,130',a:.45,p:r()*6,sp:.4,soft:1})}}}
function hmSea2(c,y0,mode){const y1=1060;const P=[['#4a86b0','#5cb4c4','#8ad8d0'],['#6a4a7a','#b06a80','#d89a8a'],['#0c1230','#121a3a','#1a2244']][mode];
 const g=c.createLinearGradient(0,y0,0,y1);g.addColorStop(0,P[0]);g.addColorStop(.6,P[1]);g.addColorStop(1,P[2]);c.fillStyle=g;c.fillRect(0,y0,XW,y1-y0);
 c.save();c.globalCompositeOperation='multiply';c.globalAlpha=.08;c.drawImage(xmNoise(),0,0);c.restore();
 const r=XR(4);for(let i=0;i<220;i++){const y=y0+3+Math.pow(r(),1.4)*(y1-y0),k=(y-y0)/(y1-y0),x=r()*XW,l=(6+r()*30)*(.4+k*1.4);c.strokeStyle=mode==2?`rgba(160,180,255,${.06+r()*.12})`:`rgba(255,255,255,${.18+r()*.4})`;c.lineWidth=.7+k*1.4;c.beginPath();c.moveTo(x,y);c.lineTo(x+l,y);c.stroke()}
 c.fillStyle=mode==2?'rgba(140,160,255,.25)':'rgba(255,255,255,.55)';c.fillRect(0,y0,XW,1.5)}
function hmSand2(c,mode){const P=[['#fbf6ea','#efe4cc'],['#f0cdb6','#c8a08e'],['#22223a','#121222']][mode];
 const path=g=>{g.moveTo(-20,HM_SHORE(-20));for(let x=0;x<=XW+20;x+=20)g.lineTo(x,HM_SHORE(x));g.lineTo(XW+20,XH+20);g.lineTo(-20,XH+20);g.closePath()};
 wash(c,path,P[0],{grad:g=>{const q=g.createLinearGradient(0,940,0,XH);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.1,gr:.2,light:false});
 // 濡れた砂と泡
 c.save();c.beginPath();path(c);c.clip();const wg=c.createLinearGradient(0,940,0,1080);wg.addColorStop(0,mode==2?'rgba(40,50,90,.6)':mode==1?'rgba(170,110,120,.5)':'rgba(170,190,190,.55)');wg.addColorStop(1,'rgba(0,0,0,0)');
 c.fillStyle=wg;c.beginPath();for(let x=-20;x<=XW+20;x+=20)c.lineTo(x,HM_SHORE(x));for(let x=XW+20;x>=-20;x-=20)c.lineTo(x,HM_SHORE(x)+30+Math.sin(x*.02)*6);c.fill();c.restore();
 for(const[off,a,lw]of[[0,.95,4],[-9,.5,2],[-20,.3,1.4]]){c.strokeStyle=mode==2?`rgba(170,190,255,${a*.35})`:`rgba(255,255,255,${a})`;c.lineWidth=lw;c.beginPath();for(let x=-20;x<=XW+20;x+=10)c.lineTo(x,HM_SHORE(x)+off+Math.sin(x*.05+off)*2);c.stroke()}
 scGrain(c,960,XH,mode==2?['#3a3a5a','#0a0a16']:['#ffffff','#c8b898','#e0d0b0'],3200,61,1.6);
 // 足あと
 const r=XR(62);c.fillStyle=mode==2?'rgba(0,0,0,.25)':'rgba(150,120,90,.25)';for(let i=0;i<22;i++){const u=i/22,x=200+u*480+Math.sin(u*6)*30+(i%2?8:-8),y=XH-20-u*240;const s=1-u*.6;c.beginPath();c.ellipse(x,y,5*s,8*s,.2,0,7);c.fill()}}
const HM_STR=[];for(let k=0;k<3;k++)for(let x=24;x<XW;x+=26)HM_STR.push({x,y:HM_SHORE(x)+56+k*72+Math.sin(x*.012+k*1.7)*16,k});
function hmBuild(mode){const B=xmLayer(),T=xmLayer(),F=xmLayer();const c=B.c,L=B.L;
 if(mode==0){scSky(c,['#6eaad6','#b4d6ea','#eef4f0'],800);scClouds(c,6,9,420,720,'#ffffff',.65);scClouds(c,7,4,140,300,'#ffffff',.35);
  xmGulls(c,6,5);hmSea2(c,800,0);hmHill(c,0,L);hmIsland2(c,180,812,180,0);
  hmSand2(c,0);
  hmPalm(T.c,110,1240,640,0,3,.1);hmPalm(T.c,250,1200,520,0,4,-.05);T.ax=180;T.ay=1220;T.d=.1;
  xmPerson(F.c,560,1250,104,'#3e5a7e',0,31,0);xmPerson(F.c,596,1256,96,'#c08a5a',0,32,1);xmPerson(F.c,630,1262,72,'#e2b84a',0,33,2);xmPerson(F.c,760,1100,60,'#8a4a4a',0,34,0);F.ax=600;F.ay=1260;F.d=.4;
 }else if(mode==1){scSky(c,['#2a2c64','#6a4a86','#d47a7a','#f6b07a','#fadc9c'],800);
  {const r=XR(12);c.save();c.filter='blur(6px)';for(let i=0;i<14;i++){const y=300+r()*420,x=r()*XW,w=160+r()*300;const g=c.createLinearGradient(0,y-8,0,y+8);g.addColorStop(0,'rgba(255,200,150,.55)');g.addColorStop(1,'rgba(120,60,100,.45)');c.fillStyle=g;c.beginPath();c.ellipse(x,y,w,6+r()*8,0,0,7);c.fill()}c.restore()}
  c.save();c.globalCompositeOperation='screen';glow(c,250,805,520,'255,190,120',.75);c.restore();
  c.fillStyle='#fff2cc';c.beginPath();c.arc(250,806,40,Math.PI,0);c.fill();
  hmSea2(c,806,1);hmHill(c,1,L);
  c.save();c.globalCompositeOperation='lighter';{const r=XR(8);for(let i=0;i<140;i++){const y=812+r()*240,x=250+(r()-.5)*(30+(y-806)*1.1);c.fillStyle=`rgba(255,200,120,${.15+r()*.45})`;c.fillRect(x,y,6+r()*26,1.6+(y-806)*.01)}}c.restore();
  hmSand2(c,1);
  hmIsland2(T.c,250,880,250,1);T.ax=250;T.ay=880;T.d=.05;
  L.push({x:250,y:806,r:200,c:'255,200,140',a:.5,p:0,sp:0,soft:1});
  hmPalm(F.c,830,1320,640,1,3,-.08);xmPerson(F.c,520,1290,118,'#3a3a5a',1,36,0);xmPerson(F.c,556,1296,104,'#6a3a3a',1,37,1);F.ax=650;F.ay=1300;F.d=.4;
 }else{scSky(c,['#03040c','#0a0d22','#1a1c3a'],800);xmStars(c,9);xmMoon(c,190,200,40);
  hmSea2(c,800,2);hmHill(c,2,L);hmIsland2(c,180,812,180,2);
  hmSand2(c,2);
  const cols=['255,110,170','110,190,255','255,210,110','170,130,255','120,255,200'];
  for(const s of HM_STR)L.push({x:s.x,y:s.y,r:18,c:cols[(s.k*2+Math.floor(s.x/120))%5],a:.35,p:s.x*.05,sp:1.5,dot:1.4});
  L.push({x:460,y:1120,rx:540,ry:150,c:'150,140,255',a:.22,p:0,sp:0,soft:1,ell:1});
  hmPalm(T.c,110,1240,620,2,3,.1);hmPalm(T.c,830,1230,560,2,4,-.08);T.ax=460;T.ay=1230;T.d=.1;
  const ppl=[[300,1330,110,0],[334,1336,98,1],[362,1342,72,2],[560,1340,112,1],[596,1346,100,0],[700,1320,96,0]];ppl.forEach((p,i)=>xmPerson(F.c,p[0],p[1],p[2],['#2a2a3a','#3a2228','#2a3a4a'][i%3],2,70+i,p[3]));F.ax=460;F.ay=1340;F.d=.4;
 }
 return scFinish(mode,B,T,F,[1000,1000,1000][mode])}
function hmFx(c,mode,t,u){c.save();
 // 波の泡がゆっくり寄せる
 if(mode<2){const k=(t*.35)%1;c.strokeStyle=`rgba(255,255,255,${.6*Math.sin(Math.PI*k)})`;c.lineWidth=2.4;c.beginPath();for(let x=-20;x<=XW+20;x+=10)c.lineTo(x,HM_SHORE(x)-24+k*26+Math.sin(x*.04+t)*2);c.stroke()}
 if(mode==1&&typeof xmShoot=='function')xmShoot(c,u);
 if(mode==2){c.globalCompositeOperation='lighter';const cols=['255,110,170','110,190,255','255,210,110','170,130,255','120,255,200'];
  // 光が砂浜を波のように走る（音楽に合わせた光のパレード）
  for(const s of HM_STR){const b=Math.pow(Math.max(0,Math.cos(s.x*.011-t*3.4+s.k*1.2)),6);if(b<.03)continue;const col=cols[(s.k+Math.floor(t*.6+s.x/300))%5];glow(c,s.x,s.y,26,col,b*.75);c.fillStyle=`rgba(255,255,255,${b*.9})`;c.beginPath();c.arc(s.x,s.y,2.2,0,7);c.fill()}
  for(let k=0;k<6;k++){const a=-Math.PI/2+Math.sin(t*1.1+k*1.3)*.6,x=80+k*150,y=1060;c.save();c.filter='blur(10px)';const g=c.createLinearGradient(x,y,x+Math.cos(a)*720,y+Math.sin(a)*720);g.addColorStop(0,`rgba(${cols[k%5]},.32)`);g.addColorStop(1,`rgba(${cols[k%5]},0)`);c.fillStyle=g;c.beginPath();c.moveTo(x,y);c.lineTo(x+Math.cos(a-.05)*720,y+Math.sin(a-.05)*720);c.lineTo(x+Math.cos(a+.05)*720,y+Math.sin(a+.05)*720);c.closePath();c.fill();
   // 海に映る色
   c.filter='blur(6px)';c.fillStyle=`rgba(${cols[k%5]},.12)`;c.fillRect(x+Math.cos(a)*120-14,820,28,170);c.restore()}
  const r=XR(77);for(let i=0;i<24;i++){const T=4+r()*3,p=((t/T+r())%1),x=40+r()*840+Math.sin(t+i)*20,y=1100-p*(500+r()*250);glow(c,x,y,9+r()*9,cols[i%5],Math.sin(Math.PI*p)*.6)}}
 c.restore();c.globalAlpha=1}
