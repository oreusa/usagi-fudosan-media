// 水彩で描く道具（11/19 絵本の中の絵を上げる）。
// にじみ：形を何度もゆがめた半透明の面を数十枚重ねる（Tyler Hobbs の水彩の描き方）。紙のざらつきで色が溜まる。
// 線：細いセピアの線を、手で描いたように少し揺らして重ねる。
(function(G){
const R_=a=>()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
function gauss(r){let u=0;for(let i=0;i<6;i++)u+=r();return u/6*2-1}
// 多角形をゆがめる：辺の中点を、辺の長さに比例してずらす
function deform(pts,depth,amt,r){let p=pts;for(let d=0;d<depth;d++){const q=[];for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length];const v=a[2]??1;q.push(a);const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2,L=Math.hypot(b[0]-a[0],b[1]-a[1]);const nv=Math.max(.2,v*(1+gauss(r)*.3));q.push([mx+gauss(r)*L*amt*nv,my+gauss(r)*L*amt*nv,nv])}p=q}return p}
function fillPoly(c,p){c.beginPath();c.moveTo(p[0][0],p[0][1]);for(let i=1;i<p.length;i++)c.lineTo(p[i][0],p[i][1]);c.closePath();c.fill()}
// 紙の目（溜まり）
let GR=null;function granule(W,H){if(GR&&GR.width==W&&GR.height==H)return GR;const c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');const d=g.createImageData(W,H);const r=R_(9);
 for(let i=0;i<d.data.length;i+=4){const v=r();d.data[i+3]=v<.55?0:Math.floor((v-.55)*560)}g.putImageData(d,0,0);g.filter='blur(1.1px)';g.drawImage(c,0,0);GR=c;return c}
// にじみの面：pts＝形、col＝色、n＝重ねる枚数、a＝1枚の濃さ
function wash(c,pts,col,o){o=o||{};const r=R_(o.seed||1);const base=deform(pts.map(p=>[p[0],p[1],1]),o.d0??3,o.amt??.4,r);const n=o.n??36;
 const L=document.createElement('canvas');L.width=c.canvas.width;L.height=c.canvas.height;const g=L.getContext('2d');g.fillStyle=col;
 for(let i=0;i<n;i++){g.globalAlpha=o.a??.045;fillPoly(g,deform(base,o.d1??3,o.amt2??.32,r))}
 // ふちに色が溜まる（にじみの縁）：少しだけ濃い線
 if(o.edge!==0){g.globalAlpha=(o.edge??.12);g.strokeStyle=col;g.lineWidth=o.ew??1.6;g.beginPath();base.forEach((p,i)=>i?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]));g.closePath();g.stroke()}
 if(o.gran!==0){g.globalAlpha=o.gran??.35;g.globalCompositeOperation='destination-out';g.drawImage(granule(L.width,L.height),0,0)}
 c.save();c.globalCompositeOperation=o.op||'source-over';c.drawImage(L,0,0);c.restore()}
function circ(x,y,rx,ry,n){const p=[];n=n||14;for(let i=0;i<n;i++){const a=i/n*Math.PI*2;p.push([x+Math.cos(a)*rx,y+Math.sin(a)*(ry??rx)])}return p}
// 手で描いた線
function ink(c,pts,o){o=o||{};const r=R_(o.seed||3);c.save();c.strokeStyle=o.col||'rgba(60,36,24,.8)';c.lineCap='round';c.lineJoin='round';
 for(let k=0;k<(o.pass??2);k++){c.lineWidth=(o.w??1.6)*(k?.6:1);c.globalAlpha=k?.5:1;c.beginPath();pts.forEach((p,i)=>{const x=p[0]+gauss(r)*(o.j??.8),y=p[1]+gauss(r)*(o.j??.8);i?c.lineTo(x,y):c.moveTo(x,y)});if(o.close)c.closePath();c.stroke()}c.restore()}
// 光（にじむ・下から照らす）
function glow(c,x,y,r,rgb,a){const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,`rgba(${rgb},${a})`);g.addColorStop(.3,`rgba(${rgb},${a*.45})`);g.addColorStop(1,`rgba(${rgb},0)`);c.fillStyle=g;c.beginPath();c.arc(x,y,r,0,7);c.fill()}
// もみじの葉
function leaf(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);c.beginPath();for(let i=0;i<7;i++){const a=-Math.PI/2+(i-3)*.62,L=i==3?1:i==2||i==4?.9:i==1||i==5?.66:.38;c.lineTo(Math.cos(a-.2)*s*L*.42,Math.sin(a-.2)*s*L*.42);c.lineTo(Math.cos(a)*s*L,Math.sin(a)*s*L);c.lineTo(Math.cos(a+.2)*s*L*.42,Math.sin(a+.2)*s*L*.42)}c.lineTo(0,s*.25);c.closePath();c.fill();c.restore()}
G.PAINT={R_,gauss,deform,wash,circ,ink,glow,leaf,fillPoly,granule};
})(window);
