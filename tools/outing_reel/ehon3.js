// 11/19 魔法の絵本ニュース（owner「写真じゃなくて作られへんの？」「めちゃくちゃお洒落な魔法の絵本のように」「お前が作れ」）
// 画面いっぱい（1080x1920）を canvas で描く。絵は場面ごとに「奥・中・手前」の層を1回だけ描き、毎コマはカメラ（寄り・横の動き・奥行きのずれ）と、
// 光（ともる・ゆらぐ・にじむ）・落ちる葉・金の粉・歩く人だけを描き足す。コマは時刻だけで決まる（何人かで分けて撮る）。
const SW=1080,SH=1920;
function R_(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function cv_(w,h){const c=document.createElement('canvas');c.width=w||SW;c.height=h||SH;return c}
function hx(h){h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function mix(a,b,k){const A=hx(a),B=hx(b);return'#'+A.map((v,i)=>Math.round(v+(B[i]-v)*k).toString(16).padStart(2,'0')).join('')}
function gl(c,x,y,r,rgb,a){if(a<=0||r<=0)return;const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,`rgba(${rgb},${a})`);g.addColorStop(.35,`rgba(${rgb},${a*.42})`);g.addColorStop(1,`rgba(${rgb},0)`);c.fillStyle=g;c.beginPath();c.arc(x,y,r,0,7);c.fill()}
// 紙の目（水彩紙のざらつき）
let PAPER=null;function paper(){if(PAPER)return PAPER;const r=R_(77),s=cv_(270,480),g=s.getContext('2d'),d=g.createImageData(270,480);for(let i=0;i<d.data.length;i+=4){const v=200+r()*55;d.data[i]=v;d.data[i+1]=v*.97;d.data[i+2]=v*.9;d.data[i+3]=255}g.putImageData(d,0,0);g.filter='blur(.6px)';g.drawImage(s,0,0);PAPER=s;return s}
// 水彩の面：形を塗って、ふちを少し濃く、中をむらに
function wc(c,path,col,o){o=o||{};c.save();c.beginPath();path(c);c.fillStyle=col;c.globalAlpha=o.a??1;c.fill();
 if(o.edge!==0){c.globalAlpha=(o.edge??.35)*(o.a??1);c.strokeStyle=mix(col,'#000000',.35);c.lineWidth=o.lw??2.2;c.filter='blur(1.2px)';c.stroke();c.filter='none'}
 if(o.gold){c.globalAlpha=o.gold;c.strokeStyle='#e9c87a';c.lineWidth=o.glw??2;c.stroke()}
 c.clip();c.globalAlpha=.10;c.globalCompositeOperation='multiply';c.drawImage(paper(),0,0,SW,SH);c.restore()}
function wob(c,pts,amp,seed){const r=R_(seed||1);c.moveTo(pts[0][0]+(r()-.5)*amp,pts[0][1]+(r()-.5)*amp);for(let i=1;i<pts.length;i++){const p=pts[i],q=pts[i-1];const mx=(p[0]+q[0])/2+(r()-.5)*amp,my=(p[1]+q[1])/2+(r()-.5)*amp;c.quadraticCurveTo(mx,my,p[0]+(r()-.5)*amp,p[1]+(r()-.5)*amp)}c.closePath()}
function leaf(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);c.beginPath();for(let i=0;i<7;i++){const a=-Math.PI/2+(i-3)*.62,L=i==3?1:i==2||i==4?.9:i==1||i==5?.66:.38;c.lineTo(Math.cos(a-.2)*s*L*.42,Math.sin(a-.2)*s*L*.42);c.lineTo(Math.cos(a)*s*L,Math.sin(a)*s*L);c.lineTo(Math.cos(a+.2)*s*L*.42,Math.sin(a+.2)*s*L*.42)}c.lineTo(0,s*.25);c.closePath();c.fill();c.restore()}
// 空
function sky(c,mode,k){const P=[['#8fbfe0','#cfe6f0','#f6efe0'],['#2a2a66','#8a4f86','#f09a6e','#f8c88e'],['#04061a','#0d1640','#22285c']][mode];const g=c.createLinearGradient(0,0,0,SH*.62);P.forEach((q,i)=>g.addColorStop(i/(P.length-1),q));c.fillStyle=g;c.fillRect(0,0,SW,SH);
 if(mode==2){const r=R_(5);for(let i=0;i<260;i++){const x=r()*SW,y=r()*SH*.55,s=r();c.fillStyle=`rgba(255,246,222,${.2+s*.75})`;c.beginPath();c.arc(x,y,.6+s*1.9,0,7);c.fill()}
  c.save();c.globalCompositeOperation='screen';gl(c,SW*.5,SH*.28,900,'60,70,150',.25);c.restore()}
 if(mode==1){c.save();c.globalCompositeOperation='screen';gl(c,SW*.62,SH*.46,800,'255,170,120',.5);c.restore()}
 if(mode==0){const r=R_(9);c.save();c.filter='blur(14px)';for(let i=0;i<7;i++){const x=r()*SW,y=150+r()*600,w=160+r()*260;c.fillStyle='rgba(255,255,255,.75)';c.beginPath();c.ellipse(x,y,w,w*.28,0,0,7);c.fill()}c.restore()}}
function moon(c,x,y,R){c.save();c.globalCompositeOperation='screen';gl(c,x,y,R*8,'170,190,255',.22);gl(c,x,y,R*2.8,'255,240,205',.35);c.restore();c.fillStyle='#fbf1d6';c.beginPath();c.arc(x,y,R,0,7);c.fill();c.fillStyle='rgba(200,180,140,.25)';c.beginPath();c.arc(x-R*.3,y-R*.1,R*.28,0,7);c.arc(x+R*.25,y+R*.3,R*.18,0,7);c.fill()}
// 山なみ（霧の重なり）
function hills(c,y,cols,seed,amp){const r=R_(seed);cols.forEach((col,i)=>{const yy=y+i*70;c.save();c.beginPath();c.moveTo(-20,SH);let x=-20;c.lineTo(-20,yy);while(x<SW+40){x+=60+r()*80;c.quadraticCurveTo(x-40,yy-amp*(.4+r()*.8)-i*10,x,yy-r()*amp*.4)}c.lineTo(SW+20,SH);c.closePath();c.fillStyle=col;c.fill();c.restore();
 c.save();c.globalAlpha=.35;c.fillStyle=cols[cols.length-1];c.filter='blur(30px)';c.fillRect(-50,yy+10,SW+100,60);c.restore()})}
// もみじの木のかたまり（何千枚の葉）。lit＝下から照らす（夜のライトアップ）
function canopy(c,cx,cy,rx,ry,mode,seed,n,lit){const r=R_(seed);const day=['#c8341f','#e0582a','#ef8a2e','#f2b43a','#b52a1d','#d9452a','#e8a23a'],dusk=['#a62a22','#c84a2a','#d7702e','#8a2a24'],night=['#ff8a3a','#ffb24a','#ff6a2a','#ffd070','#e04a20'];
 const pal=mode==0?day:mode==1?dusk:night;
 // かたまり（雲のような房）を枝の先に置く
 const K=6+Math.floor(r()*5),cl=[];for(let i=0;i<K;i++){const a=r()*6.283,d=Math.sqrt(r())*.7;cl.push({x:cx+Math.cos(a)*rx*d,y:cy+Math.sin(a)*ry*d*.9,rx:rx*(.28+r()*.22),ry:ry*(.3+r()*.25)})}
 // 枝（房の下に細く見える）
 c.save();c.strokeStyle=mode==2?'rgba(25,8,6,.9)':mode==1?'rgba(40,18,20,.8)':'rgba(70,40,30,.7)';c.lineCap='round';for(const q of cl){c.lineWidth=2+r()*4;c.beginPath();c.moveTo(cx+(r()-.5)*rx*.2,cy+ry*.9);c.quadraticCurveTo((cx+q.x)/2+(r()-.5)*60,(cy+ry+q.y)/2,q.x,q.y+q.ry*.3);c.stroke()}c.restore();
 // 房の影
 c.save();c.filter='blur(8px)';for(const q of cl){c.fillStyle=mode==2?'rgba(50,10,6,.85)':mode==1?'rgba(70,22,26,.7)':'rgba(130,34,22,.5)';c.beginPath();c.ellipse(q.x,q.y+q.ry*.15,q.rx*.85,q.ry*.75,0,0,7);c.fill()}c.restore();
 for(let i=0;i<n;i++){const q=cl[i%K];const a=r()*6.283,d=Math.pow(r(),.65)*(r()<.08?1.35:1);const x=q.x+Math.cos(a)*q.rx*d,y=q.y+Math.sin(a)*q.ry*d;
  const v=(y-(q.y-q.ry))/(q.ry*2);   // 房の中の高さ 0上〜1下
  let col=pal[i%pal.length];
  if(mode==2)col=mix('#2a0806',col,Math.min(1,.12+(lit?v:1-v)*1.1));else if(mode==1)col=mix('#3a1418',col,.4+(1-v)*.55);else col=mix(col,v<.35?'#ffe2a0':'#6a1810',v<.35?(.35-v)*.9:(v-.35)*.45);
  c.fillStyle=col;c.globalAlpha=.7+r()*.3;leaf(c,x,y,6+r()*10,r()*6.3)}
 c.globalAlpha=1;if(lit){c.save();c.globalCompositeOperation='screen';for(const q of cl)gl(c,q.x,q.y+q.ry*.6,q.rx*1.1,'255,140,50',.22);c.restore()}}
function trunk(c,x,by,h,w,mode){c.save();c.strokeStyle=mode==2?'#1a0d0a':mode==1?'#2e1a18':'#4a2e22';c.lineCap='round';c.lineWidth=w;c.beginPath();c.moveTo(x,by);c.bezierCurveTo(x+w*1.5,by-h*.4,x-w*2,by-h*.6,x+w*.8,by-h);c.stroke();c.lineWidth=w*.5;c.beginPath();c.moveTo(x,by-h*.55);c.quadraticCurveTo(x+w*4,by-h*.7,x+w*6,by-h*.95);c.stroke();c.beginPath();c.moveTo(x+w*.2,by-h*.7);c.quadraticCurveTo(x-w*4,by-h*.8,x-w*5.5,by-h*1.02);c.stroke();c.restore()}
// 多宝塔（下は四角・上は丸い胴と大きな屋根・上に相輪）
function tahoto(c,cx,by,w,mode,gold){const night=mode==2;const ver=night?'#5e1c14':'#c43c26',wall=night?'#2e2224':'#f2ead8',roof=night?'#141018':'#34303a';
 const roofS=(y,ww,hh)=>{c.beginPath();c.moveTo(cx-ww*.6,y);c.quadraticCurveTo(cx-ww*.42,y-hh*.3,cx-ww*.2,y-hh);c.lineTo(cx+ww*.2,y-hh);c.quadraticCurveTo(cx+ww*.42,y-hh*.3,cx+ww*.6,y);c.quadraticCurveTo(cx,y-hh*.18,cx-ww*.6,y);c.closePath()};
 const lo=w*.62,h1=w*.42;wc(c,g=>{g.rect(cx-lo/2,by-h1,lo,h1)},ver,{gold});c.fillStyle=wall;for(const k of[-.32,0,.32]){c.fillRect(cx+lo*k-lo*.09,by-h1*.85,lo*.18,h1*.6)}
 wc(c,()=>roofS(by-h1+4,w*1.0,w*.16),roof,{gold});
 wc(c,g=>{g.ellipse(cx,by-h1-w*.2,w*.22,w*.14,0,0,7)},wall,{gold});wc(c,g=>{g.rect(cx-w*.17,by-h1-w*.36,w*.34,w*.18)},ver,{gold});
 wc(c,()=>roofS(by-h1-w*.32,w*1.1,w*.26),roof,{gold});
 c.save();c.strokeStyle=gold?'#e9c87a':night?'#3a3030':'#6a5a4a';c.lineWidth=w*.025;c.beginPath();c.moveTo(cx,by-h1-w*.56);c.lineTo(cx,by-h1-w*1.05);c.stroke();for(let i=0;i<7;i++){c.beginPath();c.ellipse(cx,by-h1-w*.62-i*w*.055,w*.05,w*.012,0,0,7);c.stroke()}c.restore()}
// お堂の大屋根（手前に低く）
function hall(c,cx,by,w,mode,gold){const night=mode==2;const roof=night?'#0f0c12':'#2f2c34',ver=night?'#4a1610':'#b8392a',wall=night?'#3a2a26':'#efe6d2';
 wc(c,g=>g.rect(cx-w*.42,by-w*.2,w*.84,w*.2),ver,{gold});c.fillStyle=wall;for(let i=0;i<6;i++)c.fillRect(cx-w*.38+i*w*.135,by-w*.17,w*.1,w*.14);
 wc(c,g=>{g.moveTo(cx-w*.62,by-w*.19);g.quadraticCurveTo(cx-w*.45,by-w*.24,cx-w*.36,by-w*.42);g.lineTo(cx+w*.36,by-w*.42);g.quadraticCurveTo(cx+w*.45,by-w*.24,cx+w*.62,by-w*.19);g.quadraticCurveTo(cx,by-w*.27,cx-w*.62,by-w*.19)},roof,{gold});
 if(night){c.save();c.globalCompositeOperation='screen';for(let i=0;i<6;i++)gl(c,cx-w*.33+i*w*.135,by-w*.1,w*.09,'255,190,110',.5);c.restore()}}
function lantern(c,x,by,s,mode,gold){const night=mode==2;const st=night?'#2a2830':'#8f8a80';wc(c,g=>{g.rect(x-s*.08,by-s*.55,s*.16,s*.55)},st,{gold});wc(c,g=>{g.rect(x-s*.2,by-s*.85,s*.4,s*.3)},night?'#ffd68a':'#e8e2d4',{gold});wc(c,g=>{g.moveTo(x-s*.32,by-s*.85);g.lineTo(x,by-s*1.05);g.lineTo(x+s*.32,by-s*.85);g.closePath()},st,{gold})}
function person(c,x,by,s,col,seed,ph){const r=R_(seed);const sw=Math.sin(ph||0)*s*.03;c.save();c.fillStyle=col;c.beginPath();c.ellipse(x,by-s*.86,s*.1,s*.11,0,0,7);c.fill();
 c.beginPath();c.moveTo(x-s*.17,by-s*.1);c.quadraticCurveTo(x-s*.2,by-s*.66,x,by-s*.72);c.quadraticCurveTo(x+s*.2,by-s*.66,x+s*.17,by-s*.1);c.closePath();c.fill();
 c.fillRect(x-s*.1+sw,by-s*.12,s*.07,s*.12);c.fillRect(x+s*.03-sw,by-s*.12,s*.07,s*.12);if(r()<.5){c.fillStyle=mix(col,'#ffffff',.25);c.fillRect(x-s*.16,by-s*.62,s*.32,s*.06)}c.restore()}

// ---------- 場面（層）を作る ----------
const SC={};
function lay(){const c=cv_();return{c:c.getContext('2d'),cv:c}}
function finish(L,mode){for(const l of L){const g=l.c;g.save();g.globalCompositeOperation='source-atop';g.globalAlpha=.07;g.drawImage(paper(),0,0,SW,SH);g.restore()}}
// 夜の多宝塔（見せ場）。mode 0＝昼・2＝夜（同じ構図＝昼と夜の入れ替えで左右に並べる）
function scTemple(mode){const key='t'+mode;if(SC[key])return SC[key];const B=lay(),M=lay(),F=lay();const L=[];const gold=mode==2?.55:0;
 sky(B.c,mode);if(mode==2)moon(B.c,820,330,58);
 hills(B.c,900,mode==2?['#0e1430','#151a3a','#1d1f40']:['#9ab6c4','#7f9e9a','#6d8a6e'],3,120);
 // 山の上の多宝塔と、それを囲む照らされたもみじ
 canopy(M.c,300,1060,250,150,mode,11,1400,mode==2);canopy(M.c,800,1080,270,150,mode,12,1500,mode==2);
 tahoto(M.c,560,1010,250,mode,gold);if(mode==2){L.push({x:560,y:900,r:300,c:'255,190,110',a:.55,sp:1.3,p:0,ly:1});}
 canopy(M.c,560,1150,520,120,mode,13,2200,mode==2);
 hall(M.c,560,1330,700,mode,gold);
 // 手前：左右に大きな枝、石の道、灯籠、人
 wc(F.c,g=>{g.moveTo(0,1500);g.quadraticCurveTo(540,1440,1080,1500);g.lineTo(1080,1920);g.lineTo(0,1920)},mode==2?'#14121a':'#b7ab8e',{edge:0});
 wc(F.c,g=>{g.moveTo(430,1920);g.quadraticCurveTo(520,1600,540,1470);g.quadraticCurveTo(560,1600,650,1920)},mode==2?'#2a2630':'#d9cfb8',{edge:.2});
 trunk(F.c,60,1780,520,26,mode);canopy(F.c,60,1240,330,260,mode,21,2600,mode==2);trunk(F.c,1040,1800,500,24,mode);canopy(F.c,1040,1260,320,250,mode,22,2600,mode==2);
 for(const[x,y,s]of[[330,1640,150],[760,1650,150],[200,1840,210],[890,1850,210]]){lantern(F.c,x,y,s,mode,gold);if(mode==2)L.push({x,y:y-s*.7,r:s*1.3,c:'255,200,120',a:.6,sp:2.1,p:x,ly:2})}
 if(mode==2){for(const[x,y]of[[300,1420],[800,1430],[560,1300],[120,1500],[980,1500]])L.push({x,y,r:420,c:'255,140,60',a:.35,sp:.7,p:y,ly:1})}
 finish([B,M,F],mode);return SC[key]={L:[B,M,F],lights:L,mode}}
// 照らされた枝の寄り（下から見上げる）
function scBranch(){if(SC.b)return SC.b;const B=lay(),M=lay(),F=lay();B.c.fillStyle='#05040c';B.c.fillRect(0,0,SW,SH);const g=B.c.createRadialGradient(540,1200,100,540,1200,1300);g.addColorStop(0,'#2a1420');g.addColorStop(1,'#05040c');B.c.fillStyle=g;B.c.fillRect(0,0,SW,SH);
 const r=R_(4);for(let i=0;i<40;i++){B.c.save();B.c.globalCompositeOperation='screen';gl(B.c,r()*SW,r()*SH,40+r()*90,r()<.5?'255,160,70':'255,210,120',.25);B.c.restore()}
 const branch=(c,x0,y0,x1,y1,w)=>{c.save();c.strokeStyle='#1a0c0a';c.lineCap='round';c.lineWidth=w;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2+80,(y0+y1)/2-60,x1,y1);c.stroke();c.restore()};
 branch(M.c,-40,1500,1100,500,22);branch(M.c,200,1100,700,300,10);branch(M.c,600,900,1120,1100,9);
 canopy(M.c,500,700,520,380,2,31,5200,true);canopy(F.c,180,1500,360,300,2,32,3000,true);canopy(F.c,950,350,330,260,2,33,2600,true);
 finish([B,M,F],2);return SC.b={L:[B,M,F],lights:[{x:540,y:1700,r:900,c:'255,150,60',a:.3,sp:.6,p:0,ly:1}],mode:2}}
// 夕暮れの池と橋（時間で夜になり灯りがともる）
function scPond(mode){const key='p'+mode;if(SC[key])return SC[key];const B=lay(),M=lay(),F=lay();const L=[];const gold=mode==2?.5:0;
 sky(B.c,mode);if(mode==2)moon(B.c,250,300,46);hills(B.c,860,mode==2?['#0e1430','#151a3a','#1d1f40']:['#5a3a66','#6e4058','#7a4a4e'],7,100);
 canopy(M.c,200,980,330,170,mode,41,1900,mode==2);canopy(M.c,880,960,300,160,mode,42,1800,mode==2);tahoto(M.c,700,880,150,mode,gold);
 // 池（空を映す）
 const wy=1180;const pg=M.c.createLinearGradient(0,wy,0,1560);pg.addColorStop(0,mode==2?'#0c1230':'#c08070');pg.addColorStop(1,mode==2?'#05060f':'#3a2440');M.c.fillStyle=pg;M.c.fillRect(0,wy,SW,380);
 M.c.save();M.c.globalAlpha=.45;M.c.translate(0,wy*2);M.c.scale(1,-1);M.c.filter='blur(3px)';M.c.drawImage(M.cv,0,0);M.c.restore();
 M.c.save();M.c.strokeStyle=mode==2?'rgba(255,180,110,.25)':'rgba(255,230,210,.4)';M.c.lineWidth=2;const r=R_(3);for(let i=0;i<60;i++){const x=r()*SW,y=wy+10+r()*360,l=20+r()*70;M.c.beginPath();M.c.moveTo(x,y);M.c.lineTo(x+l,y);M.c.stroke()}M.c.restore();
 // 朱の反り橋
 F.c.save();F.c.strokeStyle=mode==2?'#5a1a12':'#b83a26';F.c.lineWidth=16;F.c.beginPath();F.c.moveTo(120,1300);F.c.quadraticCurveTo(540,1150,960,1300);F.c.stroke();F.c.lineWidth=8;F.c.beginPath();F.c.moveTo(120,1250);F.c.quadraticCurveTo(540,1100,960,1250);F.c.stroke();for(let i=0;i<=12;i++){const x=120+i*70,y=1250-Math.sin(i/12*Math.PI)*110;F.c.beginPath();F.c.moveTo(x,y);F.c.lineTo(x,y+50);F.c.stroke()}F.c.restore();
 for(let i=0;i<=6;i++){const x=150+i*130,y=1235-Math.sin(i/6*Math.PI)*110;L.push({x,y,r:90,c:'255,200,120',a:.75,sp:2+i*.3,p:i,ly:2,dot:6,on:i/6})}
 wc(F.c,g=>{g.moveTo(0,1560);g.quadraticCurveTo(540,1520,1080,1570);g.lineTo(1080,1920);g.lineTo(0,1920)},mode==2?'#100e16':'#3a2a2e',{edge:0});
 canopy(F.c,80,1700,300,240,mode,43,2200,mode==2);canopy(F.c,1000,1720,300,230,mode,44,2200,mode==2);
 for(const[x,y]of[[200,1150],[880,1130],[700,820]])L.push({x,y,r:380,c:'255,140,60',a:.4,sp:.7,p:x,ly:1,on:.2});
 finish([B,M,F],mode);return SC[key]={L:[B,M,F],lights:L,mode}}
// 行列（夜の参道に人がふえる）
function scPath(){if(SC.path)return SC.path;const s=scTemple(2);return SC.path=s}

// ---------- 毎コマ：層をカメラで重ね、光と粒を足す ----------
const OUT=cv_(),O=OUT.getContext('2d');const LC=cv_(SW/4,SH/4),LG=LC.getContext('2d'),BL=cv_(SW/8,SH/8),BLG=BL.getContext('2d');
// cam：{s 大きさ, x,y 中心のずれ, par 奥行きのずれの強さ}
function drawScene(S,t,cam,opt){opt=opt||{};const c=O;c.setTransform(1,0,0,1,0,0);c.globalCompositeOperation='source-over';c.globalAlpha=1;c.filter='none';
 const dep=[.25,.6,1];S.L.forEach((l,i)=>{const s=cam.s*(1+(dep[i]-.6)*(cam.ds||0));c.setTransform(s,0,0,s,SW/2-SW/2*s+(cam.x||0)*dep[i]*(cam.par??1),SH/2-SH/2*s+(cam.y||0)*dep[i]*(cam.par??1));c.drawImage(l.cv,0,0)});
 c.setTransform(1,0,0,1,0,0);
 // 光：ともる量 on（0〜1）で順番に灯る
 LG.setTransform(1,0,0,1,0,0);LG.clearRect(0,0,SW/4,SH/4);const lit=opt.lit??1;
 for(const l of S.lights){const k=Math.max(0,Math.min(1,(lit-(l.on||0))*6));if(k<=0)continue;const s=cam.s*(1+(dep[l.ly]-.6)*(cam.ds||0));const x=SW/2+(l.x-SW/2)*s+(cam.x||0)*dep[l.ly]*(cam.par??1),y=SH/2+(l.y-SH/2)*s+(cam.y||0)*dep[l.ly]*(cam.par??1);
  const tw=.85+.15*Math.sin(t*l.sp+l.p);const a=l.a*tw*k;c.globalCompositeOperation='screen';gl(c,x,y,l.r*s*.5,l.c,a);gl(LG,x/4,y/4,l.r*s/4,l.c,a);if(l.dot){c.globalCompositeOperation='lighter';c.fillStyle=`rgba(255,248,225,${k})`;c.beginPath();c.arc(x,y,l.dot*s,0,7);c.fill()}}
 c.globalCompositeOperation='source-over';
 // 光のにじみ
 BLG.clearRect(0,0,SW/8,SH/8);BLG.filter='blur(6px)';BLG.drawImage(LC,0,0,SW/8,SH/8);BLG.filter='none';c.globalCompositeOperation='lighter';c.globalAlpha=.7;c.drawImage(LC,0,0,SW,SH);c.globalAlpha=.6;c.drawImage(BL,0,0,SW,SH);c.globalAlpha=1;c.globalCompositeOperation='source-over';
 // 落ちるもみじ（光る）
 if(opt.leaves){const r=R_(900+(opt.seed||0));for(let i=0;i<opt.leaves;i++){const sp=.05+r()*.07,ph=r(),x0=r()*SW,z=.6+r()*1.4;const q=((t*sp+ph)%1+1)%1;const x=x0+Math.sin(t*.9+i)*60*z+q*120,y=-80+q*(SH+160);
   c.save();c.globalAlpha=.85;c.fillStyle=S.mode==2?['#ff9a40','#ffc060','#ff7030'][i%3]:['#d8442a','#ef8a2e','#c8341f'][i%3];if(S.mode==2){c.shadowColor='rgba(255,170,80,.9)';c.shadowBlur=14}c.translate(x,y);c.scale(1,.55+.45*Math.cos(t*2.3+i));leaf(c,0,0,14*z,t*1.5*(i%2?1:-1)+i);c.restore()}}
 // 金の粉（魔法）：下から上へ、きらめく
 if(opt.dust){const r=R_(500+(opt.seed||0));c.save();c.globalCompositeOperation='lighter';for(let i=0;i<opt.dust;i++){const x0=r()*SW,sp=.03+r()*.05,ph=r(),q=((t*sp+ph)%1+1)%1;const x=x0+Math.sin(t*.7+i*1.3)*40,y=SH*(1-q)+40;const tw=Math.max(0,Math.sin(t*3+i*2.1));const s=1.2+r()*2.8;
   c.fillStyle=`rgba(255,226,150,${.25+.6*tw})`;c.beginPath();c.arc(x,y,s,0,7);c.fill();if(tw>.8&&s>3){c.strokeStyle=`rgba(255,240,200,${(tw-.8)*3})`;c.lineWidth=1.2;c.beginPath();c.moveTo(x-s*4,y);c.lineTo(x+s*4,y);c.moveTo(x,y-s*4);c.lineTo(x,y+s*4);c.stroke()}}c.restore()}
 // 歩く人（参道を奥へ）
 if(opt.crowd){const n=Math.round(opt.crowd);const r=R_(77);for(let i=0;i<n;i++){const lane=r(),sp=.05+r()*.04,ph=r();const q=((t*sp+ph)%1+1)%1;const d=1-q;const y=1480+d*420,x=540+(lane-.5)*(140+d*700);const s=40+d*190;
   const cs=cam.s;person(c,SW/2+(x-SW/2)*cs+(cam.x||0),SH/2+(y-SH/2)*cs+(cam.y||0),s*cs,['#2a2230','#3a2a2a','#20283a','#3a3040'][i%4],i,t*6+i)}}
 // 周りを暗く・紙の目
 const vg=c.createRadialGradient(SW/2,SH*.48,SH*.25,SW/2,SH*.5,SH*.75);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,S.mode==2?'rgba(0,0,8,.55)':'rgba(40,20,10,.28)');c.fillStyle=vg;c.fillRect(0,0,SW,SH);
 c.save();c.globalCompositeOperation='multiply';c.globalAlpha=.06;c.drawImage(paper(),0,0,SW,SH);c.restore();return OUT}
