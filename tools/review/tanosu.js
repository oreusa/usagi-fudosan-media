// 11/19 owner「tanosu はなんで使いやすいか全部解析して」: 相手のページを iPhone の幅で撮り、形・字・色・押せる所を数字で出す
const {chromium,devices}=require('playwright');const fs=require('fs');
const OUT=process.argv[2]||'/tmp/tn';fs.mkdirSync(OUT,{recursive:true});
const PAGES=[['cafe','https://tanosu.com/cafe/'],['top','https://tanosu.com/'],['gourmet','https://tanosu.com/gourmet/']];
(async()=>{const b=await chromium.launch();
for(const [n,u0] of PAGES){
 for(const u of [u0,'https://web.archive.org/web/2026/'+u0]){
  const c=await b.newContext({...devices['iPhone 13'],locale:'ja-JP'});const p=await c.newPage();
  try{const r=await p.goto(u,{waitUntil:'networkidle',timeout:60000});if(!r||r.status()>=400)throw new Error('status '+(r&&r.status()))}catch(e){fs.appendFileSync(OUT+'/log.txt',n+' '+u+' '+e.message+'\n');await c.close();continue}
  await p.waitForTimeout(3000);
  const H=await p.evaluate(()=>document.documentElement.scrollHeight);
  for(let i=0;i<16&&i*760<H;i++){await p.evaluate(y=>scrollTo(0,y),i*760);await p.waitForTimeout(800);await p.screenshot({path:`${OUT}/${n}-${String(i).padStart(2,'0')}.png`})}
  await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(500);
  const A=await p.evaluate(()=>{const R={url:location.href,H:document.documentElement.scrollHeight};
   const all=[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0});
   const cs=e=>getComputedStyle(e);
   R.fixed=all.filter(e=>['fixed','sticky'].includes(cs(e).position)).map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,cls:String(e.className).slice(0,60),top:r.top,h:r.height,w:r.width,bg:cs(e).backgroundColor,text:e.innerText.replace(/\s+/g,' ').slice(0,120)}}).slice(0,12);
   const txt=all.filter(e=>[...e.childNodes].some(t=>t.nodeType==3&&t.textContent.trim()));
   const hist=(f)=>{const m={};txt.forEach(e=>{const k=f(e);m[k]=(m[k]||0)+e.innerText.length});return Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,12)};
   R.fontSize=hist(e=>cs(e).fontSize);R.fontWeight=hist(e=>cs(e).fontWeight);R.color=hist(e=>cs(e).color);R.font=hist(e=>cs(e).fontFamily.slice(0,60));R.lineHeight=hist(e=>cs(e).lineHeight);
   const bm={};all.forEach(e=>{const c=cs(e).backgroundColor;if(c!=='rgba(0, 0, 0, 0)'){const r=e.getBoundingClientRect();bm[c]=(bm[c]||0)+r.width*r.height}});R.bg=Object.entries(bm).sort((a,b)=>b[1]-a[1]).slice(0,12).map(([k,v])=>[k,Math.round(v/1000)]);
   R.body={font:cs(document.body).fontFamily,size:cs(document.body).fontSize,color:cs(document.body).color,bg:cs(document.body).backgroundColor};
   const taps=all.filter(e=>e.matches('a,button,[role=button],input,select'));R.taps=taps.length;
   R.smallTaps=taps.filter(e=>e.getBoundingClientRect().height<32).length;
   R.links=taps.slice(0,150).map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.top+scrollY),Math.round(r.height),Math.round(r.width),(e.innerText||e.getAttribute('aria-label')||e.value||'').replace(/\s+/g,' ').slice(0,40),(e.getAttribute('href')||'').slice(0,60)]});
   const imgs=[...document.images].filter(i=>i.getBoundingClientRect().width>40);R.imgs=imgs.length;R.imgSizes=imgs.slice(0,30).map(i=>{const r=i.getBoundingClientRect();return [Math.round(r.top+scrollY),Math.round(r.width),Math.round(r.height),cs(i).borderRadius,cs(i).objectFit]});
   const cards={};all.forEach(e=>{const k=e.tagName+'.'+String(e.className).split(' ')[0];if(e.parentNode&&e.parentNode.children.length>=3&&k.length>3){cards[k]=(cards[k]||0)+1}});
   R.repeat=Object.entries(cards).filter(x=>x[1]>=4).sort((a,b)=>b[1]-a[1]).slice(0,15);
   const top=R.repeat.find(x=>/article|card|post|item|LI\./i.test(x[0]));if(top){const el=all.find(e=>(e.tagName+'.'+String(e.className).split(' ')[0])===top[0]);R.cardHTML=el.outerHTML.replace(/<svg[\s\S]*?<\/svg>/g,'<svg/>').replace(/\s(srcset|sizes|style)="[^"]*"/g,'').slice(0,3000);const r=el.getBoundingClientRect();R.cardBox=[r.width,r.height,cs(el).borderRadius,cs(el).boxShadow,cs(el).backgroundColor,cs(el).padding]}
   R.headings=[...document.querySelectorAll('h1,h2,h3')].slice(0,40).map(h=>h.tagName+' '+cs(h).fontSize+' '+cs(h).fontWeight+' '+h.innerText.replace(/\s+/g,' ').slice(0,50));
   R.text=document.body.innerText.replace(/\n+/g,' | ').slice(0,6000);return R});
  fs.writeFileSync(`${OUT}/${n}.json`,JSON.stringify(A,null,1));
  for(const sel of ['button[aria-label*="メニュー"]','.menu-btn','.hamburger','button.menu','[class*=menu] button','header button']){const el=await p.$(sel);if(el&&await el.isVisible()){await el.click().catch(()=>{});await p.waitForTimeout(1200);await p.screenshot({path:`${OUT}/${n}-menu.png`});break}}
  await c.close();break}
}
await b.close()})();
