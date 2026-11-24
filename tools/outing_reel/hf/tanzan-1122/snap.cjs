// 書き出す前に、決めた時刻で止めて撮る（点検用）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>console.log('ERR',e.message));console.log('go');await p.goto('file://'+__dirname+'/index.html',{waitUntil:'domcontentloaded',timeout:30000});console.log('loaded');console.log('A',await p.evaluate(()=>typeof window.__timelines+' '+document.readyState));await p.waitForTimeout(800);console.log('B');
for(const t of process.argv.slice(3)){await p.evaluate(t=>window.__timelines.main.seek(+t,false),t);await p.waitForTimeout(150);await p.screenshot({path:process.argv[2]+'/s-'+t+'.jpg',type:'jpeg',quality:80})}await b.close()})();
