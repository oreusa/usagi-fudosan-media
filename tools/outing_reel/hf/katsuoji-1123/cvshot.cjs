// 表紙：ehon.py の html の表紙を撮る。金の絵だけ、この日の中身（勝ちダルマ）に替える（場所・大きさ・金の線は今まで通り）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const f=document.querySelector('.face.cover');const e=[...f.querySelectorAll('svg #emb')].pop()||[...f.querySelectorAll('svg')].pop();
 // 金の勝ちダルマ（顔は抜き・眉とひげ・「勝」）
 let g='<g transform="translate(250,1160) scale(.6)" fill="#e3c88c">';
 g+='<path fill-rule="evenodd" d="M0,-130 C70,-130 104,-80 104,-10 C104,62 64,96 0,96 C-64,96 -104,62 -104,-10 C-104,-80 -70,-130 0,-130Z M0,-104 C40,-104 60,-82 60,-56 C60,-28 38,-12 0,-12 C-38,-12 -60,-28 -60,-56 C-60,-82 -40,-104 0,-104Z"/>';
 g+='<path d="M-44,-84 Q-28,-96 -12,-84 Q-28,-90 -44,-84Z M44,-84 Q28,-96 12,-84 Q28,-90 44,-84Z"/>';
 g+='<circle cx="-24" cy="-64" r="11"/><circle cx="24" cy="-64" r="11"/><circle cx="-24" cy="-64" r="5" fill="#7c2a22"/><circle cx="24" cy="-64" r="5" fill="#7c2a22"/>';
 g+='<path d="M-30,-36 Q-14,-26 0,-36 Q14,-26 30,-36 Q14,-18 0,-28 Q-14,-18 -30,-36Z"/>';
 g+='<text x="0" y="62" text-anchor="middle" font-size="74" font-family="MB,serif" fill="#7c2a22">勝</text>';
 g+='<path d="M-70,90 Q0,112 70,90 L64,104 Q0,122 -64,104Z"/></g>';
 e.innerHTML=g;const fo=f.querySelector('#foil');if(fo)fo.style.display='none'});
const f=p.locator('.face.cover').first();console.log(await f.boundingBox());await f.screenshot({path:process.argv[3]});await b.close()})();
