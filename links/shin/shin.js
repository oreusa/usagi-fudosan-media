/* 新しいHP（11/19）：関西おでかけ。
   役目＝行きたい所がすぐ見つかる。こだわり＝ストーリー・写真・扇のカード・回る光・昼の日差し・夜の星。 */
(function(){
"use strict";
var D=JSON.parse(document.getElementById("d").textContent),H=document.documentElement,app=document.getElementById("app");
var RM=matchMedia("(prefers-reduced-motion:reduce)").matches;
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
function el(h){var t=document.createElement("template");t.innerHTML=h.trim();return t.content.firstChild}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}

/* ---- 日付（日本の今日） ---- */
var now=new Date(Date.now()+9*36e5),TD=now.toISOString().slice(0,10);
function dd(s){return new Date(s+"T00:00:00Z")}
function diff(a,b){return Math.round((dd(b)-dd(a))/864e5)}
var WD="日月火水木金土";
function md(s){var d=dd(s);return (d.getUTCMonth()+1)+"/"+d.getUTCDate()+"（"+WD[d.getUTCDay()]+"）"}
var dow=dd(TD).getUTCDay(),SAT=new Date(dd(TD).getTime()+((6-dow+7)%7-(dow===0?6:0))*864e5).toISOString().slice(0,10),SUN=new Date(dd(SAT).getTime()+864e5).toISOString().slice(0,10);
if(dow===0){SAT=TD;SUN=TD}

/* ---- 種類（カードの絵と同じ決め方） ---- */
var G={art:["ART","#3B5BA5","#EEF1F8","アート・展示"],light:["LIGHT","#B7862A","#F8F2E6","光・イルミ"],koyo:["KOYO","#C0532B","#F9EEEA","紅葉"],flower:["FLOWER","#C2557A","#F9EDF2","花"],fes:["MATSURI","#B23A2E","#F8ECEB","まつり"],quest:["NAZOTOKI","#5B4B8A","#F0EEF6","謎とき"],play:["PLAY","#2E8B6E","#EAF4F0","あそぶ"],spot:["SPOT","#2F7D9A","#EAF3F6","スポット"],food:["FOOD","#C9702A","#FAF0E7","グルメ"],animal:["ANIMAL","#6F7F33","#F1F3E8","いきもの"],xmas:["XMAS","#2F7A4F","#EAF4EE","クリスマス"],hallo:["HALLOWEEN","#B45F1F","#FAEFE6","ハロウィン"],shop:["MARKET","#8A6A3F","#F5F0E8","マーケット"],hatsu:["HATSUMODE","#A23B3B","#F7ECEC","初詣"]};
var PREF=["大阪","京都","兵庫","奈良","滋賀","和歌山"];
var IT=D.items.filter(function(x){return x.e>=TD}).map(function(x,i){
  x.i=i;x.st=x.s<=TD?"now":"up";x.left=diff(TD,x.e);x.g=G[x.k]||G.spot;return x});
var BYI={};IT.forEach(function(x){BYI[x.i]=x});

/* ---- ぼかし色（写真が出る前の色） ---- */
function avg(b){try{var h=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)}),hd=h[0]|h[1]<<8|h[2]<<16,l=(hd&63)/63,p=((hd>>6)&63)/31.5-1,q=((hd>>12)&63)/31.5-1,bb=l-2/3*p,r=(3*l-bb+q)/2,g=r-q;
  var f=function(v){return Math.round(255*Math.max(0,Math.min(1,v)))};return "rgb("+f(r)+","+f(g)+","+f(bb)+")"}catch(e){return ""}}
function img(x){return "/assets/ph/"+x.im}
function tile(x){return '<div class="tile" style="--gc:'+x.g[1]+';--gt:'+x.g[2]+'"><svg viewBox="0 0 24 24">'+(D.icons[x.k]||D.icons.spot||"")+'</svg><b>'+x.g[0]+'</b></div>'}
function lt(x){if(x.st==="up"){var n=diff(TD,x.s);return '<span class="lt">'+(n<=1?"あしたから":n+"日後から")+'</span>'}
  if(x.left===0)return '<span class="lt">きょうまで</span>';if(x.left<=7)return '<span class="lt">あと'+x.left+'日</span>';return '<span class="lt now">開催中</span>'}
function when(x){return x.st==="up"?md(x.s)+"から":md(x.e)+"まで"}

/* ---- 状態（URL に残す：戻る・送るで同じ画面） ---- */
var Q=new URLSearchParams(location.search),S={p:Q.get("p")||"",w:Q.get("w")||"now",g:Q.get("g")||"",n:24};
function saveQ(){var u=new URLSearchParams(location.search);["p","w","g"].forEach(function(k){if(S[k]&&!(k==="w"&&S[k]==="now"))u.set(k,S[k]);else u.delete(k)});
  history.replaceState(history.state,"",location.pathname+(u.toString()?"?"+u:""))}
function pick(){return IT.filter(function(x){
  if(S.p&&x.p!==S.p)return false;if(S.g&&x.k!==S.g)return false;
  if(S.w==="now")return x.st==="now";if(S.w==="we")return x.s<=SUN&&x.e>=SAT;return x.st==="up"}).sort(function(a,b){
  if(S.w==="up")return a.s<b.s?-1:a.s>b.s?1:0;
  var pa=a.im?0:1,pb=b.im?0:1;if(pa!==pb)return pa-pb;return a.e<b.e?-1:a.e>b.e?1:0})}

/* ---- 画面を組む ---- */
var I={sun:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg>',
 moon:'<svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>',
 now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',
 we:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',
 map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
 inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
var nNow=IT.filter(function(x){return x.st==="now"}).length;
app.innerHTML='<div class="wrap">'+
 '<header class="top"><a class="brand" href="/" aria-label="トップへ"><img id="logo" src="/assets/logo-s.png?v=2" alt="TOWN NOTE"><b>TOWN NOTE</b></a>'+
 '<button class="tg" id="tg" aria-label="昼と夜を切り替え">'+I.moon+'<span>夜</span></button></header>'+
 '<section class="hero"><div class="kick">Kansai · Odekake</div><h1 class="h1">関西の、<em>今週どこ行く？</em></h1>'+
 '<div class="live"><i class="dot"></i>いま開催中 <b data-n="'+nNow+'">0</b>件<span style="margin-left:auto;font-size:11.5px;color:var(--mut)">'+md(TD)+' 更新</span></div></section>'+
 '<div class="st" id="st"></div>'+
 '<div class="sec"><h2>今週の顔<i>This week</i></h2><small>横にめくる</small></div></div>'+
 '<div class="fan" id="fan"></div>'+
 '<div class="wrap"><div id="sent"></div><div class="bar" id="bar"><div class="seg" id="seg"><i class="pill"></i></div><div class="chips" id="chips"></div></div>'+
 '<div class="cnt"><h3 id="ch"></h3><small id="cs"></small></div><div class="grid" id="grid"></div><div id="mr"></div>'+
 '<footer class="ft">情報は各公式サイトで確かめてから出かけてください。写真の撮影者は各ページに書いています（ウィキメディア・コモンズ ほか）。<br>券・宿のリンクの一部は広告です。<br><a href="/">TOWN NOTE トップ</a>　<a href="/privacy">プライバシー</a></footer></div>'+
 '<nav class="nav" id="nav" aria-label="すぐ移動"><button data-w="now" class="cur">'+I.now+'<span>開催中</span></button><button data-w="we">'+I.we+'<span>今週末</span></button><a href="/odekake?v2t=map">'+I.map+'<span>地図</span></a><a href="/tomari">'+I.inn+'<span>泊まり</span></a><button class="mn" id="mnb" aria-label="メニュー"><em></em><span>MENU</span></button></nav>'+
 '<div class="sh" id="sh" aria-hidden="true"><div class="bk"></div><div class="pn" role="dialog" aria-modal="true"><div class="grab"><i></i></div><button class="x" aria-label="閉じる">×</button><div id="shc"></div></div></div>'+
 '<div class="sv" id="sv"><div class="bars"></div><div class="hd"><img src="/assets/logo-s.png?v=2" alt=""><span></span><button aria-label="閉じる">×</button></div><div class="fr"></div><div class="tx"></div><i class="tp l"></i><i class="tp r"></i></div>'+
 '<div class="mu" id="mu"><div class="bk"></div><div class="pn"><div class="k">Odekake</div><ol>'+
 [["関西おでかけ","/shin/odekake",1],["イルミネーション","/illumination"],["紅葉","/koyo"],["いまから行ける","/ima"],["泊まり","/tomari"],["初詣","/hatsumode"]].map(function(m,i){return '<li><a href="'+m[1]+'"'+(m[2]?' class="here"':'')+' style="transition-delay:'+(60+i*40)+'ms"><small>0'+(i+1)+'</small>'+m[0]+'</a></li>'}).join("")+
 '</ol><div class="rel"><a href="/fudosan-list">家と土地</a><a href="/okaimono">おかいもの</a><a href="/">トップへ</a></div></div></div>';

/* 数え上がり */
function countUp(b){var n=+b.dataset.n,t0=performance.now();if(RM){b.textContent=n;return}
  (function f(t){var k=Math.min(1,(t-t0)/900),e=1-Math.pow(1-k,3);b.textContent=Math.round(n*e);if(k<1)requestAnimationFrame(f)})(t0)}
$$("[data-n]").forEach(countUp);

/* ---- ストーリー ---- */
var ST=[["今週末",function(x){return x.s<=SUN&&x.e>=SAT}],["まもなく終了",function(x){return x.st==="now"&&x.left<=10}],["夜の光",function(x){return x.k==="light"}],["紅葉",function(x){return x.k==="koyo"}],["アート",function(x){return x.k==="art"}],["家族で",function(x){return x.k==="play"||x.k==="animal"}],["無料",function(x){return x.f}],["もうすぐ",function(x){return x.st==="up"&&diff(TD,x.s)<=21}]]
 .map(function(s){var l=IT.filter(s[1]).sort(function(a,b){return (a.im?0:1)-(b.im?0:1)}).slice(0,10);return {t:s[0],l:l}}).filter(function(s){return s.l.length>=2});
$("#st").innerHTML=ST.map(function(s,i){var c=s.l[0];return '<button data-s="'+i+'"><span class="rg">'+(c.im?'<img src="'+img(c)+'" alt="" loading="lazy">':'<span class="ph" style="display:block"></span>')+'</span><span>'+esc(s.t)+'</span></button>'}).join("");
var sv=$("#sv"),svS=null,svI=0,svA=null;
function svShow(){var s=ST[svS],x=s.l[svI];$(".hd span",sv).textContent=s.t+"　"+(svI+1)+"/"+s.l.length;
  $(".bars",sv).innerHTML=s.l.map(function(_,i){return '<i><b style="transform:scaleX('+(i<svI?1:0)+')"></b></i>'}).join("");
  $(".fr",sv).innerHTML=x.im?'<img src="'+img(x)+'" alt="">':tile(x);
  $(".tx",sv).innerHTML='<span class="tag" style="--gc:'+x.g[1]+'">'+x.g[0]+'</span><h3>'+esc(x.t)+'</h3><p>'+esc(x.hk||x.v||x.a)+'　'+when(x)+'</p><button data-i="'+x.i+'">くわしく見る</button>';
  try{var se=JSON.parse(localStorage.getItem("hx_seen")||"{}");se[x.t]=TD;localStorage.setItem("hx_seen",JSON.stringify(se))}catch(e){}
  if(svA)svA.cancel();var b=$$(".bars b",sv)[svI];svA=b.animate([{transform:"scaleX(0)"},{transform:"scaleX(1)"}],{duration:5200,fill:"forwards"});svA.onfinish=function(){svGo(1)}}
function svGo(d){var n=svI+d;if(n<0)n=0;if(n>=ST[svS].l.length){svClose();return}svI=n;svShow()}
function svOpen(i){svS=i;svI=0;sv.classList.add("op");document.body.style.overflow="hidden";svShow()}
function svClose(){if(svA)svA.cancel();sv.classList.remove("op");document.body.style.overflow=""}
$("#st").addEventListener("click",function(e){var b=e.target.closest("button");if(b)svOpen(+b.dataset.s)});
$(".tp.l",sv).onclick=function(){svGo(-1)};$(".tp.r",sv).onclick=function(){svGo(1)};$(".hd button",sv).onclick=svClose;
$(".tx",sv).addEventListener("click",function(e){var b=e.target.closest("button[data-i]");if(b){svClose();openSheet(BYI[b.dataset.i])}});
var sy0=null;sv.addEventListener("touchstart",function(e){sy0=e.touches[0].clientY;if(svA)svA.pause()},{passive:true});
sv.addEventListener("touchend",function(e){var dy=e.changedTouches[0].clientY-(sy0||0);if(dy>90)svClose();else if(svA)svA.play()},{passive:true});

/* ---- 今週の顔（扇） ---- */
var seed=+TD.replace(/-/g,"");
var FAN=IT.filter(function(x){return x.im&&x.s<=SUN&&x.e>=TD}).sort(function(a,b){return (b.hk?1:0)-(a.hk?1:0)||((a.i*7919+seed)%97)-((b.i*7919+seed)%97)}).slice(0,8);
var fan=$("#fan");
fan.innerHTML='<i class="pad"></i>'+FAN.map(function(x){return '<a class="fc" href="#" data-i="'+x.i+'"><span class="in" style="background-color:'+avg(x.th)+'"><img src="'+img(x)+'" alt="" loading="lazy" decoding="async"><span class="tag" style="--gc:'+x.g[1]+'">'+x.g[0]+'</span><span class="cap"><b>'+esc(x.t)+'</b><span>'+esc(x.p)+'・'+when(x)+'</span></span></span></a>'}).join("")+'<i class="pad"></i>';
var fcs=$$(".fc",fan),fq=0;
function fanTick(){fq=0;var c=fan.scrollLeft+fan.clientWidth/2;fcs.forEach(function(f){var m=f.offsetLeft+f.offsetWidth/2,o=(m-c)/f.offsetWidth;o=Math.max(-2,Math.min(2,o));
  f.style.transform="translateX("+(-o*14)+"%) rotateY("+(-o*24)+"deg) translateZ("+(-Math.abs(o)*90)+"px)";f.style.zIndex=10-Math.round(Math.abs(o)*3);f.style.opacity=1-Math.min(.45,Math.abs(o)*.25)})}
fan.addEventListener("scroll",function(){if(!fq)fq=requestAnimationFrame(fanTick)},{passive:true});
fanTick();addEventListener("resize",fanTick);
fan.addEventListener("click",function(e){var a=e.target.closest(".fc");if(!a)return;e.preventDefault();openSheet(BYI[a.dataset.i],$(".in",a))});

/* ---- 絞り込み ---- */
var seg=$("#seg"),pill=$(".pill",seg);
seg.insertAdjacentHTML("beforeend",[["","関西"]].concat(PREF.map(function(p){return [p,p]})).map(function(p){return '<button data-p="'+p[0]+'">'+p[1]+'</button>'}).join(""));
function movePill(){var b=$("button.on",seg);if(!b)return;pill.style.width=b.offsetWidth+"px";pill.style.transform="translateX("+(b.offsetLeft-4)+"px)";pill.style.left="4px"}
function kinds(){var c={};IT.forEach(function(x){if((!S.p||x.p===S.p))c[x.k]=(c[x.k]||0)+1});return Object.keys(G).filter(function(k){return c[k]})}
function drawChips(){$("#chips").innerHTML='<button class="chip'+(S.g?"":" on")+'" data-g="">すべて</button>'+kinds().map(function(k){return '<button class="chip'+(S.g===k?" on":"")+'" data-g="'+k+'" style="--c:'+G[k][1]+'"><i></i>'+G[k][3]+'</button>'}).join("")}
seg.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;S.p=b.dataset.p;S.n=24;sync();go(true)});
$("#chips").addEventListener("click",function(e){var b=e.target.closest(".chip");if(!b)return;S.g=b.dataset.g;S.n=24;sync();go(true)});
function sync(){$$("button",seg).forEach(function(b){b.classList.toggle("on",b.dataset.p===S.p)});movePill();
  var on=$("button.on",seg);if(on&&seg.scrollWidth>seg.clientWidth)seg.scrollTo({left:on.offsetLeft-seg.clientWidth/2+on.offsetWidth/2,behavior:"smooth"});
  drawChips();$$("#nav [data-w]").forEach(function(b){b.classList.toggle("cur",b.dataset.w===S.w)});saveQ()}

/* カード。並びが変わる時は、前の場所から滑って動く */
var cache={};
function card(x){if(cache[x.i])return cache[x.i];
  var a=el('<a class="cd" href="'+(x.o?"/o/"+x.o:esc(x.u))+'" data-i="'+x.i+'" style="--gc:'+x.g[1]+'"><div class="im" style="background-color:'+(x.th?avg(x.th):x.g[2])+'">'+(x.im?'<img alt="" loading="lazy" decoding="async" src="'+img(x)+'">':tile(x))+'</div>'+
   '<div class="lb"><span class="g">'+x.g[0]+'</span><span>'+esc(x.p)+'</span>'+lt(x)+'</div><h4>'+esc(x.t)+'</h4><div class="dt">'+when(x)+'</div><div class="vn">'+esc(x.v||x.a)+'</div></a>');
  var im=$("img",a);if(im){if(im.complete)im.classList.add("ld");else im.onload=function(){im.classList.add("ld")}}
  return cache[x.i]=a}
var grid=$("#grid"),first=true;
function go(anim){var L=pick(),show=L.slice(0,S.n),pr=S.p||"関西",wl={now:"開催中",we:"今週末",up:"これから"}[S.w];
  $("#ch").innerHTML=esc(pr)+"の"+wl+" <b data-n='"+L.length+"'>"+L.length+"</b>件";$("#cs").textContent=S.g?G[S.g][3]:(S.w==="we"?md(SAT)+"・"+md(SUN).replace(/（.）/,""):"");
  if(anim&&!first)countUp($("#ch b"));
  var old={};if(anim&&!RM)$$(".cd",grid).forEach(function(c){old[c.dataset.i]=c.getBoundingClientRect()});
  var frag=document.createDocumentFragment();show.forEach(function(x){frag.appendChild(card(x))});grid.replaceChildren(frag);
  if(!L.length)grid.innerHTML='<div class="none" style="grid-column:1/-1">この条件のおでかけは、いまはありません</div>';
  $("#mr").innerHTML=L.length>S.n?'<button class="more">もっと見る（残り'+(L.length-S.n)+'件）</button>':"";
  if(anim&&!RM)$$(".cd",grid).forEach(function(c,k){var o=old[c.dataset.i],n=c.getBoundingClientRect();
    if(o){var dx=o.left-n.left,dy=o.top-n.top;if(dx||dy)c.animate([{transform:"translate("+dx+"px,"+dy+"px)"},{transform:"none"}],{duration:480,easing:"cubic-bezier(.2,.9,.25,1)"})}
    else if(n.top<innerHeight+40)c.animate([{opacity:0,transform:"translateY(14px) scale(.98)"},{opacity:1,transform:"none"}],{duration:420,delay:Math.min(k,8)*35,easing:"cubic-bezier(.2,.9,.25,1)",fill:"backwards"})});
  if(anim){var b=$("#bar");var top=$("#sent").getBoundingClientRect().top+scrollY;if(scrollY>top)scrollTo({top:top,behavior:"smooth"})}
  first=false}
$("#mr").addEventListener("click",function(e){if(e.target.closest(".more")){S.n+=24;go(false)}});
sync();go(false);requestAnimationFrame(movePill);addEventListener("resize",movePill);
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(movePill);

/* 上に貼り付いたら線を出す */
new IntersectionObserver(function(e){$("#bar").classList.toggle("stuck",!e[0].isIntersecting)}).observe($("#sent"));

/* 触れたカードに光が当たる（昼のこだわり） */
function lit(e){var c=e.target.closest&&e.target.closest(".cd");if(!c)return;var r=$(".im",c).getBoundingClientRect();c.style.setProperty("--x",(e.clientX-r.left)+"px");c.style.setProperty("--y",(e.clientY-r.top)+"px");c.classList.add("lit");clearTimeout(c._t);c._t=setTimeout(function(){c.classList.remove("lit")},700)}
grid.addEventListener("pointerdown",lit);grid.addEventListener("pointermove",function(e){if(e.pointerType==="mouse")lit(e)});

/* ---- 1件の板 ---- */
var sh=$("#sh"),shc=$("#shc"),shOpen=false;
function fill(x){var tot=Math.max(1,diff(x.s,x.e)),gone=Math.max(0,Math.min(tot,diff(x.s,TD))),pc=x.st==="now"?gone/tot:0;
  var mq=encodeURIComponent((x.v||"")+" "+(x.a||x.p));
  shc.innerHTML='<div class="pim" style="background-color:'+(x.th?avg(x.th):x.g[2])+'">'+(x.im?'<img src="'+img(x)+'" alt="">':tile(x))+'</div><div class="bd" style="--gc:'+x.g[1]+'">'+
   '<div class="lb"><span class="g">'+x.g[0]+'</span><span>'+esc(x.p)+'・'+esc(x.a)+'</span></div><h2>'+esc(x.t)+'</h2>'+(x.hk?'<p class="hk">'+esc(x.hk)+'</p>':"")+
   '<div class="per"><div class="row"><span>'+md(x.s)+'</span><span>'+md(x.e)+'</span></div><div class="tr"><i style="background:'+x.g[1]+'"></i>'+(x.st==="now"?'<b style="left:'+(pc*100)+'%;border-color:'+x.g[1]+'"></b>':"")+'</div>'+
   '<div class="big">'+(x.st==="up"?"あと"+diff(TD,x.s)+"日で始まります":x.left===0?"きょうまで":"終わりまで あと"+x.left+"日")+'</div></div>'+
   '<dl class="kv">'+(x.v?'<dt>会場</dt><dd>'+esc(x.v)+'</dd>':"")+'<dt>場所</dt><dd>'+esc(x.a||x.p)+'</dd>'+(x.h?'<dt>時間</dt><dd>'+esc(x.h)+'</dd>':"")+(x.f?'<dt>料金</dt><dd>無料</dd>':"")+'</dl>'+
   (x.ds?'<p class="ds">'+esc(x.ds)+'</p>':"")+
   '<div class="acts"><a class="pr" href="'+esc(x.u)+'" target="_blank" rel="noopener">公式サイトで確かめる</a><a href="https://www.google.com/maps/search/?api=1&query='+mq+'" target="_blank" rel="noopener">地図で開く</a>'+(x.o?'<a href="/o/'+x.o+'">くわしいページ</a>':'<button data-sh="1">送る</button>')+'</div>'+
   (x.cr?'<p class="cr">写真：'+(x.cu?'<a href="'+esc(x.cu)+'" target="_blank" rel="noopener">'+esc(x.cr)+'</a>':esc(x.cr))+'</p>':"")+'</div>';
  $(".pn",sh).scrollTop=0;
  setTimeout(function(){var t=$(".tr i",shc);if(t)t.style.transform="scaleX("+pc+")"},30)}
function openSheet(x,from){if(!x)return;var go2=function(){fill(x);sh.classList.add("op");sh.setAttribute("aria-hidden","false");document.body.style.overflow="hidden"};
  if(!shOpen)history.pushState({sh:1},"");shOpen=true;
  if(from&&document.startViewTransition&&!RM){from.style.viewTransitionName="ph";sh.classList.add("nov");
    var t=document.startViewTransition(function(){from.style.viewTransitionName="";go2();var p=$(".pim",shc);if(p)p.style.viewTransitionName="ph"});
    t.finished.then(function(){var p=$(".pim",shc);if(p)p.style.viewTransitionName="";sh.classList.remove("nov")})}
  else go2()}
function closeSheet(back){if(!shOpen)return;shOpen=false;sh.classList.remove("op");sh.setAttribute("aria-hidden","true");document.body.style.overflow="";if(back!==false&&history.state&&history.state.sh)history.back()}
addEventListener("popstate",function(){if(shOpen)closeSheet(false)});
$(".bk",sh).onclick=function(){closeSheet()};$(".x",sh).onclick=function(){closeSheet()};
grid.addEventListener("click",function(e){var a=e.target.closest(".cd");if(!a||e.metaKey||e.ctrlKey)return;e.preventDefault();openSheet(BYI[a.dataset.i],$(".im",a))});
shc.addEventListener("click",function(e){if(e.target.closest("[data-sh]")){var x=null;try{navigator.share({title:document.title,url:location.href})}catch(_){}}});
/* 下に引いて閉じる */
(function(){var pn=$(".pn",sh),y0=null,dy=0;pn.addEventListener("touchstart",function(e){if(pn.scrollTop<=0){y0=e.touches[0].clientY;dy=0}else y0=null},{passive:true});
 pn.addEventListener("touchmove",function(e){if(y0==null)return;dy=e.touches[0].clientY-y0;if(dy>0){pn.style.transition="none";pn.style.transform="translate3d(0,"+dy+"px,0)"}},{passive:true});
 pn.addEventListener("touchend",function(){if(y0==null)return;pn.style.transition="";pn.style.transform="";if(dy>110)closeSheet();y0=null},{passive:true})})();

/* ---- 下のバー ---- */
var nav=$("#nav"),ly=scrollY;
nav.addEventListener("pointerdown",function(e){var b=e.target.closest("a,button");if(!b)return;var r=b.getBoundingClientRect(),s=document.createElement("i");s.className="rp";s.style.left=(e.clientX-r.left)+"px";s.style.top=(e.clientY-r.top)+"px";b.appendChild(s);setTimeout(function(){s.remove()},650);
  b.classList.remove("tap");void b.offsetWidth;b.classList.add("tap")});
nav.addEventListener("click",function(e){var b=e.target.closest("[data-w]");if(!b)return;S.w=b.dataset.w;S.n=24;sync();go(true);
  var top=$("#sent").getBoundingClientRect().top+scrollY;scrollTo({top:top,behavior:"smooth"})});
addEventListener("scroll",function(){var y=scrollY;if(Math.abs(y-ly)>8){nav.classList.toggle("hide",y>ly&&y>300);ly=y}},{passive:true});
var mu=$("#mu");$("#mnb").onclick=function(){mu.classList.add("op")};$(".bk",mu).onclick=function(){mu.classList.remove("op")};

/* ---- 昼と夜 ---- */
var cv=$("#stars"),drawn=0;
function stars(){var w=innerWidth,h=Math.min(document.body.scrollHeight,innerHeight*8),dp=Math.min(2,devicePixelRatio||1);if(drawn===w+"x"+h)return;drawn=w+"x"+h;
  cv.width=w*dp;cv.height=h*dp;cv.style.height=h+"px";var c=cv.getContext("2d");c.scale(dp,dp);var n=Math.round(w*h/2600),r=seed;
  function rnd(){r=(r*16807)%2147483647;return r/2147483647}
  for(var i=0;i<n;i++){var x=rnd()*w,y=rnd()*h,s=rnd(),a=.25+rnd()*.6;c.fillStyle="rgba(255,255,255,"+a+")";c.beginPath();c.arc(x,y,s<.92?.55+rnd()*.5:1.1+rnd()*.6,0,7);c.fill();
    if(s>.985){var g=c.createRadialGradient(x,y,0,x,y,7);g.addColorStop(0,"rgba(200,215,255,.5)");g.addColorStop(1,"rgba(200,215,255,0)");c.fillStyle=g;c.fillRect(x-7,y-7,14,14);c.fillStyle="rgba(255,255,255,.55)";c.fillRect(x-5,y-.4,10,.8);c.fillRect(x-.4,y-5,.8,10)}}}
var shootT;function shoot(){clearTimeout(shootT);if(!H.classList.contains("nt")||RM)return;
  shootT=setTimeout(function(){var s=document.createElement("i");s.className="shoot";s.style.left=(innerWidth*.45+Math.random()*innerWidth*.6)+"px";s.style.top=(scrollY+30+Math.random()*innerHeight*.4)+"px";$("#sky").appendChild(s);setTimeout(function(){s.remove()},1300);shoot()},(12+Math.random()*20)*1e3)}
function apply(n){H.classList.toggle("nt",n);try{localStorage.setItem("usagi_theme",n?"night":"day")}catch(e){}
  $("#logo").src=n?"/assets/logo-s-night.png":"/assets/logo-s.png?v=2";$$(".sv .hd img").forEach(function(i){i.src=$("#logo").src});
  $("#tg").innerHTML=(n?I.sun+"<span>昼</span>":I.moon+"<span>夜</span>");var m=$('meta[name="theme-color"]');if(m)m.content=n?"#0A0E18":"#FFFFFF";
  if(n){stars();shoot()}}
$("#tg").addEventListener("click",function(e){var n=!H.classList.contains("nt");
  if(!document.startViewTransition||RM){apply(n);return}
  var x=e.clientX||innerWidth-40,y=e.clientY||30,r=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));H.classList.add("vtt");
  var t=document.startViewTransition(function(){apply(n)});
  t.ready.then(function(){H.animate({clipPath:["circle(0px at "+x+"px "+y+"px)","circle("+r+"px at "+x+"px "+y+"px)"]},{duration:760,easing:"cubic-bezier(.4,0,.2,1)",pseudoElement:"::view-transition-new(root)"})});
  t.finished.then(function(){H.classList.remove("vtt")})});
apply(H.classList.contains("nt"));
addEventListener("load",function(){drawn=0;if(H.classList.contains("nt"))stars()});
})();
