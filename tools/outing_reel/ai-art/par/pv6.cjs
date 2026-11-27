// 1場面＝数カット。node pv3.cjs shots.json 出力mp4   shots=[{img,dep,dur,m:{...},ease}]  m のキー: z0 z1 cx cy px0 px1 py0 py1 b0 b1 r0 r1 mist ray rx ry
const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');(async()=>{
const [sj,outmp4]=process.argv.slice(2);const shots=JSON.parse(fs.readFileSync(sj));
const b=await chromium.launch({args:['--allow-file-access-from-files','--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1080,height:1662}});
await p.goto('file://'+__dirname+'/par6.html');await p.waitForFunction('window.ready');await p.evaluate(u=>setLeaves(u),'file://'+__dirname+'/leaves.png');
const E={soft:t=>.5-.5*Math.cos(Math.PI*t)*1, io:t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,out:t=>1-Math.pow(1-t,3),lin:t=>t,o2:t=>1-Math.pow(1-t,2)};
const tmp=outmp4+'.d';fs.rmSync(tmp,{recursive:true,force:true});fs.mkdirSync(tmp,{recursive:true});const parts=[];
for(const [k,s] of shots.entries()){await p.evaluate(([k,a,d])=>setPair(k,a,d),['s'+k,'file://'+s.img,'file://'+s.dep]);await p.evaluate(u=>setMask(u),'file://'+(s.mask||__dirname+'/mask/blk.png'));const m=s.m;const N=Math.round(s.dur*30);const es=E[s.ease||'o2'];const dir=`${tmp}/c${k}`;fs.mkdirSync(dir);
 for(let i=0;i<N;i++){const q=es(i/(N-1));const L=(a,b)=>(a||0)+((b||0)-(a||0))*q;
  await p.evaluate(f=>frame(f),{z:L(m.z0,m.z1),cx:m.cx??.5,cy:m.cy??.45,px:L(m.px0,m.px1),py:L(m.py0,m.py1),base:L(m.b0??1.06,m.b1??1.06),rot:L(m.r0,m.r1),tm:(i/30)+k*3,mist:m.mist||0,ray:m.ray||0,wind:m.wind,rx:m.rx,ry:m.ry,st:m.st,wy:m.wy,shk:m.shk,spk:m.spk,lf:m.lf,bok:m.bok,lu:(m.lu0??1)+((m.lu1??1)-(m.lu0??1))*Math.min(1,(i/30)/(m.lut||1.5)),sd:m.sd||k,ly:m.ly||0,fl:m.fl||0,fx:m.fx,fy:m.fy,gf:m.gf||0,gfy:m.gfy});
  const u=await p.evaluate(()=>document.getElementById('g').toDataURL('image/jpeg',.95));fs.writeFileSync(`${dir}/f${String(i).padStart(4,'0')}.jpg`,Buffer.from(u.split(',')[1],'base64'))}
 execSync(`ffmpeg -y -loglevel error -framerate 30 -i ${dir}/f%04d.jpg -c:v libx264 -crf 14 -pix_fmt yuv420p ${tmp}/c${k}.mp4`);parts.push({f:`${tmp}/c${k}.mp4`,dur:s.dur,tr:s.tr||'fade'})}
await b.close();
// つなぎ：xfade 0.3秒。色を締める＋光のにじみ＋くっきり
const X=.3;let fc='',last='[0:v]',off=0;
for(let i=1;i<parts.length;i++){off+=parts[i-1].dur-X;fc+=`${last}[${i}:v]xfade=transition=${parts[i].tr}:duration=${X}:offset=${off.toFixed(3)}[x${i}];`;last=`[x${i}]`}
fc+=`${last}${process.env.MYS?"eq=contrast=1.04:saturation=.84:gamma=.97,colorbalance=rs=-.06:gs=-.01:bs=.08:rm=-.02:bm=.04:rh=.04:gh=.01:bh=-.04,curves=all='0/0 0.25/0.22 0.75/0.78 1/0.98'":process.env.NAT?"eq=contrast=1.02:saturation=.86:gamma=1.0,colorbalance=rs=-.02:bs=.03:rh=.02:bh=-.02,curves=all='0/0 0.25/0.23 0.75/0.77 1/0.98'":"eq=contrast=1.10:saturation=1.14:gamma=.96,curves=all='0/0 0.25/0.21 0.75/0.79 1/1'"},split[a][g];[g]curves=all='0/0 0.6/0 1/1',gblur=sigma=28[gl];[a][gl]blend=all_mode=screen:all_opacity=${process.env.NAT?.22:.35},${process.env.NAT?'noise=alls=5:allf=t,unsharp=5:5:.35':'unsharp=5:5:.7'},vignette=PI/6[o]`;
execSync(`ffmpeg -y -loglevel error ${parts.map(x=>'-i '+x.f).join(' ')} -filter_complex "${fc}" -map "[o]" -c:v libx264 -crf 15 -pix_fmt yuv420p ${outmp4}`);
fs.rmSync(tmp,{recursive:true,force:true});console.log('OK',outmp4)})();
