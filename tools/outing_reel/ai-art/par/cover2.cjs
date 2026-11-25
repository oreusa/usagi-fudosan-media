// 表紙（その日の1枚目の絵＋金の枠＋明朝）。node cover2.cjs '<query>' out.png
const {chromium}=require('playwright');(async()=>{const [q,out]=process.argv.slice(2);const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:925,height:1425}});
await p.goto('file://'+__dirname+'/cover2.html?'+q);await p.waitForFunction('window.ready');await p.waitForTimeout(300);await p.screenshot({path:out});await b.close()})();
