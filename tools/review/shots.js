// 11/18 HP全体の見回り：公開中のページを スマホ幅・昼と夜 で撮り、壊れた画像・JSのエラー・横にはみ出しを数える
// node tools/review/shots.js <URLの一覧ファイル> <出力フォルダ>   （一覧は1行1URL。「名前<TAB>URL」でもよい）
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [list,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const L=fs.readFileSync(list,'utf8').split('\n').map(s=>s.trim()).filter(Boolean).map((s,i)=>{const a=s.split('\t');return a.length>1?[a[0],a[1]]:[String(i).padStart(2,'0'),a[0]]});
const b=await chromium.launch();const log=[];
for(const [name,url] of L){for(const night of [false,true]){
 const c=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
 if(night)await c.addInitScript(()=>{try{localStorage.setItem('usagi_theme','night')}catch(e){}});
 await c.addInitScript(()=>{try{localStorage.setItem('usagi_owner','1')}catch(e){}});
 const p=await c.newPage();const err=[];p.on('pageerror',e=>err.push(String(e).slice(0,160)));
 p.on('response',r=>{if(r.status()>=400&&!/google|gstatic|doubleclick|instagram/.test(r.url()))err.push(r.status()+' '+r.url().slice(0,140))});
 try{await p.goto(url,{waitUntil:'networkidle',timeout:45000})}catch(e){err.push('goto '+e)}
 await p.waitForTimeout(1500);
 await p.evaluate(async()=>{for(let y=0;y<Math.min(document.body.scrollHeight,9000);y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,120))}scrollTo(0,0)});
 await p.waitForTimeout(1200);
 const st=await p.evaluate(()=>({h:document.body.scrollHeight,over:document.documentElement.scrollWidth>innerWidth+1,
   broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&i.src&&!/instagram/.test(i.src)).map(i=>i.src.slice(-60)),
   imgs:[...document.images].filter(i=>i.naturalWidth>0).length,empty:[...document.querySelectorAll('b,strong,span')].filter(e=>/^\s*0\s*件?$/.test(e.textContent)&&e.offsetParent).length}));
 const tag=`${name}-${night?'n':'d'}`;
 await p.screenshot({path:`${out}/${tag}.png`,fullPage:true,clip:{x:0,y:0,width:390,height:Math.min(st.h,6000)}}).catch(async()=>{await p.screenshot({path:`${out}/${tag}.png`})});
 log.push([tag,url,'h='+st.h,'imgs='+st.imgs,'broken='+st.broken.length,'over='+st.over,'zero='+st.empty,'err='+err.length,st.broken.join(' '),err.join(' | ')].join('\t'));
 await c.close();}}
fs.writeFileSync(`${out}/log.tsv`,log.join('\n')+'\n');console.log(log.join('\n'));await b.close()})();
