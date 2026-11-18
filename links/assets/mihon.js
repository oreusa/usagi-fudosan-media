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
'.mph-o{margin:0 0 14px}.mph-o img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:18px;background:#eee;box-shadow:0 14px 30px -18px rgba(40,30,20,.45)}'+
'.mph-o figcaption{font-size:10.5px;color:#9a928b;margin:7px 2px 0;line-height:1.5}.mph-o figcaption a{color:inherit}'+
'.head .mhk-o{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:14px;color:var(--pc,#6b625b);margin:10px 0 0;letter-spacing:.03em;line-height:1.6;position:relative}'+
'.mds{background:#F4F4F5;border-radius:4px;padding:16px 16px 15px;margin:14px 0 0}.mds span{display:block;font-size:10.5px;color:#8a837d;letter-spacing:.08em;margin-bottom:6px}.mds p{margin:0;font-size:14.5px;line-height:1.9;color:#2B2622}'+
'.act a.mfav[aria-pressed=true]{background:#FFF7E0;border-color:#E2B53B;color:#7A5A00}'+
'.mshr{display:none;gap:8px;margin-top:8px}.mshr.open{display:flex}.mshr a{flex:1;text-align:center;font-size:13px;padding:11px 0;border-radius:10px;border:1px solid #ddd;color:#2B2622;text-decoration:none;font-weight:700}'+
/* 夜：ページ全体が反転するので、写真だけ元に戻す（night.js の決まり） */
'html.night .cmb .ib.mph img,html.night .pr5 .ti.mph img,html.night .mph-o img{filter:invert(1) hue-rotate(180deg) brightness(.9)}'+
'html.night .mnow{background:#E7F4EC}';
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
function photo(box,o,big){if(box.classList.contains('mph'))return;box.classList.add('mph');var i=document.createElement('img');i.alt='';i.loading='lazy';i.decoding='async';i.src='/assets/ph/'+(big?'':'t/')+o.im;box.insertBefore(i,box.firstChild)}
/* カード（一覧・府県・イルミ・紅葉・泊まり・いまから・1件ページの「ほかのおでかけ」） */
function cards(){
  document.querySelectorAll('a.card,a.fc').forEach(function(a){
    var tt=a.querySelector(a.matches('a.fc')?'b':'.t');if(!tt)return;var o=find(tt.textContent);if(!o)return;
    var ib=a.querySelector('.cmb .ib');if(ib&&o.im)photo(ib,o);
    if(!a.dataset.mh){var h=hook(o);if(h){var s=document.createElement('span');s.className='mhk';s.textContent=h;tt.parentNode.insertBefore(s,tt)}a.dataset.mh=1}
    var row=a.querySelector('.v2c');if(row)nowPill(row,o);
    if(o.id&&a.matches('a.card'))a.dataset.mo=o.id;
  });
  document.querySelectorAll('.pr5 a').forEach(function(a){var b=a.querySelector('.tx b');if(!b)return;var o=find(b.textContent);if(!o)return;
    var ti=a.querySelector('.ti');if(ti&&o.im)photo(ti,o);if(o.id)a.dataset.mo=o.id});
}
/* カードを押すと、そのおでかけの1件ページ（写真・説明・公式ボタン）へ。☆・地図・近くの宿は今のまま */
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-mo]');if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey)return;
  if(e.target.closest('.wfav,button'))return;e.preventDefault();location.href='/o/'+a.dataset.mo},true);
/* 1件ページ */
function detail(){var m=location.pathname.match(/^\/o\/([0-9a-f]{8})/);if(!m||document.querySelector('.mph-o,.mds'))return;var o=ID[m[1]];if(!o)return;
  var hd=document.querySelector('.head');
  if(hd){var h=hook(o);if(h){var p=document.createElement('p');p.className='mhk-o';p.textContent=h;var sub=hd.querySelector('.sub');hd.insertBefore(p,sub||null)}}
  if(o.im&&hd){var f=document.createElement('figure');f.className='mph-o';f.innerHTML='<img src="/assets/ph/'+o.im+'" alt="'+esc(o.n)+'" decoding="async"><figcaption>写真：'+(o.cu?'<a href="'+esc(o.cu)+'" target="_blank" rel="noopener">'+esc(o.cr)+'</a>':esc(o.cr))+'</figcaption>';hd.parentNode.insertBefore(f,hd.nextSibling)}
  document.querySelectorAll('.big>div').forEach(function(b){var sp=b.querySelector('span');if(sp&&sp.textContent.trim()==='いまは'){var w=document.createElement('div');w.className='mnowl';b.appendChild(w);nowPill(w,o);setInterval(function(){nowPill(w,o)},60000)}});
  var ld=document.querySelector('.lead');
  if(o.ds&&ld){var x=document.createElement('div');x.className='mds';x.innerHTML='<span>どんな催し？</span><p>'+esc(o.ds)+'</p>';ld.parentNode.insertBefore(x,ld.nextSibling)}
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
var q;function run(){clearTimeout(q);q=setTimeout(function(){if(!READY)return;cards();detail()},80)}
fetch('/assets/mihon.json?v=1').then(function(r){return r.json()}).then(function(j){D={};for(var x in j){D[x]=j[x];if(j[x].id)ID[j[x].id]=j[x]}READY=1;run();
  try{new MutationObserver(run).observe(document.body,{childList:true,subtree:true})}catch(e){}
  setInterval(function(){document.querySelectorAll('a.card .v2c').forEach(function(r){var a=r.closest('a.card'),t=a&&a.querySelector('.t');if(t)nowPill(r,find(t.textContent))})},60000)}).catch(function(){});
})();
