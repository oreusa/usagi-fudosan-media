// node mapshot6.cjs '<query>' out.mp4 秒  /  node mapshot6.cjs '<query>' out.jpg 秒 t1 t2..（試し）
const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');(async()=>{
const [q,out,dur,...ts]=process.argv.slice(2);const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1080,height:1662}});
await p.goto('file://'+__dirname+'/map6.html?'+q+'&dur='+dur);await p.waitForFunction('window.ready',null,{timeout:60000});
const shot=async(t,f)=>{await p.evaluate(t=>draw(t),t);await p.screenshot({path:f,type:'jpeg',quality:94})};
if(ts.length){for(const [i,t] of ts.entries())await shot(+t,out.replace('.jpg',`-${i}.jpg`));await b.close();return}
const d=out+'.d';fs.rmSync(d,{recursive:true,force:true});fs.mkdirSync(d);const N=Math.round(+dur*30);
for(let i=0;i<N;i++)await shot(i/30,`${d}/f${String(i).padStart(4,'0')}.jpg`);await b.close();
execSync(`ffmpeg -y -loglevel error -framerate 30 -i ${d}/f%04d.jpg -c:v libx264 -crf 15 -pix_fmt yuv420p ${out}`);fs.rmSync(d,{recursive:true,force:true});console.log('OK',out)})();
