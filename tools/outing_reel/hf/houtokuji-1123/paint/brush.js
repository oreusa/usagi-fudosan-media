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
