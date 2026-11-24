const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage();
p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>console.log('[c]',m.text()));
await p.goto('file://'+__dirname+'/p.html');await p.evaluate(()=>document.fonts.load('700 40px "Shippori Mincho"'));
for(const s of process.argv.slice(2)){const t=Date.now();const r=await p.evaluate(s=>{const L=SCN[s]();const o={};const comp=cv(),cx=comp.getContext('2d');cx.fillStyle='#f4ecdc';cx.fillRect(0,0,W,H);
 for(const k in L){o[k]=L[k].toDataURL('image/png');cx.drawImage(L[k],0,0)}o._comp=comp.toDataURL('image/jpeg',.9);return o},s);
 for(const k in r){const ext=k=='_comp'?'jpg':'png';fs.writeFileSync(`../a/${s}${k=='_comp'?'':'-'+k}.${ext}`,Buffer.from(r[k].split(',')[1],'base64'))}console.log(s,Date.now()-t,'ms')}
await b.close()})();
