// 表紙 v3（A 和の装丁・B 雑誌・C 布張り箔押し）。node cover2.cjs '<query>' out.png
const {chromium}=require('playwright');(async()=>{const [q,out]=process.argv.slice(2);const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:925,height:1425}});
await p.goto('file://'+__dirname+'/cover3.html?'+q);await p.waitForFunction('window.ready');await p.waitForTimeout(300);await p.screenshot({path:out});await b.close()})();
