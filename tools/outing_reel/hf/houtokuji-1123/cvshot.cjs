// 表紙：ehon.py の html の表紙を撮る。金の絵だけ、この日の中身（床もみじ）に替える（場所・大きさ・金の線は今まで通り）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const f=document.querySelector('.face.cover');const e=[...f.querySelectorAll('svg #emb')].pop()||[...f.querySelectorAll('svg')].pop();
 // 金の勝ちダルマ（顔は抜き・眉とひげ・「勝」）
 // 金の床もみじ：もみじ1枚と、床の線と、床にうつる薄いもみじ
 let g='<g transform="translate(250,1080)" fill="#e3c88c">';
 g+='<g transform="translate(0,-20) scale(3)"><path d="M0,-22 C2,-15 3,-12 5,-10 L13,-16 C12,-10 11,-6 10,-3 L21,-3 C17,0 14,3 11,5 L15,12 C10,11 6,10 3,9 L1,16 L-1,16 L-3,9 C-6,10 -10,11 -15,12 L-11,5 C-14,3 -17,0 -21,-3 L-10,-3 C-11,-6 -12,-10 -13,-16 L-5,-10 C-3,-12 -2,-15 0,-22Z"/><path d="M0,8 L0,24" stroke="#e3c88c" stroke-width="1.4" fill="none"/></g>';
 g+='<rect x="-90" y="54" width="180" height="4"/>';
 g+='<g transform="translate(0,128) scale(3,-3)" opacity=".38"><path d="M0,-22 C2,-15 3,-12 5,-10 L13,-16 C12,-10 11,-6 10,-3 L21,-3 C17,0 14,3 11,5 L15,12 C10,11 6,10 3,9 L1,16 L-1,16 L-3,9 C-6,10 -10,11 -15,12 L-11,5 C-14,3 -17,0 -21,-3 L-10,-3 C-11,-6 -12,-10 -13,-16 L-5,-10 C-3,-12 -2,-15 0,-22Z"/></g></g>';
 e.innerHTML=g;const fo=f.querySelector('#foil');if(fo)fo.style.display='none'});
const f=p.locator('.face.cover').first();console.log(await f.boundingBox());await f.screenshot({path:process.argv[3]});await b.close()})();
