// 公開中の月・燈のページで、地図が本当に動くかをスマホの幅で確かめる（作業環境から pages.dev に届かないため Actions で動かす）
// 地図を開く → 府県を押す → 近づくか → 戻る／＋−／カードの › → 地図リンク（Google/Apple を選ぶ画面）を、昼と夜で見る
const {chromium}=require('playwright');const fs=require('fs');
const OUT='out';fs.mkdirSync(OUT,{recursive:true});const log=[];const L=(...a)=>{const s=a.join(' ');console.log(s);log.push(s)};
const SITES=[['月',process.env.B1||'https://townnote.pages.dev',['/illumination','/koyo','/tomari','/odekake?v2t=map','/illumination-kyoto']],
             ['燈',process.env.B2||'https://lifenote-kanto.pages.dev',['/illumination','/koyo','/tomari','/odekake?v2t=map','/illumination-tokyo']]];
(async()=>{const b=await chromium.launch();let bad=0;
for(const [nm,base,paths] of SITES)for(const path of paths)for(const th of ['day','night']){
  const c=await b.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,deviceScaleFactor:2,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1 livetest'});
  await c.addInitScript(t=>{try{localStorage.setItem('usagi_theme',t);localStorage.setItem('tn_nudge','1')}catch(e){}},th);
  const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  const tag=nm+path+' '+th;let r={};
  try{
    await p.goto(base+path,{waitUntil:'load',timeout:45000});await p.waitForTimeout(2500);
    let open=await p.evaluate(()=>{const t=document.querySelector('.tn');return t&&t.classList.contains('fs')});
    if(!open){const bb=await p.evaluate(()=>{const e=document.querySelector('.tnbtn')||[...document.querySelectorAll('button,a')].find(x=>/地図で見る/.test(x.textContent)&&x.offsetParent);if(!e)return null;e.scrollIntoView({block:'center'});const q=e.getBoundingClientRect();return [q.x+q.width/2,q.y+q.height/2]});
      if(bb){await p.waitForTimeout(400);await p.touchscreen.tap(bb[0],bb[1]);await p.waitForTimeout(2000);}
      open=await p.evaluate(()=>{const t=document.querySelector('.tn');return t&&t.classList.contains('fs')});}
    r.open=open;
    const vb=()=>p.evaluate(()=>{const s=document.querySelector('.tn.fs svg');return s&&s.getAttribute('viewBox')});
    r.vb0=await vb();
    const pf=await p.evaluate(()=>{const f=[...document.querySelectorAll('.tn.fs svg .pf[data-p]')].filter(x=>!x.classList.contains('off'));if(!f.length)return null;let best=null,a=0;for(const e of f){const q=e.getBoundingClientRect();if(q.width*q.height>a){a=q.width*q.height;best=[q.x+q.width/2,q.y+q.height/2,e.getAttribute('data-p')]}}return best});
    r.pf=pf&&pf[2];
    if(pf){await p.touchscreen.tap(pf[0],pf[1]);await p.waitForTimeout(1600);}
    r.vb1=await vb();r.zoomed=!!(r.vb0&&r.vb1&&r.vb0!==r.vb1);
    await p.screenshot({path:`${OUT}/${nm}${path.replace(/[\/?=]/g,'_')}-${th}.jpg`,type:'jpeg',quality:60});
    const nx=await p.$('.tn .cnav.nx:not([hidden])');r.cardnext=null;
    if(nx){const t1=await p.evaluate(()=>(document.querySelector('.tn .cc.on .t')||{}).textContent);await nx.tap().catch(()=>{});await p.waitForTimeout(900);const t2=await p.evaluate(()=>(document.querySelector('.tn .cc.on .t')||{}).textContent);r.cardnext=t1!==t2;}
    const zin=await p.$('.tn .zm button');if(zin){const a=await vb();await zin.tap().catch(()=>{});await p.waitForTimeout(800);r.zoombtn=a!==await vb();}
    const gm=await p.evaluate(()=>{const e=[...document.querySelectorAll('.tn.fs a[href*="google.com/maps"]')].find(x=>x.offsetParent);if(!e)return null;const q=e.getBoundingClientRect();return [q.x+q.width/2,q.y+q.height/2]});
    if(gm){await p.touchscreen.tap(gm[0],gm[1]);await p.waitForTimeout(900);r.sheet=!!(await p.$('#umap-s.on'));}
  }catch(e){errs.push('TEST '+e.message.split('\n')[0]);}
  const ng=!r.open||!r.zoomed||errs.length||r.cardnext===false||r.zoombtn===false||r.sheet===false;if(ng)bad++;
  L((ng?'NG ':'OK ')+tag,JSON.stringify(r),errs.length?'ERR '+errs.join(' | '):'');
  await c.close();}
L('NG合計',bad);fs.writeFileSync(OUT+'/log.txt',log.join('\n'));await b.close();})();
