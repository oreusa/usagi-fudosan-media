const PAL=['#b3121e','#c8241f','#d93a22','#e2582a','#9c0f1c','#eb8a3a','#7e0c18'];
const PALK=['#e8a42c','#f0b83a','#d98a24','#e8702e','#c8781e','#f2c552'];   // 黄・橙（談山はカエデに黄が混ざる）
const PALM=PAL.concat(PAL,PALK);
function glow(x,cx,cy,r,a,col='255,240,200'){const g=x.createRadialGradient(cx,cy,0,cx,cy,r);g.addColorStop(0,`rgba(${col},${a})`);g.addColorStop(1,`rgba(${col},0)`);x.fillStyle=g;x.fillRect(cx-r,cy-r,r*2,r*2)}
