// 公開中のページをスマホの幅で撮る（作業環境から pages.dev に届かないため Actions で撮る）
// node tools/shot_page.js <URL> <出力フォルダ> ["#cats button" のようなタブのセレクタ]
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [url,out,tabs]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
await p.goto(url,{waitUntil:'networkidle'});await p.waitForTimeout(1500);
await p.screenshot({path:`${out}/0.png`,fullPage:true});
const log=[];
if(tabs){const n=(await p.$$(tabs)).length;
 for(let i=0;i<n;i++){const el=(await p.$$(tabs))[i];const t=(await el.textContent()).trim();await el.click();await p.waitForTimeout(1500);
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,150))}scrollTo(0,0)});
  await p.waitForTimeout(800);
  const imgs=await p.evaluate(()=>[...document.querySelectorAll('img.ph')].filter(i=>i.offsetParent).map(i=>i.naturalWidth>0?'ok':'broken'));
  log.push(`${i} ${t} imgs=${imgs.length} broken=${imgs.filter(x=>x=='broken').length}`);
  await p.screenshot({path:`${out}/tab${i}.png`,fullPage:true});}}
fs.writeFileSync(`${out}/log.txt`,log.join('\n')+'\n');console.log(log.join('\n'));await b.close()})();
