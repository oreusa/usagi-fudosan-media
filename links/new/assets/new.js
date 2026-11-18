/* 11/18 新しい関西おでかけ（/new/）の動き：昼夜・♡・一覧のしぼりこみ・送る・行きたいページ */
(function(){
var root=document.documentElement,K='odk-saved',saved={};
try{saved=JSON.parse(localStorage.getItem(K)||'{}')||{}}catch(e){}
function store(){try{localStorage.setItem(K,JSON.stringify(saved))}catch(e){}var n=Object.keys(saved).length;document.querySelectorAll('.cnt').forEach(function(c){c.textContent=n;c.hidden=!n})}
function isDark(){var t=root.getAttribute('data-theme');return t?t=='dark':matchMedia('(prefers-color-scheme: dark)').matches}
function logo(){document.querySelectorAll('img[data-logo]').forEach(function(i){i.src=isDark()?'/new/img/logo-night.png':'/new/img/logo.png'})}
try{var th=localStorage.getItem('odk-theme');if(th)root.setAttribute('data-theme',th)}catch(e){}
var tb=document.getElementById('theme');if(tb)tb.addEventListener('click',function(){var t=isDark()?'light':'dark';root.setAttribute('data-theme',t);try{localStorage.setItem('odk-theme',t)}catch(e){}logo()});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',logo);logo();
function paint(){document.querySelectorAll('[data-heart]').forEach(function(b){b.setAttribute('aria-pressed',!!saved[b.getAttribute('data-heart')])})}
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-heart]');if(b){e.preventDefault();var id=b.getAttribute('data-heart');if(saved[id])delete saved[id];else{saved[id]=Date.now();b.classList.remove('pop');void b.offsetWidth;b.classList.add('pop')}store();paint();
/* いま開いている（時間が分かるおでかけだけ・日本の時刻） */
function nowJP(){var d=new Date(Date.now()+(d0=new Date().getTimezoneOffset()+540)*6e4);return d}var d0;
function openNow(){var n=nowJP(),m=n.getHours()*60+n.getMinutes(),ymd=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
  document.querySelectorAll('[data-h]').forEach(function(c){var h=c.getAttribute('data-h'),el=c.querySelector('.now');if(!h||!el)return;var d=c.dataset;if(!(d.s<=ymd&&d.e>=ymd)){el.hidden=true;return}
    var x=h.split('-').map(function(t){var a=t.split(':');return a[0]*60+ +a[1]});var night=x[0]>=15*60,txt='',cls='';
    if(m>=x[0]&&m<x[1]){var left=x[1]-m;txt=night?'いまライトアップ中':(left<=120?'あと'+(left>=60?Math.floor(left/60)+'時間':'')+(left%60?left%60+'分':'')+'で閉まる':'いま開いています');cls='on'}
    else if(m<x[0]&&x[0]-m<=180){txt=(night?'今夜':'きょう')+h.split('-')[0]+'から';cls='soon'}
    if(txt){el.hidden=false;el.textContent=txt;el.className='now '+cls}else el.hidden=true})}
openNow();setInterval(openNow,60000);if(window.__savedView)window.__savedView();return}
  var s=e.target.closest('[data-share]');if(s){e.preventDefault();var d={title:document.title,text:s.getAttribute('data-share'),url:location.href};if(navigator.share){navigator.share(d).catch(function(){})}else{var x=document.getElementById('shr');if(x)x.classList.toggle('open')}return}
  var c=e.target.closest('[data-copy]');if(c){e.preventDefault();var t=c.getAttribute('data-copy')+' '+location.href;try{navigator.clipboard.writeText(t).then(function(){c.textContent='コピーしました'})}catch(er){}return}
  var j=e.target.closest('a[href^="#"]');if(j&&j.getAttribute('href').length>1){var el=document.getElementById(j.getAttribute('href').slice(1));if(el){e.preventDefault();el.scrollIntoView({behavior:'smooth'})}}
});
store();paint();
/* いま開いている（時間が分かるおでかけだけ・日本の時刻） */
function nowJP(){var d=new Date(Date.now()+(d0=new Date().getTimezoneOffset()+540)*6e4);return d}var d0;
function openNow(){var n=nowJP(),m=n.getHours()*60+n.getMinutes(),ymd=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
  document.querySelectorAll('[data-h]').forEach(function(c){var h=c.getAttribute('data-h'),el=c.querySelector('.now');if(!h||!el)return;var d=c.dataset;if(!(d.s<=ymd&&d.e>=ymd)){el.hidden=true;return}
    var x=h.split('-').map(function(t){var a=t.split(':');return a[0]*60+ +a[1]});var night=x[0]>=15*60,txt='',cls='';
    if(m>=x[0]&&m<x[1]){var left=x[1]-m;txt=night?'いまライトアップ中':(left<=120?'あと'+(left>=60?Math.floor(left/60)+'時間':'')+(left%60?left%60+'分':'')+'で閉まる':'いま開いています');cls='on'}
    else if(m<x[0]&&x[0]-m<=180){txt=(night?'今夜':'きょう')+h.split('-')[0]+'から';cls='soon'}
    if(txt){el.hidden=false;el.textContent=txt;el.className='now '+cls}else el.hidden=true})}
openNow();setInterval(openNow,60000);
/* 下に出る「公式・行きたい」の帯（くわしいページ） */
var sc=document.querySelector('.sticky-cta'),ac=document.querySelector('.acts');
if(sc&&ac&&'IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(x){sc.classList.toggle('on',!x.isIntersecting&&x.boundingClientRect.top<0)})}).observe(ac)}
/* 一覧のしぼりこみ */
var DIST={};function hav(a,b,c,d){var r=Math.PI/180,x=Math.sin((c-a)*r/2),y=Math.sin((d-b)*r/2);return 12742*Math.asin(Math.sqrt(x*x+Math.cos(a*r)*Math.cos(c*r)*y*y))}
function alertless(m){var nb=document.getElementById('nearb');if(nb)nb.textContent=m}
var L=document.getElementById('list');
if(L){
  var cards=[].slice.call(L.querySelectorAll('.cd')),q=new URLSearchParams(location.search),S={p:q.get('p')||'',g:q.get('g')||'',w:q.get('w')||'',free:q.get('free')||'',in:q.get('in')||'',q:q.get('q')||'',sort:q.get('sort')||'soon',n:24};
  var T=L.getAttribute('data-today'),WE=(L.getAttribute('data-we')||'').split(','),M30=L.getAttribute('data-m30'),E7=L.getAttribute('data-e7');
  if(q.get('w')=='free'){S.w='';S.free='1'}
  var inp=document.getElementById('q');if(inp)inp.value=S.q;
  function ok(c){var d=c.dataset;
    if(S.p&&d.p!=S.p)return false;if(S.g&&d.g!=S.g)return false;if(S.free&&d.free!='1')return false;if(S.in&&d.in!='1')return false;
    if(S.w=='today'&&!(d.s<=T&&d.today=='1'))return false;if(S.w=='we'&&d.we!='1')return false;if(S.w=='month'&&!(d.s<=M30))return false;if(S.w=='tomorrow'&&d.tm!='1')return false;if(S.w=='end'&&!(d.s<=T&&d.e<=E7))return false;
    if(S.q){var h=d.q;if(S.q.split(/\s+/).some(function(w){return w&&h.indexOf(w)<0}))return false}return true}
  function key(c){var d=c.dataset;if(S.sort=='near'){var k=DIST[d.ll];return k==null?'9999999':(''+Math.round(k*10+1e6))}return S.sort=='end'?d.e:S.sort=='new'?(9e9-(+d.s.replace(/-/g,'')))+'':((d.s<=T?'0':'1')+(d.s<=T?d.e:d.s))}
  function run(push){
    var r=cards.filter(ok);r.sort(function(a,b){var x=key(a),y=key(b);return x<y?-1:x>y?1:(b.dataset.img-a.dataset.img)});
    cards.forEach(function(c){c.hidden=true});r.forEach(function(c,i){L.appendChild(c);c.hidden=i>=S.n});
    document.getElementById('n').textContent=r.length;
    var mo=document.getElementById('more');mo.hidden=r.length<=S.n;mo.textContent='あと'+(r.length-S.n)+'件を見る';
    document.getElementById('empty').hidden=!!r.length;
    document.querySelectorAll('[data-set]').forEach(function(b){var k=b.getAttribute('data-set');b.setAttribute('aria-pressed',(S[k]||'')==b.getAttribute('data-v'))});
    var h1=document.getElementById('h1');if(h1)h1.textContent=(S.p||'関西')+'のおでかけ'+(S.g?'・'+S.g:'')+(S.free?'・無料':'')+(S.in?'・雨でも行ける':'');
    if(push){var u=new URLSearchParams();['p','g','w','free','in','q','sort'].forEach(function(k){if(S[k]&&!(k=='sort'&&S[k]=='soon'))u.set(k,S[k])});history.replaceState(null,'',location.pathname+(u+''?'?'+u:''))}
  }
  document.addEventListener('click',function(e){var b=e.target.closest('[data-set]');if(!b)return;var k=b.getAttribute('data-set'),v=b.getAttribute('data-v');S[k]=(S[k]==v&&k!='p'&&k!='w')?'':v;S.n=24;run(1)});
  document.getElementById('more').addEventListener('click',function(){S.n+=24;run()});
  var so=document.getElementById('sort');so.value=S.sort;so.addEventListener('change',function(){if(so.value=='near'){near()}else{S.sort=so.value;run(1)}});
  var nb=document.getElementById('nearb');if(nb)nb.addEventListener('click',near);
  function near(){if(!navigator.geolocation){alertless('この端末では場所が使えません');return}
    nb&&(nb.textContent='場所を確かめています…');
    navigator.geolocation.getCurrentPosition(function(pos){var a=pos.coords.latitude,b=pos.coords.longitude;
      cards.forEach(function(c){var ll=c.dataset.ll;if(!ll)return;var x=ll.split(',');var km=hav(a,b,+x[0],+x[1]);DIST[ll]=km;var s=c.querySelector('.dist');if(s){s.hidden=false;s.textContent='約'+(km<10?km.toFixed(1):Math.round(km))+'km'}});
      S.sort='near';so.value='near';run(1);nb&&(nb.textContent='近い順に並べました');},
      function(){nb&&(nb.textContent='場所が使えませんでした（設定で許可すると使えます）')},{timeout:10000,maximumAge:600000})}
  if(inp){var f=inp.closest('form');f.addEventListener('submit',function(e){e.preventDefault();S.q=inp.value.trim();S.n=24;run(1);inp.blur()})}
  run();
}
/* 行きたいページ */
var SV=document.getElementById('saved');
if(SV){window.__savedView=function(){fetch('/new/cards.json').then(function(r){return r.json()}).then(function(all){
  var ids=Object.keys(saved).sort(function(a,b){return saved[b]-saved[a]});var m={};all.forEach(function(c){m[c.id]=c});
  var r=ids.map(function(i){return m[i]}).filter(Boolean);
  SV.innerHTML=r.map(function(c){return c.html}).join('');document.getElementById('sempty').hidden=!!r.length;paint()})};window.__savedView()}
if('serviceWorker' in navigator){}
})();
