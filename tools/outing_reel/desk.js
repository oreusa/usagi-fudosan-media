// 11/16 絵本のまわり（机）を題材ごとに：もみじ＝木の机ともみじの葉、クリスマス＝もみの枝とオーナメント、浜＝流木の机と貝がら。
// owner「周りの星、種類ごとに変えてた背景の方が良いかも」「絵本の周りはお洒落に」。
// 本の後ろの2枚の絵：DKS＝動かない物（机・置いた物）、DKD＝動く物（舞う葉・雪・水の光）。本より後ろなので字にかからない。
// 見える範囲：カメラが寄るので x 26〜1054・y 43〜1876。本は 84,232 から 920×1380。字（上の題）は y 92〜150 のまん中。
const DK=['momiji','xmas','hama'].includes(P.scene)?P.scene:'';
function dkShadow(c,blur,dx,dy,a){c.shadowColor=`rgba(0,0,0,${a})`;c.shadowBlur=blur;c.shadowOffsetX=dx;c.shadowOffsetY=dy}
function dkNoShadow(c){c.shadowColor='rgba(0,0,0,0)';c.shadowBlur=0;c.shadowOffsetX=0;c.shadowOffsetY=0}
// 木目の板（横向き）
function dkWood(c,y0,y1,base,dark,lite,seed){const r=XR(seed);const g=c.createLinearGradient(0,y0,0,y1);g.addColorStop(0,lite);g.addColorStop(.5,base);g.addColorStop(1,dark);c.fillStyle=g;c.fillRect(0,y0,1080,y1-y0);
 c.save();c.beginPath();c.rect(0,y0,1080,y1-y0);c.clip();
 for(let i=0;i<70;i++){const y=y0+r()*(y1-y0),a=.04+r()*.09,w=.6+r()*2.2,f=.002+r()*.006,ph=r()*7,amp=2+r()*7;c.strokeStyle=r()<.5?`rgba(0,0,0,${a})`:`rgba(255,235,200,${a*.6})`;c.lineWidth=w;c.beginPath();
  for(let x=-10;x<=1090;x+=12){const yy=y+Math.sin(x*f+ph)*amp+Math.sin(x*f*3.1+ph*2)*amp*.3;x<0?c.moveTo(x,yy):c.lineTo(x,yy)}c.stroke()}
 // ふし
 for(let i=0;i<2;i++){const x=r()*1080,y=y0+(y1-y0)*(.2+r()*.6);for(let k=0;k<6;k++){c.strokeStyle=`rgba(0,0,0,${.12-k*.015})`;c.lineWidth=1.2;c.beginPath();c.ellipse(x,y,14+k*9,4+k*3.2,0,0,7);c.stroke()}}
 c.restore();c.fillStyle='rgba(0,0,0,.35)';c.fillRect(0,y1-2,1080,2);c.fillStyle='rgba(255,240,210,.08)';c.fillRect(0,y0,1080,1)}
// ---------- もみじ ----------
function dkMaple(c,x,y,s,rot,col,o){o=o||{};c.save();c.translate(x,y);c.rotate(rot);if(o.flip)c.scale(o.flip,1);
 const pts=[];for(let i=0;i<7;i++){const a=-Math.PI/2+(i-3)*.6,L=i==3?1:i==2||i==4?.92:i==1||i==5?.68:.42;
  for(let k=0;k<=6;k++){const u=k/6;const side=a-.24+.48*u;const tip=1-Math.abs(u-.5)*2;const rr=s*L*(.38+.62*Math.pow(tip,1.4))*(k%2&&k!=3?.9:1);pts.push([Math.cos(side)*rr,Math.sin(side)*rr])}}
 pts.push([s*.07,s*.2]);pts.push([-s*.07,s*.2]);
 if(o.shadow!==false)dkShadow(c,o.blur||10,4,7,o.sa||.42);
 const g=c.createRadialGradient(-s*.2,-s*.3,s*.05,0,0,s*1.05);g.addColorStop(0,col[0]);g.addColorStop(.55,col[1]);g.addColorStop(1,col[2]);c.fillStyle=g;
 c.beginPath();pts.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();c.fill();dkNoShadow(c);
 // 葉脈と柄
 c.strokeStyle='rgba(255,220,170,.38)';c.lineWidth=Math.max(.8,s*.025);c.beginPath();for(let i=0;i<7;i++){const a=-Math.PI/2+(i-3)*.6,L=i==3?1:i==2||i==4?.92:i==1||i==5?.68:.42;c.moveTo(0,s*.12);c.lineTo(Math.cos(a)*s*L*.86,Math.sin(a)*s*L*.86)}c.stroke();
 c.strokeStyle=col[2];c.lineWidth=Math.max(1.2,s*.05);c.lineCap='round';c.beginPath();c.moveTo(0,s*.12);c.quadraticCurveTo(s*.06,s*.5,s*.18,s*.78);c.stroke();
 c.restore()}
const DK_MCOL=[['#f7b24a','#e0662f','#a8301e'],['#f39a48','#d4452a','#8e2418'],['#ffd36a','#f0a030','#c0661a'],['#e8703a','#c63326','#7a1a12'],['#ff9e5e','#e05a2a','#9c2a18']];
function dkGinkgo(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);dkShadow(c,8,3,6,.35);const g=c.createLinearGradient(0,-s,0,0);g.addColorStop(0,'#ffe27a');g.addColorStop(1,'#e8b230');c.fillStyle=g;
 c.beginPath();c.moveTo(0,0);c.quadraticCurveTo(-s*.95,-s*.35,-s*.8,-s*.95);c.quadraticCurveTo(-s*.4,-s*1.08,-s*.04,-s*.86);c.lineTo(0,-s*.7);c.lineTo(s*.04,-s*.86);c.quadraticCurveTo(s*.4,-s*1.08,s*.8,-s*.95);c.quadraticCurveTo(s*.95,-s*.35,0,0);c.fill();dkNoShadow(c);
 c.strokeStyle='rgba(160,110,20,.35)';c.lineWidth=.8;for(let i=-4;i<=4;i++){c.beginPath();c.moveTo(0,-s*.02);c.lineTo(Math.sin(i*.17)*s*.9,-Math.cos(i*.17)*s*.92);c.stroke()}
 c.strokeStyle='#c99a30';c.lineWidth=2;c.beginPath();c.moveTo(0,0);c.lineTo(s*.05,s*.45);c.stroke();c.restore()}
function dkMomiji(c){
 // 机：濃い胡桃の木の板（3枚）
 dkWood(c,0,700,'#3e2618','#2a170d','#4a2e1c',11);dkWood(c,700,1350,'#3a2316','#26150c','#46291a',12);dkWood(c,1350,1920,'#3e2618','#28160c','#4a2e1c',13);
 // 窓からの夕方の光
 const L=c.createRadialGradient(140,120,40,200,300,1300);L.addColorStop(0,'rgba(255,190,120,.28)');L.addColorStop(1,'rgba(255,170,100,0)');c.fillStyle=L;c.fillRect(0,0,1080,1920);
 // 置いた葉（上の左右・下の左右。本の下にもぐる物もある）
 const r=XR(51);const put=(x,y,s,rot)=>{const k=Math.floor(r()*5);dkMaple(c,x,y,s,rot,DK_MCOL[k],{flip:r()<.5?-1:1})};
 put(70,90,70,-.5);put(170,48,46,.6);put(40,215,52,1.9);put(285,70,36,-1.2);
 dkGinkgo(c,215,175,40,2.4);
 put(1010,80,64,.4);put(905,52,42,-.8);put(1050,220,48,2.6);put(800,40,30,1.1);
 dkGinkgo(c,960,190,36,-2.2);
 put(60,1700,76,.3);put(170,1800,58,-.9);put(40,1860,46,2.2);put(300,1835,40,1.4);put(130,1640,44,-2.6);
 put(1000,1720,72,-.4);put(900,1830,54,.9);put(1050,1880,40,-2);put(770,1860,36,2.8);dkGinkgo(c,860,1690,40,.5);dkGinkgo(c,250,1720,34,-.6);
 // 小枝
 c.save();dkShadow(c,8,3,6,.4);c.strokeStyle='#4a2a16';c.lineWidth=5;c.lineCap='round';c.beginPath();c.moveTo(520,1900);c.quadraticCurveTo(600,1800,700,1770);c.moveTo(610,1808);c.quadraticCurveTo(640,1760,620,1720);c.stroke();c.restore();
 dkMaple(c,705,1760,40,.9,DK_MCOL[0],{});dkMaple(c,618,1712,34,-.3,DK_MCOL[3],{});dkMaple(c,560,1850,30,2.4,DK_MCOL[1],{})}
function dkMomijiFx(c,t){const r=XR(61);for(let i=0;i<9;i++){const x0=r()<.5?30+r()*120:930+r()*120,sp=26+r()*22,ph=r()*7,s=22+r()*20,k=Math.floor(r()*5),y0=r()*2100;
  const y=((y0+t*sp)%2100)-90,x=x0+Math.sin(t*.7+ph)*40,flip=Math.cos(t*1.3+ph);
  c.save();c.translate(x,y);c.scale(Math.abs(flip)*.8+.2,1);dkMaple(c,0,0,s,Math.sin(t*.9+ph)*.8,DK_MCOL[k],{blur:14,sa:.3});c.restore()}}
// ---------- クリスマス ----------
function dkFir(c,x0,y0,x1,y1,w,seed){const r=XR(seed);const dx=x1-x0,dy=y1-y0,L=Math.hypot(dx,dy),ux=dx/L,uy=dy/L,nx=-uy,ny=ux;
 c.save();dkShadow(c,14,5,10,.5);c.strokeStyle='#3a2414';c.lineWidth=w*.08;c.lineCap='round';c.beginPath();c.moveTo(x0,y0);c.lineTo(x1,y1);c.stroke();c.restore();
 // 針：奥から手前へ、濃い緑→明るい緑
 for(const[pass,cols,len]of[[0,['#0e2a1c','#123422'],1],[1,['#1b4a30','#22583a'],.9],[2,['#2f6e48','#3d8458'],.75]]){
  for(let i=0;i<L/2.6;i++){const u=i/(L/2.6),px=x0+dx*u,py=y0+dy*u,tip=Math.min(1,(1-u)*3.2)*Math.min(1,u*6+.3);
   for(const sd of[-1,1]){const ln=w*(.5+r()*.5)*len*tip,an=(.55+r()*.35)*sd;const ex=px+(ux*Math.cos(an)*.6+nx*Math.sin(an))*ln,ey=py+(uy*Math.cos(an)*.6+ny*Math.sin(an))*ln;
    c.strokeStyle=cols[r()<.5?0:1];c.lineWidth=1.6+pass*.3;c.beginPath();c.moveTo(px,py);c.lineTo(ex,ey);c.stroke()}}}}
function dkBall(c,x,y,R,col){c.save();dkShadow(c,16,5,10,.5);const g=c.createRadialGradient(x-R*.35,y-R*.4,R*.08,x,y,R);g.addColorStop(0,col[0]);g.addColorStop(.45,col[1]);g.addColorStop(1,col[2]);c.fillStyle=g;c.beginPath();c.arc(x,y,R,0,7);c.fill();dkNoShadow(c);
 c.fillStyle='rgba(255,255,255,.75)';c.beginPath();c.ellipse(x-R*.38,y-R*.42,R*.14,R*.22,.6,0,7);c.fill();c.fillStyle='rgba(255,255,255,.25)';c.beginPath();c.ellipse(x+R*.3,y+R*.45,R*.25,R*.1,-.4,0,7);c.fill();
 const cg=c.createLinearGradient(x-R*.22,0,x+R*.22,0);cg.addColorStop(0,'#7c5a22');cg.addColorStop(.5,'#f2d58c');cg.addColorStop(1,'#7c5a22');c.fillStyle=cg;c.fillRect(x-R*.2,y-R*1.12,R*.4,R*.2);c.strokeStyle='#c9a24e';c.lineWidth=2;c.beginPath();c.arc(x,y-R*1.2,R*.1,0,7);c.stroke();c.restore()}
const DK_RED=['#ff8a80','#c0302a','#5a0f0c'],DK_GLD=['#fff1c0','#d8a842','#6e4a14'],DK_GRN=['#9ee0b8','#2e7a50','#0e2c1c'];
function dkHolly(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);dkShadow(c,8,3,6,.45);
 const leaf=(a)=>{c.save();c.rotate(a);const g=c.createLinearGradient(0,-s*.3,0,s*.3);g.addColorStop(0,'#3d8458');g.addColorStop(1,'#1b4a30');c.fillStyle=g;c.beginPath();c.moveTo(0,0);
  for(let i=1;i<=5;i++){const u=i/5;c.lineTo(u*s,-Math.sin(Math.PI*u)*s*.32*(i%2?1:.7))}for(let i=4;i>=0;i--){const u=i/5;c.lineTo(u*s,Math.sin(Math.PI*u)*s*.32*(i%2?1:.7))}c.fill();
  c.strokeStyle='rgba(200,240,200,.35)';c.lineWidth=1;c.beginPath();c.moveTo(0,0);c.lineTo(s*.9,0);c.stroke();c.restore()};
 leaf(-2.4);leaf(-.7);leaf(.9);dkNoShadow(c);
 for(const[bx,by]of[[-s*.08,-s*.08],[s*.1,-s*.02],[0,s*.1]]){const g=c.createRadialGradient(bx-3,by-3,1,bx,by,s*.11);g.addColorStop(0,'#ff8a80');g.addColorStop(1,'#8a1a14');c.fillStyle=g;c.beginPath();c.arc(bx,by,s*.11,0,7);c.fill()}c.restore()}
function dkXmas(c){
 // 11/16 owner「飾りとかじゃない」→ 物は置かない。夜の街の奥にイルミがぼけて見え、雪が静かに降る
 const g=c.createLinearGradient(0,0,0,1920);g.addColorStop(0,'#0b1024');g.addColorStop(.5,'#141a38');g.addColorStop(1,'#0a0d1c');c.fillStyle=g;c.fillRect(0,0,1080,1920);
 // 奥のイルミ：大小のぼけを少なめに。上のまん中（題の字）はあける。遠い物ほどぼかす
 const r=XR(73);const lay=document.createElement('canvas');lay.width=1080;lay.height=1920;const q=lay.getContext('2d');q.globalCompositeOperation='lighter';
 const put=(x,y,R,a)=>{const col=r()<.8?['255,206,130','255,186,110','255,226,170'][Math.floor(r()*3)]:['255,150,130','210,225,255'][Math.floor(r()*2)];mgBokeh(q,x,y,R,col,a)};
 for(let i=0;i<9;i++){const x=r()<.5?-20+r()*300:780+r()*320,y=20+r()*230;put(x,y,30+r()*50,.26+r()*.18)}
 for(let i=0;i<14;i++){const x=-30+r()*1140,y=1640+r()*300;put(x,y,34+r()*60,.26+r()*.18)}
 for(let i=0;i<10;i++){const x=r()<.5?r()*80:1000+r()*80,y=300+r()*1300;put(x,y,16+r()*26,.2+r()*.14)}
 c.save();c.filter='blur(5px)';c.drawImage(lay,0,0);c.restore();
 // 地面の明かりのにじみ
 const h=c.createRadialGradient(540,2000,100,540,2000,900);h.addColorStop(0,'rgba(255,190,120,.22)');h.addColorStop(1,'rgba(255,190,120,0)');c.fillStyle=h;c.fillRect(0,1000,1080,920)}
const DK_XL=(()=>{const r=XR(81),L=[];const sp=[[130,60],[250,190],[60,140],[400,40],[680,30],[820,60],[950,120],[1040,60],[30,600],[1050,700],[40,1200],[1045,1300],[140,1660],[350,1700],[60,1780],[440,1880],[650,1700],[760,1780],[960,1700],[1040,1790],[880,1900]];
 for(const[x,y]of sp)if(!(y<260&&x>280&&x<800))L.push({x:x+(r()-.5)*30,y:y+(r()-.5)*30,R:16+r()*26,c:['255,206,130','255,180,110','255,226,170','255,150,120'][Math.floor(r()*4)],p:r()*7,sp:.8+r()*1.4});return L})();
function dkXmasFx(c,t){c.save();c.globalCompositeOperation='lighter';for(const l of DK_XL){const k=.5+.5*Math.sin(t*l.sp+l.p);mgBokeh(c,l.x,l.y,l.R,l.c,.12*k)}c.restore();
 const r=XR(91);for(let i=0;i<60;i++){const x0=r()*1080,sp=30+r()*50,sz=1.2+r()*3,ph=r()*7,y0=r()*2000;const y=((y0+t*sp)%2000)-40,x=x0+Math.sin(t*.7+ph)*14;mgDot(c,MG_SNOW,x,y,sz*1.6,.55)}c.globalAlpha=1}
// ---------- 浜 ----------
function dkScallop(c,x,y,s,rot,col){c.save();c.translate(x,y);c.rotate(rot);dkShadow(c,10,4,8,.32);const g=c.createRadialGradient(0,s*.3,s*.1,0,0,s);g.addColorStop(0,col[0]);g.addColorStop(1,col[1]);c.fillStyle=g;
 c.beginPath();c.moveTo(-s*.18,s*.42);for(let i=0;i<=12;i++){const a=Math.PI*(1.12+i/12*.76);const rr=s*(i%2?.96:1);c.lineTo(Math.cos(a)*rr,Math.sin(a)*rr+s*.1)}c.lineTo(s*.18,s*.42);c.closePath();c.fill();dkNoShadow(c);
 c.strokeStyle='rgba(120,70,40,.28)';c.lineWidth=1.4;for(let i=1;i<12;i++){const a=Math.PI*(1.12+i/12*.76);c.beginPath();c.moveTo(0,s*.4);c.lineTo(Math.cos(a)*s*.95,Math.sin(a)*s*.95+s*.1);c.stroke()}
 c.fillStyle=col[1];c.beginPath();c.moveTo(-s*.32,s*.42);c.lineTo(s*.32,s*.42);c.lineTo(s*.22,s*.58);c.lineTo(-s*.22,s*.58);c.fill();c.restore()}
function dkStar(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);dkShadow(c,10,4,8,.35);const g=c.createRadialGradient(0,0,s*.1,0,0,s);g.addColorStop(0,'#ffb27a');g.addColorStop(1,'#d8663a');c.fillStyle=g;c.beginPath();
 for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=i%2?s*.42:s;const a2=a+(i%2?0:0);i?c.lineTo(Math.cos(a2)*rr,Math.sin(a2)*rr):c.moveTo(Math.cos(a2)*rr,Math.sin(a2)*rr)}c.closePath();c.fill();dkNoShadow(c);
 c.fillStyle='rgba(255,236,210,.7)';const r=XR(5);for(let k=0;k<5;k++){const a=-Math.PI/2+k*2*Math.PI/5;for(let j=1;j<6;j++){c.beginPath();c.arc(Math.cos(a)*s*j/6.5+(r()-.5)*2,Math.sin(a)*s*j/6.5,1.8,0,7);c.fill()}}c.restore()}
function dkCone(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);dkShadow(c,10,4,8,.32);const g=c.createLinearGradient(-s*.3,0,s*.3,0);g.addColorStop(0,'#f6e6cf');g.addColorStop(.6,'#e2c29a');g.addColorStop(1,'#a8825a');c.fillStyle=g;
 c.beginPath();c.moveTo(0,-s);c.quadraticCurveTo(s*.42,-s*.1,s*.24,s*.55);c.quadraticCurveTo(0,s*.7,-s*.24,s*.55);c.quadraticCurveTo(-s*.42,-s*.1,0,-s);c.fill();dkNoShadow(c);
 c.strokeStyle='rgba(120,80,50,.45)';c.lineWidth=1.3;for(let i=1;i<6;i++){const yy=-s+i*s*.28;c.beginPath();c.moveTo(-s*.3*Math.min(1,i/3),yy+s*.1);c.quadraticCurveTo(0,yy-s*.02,s*.3*Math.min(1,i/3),yy-s*.06);c.stroke()}c.restore()}
function dkGlass(c,x,y,s,rot,rgb){c.save();c.translate(x,y);c.rotate(rot);dkShadow(c,8,3,6,.25);c.fillStyle=`rgba(${rgb},.75)`;const r=XR(Math.floor(x+y));c.beginPath();for(let i=0;i<7;i++){const a=i/7*Math.PI*2,rr=s*(.75+r()*.3);i?c.lineTo(Math.cos(a)*rr,Math.sin(a)*rr*.75):c.moveTo(Math.cos(a)*rr,Math.sin(a)*rr*.75)}c.closePath();c.fill();dkNoShadow(c);
 c.fillStyle='rgba(255,255,255,.45)';c.beginPath();c.ellipse(-s*.25,-s*.2,s*.22,s*.1,-.5,0,7);c.fill();c.restore()}
function dkHama(c){
 // 机：白っぽい流木の板
 dkWood(c,0,640,'#d9cebd','#c4b6a1','#e6dccd',21);dkWood(c,640,1300,'#d4c8b5','#bfb19b','#e2d8c8',22);dkWood(c,1300,1920,'#d9cebd','#c2b49e','#e6dccd',23);
 // 砂を少し
 const r=XR(31);for(const[cx,cy,rx,ry]of[[150,1800,260,110],[960,120,200,90]]){for(let i=0;i<2600;i++){const a=r()*7,d=Math.sqrt(r());c.fillStyle=`rgba(${r()<.5?'190,160,120':'236,220,190'},${.5*(1-d)})`;c.fillRect(cx+Math.cos(a)*rx*d,cy+Math.sin(a)*ry*d,1.6,1.6)}}
 dkScallop(c,110,110,64,.3,['#fff1e2','#f0b49a']);dkScallop(c,260,60,40,-.6,['#fff7ee','#e8c9a8']);dkStar(c,960,130,62,.4);dkCone(c,840,70,40,1.9);dkGlass(c,1035,250,22,.3,'120,200,200');dkGlass(c,60,250,18,1.2,'140,190,230');
 dkStar(c,130,1760,70,-.3);dkScallop(c,290,1830,52,2.6,['#fff1e2','#efa58a']);dkCone(c,60,1880,42,-1.1);dkGlass(c,400,1880,22,.8,'110,190,180');
 dkScallop(c,960,1740,66,-.4,['#fff7ee','#e8c9a8']);dkGlass(c,820,1840,24,.3,'130,200,220');dkGlass(c,880,1890,16,1,'170,220,200');dkCone(c,1040,1860,38,.6);dkStar(c,700,1880,40,1.1)}
function dkHamaFx(c,t){c.save();c.globalCompositeOperation='lighter';const r=XR(41);for(let i=0;i<26;i++){const x0=r()*1080,y0=r()*1920,R=40+r()*90,ph=r()*7;const x=x0+Math.sin(t*.35+ph)*30,y=y0+Math.cos(t*.3+ph)*24;
  const k=.5+.5*Math.sin(t*.9+ph*2);const g=c.createRadialGradient(x,y,R*.55,x,y,R);g.addColorStop(0,'rgba(200,240,255,0)');g.addColorStop(.8,`rgba(220,245,255,${.07*k})`);g.addColorStop(1,'rgba(220,245,255,0)');c.fillStyle=g;c.beginPath();c.arc(x,y,R,0,7);c.fill()}c.restore()}
// 作る・毎コマ
function dkBuild(){if(!DK)return;const s=document.getElementById('dks');if(!s)return;const c=s.getContext('2d');({momiji:dkMomiji,xmas:dkXmas,hama:dkHama})[DK](c);
 // まわりを少し暗く（本に目が行く）
 const v=c.createRadialGradient(540,920,500,540,920,1200);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,`rgba(0,0,0,${DK=='hama'?.25:.45})`);c.fillStyle=v;c.fillRect(0,0,1080,1920)}
function dkDraw(t){if(!DK)return;const d=document.getElementById('dkd');if(!d)return;const c=d.getContext('2d');c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';c.clearRect(0,0,1080,1920);
 ({momiji:dkMomijiFx,xmas:dkXmasFx,hama:dkHamaFx})[DK](c,t);c.globalAlpha=1;c.globalCompositeOperation='source-over'}
