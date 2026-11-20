// 11/20 H1 見上げた赤い天井 / H2 足もとの苔と散り紅葉 / H3 朝の光の参道（H0 と同じ描き方）
const PAL2=['#c8301e','#d9441f','#e8622a','#f08a2c','#b52418','#f2a33a','#a51c16'];
function glow(x,cx,cy,r,a,col='255,240,200'){const g=x.createRadialGradient(cx,cy,0,cx,cy,r);g.addColorStop(0,`rgba(${col},${a})`);g.addColorStop(1,`rgba(${col},0)`);x.fillStyle=g;x.fillRect(cx-r,cy-r,r*2,r*2)}
// 主役の1枚：本物に近いもみじ（7裂・ふちのぎざぎざ・切れ込みは浅め）
function mapleBig(x,S){const lob=[[-90,1],[-38,.9],[-142,.9],[8,.72],[-188,.72],[52,.42],[-232,.42]].sort((a,b)=>a[0]-b[0]);x.beginPath();
 const P=(a,r)=>[Math.cos(a*Math.PI/180)*S*r,Math.sin(a*Math.PI/180)*S*r];let first=true;
 const pts=[];for(let i=0;i<lob.length;i++){const [a,r]=lob[i];const nx=lob[(i+1)%lob.length];const an=i==lob.length-1?nx[0]+360:nx[0];
  // 葉先へ（ぎざぎざ）
  for(let k=0;k<=8;k++){const t=k/8;const aa=a-14+t*14,rr=(.42+t*(r-.42))*(1+(k%2?.05:0));pts.push(P(aa,rr))}
  for(let k=1;k<=8;k++){const t=k/8;const aa=a+t*14,rr=(r-t*(r-.42))*(1+(k%2?.05:0));pts.push(P(aa,rr))}
  const mid=(a+an)/2;if(an-a>30)pts.push(P(mid,.36))}
 pts.forEach((p,i)=>i?x.lineTo(...p):x.moveTo(...p));x.closePath()}
function H1(){const L={};const cx=520,cy=560;const LT=[cx,cy,620];
 {const c=cv(),x=c.getContext('2d');
  const g=x.createRadialGradient(cx,cy,0,cx,cy,900);g.addColorStop(0,'#fffbe8');g.addColorStop(.1,'#ffe6a8');g.addColorStop(.3,'#f2953c');g.addColorStop(.6,'#a8301c');g.addColorStop(1,'#3e0e0a');x.fillStyle=g;x.fillRect(0,0,W,H);
  const far=cv(),fx=far.getContext('2d');leafCloud(fx,cx,cy,760,900,7000,15,PAL2,71,{light:LT,shape:(u,v)=>Math.hypot(u*1.2,v)>.16+Math.sin(Math.atan2(v,u)*7)*.04});x.drawImage(layerBlur(far,4),0,0);
  x.globalCompositeOperation='screen';glow(x,cx,cy,260,.95);x.globalCompositeOperation='source-over';
  L.b=finish(c,701,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 四方から空へ向かう幹（見上げた形）
  const tk=[[-40,H+40,70,1],[W+40,H+40,70,-1],[-60,700,46,1],[W+60,820,46,-1],[200,H+60,40,1],[W-160,H+60,40,-1]];
  tk.forEach(([tx,ty,w,sd],i)=>{const dx=cx-tx,dy=cy-ty;const pts=[];for(let k=0;k<5;k++){const t=k/4*.72;pts.push([tx+dx*t+Math.sin(t*9+i)*26*sd,ty+dy*t])}trunk(x,pts,w,w*.18,'#2a1a12',720+i)});
  leafCloud(x,cx,cy,700,820,12000,9,PAL2,73,{light:LT,shape:(u,v)=>{const r=Math.hypot(u*1.15,v),a=Math.atan2(v,u);return r>.3+Math.sin(a*6)*.06+Math.sin(a*13)*.03&&r<1.25}});
  L.m=finish(layerBlur(c,.7),702,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 手前の枝先：くっきりした葉（逆光で透ける）
  const br=[[0,300,1],[W,180,-1],[0,1100,1],[W,1200,-1]];br.forEach(([bx,by,sd],i)=>{const ex=bx+sd*380,ey=by+(cy-by)*.35;
   x.strokeStyle='#2a160e';x.lineWidth=10;x.lineCap='round';x.beginPath();x.moveTo(bx,by);x.quadraticCurveTo((bx+ex)/2,by-40,ex,ey);x.stroke();
   const q=rng(80+i);for(let j=0;j<60;j++){const t=.25+q()*.8,px=bx+(ex-bx)*t+(q()-.5)*90,py=by+(ey-by)*t+(q()-.5)*90;const d=Math.hypot(px-cx,py-cy)/700;
    leaf(x,px,py,16+q()*16,q()*6,mix(mix(PAL2[j%7],'#ffd890',Math.max(0,.7-d)*.6),'#3a0806',q()*.2),7)}});
  L.n=finish(c,703,{rim:false,g:5,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,60,1360,260,160,60,48,PAL2,91);leafCloud(sx,W-40,1300,240,170,60,48,PAL2,92);leafCloud(sx,W-60,60,220,120,40,44,PAL2,93);L.f=layerBlur(s,7)}
 return L}
function H2(){const L={};const LT=[160,-60,1500];
 const MOSS=['#5e7a1e','#7a9a28','#4a6216','#94b236','#3a5010','#a8c444'];
 {const c=cv(),x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,W,H);g.addColorStop(0,'#7a9a30');g.addColorStop(.5,'#4a6418');g.addColorStop(1,'#26360c');x.fillStyle=g;x.fillRect(0,0,W,H);
  const q=rng(201);
  // 苔：小さな点を重ねてふかふかに（光は左上）
  for(let i=0;i<42000;i++){const xx=q()*W,yy=q()*H;const d=Math.hypot(xx-LT[0],yy-LT[1])/LT[2];let col=MOSS[i%6];col=mix(col,'#e8f0a0',Math.max(0,.75-d)*.45);col=mix(col,'#1a2406',Math.max(0,d-.6)*.6);x.fillStyle=rgba(col,.6);x.beginPath();x.ellipse(xx,yy,2+q()*5,1.5+q()*3,q()*3,0,7);x.fill()}
  // 苔の上の石（2つ・ふちに苔がかぶる）
  [[150,240,190,120,-.2],[790,520,150,95,.3]].forEach(([sx,sy,rx,ry,r])=>{x.save();x.translate(sx,sy);x.rotate(r);const sg=x.createRadialGradient(-rx*.3,-ry*.4,6,0,0,rx);sg.addColorStop(0,'#b4ae9c');sg.addColorStop(.6,'#7a7466');sg.addColorStop(1,'#3e3a30');x.fillStyle=sg;x.beginPath();for(let k=0;k<=24;k++){const a=k/24*Math.PI*2,rr=1+Math.sin(a*3+sx)*.07;x.lineTo(Math.cos(a)*rx*rr,Math.sin(a)*ry*rr)}x.fill();
   for(let m=0;m<900;m++){const a=q()*Math.PI*2,rr=.7+q()*.4;if(Math.sin(a)>.3&&q()<.6)continue;x.fillStyle=rgba(MOSS[m%6],.8);x.beginPath();x.ellipse(Math.cos(a)*rx*rr,Math.sin(a)*ry*rr,3+q()*5,2+q()*3,0,0,7);x.fill()}x.restore()});
  L.b=finish(c,801,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');const q=rng(211);
  // 散ったもみじ：下ほど厚く、上はぱらぱら（緑と赤の対比）
  for(let i=0;i<2600;i++){const yy=Math.pow(q(),.55)*H,k=yy/H,xx=q()*W;if(q()>.18+k*.9)continue;const d=Math.hypot(xx-LT[0],yy-LT[1])/LT[2];const s=12+k*18+q()*8;
   leaf(x,xx+3,yy+4,s,q()*6,'rgba(20,30,6,.35)',7);leaf(x,xx,yy,s,q()*6,mix(mix(PAL2[i%7],'#ffe6a8',Math.max(0,.8-d)*.4),'#2a0604',q()*.3),7)}
  L.m=finish(c,802,{rim:false,g:5,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 主役の1枚（大きく・葉脈あり）
  const hl=[500,980],S=150,rot=.25;x.save();x.translate(hl[0]+10,hl[1]+14);x.rotate(rot);x.fillStyle='rgba(20,24,6,.45)';mapleBig(x,S);x.fill();x.restore();
  x.save();x.translate(hl[0],hl[1]);x.rotate(rot);const lg=x.createRadialGradient(-30,-40,10,0,0,S);lg.addColorStop(0,'#f0702c');lg.addColorStop(.6,'#d23a1c');lg.addColorStop(1,'#9a1a12');x.fillStyle=lg;mapleBig(x,S);x.fill();
  x.strokeStyle='rgba(110,16,8,.55)';x.lineWidth=3;[[-90,1],[-38,.9],[-142,.9],[8,.72],[-188,.72],[52,.42],[-232,.42]].forEach(([a,r])=>{x.beginPath();x.moveTo(0,0);x.lineTo(Math.cos(a*Math.PI/180)*S*r*.92,Math.sin(a*Math.PI/180)*S*r*.92);x.stroke()});
  x.strokeStyle='#7a2a10';x.lineWidth=5;x.beginPath();x.moveTo(0,0);x.quadraticCurveTo(12,S*.35,-4,S*.62);x.stroke();x.restore();
  L.n=finish(c,803,{rim:false,g:4,blot:0})}
 {const c=cv(),x=c.getContext('2d');x.globalCompositeOperation='screen';const q=rng(231);
  for(let i=0;i<26;i++){const xx=q()*W,yy=q()*H,r=60+q()*140;const g3=x.createRadialGradient(xx,yy,0,xx,yy,r);g3.addColorStop(0,'rgba(255,232,160,.32)');g3.addColorStop(1,'rgba(255,210,130,0)');x.fillStyle=g3;x.beginPath();x.ellipse(xx,yy,r,r*.6,.5,0,7);x.fill()}
  glow(x,LT[0]+60,LT[1]+120,520,.35);L.f=c}
 return L}
function H3(){const L={};const sx=700,sy=330;const LT=[sx,sy,800];
 {const c=cv(),x=c.getContext('2d');
  const g=x.createRadialGradient(sx,sy,0,sx,sy,1300);g.addColorStop(0,'#fffef2');g.addColorStop(.12,'#ffe7b0');g.addColorStop(.4,'#e7a060');g.addColorStop(.75,'#8a3a26');g.addColorStop(1,'#3a1810');x.fillStyle=g;x.fillRect(0,0,W,H);
  // もやの中の遠い木（色がうすい）
  const far=cv(),fx=far.getContext('2d');leafCloud(fx,W/2,380,640,280,3200,16,PAL2.map(c=>mix(c,'#f4c8a0',.45)),301,{light:LT});x.drawImage(layerBlur(far,7),0,0);
  // 地面：もやの奥は明るく、手前は苔と落ち葉
  {const gg=x.createLinearGradient(0,600,0,H);gg.addColorStop(0,'rgba(236,190,140,.9)');gg.addColorStop(.35,'#8a6a34');gg.addColorStop(1,'#3a3a14');x.fillStyle=gg;x.fillRect(0,610,W,H-610);
   const q0=rng(305);for(let i=0;i<7000;i++){const k=Math.pow(q0(),.8),y=620+k*(H-620),xx=q0()*W;const col=mix(['#7a8a2e','#5a6a20','#9aa83a'][i%3],'#f0c890',Math.max(0,.5-k));x.fillStyle=rgba(col,.55);x.beginPath();x.ellipse(xx,y,2+k*12,1+k*4,0,0,7);x.fill()}
   for(let i=0;i<2600;i++){const k=Math.pow(q0(),.8),y=620+k*(H-620),xx=q0()*W;leaf(x,xx,y,1.5+k*11,q0()*6,mix(mix(PAL2[i%7],'#f4d0a0',Math.max(0,.5-k)*.8),'#3a0806',q0()*.3),7)}}
  {const hz=x.createLinearGradient(0,470,0,860);hz.addColorStop(0,'rgba(250,214,170,0)');hz.addColorStop(.4,'rgba(250,214,170,.95)');hz.addColorStop(1,'rgba(250,214,170,0)');x.fillStyle=hz;x.fillRect(0,470,W,390)}
  // 参道：下から奥へ曲がる道
  const pg=x.createLinearGradient(0,620,0,H);pg.addColorStop(0,'rgba(240,200,150,.9)');pg.addColorStop(1,'#6a2a16');x.fillStyle=pg;x.beginPath();x.moveTo(140,H);x.bezierCurveTo(330,1100,560,820,540,640);x.lineTo(590,640);x.bezierCurveTo(640,820,720,1100,820,H);x.fill();
  const q=rng(311);for(let i=0;i<3600;i++){const t=q(),y=640+Math.pow(t,1.3)*(H-640),k=(y-640)/(H-640),half=25+k*340,cxp=565-k*80;const xx=cxp+(q()-.5)*2*half*1.25;leaf(x,xx,y,2+k*14,q()*6,mix(mix(PAL2[i%7],'#ffe8c0',Math.max(0,.6-k)*.6),'#3a0806',q()*.25),7)}
  x.globalCompositeOperation='screen';glow(x,sx,sy,420,.95);
  for(let i=0;i<7;i++){const a=Math.PI*.62+(i-3)*.13+(q()-.5)*.05;const len=1800,wd=.018+q()*.03;const g4=x.createLinearGradient(sx,sy,sx+Math.cos(a)*len,sy+Math.sin(a)*len);g4.addColorStop(0,'rgba(255,244,210,.32)');g4.addColorStop(1,'rgba(255,244,210,0)');x.fillStyle=g4;x.beginPath();x.moveTo(sx,sy);x.lineTo(sx+Math.cos(a-wd)*len,sy+Math.sin(a-wd)*len);x.lineTo(sx+Math.cos(a+wd)*len,sy+Math.sin(a+wd)*len);x.fill()}
  x.globalCompositeOperation='source-over';
  L.b=finish(c,901,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 道の両側の古木（逆光で暗い幹）と赤い茂み
  [[330,820,22],[790,800,20],[170,1020,34],[900,980,32],[40,1300,56]].forEach(([tx,ty,w],i)=>{const sd=tx<W/2?-1:1;trunk(x,[[tx-sd*6,ty+420],[tx,ty],[tx+sd*14,ty-260],[tx+sd*40,ty-520],[tx+sd*90,ty-760],[tx+sd*160,ty-900]],w*1.5,w*.6,'#2e1a12',920+i)});
  leafCloud(x,W/2,180,700,420,13000,9,PAL2,321,{light:LT,shape:(u,v)=>{const ax=Math.abs(u);const edge=.15+ax*ax*.9+Math.sin(u*9)*.07+Math.sin(u*23)*.03;return v<edge&&!(Math.hypot((u-.19)*1.4,v-.15)<.28)}});
  L.m=finish(layerBlur(c,.8),902,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 道を歩く二人（逆光の影絵・小さく）
  const fig=(px,py,s,h)=>{x.fillStyle='#2a1610';x.beginPath();x.arc(px,py-h*s,7*s,0,7);x.fill();x.beginPath();x.moveTo(px-9*s,py-(h-10)*s);x.quadraticCurveTo(px,py-(h-6)*s,px+9*s,py-(h-10)*s);x.lineTo(px+7*s,py-18*s);x.lineTo(px+5*s,py);x.lineTo(px+1*s,py);x.lineTo(px,py-16*s);x.lineTo(px-1*s,py);x.lineTo(px-5*s,py);x.lineTo(px-7*s,py-18*s);x.fill();
   x.globalCompositeOperation='screen';x.strokeStyle='rgba(255,220,160,.7)';x.lineWidth=1.5;x.beginPath();x.arc(px,py-h*s,7*s,-1.8,.2);x.stroke();x.globalCompositeOperation='source-over'};
  fig(552,780,1.0,58);fig(576,782,.92,54);
  // 手前の土手の苔と葉
  for(const sd of[-1,1]){const ex=sd<0?0:W;const q=rng(sd>0?341:342);for(let i=0;i<2600;i++){const t=q(),y=H-q()*320*(1-t*.5);const xx=ex+(-sd)*t*260;x.fillStyle=rgba(['#6a7e22','#8aa030','#4a5a18'][i%3],.7);x.beginPath();x.ellipse(xx,y,4+q()*10,2+q()*5,0,0,7);x.fill()}
   for(let i=0;i<300;i++){const t=q();leaf(x,ex+(-sd)*t*250,H-q()*300*(1-t*.5),8+q()*10,q()*6,mix(PAL2[i%7],'#3a0806',q()*.3),7)}}
  L.n=finish(c,903,{rim:false,g:5,blot:0})}
 {const s=cv(),sx2=s.getContext('2d');leafCloud(sx2,30,60,220,180,60,46,PAL2,361);leafCloud(sx2,W-20,1380,240,140,50,46,PAL2,362);L.f=layerBlur(s,7)}
 return L}
window.SCN=Object.assign(window.SCN||{},{H1,H2,H3});
