// 表紙：ehon.py の html の表紙を撮る。金の絵だけ、この日の中身（十三重塔）に替える（場所・大きさ・金の線は今まで通り）
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.evaluate(()=>{render(0.02);const f=document.querySelector('.face.cover');const e=[...f.querySelectorAll('svg #emb')].pop()||[...f.querySelectorAll('svg')].pop();
 let g='<g transform="translate(250,1150) scale(.72)" fill="#e3c88c">';const N=13;let y=60;
 g+='<rect x="-34" y="'+(y+22)+'" width="68" height="10"/><rect x="-18" y="'+(y-20)+'" width="36" height="42"/>';
 for(let i=0;i<N;i++){const k=i/(N-1),sp=110-46*Math.pow(k,.85),th=9-2*k,yy=y-20-i*(13.6-2.4*k);
  g+=`<path d="M${-sp/2},${yy-th*.4} Q${-sp*.22},${yy+th*.3} 0,${yy+th*.35} Q${sp*.22},${yy+th*.3} ${sp/2},${yy-th*.4} Q${sp*.2},${yy-th*.9} ${sp*.08},${yy-th*1.3} L${-sp*.08},${yy-th*1.3} Q${-sp*.2},${yy-th*.9} ${-sp/2},${yy-th*.4}Z"/>`;
  if(i<N-1)g+=`<rect x="${-sp*.2}" y="${yy-th*1.3-4}" width="${sp*.4}" height="5"/>`}
 const top=y-20-(N-1)*(13.6-2.4)-12;g+=`<rect x="-2" y="${top-44}" width="4" height="46"/>`;for(let i=0;i<7;i++)g+=`<rect x="-7" y="${top-10-i*4.6}" width="14" height="2.2"/>`;g+=`<ellipse cx="0" cy="${top-46}" rx="4" ry="7"/></g>`;
 e.innerHTML=g;const fo=f.querySelector('#foil');if(fo)fo.style.display='none'});
const f=p.locator('.face.cover').first();console.log(await f.boundingBox());await f.screenshot({path:process.argv[3]});await b.close()})();
