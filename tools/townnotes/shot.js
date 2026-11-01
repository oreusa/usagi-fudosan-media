// TOWN NOTE（仮）の地図を撮る（GitHub Actions でも手元でも動く）。node tools/townnotes/shot.js [URL]
const {chromium}=require('playwright');const fs=require('fs');
const U=process.argv[2]||'http://localhost:8765/townnotes/';
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2,hasTouch:true,isMobile:true});
const log=[];p.on('pageerror',e=>log.push('E '+e.message));p.on('console',m=>{if(m.type()=='error')log.push('C '+m.text())});
await p.route('**/c',r=>r.fulfill({status:204}));
fs.mkdirSync('shots/townnotes',{recursive:true});
const top=async(d)=>{await p.evaluate(d=>{const e=document.querySelector('.tn');scrollTo(0,e.getBoundingClientRect().top+scrollY-d)},d);await p.waitForTimeout(300);};
const tapCenter=async(sel)=>{const r=await p.evaluate(s=>{const e=document.querySelector(s);if(!e)return null;const b=e.getBoundingClientRect();return {x:b.left+b.width/2,y:b.top+b.height/2}},sel);if(r)await p.touchscreen.tap(r.x,r.y);return r;};
await p.goto(U);await p.waitForFunction(()=>window.__tnReady,null,{timeout:30000}).catch(()=>log.push('not ready'));await p.waitForTimeout(1500);
await top(70);await p.screenshot({path:'shots/townnotes/1-kansai.png'});
// 大阪の形を押す
const pt=await p.evaluate(()=>{const s=document.querySelector('.tn svg.m'),m=s.getScreenCTM(),q=s.createSVGPoint();q.x=(135.50-134)*82.2;q.y=(36-34.45)*100;const r=q.matrixTransform(m);return {x:r.x,y:r.y}});
await p.touchscreen.tap(pt.x,pt.y);await p.waitForTimeout(1200);await top(70);await p.screenshot({path:'shots/townnotes/2-osaka.png'});
// 件数がいちばん多い市・区を押す
const mp=await p.evaluate(()=>{const ts=[...document.querySelectorAll('.tn .lb.m:not(.hide)')];if(!ts.length)return null;ts.sort((a,b)=>+b.querySelector('b').textContent-+a.querySelector('b').textContent);const r=ts[0].getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2,t:ts[0].textContent}});
log.push('muni '+JSON.stringify(mp));if(mp){await p.touchscreen.tap(mp.x,mp.y);await p.waitForTimeout(1200);await top(70);await p.screenshot({path:'shots/townnotes/3-ward.png'});}
const pin=await p.evaluate(()=>{const c=[...document.querySelectorAll('.tn .pinx')].find(g=>+g.dataset.r>=7);if(!c)return null;const r=c.querySelector('.dot').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}});
if(pin){await p.touchscreen.tap(pin.x,pin.y);await p.waitForTimeout(900);await p.screenshot({path:'shots/townnotes/4-pin.png'});}else log.push('no pin');
await p.evaluate(()=>[...document.querySelectorAll('#flt button')].find(x=>x.textContent=='すべて').click());await p.waitForTimeout(300);
await p.evaluate(()=>document.querySelectorAll('.tabs button')[2].click());await p.waitForTimeout(1200);await top(70);await p.screenshot({path:'shots/townnotes/5-soon.png'});
fs.writeFileSync('shots/townnotes/log.txt',log.join('\n')+'\n');console.log(log.join('\n'));await b.close();})();
