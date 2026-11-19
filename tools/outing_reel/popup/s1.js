// 見開きの絵（永観堂）
import {art,glowArt,pageArt,mapleClump,tahotoShape,hallShape,lanternShape,rabbitShape,textOn,wob,R_,mix,leafShape} from './popup.js';
const NAVY=['#1d2350','#222a5e'],MAP=['#9a2a1c','#c8452a','#e0682e','#b8341f','#f08a3a'],MAPN=['#5a1a14','#c84a22','#ff8a3a','#e0602a','#ffb050'];
export function S_night(B,Lprev,L){const F='far',N='near';
 // 奥：夜空（星は穴＝光る）
 const skyG=glowArt(6.2,4.6,(c,w,h)=>{const r=R_(4);for(let i=0;i<120;i++){const s=r();c.fillStyle=`rgba(255,240,210,${.4+s*.6})`;c.beginPath();c.arc(r()*w,r()*h*.8,1.5+s*3.5,0,7);c.fill()}c.fillStyle='#fff3d0';c.beginPath();c.arc(w*.74,h*.2,h*.085,0,7);c.fill()});
 const sky=art(6.2,4.6,(c,w,h)=>{const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,'#141a40');g.addColorStop(1,'#2a3270');c.fillStyle=g;c.beginPath();c.moveTo(0,h);c.lineTo(0,h*.08);c.quadraticCurveTo(w*.5,-h*.06,w,h*.08);c.lineTo(w,h);c.closePath();c.fill();
  c.fillStyle='#fff3d0';c.beginPath();c.arc(w*.74,h*.2,h*.085,0,7);c.fill();const r=R_(4);for(let i=0;i<120;i++){const s=r();c.fillStyle='#fff6e0';c.beginPath();c.arc(r()*w,r()*h*.8,1.5+s*3.5,0,7);c.fill()}});
 B.piece(Lprev,F,B.plane(sky,6.2,4.6,{glow:skyG,gi:1.2}),0,1.15);
 // 遠い山
 const hills=art(6.2,2.3,(c,w,h)=>{c.fillStyle='#262a52';c.beginPath();c.moveTo(0,h);c.lineTo(0,h*.45);wob(c,[[0,h*.45],[w*.15,h*.2],[w*.3,h*.38],[w*.48,h*.12],[w*.66,h*.34],[w*.82,h*.18],[w,h*.4]],30,2);c.lineTo(w,h);c.closePath();c.fill()});
 B.piece(Lprev,F,B.plane(hills,6.2,2.3),0,.75);
 // 山の上の多宝塔ともみじ
 const tw=(c,w,h,mode)=>{const g=mode=='g';tahotoShape(c,w*.5,h*.6,w*.36,g?'#000':'#2a1c2c',g?'#ffc874':'#4a3020');
  if(!g){c.fillStyle='#2e1a22';c.beginPath();c.moveTo(0,h);c.lineTo(0,h*.66);c.quadraticCurveTo(w*.5,h*.5,w,h*.66);c.lineTo(w,h);c.fill();
   mapleClump(c,w*.17,h*.62,w*.17,h*.13,MAPN,11,200);mapleClump(c,w*.83,h*.6,w*.17,h*.14,MAPN,12,200);mapleClump(c,w*.5,h*.78,w*.3,h*.1,MAPN,13,220)}};
 B.piece(Lprev,F,B.plane(art(4.8,3.9,(c,w,h)=>tw(c,w,h)),4.8,3.9,{glow:glowArt(4.8,3.9,(c,w,h)=>tw(c,w,h,'g')),gi:2.2}),0,.35);
 // 手前：お堂ともみじの並木・灯籠
 const mid=(c,w,h,g)=>{if(!g){mapleClump(c,w*.12,h*.42,w*.16,h*.24,MAPN,21,260);mapleClump(c,w*.88,h*.4,w*.16,h*.25,MAPN,22,260)}
  hallShape(c,w*.5,h*.98,w*.5,g?'#000':'#24161a',g?'#ffb860':'#4a2a1a');
  for(const x of[.27,.73]){lanternShape(c,w*x,h,h*.32,g?'#000':'#2a2228',g?'#ffd890':'#6a5030')}};
 B.piece(L,N,B.plane(art(6,2.4,(c,w,h)=>mid(c,w,h)),6,2.4,{glow:glowArt(6,2.4,(c,w,h)=>mid(c,w,h,1)),gi:2.4}),0,.3);
 // いちばん手前：両わきの大きなもみじ（額のように）
 const front=art(6.2,3.6,(c,w,h)=>{c.fillStyle='#1a0e0c';c.fillRect(w*.04,h*.45,w*.035,h*.55);c.fillRect(w*.92,h*.42,w*.035,h*.58);
  mapleClump(c,w*.05,h*.3,w*.2,h*.26,MAP,31,320);mapleClump(c,w*.95,h*.26,w*.2,h*.26,MAP,32,320);
  const r=R_(5);for(let i=0;i<40;i++){c.fillStyle=MAP[1+i%4];leafShape(c,w*(.2+r()*.6),h*(.02+r()*.12),w*.018,r()*6)}});
 B.piece(L,N,B.plane(front,6.2,3.6),0,1.25);
 // うさぎ
 const rab=(c,w,h,m)=>rabbitShape(c,w*.42,h*.98,h*.66,'#f6efe2','#d8402a',m);
 const rp=B.piece(L,N,B.plane(art(1.1,1.2,(c,w,h)=>rab(c,w,h)),1.1,1.2,{glow:glowArt(1.1,1.2,(c,w,h)=>rab(c,w,h,'glow')),gi:3}),-1.2,2.1);
 B.lamp(L,N,-.95,.85,2.15,0xffb060,1.2,1.6);
 for(const x of[-1.4,1.4])B.lamp(L,N,x*.95,.7,.45,0xffa040,1.2,1.8);B.lamp(Lprev,F,0,1.6,.5,0xffb060,2.5,3);
 return {rabbit:rp}}
export function page_night(W,D){return pageArt((c,w,h)=>{c.fillStyle='#e9dcc0';c.beginPath();c.moveTo(w*.42,0);c.lineTo(w*.58,0);c.lineTo(w*.66,h*.34);c.lineTo(w*.34,h*.34);c.fill();
 textOn(c,'あすの夜から 永観堂の',w/2,h*.45,`${h*.042}px MB`,'#3a2418');textOn(c,'もみじに 灯りが ともります',w/2,h*.51,`${h*.042}px MB`,'#3a2418');
 textOn(c,'京都・永観堂　11月20日 ― 12月6日',w/2,h*.565,`${h*.026}px MB`,'#9a6a2a')},W,D)}
