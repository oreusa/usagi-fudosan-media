// 表紙：ehon.py の html の表紙を撮る。金の絵だけ、この日の中身（床もみじ）に替える（場所・大きさ・金の線は今まで通り）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const f=document.querySelector('.face.cover');const e=[...f.querySelectorAll('svg #emb')].pop()||[...f.querySelectorAll('svg')].pop();
 // 金の勝ちダルマ（顔は抜き・眉とひげ・「勝」）
 // 金の床もみじ：もみじ1枚と、床の線と、床にうつる薄いもみじ
 let g='<g transform="translate(250,1010) scale(1.5)" fill="#e3c88c">';
 // 金のいちょう並木：とがった木が奥へ小さくなって並ぶ・道の線
 const tr=(x,y,k)=>`<path transform="translate(${x},${y}) scale(${k})" d="M0,-60 Q16,-30 22,0 Q0,8 -22,0 Q-16,-30 0,-60Z"/><rect transform="translate(${x},${y}) scale(${k})" x="-2" y="0" width="4" height="16"/>`;
 for(let i=0;i<4;i++){const k=1.9-i*.38;g+=tr(-120+i*38,20-i*26,k)+tr(120-i*38,20-i*26,k)}
 g+='<path d="M-60,60 L-6,-70 L6,-70 L60,60Z" opacity=".3"/>';
 
 g+='</g>';
 e.innerHTML=g;const fo=f.querySelector('#foil');if(fo)fo.style.display='none'});
const f=p.locator('.face.cover').first();console.log(await f.boundingBox());await f.screenshot({path:process.argv[3]});await b.close()})();
