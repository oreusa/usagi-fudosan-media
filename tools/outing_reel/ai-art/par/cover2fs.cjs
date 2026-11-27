// 表紙（画面いっぱい 1080x1920 版）。cover2.html を同じ作りのまま全画面に。node cover2fs.cjs '<query>' out.png
const {chromium}=require('playwright');(async()=>{const [q,out]=process.argv.slice(2);const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+__dirname+'/cover2.html?'+q);await p.waitForFunction('window.ready');
await p.addStyleTag({content:`html,body{width:1080px!important;height:1920px!important}#c{border-radius:0}
#fr{inset:150px 56px 150px 72px}#top{left:72px;right:56px;top:250px;font-size:28px}#dt{left:72px;right:56px;top:298px;font-size:30px}
#tt{left:72px;right:56px;bottom:640px;font-size:136px}#st{left:72px;right:56px;bottom:568px;font-size:44px}#ln{bottom:532px}
#lg{bottom:440px;width:50px;height:50px}#br{left:72px;right:56px;bottom:392px;font-size:26px}#sp{width:40px}`});
await p.waitForTimeout(400);await p.screenshot({path:out});await b.close()})();
