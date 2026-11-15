// 11/15 魔法の絵本（text.magic か scene xmas の時）。絵本から光がこぼれる・めくる端に光の粉・雪・夜空をそりが横切る・スノードーム。
// どのコマも時刻 t だけで決まる（コマを何人かで分けて撮るので、前のコマの状態を持たない）。
function mgSprite(rgb){const c=xmCanvas(64,64),g=c.getContext('2d'),q=g.createRadialGradient(32,32,0,32,32,32);
 q.addColorStop(0,`rgba(255,255,255,1)`);q.addColorStop(.12,`rgba(${rgb},.95)`);q.addColorStop(.35,`rgba(${rgb},.35)`);q.addColorStop(1,`rgba(${rgb},0)`);g.fillStyle=q;g.fillRect(0,0,64,64);return c}
const MG_GOLD=mgSprite('255,206,130'),MG_WARM=mgSprite('255,226,170'),MG_ICE=mgSprite('200,222,255'),MG_SNOW=(()=>{const c=xmCanvas(32,32),g=c.getContext('2d'),q=g.createRadialGradient(16,16,0,16,16,16);q.addColorStop(0,'rgba(255,255,255,1)');q.addColorStop(.45,'rgba(255,255,255,.75)');q.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=q;g.fillRect(0,0,32,32);return c})();
function mgDot(c,sp,x,y,r,a){if(a<=0||r<=0)return;c.globalAlpha=Math.min(1,a);c.drawImage(sp,x-r,y-r,r*2,r*2)}
// 4つの光の筋の星
function mgSpark(c,x,y,s,a,rot){if(a<=0)return;c.save();c.translate(x,y);c.rotate(rot||0);c.globalAlpha=Math.min(1,a);mgDot(c,MG_GOLD,0,0,s*2.2,a*.7);c.globalAlpha=Math.min(1,a);
 c.fillStyle='#fff3d6';c.beginPath();c.moveTo(0,-s);c.quadraticCurveTo(s*.09,-s*.09,s,0);c.quadraticCurveTo(s*.09,s*.09,0,s);c.quadraticCurveTo(-s*.09,s*.09,-s,0);c.quadraticCurveTo(-s*.09,-s*.09,0,-s);c.fill();c.restore()}
const mgBump=(t,a,b,c)=>t<=a||t>=c?0:t<b?Math.sin(Math.PI/2*(t-a)/(b-a)):Math.cos(Math.PI/2*(t-b)/(c-b));

// ---------- 絵の中：雪 ----------
function xmSnow(c,mode,t){const n=[46,70,96][mode],r=XR(700+mode);c.save();c.globalCompositeOperation='source-over';
 for(let i=0;i<n;i++){const x0=r()*XW,sp=28+r()*70,sz=1.2+r()*r()*5,ph=r()*7,y0=r()*(XH+60);
  const y=((y0+t*sp*(.6+sz/6))%(XH+60))-30,x=x0+Math.sin(t*.8+ph)*16*(sz/3+.4);
  mgDot(c,MG_SNOW,x,y,sz*1.6,(mode==0?.7:mode==1?.8:.85)*(.55+.45*Math.min(1,sz/3)))}
 for(let i=0;i<7;i++){const x0=r()*XW,sp=150+r()*90,sz=7+r()*7,ph=r()*7,y0=r()*(XH+200);const y=((y0+t*sp)%(XH+200))-100,x=x0+Math.sin(t*.6+ph)*30;mgDot(c,MG_SNOW,x,y,sz*1.8,mode==0?.28:.35)}
 c.restore()}
// ---------- 夕方：流れ星と、ツリーの星からのぼる光 ----------
function xmShoot(c,u){const k=(u-1.1)/.55;if(k<=0||k>=1.6)return;const e=Math.min(1,k),x=470-330*e,y=70+190*e;const a=k<1?1:1-(k-1)/.6;
 c.save();c.globalCompositeOperation='lighter';const L=170,dx=330/Math.hypot(330,190)*L,dy=190/Math.hypot(330,190)*L;
 for(const[w,al,bl]of[[7,.25,4],[2.2,.9,0]]){const g=c.createLinearGradient(x,y,x+dx,y-dy);g.addColorStop(0,`rgba(255,244,214,${al*a})`);g.addColorStop(1,'rgba(255,244,214,0)');c.strokeStyle=g;c.lineWidth=w;c.lineCap='round';c.filter=bl?`blur(${bl}px)`:'none';c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y-dy);c.stroke()}c.filter='none';
 mgDot(c,MG_WARM,x,y,22,a*.9);c.restore()}
function xmRise(c,x,y,t,seed,n){const r=XR(seed);c.save();c.globalCompositeOperation='lighter';
 for(let i=0;i<n;i++){const T=2.6+r()*1.6,p=((t/T+r())%1),vx=(r()-.5)*220,s=1.2+r()*2.6;const px=x+vx*p+Math.sin(t*1.3+i)*10,py=y-p*(260+r()*200);mgDot(c,MG_GOLD,px,py,s*3,Math.sin(Math.PI*p)*.9)}c.restore()}
// ---------- 夜：月の前をそりが横切る ----------
function mgDeer(c,x,y,k,ph){c.save();c.translate(x,y);c.scale(k,k);const la=Math.sin(ph)*.55;
 c.beginPath();c.ellipse(0,0,14,5.6,-.08,0,7);c.fill();                       // 体
 c.beginPath();c.moveTo(-10,-2);c.quadraticCurveTo(-15,-7,-17,-13);c.lineTo(-13.5,-13.5);c.quadraticCurveTo(-11,-7,-6,-3);c.fill();   // 首
 c.beginPath();c.ellipse(-19.5,-13.6,5,2.6,.25,0,7);c.fill();                 // 頭
 c.lineWidth=1.3;c.beginPath();c.moveTo(-16,-16);c.lineTo(-13,-24);c.moveTo(-14.4,-20.5);c.lineTo(-10,-22);c.moveTo(-13.5,-22.4);c.lineTo(-15.5,-26);c.moveTo(-17.5,-16);c.lineTo(-18,-23);c.moveTo(-17.8,-20);c.lineTo(-21,-22);c.stroke();   // 角
 c.lineWidth=2.4;c.lineCap='round';const leg=(lx,a)=>{c.beginPath();c.moveTo(lx,2);c.lineTo(lx+Math.sin(a)*9,2+Math.cos(a)*9);c.lineTo(lx+Math.sin(a)*9+Math.sin(a*1.6)*5,2+Math.cos(a)*9+5);c.stroke()};
 leg(-9,-.9+la);leg(-6,-.6-la);leg(9,.7-la);leg(11.5,.9+la);
 c.beginPath();c.moveTo(13,-3);c.lineTo(17,-6);c.stroke();c.restore()}
function mgSleighShape(c,x,y,k){c.save();c.translate(x,y);c.scale(k,k);
 c.beginPath();c.moveTo(-22,-4);c.quadraticCurveTo(-30,-16,-22,-20);c.quadraticCurveTo(-16,-22,-17,-14);c.lineTo(18,-12);c.quadraticCurveTo(26,-12,26,-22);c.lineTo(30,-22);c.quadraticCurveTo(31,2,14,2);c.lineTo(-14,2);c.quadraticCurveTo(-20,2,-22,-4);c.fill();   // そり
 c.lineWidth=1.8;c.beginPath();c.moveTo(-30,8);c.quadraticCurveTo(-36,4,-33,-1);c.moveTo(-30,8);c.lineTo(26,8);c.quadraticCurveTo(32,8,32,3);c.moveTo(-14,2);c.lineTo(-14,8);c.moveTo(16,2);c.lineTo(16,8);c.stroke();   // すべり板
 c.beginPath();c.arc(4,-24,8,0,7);c.fill();c.beginPath();c.arc(4,-35,4.6,0,7);c.fill();c.beginPath();c.moveTo(0,-38);c.quadraticCurveTo(-4,-46,-9,-44);c.lineTo(-8,-40);c.quadraticCurveTo(-3,-41,8,-37);c.fill();   // サンタ
 c.beginPath();c.ellipse(19,-25,7,9,.3,0,7);c.fill();c.restore()}   // 袋
function mgPath(s){return[980-1110*s,58+190*Math.pow(1.4416*Math.max(0,s),3)]}   // 右上の文字の上を通って、月の前へ
function xmSleigh(c,u){const s=(u-.45)/3.4;if(s<=0||s>1.4)return;c.save();
 // 光の帯：通った道をなめらかに、先ほど細く明るい
 c.globalCompositeOperation='lighter';const s0=Math.max(0,s-.42),s1=Math.min(1,s);
 for(const[wm,al,bl]of[[16,.16,7],[6,.35,2],[1.6,.85,0]]){c.filter=bl?`blur(${bl}px)`:'none';for(let j=0;j<40;j++){const a0=s0+(s1-s0)*j/40,a1=s0+(s1-s0)*(j+1)/40;if(a1<=a0)continue;const f=(j+1)/40,fade=Math.max(0,1-(s-a1)*2.6);
   const p0=mgPath(a0),p1=mgPath(a1);c.strokeStyle=`rgba(255,${206+30*f|0},${140+60*f|0},${(al*f*fade).toFixed(3)})`;c.lineWidth=wm*(.3+.7*f);c.lineCap='round';c.beginPath();c.moveTo(p0[0]+24,p0[1]+4+(s-a0)*90);c.lineTo(p1[0]+24,p1[1]+4+(s-a1)*90);c.stroke()}}
 c.filter='none';
 // 帯からこぼれる少しの光
 const r=XR(808);for(let j=0;j<14;j++){const sb=s-r()*.3;if(sb<0||sb>1)continue;const[px,py]=mgPath(sb);const age=s-sb;mgDot(c,MG_WARM,px+24+(r()-.5)*20,py+4+age*90+age*120*r(),2.4+r()*2,Math.max(0,.7-age*2.4))}
 if(s<1.05){c.globalCompositeOperation='source-over';c.globalAlpha=1;const[x,y]=mgPath(s);const t2=u*9,K=1.2;
  const ds=[62,100,138,176].map((d,i)=>{const q=mgPath(s+d*K/1110);return[q[0],q[1]-4+Math.sin(t2+i)*1.6]});
  const draw=()=>{c.lineWidth=.9;c.beginPath();c.moveTo(x-26*K,y-6*K);for(const d of ds)c.lineTo(d[0]+12*K,d[1]-6*K);c.stroke();mgSleighShape(c,x,y,K);ds.forEach((d,i)=>mgDeer(c,d[0],d[1],K,t2+i*1.2))};
  c.shadowColor='rgba(255,196,110,.95)';c.shadowBlur=10;c.fillStyle='#f2c879';c.strokeStyle='#f2c879';draw();   // ふちの金
  c.shadowBlur=0;c.fillStyle='#161a33';c.strokeStyle='#161a33';c.save();c.translate(-.9,.9);draw();c.restore()}   // 影絵
 c.restore()}
// 絵の中の動き（xmas.js の xmPage から毎コマ呼ぶ）
function xmFx(c,mode,t,u){xmSnow(c,mode,t);if(mode==1)xmShoot(c,u);if(mode==2)xmSleigh(c,u)}

// ---------- 日付のページ：赤レンガとツリーのスノードーム ----------
const GW=460,GH=600,GX=230,GY=250,GR=200;let GBASE=null,GL=[],GGLASS=null,GFRONT=null;
function mgGlobeInit(){if(GBASE)return;GBASE=xmCanvas(GW,GH);const c=GBASE.getContext('2d');GL=[];
 const q=c.createRadialGradient(GX,GY-70,20,GX,GY,GR);q.addColorStop(0,'#33427f');q.addColorStop(.6,'#1a2253');q.addColorStop(1,'#0c1130');c.fillStyle=q;c.fillRect(0,0,GW,GH);
 const r=XR(41);for(let i=0;i<60;i++){c.fillStyle=`rgba(255,246,222,${.2+r()*.6})`;c.beginPath();c.arc(GX-GR+r()*GR*2,GY-GR+r()*GR*1.1,.5+r()*1.3,0,7);c.fill()}
 c.save();c.globalCompositeOperation='screen';glow(c,GX+70,GY+60,200,'255,180,110',.25);c.restore();
 xmWarehouse(c,48,352,250,92,2,11,GL);
 wash(c,g=>wob(g,[[0,350],[GW,338],[GW,GH],[0,GH]],2,23),'#e9eef8',{grad:g=>{const h=g.createLinearGradient(0,340,0,460);h.addColorStop(0,'#f4f7fd');h.addColorStop(1,'#b9c4de');return h},edge:.15,gr:.2,light:false});
 xmTree(c,318,398,240,2,5,GL);
 xmHut(c,120,420,60,2,21,GL);
 wash(c,g=>wob(g,[[0,410],[140,398],[300,404],[GW,394],[GW,GH],[0,GH]],2,29),'#dfe6f4',{edge:.12,gr:.18,light:false});
 // ガラス（上に重ねる）
 GGLASS=xmCanvas(GW,GH);const g=GGLASS.getContext('2d');
 const rim=g.createRadialGradient(GX,GY,GR*.72,GX,GY,GR);rim.addColorStop(0,'rgba(190,210,255,0)');rim.addColorStop(.85,'rgba(190,210,255,.14)');rim.addColorStop(1,'rgba(230,240,255,.42)');g.fillStyle=rim;g.beginPath();g.arc(GX,GY,GR,0,7);g.fill();
 g.save();g.filter='blur(6px)';g.fillStyle='rgba(255,255,255,.34)';g.beginPath();g.ellipse(GX-92,GY-96,30,88,.75,0,7);g.fill();g.restore();
 g.fillStyle='rgba(255,255,255,.9)';g.beginPath();g.ellipse(GX-108,GY-118,8,18,.75,0,7);g.fill();
 g.strokeStyle='rgba(255,255,255,.35)';g.lineWidth=3;g.beginPath();g.arc(GX,GY,GR-6,.15,1.25);g.stroke();
 g.strokeStyle='rgba(255,255,255,.55)';g.lineWidth=1.5;g.beginPath();g.arc(GX,GY,GR,0,7);g.stroke();
 // 台（赤い木と金の帯）
 GFRONT=xmCanvas(GW,GH);const f=GFRONT.getContext('2d');
 f.save();f.filter='blur(10px)';f.fillStyle='rgba(60,35,20,.35)';f.beginPath();f.ellipse(GX,566,190,16,0,0,7);f.fill();f.restore();
 const bx=w=>[GX-w/2,GX+w/2];const[a0,a1]=bx(286),[b0,b1]=bx(360);
 const wd=f.createLinearGradient(b0,0,b1,0);wd.addColorStop(0,'#4a1714');wd.addColorStop(.35,'#8a2c24');wd.addColorStop(.6,'#76241e');wd.addColorStop(1,'#3e1210');
 f.fillStyle=wd;f.beginPath();f.moveTo(a0,430);f.lineTo(a1,430);f.quadraticCurveTo(b1,470,b1,548);f.quadraticCurveTo(GX,566,b0,548);f.quadraticCurveTo(a0,470,a0,430);f.fill();
 const gd=f.createLinearGradient(b0,0,b1,0);gd.addColorStop(0,'#8a6526');gd.addColorStop(.3,'#f2d58c');gd.addColorStop(.5,'#c99a45');gd.addColorStop(.75,'#f6dd9a');gd.addColorStop(1,'#7c5a22');
 f.fillStyle=gd;f.beginPath();f.ellipse(GX,431,145,13,0,0,7);f.fill();f.fillStyle='#5a1c18';f.beginPath();f.ellipse(GX,428,135,8,0,0,7);f.fill();
 f.save();f.beginPath();f.moveTo(a0,430);f.lineTo(a1,430);f.quadraticCurveTo(b1,470,b1,548);f.quadraticCurveTo(GX,566,b0,548);f.quadraticCurveTo(a0,470,a0,430);f.clip();f.fillStyle=gd;f.fillRect(b0,470,b1-b0,5);f.restore();f.beginPath();f.moveTo(b0,546);f.quadraticCurveTo(GX,566,b1,546);f.lineTo(b1,552);f.quadraticCurveTo(GX,574,b0,552);f.fill();
 f.fillStyle='#f0d38c';f.font='500 21px J';f.textAlign='center';f.letterSpacing='8px';if(P.globe)f.fillText(P.globe,GX+4,518);
 f.fillStyle='rgba(255,255,255,.18)';f.fillRect(a0+30,438,6,100)}
const GOUT=xmCanvas(GW,GH),GO=GOUT.getContext('2d');
function mgGlobe(t,u){mgGlobeInit();const c=GO;c.clearRect(0,0,GW,GH);c.save();c.beginPath();c.arc(GX,GY,GR-1,0,7);c.clip();c.drawImage(GBASE,0,0);
 c.globalCompositeOperation='lighter';for(const l of GL){const tw=l.soft?.85+.15*Math.sin(t*l.sp+l.p):.55+.45*Math.sin(t*l.sp+l.p);if(l.ell){xmEll(c,l,l.a*tw);continue}glow(c,l.x,l.y,l.r,l.c,l.a*tw);if(l.dot){c.fillStyle=`rgba(255,250,230,${.55+.45*tw})`;c.beginPath();c.arc(l.x,l.y,l.dot*.8,0,7);c.fill()}}
 // 中の雪：ページが来た時に舞い上がって、ゆっくり落ちる
 c.globalCompositeOperation='source-over';const r=XR(512),sw=Math.max(0,1-u/2.6);
 for(let i=0;i<110;i++){const a0=r()*7,rr=30+r()*170,sp=10+r()*22,sz=1+r()*2.4,y0=r()*420;
  const fall=((y0+t*sp)%420)+40,ang=a0+t*.25+sw*sw*3.2,swx=Math.cos(ang)*rr*.9,swy=Math.sin(ang)*rr*.55;
  const x=GX+swx*(.35+sw*.65)+Math.sin(t+i)*6,y=fall*(1-sw)+(GY+swy)*sw;mgDot(c,MG_SNOW,x,y,sz*1.5,.9)}
 c.restore();c.drawImage(GGLASS,0,0);c.drawImage(GFRONT,0,0);return GOUT.toDataURL('image/png')}

// ---------- ひいらぎ（水彩） ----------
function mgHolly(){const c=xmCanvas(320,230),g=c.getContext('2d');
 const leaf=(cx,cy,L,W,rot,seed,col)=>{const pts=[];for(let i=0;i<=20;i++){const u=i/20,x=(u-.5)*L,w=Math.sin(Math.PI*u)*W*(i%4==2?.62:1);pts.push([x,-w])}for(let i=20;i>=0;i--){const u=i/20,x=(u-.5)*L,w=Math.sin(Math.PI*u)*W*(i%4==0?.62:1);pts.push([x,w])}
  wash(g,h=>{h.save();h.translate(cx,cy);h.rotate(rot);pts.forEach((p,i)=>i?h.lineTo(p[0],p[1]):h.moveTo(p[0],p[1]));h.closePath();h.restore()},col,{edge:.55,gr:.3,ly0:cy-W,ly1:cy+W});
  g.save();g.translate(cx,cy);g.rotate(rot);g.strokeStyle='rgba(230,240,200,.45)';g.lineWidth=1.6;g.beginPath();g.moveTo(-L*.46,0);g.quadraticCurveTo(0,-3,L*.46,0);g.stroke();g.restore()};
 leaf(110,120,170,44,-.45,1,'#2f6b4a');leaf(212,122,160,40,.5,2,'#3d7d55');leaf(162,160,120,32,1.45,3,'#24573d');
 for(const[b,x,y]of[[0,152,112],[1,176,104],[2,166,130]]){wash(g,h=>h.arc(x,y,15,0,7),'#b8322a',{edge:.5,gr:.25});g.fillStyle='rgba(255,240,230,.75)';g.beginPath();g.arc(x-5,y-5,4,0,7);g.fill();g.fillStyle='rgba(60,20,10,.5)';g.beginPath();g.arc(x+3,y+5,1.8,0,7);g.fill()}
 return c.toDataURL('image/png')}
// 案内のページの下：雪の屋台の小さな水彩（ふちは紙に溶ける）
function mgMarket(){const c=xmCanvas(XW,420),g=c.getContext('2d');const L=[];
 wash(g,h=>h.ellipse(460,352,370,62,0,0,7),'#f4f3f0',{edge:.18,gr:.25,light:false,ec:'#b9c2d4'});
 xmString(g,110,170,810,160,56,16,2,L,12);
 xmHut(g,170,318,150,0,41,L);xmHut(g,380,330,170,0,42,L);xmHut(g,610,316,150,0,43,L);
 xmPerson(g,350,388,80,'#6b3a3a',0,44);xmPerson(g,374,392,72,'#2e4a5e',0,45);
 g.globalCompositeOperation='lighter';for(const l of L){if(l.ell){xmEll(g,l,l.a*.6);continue}glow(g,l.x,l.y,l.r*.8,l.c,l.a*.6);if(l.dot){g.fillStyle='rgba(255,250,230,.8)';g.beginPath();g.arc(l.x,l.y,l.dot,0,7);g.fill()}}
 g.globalCompositeOperation='destination-in';g.save();g.translate(460,260);g.scale(1,.55);const m=g.createRadialGradient(0,0,200,0,0,420);m.addColorStop(0,'rgba(0,0,0,1)');m.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=m;g.fillRect(-460,-480,920,960);g.restore();
 return c.toDataURL('image/png')}
// 紙のページの金の枠
function mgFrame(){const st=(x,y,s)=>`<path d="M${x},${y-s} Q${x+s*.12},${y-s*.12} ${x+s},${y} Q${x+s*.12},${y+s*.12} ${x},${y+s} Q${x-s*.12},${y+s*.12} ${x-s},${y} Q${x-s*.12},${y-s*.12} ${x},${y-s}Z" fill="#c9a24e"/>`;
 return `<g class="gfr" opacity=".75"><rect x="34" y="34" width="852" height="1312" rx="4" fill="none" stroke="#c9a24e" stroke-width="2"/><rect x="46" y="46" width="828" height="1288" rx="2" fill="none" stroke="#c9a24e" stroke-width=".9" opacity=".7"/>${st(34,34,14)}${st(886,34,14)}${st(34,1346,14)}${st(886,1346,14)}${st(460,34,8)}${st(460,1346,8)}</g>`}

// ---------- 本のまわり：光の粒・めくる端の光・開いた時に光があふれる ----------
// 座標は本を置いた机の上（#cam の中）。本は 84,232 から 920×1380
const BX=84,BY=232,BW=920,BH=1380;
// ぼけ玉：ふちが少し明るい、やわらかい円
function mgBokeh(c,x,y,R,rgb,a){if(a<=0)return;const g=c.createRadialGradient(x,y,0,x,y,R);g.addColorStop(0,`rgba(${rgb},${a*.55})`);g.addColorStop(.82,`rgba(${rgb},${a*.75})`);g.addColorStop(.93,`rgba(${rgb},${a})`);g.addColorStop(1,`rgba(${rgb},0)`);c.fillStyle=g;c.beginPath();c.arc(x,y,R,0,7);c.fill()}
function mgPre(){if(window.MGP)return MGP;const r=XR(4242);const P={bok:[],dust:[],rays:[]};
 const cols=['255,196,120','255,214,160','255,170,110','190,205,255'];
 for(let i=0;i<11;i++){const side=i%2;P.bok.push({x:side?900+r()*240:-60+r()*240,y:r()*1920,R:30+r()*70,v:6+r()*12,p:r()*7,c:cols[i%4],a:.05+r()*.07})}
 for(let i=0;i<70;i++)P.dust.push({x:BX+120+r()*(BW-240),y:BY+200+r()*1000,p:r()*7,v:6+r()*16,s:.8+r()*1.6});
 for(let i=0;i<9;i++)P.rays.push({a:-Math.PI/2+(i-4)*.2+(r()-.5)*.08,w:.05+r()*.07,l:900+r()*500,p:r()*7,al:.5+r()*.5});
 const spots=[[70,150,15],[168,96,9],[985,128,14],[905,70,8],[52,1700,12],[150,1790,16],[262,1850,8],[1010,1690,15],[905,1800,10],[790,1862,8],[1040,930,9],[30,1000,8],[40,520,7],[1050,420,7]];
 P.tw=spots.map(q=>({x:q[0],y:q[1],s:q[2]*1.4,p:r()*7,sp:1.2+r()*1.4}));
 window.MGP=P;return P}
function mgEdge(t,k){const a0=k==0?OPEN-1.25:ST[k]-TURN,a1=k==0?OPEN:ST[k];const q=sm(t,a0,a1);return{q,x:BX+BW*Math.cos(eio(q)*178*Math.PI/180)}}
function mgDraw(t){const cv=document.getElementById('mg');if(!cv)return;const c=cv.getContext('2d');c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.filter='none';c.clearRect(0,0,1080,1920);const P=mgPre();c.globalCompositeOperation='lighter';
 // 机のまわり：手前のぼけ玉（少しだけ、ゆっくり）
 for(const b of P.bok){const y=((b.y-t*b.v)%2100+2100)%2100-90;mgBokeh(c,b.x+Math.sin(t*.3+b.p)*20,y,b.R,b.c,b.a*(.75+.25*Math.sin(t*.7+b.p)))}
 // 本のまわりの金の星（またたく）
 for(const w of P.tw){const k=.55+.45*Math.sin(t*w.sp+w.p);mgSpark(c,w.x,w.y,w.s*(.7+.3*k),.35+.6*k,.3*Math.sin(t*.4+w.p))}
 // 表紙が開く時：ページから光の筋がさし、その中にほこりが光る
 const og=mgBump(t,1.5,2.7,4.6);if(og>0){const ox=544,oy=1180;c.save();c.filter='blur(9px)';
  for(const ry of P.rays){const a=ry.a+Math.sin(t*.4+ry.p)*.03,L=ry.l*(.6+.4*og);const g=c.createLinearGradient(ox,oy,ox+Math.cos(a)*L,oy+Math.sin(a)*L);g.addColorStop(0,`rgba(255,226,170,${.0})`);g.addColorStop(.12,`rgba(255,226,170,${.42*og*ry.al})`);g.addColorStop(1,'rgba(255,210,150,0)');
   c.fillStyle=g;c.beginPath();c.moveTo(ox,oy);c.lineTo(ox+Math.cos(a-ry.w)*L,oy+Math.sin(a-ry.w)*L);c.lineTo(ox+Math.cos(a+ry.w)*L,oy+Math.sin(a+ry.w)*L);c.closePath();c.fill()}
  c.filter='none';const g=c.createRadialGradient(ox,oy-200,30,ox,oy-200,700);g.addColorStop(0,`rgba(255,228,180,${.32*og})`);g.addColorStop(1,'rgba(255,200,140,0)');c.fillStyle=g;c.fillRect(0,0,1080,1920);
  for(const d of P.dust){const y=d.y-((t-1.5)*d.v),x=d.x+Math.sin(t*.8+d.p)*12;const tw=.5+.5*Math.sin(t*2+d.p*3);mgDot(c,MG_WARM,x,y,d.s*2.2,og*.55*tw)}c.restore()}
 // 最後：ボタンの上を光が横切り、まわりがほのかに明るくなる
 const te=ST[5]+3.2;if(t>te){const a=Math.min(1,(t-te)/.6);const g=c.createRadialGradient(544,1442,40,544,1442,420);g.addColorStop(0,`rgba(255,200,150,${.22*a})`);g.addColorStop(1,'rgba(255,200,150,0)');c.fillStyle=g;c.fillRect(0,1000,1080,900);
  const sw=((t-te-.6)%2.4)/1.1;if(sw>0&&sw<1){c.save();c.beginPath();c.roundRect?c.roundRect(84+142,232+1160,636,104,52):c.rect(84+142,232+1160,636,104);c.clip();const x=84+142-120+sw*(636+240);const q=c.createLinearGradient(x-60,0,x+60,0);q.addColorStop(0,'rgba(255,255,255,0)');q.addColorStop(.5,'rgba(255,245,225,.38)');q.addColorStop(1,'rgba(255,255,255,0)');c.fillStyle=q;c.fillRect(x-60,1380,120,140);c.restore()}}
 c.globalAlpha=1;c.globalCompositeOperation='source-over';c.filter='none'}
// ---------- 11/16 もみじ・浜の紙のページ：丸窓（夜の景色がのぞく）と、昼の景色の小さな水彩 ----------
function mgComposite(mode,lights,t){const X=xmBase(mode);const cv=xmCanvas(XW,XH),c=cv.getContext('2d');c.drawImage(X.B.cv,0,0);c.drawImage(X.T.cv,0,0);c.drawImage(X.F.cv,0,0);
 if(lights){c.globalCompositeOperation='lighter';for(const Ly of[X.B,X.T,X.F])for(const l of Ly.L){const tw=l.soft?.88+.12*Math.sin(t*l.sp+l.p):.6+.4*Math.sin(t*l.sp+l.p);if(l.ell){xmEll(c,l,l.a*tw);continue}glow(c,l.x,l.y,l.r*.8,l.c,l.a*tw);if(l.dot){c.fillStyle='rgba(255,250,232,.9)';c.beginPath();c.arc(l.x,l.y,l.dot,0,7);c.fill()}}c.globalCompositeOperation='source-over'}
 return cv}
let RW=null;const ROUT=xmCanvas(GW,GH),RO=ROUT.getContext('2d');
function mgRound(t,u){const hama=P.scene=='hama';if(!RW){RW=xmCanvas(GW,GH);const f=RW.getContext('2d');
  f.save();f.filter='blur(12px)';f.fillStyle='rgba(60,35,20,.35)';f.beginPath();f.ellipse(GX,GY+GR+30,GR*.9,18,0,0,7);f.fill();f.restore();
  // わく：もみじ＝木の丸窓、浜＝真ちゅうの丸窓
  const ring=f.createRadialGradient(GX-60,GY-60,GR*.6,GX,GY,GR+26);if(hama){ring.addColorStop(0,'#f6dc98');ring.addColorStop(.5,'#c99a45');ring.addColorStop(1,'#6e4e1c')}else{ring.addColorStop(0,'#8a5a3a');ring.addColorStop(.6,'#5a3622');ring.addColorStop(1,'#2a160c')}
  f.fillStyle=ring;f.beginPath();f.arc(GX,GY,GR+24,0,7);f.arc(GX,GY,GR,0,7,true);f.fill('evenodd');
  f.strokeStyle=hama?'rgba(255,240,200,.8)':'#c9a24e';f.lineWidth=2;f.beginPath();f.arc(GX,GY,GR+2,0,7);f.stroke();
  if(hama){for(let i=0;i<10;i++){const a=i/10*Math.PI*2;const x=GX+Math.cos(a)*(GR+12),y=GY+Math.sin(a)*(GR+12);const g=f.createRadialGradient(x-2,y-2,.5,x,y,6);g.addColorStop(0,'#fff4cc');g.addColorStop(1,'#8a6526');f.fillStyle=g;f.beginPath();f.arc(x,y,5.5,0,7);f.fill()}}
  else{const r=XR(3);f.strokeStyle='rgba(30,15,8,.35)';f.lineWidth=1;for(let i=0;i<40;i++){const a=r()*7,rr=GR+4+r()*18;f.beginPath();f.arc(GX,GY,rr,a,a+.3+r()*.6);f.stroke()}}}
 const c=RO;c.clearRect(0,0,GW,GH);c.drawImage(RW,0,0);c.save();c.beginPath();c.arc(GX,GY,GR,0,7);c.clip();
 const src=mgComposite(2,true,t);const k=.52,cx=460,cy=hama?1000:900;c.drawImage(src,cx-GR/k,cy-GR/k,GR*2/k,GR*2/k,GX-GR,GY-GR,GR*2,GR*2);
 if(P.scene=='momiji')mjFx(c,2,t,u);
 // ガラスの光
 c.fillStyle='rgba(255,255,255,.12)';c.beginPath();c.ellipse(GX-80,GY-90,40,90,.7,0,7);c.fill();c.restore();
 const v=c.createRadialGradient(GX,GY,GR*.7,GX,GY,GR);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,'rgba(0,0,0,.35)');c.fillStyle=v;c.beginPath();c.arc(GX,GY,GR,0,7);c.fill();
 return ROUT.toDataURL('image/png')}
function mgVig(){const src=mgComposite(0,false,0);const c=xmCanvas(XW,420),g=c.getContext('2d');const k=.62,sh=420/k;g.drawImage(src,0,1340-sh,XW,sh,(XW-XW*k)/2,0,XW*k,420);
 g.globalCompositeOperation='destination-in';g.save();g.translate(460,230);g.scale(1,.6);const m=g.createRadialGradient(0,0,160,0,0,380);m.addColorStop(0,'rgba(0,0,0,1)');m.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=m;g.fillRect(-460,-400,920,800);g.restore();return c.toDataURL('image/png')}
