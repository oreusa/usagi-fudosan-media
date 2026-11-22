// 11/21 鶏足寺だけの描き下ろし：切り紙の飛び出す絵本の筆（紙の縁・紙の目・水彩のむら）
const W=925,H=1425;
function rng(s){s=s%2147483647||7;return()=>(s=(s*16807)%2147483647)/2147483647}
function cv(w=W,h=H){const c=document.createElement('canvas');c.width=w;c.height=h;return c}
function hex(h){h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function mix(a,b,k){const A=hex(a),B=hex(b);return'#'+A.map((v,i)=>Math.round(v+(B[i]-v)*k).toString(16).padStart(2,'0')).join('')}
function rgba(h,a){const c=hex(h);return`rgba(${c[0]},${c[1]},${c[2]},${a})`}
// 紙の目：小さなざらつき＋大きな水彩のむら（色のある所だけ）
function grain(c,amt=16,seed=3,blot=.06){const x=c.getContext('2d');const r=rng(seed);
 if(blot){x.save();x.globalCompositeOperation='source-atop';for(let i=0;i<60;i++){const px=r()*c.width,py=r()*c.height,rr=40+r()*160;const g=x.createRadialGradient(px,py,0,px,py,rr);const dk=r()<.5;g.addColorStop(0,dk?`rgba(40,20,10,${blot})`:`rgba(255,248,230,${blot})`);g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.fillRect(px-rr,py-rr,rr*2,rr*2)}x.restore()}
 const d=x.getImageData(0,0,c.width,c.height),p=d.data;let fib=0;
 for(let i=0;i<p.length;i+=4){if(!p[i+3])continue;if((i>>2)%c.width==0)fib=(r()-.5)*4;const n=(r()-.5)*amt+fib;p[i]+=n;p[i+1]+=n;p[i+2]+=n}
 x.putImageData(d,0,0)}
// 切り紙の縁：形の外側に生成りの紙の芯が少し見える
function rim(c,col='#f3e8d2',px=1.6){const o=cv(c.width,c.height),x=o.getContext('2d');
 const s=cv(c.width,c.height),sx=s.getContext('2d');sx.drawImage(c,0,0);sx.globalCompositeOperation='source-in';sx.fillStyle=col;sx.fillRect(0,0,c.width,c.height);
 for(let a=0;a<12;a++){const t=a/12*Math.PI*2;x.drawImage(s,Math.cos(t)*px,Math.sin(t)*px+(Math.sin(t)>0?.6:0))}
 x.drawImage(c,0,0);return o}
function finish(c,seed,opt={}){grain(c,opt.g??15,seed,opt.blot??.07);return opt.rim===false?c:rim(c,opt.rimc,opt.rimw)}
// もみじの葉（5〜7裂）
function leafPath(x,s,lobes=7){x.beginPath();for(let i=0;i<lobes*2;i++){const a=-Math.PI/2+i*Math.PI/lobes;const isTip=i%2==0;const k=Math.abs(Math.sin(i*Math.PI/lobes/2+.2));
 const r=isTip?s*(i==0?1:i==2||i==lobes*2-2?.92:i==4||i==lobes*2-4?.78:.5):s*.34;x.lineTo(Math.cos(a)*r,Math.sin(a)*r)}x.closePath()}
function leaf(x,px,py,s,rot,col,lobes=7){x.save();x.translate(px,py);x.rotate(rot);x.fillStyle=col;leafPath(x,s,lobes);x.fill();x.restore()}
const AKA=['#b8261c','#cf3a1e','#a51e1a','#e0542a','#d8441f','#8f1a17','#e8702e','#f08a2c','#c42f22'];
const KI=['#e8a42c','#f0b83a','#d98a24','#e8702e'];
const AO=['#7a8a3a','#9aa84a','#6a7a32','#b8ac48'];
// 木の葉の茂み：輪郭は葉のぎざぎざ、上と光の側は明るく
function canopy(x,cx,cy,rx,ry,pal,seed,n=900,light=[.7,.15],leafS=[7,14],shape){const r=rng(seed);
 const inside=(u,v)=>shape?shape(u,v):(u*u+v*v<1);
 // 下塗り：中を埋める濃い面（輪郭の内側だけ）
 x.save();for(let i=0;i<220;i++){let u,v;do{u=r()*2-1;v=r()*2-1}while(!inside(u*1.08,v*1.08));const c=mix(pal[i%pal.length],'#3a0e0a',.35+(v+1)*.12);x.fillStyle=c;x.beginPath();x.ellipse(cx+u*rx,cy+v*ry,rx*.16,ry*.16,0,0,7);x.fill()}x.restore();
 // 下地の影
 x.save();for(let i=0;i<n*.35;i++){let u,v;do{u=r()*2-1;v=r()*2-1}while(!inside(u,v));x.globalAlpha=1;leaf(x,cx+u*rx,cy+v*ry+ry*.06,leafS[1]*1.3,r()*6,mix(pal[Math.floor(r()*pal.length)],'#3a0e0a',.5))}
 for(let i=0;i<n;i++){let u,v;do{u=r()*2-1;v=r()*2-1}while(!inside(u,v));
  const lit=Math.max(0,Math.min(1,.5+(u*(light[0]-.5)*1.6)-(v*.6)));let c=pal[Math.floor(r()*pal.length)];c=lit>.6?mix(c,'#ffd9a0',(lit-.6)*.7):mix(c,'#4a120c',(.6-lit)*.55);
  leaf(x,cx+u*rx,cy+v*ry,leafS[0]+r()*(leafS[1]-leafS[0]),r()*6,c)}x.restore()}
// 古木の幹（曲がり・こぶ・樹皮の筋）
function trunk(x,pts,w0,w1,col,seed){const r=rng(seed);const L=[],R=[];
 for(let i=0;i<pts.length;i++){const k=i/(pts.length-1),w=w0+(w1-w0)*k;const p=pts[i],q=pts[Math.min(i+1,pts.length-1)],o=pts[Math.max(i-1,0)];const dx=q[0]-o[0],dy=q[1]-o[1],l=Math.hypot(dx,dy)||1;const nx=-dy/l,ny=dx/l;const j=1+(r()-.5)*.18;
  L.push([p[0]+nx*w/2*j,p[1]+ny*w/2*j]);R.push([p[0]-nx*w/2*j,p[1]-ny*w/2*j])}
 x.beginPath();x.moveTo(...L[0]);for(let i=1;i<L.length;i++){const m=[(L[i-1][0]+L[i][0])/2,(L[i-1][1]+L[i][1])/2];x.quadraticCurveTo(L[i-1][0],L[i-1][1],m[0],m[1])}x.lineTo(...L[L.length-1]);x.lineTo(...R[R.length-1]);
 for(let i=R.length-2;i>=0;i--){const m=[(R[i+1][0]+R[i][0])/2,(R[i+1][1]+R[i][1])/2];x.quadraticCurveTo(R[i+1][0],R[i+1][1],m[0],m[1])}x.closePath();
 const g=x.createLinearGradient(pts[0][0]-w0,0,pts[0][0]+w0,0);g.addColorStop(0,mix(col,'#000000',.35));g.addColorStop(.6,col);g.addColorStop(1,mix(col,'#c8a080',.25));x.fillStyle=g;x.fill();
 x.save();x.clip();x.strokeStyle=rgba('#1a0e08',.35);x.lineWidth=1.4;for(let i=0;i<w0*.5;i++){const t=r();x.beginPath();let px=pts[0][0]+(t-.5)*w0;let py=pts[0][1];x.moveTo(px,py);for(let k=1;k<pts.length;k++){x.lineTo(pts[k][0]+(t-.5)*(w0+(w1-w0)*k/(pts.length-1))+(r()-.5)*3,pts[k][1])}x.stroke()}
 // 苔
 for(let i=0;i<70;i++){const k=r()*.5,idx=Math.floor(k*(pts.length-1));const p=pts[idx];x.fillStyle=rgba(AO[i%4],.55);x.beginPath();x.ellipse(p[0]-w0*.3+(r()-.5)*w0*.4,p[1]+(r()-.5)*20,6+r()*10,3+r()*5,0,0,7);x.fill()}x.restore()}
// 石垣：不ぞろいの石を積む（苔つき）
function ishigaki(x,poly,seed,stoneW=34,stoneH=22,base='#8a8476',moss=.5){const r=rng(seed);x.save();x.beginPath();poly.forEach((p,i)=>i?x.lineTo(...p):x.moveTo(...p));x.closePath();x.fillStyle='#3a342a';x.fill();x.clip();
 const ys=poly.map(p=>p[1]),xs=poly.map(p=>p[0]);const y0=Math.min(...ys),y1=Math.max(...ys),x0=Math.min(...xs),x1=Math.max(...xs);
 for(let y=y0;y<y1;y+=stoneH*(.8+r()*.3)){const sc=.55+.45*((y-y0)/(y1-y0+1));let xx=x0-r()*stoneW;while(xx<x1){const w=stoneW*sc*(.7+r()*.7),h=stoneH*sc*(.8+r()*.5);
  const c=mix(base,r()<.5?'#a8a090':'#6a6458',r()*.6);x.fillStyle=c;x.beginPath();const j=()=>(r()-.5)*w*.18;x.moveTo(xx+j(),y+j());x.lineTo(xx+w+j(),y+j());x.lineTo(xx+w+j(),y+h+j());x.lineTo(xx+j(),y+h+j());x.closePath();x.fill();
  x.fillStyle=rgba('#ffffff',.12);x.fillRect(xx+2,y+1,w*.7,2);
  if(r()<moss){x.fillStyle=rgba(AO[Math.floor(r()*4)],.85);x.beginPath();x.ellipse(xx+w*.5,y+2,w*.5,h*.28,0,0,7);x.fill()}
  xx+=w+2}}x.restore()}
function sky(x,top,bot,y0=0,y1=H){const g=x.createLinearGradient(0,y0,0,y1);g.addColorStop(0,top);g.addColorStop(1,bot);x.fillStyle=g;x.fillRect(0,y0,W,y1-y0)}
function rays(x,ox,oy,n,seed,col='#fff2cc',a=.18){const r=rng(seed);x.save();x.globalCompositeOperation='lighter';for(let i=0;i<n;i++){const ang=Math.PI*.55+r()*.5,len=1600,w=.02+r()*.04;const g=x.createLinearGradient(ox,oy,ox+Math.cos(ang)*len,oy+Math.sin(ang)*len);g.addColorStop(0,rgba(col,a));g.addColorStop(1,rgba(col,0));x.fillStyle=g;x.beginPath();x.moveTo(ox,oy);x.lineTo(ox+Math.cos(ang-w)*len,oy+Math.sin(ang-w)*len);x.lineTo(ox+Math.cos(ang+w)*len,oy+Math.sin(ang+w)*len);x.closePath();x.fill()}x.restore()}
