// 11/20 見せ場：朝の光が差す、真っ赤な石段（光・奥行き・空気で「きれい」を出す）
const HV={x:470,y:500};
function layerBlur(src,px){const c=cv(src.width,src.height),x=c.getContext('2d');x.filter=`blur(${px}px)`;x.drawImage(src,0,0);return c}
function leafCloud(x,cx,cy,rx,ry,n,sz,pal,seed,{light=null,alpha=1,shape}={}){const q=rng(seed);
 for(let i=0;i<n;i++){let u,v;do{u=q()*2-1;v=q()*2-1}while(shape?!shape(u,v):(u*u+v*v>1));const px=cx+u*rx,py=cy+v*ry;let col=pal[Math.floor(q()*pal.length)];
  if(light){const d=Math.hypot(px-light[0],py-light[1])/light[2];col=mix(col,'#ffe08a',Math.max(0,.75-d)*.55);col=mix(col,'#3a0806',Math.max(0,Math.min(1,d-.5))*.55)}
  const s=sz*(.6+q()*.8);x.globalAlpha=alpha*(.55+q()*.45);
  if(q()<.28){x.fillStyle=col;x.beginPath();x.ellipse(px,py,s*.9,s*(.6+q()*.3),q()*3,0,7);x.fill()}else{leaf(x,px+s*.12,py+s*.18,s*1.05,q()*6,'rgba(60,8,10,.35)',7);leaf(x,px,py,s*1.15,q()*6,col,7)}}x.globalAlpha=1}
function H0(){const L={};const {x:vx,y:vy}=HV;const LT=[vx,vy-60,700];
 const PAL=['#b3121e','#c8241f','#d93a22','#e2582a','#9c0f1c','#eb8a3a','#7e0c18'];
 // ---- b：光の奥・遠い木・石段 ----
 {const c=cv(),x=c.getContext('2d');
  const g=x.createRadialGradient(vx,vy-40,10,vx,vy-40,900);g.addColorStop(0,'#fff8e0');g.addColorStop(.12,'#ffd98e');g.addColorStop(.35,'#e98a3c');g.addColorStop(.7,'#9a2c1a');g.addColorStop(1,'#4a120c');x.fillStyle=g;x.fillRect(0,0,W,H);
  // 遠いもみじ（ぼけ）
  const far=cv(),fx=far.getContext('2d');leafCloud(fx,vx,vy-160,520,300,2600,16,PAL,3,{light:LT,shape:(u,v)=>!(Math.abs(u)<.16&&v>.1)});leafCloud(fx,vx,vy+40,600,130,900,12,PAL,4,{light:LT,shape:(u,v)=>Math.abs(u)>.12});
  x.drawImage(layerBlur(far,5),0,0);
  // 光のにじみ
  x.globalCompositeOperation='screen';const g2=x.createRadialGradient(vx,vy-30,0,vx,vy-30,300);g2.addColorStop(0,'rgba(255,246,210,.95)');g2.addColorStop(1,'rgba(255,200,120,0)');x.fillStyle=g2;x.fillRect(0,0,W,H);x.globalCompositeOperation='source-over';
  // 地面（苔の土手）
  {const gg=x.createLinearGradient(0,vy,0,H);gg.addColorStop(0,'#a07a3a');gg.addColorStop(.2,'#5e6a2a');gg.addColorStop(1,'#26300f');x.fillStyle=gg;x.beginPath();x.moveTo(0,H);x.lineTo(0,vy+160);x.lineTo(vx-30,vy+8);x.lineTo(vx+30,vy+8);x.lineTo(W,vy+160);x.lineTo(W,H);x.fill()}
  const q=rng(8);for(let i=0;i<9000;i++){const k=Math.pow(q(),.9),y=vy+10+k*(H-vy),side=q()<.5?-1:1,xx=vx+side*(30+k*300+q()*(W*.6))*(.4+q()*.8);x.fillStyle=rgba(['#7a8a2e','#5a6a20','#9aa83a','#3e4a14'][i%4],.5);x.beginPath();x.ellipse(xx,y,2+k*14,1+k*5,0,0,7);x.fill()}
  for(let i=0;i<5000;i++){const k=Math.pow(q(),.9),y=vy+10+k*(H-vy),xx=q()*W;leaf(x,xx,y,1.5+k*12,q()*6,mix(PAL[i%7],'#3a0a06',.25+q()*.3),7)}
  {const hz=x.createLinearGradient(0,vy-40,0,vy+260);hz.addColorStop(0,'rgba(255,226,160,.9)');hz.addColorStop(1,'rgba(255,200,130,0)');x.fillStyle=hz;x.fillRect(0,vy-40,W,300)}
  // 石段：手前ほど広い。踏み面は散り紅葉でうめつくす
  const n=24,y0=H+20,y1=vy+10,w0=640,w1=36;const ys=[];for(let i=0;i<=n;i++)ys.push(y1+(y0-y1)*Math.pow(i/n,1.85));
  for(let i=0;i<n;i++){const ya=ys[i],yb=ys[i+1],k=(ya-y1)/(y0-y1),wa=w1+(w0-w1)*k,wb=w1+(w0-w1)*((yb-y1)/(y0-y1)),rise=(yb-ya)*.3;
   const tr=x.createLinearGradient(0,ya,0,yb);tr.addColorStop(0,'#8a3a22');tr.addColorStop(1,'#6a2618');x.fillStyle=tr;x.beginPath();x.moveTo(vx-wa/2,ya);x.lineTo(vx+wa/2,ya);x.lineTo(vx+wb/2,yb-rise);x.lineTo(vx-wb/2,yb-rise);x.fill();
   x.fillStyle='#2e221a';x.beginPath();x.moveTo(vx-wb/2,yb-rise);x.lineTo(vx+wb/2,yb-rise);x.lineTo(vx+wb/2,yb);x.lineTo(vx-wb/2,yb);x.fill();
   const s=1.5+k*12,cnt=Math.floor(wb*(yb-rise-ya)/(s*s)*2.6);for(let j=0;j<cnt;j++){const v=q(),yy=ya+(yb-rise-ya)*v,ww=wa+(wb-wa)*v,xx=vx-ww/2+ww*q();
    const d=Math.hypot(xx-LT[0],yy-LT[1])/900;leaf(x,xx,yy,s*(.7+q()*.6),q()*6,mix(mix(PAL[j%7],'#fff0b0',Math.max(0,.5-d)*.6),'#3a0806',q()*.25),7)}
   // 段の縁に光
   x.fillStyle=rgba('#ffe2a0',.25*(1-k));x.fillRect(vx-wb/2,yb-rise-1,wb,1.5+k*2)}
  // 木もれ日（段の上のやわらかい光のまだら）
  x.globalCompositeOperation='screen';for(let i=0;i<60;i++){const k=Math.pow(q(),.8),y=vy+30+k*(H-vy-30),w=40+k*560;const xx=vx+(q()-.5)*w;const r=8+k*70;const g3=x.createRadialGradient(xx,y,0,xx,y,r);g3.addColorStop(0,'rgba(255,224,150,.55)');g3.addColorStop(1,'rgba(255,200,120,0)');x.fillStyle=g3;x.beginPath();x.ellipse(xx,y,r,r*.35,0,0,7);x.fill()}
  // 光の筋
  for(let i=0;i<4;i++){const a=Math.PI/2+(q()-.5)*.9;const len=1500;const wd=.025+q()*.035;const g4=x.createLinearGradient(vx,vy-80,vx+Math.cos(a)*len,vy-80+Math.sin(a)*len);g4.addColorStop(0,'rgba(255,240,200,.18)');g4.addColorStop(1,'rgba(255,240,200,0)');x.fillStyle=g4;x.beginPath();x.moveTo(vx,vy-80);x.lineTo(vx+Math.cos(a-wd)*len,vy-80+Math.sin(a-wd)*len);x.lineTo(vx+Math.cos(a+wd)*len,vy-80+Math.sin(a+wd)*len);x.fill()}
  x.globalCompositeOperation='source-over';
  L.b=finish(c,601,{rim:false,g:7,blot:.03})}
 // ---- m：中ほどの古木の幹（逆光で縁が金色）と、上をおおう赤い天井 ----
 {const c=cv(),x=c.getContext('2d');
  const tk=[[vx-150,vy+120,16,-1],[vx+150,vy+120,16,1],[vx-250,vy+260,26,-1],[vx+250,vy+260,26,1]];
  tk.forEach(([tx,ty,w,sd],i)=>{trunk(x,[[tx,ty],[tx-sd*8,ty-160],[tx+sd*6,ty-320],[tx-sd*40,ty-470]],w,w*.5,'#2a1a12',900+i);
});
  leafCloud(x,vx,170,620,300,11000,8,PAL,21,{light:LT,shape:(u,v)=>v<.55-Math.abs(u)*.05+Math.sin(u*8)*.06&&!(Math.abs(u)<.18&&v>.25)});
  leafCloud(x,90,520,170,220,2600,8,PAL,22,{light:LT});leafCloud(x,W-90,520,170,220,2600,8,PAL,23,{light:LT});
  L.m=finish(layerBlur(c,.8),602,{rim:false,g:6,blot:0})}
 // ---- n：手前の大きな幹（左右）と苔の石垣 ----
 {const c=cv(),x=c.getContext('2d');
  for(const sd of[-1,1]){const ex=sd<0?0:W;
   const q=rng(sd>0?41:42);for(let i=0;i<4000;i++){const t=q(),y=H-q()*400*(1-t*.3);const xx=ex+(-sd)*t*300;if(y<H-420+t*60)continue;x.fillStyle=rgba(['#6a7e22','#8aa030','#4a5a18','#a8b840'][i%4],.7);x.beginPath();x.ellipse(xx,y,4+q()*12,2+q()*5,0,0,7);x.fill()}
   for(let i=0;i<500;i++){const t=q();leaf(x,ex+(-sd)*t*290,H-q()*380*(1-t*.5),7+q()*9,q()*6,mix(PAL[i%7],'#3a0806',q()*.3),7)}}
  for(const sd of[-1,1]){const X=v=>sd<0?v:W-v;
   trunk(x,[[X(40),H-230],[X(78),H-480],[X(46),H-700],[X(96),H-900],[X(70),H-1080],[X(150),H-1280]],84,34,'#4a2e1e',51+(sd>0));
   trunk(x,[[X(82),H-760],[X(150),H-860],[X(230),H-900],[X(300),H-980]],30,8,'#4a2e1e',53+(sd>0));
   trunk(x,[[X(76),H-1000],[X(20),H-1120],[X(-10),H-1200]],26,8,'#4a2e1e',55+(sd>0));
   leafCloud(x,X(260),H-1000,120,80,900,7,PAL,57+(sd>0),{light:LT})}
  L.n=finish(c,603,{rim:false,g:6,blot:0})}
 // ---- f：手前のぼけた大きな葉（奥行き） ----
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,40,80,200,160,60,46,PAL,61);leafCloud(sx,W-30,40,220,140,60,46,PAL,62);leafCloud(sx,W/2,H-20,500,60,40,40,PAL,63);
  L.f=layerBlur(s,7)}
 return L}
window.SCN=Object.assign(window.SCN||{},{H0});
