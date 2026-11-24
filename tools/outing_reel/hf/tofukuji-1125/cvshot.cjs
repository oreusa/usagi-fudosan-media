// 表紙：ehon.py の html の表紙をそのまま撮る（金の絵は ehon.py が中身から選ぶ）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const fo=document.querySelector('.face.cover #foil');if(fo)fo.style.display='none'});
await p.locator('.face.cover').first().screenshot({path:process.argv[3]});await b.close()})();
