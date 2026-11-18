/* 11/18 今のHPのクオリティアップ（見本）。今のページ・部品はそのまま、足すだけ。
   ?mihon=1 を付けた人だけに出る（night.js が読み込む・?mihon=0 で消える）。
   足す物：カードの絵の所に本物の写真／【地名】の一言／いまライトアップ中・あと◯分／カードを押すと1件ページ／
   1件ページに 写真・どんな催し？・行きたい・カレンダー・送る。表は /assets/mihon.json（tools/mihon/build.py）。 */
(function(){
if(window.__mihon)return;window.__mihon=1;
var D={},ID={},READY=0;
var css=
/* カードの絵の所（66px の角丸）に写真。英字の札（LIGHT など）と日付の札は今のまま */
'.cmb .ib.mph{background:#ddd}'+
'.cmb .ib.mph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:inherit}'+
'.cmb .ib.mph svg,.cmb .ib.mph::before{display:none!important}'+
'.cmb .ib.mph::after{z-index:2}'+
'.cmb .ib.mph .lb{z-index:1;color:#fff;opacity:1;bottom:0;padding:9px 0 5px .22em;background:linear-gradient(transparent,rgba(20,16,12,.55));text-shadow:0 1px 2px rgba(0,0,0,.3)}'+
/* 【地名】の一言（題の上の小さな1行） */
'.mhk{display:block;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12.5px;line-height:1.5;color:var(--pc,#6b625b);margin:2px 0 3px;letter-spacing:.02em}'+
'a.fc .mhk{font-size:11.5px;margin:1px 0 2px}'+
/* いまライトアップ中（今の「開催中」の札の横） */
'.mnow{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;line-height:1;padding:5px 9px 5px 8px;border-radius:999px;background:#E7F4EC;color:#1E7A4A;white-space:nowrap}'+
'.mnow::before{content:"";width:6px;height:6px;border-radius:50%;background:#22A35A;box-shadow:0 0 0 0 rgba(34,163,90,.5);animation:mnp 1.8s ease-out infinite}'+
'.mnow.soon{background:#FBF0E2;color:#A55A12}.mnow.soon::before{background:#E08A2E;animation:none}'+
'@keyframes mnp{0%{box-shadow:0 0 0 0 rgba(34,163,90,.5)}80%,100%{box-shadow:0 0 0 7px rgba(34,163,90,0)}}'+
'@media (prefers-reduced-motion:reduce){.mnow::before{animation:none}}'+
'.mnowl{margin-top:8px}'+
/* おすすめ5 の小さな絵 → 写真 */
'.pr5 .ti.mph{overflow:hidden;padding:0!important}.pr5 .ti.mph img{width:100%;height:100%;object-fit:cover;display:block}.pr5 .ti.mph svg{display:none}'+
/* 1件ページ：写真・一言・どんな催し？・ボタン */
'img.mfade{opacity:0;transform:scale(1.035);transition:opacity .55s cubic-bezier(.2,.7,.2,1),transform .9s cubic-bezier(.2,.7,.2,1)}img.mfade.in{opacity:1;transform:none}'+
'.mbp,.mnsl,.m1,.cmb .ib.mph,.pr5 .ti.mph{background:linear-gradient(100deg,#ece8e3 30%,#f6f3ef 50%,#ece8e3 70%) 0 0/300% 100%!important;animation:mshm 1.3s linear infinite}'+
'.mbp.ld,.mnsl.ld,.m1.ld,.cmb .ib.mph.ld,.pr5 .ti.mph.ld{animation:none}'+
'@keyframes mshm{to{background-position:-300% 0}}'+
'.mnews .mnsl img.in{transform:scale(1.0);transition:opacity .55s,transform 7s linear}.mnews .mnsl.cur img.in{transform:scale(1.07)}'+
'a.card.mbig,.mnews .mnsl,.pr5 .m1{-webkit-tap-highlight-color:transparent}.mnews .mnsl:active,.pr5 .m1:active{scale:.985;transition:scale .15s}'+
'@media (prefers-reduced-motion:reduce){img.mfade{transition:none;transform:none}.mnews .mnsl.cur img.in{transform:none}.mbp,.mnsl,.m1{animation:none!important}}'+
'.mph-o{margin:0 0 14px}.mph-o img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:18px;background:#eee;box-shadow:0 14px 30px -18px rgba(40,30,20,.45)}'+
'.mph-o figcaption{font-size:10.5px;color:#9a928b;margin:7px 2px 0;line-height:1.5}.mph-o figcaption a{color:inherit}'+
'.head .mhk-o{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:14px;color:var(--pc,#6b625b);margin:10px 0 0;letter-spacing:.03em;line-height:1.6;position:relative}'+
'.mds{background:#F4F4F5;border-radius:4px;padding:16px 16px 15px;margin:14px 0 0}.mds span{display:block;font-size:10.5px;color:#8a837d;letter-spacing:.08em;margin-bottom:6px}.mds p{margin:0;font-size:14.5px;line-height:1.9;color:#2B2622}'+
'.act a.mfav[aria-pressed=true]{background:#FFF7E0;border-color:#E2B53B;color:#7A5A00}'+
'.mshr{display:none;gap:8px;margin-top:8px}.mshr.open{display:flex}.mshr a{flex:1;text-align:center;font-size:13px;padding:11px 0;border-radius:10px;border:1px solid #ddd;color:#2B2622;text-decoration:none;font-weight:700}'+
/* 夜：ページ全体が反転するので、写真だけ元に戻す（night.js の決まり） */

'html.night .mnow{background:#E7F4EC}'+
/* 写真のあるカード：上に大きな写真。カードの絵のタイルと日付の札は今のまま、写真の下の端に少し重ねる */
'html body a.card.cm.mbig.mbig.mbig.mbig.mbig.mbig{padding-top:166px!important;min-height:0}'+
'a.card.mbig .mbp{position:absolute;left:0;right:0;top:0;height:150px;border-radius:8px 8px 0 0;overflow:hidden;background:#e9e6e2}'+
'a.card.mbig .mbp img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s ease}'+
'a.card.mbig:hover .mbp img{transform:scale(1.03)}'+
'a.card.mbig .mbp small{position:absolute;right:8px;bottom:6px;font-size:9px;color:#fff;opacity:.85;text-shadow:0 1px 2px rgba(0,0,0,.6);max-width:60%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'+
'a.card.mbig .cmb{top:120px!important;z-index:2}'+
'a.card.mbig .cmb .ib{box-shadow:0 0 0 3px #fff,0 10px 18px -10px rgba(0,0,0,.45)}'+
'a.card.mbig .wfav{z-index:3}'+
/* きょうのおでかけニュース（3つの入口のすぐ下） */
'.mnews{margin:22px 0 6px}'+
'.mnews .mnh{display:flex;align-items:flex-end;justify-content:space-between;padding:0 2px 10px}'+
'.mnews .mnh small{display:block;font-family:Jost,sans-serif;font-size:10px;letter-spacing:.28em;color:#B97A62;margin-bottom:5px}'+
'.mnews .mnh b{font-family:"Shippori Mincho","Noto Serif JP",serif;font-weight:600;font-size:19px;letter-spacing:.12em;color:#2B2622}'+
'.mnews .mnh time{font-size:11.5px;color:#8a837d;letter-spacing:.04em}'+
'.mnews .mnh{gap:8px}.mnews .mnlive{margin-left:auto;margin-right:8px;display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:#1E7A4A;background:#E7F4EC;border-radius:999px;padding:5px 10px;white-space:nowrap}.mnews .mnlive b{font-family:Jost,sans-serif;font-size:13px}.mnews .mnlive i{width:7px;height:7px;border-radius:50%;background:#22A35A;animation:mnp 1.8s ease-out infinite}.mnews .mnlive i.s{background:#E08A2E;animation:none}.mnews .mnlive:has(i.s){color:#A55A12;background:#FBF0E2}'+'.mnews .mntr{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:10px;scrollbar-width:none;-webkit-overflow-scrolling:touch;margin:0 -2px;padding:0 2px 4px}.mnews .mntr::-webkit-scrollbar{display:none}'+
'.mnews .mnsl{position:relative;flex:0 0 100%;scroll-snap-align:start;border-radius:16px;overflow:hidden;aspect-ratio:4/3;display:block;color:#fff;text-decoration:none;background:#2b2622;box-shadow:0 16px 30px -20px rgba(40,30,20,.6)}'+
'.mnews .mnsl img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}'+
'.mnews .mnsl::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 38%,rgba(10,8,6,.78) 100%)}'+
'.mnews .mntx{position:absolute;left:16px;right:16px;bottom:15px;z-index:1}'+
'.mnews .mntg{display:inline-flex;gap:6px;align-items:center;font-size:11px;font-weight:700;background:rgba(255,255,255,.94);color:#2B2622;border-radius:999px;padding:5px 10px;margin-bottom:9px}'+
'.mnews .mntg i{font-style:normal;color:var(--pc,#B97A62)}'+
'.mnews .mntx b{display:block;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:900;font-size:21px;line-height:1.38;letter-spacing:.01em;text-shadow:0 1px 10px rgba(0,0,0,.35)}'+
'.mnews .mntx .mnn{display:block;font-size:12px;opacity:.9;margin-top:5px}'+
'.mnews .mncr{position:absolute;top:8px;right:10px;z-index:1;font-size:9px;opacity:.8;text-shadow:0 1px 2px rgba(0,0,0,.6)}'+
'.mnews .mndt{display:flex!important;flex-direction:row;justify-content:center;gap:6px;margin-top:10px}.mnews .mndt i{display:block;flex:none;width:6px;height:6px;border-radius:3px;background:#d6d1cb;transition:width .3s}.mnews .mndt i.on{width:18px;background:#2B2622}'+
/* おすすめ5 の1位：大きな写真 */
'.pr5 .m1{display:block;position:relative;margin:4px 0 2px;border-radius:12px;overflow:hidden;aspect-ratio:16/9;background:#e9e6e2}.pr5 .m1 img{width:100%;height:100%;object-fit:cover;display:block}'+
'.pr5 .m1 em{position:absolute;left:10px;top:10px;font-style:normal;font-family:Jost,sans-serif;font-weight:600;font-size:11px;letter-spacing:.14em;background:#fff;color:#C0563C;border-radius:999px;padding:4px 10px}'+
'html.night .mnews .mnsl{filter:invert(1) hue-rotate(180deg)}html.night .mnews .mnsl img{filter:none!important}'+
'html.night a.card.mbig .cmb .ib{box-shadow:0 0 0 3px #fff}'+
'html.night .mnews .mndt i.on{background:#2B2622}';
var st=document.createElement('style');st.textContent=css;(document.head||document.documentElement).appendChild(st);
function k(s){return (s||'').replace(/\s+/g,'')}
function find(t){return D[k(t)]}
function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function hook(o){return o.hk?(o.ar?'【'+o.ar+'】':'')+o.hk:''}
/* 日本の時刻 */
function jst(){return new Date(Date.now()+9*36e5)}
function ymd(d){return d.toISOString().slice(0,10)}
function closed(o,d){var t=ymd(d),w=d.getUTCDay();
  if(o.cl){if(o.cl.indexOf('-'+t)>=0)return true;if(o.cl.indexOf('+'+t)>=0)return false;}
  if(o.dy&&/^wd:/.test(o.dy)&&o.dy.slice(3).indexOf(String(w))<0)return true;return false}
function now(o){if(!o||!o.h)return null;var d=jst(),t=ymd(d);if(!(o.s<=t&&o.e>=t)||closed(o,d))return null;
  var m=d.getUTCHours()*60+d.getUTCMinutes(),x=o.h.split('-').map(function(v){var a=v.split(':');return a[0]*60+ +a[1]});if(x.length<2)return null;
  var night=x[0]>=15*60;
  if(m>=x[0]&&m<x[1]){var l=x[1]-m;if(l<=60)return{c:'',t:'あと'+l+'分で終わり'};return{c:'',t:night?'いまライトアップ中':'いま開いています'}}
  if(m<x[0]&&x[0]-m<=180)return{c:'soon',t:(night?'今夜':'きょう')+o.h.split('-')[0]+'から'};return null}
function nowPill(host,o,cls){var n=now(o),p=host.querySelector('.mnow');if(!n){if(p)p.remove();return}
  if(!p){p=document.createElement('span');host.appendChild(p)}p.className='mnow '+(n.c||'')+(cls?' '+cls:'');p.textContent=n.t}
function photo(box,o,big){if(box.classList.contains('mph'))return;box.classList.add('mph');var i=document.createElement('img');i.alt='';i.loading='lazy';i.decoding='async';i.className='mfade';i.src='/assets/ph/'+(big?'':'t/')+o.im;box.insertBefore(i,box.firstChild)}
/* カード（一覧・府県・イルミ・紅葉・泊まり・いまから・1件ページの「ほかのおでかけ」） */
function cards(){
  document.querySelectorAll('a.card,a.fc').forEach(function(a){
    var tt=a.querySelector(a.matches('a.fc')?'b':'.t');if(!tt)return;var o=find(tt.textContent);if(!o)return;
    if(o.im){if(a.matches('a.card')&&!o.wk){if(!a.querySelector('.mbp')&&a.querySelector('.cmb')){var f=document.createElement('div');f.className='mbp';f.innerHTML='<img class="mfade" src="/assets/ph/s/'+o.im+'" alt="" loading="lazy" decoding="async"><small>'+esc(o.cr.replace(/（.*$/,''))+'</small>';a.insertBefore(f,a.firstChild);a.classList.add('mbig');var go=a.querySelector(':scope>.go');if(go){var cs=getComputedStyle(go);if(cs.position==='absolute'&&parseFloat(cs.top)<60)go.style.top=(parseFloat(cs.top)+152)+'px'}}}
      else if(!a.querySelector('.mbp')){var ib=a.querySelector('.cmb .ib');if(ib)photo(ib,o)}}
    if(!a.dataset.mh){var h=hook(o);if(h){var s=document.createElement('span');s.className='mhk';s.textContent=h;tt.parentNode.insertBefore(s,tt)}a.dataset.mh=1}
    var row=a.querySelector('.v2c');if(row)nowPill(row,o);
    if(o.id&&a.matches('a.card'))a.dataset.mo=o.id;
  });
  document.querySelectorAll('.pr5 a').forEach(function(a){var b=a.querySelector('.tx b');if(!b)return;var o=find(b.textContent);if(!o)return;
    var ti=a.querySelector('.ti');if(ti&&o.im)photo(ti,o);if(o.id)a.dataset.mo=o.id});
  var p5=document.querySelector('.pr5');if(p5&&!p5.querySelector('.m1')){var as=p5.querySelectorAll('a[data-mo]');for(var i=0;i<as.length;i++){var b2=as[i].querySelector('.tx b'),o2=b2&&find(b2.textContent);if(o2&&o2.im&&!o2.wk){var m1=document.createElement('a');m1.className='m1';m1.href='/o/'+o2.id;m1.innerHTML='<img class="mfade" src="/assets/ph/s/'+o2.im+'" alt="" loading="lazy" decoding="async"><em>No.'+(i+1)+'</em>';as[i].parentNode.insertBefore(m1,as[i]);break}}}
  news();
}

/* きょうのおでかけニュース：3つの入口のすぐ下。写真のある・いま開催中か7日以内に始まる催しから、終わりが近い順に4つ */
function news(){var q=document.querySelector('.qk');if(!q||document.querySelector('.mnews'))return;
  var t=ymd(jst()),t7=ymd(new Date(jst().getTime()+7*864e5)),L=[];
  for(var x in D){var o=D[x];if(o.im&&!o.wk&&o.id&&o.hk&&o.e>=t&&o.s<=t7)L.push(o)}
  var sc=function(o){return (/イルミ|ライト|灯|光|夜|ルミナ|紅葉|もみじ/.test(o.n+o.hk)?0:2)+(o.s<=t?0:1)};
  L.sort(function(a,b){return sc(a)-sc(b)||(a.e<b.e?-1:1)});
  var P={};L=L.filter(function(o){if(P[o.p]>=1&&L.length>6)return false;P[o.p]=(P[o.p]||0)+1;return true}).slice(0,5);if(!L.length)return;
  var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"},W='日月火水木金土',d=jst();
  var h='<div class="mnh"><div><small>TODAY’S NEWS</small><b>きょうのおでかけニュース</b></div><span class="mnlive"></span><time>'+(d.getUTCMonth()+1)+'/'+d.getUTCDate()+'（'+W[d.getUTCDay()]+'）</time></div><div class="mntr">';
  L.forEach(function(o){var st=o.s<=t?'開催中':(+o.s.slice(5,7))+'/'+(+o.s.slice(8))+'から';h+='<a class="mnsl" href="/o/'+o.id+'" style="--pc:'+(PC[o.p]||'#B97A62')+'"><img class="mfade" src="/assets/ph/'+o.im+'" alt="" decoding="async"'+(L.indexOf(o)===0?' fetchpriority="high"':' loading="lazy"')+'><span class="mncr">写真：'+esc(o.cr.replace(/（.*$/,''))+'</span><span class="mntx"><span class="mntg"><i>'+esc(o.p)+'</i>'+st+'・'+(+o.e.slice(5,7))+'/'+(+o.e.slice(8))+'まで</span><b>'+esc(hook(o))+'</b><span class="mnn">'+esc(o.n)+'</span></span></a>'});
  h+='</div><div class="mndt">'+L.map(function(o,i){return '<i'+(i?'':' class="on"')+'></i>'}).join('')+'</div>';
  var w=document.createElement('section');w.className='mnews';w.setAttribute('aria-label','きょうのおでかけニュース');w.innerHTML=h;q.parentNode.insertBefore(w,q.nextSibling);
  var lv=w.querySelector('.mnlive');function live(){var on=0,soon=0;for(var x in D){var n=now(D[x]);if(n){if(n.c==='soon')soon++;else on++}}lv.innerHTML=on?'<i></i>いま開いている所 <b>'+on+'</b>':soon?'<i class="s"></i>まもなく点灯 <b>'+soon+'</b>':'';lv.hidden=!(on||soon)}live();setInterval(live,60000);
  var tr=w.querySelector('.mntr'),dots=w.querySelectorAll('.mndt i'),sl=w.querySelectorAll('.mnsl'),cur=0,hold=0;if(sl[0])sl[0].classList.add('cur');
  tr.addEventListener('scroll',function(){var i=Math.round(tr.scrollLeft/tr.clientWidth);if(i!==cur){cur=i;dots.forEach(function(e,k){e.classList.toggle('on',k===i)});sl.forEach(function(e,k){e.classList.toggle('cur',k===i)})}},{passive:true});
  ['touchstart','pointerdown'].forEach(function(ev){tr.addEventListener(ev,function(){hold=Date.now()},{passive:true})});
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches)setInterval(function(){if(Date.now()-hold<9000||document.hidden)return;var r=tr.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;tr.scrollTo({left:((cur+1)%dots.length)*tr.clientWidth,behavior:'smooth'})},5200);
}
/* カードを押すと、そのおでかけの1件ページ（写真・説明・公式ボタン）へ。☆・地図・近くの宿は今のまま */
function go(id,img){try{var o=ID[id];if(o&&o.im)sessionStorage.setItem('tn_mph',JSON.stringify({id:id,im:o.im}));else sessionStorage.removeItem('tn_mph')}catch(x){}
  if(img&&document.startViewTransition!==undefined||img&&'onpagereveal' in window){document.querySelectorAll('[style*="view-transition-name"]').forEach(function(x){if(x!==img)x.style.viewTransitionName=''});img.style.viewTransitionName='mph'}
  location.href='/o/'+id}
document.addEventListener('click',function(e){if(e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey)return;var t=e.target.closest&&e.target.closest('a[data-mo],a.mnsl,a.m1');if(!t)return;
  if(e.target.closest('.wfav,button'))return;var id=t.dataset.mo||(t.getAttribute('href')||'').replace(/^\/o\//,'');if(!/^[0-9a-f]{8}$/.test(id))return;
  e.preventDefault();go(id,t.querySelector('.mbp img,.ib.mph img,.ti.mph img,img'))},true);
/* 押す前に次のページを用意しておく（指を置いた時・マウスを乗せた時）→ 押した瞬間に開く */
try{if(HTMLScriptElement.supports&&HTMLScriptElement.supports('speculationrules')){var sr=document.createElement('script');sr.type='speculationrules';sr.textContent=JSON.stringify({prerender:[{where:{href_matches:'/o/*'},eagerness:'moderate'}],prefetch:[{where:{and:[{href_matches:'/*'},{not:{href_matches:'/c'}}]},eagerness:'conservative'}]});document.head.appendChild(sr)}}catch(x){}
var warm={};document.addEventListener('pointerdown',function(e){var t=e.target.closest&&e.target.closest('a[data-mo]');if(!t||warm[t.dataset.mo])return;warm[t.dataset.mo]=1;var l=document.createElement('link');l.rel='prefetch';l.href='/o/'+t.dataset.mo;document.head.appendChild(l)},{passive:true});
/* 1件ページ */
function detail(){var m=location.pathname.match(/^\/o\/([0-9a-f]{8})/);if(!m||document.body.dataset.mhd)return;var o=ID[m[1]];if(!o)return;document.body.dataset.mhd=1;
  var hd=document.querySelector('.head');
  if(hd){var h=hook(o);if(h){var p=document.createElement('p');p.className='mhk-o';p.textContent=h;var sub=hd.querySelector('.sub');hd.insertBefore(p,sub||null)}}
  var cap='<figcaption>写真：'+(o.cu?'<a href="'+esc(o.cu)+'" target="_blank" rel="noopener">'+esc(o.cr)+'</a>':esc(o.cr))+'</figcaption>';
  var ex=document.querySelector('.mph-o');if(ex){ex.querySelector('img').alt=o.n;ex.insertAdjacentHTML('beforeend',cap)}
  else if(o.im&&hd){var f=document.createElement('figure');f.className='mph-o';f.innerHTML='<img src="/assets/ph/'+o.im+'" alt="'+esc(o.n)+'" decoding="async" fetchpriority="high" class="mfade">'+cap;hd.parentNode.insertBefore(f,hd.nextSibling)}
  document.querySelectorAll('.big>div').forEach(function(b){var sp=b.querySelector('span');if(sp&&sp.textContent.trim()==='いまは'){var w=document.createElement('div');w.className='mnowl';b.appendChild(w);nowPill(w,o);setInterval(function(){nowPill(w,o)},60000)}});
  var ld=document.querySelector('.lead');
  if(o.ds&&ld){var x=document.createElement('div');x.className='mds';x.innerHTML='<span>どんな催し？</span><p>'+esc(o.ds)+'</p>';ld.parentNode.insertBefore(x,ld.nextSibling);ld.style.display='none'}
  var ac=document.querySelector('.act');if(ac){
    var fav=[];try{fav=JSON.parse(localStorage.getItem('tn_fav')||'[]')||[]}catch(e){}
    var on=fav.indexOf(o.u)>=0,cal='https://calendar.google.com/calendar/render?action=TEMPLATE&text='+encodeURIComponent(o.n)+'&dates='+o.s.replace(/-/g,'')+'/'+(function(){var d=new Date(o.e+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+1);return ymd(d).replace(/-/g,'')})()+'&details='+encodeURIComponent('公式：'+o.u+'\n'+location.href)+'&location='+encodeURIComponent((document.querySelector('.sub')||{}).textContent||'');
    var w=document.createElement('div');w.innerHTML='<a class="g mfav" href="#" role="button" aria-pressed="'+on+'">'+(on?'★ 行きたいに入っています':'☆ 行きたいに入れる')+'</a><a class="g" href="'+cal+'" target="_blank" rel="noopener">カレンダーに入れる</a><a class="g mshare" href="#" role="button">この催しを送る</a><div class="mshr"><a href="https://line.me/R/share?text='+encodeURIComponent(o.n+' '+location.href)+'" target="_blank" rel="noopener">LINE</a><a href="https://x.com/intent/post?text='+encodeURIComponent(o.n)+'&url='+encodeURIComponent(location.href)+'" target="_blank" rel="noopener">X</a><a href="#" class="mcp">URLをコピー</a></div>';
    var first=ac.querySelector('a.o');var ref=first?first.nextSibling:ac.firstChild;while(w.firstChild)ac.insertBefore(w.firstChild,ref);
    ac.addEventListener('click',function(e){var b=e.target.closest('a');if(!b)return;
      if(b.classList.contains('mfav')){e.preventDefault();var f=[];try{f=JSON.parse(localStorage.getItem('tn_fav')||'[]')||[]}catch(x){}var i=f.indexOf(o.u);if(i>=0)f.splice(i,1);else f.push(o.u);try{localStorage.setItem('tn_fav',JSON.stringify(f))}catch(x){}var y=i<0;b.setAttribute('aria-pressed',y);b.textContent=y?'★ 行きたいに入っています':'☆ 行きたいに入れる'}
      else if(b.classList.contains('mshare')){e.preventDefault();if(navigator.share){navigator.share({title:o.n,url:location.href}).catch(function(){})}else ac.querySelector('.mshr').classList.toggle('open')}
      else if(b.classList.contains('mcp')){e.preventDefault();try{navigator.clipboard.writeText(location.href).then(function(){b.textContent='コピーしました'})}catch(x){}}});
  }
}
function fin(i){if(i.classList.contains('in'))return;i.classList.add('in');var p=i.parentElement;if(p)p.classList.add('ld')}
function fade(){document.querySelectorAll('img.mfade:not(.in)').forEach(function(i){if(i.complete&&i.naturalWidth)fin(i)})}
/* 写真が読めたら出す（カードが作り直されて写真が写し替えられても拾えるよう、ページ全体で受ける） */
document.addEventListener('load',function(e){var i=e.target;if(i&&i.tagName==='IMG'&&i.classList.contains('mfade'))fin(i)},true);
document.addEventListener('error',function(e){var i=e.target;if(i&&i.tagName==='IMG'&&i.classList.contains('mfade'))fin(i)},true);
setInterval(fade,700);
var q;function run(){clearTimeout(q);q=setTimeout(function(){if(!READY)return;cards();detail();fade()},80)}
fetch('/assets/mihon.json?v='+(window.__mhv||2)).then(function(r){return r.json()}).then(function(j){D={};for(var x in j){D[x]=j[x];if(j[x].id)ID[j[x].id]=j[x]}READY=1;run();
  try{new MutationObserver(run).observe(document.body,{childList:true,subtree:true})}catch(e){}
  setInterval(function(){document.querySelectorAll('a.card .v2c').forEach(function(r){var a=r.closest('a.card'),t=a&&a.querySelector('.t');if(t)nowPill(r,find(t.textContent))})},60000)}).catch(function(){});
})();
