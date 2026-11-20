// 11/20 owner「他社より確実に上・全ページ全項目」：他社のページを iPhone の幅で上から下まで撮る（403 の時は web.archive.org）
// node tools/review/full.js <一覧（名前<TAB>URL）> <出力>
const {chromium,devices}=require('playwright');const fs=require('fs');
(async()=>{const [list,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const L=fs.readFileSync(list,'utf8').split('\n').map(s=>s.trim()).filter(s=>s&&!s.startsWith('#')).map(s=>s.split('\t'));
const b=await chromium.launch();const log=[];
for(const [n,u0] of L){let ok=false;
 for(const u of [u0,'https://web.archive.org/web/2026/'+u0]){
  const c=await b.newContext({...devices['iPhone 13'],locale:'ja-JP',deviceScaleFactor:1});const p=await c.newPage();
  try{const r=await p.goto(u,{waitUntil:'domcontentloaded',timeout:45000});if(!r||r.status()>=400)throw new Error('status '+(r&&r.status()));
   await p.waitForTimeout(4000);
   for(let y=0;y<8000;y+=700){await p.evaluate(v=>scrollTo(0,v),y);await p.waitForTimeout(250)}await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(800);
   const H=await p.evaluate(()=>document.documentElement.scrollHeight);
   await p.screenshot({path:`${out}/${n}.jpg`,type:'jpeg',quality:70,fullPage:true,clip:{x:0,y:0,width:390,height:Math.min(H,7000)}});
   log.push(n+'\t'+u+'\tok\t'+H);ok=true}catch(e){log.push(n+'\t'+u+'\t'+e.message.slice(0,80))}
  await c.close();if(ok)break}}
fs.writeFileSync(out+'/log.txt',log.join('\n'));await b.close()})();
