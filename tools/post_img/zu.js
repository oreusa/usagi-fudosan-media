// 投稿の絵の新しい3つの形（11/22 オーナー「画像とかももっと工夫できそ？アップグレードは大事」→「月に任せる」。設計図 https://claude.ai/artifact/93ENQXWK2LqNL2ADzRA74C ）
// glass.js と同じ光の地・ロゴ・字で、中身の形だけ替える。
// 使い方：node tools/post_img/zu.js <spec.json>   spec＝[{kind, name, night?, pill, en, head, …}]
//   kind "route"：路線の並び順に全部の駅と順位。stations:[[駅, 人数, 順位, 目立たせる?]…]（線の上の順）、cap（出どころ1行）、q（問い1行）
//   kind "floor"：1つの建物に開く店を階ごとに。floors:[[階, [店…], 目立たせる?]…]（上の階から）、foot（駅からの道1行）、q
//   kind "grid" ：2府4県を1枚のマス目に。cells:[[府県, 大きい字, 小さい字1行]…]（6つ）、q
//   head は <br> と <em>…</em> だけ。どの形も最後に q の問いを1行（本文の問いと同じ言葉）。
//   出来上がり：OUT_DIR（無ければ media/post）/card-<name>.jpg と cards.json。はみ出す時は作らない（× を出す）。
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const CFG=require(process.env.CARD_CFG||'./card-config.js');
const OUT=process.env.OUT_DIR||CFG.out;
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const head=s=>esc(s).split('&lt;br&gt;').map(l=>`<span class="ln">${l.replace(/&lt;em&gt;/g,'<em>').replace(/&lt;\/em&gt;/g,'</em>')}</span>`).join('');
const logo='data:image/png;base64,'+fs.readFileSync(CFG.logo).toString('base64');
const num=n=>typeof n==='number'?n.toLocaleString('en-US'):esc(n);
const stars=(seed)=>{let s=0;for(const c of seed)s=(s*31+c.charCodeAt(0))>>>0;const r=()=>(s=(s*1103515245+12345)>>>0)/4294967296;let o='';
  for(let i=0;i<110;i++){const x=r()*1080,y=r()*1350,z=r()<.08?2.6:r()<.3?1.7:1.1,a=.2+r()*.6;o+=`<b style="left:${x.toFixed(0)}px;top:${y.toFixed(0)}px;width:${z}px;height:${z}px;opacity:${a.toFixed(2)}"></b>`}return o};

function body(x,N){
  if(x.kind==='route'){
    const st=x.stations,mx=Math.max(...st.map(s=>+s[1]||0)),two=st.length>24,half=Math.ceil(st.length/(two?2:1));
    const col=a=>`<div class="rt">${a.map(s=>`<div class="s${s[3]?' hi':''}"><i></i><span class="nm">${esc(s[0])}</span><span class="b"><em style="width:${Math.max(1.5,(+s[1]||0)/mx*100).toFixed(1)}%"></em></span><span class="v">${num(s[1])}</span><span class="rk">${esc(s[2])}<small>位</small></span></div>`).join('')}</div>`;
    return `<div class="card route${two?' two':''}"><div class="cols">${two?col(st.slice(0,half))+col(st.slice(half)):col(st)}</div><div class="src">${esc(x.cap||'')}</div></div>`;
  }
  if(x.kind==='floor'){
    return `<div class="card floor">${x.floors.map(f=>`<div class="fl${f[2]?' hi':''}"><div class="fn">${esc(f[0])}</div><div class="fs">${f[1].map(n=>`<span>${esc(n)}</span>`).join('')}</div></div>`).join('')}<div class="src">${esc(x.foot||'')}</div></div>`;
  }
  if(x.kind==='grid'){
    return `<div class="grid">${x.cells.map(c=>`<div class="cell"><div class="pf">${esc(c[0])}</div><div class="cb">${esc(c[1])}</div><div class="cs">${esc(c[2]||'')}</div></div>`).join('')}</div>`;
  }
  return '';
}

const HTML=x=>{const N=x.night!=null?!!x.night:!!(CFG.night&&CFG.night.test(x.name||''));
const fg=N?'#F5F5F7':'#1D1D1F',sub=N?'rgba(245,245,247,.62)':'#6E6E73',ln=N?'rgba(255,255,255,.12)':'rgba(0,0,0,.07)',acc=N?'#FFB65C':'#C2560C',line=N?'#7FE3D8':'#0E8F84';
return `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}
body{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:"Noto Sans JP",sans-serif;-webkit-font-smoothing:antialiased;background:${N?'#070A14':'#F8F8FA'};color:${fg}}
.hero{position:absolute;inset:0 0 auto 0;height:760px;overflow:hidden}
.hero i{position:absolute;border-radius:50%;filter:blur(${N?90:110}px);opacity:${N?.4:.3}}
.hero i:nth-child(1){width:860px;height:860px;left:-300px;top:-420px;background:#FFB65C}
.hero i:nth-child(2){width:780px;height:780px;right:-360px;top:-260px;background:#2EC4B6}
.hero i:nth-child(3){width:620px;height:620px;left:260px;top:60px;background:#F6A6C8;opacity:${N?.3:.1}}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(${N?'7,10,20':'248,248,250'},0) 40%,${N?'#070A14':'#F8F8FA'})}
.stz{position:absolute;inset:0}.stz b{position:absolute;border-radius:50%;background:#fff;box-shadow:0 0 6px rgba(255,255,255,.8)}
.top{position:absolute;left:64px;right:64px;top:56px;display:flex;align-items:center;gap:16px}
.top img{width:56px;height:56px;border-radius:50%;background:rgba(255,255,255,.75);padding:5px;object-fit:contain}
.top .br{font:600 20px Inter;letter-spacing:.22em;color:${N?'rgba(245,245,247,.85)':'rgba(29,29,31,.75)'}}
.top .pl{margin-left:auto;font:500 24px "Noto Sans JP";padding:10px 24px;border-radius:999px;background:${N?'rgba(255,255,255,.12)':'rgba(255,255,255,.6)'};border:1px solid ${N?'rgba(255,255,255,.18)':'rgba(255,255,255,.85)'}}
.en{position:absolute;left:64px;top:150px;font:500 22px Inter;letter-spacing:.3em;color:${sub}}
.hd{position:absolute;left:60px;right:60px;top:190px;font:800 ${x.hs||68}px/1.24 "Noto Sans JP";letter-spacing:-.01em}
.hd .ln{display:block;white-space:nowrap;overflow:hidden}
.hd em{font-style:normal;background:linear-gradient(90deg,rgba(255,182,92,.6),rgba(46,196,182,.5));background-size:100% 24%;background-position:0 88%;background-repeat:no-repeat}
.main{position:absolute;left:48px;right:48px;top:var(--mt);bottom:150px;display:flex;flex-direction:column}
.card{flex:1;border-radius:36px;padding:26px 34px;background:${N?'rgba(22,28,44,.66)':'rgba(255,255,255,.86)'};border:1px solid ${N?'rgba(255,255,255,.12)':'rgba(255,255,255,.95)'};box-shadow:0 30px 70px -40px rgba(0,0,0,${N?.9:.3});display:flex;flex-direction:column}
.route{padding:22px 34px 18px}
.cols{flex:1;min-height:0;display:flex;gap:0 36px}
.rt{flex:1;min-width:0;display:flex;flex-direction:column}
.s{display:grid;grid-template-columns:24px 180px 1fr 116px 70px;align-items:center;gap:12px;position:relative;flex:1 1 0;min-height:0;line-height:1}
.two .s{grid-template-columns:22px 150px 1fr 0 58px;gap:8px}.two .s .v{display:none}
.s::before{content:"";position:absolute;left:9px;top:0;bottom:0;width:4px;background:${line};opacity:.85}
.s:first-child::before{top:50%}.s:last-child::before{bottom:50%}
.s i{width:22px;height:22px;border-radius:50%;border:4px solid ${line};background:${N?'#151B2B':'#fff'};z-index:1}
.two .s i{width:22px;height:22px}.two .s::before{left:9px}
.s .nm{font:500 27px "Noto Sans JP";white-space:nowrap;overflow:hidden}
.s .b{height:12px;border-radius:6px;background:${ln};overflow:hidden}.s .b em{display:block;height:100%;border-radius:6px;background:${N?'rgba(245,245,247,.45)':'rgba(29,29,31,.32)'}}
.s .v{font:400 24px Inter;text-align:right;color:${sub};font-variant-numeric:tabular-nums}
.s .rk{font:500 26px Inter;text-align:right;font-variant-numeric:tabular-nums}.s .rk small{font:500 18px "Noto Sans JP";margin-left:2px;color:${sub}}
.s.hi .nm,.s.hi .rk{color:${acc};font-weight:800}.s.hi .b em{background:${acc}}.s.hi i{border-color:${acc};background:${acc}}
.src{margin-top:auto;padding-top:14px;width:100%;font:400 20px "Noto Sans JP";color:${sub}}
.floor{gap:0;padding:18px 34px}
.fl{display:grid;grid-template-columns:128px 1fr;gap:24px;align-items:center;padding:22px 0;border-bottom:1px solid ${ln};flex:1}
.fl:last-of-type{border-bottom:0}
.fn{font:300 68px/1 Inter;letter-spacing:-.03em;color:${sub}}
.fs{display:flex;flex-wrap:wrap;gap:12px 14px}.fs span{font:500 32px "Noto Sans JP";padding:10px 22px;border-radius:999px;background:${N?'rgba(255,255,255,.08)':'#F2F2F5'}}
.fl.hi .fn{color:${acc}}.fl.hi .fs span:first-child{background:${acc};color:#fff;font-weight:700}
.grid{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:18px}
.cell{border-radius:30px;padding:24px 28px;background:${N?'rgba(22,28,44,.66)':'rgba(255,255,255,.88)'};border:1px solid ${N?'rgba(255,255,255,.12)':'rgba(255,255,255,.95)'};box-shadow:0 24px 50px -36px rgba(0,0,0,${N?.9:.28});display:flex;flex-direction:column;min-width:0}
.pf{font:700 26px "Noto Sans JP";color:${line};letter-spacing:.08em}
.cb{margin-top:10px;font:800 40px/1.25 "Noto Sans JP";overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.cs{margin-top:auto;font:500 24px "Noto Sans JP";color:${sub};white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.q{position:absolute;left:64px;right:64px;bottom:72px;font:700 38px "Noto Sans JP";display:flex;align-items:center;gap:16px}
.q::before{content:"";width:10px;height:44px;border-radius:5px;background:linear-gradient(180deg,#FFB65C,#2EC4B6)}
.ft{position:absolute;right:64px;bottom:30px;font:500 18px Inter;letter-spacing:.32em;color:${sub}}
</style><body>
<div class="hero"><i></i><i></i><i></i></div>${N?`<div class="stz">${stars(x.name)}</div>`:''}
<div class="top"><img src="${logo}"><div class="br">${esc(CFG.name||'KANSAI TOWN NOTE')}</div>${x.pill?`<div class="pl">${esc(x.pill)}</div>`:''}</div>
${x.en?`<div class="en">${esc(x.en)}</div>`:''}<div class="hd">${head(x.head)}</div>
<div class="main" style="--mt:${x.mt||400}px">${body(x,N)}</div>
${x.q?`<div class="q">${esc(x.q)}</div>`:''}<div class="ft">${esc(CFG.brand||'TOWN NOTE')}</div></body>`};

(async()=>{const specs=[].concat(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));fs.mkdirSync(OUT,{recursive:true});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});let n=0;
 for(const x of specs){if(!/^[a-z0-9-]+$/.test(x.name||'')||!['route','floor','grid'].includes(x.kind)){console.log('× name か kind：',x.name,x.kind);continue}
  // 見出しの行数で中身の上の位置を決め、見出しが横にはみ出す時は字を小さく（68→62→56）。中身がはみ出す時は作らない
  const lines=String(x.head||'').split('<br>').length;let bad=true;
  for(const hs of [x.hs||68,62,56]){const mt=190+Math.ceil(hs*1.24)*lines+40;
   await p.setContent(HTML(Object.assign({},x,{hs,mt})),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
   bad=await p.evaluate(()=>{const over=e=>e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2;
    const els=[...document.querySelectorAll('.hd .ln,.s .nm,.cs,.q')];const m=document.querySelector('.main');
    const kids=[...m.querySelectorAll('.s,.fl,.cell,.src')];const mb=m.getBoundingClientRect();
    const why=[];els.forEach(e=>{if(e.scrollWidth>e.clientWidth+2)why.push('横：'+e.textContent.slice(0,12))});
    kids.forEach(k=>{if(k.getBoundingClientRect().bottom>mb.bottom+1)why.push('下：'+k.textContent.slice(0,12))});
    if([...document.querySelectorAll('.s')].some(s=>s.getBoundingClientRect().height<28))why.push('駅の行が細い');return why.join(' / ')});
   if(bad)console.log('  ',x.name,hs,bad);
   if(!bad)break}
  if(bad){console.log('× 入らない：',x.name,bad);process.exitCode=1;continue}
  await p.screenshot({path:path.join(OUT,`card-${x.name}.jpg`),type:'jpeg',quality:90});n++;
  if(!process.env.OUT_DIR||process.env.OUT_DIR===CFG.out){const f=path.join(OUT,'cards.json');let j={};try{j=JSON.parse(fs.readFileSync(f,'utf8'))}catch(e){}j.items=j.items||{};
   j.items[`card-${x.name}`]={url:CFG.base+`card-${x.name}.jpg?v=`+Date.now().toString(36),made:new Date(Date.now()+9*3600e3).toISOString().slice(0,10)};fs.writeFileSync(f,JSON.stringify(j,null,1))}}
 await b.close();console.log(`作った ${n} 枚`)})();
