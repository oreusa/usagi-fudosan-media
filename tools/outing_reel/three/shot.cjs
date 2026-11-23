const {chromium}=require('playwright');const fs=require('fs');const http=require('http');const path=require('path');
const [,,qs,out,t0,t1,fps]=process.argv;
const srv=http.createServer((q,s)=>{const p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));fs.readFile(p,(e,d)=>{if(e){s.writeHead(404);return s.end()}s.writeHead(200,{'Content-Type':p.endsWith('.js')?'text/javascript':p.endsWith('.html')?'text/html':'application/octet-stream'});s.end(d)})}).listen(0,async()=>{
const port=srv.address().port;const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const pg=await b.newPage({viewport:{width:1080,height:1920}});pg.on('console',m=>console.log('C',m.text()));pg.on('pageerror',e=>console.log('E',e.message));
await pg.goto(`http://127.0.0.1:${port}/${process.env.SCN||"scene.html"}?${qs}`);await pg.waitForFunction('window.ready',null,{timeout:120000});
fs.mkdirSync(out,{recursive:true});const F=+(fps||30);const a=+t0,z=+t1;let i=0;const st=Date.now();
for(let t=a;t<=z+1e-6;t+=1/F){await pg.evaluate(t=>window.renderAt(t),t);const u=await pg.evaluate(()=>document.querySelector('canvas').toDataURL('image/jpeg',.93));fs.writeFileSync(`${out}/f${String(i++).padStart(4,'0')}.jpg`,Buffer.from(u.split(',')[1],'base64'));}
console.log('frames',i,'sec',(Date.now()-st)/1000);await b.close();srv.close()});
