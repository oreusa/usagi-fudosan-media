// 11/2 オーナー「全体不具合ダメ。全部確認、100パーセント、動作も」
// 公開中の月・燈の全ページで、押して動くかを確かめる（スマホの幅・iPhone の形）。
// ページごと：エラー／メニューが開いて閉じる／昼夜の切り替え／ボタンを全部押してエラーが出ないか／
// 府県・タブで中身が0にならないか／地図を開いて府県で近づく／Googleマップのリンクで選ぶ画面／中のリンクが開けるか（404 など）
// /koe は送信まで（隠し欄に字を入れて、保存されない形で）確かめる。結果は out/all.txt と out/all/*.jpg
const {chromium}=require('playwright');const fs=require('fs');
const OUT='out';fs.mkdirSync(OUT+'/all',{recursive:true});const log=[];const L=s=>{console.log(s);log.push(s)};
const SITES=[{nm:'月',base:process.env.B1||'https://townnote.pages.dev',extra:['/odekake','/ima','/fudosan','/fudosan-list','/chika-kansai','/chika-osaka','/uru','/gyosha','/machi/osaka-01','/koe','/koyo','/tomari']},
             {nm:'燈',base:process.env.B2||'https://usagi-life-notes.pages.dev',extra:['/odekake','/okaimono','/ima','/nesage','/kaimawari','/tanka','/furusato','/tomari','/koyo','/privacy','/koe']}];
const UA='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1 livetest';
async function list(s){let l=['/'];try{if(!API)API=await require('playwright').request.newContext();const x=await (await API.get(s.base+'/sitemap.xml')).text();for(const m of x.matchAll(/<loc>([^<]+)<\/loc>/g))l.push(new URL(m[1]).pathname);}catch(e){}
  l=l.filter(p=>!/^\/machi\//.test(p)).concat(s.extra).map(p=>p.replace(/\.html$/,''));return [...new Set(l)];}
const linkOK=new Map();
let API;async function checkLinks(base,hrefs){if(!API)API=await require('playwright').request.newContext();const bad=[];for(const h of hrefs){if(linkOK.has(h)){if(!linkOK.get(h))bad.push(h);continue;}
  let ok=true;try{const r=await API.get(base+h,{timeout:20000});ok=r.status()<400;}catch(e){ok=false}linkOK.set(h,ok);if(!ok)bad.push(h);}return bad;}
(async()=>{const b=await chromium.launch();let ng=0,n=0;
for(const s of SITES){const pages=await list(s);L(`## ${s.nm} ${pages.length}ページ`);
 for(const path of pages)for(const th of ['day','night']){n++;
  const c=await b.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,deviceScaleFactor:1,userAgent:UA});
  await c.addInitScript(t=>{try{localStorage.setItem('usagi_theme',t);localStorage.setItem('tn_nudge','1')}catch(e){}},th);
  await c.route(/\/c(\?|$)|\/c\?|koe-send|google\.com\/maps|maps\.apple\.com|rakuten|amazon|yahoo|moshimo|a8\.net|valuecommerce/,r=>{const u=r.request().url();if(/koe-send/.test(u))return r.continue();return r.fulfill({status:204,body:''})});
  const p=await c.newPage();const errs=[],bad=[];p.on('pageerror',e=>errs.push('JS '+e.message.slice(0,140)));
  p.on('response',r=>{const u=r.url();if(r.status()>=400&&u.startsWith(s.base))bad.push(r.status()+' '+u.replace(s.base,''))});
  const R={};const tag=`${s.nm}${path} ${th}`;
  try{
   await p.goto(s.base+path,{waitUntil:'load',timeout:45000});await p.waitForTimeout(1800);
   // 昼夜
   R.theme=await p.evaluate(t=>document.documentElement.classList.contains('night')===(t==='night'),th);
   // メニュー
   const mb=await p.$('#umenu');if(mb){await p.evaluate(()=>document.getElementById('umenu').click());await p.waitForTimeout(500);
     R.menu=await p.evaluate(()=>{const u=document.getElementById('upan');return !!(u&&u.classList.contains('on'))});
     R.menuItems=await p.evaluate(()=>[...document.querySelectorAll('#upan a.ui')].map(a=>a.getAttribute('href')));
     await p.evaluate(()=>{const x=document.querySelector('#upan .ux');x&&x.click()});await p.waitForTimeout(400);
     R.menuClose=await p.evaluate(()=>!document.getElementById('upan').classList.contains('on'));}
   else R.menu='なし';
   // 太陽と月のマーク
   const tb=await p.$('#utheme');if(tb){const a=await p.evaluate(()=>document.documentElement.classList.contains('night'));await p.evaluate(()=>document.getElementById('utheme').click());await p.waitForTimeout(400);
     const z=await p.evaluate(()=>document.documentElement.classList.contains('night'));R.toggle=a!==z;await p.evaluate(()=>document.getElementById('utheme').click());await p.waitForTimeout(300);}
   if(th==='day'){
    // ボタンを全部押す（メニュー・地図の中・送信ボタン以外）。押したあと中身が空にならないか
    const cnt=await p.evaluate(()=>{const v=e=>!!(e.offsetParent||e.getClientRects().length);window.__B=[...document.querySelectorAll('main button,.wrap button,body > button,[role=tab],.flt button,#flt button,.tabs button,#cats button')].filter(e=>v(e)&&!e.closest('#upan,.tn,form,#umap-s')&&e.id!=='umenu'&&e.id!=='utheme');return window.__B.length});
    R.buttons=cnt;const empty=[];
    for(let i=0;i<Math.min(cnt,40);i++){const t=await p.evaluate(i=>{const e=window.__B[i];if(!e||!(e.offsetParent||e.getClientRects().length))return null;e.scrollIntoView({block:'center'});e.click();return (e.textContent||'').trim().slice(0,12)},i);
      if(t===null)continue;await p.waitForTimeout(250);
      if(p.url().replace(/[?#].*/,'')!==(s.base+path).replace(/[?#].*/,'')){await p.goBack().catch(()=>{});await p.waitForTimeout(800);await p.evaluate(()=>{const v=e=>!!(e.offsetParent||e.getClientRects().length);window.__B=[...document.querySelectorAll('main button,.wrap button,body > button,[role=tab],.flt button,#flt button,.tabs button,#cats button')].filter(e=>v(e)&&!e.closest('#upan,.tn,form,#umap-s')&&e.id!=='umenu'&&e.id!=='utheme')});continue;}
      const vis=await p.evaluate(()=>[...document.querySelectorAll('a.card,.card,.it,li.k,.kc,.row')].filter(e=>e.offsetParent).length);
      if(vis===0)empty.push(t);}
    if(empty.length)R.emptyAfter=empty;
    await p.goto(s.base+path,{waitUntil:'load'});await p.waitForTimeout(1200);
    // 中のリンク
    const hrefs=await p.evaluate(()=>[...new Set([...document.querySelectorAll('a[href^="/"]')].map(a=>a.getAttribute('href').replace(/#.*/,'')).filter(h=>h&&!/^\/c(\?|$)/.test(h)))]);
    const bl=await checkLinks(s.base,hrefs);if(bl.length)R.badLinks=bl;
   }
   // 地図
   const hasMap=await p.evaluate(()=>!!document.querySelector('.tn'));
   if(hasMap){let open=await p.evaluate(()=>document.querySelector('.tn').classList.contains('fs'));
     if(!open){const bb=await p.evaluate(()=>{const e=document.querySelector('.tnbtn')||[...document.querySelectorAll('button,a')].find(x=>/地図で見る/.test(x.textContent)&&x.offsetParent&&!x.closest('#upan'));if(!e)return null;e.scrollIntoView({block:'center'});const q=e.getBoundingClientRect();return [q.x+q.width/2,q.y+q.height/2]});
       if(bb){await p.waitForTimeout(300);await p.touchscreen.tap(bb[0],bb[1]);await p.waitForTimeout(1800);}
       open=await p.evaluate(()=>document.querySelector('.tn').classList.contains('fs'));}
     R.mapOpen=open;
     if(open){const vb=()=>p.evaluate(()=>{const e=document.querySelector('.tn.fs svg');return e&&e.getAttribute('viewBox')});const v0=await vb();
       const pf=await p.evaluate(()=>{let best=null,a=0;for(const e of document.querySelectorAll('.tn.fs svg .pf[data-p]:not(.off)')){const q=e.getBoundingClientRect();if(q.width*q.height>a){a=q.width*q.height;best=[q.x+q.width/2,q.y+q.height/2]}}return best});
       if(pf){await p.touchscreen.tap(pf[0],pf[1]);await p.waitForTimeout(1500);}R.mapZoom=v0!==await vb();
       const gm=await p.evaluate(()=>{const e=[...document.querySelectorAll('.tn.fs a[href*="google.com/maps"]')].find(x=>x.offsetParent);if(!e)return null;const q=e.getBoundingClientRect();return [q.x+q.width/2,q.y+q.height/2]});
       if(gm){await p.touchscreen.tap(gm[0],gm[1]);await p.waitForTimeout(800);R.mapLinkSheet=!!(await p.$('#umap-s'));}
       await p.screenshot({path:`${OUT}/all/${s.nm}${path.replace(/\//g,'_')}-map-${th}.jpg`,type:'jpeg',quality:55});}}
   // ページの地図リンク（Google/Apple）
   if(th==='day'&&!hasMap){const gm=await p.evaluate(()=>{const e=[...document.querySelectorAll('a[href*="google.com/maps"]')].find(x=>x.offsetParent&&!x.closest('.tn'));if(!e)return null;e.scrollIntoView({block:'center'});const q=e.getBoundingClientRect();return [q.x+q.width/2,q.y+q.height/2]});
     if(gm){await p.waitForTimeout(300);await p.touchscreen.tap(gm[0],gm[1]);await p.waitForTimeout(800);R.linkSheet=!!(await p.$('#umap-s'));}}
   // リクエスト・感想：送る（隠し欄に字を入れて、保存されない形）
   if(/^\/koe/.test(path)&&th==='day'){await p.goto(s.base+path,{waitUntil:'load'});await p.waitForTimeout(1000);
     const ok=await p.evaluate(async()=>{const f=document.querySelector('form');if(!f)return 'no form';const r=f.querySelector('input[type=radio]');r&&r.click();const t=f.querySelector('textarea');t.value='動作の点検です（保存されません）';t.dispatchEvent(new Event('input',{bubbles:true}));
       const hp=f.querySelector('[name=hp],input.hp,#hp');if(hp)hp.value='x';else return 'no hp';const bt=f.querySelector('button[type=submit],button:not([type])');bt.click();await new Promise(r=>setTimeout(r,2500));
       const th=[...document.querySelectorAll('.thanks,#thanks,.done,[data-done]')].find(e=>e.offsetParent);return th?'送れた':'返事なし: '+document.body.innerText.match(/(送れ[^\n]{0,20}|ありがとう[^\n]{0,20})/)?.[0]});R.koe=ok;}
  }catch(e){errs.push('TEST '+e.message.split('\n')[0].slice(0,120));}
  const fail=errs.length||bad.length||R.theme===false||R.menu===false||R.menuClose===false||R.toggle===false||R.emptyAfter||R.badLinks||R.mapOpen===false||R.mapZoom===false||R.mapLinkSheet===false||R.linkSheet===false||(R.koe&&R.koe!=='送れた');
  if(fail){ng++;await p.screenshot({path:`${OUT}/all/NG-${s.nm}${path.replace(/\//g,'_')}-${th}.jpg`,type:'jpeg',quality:55}).catch(()=>{});}
  delete R.menuItems;L(`${fail?'NG':'OK'} ${tag} ${JSON.stringify(R)}${errs.length?' ERR '+errs.join(' | '):''}${bad.length?' 404 '+[...new Set(bad)].join(' '):''}`);
  await c.close();}}
L(`見た ${n}／NG ${ng}`);fs.writeFileSync(OUT+'/all.txt',log.join('\n'));await b.close();})();
