// 投稿に付ける画像を作る（11/11 オーナー「投稿にHPの一部を載せる。今ずっと文字だけ」）。
// HPの画面（まちランキングの回・市ごとの解体補助・費用の目安・街の相場・季節のおでかけ）をスマホ幅で撮り、
// 縦4:横5（1080×1350）の1枚にして media/post/<名前>.jpg に置く。中身が変わった物だけ作り直す（media/post/index.json に控え）。
// 投稿の係は index.json の url を、そのページへ送る投稿の画像に付ける。
// 使い方：node tools/post_img/make.js [名前の先頭で絞る]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const http=require('http');const crypto=require('crypto');
const ROOT=path.join(__dirname,'..','..');const SITE=path.join(ROOT,'links');const OUT=path.join(ROOT,'media','post');
const BASE='https://oreusa.github.io/usagi-fudosan-media/media/post/';
const only=process.argv[2]||'';
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp','.webmanifest':'application/json'};
const srv=http.createServer((q,s)=>{let u=decodeURIComponent(q.url.split('?')[0]);if(u.endsWith('/'))u+='index.html';let f=path.join(SITE,u);
 if(!fs.existsSync(f)||fs.statSync(f).isDirectory()){if(fs.existsSync(f+'.html'))f+='.html';else if(fs.existsSync(path.join(f,'index.html')))f=path.join(f,'index.html');else{s.writeHead(404);return s.end()}}
 s.writeHead(200,{'content-type':MIME[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(s)});
// 撮る物の一覧：name・page（HPの道）・sel（撮る所）・label（上の小さい見出し）
function targets(){const T=[];const rk=fs.readFileSync(path.join(SITE,'ranking.html'),'utf8');
 for(const m of rk.matchAll(/<details class="rk" id="(r\d+)"/g))T.push({name:'rank-'+m[1],page:'/ranking',hash:'#'+m[1],sel:'#'+m[1],open:true,label:'関西まちランキング'});
 T.push({name:'kaitai-hiyo',page:'/kaitai',hash:'#kaitai',sel:'#kaitai',label:'解体の費用の目安'},{name:'kaitai-katazuke',page:'/kaitai',hash:'#katazuke',sel:'#katazuke',label:'片付けの費用の目安'},{name:'kaitai-hojo',page:'/kaitai',hash:'#hojo',sel:'#hojo',label:'解体の補助がある市'});
 for(const f of fs.readdirSync(SITE))if(/^kaitai-.+\.html$/.test(f)){const c=f.slice(7,-5);T.push({name:'kaitai-'+c,page:'/kaitai-'+c,hash:'',sel:'#shi',label:'市の解体の補助'})}
 for(const f of fs.readdirSync(path.join(SITE,'machi')))if(f.endsWith('.html')&&f!=='index.html'){const c=f.slice(0,-5);T.push({name:'machi-'+c,page:'/machi/'+c,hash:'',sel:'main, body',top:true,label:'街の相場'})}
 for(const p of ['koyo','illumination','hatsumode'])if(fs.existsSync(path.join(SITE,p+'.html')))T.push({name:'odekake-'+p,page:'/'+p,hash:'',sel:'main, body',top:true,label:'関西おでかけリスト'});
 // 11/12 府県ごとのおでかけ（koyo-nara 等）と実家ノート（jikka/*・診断）も撮る。昼の投稿の2本目がここへ送るため
 for(const f of fs.readdirSync(SITE))if(/^(koyo|illumination|hatsumode)-[a-z]+\.html$/.test(f)){const c=f.slice(0,-5);T.push({name:'odekake-'+c,page:'/'+c,hash:'',sel:'main, body',top:true,label:'関西おでかけリスト'})}
 const JK=path.join(SITE,'jikka');if(fs.existsSync(JK)){for(const f of fs.readdirSync(JK))if(f.endsWith('.html')&&f!=='index.html'){const c=f.slice(0,-5);T.push({name:'jikka-'+c,page:'/jikka/'+c,hash:'',sel:'main, body',top:true,label:'実家・空き家ノート'})}
  if(fs.existsSync(path.join(JK,'shindan','index.html')))T.push({name:'jikka-shindan',page:'/jikka/shindan/',hash:'',sel:'main, body',top:true,label:'実家・空き家ノート'})}
 return T.filter(t=>t.name.startsWith(only))}
const CARD=(img,label,page)=>`<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500&family=Shippori+Mincho:wght@600&family=Zen+Kaku+Gothic+New:wght@500&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;background:#F6F3EE;position:relative;overflow:hidden;font-family:"Zen Kaku Gothic New",sans-serif;color:#3A332E}
.fr{position:absolute;inset:26px;border:1px solid #CDBFAF}
.hd{position:absolute;left:70px;right:70px;top:62px;display:flex;justify-content:space-between;align-items:baseline}
.hd b{font:600 40px "Shippori Mincho",serif;letter-spacing:.08em}.hd i{font:500 22px Jost,sans-serif;letter-spacing:.3em;color:#B08A6E;font-style:normal}
.ph{position:absolute;left:150px;top:150px;width:780px;height:1070px;border-radius:38px;overflow:hidden;background:#fff;box-shadow:0 24px 60px rgba(90,70,50,.18),0 0 0 1px #E4DACD}
.ph img{width:780px;display:block}.ph:after{content:"";position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(rgba(255,255,255,0),#fff)}
.ft{position:absolute;left:0;right:0;bottom:58px;text-align:center;font-size:26px;letter-spacing:.12em;color:#6B5F55}</style>
<div class="fr"></div><div class="hd"><b>${label}</b><i>TOWN NOTE</i></div><div class="ph"><img src="${img}"></div><div class="ft">つづきは townnote.pages.dev${page}</div>`;
(async()=>{fs.mkdirSync(OUT,{recursive:true});const idxf=path.join(OUT,'index.json');let idx={};try{idx=JSON.parse(fs.readFileSync(idxf,'utf8')).items||{}}catch(e){}
 await new Promise(r=>srv.listen(0,r));const port=srv.address().port;const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,timezoneId:'Asia/Tokyo',colorScheme:'light'});const p=await ctx.newPage();await p.clock.setFixedTime(new Date('2026-11-11T03:00:00Z')); // 昼の見た目で撮る（夜は night.js が色を変える）
 const c=await b.newPage({viewport:{width:1080,height:1350}});
 await p.route('**/*',r=>{const u=r.request().url();(u.startsWith('http://127.0.0.1')||u.includes('fonts.g'))?r.continue():r.abort()}); // 数える合図・外の絵は呼ばない
 let made=0,kept=0,fail=[];const T=targets();const today=new Date(Date.now()+9*3600e3).toISOString().slice(0,10);
 for(const t of T){try{await p.goto(`http://127.0.0.1:${port}${t.page}`,{waitUntil:'load'});await p.waitForTimeout(250);
   const el=await p.$(t.sel.split(',')[0].trim())||await p.$('body');
   const h=crypto.createHash('sha1').update(await el.evaluate(e=>e.innerText)).digest('hex').slice(0,12);
   if(!process.env.FORCE&&idx[t.name]&&idx[t.name].hash===h&&fs.existsSync(path.join(OUT,t.name+'.jpg'))){kept++;continue}
   if(t.open)await el.evaluate(e=>{e.open=true});
   await p.evaluate(()=>{for(const e of document.querySelectorAll('*')){const s=getComputedStyle(e);if((s.position==='fixed'||s.position==='sticky')&&e.tagName!=='BODY')e.style.display='none'}});
   await p.addStyleTag({content:'*{opacity:1!important;transition:none!important;animation:none!important}.tk-v{transform:none!important}'}); // 画面に入ると出る動きを止めて、最初から見える形で撮る
   await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
   let box=t.top?{x:0,y:0,width:390,height:560}:await el.boundingBox();box={x:0,y:Math.max(0,box.y-8),width:390,height:Math.min(box.height+16,560)};
   const shot=await p.screenshot({clip:box,fullPage:true,type:'png'});
   if(process.env.DBG)fs.writeFileSync('/tmp/shot-'+t.name+'.png',shot);
   await c.setContent(CARD('data:image/png;base64,'+shot.toString('base64'),t.label,t.page+t.hash),{waitUntil:'networkidle'});await c.evaluate(()=>document.fonts.ready);
   await c.screenshot({path:path.join(OUT,t.name+'.jpg'),type:'jpeg',quality:86});
   idx[t.name]={hash:h,page:t.page+t.hash,label:t.label,url:BASE+t.name+'.jpg?v='+h,made:today};made++}catch(e){fail.push(t.name+' '+String(e).slice(0,80))}}
 for(const k of Object.keys(idx))if(!only&&!T.find(t=>t.name===k)){delete idx[k];try{fs.unlinkSync(path.join(OUT,k+'.jpg'))}catch(e){}}
 fs.writeFileSync(idxf,JSON.stringify({about:'投稿に付ける画像。投稿の2本目で送るページ（page）と同じ行の url を、1本目の画像に付ける。tools/post_img/make.js が毎朝作る',updated:today,items:idx},null,1));
 console.log(`作った ${made}・そのまま ${kept}・失敗 ${fail.length}`);fail.forEach(f=>console.log(' ×',f));await b.close();srv.close()})();
