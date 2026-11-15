// クリスマスの絵（scene: 'xmas'）。canvas に描いて、ページの絵にする。mode 0 昼の赤レンガ／1 夕方のツリー／2 夜
function XR(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function xmCanvas(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c}
function xmGrain(c,W,H,a,seed){const r=XR(seed),cv=xmCanvas(256,256),g=cv.getContext('2d'),d=g.createImageData(256,256);
 for(let i=0;i<d.data.length;i+=4){const v=200+r()*55;d.data[i]=v;d.data[i+1]=v*.96;d.data[i+2]=v*.88;d.data[i+3]=255}g.putImageData(d,0,0);
 c.save();c.globalAlpha=a;c.globalCompositeOperation='multiply';c.fillStyle=c.createPattern(cv,'repeat');c.fillRect(0,0,W,H);c.restore()}
function xmGlow(c,x,y,r,col,a){const g=c.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,col.replace('A',a));g.addColorStop(.35,col.replace('A',a*.45));g.addColorStop(1,col.replace('A',0));c.fillStyle=g;c.fillRect(x-r,y-r,r*2,r*2)}
// れんが倉庫：x,y＝左下、w 幅、h 高さ。night で窓が灯る
function xmWarehouse(c,x,y,w,h,night,seed,k){const r=XR(seed);k=k||1;
 const top=y-h,roofH=h*.09;
 // 屋根
 c.fillStyle=night?'#1d1b26':'#4a4650';c.beginPath();c.moveTo(x-6*k,top+roofH*.2);c.lineTo(x+w*.04,top-roofH);c.lineTo(x+w*.96,top-roofH);c.lineTo(x+w+6*k,top+roofH*.2);c.closePath();c.fill();
 c.fillStyle=night?'#2a2733':'#5d5964';c.fillRect(x+w*.04,top-roofH,w*.92,roofH*.25);
 // 壁（れんが色の濃淡）
 const g=c.createLinearGradient(0,top,0,y);if(night){g.addColorStop(0,'#5a2a26');g.addColorStop(1,'#3a1a1c')}else{g.addColorStop(0,'#c0573c');g.addColorStop(1,'#9c3f2c')}
 c.fillStyle=g;c.fillRect(x,top,w,h);
 // れんがの目地
 c.save();c.beginPath();c.rect(x,top,w,h);c.clip();c.globalAlpha=night?.12:.16;c.strokeStyle=night?'#000':'#f3d2b8';c.lineWidth=.8*k;
 const bh=7*k,bw=18*k;for(let yy=top,row=0;yy<y;yy+=bh,row++){c.beginPath();c.moveTo(x,yy);c.lineTo(x+w,yy);c.stroke();for(let xx=x+(row%2?bw/2:0);xx<x+w;xx+=bw){c.beginPath();c.moveTo(xx,yy);c.lineTo(xx,yy+bh);c.stroke()}}
 c.globalAlpha=night?.08:.12;for(let i=0;i<w*h/400;i++){c.fillStyle=r()<.5?'#000':'#fff';c.fillRect(x+r()*w,top+r()*h,bw*.9,bh*.8)}c.restore();
 // 白い石の帯
 const bands=[top+h*.02,top+h*.34,top+h*.66];c.fillStyle=night?'#8c7f78':'#efe2cf';for(const b of bands)c.fillRect(x-2*k,b,w+4*k,h*.025);
 c.fillStyle=night?'#6d625c':'#d9c8b0';c.fillRect(x-4*k,y-h*.04,w+8*k,h*.04);
 // 窓：3段・アーチ
 const cols=Math.round(w/(34*k));const ww=w/cols;
 for(let fl=0;fl<3;fl++){const fy=top+h*(.08+fl*.32),fh=h*.2;
  for(let i=0;i<cols;i++){const wx=x+i*ww+ww*.28,wwid=ww*.44;
   const lit=night&&r()<.82;
   c.fillStyle=night?(lit?'#ffcf7a':'#241a22'):'#3b4a5c';
   c.beginPath();c.moveTo(wx,fy+fh);c.lineTo(wx,fy+wwid*.5);c.arc(wx+wwid/2,fy+wwid*.5,wwid/2,Math.PI,0);c.lineTo(wx+wwid,fy+fh);c.closePath();c.fill();
   if(!night){c.fillStyle='rgba(255,255,255,.35)';c.fillRect(wx+wwid*.15,fy+wwid*.35,wwid*.18,fh*.6)}
   c.strokeStyle=night?'#a8968a':'#f4ead8';c.lineWidth=2.2*k;c.stroke();
   c.lineWidth=1*k;c.beginPath();c.moveTo(wx+wwid/2,fy+wwid*.1);c.lineTo(wx+wwid/2,fy+fh);c.moveTo(wx,fy+fh*.55);c.lineTo(wx+wwid,fy+fh*.55);c.stroke();
   if(lit){c.save();c.globalCompositeOperation='lighter';xmGlow(c,wx+wwid/2,fy+fh*.5,wwid*1.6,'rgba(255,180,90,A)',.35);c.restore()}}}
 // 鉄のバルコニー（2階の前）
 c.strokeStyle=night?'#151418':'#2f2b2e';c.lineWidth=2*k;c.beginPath();c.moveTo(x,top+h*.36);c.lineTo(x+w,top+h*.36);c.stroke();
 for(let xx=x;xx<x+w;xx+=8*k){c.beginPath();c.moveTo(xx,top+h*.36);c.lineTo(xx,top+h*.31);c.stroke()}
 c.beginPath();c.moveTo(x,top+h*.31);c.lineTo(x+w,top+h*.31);c.stroke()}
// ツリー：cx 中心、by 根元、h 高さ
function xmTree(c,cx,by,h,night,t,seed){const r=XR(seed);const w=h*.42;t=t||0;
 // 影と幹
 c.fillStyle='rgba(0,0,0,.25)';c.beginPath();c.ellipse(cx,by,w*.7,h*.03,0,0,7);c.fill();
 c.fillStyle='#4a2e20';c.fillRect(cx-w*.06,by-h*.08,w*.12,h*.08);
 // 鉢（木の箱）
 c.fillStyle=night?'#6b2a22':'#a8322a';c.fillRect(cx-w*.2,by-h*.07,w*.4,h*.07);c.fillStyle='#d9b45a';c.fillRect(cx-w*.2,by-h*.07,w*.4,h*.008);
 // 枝の段（下から上へ）
 const tiers=7;for(let i=0;i<tiers;i++){const y0=by-h*.07-i*h*.122,ww=w*(1-i/tiers*.88),y1=y0-h*.22;
  const g=c.createLinearGradient(cx-ww,0,cx+ww,0);
  if(night){g.addColorStop(0,'#0c2a22');g.addColorStop(.5,'#1d4a38');g.addColorStop(1,'#0a201a')}else{g.addColorStop(0,'#1f4d3a');g.addColorStop(.45,'#3f7a55');g.addColorStop(1,'#1a3d2e')}
  c.fillStyle=g;c.beginPath();c.moveTo(cx,y1);
  const n=9;for(let j=0;j<=n;j++){const u=j/n,xx=cx-ww+u*ww*2,yy=y0+Math.sin(u*Math.PI)*h*.035+(j%2?h*.012:0);c.lineTo(xx,yy)}c.closePath();c.fill();
  // 針葉の筋
  c.strokeStyle=night?'rgba(120,200,160,.10)':'rgba(190,230,170,.22)';c.lineWidth=1.4;for(let j=0;j<ww/3;j++){const u=r(),xx=cx-ww*.9+u*ww*1.8,yy=y0-r()*h*.16;c.beginPath();c.moveTo(xx,yy);c.lineTo(xx+(xx<cx?-1:1)*6,yy+9);c.stroke()}}
 const top=by-h*.07-tiers*h*.122-h*.08;
 // 金のリボン（らせん）
 c.save();c.strokeStyle=night?'rgba(240,200,110,.75)':'rgba(230,190,90,.9)';c.lineWidth=h*.008;
 for(let k=0;k<5;k++){const yA=by-h*.12-k*h*.15;const wA=w*(1-((by-yA)/h)*.95);c.beginPath();c.moveTo(cx-wA*.85,yA);c.quadraticCurveTo(cx,yA+h*.05,cx+wA*.85,yA-h*.06);c.stroke()}c.restore();
 // オーナメント
 const cols=['#c0392b','#e2b84a','#f4ead8','#b03050','#d4af37'];
 for(let i=0;i<70;i++){const v=Math.pow(r(),.8),yy=by-h*.1-v*h*.78,half=w*(1-v*.92)*.85,xx=cx+(r()*2-1)*half;const s=h*(.009+r()*.01);
  c.fillStyle=cols[i%5];c.beginPath();c.arc(xx,yy,s,0,7);c.fill();c.fillStyle='rgba(255,255,255,.55)';c.beginPath();c.arc(xx-s*.35,yy-s*.35,s*.35,0,7);c.fill()}
 // 電球
 c.save();c.globalCompositeOperation='lighter';
 for(let i=0;i<140;i++){const v=Math.pow(r(),.75),yy=by-h*.1-v*h*.8,half=w*(1-v*.92)*.9,xx=cx+(r()*2-1)*half;const tw=.55+.45*Math.sin(t*2.4+i*1.7);
  xmGlow(c,xx,yy,h*(night?.03:.016),'rgba(255,210,120,A)',(night?.9:.55)*tw);c.fillStyle=`rgba(255,248,220,${(night?1:.8)*tw})`;c.beginPath();c.arc(xx,yy,h*.0035,0,7);c.fill()}
 c.restore();
 // 星
 c.save();c.translate(cx,top);c.globalCompositeOperation='lighter';xmGlow(c,0,0,h*(night?.16:.09),'rgba(255,220,130,A)',night?.85:.5);c.restore();
 c.save();c.translate(cx,top);c.fillStyle='#f6d36b';c.strokeStyle='#b8862a';c.lineWidth=2;c.beginPath();for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,rr=(i%2?.4:1)*h*.045;c.lineTo(Math.cos(a)*rr,Math.sin(a)*rr)}c.closePath();c.fill();c.stroke();c.restore()}
// 屋台（木の小屋）
function xmHut(c,x,y,w,night,seed){const r=XR(seed);const h=w*.62;
 c.fillStyle=night?'#3a2418':'#8a5a3a';c.fillRect(x,y-h,w,h);
 c.strokeStyle=night?'rgba(0,0,0,.4)':'rgba(60,30,15,.35)';c.lineWidth=1;for(let yy=y-h;yy<y;yy+=6){c.beginPath();c.moveTo(x,yy);c.lineTo(x+w,yy);c.stroke()}
 // 窓口（灯り）
 c.fillStyle=night?'#ffc979':'#f3dcb0';c.fillRect(x+w*.12,y-h*.78,w*.76,h*.42);
 if(night){c.save();c.globalCompositeOperation='lighter';xmGlow(c,x+w/2,y-h*.55,w*.9,'rgba(255,170,80,A)',.5);c.restore()}
 c.fillStyle=night?'#5a1f1a':'#a8322a';c.fillRect(x+w*.08,y-h*.36,w*.84,h*.08);
 // 三角屋根と雪のような白
 c.fillStyle=night?'#2a1c16':'#5a3a28';c.beginPath();c.moveTo(x-w*.1,y-h);c.lineTo(x+w/2,y-h-w*.36);c.lineTo(x+w*1.1,y-h);c.closePath();c.fill();
 c.fillStyle=night?'#cfc6d8':'#fbf6ee';c.beginPath();c.moveTo(x-w*.1,y-h);c.lineTo(x+w/2,y-h-w*.36);c.lineTo(x+w*1.1,y-h);c.lineTo(x+w*1.05,y-h+5);c.lineTo(x+w/2,y-h-w*.3);c.lineTo(x-w*.05,y-h+5);c.closePath();c.fill();
 // ガーランド
 c.strokeStyle='#2e5e40';c.lineWidth=4;c.beginPath();c.moveTo(x-w*.05,y-h+4);c.quadraticCurveTo(x+w/2,y-h+w*.12,x+w*1.05,y-h+4);c.stroke();
 for(let i=1;i<6;i++){const u=i/6,xx=x-w*.05+u*w*1.1,yy=y-h+4+Math.sin(u*Math.PI)*w*.06;c.fillStyle=i%2?'#c0392b':'#e2b84a';c.beginPath();c.arc(xx,yy,3,0,7);c.fill()}}
// 電球のひも
function xmString(c,x0,y0,x1,y1,sag,n,night,t){c.strokeStyle=night?'rgba(30,20,20,.8)':'rgba(60,40,30,.6)';c.lineWidth=1.5;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2,(y0+y1)/2+sag,x1,y1);c.stroke();
 c.save();c.globalCompositeOperation='lighter';for(let i=1;i<n;i++){const u=i/n,xx=(1-u)*(1-u)*x0+2*u*(1-u)*(x0+x1)/2+u*u*x1,yy=(1-u)*(1-u)*y0+2*u*(1-u)*((y0+y1)/2+sag)+u*u*y1;
  const tw=.6+.4*Math.sin((t||0)*3+i*2.1);xmGlow(c,xx,yy+4,night?22:12,'rgba(255,205,120,A)',(night?.8:.45)*tw);c.fillStyle=`rgba(255,246,215,${tw})`;c.beginPath();c.arc(xx,yy+4,2.6,0,7);c.fill()}c.restore()}
// 観覧車（遠景）
function xmWheel(c,cx,cy,R,night){c.save();c.strokeStyle=night?'rgba(160,190,255,.55)':'rgba(120,130,150,.55)';c.lineWidth=2;c.beginPath();c.arc(cx,cy,R,0,7);c.stroke();c.beginPath();c.arc(cx,cy,R*.92,0,7);c.stroke();
 for(let i=0;i<24;i++){const a=i/24*Math.PI*2;c.beginPath();c.moveTo(cx,cy);c.lineTo(cx+Math.cos(a)*R,cy+Math.sin(a)*R);c.lineWidth=.8;c.stroke();
  if(night){c.save();c.globalCompositeOperation='lighter';const hue=['rgba(255,120,170,A)','rgba(120,200,255,A)','rgba(255,220,120,A)','rgba(150,255,190,A)'][i%4];xmGlow(c,cx+Math.cos(a)*R,cy+Math.sin(a)*R,10,hue,.9);c.restore()}}
 c.lineWidth=3;c.beginPath();c.moveTo(cx,cy);c.lineTo(cx-R*.35,cy+R*1.25);c.moveTo(cx,cy);c.lineTo(cx+R*.35,cy+R*1.25);c.stroke();
 if(night){c.globalCompositeOperation='lighter';xmGlow(c,cx,cy,R*.5,'rgba(255,140,200,A)',.35)}c.restore()}
function xmSea(c,y0,y1,night,mode){const g=c.createLinearGradient(0,y0,0,y1);
 if(night){g.addColorStop(0,'#1c2752');g.addColorStop(1,'#0c1230')}else if(mode==1){g.addColorStop(0,'#c98aa0');g.addColorStop(1,'#7a5a8a')}else{g.addColorStop(0,'#9fc2d6');g.addColorStop(1,'#6c98b4')}
 c.fillStyle=g;c.fillRect(0,y0,920,y1-y0);c.strokeStyle=night?'rgba(255,220,160,.18)':'rgba(255,255,255,.35)';c.lineWidth=1.4;const r=XR(4);for(let i=0;i<40;i++){const x=r()*920,y=y0+6+r()*(y1-y0-8),l=20+r()*60;c.beginPath();c.moveTo(x,y);c.lineTo(x+l,y);c.stroke()}}
function xmSky(c,mode){const g=c.createLinearGradient(0,0,0,900);
 if(mode==0){g.addColorStop(0,'#cfe0ec');g.addColorStop(.6,'#eef0ea');g.addColorStop(1,'#f8efe0')}
 else if(mode==1){g.addColorStop(0,'#5a4a8a');g.addColorStop(.45,'#b46f93');g.addColorStop(.8,'#f0a77e');g.addColorStop(1,'#f8d3a0')}
 else{g.addColorStop(0,'#070b22');g.addColorStop(.6,'#16204a');g.addColorStop(1,'#2a2a5a')}
 c.fillStyle=g;c.fillRect(0,0,920,1380)}
function xmClouds(c,mode,seed){const r=XR(seed);c.save();c.globalAlpha=mode==2?.08:.5;c.fillStyle=mode==1?'#ffd9c2':'#ffffff';c.filter='blur(14px)';
 for(let i=0;i<7;i++){const x=r()*920,y=120+r()*420,w=120+r()*220;c.beginPath();c.ellipse(x,y,w,w*.18,0,0,7);c.fill()}c.restore()}
function xmStars(c,seed){const r=XR(seed);for(let i=0;i<110;i++){const x=r()*920,y=r()*620,s=r();c.fillStyle=`rgba(255,246,220,${.3+s*.7})`;c.beginPath();c.arc(x,y,.6+s*1.8,0,7);c.fill()}}
function xmBokeh(c,seed,n,y0,y1,a){const r=XR(seed);c.save();c.globalCompositeOperation='lighter';for(let i=0;i<n;i++){const x=r()*920,y=y0+r()*(y1-y0),s=14+r()*40;const col=['rgba(255,200,110,A)','rgba(255,150,120,A)','rgba(255,235,170,A)'][i%3];
 c.fillStyle=col.replace('A',a*(.3+r()*.7));c.beginPath();c.arc(x,y,s,0,7);c.fill()}c.restore()}
function xmGulls(c,seed,n){const r=XR(seed);c.strokeStyle='rgba(70,70,90,.7)';c.lineWidth=2.2;c.lineCap='round';for(let i=0;i<n;i++){const x=80+r()*560,y=180+r()*360,s=8+r()*12;c.beginPath();c.moveTo(x-s,y);c.quadraticCurveTo(x-s*.5,y-s*.6,x,y);c.quadraticCurveTo(x+s*.5,y-s*.6,x+s,y);c.stroke()}}
function xmFlags(c,x0,y0,x1,y1,sag,n){c.strokeStyle='rgba(80,50,40,.6)';c.lineWidth=1.2;c.beginPath();c.moveTo(x0,y0);c.quadraticCurveTo((x0+x1)/2,(y0+y1)/2+sag,x1,y1);c.stroke();
 const cols=['#c0392b','#2e6b4a','#e2b84a','#f4ead8'];for(let i=1;i<n;i++){const u=i/n,xx=(1-u)*(1-u)*x0+2*u*(1-u)*(x0+x1)/2+u*u*x1,yy=(1-u)*(1-u)*y0+2*u*(1-u)*((y0+y1)/2+sag)+u*u*y1;c.fillStyle=cols[i%4];c.beginPath();c.moveTo(xx-9,yy);c.lineTo(xx+9,yy);c.lineTo(xx,yy+22);c.closePath();c.fill()}}
function xmMoon(c,x,y,R){c.save();c.globalCompositeOperation='lighter';xmGlow(c,x,y,R*5,'rgba(255,240,200,A)',.22);c.restore();c.fillStyle='#fff3cf';c.beginPath();c.arc(x,y,R,0,7);c.fill();c.fillStyle='rgba(200,180,140,.25)';c.beginPath();c.arc(x-R*.3,y+R*.2,R*.25,0,7);c.arc(x+R*.3,y-R*.25,R*.15,0,7);c.fill()}
function xmPage(mode,t){const cv=xmCanvas(920,1380),c=cv.getContext('2d');const night=mode==2;
 xmSky(c,mode);if(night)xmStars(c,8);else xmClouds(c,mode,3+mode);
 if(mode==0){
  c.save();c.globalCompositeOperation='screen';xmGlow(c,230,560,420,'rgba(255,214,160,A)',.55);c.restore();
  xmGulls(c,6,6);
  xmWheel(c,150,640,120,false);
  xmSea(c,790,860,false,0);
  c.fillStyle='#d9cdbb';c.fillRect(0,860,920,520);
  xmWarehouse(c,-40,1010,560,190,false,11,1);
  xmWarehouse(c,560,980,420,150,false,12,.85);
  c.fillStyle='#e8dcc8';c.fillRect(0,1010,920,370);
  const pv=c.createLinearGradient(0,1010,0,1380);pv.addColorStop(0,'#d8c6ac');pv.addColorStop(1,'#b8a184');c.fillStyle=pv;c.fillRect(0,1010,920,370);
  c.strokeStyle='rgba(255,255,255,.25)';for(let y=1030;y<1380;y+=26){c.beginPath();c.moveTo(0,y);c.lineTo(920,y);c.stroke()}
  xmFlags(c,0,900,920,880,60,22);
  xmString(c,0,980,920,950,70,26,false,t);
  xmHut(c,140,1080,110,false,26);xmHut(c,290,1090,100,false,27);
  xmTree(c,620,1180,520,false,t,5);
  xmHut(c,30,1230,170,false,21);xmHut(c,240,1270,150,false,22);xmHut(c,770,1290,160,false,23);
 }else if(mode==1){
  xmClouds(c,1,9);
  xmWheel(c,780,700,110,false);
  xmSea(c,820,880,false,1);
  xmWarehouse(c,420,1000,560,210,false,13,1);
  const pv=c.createLinearGradient(0,1000,0,1380);pv.addColorStop(0,'#caa58c');pv.addColorStop(1,'#8f6c5c');c.fillStyle=pv;c.fillRect(0,1000,920,380);
  c.save();c.globalCompositeOperation='multiply';c.fillStyle='rgba(120,70,120,.25)';c.fillRect(0,0,920,1380);c.restore();
  xmTree(c,330,1300,1040,false,t,7);
  xmString(c,560,1040,920,990,40,12,false,t);
  xmHut(c,600,1290,170,false,24);xmHut(c,40,1320,130,false,25);
  c.save();c.globalCompositeOperation='screen';xmGlow(c,700,420,600,'rgba(255,190,140,A)',.25);c.restore();
 }else{
  xmMoon(c,180,210,44);
  xmWheel(c,120,700,120,true);
  xmSea(c,790,880,true,2);
  c.save();c.globalCompositeOperation='lighter';const r=XR(31);for(let i=0;i<60;i++){const x=r()*920,y=800+r()*75;c.fillStyle=`rgba(255,200,120,${.15+r()*.3})`;c.fillRect(x,y,8+r()*30,2)}c.restore();
  xmWarehouse(c,-40,1020,560,200,true,11,1);xmWarehouse(c,520,990,460,160,true,12,.85);
  const pv=c.createLinearGradient(0,1020,0,1380);pv.addColorStop(0,'#2a2030');pv.addColorStop(1,'#120c18');c.fillStyle=pv;c.fillRect(0,1020,920,360);
  xmString(c,0,940,920,910,80,26,true,t);xmString(c,0,1060,920,1040,50,22,true,t+1);
  c.save();c.globalCompositeOperation='lighter';xmGlow(c,320,900,520,'rgba(255,170,90,A)',.35);c.restore();
  xmTree(c,320,1230,780,true,t,5);
  xmHut(c,600,1240,150,true,21);xmHut(c,770,1270,130,true,22);
  c.save();c.globalCompositeOperation='lighter';xmGlow(c,320,1230,320,'rgba(255,190,110,A)',.28);c.restore();
  xmBokeh(c,41,26,700,1380,.18);
 }
 // 絵本の紙：周りを少し暗く・紙の目
 const vg=c.createRadialGradient(460,640,300,460,690,1000);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,night?'rgba(0,0,0,.45)':'rgba(80,50,30,.22)');c.fillStyle=vg;c.fillRect(0,0,920,1380);
 xmGrain(c,920,1380,night?.18:.3,77+mode);
 return cv.toDataURL('image/jpeg',.93)}
