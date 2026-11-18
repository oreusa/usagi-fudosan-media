// 11/18 HP全体の見回り：公開中のページを スマホ幅・昼と夜 で撮り、壊れた画像・JSのエラー・横にはみ出しを数える
// node tools/review/shots.js <URLの一覧ファイル> <出力フォルダ>   （一覧は1行1URL。「名前<TAB>URL」でもよい）
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [list,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const L=fs.readFileSync(list,'utf8').split('\n').map(s=>s.trim()).filter(Boolean).map((s,i)=>{const a=s.split('\t');return a.length>1?[a[0],a[1]]:[String(i).padStart(2,'0'),a[0]]});
const b=await chromium.launch();const log=[];
for(const [name,url] of L){for(const night of [false,true]){
 const c=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
 if(night)await c.addInitScript(()=>{try{localStorage.setItem('usagi_theme','night')}catch(e){}});
 await c.addInitScript(()=>{try{localStorage.setItem('usagi_owner','1')}catch(e){}});
 const p=await c.newPage();const err=[];p.on('pageerror',e=>err.push(String(e).slice(0,160)));
 p.on('response',r=>{if(r.status()>=400&&!/google|gstatic|doubleclick|instagram/.test(r.url()))err.push(r.status()+' '+r.url().slice(0,140))});
 try{await p.goto(url,{waitUntil:'networkidle',timeout:45000})}catch(e){err.push('goto '+e)}
 await p.waitForTimeout(1500);
 await p.evaluate(async()=>{for(let y=0;y<Math.min(document.body.scrollHeight,9000);y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,120))}scrollTo(0,0)});
 await p.waitForTimeout(1200);
 const st=await p.evaluate(()=>({h:document.body.scrollHeight,over:document.documentElement.scrollWidth>innerWidth+1,ovw:(()=>{if(document.documentElement.scrollWidth<=innerWidth+1)return '';const o=[];for(const e of document.body.querySelectorAll('*')){const r=e.getBoundingClientRect();if(r.right>innerWidth+1&&r.width>0&&getComputedStyle(e).position!=='fixed')o.push(e.tagName+'.'+String(e.className).slice(0,30)+'@'+Math.round(r.left)+'-'+Math.round(r.right));if(o.length>6)break}return 'sw='+document.documentElement.scrollWidth+' '+o.join(',')})(),
   broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&i.src&&!/instagram/.test(i.src)).map(i=>i.src.slice(-60)),
   imgs:[...document.images].filter(i=>i.naturalWidth>0).length,empty:[...document.querySelectorAll('b,strong,span')].filter(e=>/^\s*0\s*件?$/.test(e.textContent)&&e.offsetParent).length}));
 // 11/18 見やすさの自動点検（axe-core）：文字の濃さ・押す所の名前・画像の説明など。重い・深刻の数だけ記録（昼だけ）
 let ax='';if(!night){try{await p.addScriptTag({path:require.resolve('axe-core')});const r=await p.evaluate(async()=>{const x=await axe.run(document,{resultTypes:['violations']});return x.violations.filter(v=>v.impact==='serious'||v.impact==='critical').map(v=>v.id+':'+v.nodes.length)});ax=r.join(',')||'0'}catch(e){ax='err'}}
 const tag=`${name}-${night?'n':'d'}`;
 // 1画面ずつ（全体を1枚で撮ると、夜の背景や固定の部品・あとから出る部分が本物と違って写るため）
 const N=Math.min(Math.ceil(st.h/760),+(process.env.MAXN||8));
 for(let i=0;i<N;i++){await p.evaluate(y=>scrollTo(0,y),i*760);await p.waitForTimeout(700);await p.screenshot({path:`${out}/${tag}-${i}.png`})}
 log.push([tag,url,'h='+st.h,'imgs='+st.imgs,'broken='+st.broken.length,'over='+st.over+(st.ovw?'('+st.ovw+')':''),'zero='+st.empty,'err='+err.length,'axe='+ax,st.broken.join(' '),err.join(' | ')].join('\t'));
 await c.close();}}
fs.writeFileSync(`${out}/log.tsv`,log.join('\n')+'\n');console.log(log.join('\n'));await b.close()})();
