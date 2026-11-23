// 表紙：ehon.py の html の表紙を撮る。金の絵だけ、この日の中身（床もみじ）に替える（場所・大きさ・金の線は今まで通り）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const f=document.querySelector('.face.cover');const e=[...f.querySelectorAll('svg #emb')].pop()||[...f.querySelectorAll('svg')].pop();
 // 金の勝ちダルマ（顔は抜き・眉とひげ・「勝」）
 // 金の床もみじ：もみじ1枚と、床の線と、床にうつる薄いもみじ
 let g='<g transform="translate(250,1010) scale(1.5)" fill="#e3c88c">';
 // 金の神護寺：大きなもみじ1枚と、下へ続く石段の線
 g+='<path transform="translate(0,-14) scale(1.7)" d="M0,-22 L3,-11 L7,-15 L6,-7 L16,-13 L11,-3 L21,-2 L11,3 L15,11 L5,7 L2,14 L0,10 L-2,14 L-5,7 L-15,11 L-11,3 L-21,-2 L-11,-3 L-16,-13 L-6,-7 L-7,-15 L-3,-11Z"/>';
 g+='<rect x="-1.2" y="10" width="2.4" height="24" />';
 for(let i=0;i<6;i++){const w=40+i*24,y=40+i*14;g+=`<rect x="${-w/2}" y="${y}" width="${w}" height="3" opacity="${1-i*.12}"/>`}
 g+='</g>';
 e.innerHTML=g;const fo=f.querySelector('#foil');if(fo)fo.style.display='none'});
const f=p.locator('.face.cover').first();console.log(await f.boundingBox());await f.screenshot({path:process.argv[3]});await b.close()})();
