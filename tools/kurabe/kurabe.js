// 関西と関東の HP を全ページ並べて見比べる（作業環境から本番に届かないので Actions で動かす）
// node tools/kurabe/kurabe.js <出力フォルダ>
// 両方の入口から内のリンクをたどり、1ページごとに 中身の量・カード・絵・エラー・下のバー・見出し・見た目の版 を report.json に。
// 1件ページ（/o/ /machi/ /jikka/ /kaiten/）は2つずつ。iPhone 幅の昼と夜の1画面目を jpg で残す。
const {chromium}=require('playwright');const fs=require('fs');
const SITES=process.env.KB_K?{k:process.env.KB_K,t:process.env.KB_T}:{k:'https://kansai.townnote.app',t:'https://kanto.townnote.app'};
const SKIP=/^\/(o|machi|jikka|kaiten|townnotes|card|promo|kyu|stats|c|wx|api|shin|assets)\/./;
(async()=>{const out=process.argv[2];fs.mkdirSync(out,{recursive:true});const b=await chromium.launch();const rep=[];
for(const [r,base] of Object.entries(SITES)){
 const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
 await ctx.addInitScript(()=>{try{localStorage.setItem('usagi_owner','1')}catch(e){}});
 const seen=new Set(),q=['/'],samp={};let n=0;
 const visit=async(u,deep)=>{const p=await ctx.newPage();const er=[],bad=[];p.on('pageerror',e=>er.push(String(e.message).slice(0,120)));p.on('response',x=>{if(x.status()>=400&&x.url().startsWith(base))bad.push(x.status()+' '+x.url().replace(base,'').slice(0,90))});
  let st=0;try{const x=await p.goto(base+u,{waitUntil:'load',timeout:40000});st=x?x.status():0;await p.waitForTimeout(1800)}catch(e){er.push('goto '+String(e.message).slice(0,60))}
  let m={};try{m=await p.evaluate(()=>{const H=document.documentElement,vis=e=>!!e.offsetParent;const T=s=>(s||'').trim().replace(/\s+/g,' ');
   return {title:document.title.slice(0,70),cls:H.className,txt:document.body.innerText.length,screens:Math.round(H.scrollHeight/innerHeight*10)/10,over:H.scrollWidth-innerWidth,
    cards:document.querySelectorAll('.cd,.kc,.pc,.of,.rk li,#grid a,#grid .lr').length,imgs:[...document.querySelectorAll('img')].filter(vis).length,
    broken:[...document.querySelectorAll('img')].filter(i=>vis(i)&&i.complete&&!i.naturalWidth).length,
    look:((document.querySelector('link[href*="look.css"]')||{}).href||'').replace(/.*\?/,''),
    h:[...document.querySelectorAll('h1,h2,h3')].filter(vis).map(x=>T(x.textContent).slice(0,26)).slice(0,16),
    bar:[...document.querySelectorAll('#bar a,#bar button,.tnbar a,.tnbar button,#v2bar a,#v2bar button,.bb a,.bb button')].filter(vis).map(x=>T(x.textContent).slice(0,10)).slice(0,10),
    menu:[...document.querySelectorAll('.mn a,.mnsn a,.rel a,.sheet a,.mn button')].map(x=>T(x.textContent).slice(0,16)).filter(Boolean).slice(0,40),
    foot:[...document.querySelectorAll('footer a,.c3f a,.knft a,.ft a')].map(x=>T(x.textContent).slice(0,14)).slice(0,20),
    sdc:!!document.querySelector('.sdc'),links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))}})}catch(e){er.push('eval '+String(e.message).slice(0,60))}
  const name=r+'_'+(u.replace(/[^a-z0-9]+/gi,'_').replace(/^_|_$/g,'')||'top');
  if(deep){try{await p.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important}'});await p.screenshot({path:`${out}/${name}-d.jpg`,type:'jpeg',quality:50});
   await p.evaluate(()=>{try{localStorage.setItem('usagi_theme','night')}catch(e){}});await p.reload({waitUntil:'load'});await p.waitForTimeout(1500);await p.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important}'});await p.screenshot({path:`${out}/${name}-n.jpg`,type:'jpeg',quality:50});
   await p.evaluate(()=>{try{localStorage.removeItem('usagi_theme')}catch(e){}})}catch(e){}}
  const links=m.links||[];delete m.links;rep.push(Object.assign({r,u,st,er,bad:bad.slice(0,6)},m));console.log(r,u,st,er.length,bad.length);await p.close();return links};
 while(q.length&&n<170){const u=q.shift();if(seen.has(u))continue;seen.add(u);n++;
  const links=await visit(u,true);
  for(const h of links){if(!h||/^(https?:|mailto:|tel:|#|javascript|data:)/.test(h))continue;let x=h.split('#')[0].split('?')[0].replace(/\.html$/,'');if(!x.startsWith('/'))continue;if(x.length>1)x=x.replace(/\/$/,'');
   if(/\.(json|xml|png|jpg|webp|txt|svg|pdf|js|css)$/.test(x))continue;
   if(SKIP.test(x)){const k=x.split('/')[1];samp[k]=samp[k]||[];if(samp[k].length<2&&!samp[k].includes(x))samp[k].push(x);continue}
   if(/^\/kaitai-[a-z]+$/.test(x)&&!/ranking/.test(x)){samp.kaitai=samp.kaitai||[];if(samp.kaitai.length<2&&!samp.kaitai.includes(x))samp.kaitai.push(x);continue}
   if(!seen.has(x))q.push(x)}}
 for(const k in samp)for(const x of samp[k])if(!seen.has(x)){seen.add(x);await visit(x,true)}
 await ctx.close()}
fs.writeFileSync(`${out}/report.json`,JSON.stringify(rep,null,1));await b.close()})();
