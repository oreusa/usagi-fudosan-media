// 見開き2〜6（時計・入れ替え制と券・地図とバス・混み具合・おわり）
import {THREE,art,glowArt,pageArt,mapleClump,tahotoShape,hallShape,lanternShape,rabbitShape,textOn,wob,R_,mix,leafShape,cl,sm,eo,eio} from './popup.js';
const MAP=['#9a2a1c','#c8452a','#e0682e','#b8341f','#f08a3a'],MAPN=['#5a1a14','#c84a22','#ff8a3a','#e0602a','#ffb050'];
const INK='#3a2418',GOLD='#b8862e';
// 光る点（足し算で光る丸）
function dotTex(){const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');const gr=g.createRadialGradient(64,64,0,64,64,64);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.25,'rgba(255,230,180,.8)');gr.addColorStop(1,'rgba(255,200,120,0)');g.fillStyle=gr;g.fillRect(0,0,128,128);return new THREE.CanvasTexture(c)}
let DT=null;export function glowDot(parent,x,y,z,s,col){DT=DT||dotTex();const m=new THREE.MeshBasicMaterial({map:DT,color:new THREE.Color(col||'#ffc070').multiplyScalar(2.2),transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,opacity:0});
 const me=new THREE.Mesh(new THREE.PlaneGeometry(s,s),m);me.position.set(x,y,z);parent.add(me);return me}
// 紙の上に寝かせて貼る（判子・地図の札など）
export function decal(B,L,c,w,h,x,z){const m=new THREE.MeshStandardMaterial({map:new THREE.CanvasTexture(c),transparent:true,roughness:.9,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2});m.map.colorSpace=THREE.SRGBColorSpace;
 const me=new THREE.Mesh(new THREE.PlaneGeometry(w,h),m);me.rotation.x=-Math.PI/2;me.position.set(x,.012,z);me.receiveShadow=true;L.near.add(me);return me}
const sky=(top,bot,moon,seed)=>art(6.2,4.6,(c,w,h)=>{const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,top);g.addColorStop(1,bot);c.fillStyle=g;c.beginPath();c.moveTo(0,h);c.lineTo(0,h*.08);c.quadraticCurveTo(w*.5,-h*.06,w,h*.08);c.lineTo(w,h);c.closePath();c.fill();
 if(moon){c.fillStyle='#fff3d0';c.beginPath();c.arc(w*moon[0],h*moon[1],h*.07,0,7);c.fill()}const r=R_(seed||4);if(seed)for(let i=0;i<90;i++){c.fillStyle='#fff6e0';c.beginPath();c.arc(r()*w,r()*h*.7,1.5+r()*3,0,7);c.fill()}});
const skyGlow=(moon,seed)=>glowArt(6.2,4.6,(c,w,h)=>{const r=R_(seed||4);if(seed)for(let i=0;i<90;i++){c.fillStyle=`rgba(255,240,210,${.4+r()*.6})`;c.beginPath();c.arc(r()*w,r()*h*.7,1.5+r()*3,0,7);c.fill()}if(moon){c.fillStyle='#fff3d0';c.beginPath();c.arc(w*moon[0],h*moon[1],h*.07,0,7);c.fill()}});
const rab=(c,w,h,m,flip)=>{if(flip){c.translate(w,0);c.scale(-1,1)}rabbitShape(c,w*.42,h*.98,h*.66,'#f6efe2','#d8402a',m)};
function rabbit(B,L,x,d,flip,lampInt){const p=B.piece(L,'near',B.plane(art(1.1,1.2,(c,w,h)=>rab(c,w,h,0,flip)),1.1,1.2,{glow:glowArt(1.1,1.2,(c,w,h)=>rab(c,w,h,'glow',flip)),gi:2.2}),x,d);B.lamp(L,'near',x+(flip?-.25:.25),.85,d+.05,0xffb060,lampInt??.9,1.4);return p}

// ---- 2. 夕方→夜・懐中時計（受付の時間） ----
export function S_clock(B,Lprev,L){const F='far',N='near';
 B.piece(Lprev,F,B.plane(sky('#1c1f4a','#7a4a78',null,9),6.2,4.6,{glow:skyGlow(null,9),gi:.9}),0,1.15);
 const dusk=B.piece(Lprev,F,B.plane(art(6.2,2.6,(c,w,h)=>{const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,'rgba(240,140,90,0)');g.addColorStop(.6,'#f0a070');g.addColorStop(1,'#f6c890');c.fillStyle=g;c.fillRect(0,0,w,h)}),6.2,2.6,{glow:glowArt(6.2,2.6,(c,w,h)=>{const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,'#000');g.addColorStop(1,'#a05030');c.fillStyle=g;c.fillRect(0,0,w,h)}),gi:1.4,glowColor:'#ffb080'}),0,1.05);
 // 懐中時計（金のふち・文字盤）
 const R=1.15;const face=(c,w,h,g)=>{const cx=w/2,cy=w/2,r=w*.46;if(g){c.fillStyle='#000';return}c.fillStyle='#c9a35a';c.beginPath();c.arc(cx,cy,r,0,7);c.fill();c.fillRect(cx-w*.05,0,w*.1,w*.06);c.beginPath();c.arc(cx,w*.02,w*.07,0,7);c.lineWidth=w*.025;c.strokeStyle='#c9a35a';c.stroke();
  c.fillStyle='#fbf3e0';c.beginPath();c.arc(cx,cy,r*.86,0,7);c.fill();c.strokeStyle=INK;for(let i=0;i<60;i++){const a=i/60*6.283;const L2=i%5?r*.04:r*.1;c.lineWidth=i%5?2:6;c.beginPath();c.moveTo(cx+Math.sin(a)*r*.8,cy-Math.cos(a)*r*.8);c.lineTo(cx+Math.sin(a)*(r*.8-L2),cy-Math.cos(a)*(r*.8-L2));c.stroke()}
  c.fillStyle=INK;c.font=`${r*.16}px MB`;c.textAlign='center';c.textBaseline='middle';[12,3,6,9].forEach((n,i)=>{const a=i/4*6.283;c.fillText(String(n),cx+Math.sin(a)*r*.6,cy-Math.cos(a)*r*.6)});
  // 受付の時間（5:30〜8:30）を朱で塗る
  c.fillStyle='rgba(200,60,40,.25)';c.beginPath();c.moveTo(cx,cy);c.arc(cx,cy,r*.74,-Math.PI/2+5.5/12*6.283,-Math.PI/2+8.5/12*6.283);c.closePath();c.fill()};
 const clockP=B.piece(Lprev,F,B.plane(art(2*R,2*R+.2,(c,w,h)=>{c.translate(0,h-w);face(c,w,h)}),2*R,2*R+.2),.2,.55);
 const hand=(len,wid,col)=>{const c=document.createElement('canvas');c.width=64;c.height=512;const g=c.getContext('2d');g.fillStyle=col;g.beginPath();g.moveTo(32,0);g.lineTo(52,440);g.lineTo(32,512);g.lineTo(12,440);g.closePath();g.fill();
  const m=new THREE.MeshStandardMaterial({map:new THREE.CanvasTexture(c),alphaTest:.5,side:2,roughness:.6,metalness:.2});m.map.colorSpace=THREE.SRGBColorSpace;const geo=new THREE.PlaneGeometry(wid,len);geo.translate(0,len/2,0);const me=new THREE.Mesh(geo,m);me.castShadow=true;return me};
 const hh=hand(R*.5,.12,INK),mh=hand(R*.72,.08,'#a8302a');[hh,mh].forEach((h,i)=>{h.position.set(0,R+.0,.02+i*.01);clockP.userData.me.add(h)});
 // 池と朱の橋・灯り
 const bridge=(c,w,h,g)=>{if(!g){c.fillStyle='#24203a';c.fillRect(0,h*.78,w,h*.22);mapleClump(c,w*.1,h*.45,w*.14,h*.3,MAPN,41,200);mapleClump(c,w*.9,h*.42,w*.14,h*.32,MAPN,42,200)}
  c.strokeStyle=g?'#000':'#b8382a';c.lineWidth=h*.06;c.beginPath();c.moveTo(w*.12,h*.84);c.quadraticCurveTo(w*.5,h*.38,w*.88,h*.84);c.stroke();c.lineWidth=h*.03;c.beginPath();c.moveTo(w*.12,h*.72);c.quadraticCurveTo(w*.5,h*.26,w*.88,h*.72);c.stroke();
  for(let i=0;i<=10;i++){const u=i/10,x=w*(.12+.76*u),y=h*(.72-Math.sin(u*Math.PI)*.23);c.lineWidth=h*.02;c.beginPath();c.moveTo(x,y);c.lineTo(x,y+h*.12);c.stroke()}};
 B.piece(L,N,B.plane(art(6.2,2.0,(c,w,h)=>bridge(c,w,h)),6.2,2.0),0,.35);
 const lamps=[];for(let i=0;i<7;i++){const u=i/6,x=-3.1+6.2*(.12+.76*u),y=2.0*(1-(.72-Math.sin(u*Math.PI)*.23))+.06;lamps.push(glowDot(L.near,x,y,.42,.26))}
 rabbit(B,L,-1.6,1.7,false,.8);
 const key=B.key,hemi=B.hemi;
 return {upd(a){const q=eio(sm(a,.6,3.4));const hr=17.5+3*q;hh.rotation.z=-((hr%12)/12)*Math.PI*2;mh.rotation.z=-((hr*60%60)/60)*Math.PI*2;
  dusk.userData.me.material.opacity=1;dusk.visible=dusk.visible&&q<.999;dusk.userData.me.material.emissiveIntensity=1.4*(1-q);dusk.userData.me.material.color.setScalar(1-q*.85);
  lamps.forEach((l,i)=>l.material.opacity=sm(q,i/7*.85,i/7*.85+.12));
  key.color.set(mix('#ffb070','#ffd9a8',q));key.intensity=70+20*(1-q);hemi.color.set(mix('#a070a0','#5a6aa8',q))}}}
export function page_clock(W,D){return pageArt((c,w,h)=>{c.fillStyle='rgba(60,70,120,.18)';c.fillRect(0,0,w,h*.3);
 textOn(c,'受付は 夕方5時半から 夜8時半まで',w/2,h*.43,`${h*.034}px MB`,INK);
 textOn(c,'17:30 ― 20:30',w/2,h*.51,`${h*.066}px MB`,'#a8302a');textOn(c,'12月6日まで 毎晩',w/2,h*.565,`${h*.028}px MB`,'#9a6a2a')},W,D)}

// ---- 3. 昼と夜は入れ替え制・前売りなし ----
export function S_ticket(B,Lprev,L){const F='far',N='near';
 const sp=art(6.2,4.6,(c,w,h)=>{c.beginPath();c.moveTo(0,h);c.lineTo(0,h*.08);c.quadraticCurveTo(w*.5,-h*.06,w,h*.08);c.lineTo(w,h);c.closePath();c.save();c.clip();
  const g1=c.createLinearGradient(0,0,0,h);g1.addColorStop(0,'#7fb4d8');g1.addColorStop(1,'#d8ecf0');c.fillStyle=g1;c.fillRect(0,0,w/2,h);const g2=c.createLinearGradient(0,0,0,h);g2.addColorStop(0,'#141a40');g2.addColorStop(1,'#2a3270');c.fillStyle=g2;c.fillRect(w/2,0,w/2,h);
  c.fillStyle='#ffe08a';c.beginPath();c.arc(w*.22,h*.22,h*.07,0,7);c.fill();c.fillStyle='#fff';c.globalAlpha=.85;for(const[x,y,s]of[[.1,.4,1],[.33,.33,.8]]){c.beginPath();c.ellipse(w*x,h*y,w*.08*s,h*.03*s,0,0,7);c.fill()}c.globalAlpha=1;
  c.fillStyle='#fff3d0';c.beginPath();c.arc(w*.78,h*.22,h*.065,0,7);c.fill();const r=R_(8);for(let i=0;i<50;i++){c.beginPath();c.arc(w*(.52+r()*.46),r()*h*.6,1.5+r()*2.5,0,7);c.fill()}
  c.restore();c.fillStyle='#c9a35a';c.fillRect(w/2-4,h*.04,8,h);textOn(c,'昼の拝観',w*.25,h*.46,`${h*.075}px MB`,'#3a2418');textOn(c,'夜の拝観',w*.75,h*.46,`${h*.075}px MB`,'#f6e2a8')});
 B.piece(Lprev,F,B.plane(sp,6.2,4.6,{glow:glowArt(6.2,4.6,(c,w,h)=>{c.fillStyle='#fff3d0';c.beginPath();c.arc(w*.78,h*.22,h*.065,0,7);c.fill();const r=R_(8);for(let i=0;i<50;i++){c.beginPath();c.arc(w*(.52+r()*.46),r()*h*.6,1.5+r()*2.5,0,7);c.fill()}}),gi:1}),0,1.15);
 // 昼の境内（左）と夜の境内（右）を1枚に
 const halls=(c,w,h,g)=>{if(!g){mapleClump(c,w*.12,h*.4,w*.13,h*.3,MAP,51,200);mapleClump(c,w*.88,h*.4,w*.13,h*.3,MAPN,52,200)}
  c.save();c.beginPath();c.rect(0,0,w/2,h);c.clip();if(!g)hallShape(c,w*.5,h*.98,w*.62,'#c03a28','#f2ead8');c.restore();
  c.save();c.beginPath();c.rect(w/2,0,w/2,h);c.clip();hallShape(c,w*.5,h*.98,w*.62,g?'#000':'#24161a',g?'#ffb860':'#4a2a1a');c.restore()};
 B.piece(Lprev,F,B.plane(art(6,2.3,(c,w,h)=>halls(c,w,h)),6,2.3,{glow:glowArt(6,2.3,(c,w,h)=>halls(c,w,h,1)),gi:2}),0,.4);
 // 札：昼の拝観／夜の拝観
 const tag=(t)=>art(1.5,.55,(c,w,h)=>{c.fillStyle='#f5ecd6';c.fillRect(0,0,w,h);c.strokeStyle='#c9a35a';c.lineWidth=5;c.strokeRect(8,8,w-16,h-16);textOn(c,t,w/2,h*.68,`${h*.5}px MB`,INK)});
 // 拝観券（立つ）
 const tk=art(2.4,1.25,(c,w,h)=>{c.fillStyle='#f6edd8';c.beginPath();c.roundRect(0,0,w,h,16);c.fill();c.fillStyle='#000';c.globalCompositeOperation='destination-out';for(const y of[h*.5]){c.beginPath();c.arc(0,y,h*.12,0,7);c.arc(w,y,h*.12,0,7);c.fill()}c.globalCompositeOperation='source-over';
  c.strokeStyle='#c9a35a';c.lineWidth=5;c.strokeRect(14,14,w-28,h-28);c.setLineDash([12,10]);c.beginPath();c.moveTo(w*.72,18);c.lineTo(w*.72,h-18);c.stroke();c.setLineDash([]);
  textOn(c,'拝 観 券',w*.36,h*.36,`${h*.15}px MB`,'#9a6a2a');textOn(c,'永観堂 夜の拝観',w*.36,h*.62,`${h*.13}px MB`,INK);});
 
 rabbit(B,L,-1.55,1.95,false,.8);
 // 判子（紙に押す）
 const tkp=B.piece(L,N,B.plane(tk,2.4,1.25),.15,1.35);
 const st=document.createElement('canvas');st.width=st.height=512;const sg=st.getContext('2d');sg.strokeStyle='#c0302a';sg.fillStyle='#c0302a';sg.lineWidth=26;sg.beginPath();sg.arc(256,256,226,0,7);sg.stroke();sg.lineWidth=6;sg.beginPath();sg.arc(256,256,190,0,7);sg.stroke();
 sg.font='120px MB';sg.textAlign='center';sg.fillText('前売り',256,236);sg.font='150px MB';sg.fillText('なし',256,396);
 const sm_=new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(st),transparent:true,depthWrite:false,opacity:0});sm_.map.colorSpace=THREE.SRGBColorSpace;const sd=new THREE.Mesh(new THREE.PlaneGeometry(.66,.66),sm_);sd.position.set(.86,.63,.03);tkp.userData.me.add(sd);
 return {upd(a){const q=sm(a,1.5,1.72);sd.material.opacity=q>0?.9:0;const s=1+(1-eo(q))*1.8;sd.scale.set(s,s,1);sd.position.z=.03+(1-eo(q))*.6;sd.rotation.z=-.2;
  tkp.userData.k=1}}}
export function page_ticket(W,D){return pageArt((c,w,h)=>{textOn(c,'昼とは 入れ替え制',w*.42,h*.45,`${h*.042}px MB`,INK);textOn(c,'前売り券は ありません',w*.42,h*.51,`${h*.042}px MB`,INK);textOn(c,'券は その夜 受付で',w*.42,h*.565,`${h*.028}px MB`,'#9a6a2a')},W,D)}

// ---- 4. 地図：京都駅→市バス5系統→永観堂・車は× ----
const ROUTE=[[-1.9,1.95],[-1.2,1.75],[-.4,1.7],[.2,1.35],[.9,1.1],[1.5,.75]];
function rpt(u){const n=ROUTE.length-1,f=u*n,i=Math.min(n-1,Math.floor(f)),k=f-i;const a=ROUTE[i],b=ROUTE[i+1];return[a[0]+(b[0]-a[0])*k,a[1]+(b[1]-a[1])*k]}
export function S_map(B,Lprev,L){const F='far',N='near';
 B.piece(Lprev,F,B.plane(sky('#3a6aa0','#b8d8e8',null,0),6.2,4.6),0,1.15);
 const mts=art(6.2,2.6,(c,w,h)=>{const r=R_(3);for(let i=0;i<5;i++){c.fillStyle=mix('#7e9a70','#4e6a48',i/5);const x=w*(.1+i*.2),hh=h*(.5+r()*.35);c.beginPath();c.moveTo(x-w*.22,h);c.quadraticCurveTo(x,h-hh*1.6,x+w*.22,h);c.fill()}textOn(c,'東 山',w*.2,h*.5,`${h*.09}px MB`,'#f5ecd6')});
 B.piece(Lprev,F,B.plane(mts,6.2,2.6),0,.7);
 const tem=(c,w,h)=>{c.fillStyle='#6e8a5a';c.beginPath();c.moveTo(0,h);c.quadraticCurveTo(w*.5,h*.45,w,h);c.fill();mapleClump(c,w*.2,h*.62,w*.18,h*.16,MAP,61,120);mapleClump(c,w*.8,h*.6,w*.18,h*.17,MAP,62,120);tahotoShape(c,w*.5,h*.66,w*.4,'#c03a28','#f2ead8')};
 B.piece(L,N,B.plane(art(1.9,2.1,tem),1.9,2.1),1.5,.55);
 const lab=(t,col)=>art(1.6,.5,(c,w,h)=>{c.fillStyle='#f5ecd6';c.fillRect(0,0,w,h);c.strokeStyle='#c9a35a';c.lineWidth=5;c.strokeRect(7,7,w-14,h-14);textOn(c,t,w/2,h*.7,`${h*.48}px MB`,col||INK)});
 B.piece(L,N,B.plane(lab('永観堂','#a8302a'),1.4,.44),1.5,.95);
 // 京都駅（小さな駅舎）
 const sta=art(1.8,1.0,(c,w,h)=>{c.fillStyle='#4a4a58';c.fillRect(w*.05,h*.3,w*.9,h*.7);c.fillStyle='#f2e6c8';for(let i=0;i<7;i++)c.fillRect(w*(.1+i*.115),h*.42,w*.07,h*.18);c.fillStyle='#2a2a34';c.fillRect(0,h*.22,w,h*.1);textOn(c,'京都駅',w/2,h*.92,`${h*.2}px MB`,'#f5ecd6')});
 B.piece(L,N,B.plane(sta,1.6,.9),-2.0,2.1);
 // バス（立つ・道を走る）
 const bus=art(1.0,.62,(c,w,h)=>{c.fillStyle='#2f8a5a';c.beginPath();c.roundRect(w*.02,h*.08,w*.96,h*.72,h*.16);c.fill();c.fillStyle='#f5ecd6';for(let i=0;i<4;i++)c.fillRect(w*(.08+i*.18),h*.2,w*.13,h*.24);c.fillStyle='#f6c64a';c.beginPath();c.arc(w*.86,h*.32,h*.12,0,7);c.fill();textOn(c,'5',w*.86,h*.4,`${h*.2}px MB`,'#2f6a4a');
  c.fillStyle='#222';c.beginPath();c.arc(w*.24,h*.82,h*.13,0,7);c.arc(w*.76,h*.82,h*.13,0,7);c.fill()});
 const bp=B.piece(L,N,B.plane(bus,1.0,.62),ROUTE[0][0],ROUTE[0][1]);
 // 車に×（後で起き上がる）
 const car=art(1.1,.75,(c,w,h)=>{c.fillStyle='#5a5a68';c.beginPath();c.roundRect(w*.05,h*.4,w*.9,h*.38,h*.1);c.fill();c.beginPath();c.roundRect(w*.25,h*.18,w*.5,h*.28,h*.08);c.fill();c.fillStyle='#222';c.beginPath();c.arc(w*.27,h*.8,h*.1,0,7);c.arc(w*.73,h*.8,h*.1,0,7);c.fill();
  c.strokeStyle='#c0302a';c.lineWidth=h*.1;c.lineCap='round';c.beginPath();c.moveTo(w*.15,h*.08);c.lineTo(w*.85,h*.9);c.moveTo(w*.85,h*.08);c.lineTo(w*.15,h*.9);c.stroke()});
 const cp=B.piece(L,N,B.plane(car,1.0,.68),-.55,2.3);cp.userData.k=0;
 return {upd(a){const q=eio(sm(a,.5,2.6));const[x,z]=rpt(q);bp.position.x=x;bp.position.z=z;bp.position.y=.006+Math.abs(Math.sin(a*14))*.02*(q>0&&q<1);cp.userData.k=eo(sm(a,2.7,3.1))}}}
export function page_map(W,D){return pageArt((c,w,h)=>{const X=x=>(x+W/2)/W*w,Z=z=>z/D*h;
 c.fillStyle='rgba(120,160,190,.55)';c.beginPath();c.moveTo(X(-.9),0);c.bezierCurveTo(X(-1.2),h*.3,X(-.5),h*.5,X(-1.0),h);c.lineTo(X(-.75),h);c.bezierCurveTo(X(-.25),h*.5,X(-.95),h*.3,X(-.65),0);c.fill();
 c.fillStyle='rgba(60,90,110,.8)';textOn(c,'鴨川',X(-.55),Z(1.2),`${h*.028}px MB`,'rgba(50,80,100,.85)');
 c.strokeStyle='rgba(58,36,24,.18)';c.lineWidth=h*.012;for(const z of[.9,1.8]){c.beginPath();c.moveTo(0,Z(z));c.lineTo(w,Z(z));c.stroke()}for(const x of[-2,0,1.8]){c.beginPath();c.moveTo(X(x),0);c.lineTo(X(x),h);c.stroke()}
 c.setLineDash([h*.004,h*.018]);c.lineCap='round';c.strokeStyle='#b0302a';c.lineWidth=h*.012;c.beginPath();ROUTE.forEach((p,i)=>i?c.lineTo(X(p[0]),Z(p[1])):c.moveTo(X(p[0]),Z(p[1])));c.stroke();c.setLineDash([]);
 textOn(c,'京都駅から 市バス5系統で',w*.5,h*.5,`${h*.04}px MB`,INK);textOn(c,'車では 入れません',w*.5,h*.56,`${h*.04}px MB`,'#a8302a')},W,D)}

// ---- 5. 11月後半は大変な人出（人が列で起き上がる） ----
export function S_crowd(B,Lprev,L){const F='far',N='near';
 B.piece(Lprev,F,B.plane(sky('#141a40','#2a3270',[.25,.2],6),6.2,4.6,{glow:skyGlow([.25,.2],6),gi:1}),0,1.15);
 const tw=(c,w,h,g)=>{tahotoShape(c,w*.7,h*.62,w*.3,g?'#000':'#2a1c2c',g?'#ffc874':'#4a3020');if(!g){mapleClump(c,w*.2,h*.62,w*.2,h*.2,MAPN,71,200);mapleClump(c,w*.88,h*.66,w*.14,h*.16,MAPN,72,160);c.fillStyle='#2e1a22';c.fillRect(0,h*.8,w,h*.2)}};
 B.piece(Lprev,F,B.plane(art(5.2,3.6,(c,w,h)=>tw(c,w,h)),5.2,3.6,{glow:glowArt(5.2,3.6,(c,w,h)=>tw(c,w,h,1)),gi:2}),0,.4);
 const rows=[];const r=R_(31);for(let k=0;k<4;k++){const ppl=art(6,1.0+k*.12,(c,w,h)=>{const n=9+k*2;for(let i=0;i<n;i++){const x=w*(.04+.92*(i+.5*(k%2))/n),s=h*(.72+r()*.2);c.fillStyle=['#4a3a58','#5a3a3a','#3a4058','#5a4860'][(i+k)%4];
  if(r()<.22){rabbitShape(c,x,h,s*.7,'#efe6d6','#d8402a')}else{c.beginPath();c.ellipse(x,h-s*.86,s*.1,s*.11,0,0,7);c.fill();c.beginPath();c.moveTo(x-s*.18,h);c.quadraticCurveTo(x-s*.2,h-s*.7,x,h-s*.74);c.quadraticCurveTo(x+s*.2,h-s*.7,x+s*.18,h);c.fill()}}});
  const p=B.piece(L,N,B.plane(ppl,6,1.0+k*.12),0,.5+k*.55);p.userData.k=0;rows.push(p)}
 const lam=[];for(const x of[-2.6,2.6]){B.piece(L,N,B.plane(art(.5,1.0,(c,w,h)=>lanternShape(c,w/2,h,h*.92,'#2a2228','#6a5030')),.5,1.0,{glow:glowArt(.5,1.0,(c,w,h)=>lanternShape(c,w/2,h,h*.92,'#000','#ffd890')),gi:2.4}),x,1.0)}
 return {upd(a){rows.forEach((p,k)=>p.userData.k=eo(sm(a,.3+k*.45,.75+k*.45)))}}}
export function page_crowd(W,D){return pageArt((c,w,h)=>{textOn(c,'11月の後半は',w/2,h*.5,`${h*.04}px MB`,INK);textOn(c,'大変な人出に なりそうです',w/2,h*.56,`${h*.044}px MB`,'#a8302a')},W,D)}

// ---- 6. おわり：あしたは どこへ ----
export function S_end(B,Lprev,L){const F='far',N='near';
 B.piece(Lprev,F,B.plane(sky('#141a40','#2a3270',[.5,.3],12),6.2,4.6,{glow:skyGlow([.5,.3],12),gi:1.2}),0,1.15);
 const hills=art(6.2,2.0,(c,w,h)=>{c.fillStyle='#262a52';c.beginPath();c.moveTo(0,h);wob(c,[[0,h*.5],[w*.2,h*.2],[w*.4,h*.45],[w*.6,h*.15],[w*.8,h*.4],[w,h*.25]],30,4);c.lineTo(w,h);c.fill()});
 B.piece(Lprev,F,B.plane(hills,6.2,2.0),0,.7);
 const fr=art(6.2,3.4,(c,w,h)=>{mapleClump(c,w*.04,h*.32,w*.2,h*.28,MAP,81,300);mapleClump(c,w*.96,h*.3,w*.2,h*.28,MAP,82,300);c.fillStyle='#1a0e0c';c.fillRect(w*.03,h*.5,w*.035,h*.5);c.fillRect(w*.93,h*.5,w*.035,h*.5)});
 B.piece(L,N,B.plane(fr,6.2,3.4),0,1.0);
 const mid=(c,w,h,g)=>{if(!g){mapleClump(c,w*.2,h*.45,w*.16,h*.3,MAPN,83,220);mapleClump(c,w*.8,h*.42,w*.16,h*.32,MAPN,84,220)}for(const x of[.36,.64])lanternShape(c,w*x,h,h*.4,g?'#000':'#2a2228',g?'#ffd890':'#6a5030')};
 B.piece(Lprev,F,B.plane(art(6,2.4,(c,w,h)=>mid(c,w,h)),6,2.4,{glow:glowArt(6,2.4,(c,w,h)=>mid(c,w,h,1)),gi:2.4}),0,.35);
 const sign=art(1.5,1.5,(c,w,h)=>{c.fillStyle='#5a3a24';c.fillRect(w*.46,h*.25,w*.08,h*.75);c.fillStyle='#f5ecd6';c.beginPath();c.moveTo(w*.08,h*.12);c.lineTo(w*.8,h*.12);c.lineTo(w*.96,h*.24);c.lineTo(w*.8,h*.36);c.lineTo(w*.08,h*.36);c.closePath();c.fill();c.strokeStyle='#c9a35a';c.lineWidth=4;c.stroke();textOn(c,'あした',w*.46,h*.31,`${h*.16}px MB`,'#a8302a')});
 B.piece(L,N,B.plane(sign,1.5,1.5),1.3,1.7);
 rabbit(B,L,-.4,1.85,false,1.0);
 return {upd(a){}}}
export function page_end(W,D){return pageArt((c,w,h)=>{textOn(c,'あしたは どこへ いこう',w/2,h*.46,`${h*.046}px MB`,INK);textOn(c,'つづきは あしたの この時間に',w/2,h*.52,`${h*.03}px MB`,'#9a6a2a')},W,D)}
