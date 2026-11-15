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
 c.save();c.globalCompositeOperation='source-atop';c.globalAlpha=.1;c.drawImage(xmNoise(),0,0);c.restore();
 // 葉の細かい針：光の当たる左は明るく、右と内側は暗く
 c.save();c.globalCompositeOperation='source-atop';c.lineCap='round';for(let i=0;i<2600;i++){const v=Math.pow(r(),.8),yy=tip+v*(by-h*.1-tip),hw=half(yy),u=r()*2-1,xx=cx+u*hw*.95;const lit=u<-.1&&r()<.75;
  c.strokeStyle=lit?(night?'rgba(120,170,120,.35)':'rgba(170,215,150,.45)'):(r()<.5?'rgba(5,25,15,.35)':'rgba(40,90,60,.3)');c.lineWidth=h*.0022+.4;const a=(u<0?Math.PI+.5:-.5)+(r()-.5)*.9,l=h*(.008+r()*.012);c.beginPath();c.moveTo(xx,yy);c.lineTo(xx+Math.cos(a)*l,yy+Math.sin(a)*l*.6);c.stroke()}
 // 枝の上の雪（昼と夕方）・内側の影
 if(!night){for(let i=0;i<160;i++){const v=Math.pow(r(),.8),yy=tip+v*(by-h*.12-tip),hw=half(yy),xx=cx+(r()*2-1)*hw*.85;c.fillStyle='rgba(255,255,255,.55)';c.beginPath();c.ellipse(xx,yy,h*(.006+r()*.01),h*.003,(r()-.5)*.5,0,7);c.fill()}}
 const ig=c.createLinearGradient(cx-w,0,cx+w,0);ig.addColorStop(0,'rgba(0,0,0,0)');ig.addColorStop(.55,'rgba(0,0,0,.06)');ig.addColorStop(1,'rgba(0,10,5,.32)');c.fillStyle=ig;c.fillRect(cx-w,tip,w*2,by-tip);c.restore();
 // 金の玉のガーランド（細い玉をつなぐ）
 c.save();for(let k=0;k<5;k++){const y1=by-h*.14-k*h*.15,y0=y1-h*.07;const a=half(y0),b=half(y1);const n=Math.round((a+b)/(h*.0065));
  for(let i=0;i<=n;i++){const u=i/n,x=(1-u)*(1-u)*(cx-a*.9)+2*u*(1-u)*cx+u*u*(cx+b*.9),y=(1-u)*(1-u)*y0+2*u*(1-u)*(y0+(y1-y0)*.75)+u*u*y1;const rr=h*.0031;
   c.fillStyle='rgba(60,35,10,.35)';c.beginPath();c.arc(x+rr*.4,y+rr*.6,rr,0,7);c.fill();
   const g=c.createRadialGradient(x-rr*.4,y-rr*.4,rr*.1,x,y,rr);g.addColorStop(0,night?'#fff3cf':'#fff6dc');g.addColorStop(.5,night?'#e9be6a':'#e2b65c');g.addColorStop(1,'#8a6224');c.fillStyle=g;c.beginPath();c.arc(x,y,rr,0,7);c.fill()}}c.restore();
 // オーナメント（影・つや）
 const OC=['#b8322a','#d9a93f','#efe4cf','#8d2a3c','#c98f2e'];
 for(let i=0;i<46;i++){const v=Math.pow(r(),.85),yy=tip+h*.06+v*(by-h*.16-tip),hw=half(yy)*.82,xx=cx+(r()*2-1)*hw,s=h*(.007+r()*.006);const col=OC[i%5];
  c.fillStyle='rgba(0,0,0,.28)';c.beginPath();c.arc(xx+s*.25,yy+s*.3,s,0,7);c.fill();
  const g=c.createRadialGradient(xx-s*.4,yy-s*.4,s*.1,xx,yy,s);g.addColorStop(0,xmMix(col,'#ffffff',.55));g.addColorStop(.5,col);g.addColorStop(1,xmMix(col,'#000000',.35));c.fillStyle=g;c.beginPath();c.arc(xx,yy,s,0,7);c.fill();
  c.strokeStyle='rgba(60,40,20,.5)';c.lineWidth=1;c.beginPath();c.moveTo(xx,yy-s);c.lineTo(xx,yy-s*1.6);c.stroke()}
 // 電球（またたくので位置だけ覚える）
 if(L)for(let i=0;i<150;i++){const v=Math.pow(r(),.8),yy=tip+h*.04+v*(by-h*.12-tip),hw=half(yy)*.9,xx=cx+(r()*2-1)*hw;L.push({x:xx,y:yy,r:h*(night?.026:.014),c:'255,212,128',a:night?.85:.5,p:r()*9,sp:2.2+r(),dot:h*.0032})}
 // 星
 const sx=cx,sy=tip-h*.015;if(L)L.push({x:sx,y:sy,r:h*(night?.11:.06),c:'255,222,140',a:night?.6:.35,p:0,sp:1,soft:1});
 c.save();c.translate(sx,sy);c.fillStyle='#f3cf68';c.strokeStyle='#9c6f20';c.lineWidth=1.8;c.beginPath();for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=(i%2?.42:1)*h*.042;c.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}c.closePath();c.fill();c.stroke();
 c.fillStyle='rgba(255,255,240,.6)';c.beginPath();c.moveTo(0,-h*.042);c.lineTo(h*.008,-h*.01);c.lineTo(-h*.008,-h*.01);c.closePath();c.fill();c.restore()}

// ---------- 屋台（雪の屋根・中のあかり・もみの木のガーランド・ランタン） ----------
function xmHut(c,x,y,w,mode,seed,L){const r=XR(seed);const night=mode==2,dusk=mode==1,h=w*.62;
 // 板の壁：縦の板、下ほど暗い
 const wd=night?['#4a2e1e','#2a1810']:dusk?['#8e5a3c','#5e3826']:['#a8714a','#7a4c30'];
 wash(c,g=>wob(g,[[x,y-h],[x+w,y-h],[x+w,y],[x,y]],1.2,seed),wd[0],{grad:g=>{const q=g.createLinearGradient(0,y-h,0,y);q.addColorStop(0,wd[0]);q.addColorStop(1,wd[1]);return q},edge:.45,gr:.35});
 c.save();c.strokeStyle=night?'rgba(0,0,0,.35)':'rgba(60,30,12,.28)';c.lineWidth=1;for(let xx=x+w/14;xx<x+w;xx+=w/14){c.beginPath();c.moveTo(xx,y-h+2);c.lineTo(xx+(r()-.5)*1.5,y-1);c.stroke()}c.restore();
 // 窓口：中は暖かいあかり（上が明るい）
 const ox=x+w*.09,oy=y-h*.84,ow=w*.82,oh=h*.5;
 const ig=c.createLinearGradient(0,oy,0,oy+oh);ig.addColorStop(0,night?'#ffe2a6':'#fbe9c6');ig.addColorStop(.6,night?'#f2a85a':'#e9c491');ig.addColorStop(1,night?'#a5562a':'#c79a68');c.fillStyle=ig;c.fillRect(ox,oy,ow,oh);
 c.fillStyle='rgba(80,40,15,.25)';c.fillRect(ox,oy,ow,4);c.fillRect(ox,oy,3,oh);c.fillRect(ox+ow-3,oy,3,oh);
 // つるした飾り
 for(let i=0;i<9;i++){const ix=ox+ow*(.07+i*.108),len=oh*(.12+r()*.18),iy=oy+len;const cl=['#c0392b','#e2b84a','#f4ead8','#2e6b4a','#b03050'][Math.floor(r()*5)];
  c.strokeStyle='rgba(70,40,20,.5)';c.lineWidth=.8;c.beginPath();c.moveTo(ix,oy+3);c.lineTo(ix,iy-3);c.stroke();
  const gg=c.createRadialGradient(ix-1.2,iy-1.4,.3,ix,iy,3.6);gg.addColorStop(0,xmMix(cl,'#ffffff',.6));gg.addColorStop(1,cl);c.fillStyle=gg;c.beginPath();c.arc(ix,iy,3.4,0,7);c.fill()}
 // 棚：品物を小さく、たくさん
 const sy=oy+oh*.62;c.fillStyle='rgba(90,50,25,.65)';c.fillRect(ox+2,sy,ow-4,2.2);
 for(let i=0;i<14;i++){const ix=ox+ow*(.05+i*.066),k=r();const cl=['#b8322a','#2e6b4a','#e2b84a','#f4ead8','#8d2a3c','#c97b3a'][Math.floor(r()*6)];
  if(k<.3){c.fillStyle=cl;c.fillRect(ix-3,sy-8,6,8);c.strokeStyle=cl;c.lineWidth=1.3;c.beginPath();c.arc(ix+3.5,sy-4,2.4,-1.4,1.4);c.stroke()}
  else if(k<.55){c.fillStyle='#b5713a';c.beginPath();c.moveTo(ix,sy-1);c.bezierCurveTo(ix-6,sy-6,ix-3,sy-11,ix,sy-8);c.bezierCurveTo(ix+3,sy-11,ix+6,sy-6,ix,sy-1);c.fill();c.strokeStyle='rgba(255,255,255,.7)';c.lineWidth=.6;c.stroke()}
  else if(k<.8){const gg=c.createRadialGradient(ix-1.5,sy-6.5,.4,ix,sy-5,4.5);gg.addColorStop(0,xmMix(cl,'#ffffff',.55));gg.addColorStop(1,cl);c.fillStyle=gg;c.beginPath();c.arc(ix,sy-5,4.3,0,7);c.fill()}
  else{c.fillStyle='#2e6b4a';c.beginPath();c.moveTo(ix,sy-13);c.lineTo(ix+5,sy);c.lineTo(ix-5,sy);c.closePath();c.fill();c.fillStyle='#e2b84a';c.beginPath();c.arc(ix,sy-13,1.4,0,7);c.fill()}}
 // 人の影（店の人）
 c.fillStyle=night?'rgba(60,25,10,.55)':'rgba(90,50,25,.35)';c.beginPath();c.ellipse(ox+ow*.72,oy+oh*.42,ow*.06,oh*.2,0,0,7);c.fill();c.beginPath();c.arc(ox+ow*.72,oy+oh*.14,ow*.04,0,7);c.fill();
 if(L){L.push({x:ox+ow/2,y:oy+oh*.45,r:w*.85,c:'255,176,90',a:night?.55:dusk?.25:.08,p:r()*5,sp:.4,soft:1});
  L.push({x:x+w/2,y:y+w*.06,rx:w*.95,ry:w*.16,c:'255,170,90',a:night?.35:dusk?.14:0,p:0,sp:0,soft:1,ell:1})}   // 足もとに落ちる光
 // カウンター（赤い布と白い縁）
 wash(c,g=>wob(g,[[x+w*.04,y-h*.36],[x+w*.96,y-h*.36],[x+w*.96,y-h*.27],[x+w*.04,y-h*.27]],.8,seed+2),night?'#6a1d18':'#b3332a',{edge:.3,light:false});
 c.fillStyle='rgba(255,245,230,.75)';for(let i=0;i<10;i++){const xx=x+w*(.04+i*.092);c.beginPath();c.arc(xx+w*.046,y-h*.27,w*.046,0,Math.PI);c.fill()}
 // 屋根：濃い木の三角＋厚い雪
 const ry=y-h,ph=w*.36;
 wash(c,g=>wob(g,[[x-w*.12,ry+4],[x+w/2,ry-ph],[x+w*1.12,ry+4]],1.2,seed+3),night?'#24160e':'#4e3222',{edge:.4});
 wash(c,g=>{g.moveTo(x-w*.14,ry+2);g.lineTo(x+w/2,ry-ph-5);g.lineTo(x+w*1.14,ry+2);
  for(let i=8;i>=0;i--){const u=i/8,xx=x-w*.14+u*w*1.28,dy=(1-Math.abs(u-.5)*2)*-ph;g.quadraticCurveTo(xx+w*.05,ry+dy+11+(i%3)*3,xx,ry+dy+3)}g.closePath()},night?'#cfd6ea':'#fbfbf8',
  {grad:g=>{const q=g.createLinearGradient(0,ry-ph,0,ry+12);q.addColorStop(0,night?'#e8ecf8':'#ffffff');q.addColorStop(1,night?'#9aa6c8':'#d9dee8');return q},edge:.22,light:false,gr:.12,ec:'#8e9ab8'});
 // もみの木のガーランドと電球
 const gx0=x-w*.02,gx1=x+w*1.02,gy=ry+6,sag=w*.1;c.save();
 for(let i=0;i<150;i++){const u=r(),xx=gx0+(gx1-gx0)*u,yy=gy+Math.sin(u*Math.PI)*sag+(r()-.5)*5;c.strokeStyle=['#1d4a32','#2c6044','#3d7a52'][i%3];c.lineWidth=1.3;const a=r()*6.3,l=3+r()*4;c.beginPath();c.moveTo(xx,yy);c.lineTo(xx+Math.cos(a)*l,yy+Math.sin(a)*l);c.stroke()}c.restore();
 if(L)for(let i=1;i<10;i++){const u=i/10,xx=gx0+(gx1-gx0)*u,yy=gy+Math.sin(u*Math.PI)*sag+3;L.push({x:xx,y:yy,r:night?20:12,c:i%3?'255,206,128':'255,150,110',a:night?.85:.45,p:r()*6,sp:2.2,dot:1.9})}
 // 角のランタン
 const lx=x+w*1.02,ly=ry+h*.2;c.strokeStyle='rgba(30,20,15,.8)';c.lineWidth=1;c.beginPath();c.moveTo(lx,ry+2);c.lineTo(lx,ly-6);c.stroke();
 c.fillStyle=night?'#ffdca0':'#f3d9a2';c.fillRect(lx-3.5,ly-6,7,10);c.strokeStyle='#2a1c14';c.lineWidth=1.2;c.strokeRect(lx-3.5,ly-6,7,10);c.fillStyle='#2a1c14';c.beginPath();c.moveTo(lx-5,ly-6);c.lineTo(lx,ly-10);c.lineTo(lx+5,ly-6);c.fill();
 if(L)L.push({x:lx,y:ly-1,r:night?34:16,c:'255,196,110',a:night?.8:.3,p:r()*4,sp:3.1,dot:2.2})}

// ---------- 人（丸い頭・コート・マフラー・帽子。夜はツリー側のふちが光る） ----------
function xmPerson(c,x,y,s,col,mode,seed,kind){const r=XR(seed);kind=kind==null?Math.floor(r()*3):kind;const night=mode==2,dusk=mode==1;
 const dk=night?.55:dusk?.25:0,coat=xmMix(col,'#120a14',dk),coat2=xmMix(coat,'#000000',.3),skin=xmMix('#ecc9a8','#2a1a20',dk*1.1),hair=xmMix(['#3a2418','#5a3a22','#1e1410'][Math.floor(r()*3)],'#000',dk*.5);
 const acc=xmMix(['#c0392b','#e2b84a','#f1e7d6','#2e6b4a'][Math.floor(r()*4)],'#100810',dk);
 const ch=kind==2;const S=ch?s*.72:s;
 c.save();c.globalAlpha=night?.45:.28;c.fillStyle='#1a0e0a';c.filter='blur(2px)';c.beginPath();c.ellipse(x+S*.08,y,S*.26,S*.045,0,0,7);c.fill();c.filter='none';c.restore();
 // 足とブーツ
 c.strokeStyle=xmMix('#2b2228','#000',dk*.5);c.lineCap='round';c.lineWidth=S*.055;c.beginPath();c.moveTo(x-S*.045,y-S*.3);c.lineTo(x-S*.05,y-S*.03);c.moveTo(x+S*.045,y-S*.3);c.lineTo(x+S*.055,y-S*.03);c.stroke();
 c.fillStyle=xmMix('#3a2418','#000',dk*.4);c.beginPath();c.ellipse(x-S*.06,y-S*.02,S*.05,S*.025,0,0,7);c.ellipse(x+S*.065,y-S*.02,S*.05,S*.025,0,0,7);c.fill();
 // コート（肩は丸く、すそが広がる）
 const sh=y-S*.73,hm=y-S*(kind==0?.24:.3);
 wash(c,g=>{g.moveTo(x-S*.1,sh);g.quadraticCurveTo(x-S*.15,sh+S*.02,x-S*.155,sh+S*.1);g.lineTo(x-S*(kind==0?.2:.17),hm);g.quadraticCurveTo(x,hm+S*.03,x+S*(kind==0?.2:.17),hm);g.lineTo(x+S*.155,sh+S*.1);g.quadraticCurveTo(x+S*.15,sh+S*.02,x+S*.1,sh);g.closePath()},coat,
  {grad:g=>{const q=g.createLinearGradient(x-S*.2,0,x+S*.2,0);q.addColorStop(0,xmMix(coat,'#ffffff',.12));q.addColorStop(1,coat2);return q},edge:.45,gr:.25});
 c.strokeStyle='rgba(0,0,0,.18)';c.lineWidth=1;c.beginPath();c.moveTo(x,sh+S*.06);c.lineTo(x,hm);c.stroke();
 // 腕
 c.strokeStyle=coat2;c.lineWidth=S*.06;c.beginPath();c.moveTo(x-S*.14,sh+S*.06);c.quadraticCurveTo(x-S*.19,sh+S*.2,x-S*.15,sh+S*.32);c.moveTo(x+S*.14,sh+S*.06);c.quadraticCurveTo(x+S*.19,sh+S*.2,x+S*.15,sh+S*.32);c.stroke();
 // マフラー
 c.fillStyle=acc;c.beginPath();c.ellipse(x,sh+S*.005,S*.1,S*.04,0,0,7);c.fill();c.fillRect(x+S*.03,sh,S*.045,S*.17);
 // 頭・髪・帽子
 const hy=y-S*.83,hr=S*.085;c.fillStyle=skin;c.beginPath();c.arc(x,hy,hr,0,7);c.fill();
 c.fillStyle=hair;c.beginPath();c.arc(x,hy-hr*.15,hr*1.04,Math.PI*.95,Math.PI*2.05);c.fill();
 if(kind==0){c.beginPath();c.moveTo(x-hr,hy-hr*.2);c.quadraticCurveTo(x-hr*1.25,hy+hr*1.3,x-hr*.55,hy+hr*1.6);c.lineTo(x-hr*.6,hy);c.fill();c.beginPath();c.moveTo(x+hr,hy-hr*.2);c.quadraticCurveTo(x+hr*1.25,hy+hr*1.3,x+hr*.55,hy+hr*1.6);c.lineTo(x+hr*.6,hy);c.fill()}
 else{const bc=xmMix(['#b8322a','#2e4a5e','#e2b84a','#3d6b52'][Math.floor(r()*4)],'#100810',dk);c.fillStyle=bc;c.beginPath();c.arc(x,hy-hr*.25,hr*1.08,Math.PI,0);c.fill();c.fillStyle=xmMix(bc,'#000',.2);c.fillRect(x-hr*1.1,hy-hr*.35,hr*2.2,hr*.42);c.fillStyle=xmMix(bc,'#ffffff',.4);c.beginPath();c.arc(x,hy-hr*1.4,hr*.36,0,7);c.fill()}
 // 夜：ツリー側のふちが光る
 if(night||dusk){c.save();c.globalCompositeOperation='lighter';c.strokeStyle=`rgba(255,180,100,${night?.55:.25})`;c.lineWidth=1.4;c.beginPath();c.arc(x,hy,hr,-Math.PI*.6,Math.PI*.3);c.stroke();c.beginPath();c.moveTo(x+S*.15,sh+S*.06);c.lineTo(x+S*(kind==0?.2:.17),hm);c.stroke();c.restore()}}

// ---------- 電球のひも・旗 ----------
function xmString(c,x0,y0,x1,y1,sag,n,mode,L,seed){c.strokeStyle=mode==2?'rgba(20,14,16,.7)':'rgba(60,40,30,.5)';c.lineWidth=1.3;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2,(y0+y1)/2+sag,x1,y1);c.stroke();
 const r=XR(seed||5);if(L)for(let i=1;i<n;i++){const u=i/n,xx=(1-u)*(1-u)*x0+2*u*(1-u)*(x0+x1)/2+u*u*x1,yy=(1-u)*(1-u)*y0+2*u*(1-u)*((y0+y1)/2+sag)+u*u*y1+4;
  c.fillStyle=mode==2?'#3a2a1a':'#6a5040';c.fillRect(xx-1.2,yy-5,2.4,3);L.push({x:xx,y:yy,r:mode==2?24:12,c:i%4==0?'255,140,110':'255,206,125',a:mode==2?.8:.4,p:r()*6,sp:2,dot:2.1})}}
function xmFlags(c,x0,y0,x1,y1,sag,n){c.strokeStyle='rgba(80,50,40,.55)';c.lineWidth=1.1;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2,(y0+y1)/2+sag,x1,y1);c.stroke();
 const cols=['#b8322a','#2c5a3e','#d9a93f','#efe4cf'];for(let i=1;i<n;i++){const u=i/n,xx=(1-u)*(1-u)*x0+2*u*(1-u)*(x0+x1)/2+u*u*x1,yy=(1-u)*(1-u)*y0+2*u*(1-u)*((y0+y1)/2+sag)+u*u*y1;
  wash(c,g=>{g.moveTo(xx-8,yy);g.lineTo(xx+8,yy);g.lineTo(xx,yy+20);g.closePath()},cols[i%4],{edge:.3,light:false,ew:1.5})}}
// ---------- 石だたみ（奥ほど小さく）と雪 ----------
function xmGround(c,y0,mode){const P=[['#e4d8c4','#b9a487'],['#c49c8a','#7d5c55'],['#2c2738','#121019']][mode];
 wash(c,g=>wob(g,[[-20,y0],[XW+20,y0],[XW+20,XH+20],[-20,XH+20]],2,17),P[0],{grad:g=>{const q=g.createLinearGradient(0,y0,0,XH);q.addColorStop(0,P[0]);q.addColorStop(1,P[1]);return q},edge:.1,gr:.3,light:false});
 const r=XR(77);c.save();let yy=y0+4,k=0;while(yy<XH){const rh=5+((yy-y0)/(XH-y0))*26,sw=rh*1.7;let xx=-(k%2)*sw*.5;
  while(xx<XW){const w=sw*(.8+r()*.4);c.fillStyle=mode==2?`rgba(${120+r()*40},${120+r()*40},${150+r()*40},${.06+r()*.05})`:`rgba(255,250,240,${.1+r()*.14})`;c.beginPath();c.ellipse(xx+w/2,yy+rh/2,w/2-1.2,rh/2-1,0,0,7);c.fill();
   c.strokeStyle=mode==2?'rgba(0,0,0,.25)':'rgba(90,60,40,.12)';c.lineWidth=.8;c.stroke();xx+=w}yy+=rh;k++}
 // 雪のたまり（ふち）
 c.filter='blur(6px)';for(let i=0;i<14;i++){const x=r()<.5?r()*200:XW-r()*200,y=y0+40+r()*(XH-y0);c.fillStyle=mode==2?'rgba(170,185,225,.16)':'rgba(255,255,255,.4)';c.beginPath();c.ellipse(x,y,60+r()*90,10+r()*14,0,0,7);c.fill()}
 c.restore()}
// ---------- 月（にじむ光の輪・やわらかい模様・照らされた雲） ----------
function xmMoon(c,x,y,R){c.save();c.globalCompositeOperation='screen';glow(c,x,y,R*7,'200,210,255',.18);glow(c,x,y,R*2.6,'255,240,205',.3);c.restore();
 const g=c.createRadialGradient(x-R*.35,y-R*.35,R*.1,x,y,R);g.addColorStop(0,'#fffaf0');g.addColorStop(.7,'#f6ecd0');g.addColorStop(1,'#e8d9b0');c.fillStyle=g;c.beginPath();c.arc(x,y,R,0,7);c.fill();
 c.save();c.beginPath();c.arc(x,y,R,0,7);c.clip();c.filter='blur(2.5px)';c.fillStyle='rgba(170,150,120,.22)';for(const[a,b,s]of[[-.3,.15,.26],[.28,-.3,.15],[.22,.38,.12],[-.1,-.42,.09],[.45,.05,.1]]){c.beginPath();c.arc(x+R*a,y+R*b,R*s,0,7);c.fill()}c.restore();
 c.save();c.filter='blur(5px)';c.globalAlpha=.55;for(const[dx,dy,w]of[[-R*1.6,R*.7,R*2.4],[R*1.2,R*1.1,R*1.8]]){const q=c.createLinearGradient(x+dx-w,0,x+dx+w,0);q.addColorStop(0,'rgba(60,70,120,0)');q.addColorStop(.5,'rgba(150,160,210,.5)');q.addColorStop(1,'rgba(60,70,120,0)');c.fillStyle=q;c.beginPath();c.ellipse(x+dx,y+dy,w,R*.13,0,0,7);c.fill()}c.restore()}

// ---------- 1ページ分の下絵：層に分ける（奥・ツリー・手前）。ツリーと手前はページから立ち上がる ----------
const XBASE={};
function xmLayer(){const cv=xmCanvas(XW,XH);return{cv,c:cv.getContext('2d'),L:[]}}
function xmShadowOf(cv){const s=xmCanvas(XW,XH),g=s.getContext('2d');g.filter='brightness(0) blur(7px)';g.drawImage(cv,0,0);return s}
function xmBase(mode){if(XBASE[mode])return XBASE[mode];if(typeof P!='undefined'&&P.scene=='momiji')return XBASE[mode]=mjBuild(mode);if(typeof P!='undefined'&&P.scene=='hama')return XBASE[mode]=hmBuild(mode);const B=xmLayer(),T=xmLayer(),F=xmLayer();let c=B.c,L=B.L;
 xmSky(c,mode);
 if(mode==0){
  c.save();c.globalCompositeOperation='screen';glow(c,250,560,460,'255,220,170',.5);c.restore();
  xmGulls(c,6,7);xmWheel(c,150,650,118,0,null);xmSea(c,792,862,0);
  xmWarehouse(c,-30,1015,560,195,0,11,L);xmWarehouse(c,560,985,400,150,0,12,L);
  xmGround(c,1010,0);
  xmFlags(c,-10,905,930,885,58,22);xmString(c,-10,980,930,955,64,24,0,L,8);
  xmHut(c,150,1085,100,0,26,L);xmHut(c,290,1095,92,0,27,L);
  xmTree(T.c,630,1190,540,0,5,T.L);T.ax=630;T.ay=1190;T.d=.1;
  xmPerson(F.c,410,1180,92,'#3e4f6e',0,31,0);xmPerson(F.c,438,1184,84,'#a8543a',0,32,1);xmPerson(F.c,860,1170,80,'#7b6a4e',0,33,0);
  xmHut(F.c,25,1240,170,0,21,F.L);xmHut(F.c,235,1285,150,0,22,F.L);xmHut(F.c,775,1300,150,0,23,F.L);
  xmPerson(F.c,560,1320,120,'#6b3a3a',0,34,0);xmPerson(F.c,600,1326,104,'#2e4a5e',0,35,1);xmPerson(F.c,636,1330,76,'#c0392b',0,46,2);F.ax=460;F.ay=1330;F.d=.4;
 }else if(mode==1){
  c.save();c.globalCompositeOperation='screen';glow(c,700,640,560,'255,190,150',.35);c.restore();
  xmWheel(c,790,700,105,1,L);xmSea(c,828,882,1);
  xmWarehouse(c,430,1005,540,215,1,13,L);
  xmGround(c,1000,1);
  xmString(c,560,1040,930,990,40,12,1,L,9);
  xmTree(T.c,320,1300,1060,1,7,T.L);T.ax=320;T.ay=1300;T.d=.1;
  xmHut(F.c,610,1290,170,1,24,F.L);
  xmPerson(F.c,820,1300,110,'#3e3a5e',1,36,0);xmPerson(F.c,852,1306,96,'#a8543a',1,37,1);F.ax=730;F.ay=1310;F.d=.4;
  for(const q of[B,T,F]){q.c.save();q.c.globalCompositeOperation='source-atop';q.c.fillStyle='rgba(110,70,120,.14)';q.c.fillRect(0,0,XW,XH);q.c.restore()}
 }else{
  xmStars(c,8);xmMoon(c,210,250,58);
  xmWheel(c,120,700,118,2,L);xmSea(c,792,882,2);
  c.save();c.globalCompositeOperation='lighter';const r=XR(31);for(let i=0;i<70;i++){const x=r()*XW,y=800+r()*78;c.fillStyle=`rgba(255,200,120,${.1+r()*.25})`;c.fillRect(x,y,6+r()*26,1.6)}c.restore();
  xmWarehouse(c,-30,1025,560,205,2,11,L);xmWarehouse(c,520,995,450,165,2,12,L);
  xmGround(c,1020,2);
  xmString(c,-10,940,930,912,78,26,2,L,10);xmString(c,-10,1062,930,1040,48,22,2,L,11);
  L.push({x:320,y:1250,rx:430,ry:90,c:'255,170,90',a:.45,p:0,sp:0,soft:1,ell:1});   // ツリーの足もとの光
  xmTree(T.c,320,1235,800,2,5,T.L);T.ax=320;T.ay=1235;T.d=.1;
  xmHut(F.c,600,1245,150,2,21,F.L);xmHut(F.c,770,1275,130,2,22,F.L);
  xmPerson(F.c,560,1320,110,'#4a3a5a',2,38,0);xmPerson(F.c,592,1324,98,'#5a2a30',2,39,1);F.ax=690;F.ay=1320;F.d=.4;
 }
 T.sh=xmShadowOf(T.cv);F.sh=xmShadowOf(F.cv);
 // 紙のふちの暗さと紙の目（毎コマ最後に重ねる）
 const V=xmCanvas(XW,XH),v=V.getContext('2d');const vg=v.createRadialGradient(460,660,320,460,700,1020);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,mode==2?'rgba(0,0,0,.45)':'rgba(80,50,30,.2)');v.fillStyle=vg;v.fillRect(0,0,XW,XH);
 XBASE[mode]={B,T,F,V,gy:[1010,1000,1020][mode]};return XBASE[mode]}

// ---------- 毎コマ：立ち上がり・光のにじみ・地面に映る光 ----------
const XOUT=xmCanvas(XW,XH),XO=XOUT.getContext('2d');
const XLC=xmCanvas(XW/2,XH/2),XLG=XLC.getContext('2d'),XB1=xmCanvas(XW/4,XH/4),XB1G=XB1.getContext('2d'),XB2=xmCanvas(XW/8,XH/8),XB2G=XB2.getContext('2d');
function xmEll(c,l,a){c.save();c.translate(l.x,l.y);c.scale(1,l.ry/l.rx);glow(c,0,0,l.rx,l.c,a);c.restore()}
function xmPopK(u,d){const x=Math.max(0,Math.min(1,(u-d)/1.05));if(x<=0)return 0;const c1=1.5;return 1+(c1+1)*Math.pow(x-1,3)+c1*Math.pow(x-1,2)}
function xmPage(mode,t,u){const X=xmBase(mode);t=t||0;u=u||0;const c=XO;const k=Math.max(0,Math.min(1,(u+.9)/5.2)),uu=u+.55;
 c.setTransform(1,0,0,1,0,0);c.globalCompositeOperation='source-over';c.globalAlpha=1;c.filter='none';
 XLG.setTransform(1,0,0,1,0,0);XLG.clearRect(0,0,XW/2,XH/2);XLG.globalCompositeOperation='lighter';
 const layers=[[X.B,6,null],[X.T,22,X.T],[X.F,38,X.F]];
 const lightsOf=(Ly,ox,kk,ax,ay)=>{for(const l of Ly.L){const tw=l.soft?.88+.12*Math.sin(t*l.sp+l.p):.6+.4*Math.sin(t*l.sp+l.p);let x=l.x+ox,y=l.y;if(kk!=null){y=ay+(y-ay)*kk;x=ax+(x-ax)*(.92+.08*kk)}const a=l.a*tw*(kk==null?1:Math.min(1,kk));if(kk!=null&&kk<.03)continue;const ka=kk==null?1:Math.min(1,kk);
   if(l.ell){XLG.save();XLG.scale(.5,.5);xmEll(XLG,{...l,x,y},a);XLG.restore();continue}
   glow(XLG,x/2,y/2,l.r/2,l.c,a);
   c.globalCompositeOperation='lighter';glow(c,x,y,l.r*.32,l.c,Math.min(1,a*1.1));if(l.dot){c.fillStyle=`rgba(255,250,232,${Math.min(1,.6+.4*tw)*ka})`;c.beginPath();c.arc(x,y,l.dot,0,7);c.fill()}c.globalCompositeOperation='source-over'}};
 for(const[Ly,par,pop]of layers){const ox=(k-.5)*-par;
  if(!pop){c.drawImage(Ly.cv,ox,0);continue}
  const kk=Math.max(0,xmPopK(uu,Ly.d));if(kk<=0.001)continue;const ax=Ly.ax+ox,ay=Ly.ay;
  // 紙の影：ページの上に、右奥へ伸びる
  c.save();c.globalAlpha=Math.min(1,kk)*(mode==2?.4:.24);c.translate(ax,ay);c.transform(1,0,-.22,.1*Math.min(1,kk),0,0);c.translate(-ax,-ay);c.drawImage(Ly.sh,ox,0);c.restore();
  c.save();c.translate(ax,ay);c.scale(.92+.08*kk,kk);c.translate(-ax,-ay);c.drawImage(Ly.cv,ox,0);
  c.restore()}
 // 光：奥から順に（立ち上がりと同じ動き）
 lightsOf(X.B,(k-.5)*-6,null);lightsOf(X.T,(k-.5)*-22,Math.max(0,xmPopK(uu,X.T.d)),X.T.ax+(k-.5)*-22,X.T.ay);lightsOf(X.F,(k-.5)*-38,Math.max(0,xmPopK(uu,X.F.d)),X.F.ax+(k-.5)*-38,X.F.ay);
 // にじみ（ブルーム）：小さく縮めてぼかし、2段で重ねる
 XB1G.clearRect(0,0,XW/4,XH/4);XB1G.filter='blur(5px)';XB1G.drawImage(XLC,0,0,XW/4,XH/4);XB1G.filter='none';
 XB2G.clearRect(0,0,XW/8,XH/8);XB2G.filter='blur(6px)';XB2G.drawImage(XLC,0,0,XW/8,XH/8);XB2G.filter='none';
 c.globalCompositeOperation='lighter';c.globalAlpha=mode==2?.95:mode==1?.7:.45;c.drawImage(XLC,0,0,XW,XH);c.globalAlpha=mode==2?.9:.55;c.drawImage(XB1,0,0,XW,XH);c.globalAlpha=mode==2?.8:.4;c.drawImage(XB2,0,0,XW,XH);
 // 夜：ぬれた石だたみに光が映る
 if(mode==2){const gy=X.gy;c.save();c.beginPath();c.rect(0,gy,XW,XH-gy);c.clip();c.globalAlpha=.42;c.filter='blur(4px)';c.translate(0,gy*2+40);c.scale(1,-1);c.drawImage(XB1,0,0,XW,XH);c.restore()}
 c.globalCompositeOperation='source-over';c.globalAlpha=1;c.filter='none';
 if(typeof MG!='undefined'&&MG){if(P.scene=='momiji')mjFx(c,mode,t,u);else if(P.scene=='hama')hmFx(c,mode,t,u);else xmFx(c,mode,t,u)}
 c.drawImage(X.V,0,0);c.save();c.globalCompositeOperation='multiply';c.globalAlpha=.08;c.drawImage(xmNoise(),0,0);c.restore();
 return XOUT.toDataURL('image/jpeg',.92)}
