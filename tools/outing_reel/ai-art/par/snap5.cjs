// 試し：場面の json の1カット目を、決めた秒で数枚だけ撮る。node snap5.cjs shot.json out.jpg t1 t2 ...
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [sj,out,...ts]=process.argv.slice(2);const s=JSON.parse(fs.readFileSync(sj))[0];const m=s.m;
const b=await chromium.launch({args:['--allow-file-access-from-files','--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1080,height:1662}});
await p.goto('file://'+__dirname+'/par5.html');await p.waitForFunction('window.ready');await p.evaluate(u=>setLeaves(u),'file://'+__dirname+'/leaves.png');await p.evaluate(([a,d])=>setPair('s0',a,d),['file://'+s.img,'file://'+s.dep]);
for(const [j,t] of ts.entries()){const q=Math.min(1,t/s.dur);const L=(a,b)=>(a||0)+((b||0)-(a||0))*q;
 await p.evaluate(f=>frame(f),{z:L(m.z0,m.z1),cx:m.cx??.5,cy:m.cy??.45,px:L(m.px0,m.px1),py:L(m.py0,m.py1),base:L(m.b0??1.06,m.b1??1.06),tm:+t,wind:m.wind,st:m.st,wy:m.wy,shk:m.shk,spk:m.spk,lf:m.lf,bok:m.bok,lu:(m.lu0??1)+((m.lu1??1)-(m.lu0??1))*Math.min(1,t/(m.lut||1.5)),sd:m.sd||0,ly:m.ly||0,ray:m.ray,mist:m.mist,rx:m.rx,ry:m.ry});
 const u=await p.evaluate(()=>document.getElementById('g').toDataURL('image/jpeg',.9));fs.writeFileSync(out.replace('.jpg',`-${j}.jpg`),Buffer.from(u.split(',')[1],'base64'))}
await b.close()})();
