// 11/22 談山神社だけの描き下ろし：十三重塔ともみじ（昼の見せ場／朱の社殿と斜面のカエデ／夕暮れの石段と灯籠／夜のライトアップ）
// 筆は lib.js（紙の目・もみじの葉・茂み）。絵はこの場所のためにここで描く
const PAL=['#b3121e','#c8241f','#d93a22','#e2582a','#9c0f1c','#eb8a3a','#7e0c18'];
const PALK=['#e8a42c','#f0b83a','#d98a24','#e8702e','#c8781e','#f2c552'];   // 黄・橙（談山はカエデに黄が混ざる）
const PALM=PAL.concat(PAL,PALK);
function glow(x,cx,cy,r,a,col='255,240,200'){const g=x.createRadialGradient(cx,cy,0,cx,cy,r);g.addColorStop(0,`rgba(${col},${a})`);g.addColorStop(1,`rgba(${col},0)`);x.fillStyle=g;x.fillRect(cx-r,cy-r,r*2,r*2)}
function layerBlur(src,px){const c=cv(src.width,src.height),x=c.getContext('2d');x.filter=`blur(${px}px)`;x.drawImage(src,0,0);return c}
function leafCloud(x,cx,cy,rx,ry,n,sz,pal,seed,{light=null,alpha=1,shape,dark='#3a0806',hi='#ffe08a',edge=.16}={}){const q=rng(seed);const ph=[q()*9,q()*9,q()*9];
 // 輪郭は楕円＋ゆらぎ（ふわっとした木のかたまり）。shape は楕円の中でさらに切る
 const inside=(u,v)=>{const a=Math.atan2(v,u),r=Math.hypot(u,v);const lim=1-edge+edge*(.55*Math.sin(5*a+ph[0])+.3*Math.sin(9*a+ph[1])+.15*Math.sin(17*a+ph[2]));return r<lim&&(!shape||shape(u,v))};
 for(let i=0;i<n;i++){let u,v,tries=0;do{u=q()*2-1;v=q()*2-1;tries++}while(!inside(u,v)&&tries<80);if(tries>=80)continue;const px=cx+u*rx,py=cy+v*ry;let col=pal[Math.floor(q()*pal.length)];
  // かたまりの中の陰影：上と光の側は明るく、下は暗く
  col=mix(col,dark,Math.max(0,v)*.35);
  if(light){const d=Math.hypot(px-light[0],py-light[1])/light[2];col=mix(col,hi,Math.max(0,.75-d)*.55);col=mix(col,dark,Math.max(0,Math.min(1,d-.5))*.6)}
  const s=sz*(.6+q()*.8);x.globalAlpha=alpha*(.55+q()*.45);
  if(q()<.22){x.fillStyle=col;x.beginPath();x.ellipse(px,py,s*.9,s*(.6+q()*.3),q()*3,0,7);x.fill()}else{leaf(x,px+s*.12,py+s*.18,s*1.05,q()*6,'rgba(60,8,10,.35)',7);leaf(x,px,py,s*1.15,q()*6,col,7)}}x.globalAlpha=1}
// もみじの木：幹と枝を描いてから、いくつかの葉のかたまりを枝先にのせる
function maple(x,bx,by,h,pal,seed,o={}){const q=rng(seed);const lean=o.lean||0;const tc=o.trunk||'#3a2418';
 // 幹は低い所で分かれ、枝が横へ大きく広がる（傘の形）。葉のかたまりは枝先ごとに大小
 const fork=[bx+lean*h*.08,by-h*.28];trunk(x,[[bx,by],[bx+lean*h*.04,by-h*.14],fork],h*.05,h*.03,tc,seed);
 const tips=[];const nb=7;for(let i=0;i<nb;i++){const a=-Math.PI/2+(i-(nb-1)/2)*.42+(q()-.5)*.2+lean*.4;const l=h*(.3+q()*.2)*(1-Math.abs(i-(nb-1)/2)*.04);
  const t=[fork[0]+Math.cos(a)*l*1.15,fork[1]+Math.sin(a)*l*.7-h*.04];const m=[(fork[0]+t[0])/2+(q()-.5)*20,(fork[1]+t[1])/2-12];trunk(x,[fork,m,t],h*.022,h*.006,tc,seed+i+1);tips.push(t)}
 const R=h*.36;const cx=fork[0],cy=fork[1]-h*.24;
 leafCloud(x,cx,cy,R*1.25,R*.75,Math.floor(h*h*.03),o.sz||9,pal,seed+20,{...o,shape:(u,v)=>v<.82+Math.sin(u*9)*.08});
 tips.forEach((t,i)=>leafCloud(x,t[0],t[1]+h*.01,R*(.42+q()*.2),R*(.34+q()*.12),Math.floor(h*h*.009),o.sz||9,pal,seed+30+i,o))}
// 枝先から垂れるもみじ（画面の縁から入る手前の枝）
function hangBranch(x,pts,pal,seed,o={}){trunk(x,pts,o.w0||22,o.w1||4,o.trunk||'#2e1c12',seed);const pts2=pts;const q=rng(seed+5);
 for(let i=1;i<pts.length;i++){const [ax,ay]=pts[i-1],[bx,by]=pts[i];for(let k=0;k<3;k++){const t=q();const px=ax+(bx-ax)*t,py=ay+(by-ay)*t;leafCloud(x,px+(q()-.5)*30,py+40+q()*50,70+q()*50,45+q()*30,520,o.sz||10,pal,seed+i*10+k,o)}}}
// 山の稜線（かすみ）
function ridge(x,y,amp,col,seed,top=0){const q=rng(seed);x.fillStyle=col;x.beginPath();x.moveTo(0,H);let px=0,py=y;x.lineTo(0,y);const f1=.004+q()*.004,f2=.013+q()*.01,p1=q()*9,p2=q()*9;
 for(let xx=0;xx<=W;xx+=6){py=y-Math.sin(xx*f1+p1)*amp-Math.sin(xx*f2+p2)*amp*.35-(top?Math.max(0,1-Math.abs(xx-top[0])/top[1])*top[2]:0);x.lineTo(xx,py)}x.lineTo(W,H);x.fill()}
// ===== 十三重塔：初重だけ背が高く、上の12の屋根は詰まって重なる。檜皮ぶきの反った軒、上に相輪 =====
function pagoda(x,cx,by,Hh,o={}){const night=!!o.night;const q=rng(o.seed||13);
 const base=Hh*.035,body1=Hh*.12,bw1=Hh*.115;const R1=Hh*.33,RT=Hh*.175;const sp=[];let y=by-base-body1;
 // 石の基壇
 x.fillStyle=night?'#2a2420':'#8a8272';x.fillRect(cx-bw1*1.05,by-base,bw1*2.1,base);x.fillStyle=night?'rgba(255,200,120,.35)':'rgba(255,255,255,.25)';x.fillRect(cx-bw1*1.05,by-base,bw1*2.1,2);
 // 初重の壁（板扉・連子窓）
 const bx=cx-bw1/2;const g=x.createLinearGradient(bx,0,bx+bw1,0);
 if(night){g.addColorStop(0,'#c98a3a');g.addColorStop(.5,'#f3c070');g.addColorStop(1,'#8a5222')}else{g.addColorStop(0,'#8a3a22');g.addColorStop(.45,'#7a301e');g.addColorStop(1,'#3a1410')}
 x.fillStyle=g;x.fillRect(bx,by-base-body1,bw1,body1);
 x.fillStyle=night?'rgba(60,24,6,.75)':'rgba(30,14,6,.6)';const dw=bw1*.28;x.fillRect(cx-dw/2,by-base-body1*.8,dw,body1*.8);
 x.strokeStyle=night?'rgba(80,30,8,.6)':'rgba(30,14,6,.45)';x.lineWidth=1.2;for(let i=0;i<4;i++){const xx=bx+bw1*(.1+i*.27);x.beginPath();x.moveTo(xx,by-base-body1);x.lineTo(xx,by-base);x.stroke()}
 // 屋根の段（下から）
 const N=13;const gaps=[];for(let i=1;i<N;i++)gaps.push(Hh*(.043-.008*(i/N)));
 const roofs=[];for(let i=0;i<N;i++){const k=i/(N-1);const span=R1+(RT-R1)*Math.pow(k,.85);const th=Hh*(.03-.008*k);roofs.push({y,span,th});if(i<N-1)y-=gaps[i]}
 // 上の段の軸（屋根の間に少し見える）
 for(let i=1;i<N;i++){const r=roofs[i],w=r.span*.42;x.fillStyle=night?'#e0a050':'#8a3a26';x.fillRect(cx-w/2,r.y,w,roofs[i-1].y-r.y);
  x.fillStyle=night?'rgba(255,240,200,.5)':'rgba(240,230,210,.55)';x.fillRect(cx-w/2+2,r.y+r.th*.5,w-4,Math.max(1,(roofs[i-1].y-r.y)*.18))}
 // 屋根を下から順に（上の屋根が下の屋根の上に重なる）
 for(let i=0;i<N;i++){const {y:ry,span,th}=roofs[i];const L=cx-span/2,Rr=cx+span/2;const lift=th*.9+span*.03;
  // 軒の裏（垂木の影）
  x.beginPath();x.moveTo(L,ry-lift);x.quadraticCurveTo(cx-span*.3,ry-th*.15,cx,ry-th*.1);x.quadraticCurveTo(cx+span*.3,ry-th*.15,Rr,ry-lift);x.lineTo(Rr,ry-lift-th*.25);x.quadraticCurveTo(cx,ry-th*.3,L,ry-lift-th*.25);x.closePath();
  if(night){const gg=x.createLinearGradient(0,ry-th,0,ry+th*.3);gg.addColorStop(0,'#6a3410');gg.addColorStop(1,'#ffc66a');x.fillStyle=gg}else x.fillStyle='#24160e';x.fill();
  // 屋根の面（檜皮）
  x.beginPath();x.moveTo(L-th*.15,ry-lift-th*.2);x.quadraticCurveTo(cx-span*.3,ry-th*.55,cx-span*.12,ry-th*1.05);x.lineTo(cx,ry-th*2.1);x.lineTo(cx+span*.12,ry-th*1.05);x.quadraticCurveTo(cx+span*.3,ry-th*.55,Rr+th*.15,ry-lift-th*.2);
  x.quadraticCurveTo(cx,ry-th*.05,L-th*.15,ry-lift-th*.2);x.closePath();
  const rg=x.createLinearGradient(L,0,Rr,0);
  if(night){rg.addColorStop(0,'#1a0e0a');rg.addColorStop(.5,'#3a2014');rg.addColorStop(1,'#140a06')}else{rg.addColorStop(0,'#b08a64');rg.addColorStop(.3,'#8a6448');rg.addColorStop(.65,'#5a3e2c');rg.addColorStop(1,'#33221a')}
  x.fillStyle=rg;x.fill();
  // 軒先の白い線（光）と苔
  x.strokeStyle=night?'rgba(255,214,140,.95)':'rgba(255,236,200,.7)';x.lineWidth=night?2:1.6;x.beginPath();x.moveTo(L-th*.15,ry-lift-th*.2);x.quadraticCurveTo(cx,ry-th*.05,Rr+th*.15,ry-lift-th*.2);x.stroke();
  if(!night){x.save();x.clip();for(let k=0;k<span*.25;k++){x.fillStyle=rgba(['#7a8a3a','#5a6a2a','#9aa84a'][k%3],.35);x.beginPath();x.ellipse(L+q()*span,ry-th*(.2+q()*.9),3+q()*5,1.5,0,0,7);x.fill()}x.restore()}
 }
 // 相輪（九輪・水煙）
 const top=roofs[N-1].y-roofs[N-1].th*1.6;const sh=Hh*.2;
 x.fillStyle=night?'#ffd890':'#4a3a2a';x.fillRect(cx-Hh*.006,top-sh,Hh*.012,sh);
 for(let i=0;i<9;i++){const yy=top-sh*.22-i*sh*.065;const w=Hh*.028;x.fillStyle=night?'#ffe0a0':'#5a4a36';x.fillRect(cx-w/2,yy,w,Hh*.006)}
 x.fillStyle=night?'#fff0c0':'#3a2e22';x.beginPath();x.ellipse(cx,top-sh*.12,Hh*.022,Hh*.012,0,0,7);x.fill();
 x.beginPath();x.ellipse(cx,top-sh*.9,Hh*.014,Hh*.03,0,0,7);x.fill();x.beginPath();x.arc(cx,top-sh,Hh*.008,0,7);x.fill();
 return {top:top-sh,roofs}}
// 朱塗りの社殿（屋根・朱の柱・白い壁）
function shaden(x,cx,by,w,h,o={}){const roofH=h*.42;const L=cx-w/2;
 x.fillStyle='#f4ead8';x.fillRect(L+w*.05,by-h*.58,w*.9,h*.58);
 x.fillStyle='#c8381e';for(let i=0;i<=6;i++){const xx=L+w*.05+i*(w*.9/6);x.fillRect(xx-w*.012,by-h*.58,w*.024,h*.58)}
 x.fillRect(L+w*.05,by-h*.58,w*.9,h*.05);x.fillRect(L+w*.05,by-h*.25,w*.9,h*.03);
 x.fillStyle='rgba(30,10,4,.35)';x.fillRect(L+w*.05,by-h*.53,w*.9,h*.06);
 x.beginPath();x.moveTo(L-w*.06,by-h*.56);x.quadraticCurveTo(cx-w*.3,by-h*.6,cx-w*.25,by-h*.58-roofH);x.lineTo(cx+w*.25,by-h*.58-roofH);x.quadraticCurveTo(cx+w*.3,by-h*.6,L+w*1.06,by-h*.56);x.closePath();
 const g=x.createLinearGradient(0,by-h*.58-roofH,0,by-h*.56);g.addColorStop(0,'#5a4636');g.addColorStop(1,'#2a1e16');x.fillStyle=g;x.fill();
 x.strokeStyle='rgba(255,236,200,.55)';x.lineWidth=1.5;x.beginPath();x.moveTo(L-w*.06,by-h*.56);x.quadraticCurveTo(cx,by-h*.5,L+w*1.06,by-h*.56);x.stroke();
 x.fillStyle='#2a1e16';x.fillRect(cx-w*.25,by-h*.58-roofH-h*.03,w*.5,h*.04)}
// 石灯籠
function tourou(x,cx,by,h,lit){x.fillStyle='#6a645a';x.fillRect(cx-h*.05,by-h*.55,h*.1,h*.55);x.fillRect(cx-h*.16,by-h*.08,h*.32,h*.08);
 x.fillRect(cx-h*.14,by-h*.6,h*.28,h*.06);x.fillStyle=lit?'#ffd890':'#4a4438';x.fillRect(cx-h*.1,by-h*.8,h*.2,h*.2);x.fillStyle='#5a544a';x.fillRect(cx-h*.04,by-h*.8,h*.08,h*.2);
 x.beginPath();x.moveTo(cx-h*.24,by-h*.8);x.lineTo(cx,by-h*.95);x.lineTo(cx+h*.24,by-h*.8);x.closePath();x.fillStyle='#57514a';x.fill();x.beginPath();x.arc(cx,by-h*.97,h*.035,0,7);x.fill()}

// ===== H0 見せ場：昼、もみじの山に立つ十三重塔（左上から日の光・山のかすみ） =====
const SUN=[150,170];
function ground(x,y,col1,col2){const g=x.createLinearGradient(0,y,0,H);g.addColorStop(0,col1);g.addColorStop(1,col2);x.fillStyle=g;x.fillRect(0,y,W,H-y)}
function H0(){const L={};const LT=[SUN[0],SUN[1],1150];const pcx=640,pby=1150,PH=930;
 {const c=cv(),x=c.getContext('2d');
  sky(x,'#fbeed2','#efc68e',0,760);glow(x,SUN[0],SUN[1],760,.95,'255,250,230');
  ridge(x,560,46,'rgba(170,140,150,.4)',3,[700,300,70]);ridge(x,640,40,'rgba(150,100,96,.45)',4);
  // 遠い山の紅葉（ぼかして空気の奥行き）
  // 奥ほど淡く霞む紅葉の山（3列）
  for(let row=0;row<3;row++){const far=cv(),fx=far.getContext('2d');const y=600+row*130;const k=row/2;
   {const g=fx.createLinearGradient(0,y-40,0,y+300);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(.3,mix('#c88a6a','#7a2a18',k));g.addColorStop(1,mix('#c88a6a','#5a1a10',k));fx.fillStyle=g;fx.fillRect(0,y-40,W,H)}
   for(let i=0;i<9+row*2;i++)leafCloud(fx,(i/(8+row*2))*W+(row%2)*40-20,y+(i%3)*14,120+row*20,70+row*14,900+row*500,8+row*3,PALM,100+row*20+i,{light:LT});
   const hzA=[.55,.3,.08][row];fx.globalCompositeOperation='source-atop';fx.fillStyle=`rgba(255,236,214,${hzA})`;fx.fillRect(0,0,W,H);fx.globalCompositeOperation='source-over';
   x.drawImage(layerBlur(far,[5,3,1.5][row]),0,0)}
  {const hz=x.createLinearGradient(0,440,0,760);hz.addColorStop(0,'rgba(255,240,210,0)');hz.addColorStop(.5,'rgba(255,240,214,.7)');hz.addColorStop(1,'rgba(255,226,190,0)');x.fillStyle=hz;x.fillRect(0,440,W,320)}
  L.b=finish(c,1101,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 塔の後ろ・左右のもみじの木
  leafCloud(x,W/2,1150,620,170,9000,10,PALM,26,{light:LT,edge:.1});
  maple(x,300,1040,520,PALM,21,{light:LT});maple(x,960,1020,540,PAL,22,{light:LT,lean:-.2});
  {const pc=cv(),px=pc.getContext('2d');pagoda(px,pcx,pby,PH,{seed:7});px.globalCompositeOperation='source-atop';const x0=x;{const x=px;const lg=x.createLinearGradient(pcx-PH*.18,0,pcx+PH*.05,0);lg.addColorStop(0,'rgba(255,214,150,.45)');lg.addColorStop(1,'rgba(255,214,150,0)');x.fillStyle=lg;x.fillRect(pcx-PH*.2,pby-PH*1.1,PH*.25,PH*1.1)}x0.drawImage(pc,0,0)}
  // 足もとの低い木
  maple(x,380,1270,330,PALM,23,{light:LT});maple(x,890,1280,320,PALM,24,{light:LT});
  {const hz=x.createLinearGradient(0,1000,0,1180);hz.addColorStop(0,'rgba(255,236,206,0)');hz.addColorStop(.6,'rgba(255,236,206,.35)');hz.addColorStop(1,'rgba(255,236,206,0)');x.globalCompositeOperation='source-atop';x.fillStyle=hz;x.fillRect(0,1000,W,180);x.globalCompositeOperation='source-over'}
  L.m=finish(c,1102,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  // 手前：左上から垂れる枝と、下の斜面の紅葉
  leafCloud(x,W/2,H+40,720,250,9000,13,PALM,34,{light:[W/2,H-300,900]});
  L.n=finish(c,1103,{rim:false,g:6,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,60,120,260,150,60,46,PAL,60);leafCloud(sx,W-10,40,170,140,40,46,PAL,61);leafCloud(sx,30,H-40,230,150,50,46,PAL,62);L.f=layerBlur(s,7)}
 return L}

// ===== H1 朱の社殿と、山の斜面いっぱいのカエデ（見上げる） =====
function H1(){const L={};const LT=[720,140,1250];
 {const c=cv(),x=c.getContext('2d');sky(x,'#d6e4ea','#f6e6c8',0,460);glow(x,LT[0],LT[1],620,.85,'255,250,232');
  const far=cv(),fx=far.getContext('2d');ground(fx,380,'#9a3a20','#5a1c12');
  for(let i=0;i<10;i++)leafCloud(fx,(i/9)*W,380+(i%2)*40,140,110,1400,12,PALM,200+i,{light:LT});
  for(let r=1;r<4;r++)for(let i=0;i<9;i++)leafCloud(fx,(i/8)*W+(r%2)*50-25,380+r*110+(i%2)*20,150,100,1500,12,PALM,230+r*10+i,{light:LT});
  x.drawImage(layerBlur(far,3.5),0,0);
  L.b=finish(c,1201,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  // 斜面の上の朱の社殿と、そこへ上がる石段
  for(let i=0;i<6;i++)maple(x,80+i*160,620+(i%2)*30,300,PALM,300+i,{light:LT});
  shaden(x,470,720,420,240);
  ground(x,720,'#6a4a30','#3a2618');
  const n=16;for(let i=0;i<n;i++){const k=i/n,yy=720+k*560,w=120+k*330;x.fillStyle=mix('#a49a88','#5a5244',k*.5);x.fillRect(470-w/2,yy,w,560/n*.68);x.fillStyle='rgba(40,30,20,.6)';x.fillRect(470-w/2,yy+560/n*.68,w,560/n*.32);
   const q=rng(400+i);for(let j=0;j<w*.08;j++)leaf(x,470-w/2+q()*w,yy+q()*14,3+k*8,q()*6,PALM[j%PALM.length],7)}
  L.m=finish(c,1202,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  maple(x,70,1300,760,PALM,61,{light:LT,lean:.15});maple(x,W-60,1320,780,PAL,62,{light:LT,lean:-.15});
  L.n=finish(c,1203,{rim:false,g:6,blot:0})}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,W-40,30,240,150,40,46,PALM,71);leafCloud(sx,40,H-50,230,150,50,46,PAL,72);L.f=layerBlur(s,7)}
 return L}

// ===== H2 夕暮れ：灯籠に灯がともる石段（混む昼を外して、夕方から） =====
const LAN=[[230,1060,150],[700,1060,150],[330,840,96],[600,840,96],[385,730,64],[540,730,64]];
function H2(){const L={};const LT=[W/2,600,700];
 {const c=cv(),x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,700);g.addColorStop(0,'#26285a');g.addColorStop(.45,'#8a4a72');g.addColorStop(.82,'#f2905e');g.addColorStop(1,'#ffcf86');x.fillStyle=g;x.fillRect(0,0,W,H);
  glow(x,W/2,640,520,.75,'255,210,150');
  ridge(x,600,36,'#4a2a44',8,[460,260,40]);ridge(x,650,26,'#2e1a28',9);
  L.b=finish(c,1301,{rim:false,g:7,blot:.03})}
 {const c=cv(),x=c.getContext('2d');
  ground(x,650,'#3a2228','#140a0e');
  const n=22,y0=H+10,y1=650;for(let i=0;i<n;i++){const k1=i/n,k2=(i+1)/n;const ya=y1+(y0-y1)*Math.pow(k1,1.7),yb=y1+(y0-y1)*Math.pow(k2,1.7);const wa=70+560*Math.pow(k1,1.1),wb=70+560*Math.pow(k2,1.1);
   x.fillStyle=mix('#8a7676','#3a2c30',.25+k1*.45);x.fillRect(W/2-wa/2,ya,wa,(yb-ya)*.7);x.fillStyle='#1a1014';x.fillRect(W/2-wb/2,ya+(yb-ya)*.7,wb,(yb-ya)*.3);
   x.fillStyle='rgba(255,206,140,.35)';x.fillRect(W/2-wa/2,ya,wa,1.5)}
  const OP={light:LT,dark:'#1a0406',hi:'#ffbe7a'};
  maple(x,120,760,560,PAL,91,OP);maple(x,W-110,760,580,PAL,92,{...OP,lean:-.1});maple(x,300,680,280,PALM,93,OP);maple(x,650,680,280,PALM,94,OP);
  LAN.forEach(([lx,ly,lh])=>tourou(x,lx,ly,lh,true));
  L.m=finish(c,1302,{rim:false,g:6,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  x.globalCompositeOperation='lighter';LAN.forEach(([lx,ly,lh])=>{glow(x,lx,ly-lh*.7,lh*1.1,.9,'255,200,120');glow(x,lx,ly-lh*.3,lh*2.2,.35,'255,160,80')});
  L.n=c}
 {const s=cv(),sx=s.getContext('2d');leafCloud(sx,20,40,220,180,50,46,PAL,95,{dark:'#1a0404'});leafCloud(sx,W-10,H-60,240,160,50,46,PAL,96,{dark:'#1a0404'});L.f=layerBlur(s,7)}
 return L}

// ===== H3 夜：ライトアップで浮かぶ塔と、照らされたもみじ =====
function H3(){const L={};const pcx=470,pby=1110,PH=980;const LT=[pcx,pby-160,600];const OP={light:LT,dark:'#0c0208',hi:'#ffcf80'};
 {const c=cv(),x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,H);g.addColorStop(0,'#060920');g.addColorStop(.55,'#121a40');g.addColorStop(1,'#1c1636');x.fillStyle=g;x.fillRect(0,0,W,H);
  const q=rng(5);for(let i=0;i<300;i++){const s=q()*1.8+.3;x.fillStyle=`rgba(255,250,235,${.3+q()*.6})`;x.beginPath();x.arc(q()*W,q()*720,s,0,7);x.fill()}
  ridge(x,800,40,'#0c0e26',11);
  L.b=finish(c,1401,{rim:false,g:6,blot:.02})}
 {const c=cv(),x=c.getContext('2d');
  maple(x,170,1060,560,PAL,111,OP);maple(x,790,1060,560,PAL,112,{...OP,lean:-.1});
  pagoda(x,pcx,pby,PH,{night:true,seed:9});
  maple(x,260,1260,340,PAL,113,{...OP,light:[pcx,pby,560]});maple(x,700,1270,330,PAL,114,{...OP,light:[pcx,pby,560]});
  L.m=finish(c,1402,{rim:false,g:5,blot:0})}
 {const c=cv(),x=c.getContext('2d');
  hangBranch(x,[[W+30,300],[W-90,265],[W-210,290],[W-330,270]],PAL,121,{dark:'#0c0208',hi:'#ff9a60',light:[W-200,520,420]});
  leafCloud(x,W/2,H+30,720,230,8000,13,PAL,122,{light:[W/2,H-260,700],dark:'#0c0208',hi:'#ffb070'});
  L.n=finish(c,1403,{rim:false,g:5,blot:0})}
 {const c=cv(),x=c.getContext('2d');x.globalCompositeOperation='lighter';glow(x,pcx,pby-PH*.42,PH*.5,.3,'255,200,120');glow(x,pcx,pby,380,.45,'255,170,90');L.f=c}
 return L}
window.SCN=Object.assign(window.SCN||{},{H0,H1,H2,H3});
