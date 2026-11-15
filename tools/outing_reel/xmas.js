// クリスマスの絵（scene: 'xmas'）。水彩の絵本のように canvas に描く。mode 0 昼の赤レンガ／1 夕方のツリー／2 夜
// 下絵（重い）は1回だけ描いてしまっておき、毎コマは電球・星のまたたきだけを上に重ねる。
function XR(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function xmCanvas(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c}
const XW=920,XH=1380;
function xmHex(h){h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function xmMix(a,b,k){const A=xmHex(a),B=xmHex(b);return'#'+A.map((v,i)=>Math.round(v+(B[i]-v)*k).toString(16).padStart(2,'0')).join('')}
// 紙のにじみ用の模様（粗いむら＋細かい粒）
let XNOISE=null;
function xmNoise(){if(XNOISE)return XNOISE;const r=XR(901);const s=xmCanvas(115,173),g=s.getContext('2d'),d=g.createImageData(115,173);
 for(let i=0;i<d.data.length;i+=4){const v=r()*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255}g.putImageData(d,0,0);
 const n=xmCanvas(XW,XH),c=n.getContext('2d');c.imageSmoothingEnabled=true;c.filter='blur(6px)';c.drawImage(s,0,0,XW,XH);c.filter='none';
 const f=xmCanvas(230,345),fg=f.getContext('2d'),fd=fg.createImageData(230,345);for(let i=0;i<fd.data.length;i+=4){const v=120+r()*135;fd.data[i]=fd.data[i+1]=fd.data[i+2]=v;fd.data[i+3]=255}fg.putImageData(fd,0,0);
 c.globalAlpha=.5;c.drawImage(f,0,0,XW,XH);XNOISE=n;return n}
const XL=xmCanvas(XW,XH),XG=XL.getContext('2d');
// 水彩でぬる：形をぬる→ふちに濃いにじみ→中に紙のむら。path(g) が形を作る
function wash(c,path,col,o){o=o||{};const g=XG;g.save();g.setTransform(1,0,0,1,0,0);g.globalCompositeOperation='source-over';g.globalAlpha=1;g.filter='none';g.clearRect(0,0,XW,XH);
 g.beginPath();path(g);
 if(o.grad){g.fillStyle=o.grad(g)}else g.fillStyle=col;g.globalAlpha=o.a==null?.92:o.a;g.fill();
 g.globalAlpha=o.edge==null?.5:o.edge;g.strokeStyle=o.ec||xmMix(col,'#2a1408',.35);g.lineWidth=o.ew||2.4;g.filter='blur(1.2px)';g.stroke();g.filter='none';
 g.globalCompositeOperation='source-atop';g.globalAlpha=o.gr==null?.22:o.gr;g.drawImage(xmNoise(),0,0);
 if(o.light!==false){const lg=g.createLinearGradient(0,o.ly0||0,0,o.ly1||XH);lg.addColorStop(0,'rgba(255,250,240,.16)');lg.addColorStop(1,'rgba(40,20,10,.12)');g.globalAlpha=1;g.fillStyle=lg;g.fillRect(0,0,XW,XH)}
 g.restore();c.drawImage(XL,0,0)}
// 手で描いたようにゆれる線（多角形）
function wob(g,pts,amp,seed){const r=XR(seed||1);g.moveTo(pts[0][0]+(r()-.5)*amp,pts[0][1]+(r()-.5)*amp);
 for(let i=1;i<=pts.length;i++){const a=pts[(i-1)%pts.length],b=pts[i%pts.length];const n=Math.max(1,Math.round(Math.hypot(b[0]-a[0],b[1]-a[1])/26));
  for(let k=1;k<=n;k++){const u=k/n;g.lineTo(a[0]+(b[0]-a[0])*u+(r()-.5)*amp,a[1]+(b[1]-a[1])*u+(r()-.5)*amp)}}g.closePath()}
function glow(c,x,y,r,rgb,a){if(a<=0)return;const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,`rgba(${rgb},${a})`);g.addColorStop(.3,`rgba(${rgb},${a*.4})`);g.addColorStop(1,`rgba(${rgb},0)`);c.fillStyle=g;c.fillRect(x-r,y-r,r*2,r*2)}

// ---------- 空 ----------
function xmSky(c,mode){const P=[['#a9c8de','#e6eef0','#fbeedb'],['#4d4785','#b26e98','#f2a985'],['#060a20','#141d48','#2b2b5c']][mode];
 const g=c.createLinearGradient(0,0,0,980);g.addColorStop(0,P[0]);g.addColorStop(.55,P[1]);g.addColorStop(1,P[2]);c.fillStyle=g;c.fillRect(0,0,XW,XH);
 // むら（水をたっぷり含んだ空）
 c.save();c.globalCompositeOperation=mode==2?'screen':'multiply';c.globalAlpha=mode==2?.05:.07;c.drawImage(xmNoise(),0,0);c.restore();
 const r=XR(3+mode);c.save();c.filter='blur(18px)';
 for(let i=0;i<(mode==2?3:9);i++){const x=r()*XW,y=90+r()*(mode==1?520:430),w=140+r()*260;
  c.globalAlpha=mode==2?.05:mode==1?.32:.55;c.fillStyle=mode==1?(i%2?'#ffd5bd':'#e7a3b5'):'#ffffff';c.beginPath();c.ellipse(x,y,w,w*.16,(r()-.5)*.1,0,7);c.fill();
  if(mode!=2){c.globalAlpha=.12;c.fillStyle=mode==1?'#7a4f86':'#9eb4c6';c.beginPath();c.ellipse(x+20,y+w*.1,w*.8,w*.06,0,0,7);c.fill()}}
 c.restore()}
function xmStars(c,seed){const r=XR(seed);for(let i=0;i<150;i++){const x=r()*XW,y=r()*700,s=r();c.fillStyle=`rgba(255,246,222,${.25+s*.7})`;c.beginPath();c.arc(x,y,.5+s*1.6,0,7);c.fill()}}
function xmMoon(c,x,y,R){c.save();c.globalCompositeOperation='screen';glow(c,x,y,R*6,'255,236,190',.25);c.restore();
 wash(c,g=>g.arc(x,y,R,0,7),'#fbefc8',{edge:.25,gr:.18,light:false});c.fillStyle='rgba(190,170,130,.22)';c.beginPath();c.arc(x-R*.3,y+R*.15,R*.22,0,7);c.arc(x+R*.28,y-R*.3,R*.13,0,7);c.arc(x+R*.2,y+R*.4,R*.1,0,7);c.fill()}
function xmGulls(c,seed,n){const r=XR(seed);c.strokeStyle='rgba(70,70,92,.65)';c.lineCap='round';for(let i=0;i<n;i++){const x=70+r()*480,y=200+r()*330,s=7+r()*11;c.lineWidth=1.6+s*.08;c.beginPath();c.moveTo(x-s,y+s*.1);c.quadraticCurveTo(x-s*.5,y-s*.55,x,y);c.quadraticCurveTo(x+s*.5,y-s*.55,x+s,y+s*.1);c.stroke()}}

// ---------- 観覧車（遠く） ----------
function xmWheel(c,cx,cy,R,mode,L){const col=mode==2?'rgba(170,190,240,.5)':mode==1?'rgba(120,90,130,.45)':'rgba(110,125,145,.5)';c.save();c.strokeStyle=col;c.lineWidth=2.2;
 c.beginPath();c.arc(cx,cy,R,0,7);c.stroke();c.lineWidth=1;c.beginPath();c.arc(cx,cy,R*.9,0,7);c.stroke();
 for(let i=0;i<30;i++){const a=i/30*Math.PI*2;c.beginPath();c.moveTo(cx,cy);c.lineTo(cx+Math.cos(a)*R,cy+Math.sin(a)*R);c.lineWidth=.7;c.stroke();
  c.fillStyle=col;c.fillRect(cx+Math.cos(a)*R*1.03-3,cy+Math.sin(a)*R*1.03-2,6,5);
  if(L)L.push({x:cx+Math.cos(a)*R,y:cy+Math.sin(a)*R,r:9,c:['255,130,180','130,200,255','255,220,130','160,255,200'][i%4],a:.9,p:i*.7,sp:1.2})}
 c.lineWidth=3;c.beginPath();c.moveTo(cx,cy);c.lineTo(cx-R*.32,cy+R*1.3);c.moveTo(cx,cy);c.lineTo(cx+R*.32,cy+R*1.3);c.stroke();c.restore()}

// ---------- 海 ----------
function xmSea(c,y0,y1,mode){const P=[['#a9c6d6','#7da3bb'],['#c48aa2','#7e5f8e'],['#1d2856','#0d1330']][mode];
 wash(c,g=>wob(g,[[-20,y0],[XW+20,y0],[XW+20,y1],[-20,y1]],3,7),P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,y1);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.15,gr:.25,light:false});
 const r=XR(4);c.strokeStyle=mode==2?'rgba(255,214,150,.22)':'rgba(255,255,255,.45)';c.lineWidth=1.3;for(let i=0;i<46;i++){const x=r()*XW,y=y0+5+r()*(y1-y0-8),l=14+r()*56;c.beginPath();c.moveTo(x,y);c.lineTo(x+l,y);c.stroke()}}

// ---------- 赤レンガ倉庫 ----------
function xmWarehouse(c,x,y,w,h,mode,seed,L){const r=XR(seed);const night=mode==2,top=y-h;
 const wall=night?'#5b2c2a':mode==1?'#b65a46':'#c4603f',wall2=night?'#331719':mode==1?'#7f3a35':'#97402c';
 // 屋根（灰色の瓦）
 const rh=h*.1;wash(c,g=>wob(g,[[x-8,top+2],[x+w*.035,top-rh],[x+w*.965,top-rh],[x+w+8,top+2]],2,seed),night?'#22202b':'#5b5763',{edge:.4,gr:.3});
 // 壁
 wash(c,g=>wob(g,[[x,top],[x+w,top],[x+w,y],[x,y]],2.5,seed+1),wall,{grad:g=>{const q=g.createLinearGradient(0,top,0,y);q.addColorStop(0,wall);q.addColorStop(1,wall2);return q},edge:.45,gr:.3});
 // れんがを少しだけ（全部は描かない＝絵本らしく）
 c.save();c.beginPath();c.rect(x,top,w,h);c.clip();c.strokeStyle=night?'rgba(0,0,0,.25)':'rgba(255,225,200,.32)';c.lineWidth=1.1;
 for(let i=0;i<w*h/2600;i++){const bx=x+r()*w,by=top+r()*h,bw=14+r()*8;c.strokeRect(bx,by,bw,6)}
 c.restore();
 // 白い石の帯
 const bands=[top+h*.015,top+h*.345,top+h*.67];for(const b of bands)wash(c,g=>wob(g,[[x-3,b],[x+w+3,b],[x+w+3,b+h*.028],[x-3,b+h*.028]],1.2,seed+b|0),night?'#8d817c':'#f1e3cd',{edge:.25,gr:.15,light:false});
 wash(c,g=>wob(g,[[x-6,y-h*.045],[x+w+6,y-h*.045],[x+w+6,y],[x-6,y]],1.5,seed+9),night?'#6b605c':'#dccab0',{edge:.3,gr:.2,light:false});
 // 窓（アーチ・3段）
 const cols=Math.max(4,Math.round(w/34)),ww=w/cols;
 for(let fl=0;fl<3;fl++){const fy=top+h*(.075+fl*.325),fh=h*.21;
  for(let i=0;i<cols;i++){const wx=x+i*ww+ww*.27,wd=ww*.46;const lit=night&&r()<.85;
   c.fillStyle=night?(lit?'#ffcf80':'#21181f'):mode==1?'#4a4560':'#3e5163';
   c.beginPath();c.moveTo(wx,fy+fh);c.lineTo(wx,fy+wd*.5);c.arc(wx+wd/2,fy+wd*.5,wd/2,Math.PI,0);c.lineTo(wx+wd,fy+fh);c.closePath();c.fill();
   if(!night){c.fillStyle='rgba(255,255,255,.28)';c.fillRect(wx+wd*.12,fy+wd*.4,wd*.16,fh*.55)}
   c.strokeStyle=night?'rgba(200,180,160,.6)':'rgba(250,240,224,.95)';c.lineWidth=2;c.stroke();
   if(lit&&L)L.push({x:wx+wd/2,y:fy+fh*.5,r:wd*1.7,c:'255,175,90',a:.32,p:r()*6,sp:.3,soft:1})}}
 // 鉄のバルコニー
 c.strokeStyle=night?'rgba(10,10,14,.85)':'rgba(40,36,40,.8)';c.lineWidth=1.6;const by=top+h*.355;c.beginPath();c.moveTo(x,by);c.lineTo(x+w,by);c.moveTo(x,by-h*.045);c.lineTo(x+w,by-h*.045);c.stroke();
 for(let xx=x;xx<x+w;xx+=7){c.beginPath();c.moveTo(xx,by);c.lineTo(xx,by-h*.045);c.stroke()}}

// ---------- ツリー（枝を1本ずつ重ねる） ----------
function xmTree(c,cx,by,h,mode,seed,L){const r=XR(seed);const night=mode==2,w=h*.4;
 const G=night?['#0b2620','#143a2e','#22543f','#2f6b4c']:mode==1?['#173b30','#24533f','#356e4f','#4f8a5e']:['#1c4535','#2c6047','#3f7d56','#5f9a68'];
 // 影
 c.save();c.globalAlpha=.3;c.fillStyle='#1a0e0a';c.filter='blur(8px)';c.beginPath();c.ellipse(cx,by+4,w*.85,h*.03,0,0,7);c.fill();c.restore();
 // 木の箱
 wash(c,g=>wob(g,[[cx-w*.17,by-h*.07],[cx+w*.17,by-h*.07],[cx+w*.15,by],[cx-w*.15,by]],1.5,seed),night?'#5a2018':'#a8342a',{edge:.4});
 c.fillStyle='#d8b057';c.fillRect(cx-w*.17,by-h*.07,w*.34,h*.007);
 // 枝：下の段から。暗い色→明るい色（左上から光）
 const tip=by-h*.95;const half=yy=>w*Math.pow((yy-tip)/(by-h*.08-tip),.92);
 for(let pass=0;pass<4;pass++){for(let i=0;i<520;i++){const v=Math.pow(r(),.75),yy=tip+v*(by-h*.1-tip);const hw=half(yy);if(hw<4)continue;
   const u=r()*2-1,xx=cx+u*hw*(pass==0?1:.92);if(pass>=2&&u>.35&&r()<.7)continue;if(pass==3&&(u>0||r()<.4))continue;
   const len=h*(.035+.03*v)*(1-pass*.12),ang=(u<0?Math.PI+.45:-.45)+(r()-.5)*.5+(u<0?-1:1)*Math.abs(u)*.2;
   c.fillStyle=G[pass];c.globalAlpha=.85;c.beginPath();c.ellipse(xx,yy+len*.25,len,len*.32,u<0?Math.PI-ang:ang,0,7);c.fill()}}
 c.globalAlpha=1;
 c.save();c.globalCompositeOperation='multiply';c.globalAlpha=.25;c.beginPath();c.moveTo(cx,tip);c.lineTo(cx+w,by-h*.08);c.lineTo(cx-w,by-h*.08);c.closePath();c.clip();c.drawImage(xmNoise(),0,0);c.restore();
 // 金のリボン
 c.save();c.lineCap='round';for(let k=0;k<5;k++){const y1=by-h*.14-k*h*.15,y0=y1-h*.07;const a=half(y0),b=half(y1);
  c.strokeStyle='rgba(120,80,20,.35)';c.lineWidth=h*.009;c.beginPath();c.moveTo(cx-a*.9,y0+4);c.quadraticCurveTo(cx,y0+(y1-y0)*.75+4,cx+b*.9,y1+4);c.stroke();
  c.strokeStyle=night?'rgba(245,205,120,.85)':'rgba(236,196,98,.95)';c.lineWidth=h*.007;c.beginPath();c.moveTo(cx-a*.9,y0);c.quadraticCurveTo(cx,y0+(y1-y0)*.75,cx+b*.9,y1);c.stroke()}c.restore();
 // オーナメント（影・つや）
 const OC=['#b8322a','#d9a93f','#efe4cf','#8d2a3c','#c98f2e'];
 for(let i=0;i<46;i++){const v=Math.pow(r(),.85),yy=tip+h*.06+v*(by-h*.16-tip),hw=half(yy)*.82,xx=cx+(r()*2-1)*hw,s=h*(.007+r()*.006);const col=OC[i%5];
  c.fillStyle='rgba(0,0,0,.28)';c.beginPath();c.arc(xx+s*.25,yy+s*.3,s,0,7);c.fill();
  const g=c.createRadialGradient(xx-s*.4,yy-s*.4,s*.1,xx,yy,s);g.addColorStop(0,xmMix(col,'#ffffff',.55));g.addColorStop(.5,col);g.addColorStop(1,xmMix(col,'#000000',.35));c.fillStyle=g;c.beginPath();c.arc(xx,yy,s,0,7);c.fill();
  c.strokeStyle='rgba(60,40,20,.5)';c.lineWidth=1;c.beginPath();c.moveTo(xx,yy-s);c.lineTo(xx,yy-s*1.6);c.stroke()}
 // 電球（またたくので位置だけ覚える）
 if(L)for(let i=0;i<150;i++){const v=Math.pow(r(),.8),yy=tip+h*.04+v*(by-h*.12-tip),hw=half(yy)*.9,xx=cx+(r()*2-1)*hw;L.push({x:xx,y:yy,r:h*(night?.026:.014),c:'255,212,128',a:night?.85:.5,p:r()*9,sp:2.2+r(),dot:h*.0032})}
 // 星
 const sx=cx,sy=tip-h*.015;if(L)L.push({x:sx,y:sy,r:h*(night?.17:.08),c:'255,222,140',a:night?.8:.45,p:0,sp:1,soft:1});
 c.save();c.translate(sx,sy);c.fillStyle='#f3cf68';c.strokeStyle='#9c6f20';c.lineWidth=1.8;c.beginPath();for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=(i%2?.42:1)*h*.042;c.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}c.closePath();c.fill();c.stroke();
 c.fillStyle='rgba(255,255,240,.6)';c.beginPath();c.moveTo(0,-h*.042);c.lineTo(h*.008,-h*.01);c.lineTo(-h*.008,-h*.01);c.closePath();c.fill();c.restore()}

// ---------- 屋台（品物とあかり） ----------
function xmHut(c,x,y,w,mode,seed,L){const r=XR(seed);const night=mode==2,h=w*.6;
 // 壁（板）
 wash(c,g=>wob(g,[[x,y-h],[x+w,y-h],[x+w,y],[x,y]],1.5,seed),night?'#3d2618':'#94603c',{edge:.45,gr:.3});
 c.strokeStyle=night?'rgba(0,0,0,.35)':'rgba(70,35,15,.3)';c.lineWidth=1;for(let yy=y-h+7;yy<y;yy+=7){c.beginPath();c.moveTo(x+2,yy);c.lineTo(x+w-2,yy);c.stroke()}
 // 窓口の中：あかりと品物
 const ox=x+w*.1,oy=y-h*.82,ow=w*.8,oh=h*.46;
 const ig=c.createLinearGradient(0,oy,0,oy+oh);ig.addColorStop(0,night?'#ffd896':'#f6e2bb');ig.addColorStop(1,night?'#d9883e':'#d7b07a');c.fillStyle=ig;c.fillRect(ox,oy,ow,oh);
 // 棚と品物（マグ・オーナメント・小さなツリー）
 c.fillStyle=night?'rgba(80,40,20,.6)':'rgba(110,70,40,.55)';c.fillRect(ox,oy+oh*.55,ow,2);
 for(let i=0;i<7;i++){const ix=ox+ow*(.08+i*.13),iy=oy+oh*.55,k=r();const cl=['#b8322a','#2e6b4a','#e2b84a','#f4ead8','#8d2a3c'][Math.floor(r()*5)];
  if(k<.4){c.fillStyle=cl;c.fillRect(ix-5,iy-12,10,12);c.strokeStyle=cl;c.lineWidth=2;c.beginPath();c.arc(ix+6,iy-6,3.5,-1.4,1.4);c.stroke()}
  else if(k<.75){c.fillStyle=cl;c.beginPath();c.arc(ix,iy-7,6,0,7);c.fill();c.fillStyle='rgba(255,255,255,.5)';c.beginPath();c.arc(ix-2,iy-9,2,0,7);c.fill()}
  else{c.fillStyle='#2e6b4a';c.beginPath();c.moveTo(ix,iy-18);c.lineTo(ix+7,iy);c.lineTo(ix-7,iy);c.closePath();c.fill()}}
 for(let i=0;i<5;i++){const ix=ox+ow*(.12+i*.19),iy=oy+oh*.25;c.fillStyle=['#c0392b','#e2b84a','#f4ead8','#2e6b4a','#b03050'][i];c.beginPath();c.arc(ix,iy,4.5,0,7);c.fill();c.strokeStyle='rgba(60,40,20,.5)';c.beginPath();c.moveTo(ix,oy);c.lineTo(ix,iy-4.5);c.stroke()}
 if(L)L.push({x:ox+ow/2,y:oy+oh*.5,r:w*.9,c:'255,170,80',a:night?.45:.12,p:r()*5,sp:.4,soft:1});
 // カウンター
 wash(c,g=>wob(g,[[x+w*.06,y-h*.38],[x+w*.94,y-h*.38],[x+w*.94,y-h*.3],[x+w*.06,y-h*.3]],1,seed+2),night?'#5a1f1a':'#a8322a',{edge:.3,light:false});
 // 屋根と白いふち
 wash(c,g=>wob(g,[[x-w*.1,y-h],[x+w/2,y-h-w*.34],[x+w*1.1,y-h]],1.5,seed+3),night?'#26180f':'#5a3a26',{edge:.4});
 wash(c,g=>wob(g,[[x-w*.1,y-h],[x+w/2,y-h-w*.34],[x+w*1.1,y-h],[x+w*1.05,y-h+6],[x+w/2,y-h-w*.27],[x-w*.05,y-h+6]],1,seed+4),night?'#d8d0e2':'#fbf7f0',{edge:.25,light:false,gr:.1});
 // ガーランドと電球
 c.strokeStyle='#2c5a3e';c.lineWidth=4;c.lineCap='round';c.beginPath();c.moveTo(x-w*.04,y-h+5);c.quadraticCurveTo(x+w/2,y-h+w*.12,x+w*1.04,y-h+5);c.stroke();
 if(L)for(let i=1;i<8;i++){const u=i/8,xx=x-w*.04+u*w*1.08,yy=y-h+5+Math.sin(u*Math.PI)*w*.055;L.push({x:xx,y:yy,r:night?16:9,c:'255,205,120',a:night?.8:.45,p:r()*6,sp:2.5,dot:2.4})}}

// ---------- 人（そぞろ歩き） ----------
function xmPerson(c,x,y,s,col,mode,seed){const r=XR(seed);const night=mode==2;const coat=night?xmMix(col,'#100810',.6):col,skin=night?'#3a2a2a':'#e9c7a8',hair=night?'#120a0a':['#3a2418','#5a3a22','#1e1410'][Math.floor(r()*3)];
 c.save();c.globalAlpha=.3;c.fillStyle='#1a0e0a';c.beginPath();c.ellipse(x,y,s*.32,s*.05,0,0,7);c.fill();c.restore();
 wash(c,g=>{g.moveTo(x-s*.07,y);g.lineTo(x-s*.08,y-s*.28);g.lineTo(x+s*.08,y-s*.28);g.lineTo(x+s*.07,y);},night?'#0a0608':'#2b2228',{edge:.2,light:false,gr:.1});
 wash(c,g=>wob(g,[[x-s*.2,y-s*.25],[x-s*.13,y-s*.72],[x+s*.13,y-s*.72],[x+s*.2,y-s*.25]],1,seed),coat,{edge:.35,gr:.25});
 c.fillStyle=night?'#2a1010':['#c0392b','#e2b84a','#f4ead8'][Math.floor(r()*3)];c.fillRect(x-s*.12,y-s*.74,s*.24,s*.07);
 c.fillStyle=skin;c.beginPath();c.arc(x,y-s*.83,s*.1,0,7);c.fill();c.fillStyle=hair;c.beginPath();c.arc(x,y-s*.86,s*.105,Math.PI*1.05,Math.PI*1.95);c.fill()}

// ---------- 電球のひも ----------
function xmString(c,x0,y0,x1,y1,sag,n,mode,L,seed){c.strokeStyle=mode==2?'rgba(20,14,16,.7)':'rgba(60,40,30,.5)';c.lineWidth=1.3;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2,(y0+y1)/2+sag,x1,y1);c.stroke();
 const r=XR(seed||5);if(L)for(let i=1;i<n;i++){const u=i/n,xx=(1-u)*(1-u)*x0+2*u*(1-u)*(x0+x1)/2+u*u*x1,yy=(1-u)*(1-u)*y0+2*u*(1-u)*((y0+y1)/2+sag)+u*u*y1+4;L.push({x:xx,y:yy,r:mode==2?20:11,c:'255,206,125',a:mode==2?.75:.4,p:r()*6,sp:2,dot:2.3})}}
function xmFlags(c,x0,y0,x1,y1,sag,n){c.strokeStyle='rgba(80,50,40,.55)';c.lineWidth=1.1;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2,(y0+y1)/2+sag,x1,y1);c.stroke();
 const cols=['#b8322a','#2c5a3e','#d9a93f','#efe4cf'];for(let i=1;i<n;i++){const u=i/n,xx=(1-u)*(1-u)*x0+2*u*(1-u)*(x0+x1)/2+u*u*x1,yy=(1-u)*(1-u)*y0+2*u*(1-u)*((y0+y1)/2+sag)+u*u*y1;
  wash(c,g=>{g.moveTo(xx-8,yy);g.lineTo(xx+8,yy);g.lineTo(xx,yy+20);g.closePath()},cols[i%4],{edge:.3,light:false,ew:1.5})}}
function xmGround(c,y0,mode){const P=[['#e0d2bd','#bba486'],['#c9a28c','#86655a'],['#2a2232','#110c17']][mode];
 wash(c,g=>wob(g,[[-20,y0],[XW+20,y0],[XW+20,XH+20],[-20,XH+20]],2,17),P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,XH);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.1,gr:.3,light:false});
 c.strokeStyle=mode==2?'rgba(255,255,255,.04)':'rgba(255,255,255,.22)';c.lineWidth=1;for(let y=y0+18,k=0;y<XH;y+=16+k*3,k++){c.beginPath();c.moveTo(0,y);c.lineTo(XW,y);c.stroke()}}

// ---------- 1ページ分の下絵 ----------
const XBASE={},XLIGHTS={};
function xmBase(mode){if(XBASE[mode])return;const cv=xmCanvas(XW,XH),c=cv.getContext('2d');const L=[];
 xmSky(c,mode);
 if(mode==0){
  c.save();c.globalCompositeOperation='screen';glow(c,250,560,460,'255,220,170',.5);c.restore();
  xmGulls(c,6,7);xmWheel(c,150,650,118,0,null);xmSea(c,792,862,0);
  xmWarehouse(c,-30,1015,560,195,0,11,L);xmWarehouse(c,560,985,400,150,0,12,L);
  xmGround(c,1010,0);
  xmFlags(c,-10,905,930,885,58,22);xmString(c,-10,980,930,955,64,24,0,L,8);
  xmHut(c,150,1085,100,0,26,L);xmHut(c,290,1095,92,0,27,L);
  xmTree(c,630,1190,540,0,5,L);
  xmPerson(c,410,1180,92,'#3e4f6e',0,31);xmPerson(c,438,1184,84,'#a8543a',0,32);xmPerson(c,860,1170,80,'#7b6a4e',0,33);
  xmHut(c,25,1240,170,0,21,L);xmHut(c,235,1285,150,0,22,L);xmHut(c,775,1300,150,0,23,L);
  xmPerson(c,560,1320,120,'#6b3a3a',0,34);xmPerson(c,600,1326,104,'#2e4a5e',0,35);
 }else if(mode==1){
  c.save();c.globalCompositeOperation='screen';glow(c,700,640,560,'255,190,150',.35);c.restore();
  xmWheel(c,790,700,105,1,null);xmSea(c,828,882,1);
  xmWarehouse(c,430,1005,540,215,1,13,L);
  xmGround(c,1000,1);
  xmString(c,560,1040,930,990,40,12,1,L,9);
  xmTree(c,320,1300,1060,1,7,L);
  xmHut(c,610,1290,170,1,24,L);
  xmPerson(c,820,1300,110,'#3e3a5e',1,36);xmPerson(c,852,1306,96,'#a8543a',1,37);
  c.save();c.globalCompositeOperation='multiply';c.fillStyle='rgba(110,70,120,.16)';c.fillRect(0,0,XW,XH);c.restore();
 }else{
  xmStars(c,8);xmMoon(c,210,250,60);
  xmWheel(c,120,700,118,2,L);xmSea(c,792,882,2);
  c.save();c.globalCompositeOperation='lighter';const r=XR(31);for(let i=0;i<70;i++){const x=r()*XW,y=800+r()*78;c.fillStyle=`rgba(255,200,120,${.1+r()*.25})`;c.fillRect(x,y,6+r()*26,1.6)}c.restore();
  xmWarehouse(c,-30,1025,560,205,2,11,L);xmWarehouse(c,520,995,450,165,2,12,L);
  xmGround(c,1020,2);
  xmString(c,-10,940,930,912,78,26,2,L,10);xmString(c,-10,1062,930,1040,48,22,2,L,11);
  c.save();c.globalCompositeOperation='lighter';glow(c,320,950,520,'255,170,90',.22);c.restore();
  xmTree(c,320,1235,800,2,5,L);
  xmHut(c,600,1245,150,2,21,L);xmHut(c,770,1275,130,2,22,L);
  xmPerson(c,560,1320,110,'#2a2a3a',2,38);xmPerson(c,590,1324,98,'#3a2228',2,39);
  c.save();c.globalCompositeOperation='lighter';glow(c,320,1240,300,'255,190,110',.2);c.restore();
  // 空気の中の小さなきらめき
  const r2=XR(55);for(let i=0;i<40;i++)L.push({x:r2()*XW,y:300+r2()*900,r:5+r2()*6,c:'255,236,190',a:.5,p:r2()*9,sp:1.5+r2(),dot:1.2});
 }
 // 絵本の紙：ふちを少し暗く
 const vg=c.createRadialGradient(460,660,320,460,700,1020);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,mode==2?'rgba(0,0,0,.42)':'rgba(80,50,30,.2)');c.fillStyle=vg;c.fillRect(0,0,XW,XH);
 c.save();c.globalCompositeOperation='multiply';c.globalAlpha=mode==2?.1:.1;c.drawImage(xmNoise(),0,0);c.restore();
 XBASE[mode]=cv;XLIGHTS[mode]=L}
const XOUT=xmCanvas(XW,XH),XO=XOUT.getContext('2d');
function xmPage(mode,t,u){xmBase(mode);t=t||0;const c=XO;c.globalCompositeOperation='source-over';c.drawImage(XBASE[mode],0,0);
 c.globalCompositeOperation='lighter';
 for(const l of XLIGHTS[mode]){const tw=l.soft?.85+.15*Math.sin(t*l.sp+l.p):.55+.45*Math.sin(t*l.sp+l.p);glow(c,l.x,l.y,l.r,l.c,l.a*tw);
  if(l.dot){c.fillStyle=`rgba(255,250,230,${(.55+.45*tw).toFixed(3)})`;c.beginPath();c.arc(l.x,l.y,l.dot,0,7);c.fill()}}
 c.globalCompositeOperation='source-over';if(typeof MG!='undefined'&&MG)xmFx(c,mode,t,u||0);return XOUT.toDataURL('image/jpeg',.92)}
