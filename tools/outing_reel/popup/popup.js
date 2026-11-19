// 飛び出す絵本（pop-up book）エンジン。机の上の本を three.js で組み、ページ（葉）が背で回ると、
// 間に挟まれた紙の部品が起き上がる／たたまれる。部品の絵は canvas で描いた切り紙（色紙＋紙の目）。
// コマは時刻 t だけで決まる（何人かで分けて撮れる）。
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
export {THREE};
export const PX=300;  // 1単位あたりの絵の画素
export function R_(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
export const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),sm=(t,a,b)=>cl((t-a)/(b-a)),eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,eo=x=>1-Math.pow(1-x,3);
export function hx(h){h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
export function mix(a,b,k){const A=hx(a),B=hx(b);return'#'+A.map((v,i)=>Math.round(v+(B[i]-v)*k).toString(16).padStart(2,'0')).join('')}
// 紙の目（繊維）
let GRAIN=null;export function grain(){if(GRAIN)return GRAIN;const s=document.createElement('canvas');s.width=s.height=512;const g=s.getContext('2d');const d=g.createImageData(512,512);const r=R_(7);
 for(let i=0;i<d.data.length;i+=4){const v=128+(r()-.5)*40;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255}g.putImageData(d,0,0);
 g.globalAlpha=.25;for(let i=0;i<900;i++){g.strokeStyle=r()<.5?'#fff':'#000';g.lineWidth=.6;g.beginPath();const x=r()*512,y=r()*512,a=r()*6.3,l=4+r()*14;g.moveTo(x,y);g.quadraticCurveTo(x+Math.cos(a+.5)*l*.5,y+Math.sin(a+.5)*l*.5,x+Math.cos(a)*l,y+Math.sin(a)*l);g.stroke()}
 g.globalAlpha=1;g.filter='blur(.7px)';g.drawImage(s,0,0);GRAIN=s;return s}
// 切り紙の絵を作る：draw(c,W,H) は画素で描く。紙の目を重ね、ふちに白い紙の芯を少し出す
export function art(wu,hu,draw,opt={}){const W=Math.round(wu*PX),H=Math.round(hu*PX);const c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');draw(g,W,H);
 // 紙の芯（切り口）：形の少し内側に明るい線
 if(opt.core!==0){const e=document.createElement('canvas');e.width=W;e.height=H;const q=e.getContext('2d');q.drawImage(c,0,0);q.globalCompositeOperation='source-in';q.fillStyle='rgba(255,250,235,.55)';q.fillRect(0,0,W,H);
  const m=document.createElement('canvas');m.width=W;m.height=H;const k=m.getContext('2d');k.drawImage(e,0,0);k.globalCompositeOperation='destination-out';k.drawImage(c,2,2);k.drawImage(c,-1,-1);g.drawImage(m,0,0)}
 const t=document.createElement('canvas');t.width=W;t.height=H;const tg=t.getContext('2d');const G=grain();for(let y=0;y<H;y+=512)for(let x=0;x<W;x+=512)tg.drawImage(G,x,y);tg.globalCompositeOperation='destination-in';tg.drawImage(c,0,0);
 g.save();g.globalAlpha=opt.grain??.22;g.globalCompositeOperation='overlay';g.drawImage(t,0,0);g.restore();return c}
// 光る所（emissive）の絵：draw(c,W,H) で光る所だけを描く。黒＝光らない
export function glowArt(wu,hu,draw){const W=Math.round(wu*PX),H=Math.round(hu*PX);const c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,W,H);draw(g,W,H);return c}
function tex(c,r){const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=r.capabilities.getMaxAnisotropy();t.needsUpdate=true;return t}

export class Book{
 constructor(opt){this.o=Object.assign({W:6,D:5.6,cover:'#7a2a24'},opt);const W=this.o.W,D=this.o.D;
  const r=this.r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setPixelRatio(1);r.setSize(1080,1920);r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;
  r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.0;document.body.appendChild(r.domElement);
  const s=this.s=new THREE.Scene();s.background=new THREE.Color('#0d0a0c');s.fog=new THREE.Fog('#0d0a0c',14,30);
  this.cam=new THREE.PerspectiveCamera(30,1080/1920,.1,100);
  // 机（濃い胡桃の木目）
  const dc=document.createElement('canvas');dc.width=1024;dc.height=1024;const dg=dc.getContext('2d');const rr=R_(3);dg.fillStyle='#3a2416';dg.fillRect(0,0,1024,1024);
  for(let i=0;i<220;i++){dg.strokeStyle=`rgba(${rr()<.5?'20,10,4':'90,58,34'},${.15+rr()*.25})`;dg.lineWidth=1+rr()*3;dg.beginPath();const y=rr()*1024;dg.moveTo(0,y);for(let x=0;x<=1024;x+=64)dg.lineTo(x,y+Math.sin(x*.01+i)*6+(rr()-.5)*3);dg.stroke()}
  const dt=tex(dc,r);dt.wrapS=dt.wrapT=THREE.RepeatWrapping;dt.repeat.set(3,3);
  const desk=new THREE.Mesh(new THREE.PlaneGeometry(40,40),new THREE.MeshStandardMaterial({map:dt,roughness:.7}));desk.rotation.x=-Math.PI/2;desk.receiveShadow=true;s.add(desk);
  // 表紙の板（布張り）
  const cc=document.createElement('canvas');cc.width=cc.height=512;const cg=cc.getContext('2d');cg.fillStyle=this.o.cover;cg.fillRect(0,0,512,512);cg.globalAlpha=.18;for(let y=0;y<512;y+=3){cg.fillStyle=y%6?'#000':'#fff';cg.fillRect(0,y,512,1)}for(let x=0;x<512;x+=3){cg.fillStyle=x%6?'#000':'#fff';cg.fillRect(x,0,1,512)}
  const cm=new THREE.MeshStandardMaterial({map:tex(cc,r),roughness:.85});
  for(const zz of[-D/2-.05,D/2+.05]){const b=new THREE.Mesh(new THREE.BoxGeometry(W+.3,.06,D+.18),cm);b.position.set(0,.03,zz);b.castShadow=b.receiveShadow=true;s.add(b)}
  // 紙の束（手前と奥）
  const pm=new THREE.MeshStandardMaterial({color:'#e9dcc0',roughness:.95});this.blockN=new THREE.Mesh(new THREE.BoxGeometry(W,.1,D),pm);this.blockN.position.set(0,.11,D/2);this.blockN.receiveShadow=true;s.add(this.blockN);
  this.blockF=new THREE.Mesh(new THREE.BoxGeometry(W,.1,D),pm);this.blockF.position.set(0,.11,-D/2);this.blockF.receiveShadow=true;s.add(this.blockF);
  // 光：読書灯（暖かい・柔らかい影）＋部屋の青い明かり
  const key=this.key=new THREE.SpotLight(0xffd9a8,70,40,.55,.8,1.4);key.position.set(-4.5,11,6.5);key.target.position.set(0,1,0);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.bias=-.0004;key.shadow.normalBias=.02;key.shadow.radius=6;s.add(key,key.target);
  this.hemi=new THREE.HemisphereLight(0x5a6aa8,0x2a1608,.55);s.add(this.hemi);
  this.leaves=[];this.spreads=[];this.lamps=[];
  const comp=this.comp=new EffectComposer(r);comp.setPixelRatio(1);comp.setSize(1080,1920);comp.addPass(new RenderPass(s,this.cam));this.bloom=new UnrealBloomPass(new THREE.Vector2(540,960),.7,.6,.92);comp.addPass(this.bloom);comp.addPass(new OutputPass());}
 // 部品の板
 plane(c,wu,hu,opt={}){const r=this.r;const m=new THREE.MeshStandardMaterial({map:tex(c,r),alphaTest:.5,side:THREE.DoubleSide,roughness:.92,metalness:0});
  if(opt.glow){m.emissiveMap=tex(opt.glow,r);m.emissive=new THREE.Color(opt.glowColor||'#ffd9a0');m.emissiveIntensity=opt.gi??1.6}
  const g=new THREE.PlaneGeometry(wu,hu);g.translate(0,hu/2,0);const me=new THREE.Mesh(g,m);me.castShadow=true;me.receiveShadow=true;
  me.customDepthMaterial=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,map:m.map,alphaTest:.5});return me}
 // ページ（葉）：表に front の絵、裏に back の絵。背（x軸）で回る
 addLeaf(front,back){const W=this.o.W,D=this.o.D,r=this.r;const grp=new THREE.Group();this.s.add(grp);
  const mk=(c,flip)=>{const m=new THREE.MeshStandardMaterial({map:tex(c,r),roughness:.95});const g=new THREE.PlaneGeometry(W,D);g.rotateX(flip?Math.PI/2:-Math.PI/2);g.translate(0,0,D/2);
   const me=new THREE.Mesh(g,m);me.receiveShadow=true;me.castShadow=true;return me};
  const f=mk(front,false);f.position.y=.004;grp.add(f);const b=mk(back,true);b.position.y=-.004;grp.add(b);
  const L={grp,near:new THREE.Group(),far:new THREE.Group(),a:0};grp.add(L.near);grp.add(L.far);this.leaves.push(L);return L}
 // 部品を付ける：side='near'（この葉の表）か 'far'（この葉の裏＝次の見開きの奥）
 piece(L,side,me,x,d,opt={}){const p=new THREE.Group();p.position.set(x,side=='near'?.006:-.006,d);p.add(me);(side=='near'?L.near:L.far).add(p);p.userData={side,lean:opt.lean||0,bob:opt.bob||0,me};
  (side=='near'?(L.nearP=L.nearP||[]):(L.farP=L.farP||[])).push(p);return p}
 lamp(L,side,x,y,d,col,int,dist){const l=new THREE.PointLight(col,0,dist||3,1.6);l.position.set(x,y,d*(side=='near'?1:1));(side=='near'?L.near:L.far).add(l);l.userData={side,int};this.lamps.push({l,L,side});return l}
 // α（0＝手前に寝ている、π＝奥に寝ている）を葉ごとに決めて置く
 pose(alphas,t){const n=this.leaves.length;
  this.leaves.forEach((L,j)=>{const a=alphas[j];L.a=a;L.grp.rotation.x=-a;L.grp.position.y=.17+((n-j)*.012)*(1-a/Math.PI)+(j*.012)*(a/Math.PI)});
  // 見開き j の開き＝(前の葉の角度) − (この葉の角度)。前が無ければ π
  this.leaves.forEach((L,j)=>{const prev=j>0?this.leaves[j-1].a:Math.PI;const open=cl(prev-L.a,0,Math.PI);const b=Math.min(open,Math.PI/2);const vis=open>.002;
   (L.nearP||[]).forEach(p=>{p.rotation.x=Math.PI/2-b*(p.userData.k??1);p.visible=vis});
   if(j>0)(this.leaves[j-1].farP||[]).forEach(p=>{p.rotation.x=Math.PI/2+b*(p.userData.k??1);p.visible=vis});L.open=open/Math.PI});
  this.lamps.forEach(o=>{const j=this.leaves.indexOf(o.L);const sp=o.side=='near'?j:j+1;const L=this.leaves[sp];o.l.intensity=L?o.l.userData.int*Math.pow(L.open??0,2)*(o.on??1):0})}
 fx(t){if(!this.fxp){const n=140,geo=new THREE.BufferGeometry();this.fxd=[];const r=R_(5);for(let i=0;i<n;i++)this.fxd.push([r()*7-3.5,r(),r()*4-1,r()*.5+.15,r()*6.3]);geo.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(n*3),3));geo.setAttribute('color',new THREE.Float32BufferAttribute(new Float32Array(n*3),3));
   const c=document.createElement('canvas');c.width=c.height=64;const g=c.getContext('2d');const gr=g.createRadialGradient(32,32,0,32,32,32);gr.addColorStop(0,'#fff');gr.addColorStop(.3,'rgba(255,220,150,.7)');gr.addColorStop(1,'rgba(255,200,120,0)');g.fillStyle=gr;g.fillRect(0,0,64,64);
   this.fxp=new THREE.Points(geo,new THREE.PointsMaterial({size:.09,map:new THREE.CanvasTexture(c),vertexColors:true,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}));this.s.add(this.fxp);
   this.lv=[];const lc=document.createElement('canvas');lc.width=lc.height=128;const lg=lc.getContext('2d');lg.fillStyle='#d8482a';leafShape(lg,64,64,56,0);const lt=new THREE.CanvasTexture(lc);lt.colorSpace=THREE.SRGBColorSpace;
   for(let i=0;i<16;i++){const m=new THREE.Mesh(new THREE.PlaneGeometry(.22,.22),new THREE.MeshStandardMaterial({map:lt,alphaTest:.5,side:2,color:new THREE.Color().setHSL(.02+r()*.07,.8,.5+r()*.15)}));m.castShadow=true;this.s.add(m);this.lv.push([m,r()*6-3,r(),r()*3-.5,.12+r()*.1,r()*6.3])}}
  const P=this.fxp.geometry.attributes.position,C=this.fxp.geometry.attributes.color;this.fxd.forEach((d,i)=>{const y=((d[1]+t*d[3]*.25)%1)*5;P.setXYZ(i,d[0]+Math.sin(t*.6+d[4])*.3,y,d[2]+Math.cos(t*.5+d[4])*.2);const tw=.5+.5*Math.sin(t*3+d[4]*5);C.setXYZ(i,tw,tw*.85,tw*.6)});P.needsUpdate=C.needsUpdate=true;
  this.lv.forEach(([m,x,ph,z,sp,rot])=>{const q=(ph+t*sp*.25)%1;m.position.set(x+Math.sin(t*1.1+rot)*.5,5.2-q*5.2,z+Math.cos(t*.7+rot)*.3);m.rotation.set(t*1.3+rot,t*.9,t*.7+rot)})}
 draw(t){this.fx(t||0);this.comp.render()}
}
// ---------- 描く道具（切り紙） ----------
export function wob(c,pts,amp,seed){const r=R_(seed||1);c.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++){const p=pts[i],q=pts[i-1];c.quadraticCurveTo((p[0]+q[0])/2+(r()-.5)*amp,(p[1]+q[1])/2+(r()-.5)*amp,p[0],p[1])}}
export function leafShape(c,x,y,s,rot){c.save();c.translate(x,y);c.rotate(rot);c.beginPath();for(let i=0;i<7;i++){const a=-Math.PI/2+(i-3)*.62,L=i==3?1:i==2||i==4?.9:i==1||i==5?.66:.38;c.lineTo(Math.cos(a-.2)*s*L*.42,Math.sin(a-.2)*s*L*.42);c.lineTo(Math.cos(a)*s*L,Math.sin(a)*s*L);c.lineTo(Math.cos(a+.2)*s*L*.42,Math.sin(a+.2)*s*L*.42)}c.lineTo(0,s*.25);c.closePath();c.fill();c.restore()}
// もみじの房（切り紙）：外形はでこぼこの雲形。中に色の違う葉を重ねる
export function mapleClump(c,cx,cy,rx,ry,cols,seed,dense){const r=R_(seed);c.save();c.beginPath();const N=26;for(let i=0;i<=N;i++){const a=i/N*6.283;const k=1+(r()-.5)*.28;const x=cx+Math.cos(a)*rx*k,y=cy+Math.sin(a)*ry*k;if(i==0)c.moveTo(x,y);else{const ap=(i-.5)/N*6.283;c.quadraticCurveTo(cx+Math.cos(ap)*rx*1.18,cy+Math.sin(ap)*ry*1.18,x,y)}}c.closePath();c.fillStyle=cols[0];c.fill();
 c.clip();for(let i=0;i<(dense||160);i++){c.fillStyle=cols[1+(i%(cols.length-1))];const a=r()*6.283,d=Math.sqrt(r());leafShape(c,cx+Math.cos(a)*rx*d,cy+Math.sin(a)*ry*d,rx*(.07+r()*.08),r()*6.3)}c.restore();
 // ふちから飛び出す葉
 for(let i=0;i<34;i++){const a=r()*6.283;c.fillStyle=cols[1+(i%(cols.length-1))];leafShape(c,cx+Math.cos(a)*rx*1.05,cy+Math.sin(a)*ry*1.05,rx*(.08+r()*.06),a+Math.PI/2)}}
export function tahotoShape(c,cx,by,w,col,win){c.fillStyle=col;const roof=(y,ww,hh)=>{c.beginPath();c.moveTo(cx-ww*.6,y);c.quadraticCurveTo(cx-ww*.42,y-hh*.3,cx-ww*.2,y-hh);c.lineTo(cx+ww*.2,y-hh);c.quadraticCurveTo(cx+ww*.42,y-hh*.3,cx+ww*.6,y);c.quadraticCurveTo(cx,y-hh*.18,cx-ww*.6,y);c.closePath();c.fill()};
 const lo=w*.62,h1=w*.42;c.fillRect(cx-lo/2,by-h1,lo,h1);roof(by-h1+4,w,w*.16);c.beginPath();c.ellipse(cx,by-h1-w*.2,w*.22,w*.14,0,0,7);c.fill();c.fillRect(cx-w*.17,by-h1-w*.36,w*.34,w*.18);roof(by-h1-w*.32,w*1.1,w*.26);
 c.fillRect(cx-w*.018,by-h1-w*1.08,w*.036,w*.55);for(let i=0;i<7;i++){c.beginPath();c.ellipse(cx,by-h1-w*.62-i*w*.055,w*.055,w*.014,0,0,7);c.fill()}c.beginPath();c.arc(cx,by-h1-w*1.1,w*.03,0,7);c.fill();
 if(win){c.fillStyle=win;for(const k of[-.3,-.1,.1,.3])c.fillRect(cx+lo*k-lo*.06,by-h1*.82,lo*.12,h1*.55);c.fillRect(cx-w*.13,by-h1-w*.33,w*.26,w*.1)}}
export function hallShape(c,cx,by,w,col,win){c.fillStyle=col;c.fillRect(cx-w*.42,by-w*.2,w*.84,w*.2);c.beginPath();c.moveTo(cx-w*.62,by-w*.19);c.quadraticCurveTo(cx-w*.45,by-w*.24,cx-w*.36,by-w*.42);c.lineTo(cx+w*.36,by-w*.42);c.quadraticCurveTo(cx+w*.45,by-w*.24,cx+w*.62,by-w*.19);c.quadraticCurveTo(cx,by-w*.27,cx-w*.62,by-w*.19);c.fill();
 if(win){c.fillStyle=win;for(let i=0;i<6;i++)c.fillRect(cx-w*.37+i*w*.13,by-w*.16,w*.085,w*.13)}}
export function lanternShape(c,x,by,s,col,win){c.fillStyle=col;c.fillRect(x-s*.07,by-s*.5,s*.14,s*.5);c.fillRect(x-s*.22,by-s*.06,s*.44,s*.06);c.fillRect(x-s*.2,by-s*.86,s*.4,s*.34);c.beginPath();c.moveTo(x-s*.34,by-s*.84);c.lineTo(x,by-s*1.06);c.lineTo(x+s*.34,by-s*.84);c.closePath();c.fill();c.beginPath();c.arc(x,by-s*1.08,s*.05,0,7);c.fill();
 if(win){c.fillStyle=win;c.fillRect(x-s*.14,by-s*.8,s*.28,s*.22)}}
// うさぎ（切り紙）：ちょうちんを持って歩く。glow=true でちょうちんだけ光らせる
export function rabbitShape(c,x,by,s,body,lant,mode){c.save();c.translate(x,by);c.scale(s,s);
 if(mode!='glow'){c.fillStyle=body;
 c.beginPath();c.ellipse(0,-0.42,.3,.4,0,0,7);c.fill();               // からだ
 c.beginPath();c.ellipse(.04,-.98,.24,.22,0,0,7);c.fill();             // あたま
 c.beginPath();c.ellipse(-.06,-1.38,.07,.26,-.18,0,7);c.fill();c.beginPath();c.ellipse(.15,-1.36,.07,.25,.22,0,7);c.fill();  // 耳
 c.beginPath();c.arc(-.27,-.12,.09,0,7);c.fill();                        // しっぽ
 c.beginPath();c.ellipse(.1,-.02,.13,.06,0,0,7);c.fill();c.beginPath();c.ellipse(-.12,-.02,.12,.06,0,0,7);c.fill();
 c.fillStyle='#3a2418';c.beginPath();c.arc(.15,-1.0,.028,0,7);c.fill();c.fillStyle='#e8a0a0';c.beginPath();c.arc(.2,-.92,.035,0,7);c.fill();
 c.strokeStyle=body;c.lineWidth=.07;c.lineCap='round';c.beginPath();c.moveTo(.15,-.6);c.lineTo(.42,-.72);c.stroke();       // うで
 c.strokeStyle='#4a3020';c.lineWidth=.035;c.beginPath();c.moveTo(.4,-.74);c.lineTo(.62,-1.0);c.lineTo(.62,-.86);c.stroke();}  // 棒
 c.fillStyle=mode=='glow'?'#ffcf80':lant;c.beginPath();c.ellipse(.62,-.7,.13,.17,0,0,7);c.fill();if(mode!='glow'){c.fillStyle='#2a1a12';c.fillRect(.53,-.89,.18,.04);c.fillRect(.53,-.53,.18,.04)}
 c.restore()}
export function textOn(c,txt,x,y,font,col,opt={}){c.save();c.font=font;c.fillStyle=col;c.textAlign=opt.align||'center';c.textBaseline='alphabetic';if(opt.ls){c.letterSpacing=opt.ls}c.fillText(txt,x,y);c.restore()}
export function pageArt(draw,W,D,base){return art(W,D,(c,w,h)=>{c.fillStyle=base||'#f3e8d2';c.fillRect(0,0,w,h);const g=c.createRadialGradient(w/2,h*.4,h*.2,w/2,h*.5,h*.9);g.addColorStop(0,'rgba(255,255,255,0)');g.addColorStop(1,'rgba(120,80,30,.16)');c.fillStyle=g;c.fillRect(0,0,w,h);
 c.strokeStyle='rgba(185,140,70,.75)';c.lineWidth=w*.005;c.strokeRect(w*.04,h*.03,w*.92,h*.94);c.lineWidth=w*.0015;c.strokeRect(w*.052,h*.04,w*.896,h*.92);
 const r=R_(Math.round(h)%97+3);const cols=['#c8452a','#e0682e','#d9a23a','#b8341f'];for(let i=0;i<26;i++){const cx=r()<.5?w*(.07+r()*.16):w*(.77+r()*.16),cy=h*(.62+r()*.32);c.globalAlpha=.55+r()*.35;c.fillStyle=cols[i%4];leafShape(c,cx,cy,w*(.012+r()*.014),r()*6.3)}c.globalAlpha=1;
 if(draw)draw(c,w,h)},{core:0,grain:.3})}
