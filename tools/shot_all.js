// 公開中の全種類のページを1回でまとめて見る（作業環境から pages.dev に届かないため Actions で動かす）
// node tools/shot_all.js <出力フォルダ> [tech=2 を付けるなら "2"]
// 1ページごとに：上から下までの写真（jpg）・画面の枚数・横はみ出し・エラー・こわれた絵・見えない物・リンクの数を report.json に残す
const {chromium}=require('playwright');const fs=require('fs');
const T='https://townnote.pages.dev',L='https://lifenote-kanto.pages.dev';
const PAGES=[
 ['t-top',T+'/'],['t-odekake',T+'/odekake'],['t-ima',T+'/ima'],['t-illumi',T+'/illumination'],['t-koyo',T+'/koyo'],['t-tomari',T+'/tomari'],['t-hatsumode',T+'/hatsumode'],['t-odekake-osaka',T+'/odekake-osaka'],
 ['t-fudosan',T+'/fudosan-list'],['t-uru',T+'/uru'],['t-sagasu',T+'/sagasu'],['t-chika',T+'/chika-kansai'],['t-machi',T+'/machi/osaka-01'],['t-gyosha',T+'/gyosha'],['t-moushikomi',T+'/moushikomi'],
 ['t-kaitai',T+'/kaitai'],['t-kaitai-rank',T+'/kaitai-ranking'],['t-kaitai-city',T+'/kaitai-neyagawa'],['t-ranking',T+'/ranking'],
 ['t-jikka',T+'/jikka/'],['t-jikka-town',T+'/jikka/osaka-01'],['t-shindan',T+'/jikka/shindan/?machi=osaka-42&w=A&d=1'],
 ['t-okaimono',T+'/okaimono'],['t-nesage',T+'/nesage'],['t-kaimawari',T+'/kaimawari'],['t-furusato',T+'/furusato'],['t-otoku',T+'/otoku'],['t-koe',T+'/koe'],['t-privacy',T+'/privacy'],
 ['l-top',L+'/'],['l-odekake',L+'/odekake'],['l-ima',L+'/ima'],['l-illumi',L+'/illumination'],['l-koyo',L+'/koyo'],['l-tomari',L+'/tomari'],['l-odekake-tokyo',L+'/odekake-tokyo'],
 ['l-fudosan',L+'/fudosan-list'],['l-uru',L+'/uru'],['l-sagasu',L+'/sagasu'],['l-chika',L+'/chika-kanto'],['l-machi',L+'/machi/chiba-01'],['l-moushikomi',L+'/moushikomi'],
 ['l-kaitai',L+'/kaitai'],['l-kaitai-rank',L+'/kaitai-ranking'],['l-kaitai-city',L+'/kaitai-yokohama'],
 ['l-jikka',L+'/jikka/'],['l-jikka-town',L+'/jikka/chiba-01'],
 ['l-okaimono',L+'/okaimono'],['l-nesage',L+'/nesage'],['l-kaimawari',L+'/kaimawari'],['l-furusato',L+'/furusato'],['l-otoku',L+'/otoku'],['l-koe',L+'/koe'],['l-privacy',L+'/privacy']
];
(async()=>{const [out,tech]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const rep=[];
for(const [w,h,tag] of [[390,844,'sp'],[1280,800,'pc']]){
 const c=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1});
 if(tech)await c.addInitScript(t=>{try{localStorage.setItem('tn_tech',t);localStorage.setItem('usagi_owner','1')}catch(e){}},tech);
 else await c.addInitScript(()=>{try{localStorage.setItem('usagi_owner','1')}catch(e){}});
 for(const [n,u] of PAGES){
  if(tag==='pc'&&!/top|okaimono|odekake$|fudosan|shindan|nesage|furusato/.test(n))continue;
  const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e.message).slice(0,160)));
  const bad=[];p.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url().slice(0,120))});
  let st=0;try{const r=await p.goto(u,{waitUntil:'load',timeout:45000});st=r?r.status():0}catch(e){errs.push('goto '+String(e.message).slice(0,80))}
  await p.waitForTimeout(2500);
  // 下までゆっくり動かして、動きで出てくる物を出す
  let inv=[];try{
   const H=await p.evaluate(()=>document.documentElement.scrollHeight);
   for(let y=0;y<Math.min(H,16000);y+=700){await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(160);
    const r=await p.evaluate(()=>{const o=[];for(const e of document.querySelectorAll('main *,.wrap *')){if(!e.offsetParent)continue;const r=e.getBoundingClientRect();if(r.height<14||r.width<40||r.top<160||r.bottom>innerHeight-160)continue;const op=parseFloat(getComputedStyle(e).opacity);if(op<.5)o.push((e.className||e.tagName).toString().slice(0,30))}return o.slice(0,4)});inv=inv.concat(r)}
   await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(400);
  }catch(e){errs.push('scroll '+String(e.message).slice(0,80))}
  let m={};try{m=await p.evaluate(()=>({title:document.title.slice(0,60),screens:Math.round(document.documentElement.scrollHeight/innerHeight*10)/10,over:document.documentElement.scrollWidth-innerWidth,
   links:document.querySelectorAll('a[href]').length,ext:[...document.querySelectorAll('a[href^="http"]')].filter(a=>a.offsetParent&&a.host!==location.host).length,
   brokenImg:[...document.querySelectorAll('img')].filter(i=>i.offsetParent&&i.complete&&!i.naturalWidth).map(i=>i.src.slice(0,100)).slice(0,5),
   bar:[...document.querySelectorAll('#v2bar a,#v2bar button,.tnbar a,.tnbar button')].map(x=>x.textContent.trim().replace(/\s+/g,'')).slice(0,8),
   h:[...document.querySelectorAll('h1,h2')].filter(x=>x.offsetParent).map(x=>x.textContent.trim().replace(/\s+/g,' ').slice(0,24)).slice(0,14),
   small:[...document.querySelectorAll('a,button')].filter(e=>{if(!e.offsetParent)return false;const r=e.getBoundingClientRect();return r.width>0&&(r.height<28)&&e.textContent.trim().length>0}).length,
   empty:[...document.querySelectorAll('section,.sec,.box,ul,ol')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height>40&&!e.textContent.trim()&&!e.querySelector('img,svg,canvas,iframe,input')).length,
   more:[...document.querySelectorAll('.fx-more')].length,ms:(()=>{try{const t=performance.getEntriesByType('navigation')[0];return Math.round(t.loadEventEnd)}catch(e){return 0}})(),kb:(()=>{try{return Math.round(performance.getEntriesByType('resource').reduce((a,r)=>a+(r.transferSize||0),performance.getEntriesByType('navigation')[0].transferSize||0)/1024)}catch(e){return 0}})(),req:performance.getEntriesByType('resource').length,
   tiny:[...document.querySelectorAll('main *,.wrap *,body>*')].filter(e=>e.offsetParent&&e.childElementCount===0&&e.textContent.trim().length>3&&parseFloat(getComputedStyle(e).fontSize)<11).length,
   first:[...document.querySelectorAll('a[href],button')].filter(e=>{if(!e.offsetParent||e.closest('#v2bar,.tnbar,header,nav'))return false;const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&r.height>=36}).map(e=>e.textContent.trim().replace(/\s+/g,' ').slice(0,18)).slice(0,5),
   alt:[...document.querySelectorAll('img')].filter(i=>i.offsetParent&&!i.getAttribute('alt')).length,desc:(document.querySelector('meta[name=description]')||{}).content?1:0,tk:document.documentElement.className}))}catch(e){errs.push('eval '+String(e.message).slice(0,80))}
  // 全体写真では、スクロールで出てくる動きが「まだ出ていない」状態で写るので、撮る時だけ動きを止める（見えない物の点検は上で済んでいる）
  try{await p.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important}'});await p.waitForTimeout(150)}catch(e){}
  try{await p.screenshot({path:`${out}/${tag}-${n}.jpg`,type:'jpeg',quality:52,fullPage:true,clip:undefined})}catch(e){try{await p.screenshot({path:`${out}/${tag}-${n}.jpg`,type:'jpeg',quality:52})}catch(_){}}
  if(tag==='sp'){try{fs.writeFileSync(`${out}/${n}.html`,await p.content())}catch(e){}}
  rep.push(Object.assign({n,tag,u,st,errs,bad:bad.slice(0,6),inv:[...new Set(inv)].slice(0,6)},m));console.log(tag,n,st,m.screens,errs.length,bad.length);
  await p.close();}
 await c.close();}
fs.writeFileSync(`${out}/report.json`,JSON.stringify(rep,null,1));await b.close()})();
