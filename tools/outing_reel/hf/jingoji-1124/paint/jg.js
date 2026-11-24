function tourou(x,cx,by,h,lit){x.fillStyle='#6a645a';x.fillRect(cx-h*.05,by-h*.55,h*.1,h*.55);x.fillRect(cx-h*.16,by-h*.08,h*.32,h*.08);
 x.fillRect(cx-h*.14,by-h*.6,h*.28,h*.06);x.fillStyle=lit?'#ffd890':'#4a4438';x.fillRect(cx-h*.1,by-h*.8,h*.2,h*.2);x.fillStyle='#5a544a';x.fillRect(cx-h*.04,by-h*.8,h*.08,h*.2);
 x.beginPath();x.moveTo(cx-h*.24,by-h*.8);x.lineTo(cx,by-h*.95);x.lineTo(cx+h*.24,by-h*.8);x.closePath();x.fillStyle='#57514a';x.fill();x.beginPath();x.arc(cx,by-h*.97,h*.035,0,7);x.fill()}
// 11/24 京都・高雄 神護寺だけの描き下ろし：長い石段と両側のもみじ・金堂・散りもみじ・朝の光
const PR=AKA.concat(AKA,['#e8702e','#f0a03a']);
// 石段：下から上の門へ（遠近）
function steps(x,x0,y0,x1,y1,n,wTop,wBot,col,seed){const q=rng(seed);for(let k=n-1;k>=0;k--){const t=k/(n-1),y=y0+(y1-y0)*t,w=wTop+(wBot-wTop)*t,cx=x0+(x1-x0)*t,h=6+t*26;
 x.fillStyle=mix(col,'#5a4a3a',.15+(1-t)*.2);x.fillRect(cx-w/2,y,w,h);x.fillStyle=`rgba(255,244,220,${.25+t*.35})`;x.fillRect(cx-w/2,y,w,2+t*2);x.fillStyle='rgba(40,20,10,.3)';x.fillRect(cx-w/2,y+h-3-t*3,w,3+t*3);
 for(let i=0;i<4+t*14;i++)leaf(x,cx-w/2+q()*w,y+q()*h*.5,2+t*8,q()*6,PR[i%PR.length],7)}}
function gate(x,cx,by,s,dark){const c=dark||'#3a2620';x.fillStyle=c;x.beginPath();x.moveTo(cx-s,by-s*.7);x.quadraticCurveTo(cx,by-s*.82,cx+s,by-s*.7);x.lineTo(cx+s*.7,by-s*1.0);x.lineTo(cx-s*.7,by-s*1.0);x.fill();
 x.fillStyle='#6a3a28';x.fillRect(cx-s*.62,by-s*.7,s*1.24,s*.7);x.fillStyle='rgba(255,226,170,.55)';x.fillRect(cx-s*.22,by-s*.55,s*.44,s*.55);x.fillStyle=c;x.fillRect(cx-s*.66,by-s*.72,s*.1,s*.72);x.fillRect(cx+s*.56,by-s*.72,s*.1,s*.72)}
// ===== H0 長い石段と両側のもみじ（上に楼門） =====
function H0(){const L={};const LT=[W/2,330,1000];
 {const c=cv(),x=c.getContext('2d');sky(x,'#fff4dc','#ffd9a0',0,900);glow(x,LT[0],LT[1],620,.9,'255,250,232');
  const far=cv(),fx=far.getContext('2d');for(let r=0;r<3;r++)for(let i=0;i<8;i++)leafCloud(fx,(i/7)*W+(r%2)*50-25,120+r*150,170,120,1400,10,PR,5000+r*10+i,{light:LT});x.drawImage(layerBlur(far,5),0,0);
  L.b=finish(c,5001,{rim:false,g:6,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  gate(x,W/2,470,120);
  // 石段の両わきの土手と苔
  x.fillStyle='#5a4030';x.beginPath();x.moveTo(W/2-70,470);x.lineTo(0,H);x.lineTo(0,700);x.fill();x.beginPath();x.moveTo(W/2+70,470);x.lineTo(W,H);x.lineTo(W,700);x.fill();
  steps(x,W/2,470,W/2,H-60,22,140,860,'#9a876c',5010);{const g=x.createLinearGradient(0,470,0,H);g.addColorStop(0,'rgba(255,236,200,.25)');g.addColorStop(1,'rgba(40,20,10,.25)');x.fillStyle=g;x.fillRect(0,470,W,H-470)}
  for(let s of[-1,1])for(let i=0;i<5;i++){const k=i/4;leafCloud(x,W/2+s*(150+k*300),420+k*520,90+k*140,130+k*200,1800+k*2600,9+k*6,PR,5020+i+(s>0?10:0),{light:LT})}
  L.m=finish(c,5002,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 手前：両側から覆いかぶさるもみじの枝
  hangBranch(x,[[-30,80],[120,60],[260,110],[380,90]],PR,5031,{light:LT});hangBranch(x,[[W+30,60],[W-130,40],[W-280,100],[W-400,80]],PR,5032,{light:LT});
  trunk(x,[[20,H],[60,H-500],[30,H-900],[90,H-1200]],50,14,'#3a2418',5033);trunk(x,[[W-20,H],[W-70,H-520],[W-40,H-880],[W-110,H-1180]],50,14,'#3a2418',5034);
  L.n=finish(c,5003,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,40,H-60,220,140,50,46,PR,5041);leafCloud(sx,W-30,H-40,200,130,40,46,PR,5042);L.f=layerBlur(s,7)}
 return L}
// ===== H1 金堂：石段の上の大きなお堂 =====
function H1(){const L={};const LT=[W*.7,160,1000];
 {const c=cv(),x=c.getContext('2d');sky(x,'#d6eaf4','#fff0d6',0,700);glow(x,LT[0],LT[1],600,.8,'255,250,232');
  for(let i=0;i<9;i++)leafCloud(x,(i/8)*W,260+Math.sin(i*1.4)*40,150,120,1500,10,PR,5100+i,{light:LT});L.b=finish(c,5101,{rim:false,g:6,blot:.03})}
 {const c=cv(),x=c.getContext('2d');const cx=W/2,by=760;
  // 金堂：大きな屋根・柱・石の基壇
  x.fillStyle='#8a8070';x.fillRect(cx-300,by,600,60);x.fillStyle='rgba(255,240,210,.4)';x.fillRect(cx-300,by,600,3);
  x.fillStyle='#4a2c20';x.fillRect(cx-250,by-200,500,200);x.fillStyle='rgba(255,220,160,.35)';for(let i=0;i<5;i++)x.fillRect(cx-210+i*92,by-170,56,150);
  x.fillStyle='#2a1c16';x.beginPath();x.moveTo(cx-360,by-190);x.quadraticCurveTo(cx,by-150,cx+360,by-190);x.lineTo(cx+200,by-360);x.lineTo(cx-200,by-360);x.closePath();x.fill();
  x.fillStyle='rgba(255,236,200,.35)';x.beginPath();x.moveTo(cx-360,by-190);x.quadraticCurveTo(cx,by-150,cx+360,by-190);x.lineTo(cx+360,by-182);x.quadraticCurveTo(cx,by-142,cx-360,by-182);x.fill();
  steps(x,cx,by+60,cx,H-40,16,420,900,'#b8a68a',5110);
  maple(x,100,900,600,PR,5120,{light:LT});maple(x,W-80,880,640,PR,5121,{light:LT,lean:-.08});
  L.m=finish(c,5102,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');tourou(x,150,1330,300,false);tourou(x,W-150,1330,300,false);L.n=finish(c,5103,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,W-20,30,200,130,50,44,PR,5141);L.f=layerBlur(s,6)}
 return L}
// ===== H2 散りもみじ：苔と石の上に赤いじゅうたん =====
function H2(){const L={};const LT=[W*.3,100,1100];
 {const c=cv(),x=c.getContext('2d');sky(x,'#3a4a2a','#5a6a32',0,H);for(let i=0;i<8;i++)leafCloud(x,(i/7)*W,140+Math.sin(i)*40,170,140,1600,11,PR,5200+i,{light:LT});glow(x,LT[0],LT[1],700,.55,'255,246,220');L.b=finish(c,5201,{rim:false,g:6,blot:.03})}
 {const c=cv(),x=c.getContext('2d');const q=rng(5210);
  // 苔の地面に、散ったもみじがびっしり（奥は小さく、手前は大きく）
  const g=x.createLinearGradient(0,520,0,H);g.addColorStop(0,'#6a7a3a');g.addColorStop(1,'#3a4a22');x.fillStyle=g;x.fillRect(0,520,W,H-520);
  for(let i=0;i<5200;i++){const t=Math.pow(q(),.8),y=520+t*(H-520);leaf(x,q()*W,y,3+t*14,q()*6,PR[i%PR.length],7)}
  [[300,980,110,50],[700,1160,150,64]].forEach(([sx,sy,rx,ry])=>{const gg=x.createRadialGradient(sx-rx*.3,sy-ry*.4,4,sx,sy,rx);gg.addColorStop(0,'#8a8478');gg.addColorStop(1,'#4a463e');x.fillStyle=gg;x.beginPath();x.ellipse(sx,sy,rx,ry,0,0,7);x.fill();for(let k=0;k<30;k++)leaf(x,sx+(q()-.5)*rx*1.4,sy-ry*.4+(q()-.5)*ry,8+q()*6,q()*6,PR[k%PR.length],7)});
  tourou(x,640,900,360,false);
  L.m=finish(c,5202,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');maple(x,60,760,560,PR,5230,{light:LT,lean:.1});L.n=finish(c,5203,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');const q=rng(5240);for(let i=0;i<18;i++)leaf(sx,q()*W,q()*H*.8,14+q()*16,q()*6,PR[i%PR.length],7);L.f=layerBlur(s,1.5)}
 return L}
// ===== H3 朝の光：もみじのすき間から光の筋が石段に落ちる =====
function H3(){const L={};const LT=[W*.75,60,1100];
 {const c=cv(),x=c.getContext('2d');sky(x,'#fff2d0','#e8b880',0,H);glow(x,LT[0],LT[1],800,.9,'255,250,236');L.b=finish(c,5301,{rim:false,g:6,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  for(let r=0;r<3;r++)for(let i=0;i<8;i++)leafCloud(x,(i/7)*W+(r%2)*60-30,60+r*170,180,140,2200,11,PR,5310+r*10+i,{light:LT});
  x.fillStyle='#6a5040';x.beginPath();x.moveTo(W*.35,600);x.lineTo(W*.65,600);x.lineTo(W*.95,H);x.lineTo(W*.05,H);x.fill();
  steps(x,W/2,600,W/2,H-40,18,280,880,'#a8906e',5320);for(let s2 of[-1,1])for(let i=0;i<4;i++){const k=i/3;leafCloud(x,W/2+s2*(250+k*230),640+k*560,110+k*120,160+k*180,2000+k*2000,10+k*5,PR,5350+i+(s2>0?10:0),{light:LT})}
  // 光の筋
  x.save();x.globalCompositeOperation='lighter';for(let i=0;i<6;i++){const sx=W*.75-i*70,g=x.createLinearGradient(sx,0,sx-360,H);g.addColorStop(0,'rgba(255,240,200,.28)');g.addColorStop(1,'rgba(255,240,200,0)');x.fillStyle=g;x.beginPath();x.moveTo(sx-20,0);x.lineTo(sx+20,0);x.lineTo(sx-300,H);x.lineTo(sx-400,H);x.fill()}x.restore();
  L.m=finish(c,5302,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');trunk(x,[[30,H],[80,H-600],[40,H-1100],[120,H-1400]],60,16,'#3a2418',5330);trunk(x,[[W-30,H],[W-90,H-640],[W-50,H-1080],[W-140,H-1400]],60,16,'#3a2418',5331);L.n=finish(c,5303,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,40,H-60,220,140,50,46,PR,5341);L.f=layerBlur(s,7)}
 return L}
window.SCN=Object.assign(window.SCN||{},{H0,H1,H2,H3});
