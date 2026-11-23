// 表紙：ehon.py の html の表紙を撮る。金の絵だけ、この日の中身（床もみじ）に替える（場所・大きさ・金の線は今まで通り）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const f=document.querySelector('.face.cover');const e=[...f.querySelectorAll('svg #emb')].pop()||[...f.querySelectorAll('svg')].pop();
 // 金の勝ちダルマ（顔は抜き・眉とひげ・「勝」）
 // 金の床もみじ：もみじ1枚と、床の線と、床にうつる薄いもみじ
 let g='<g transform="translate(250,1010) scale(1.5)" fill="#e3c88c">';
 // 金の光の並木：光の粒でできた木と、道の線と、道にうつる光
 let sd=7;const R=()=>{sd=(sd*16807)%2147483647;return sd/2147483647};
 for(let i=0;i<150;i++){const u=R(),y=-30-u*110,rad=46*Math.sin(Math.PI*Math.min(1,u*1.05))*(.6+R()*.45);const x=(R()*2-1)*rad;g+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(1.6+R()*2).toFixed(1)}"/>`}
 g+='<rect x="-3" y="-40" width="6" height="94"/>';
 g+='<rect x="-90" y="54" width="180" height="4"/>';
 for(let i=0;i<40;i++){const x=(R()*2-1)*40,y=64+R()*60;g+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(1+R()*1.5).toFixed(1)}" opacity=".35"/>`}
 g+='</g>';
 e.innerHTML=g;const fo=f.querySelector('#foil');if(fo)fo.style.display='none'});
const f=p.locator('.face.cover').first();console.log(await f.boundingBox());await f.screenshot({path:process.argv[3]});await b.close()})();
