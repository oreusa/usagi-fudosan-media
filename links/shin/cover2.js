/* 新しい表紙（見本 /shin/cover2）。11/19 23時 owner「トップださ」「地図適当すぎ」「ツールなかったの？」。
   役目＝開いてすぐ「いま関西でやっているおでかけ」が写真で分かり、家と土地・おかいものへも1タップで行ける。
   こだわり＝本物の地図（MapLibre・地図の絵は OpenFreeMap）に、いま開催中の所が点で並び、押すと写真のカードが出る。
   地図の部品（約800KB）は、地図の所に近づいた時に初めて読む（一番上はすぐ出る）。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,TD=S_.TD,dd=S_.dd,diff=S_.diff,md=S_.md,RM=S_.RM,D=S_.data,RG=S_.reg;
function avg(b){try{var h=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)}),hd=h[0]|h[1]<<8|h[2]<<16,l=(hd&63)/63,p=((hd>>6)&63)/31.5-1,q=((hd>>12)&63)/31.5-1,bb=l-2/3*p,r=(3*l-bb+q)/2,g=r-q;
  var f=function(v){return Math.round(255*Math.max(0,Math.min(1,v)))};return "rgb("+f(r)+","+f(g)+","+f(bb)+")"}catch(e){return ""}}
function img(x){return x.im.indexOf("/")>=0?x.im:"/assets/ph/"+x.im}
function left(e){var n=diff(TD,e);return n<=0?"きょうまで":n<=7?"あと"+n+"日":md(e)+"まで"}
function link(x){return x.o?"/o/"+x.o:"/odekake"}
var DT=dd(TD),N=D.pins.length;
var cards=D.top.map(function(x,i){return '<a class="c2c" href="'+link(x)+'" style="background-color:'+avg(x.th)+'"><img src="'+img(x)+'" alt="" '+(i<2?'fetchpriority="high"':'loading="lazy"')+' decoding="async">'+
  '<span class="c2g"><small>'+esc(x.p)+'・'+left(x.e)+'</small><b>'+esc(x.t)+'</b></span></a>'}).join("");
var PF=["すべて"].concat(RG.pref);
S_.main.innerHTML='<div class="c2">'+
 '<section class="wrap c2hero"><p class="c2d">'+(DT.getUTCMonth()+1)+'月'+DT.getUTCDate()+'日（'+"日月火水木金土"[DT.getUTCDay()]+'）・いま開催中 <b>'+N+'</b>件</p>'+
 '<h1>'+esc(D.h1)+'</h1><p class="c2s">'+esc(D.sub)+'</p></section>'+
 '<div class="c2r" id="c2r">'+cards+'</div><div class="c2dots" id="c2dots">'+D.top.map(function(_,i){return '<i'+(i?'':' class="on"')+'></i>'}).join("")+'</div>'+
 '<div class="wrap"><a class="c2all" href="/odekake">いま開催中のおでかけを、ぜんぶ見る<i>'+N+'件</i></a></div>'+
 '<section class="wrap c2sec" id="mapsec"><h2>地図で探す</h2><p class="c2p">点を押すと、その場所のおでかけが出ます。</p>'+
 '<div class="c2pf" id="c2pf">'+PF.map(function(p,i){return '<button type="button" data-p="'+(i?p:"")+'"'+(i?'':' class="on"')+'>'+p+(i&&D.pc[p]!=null?'<small>'+D.pc[p]+'</small>':'')+'</button>'}).join("")+'</div>'+
 '<div class="c2map" id="c2map"><div class="c2ml">地図を読みこんでいます…</div></div><div class="c2pk" id="c2pk" aria-live="polite"></div></section>'+
 '<section class="wrap c2sec"><h2>家と土地の値段</h2><p class="c2p">'+esc(D.ie.s)+'</p><a class="c2row" href="/fudosan-list"><b>街の家と土地の相場</b><span>'+D.ie.n+'の街</span></a>'+
 '<a class="c2row" href="/ikura"><b>お家はいくらで売れる？</b><span>30秒で目安</span></a><a class="c2row" href="/uru"><b>家を売る前に</b><span>3つの順で</span></a></section>'+
 '<section class="wrap c2sec"><h2>日用品の値段くらべ</h2><p class="c2p">楽天・Yahoo!ショッピング・Amazon を1つの画面で。</p><a class="c2row" href="/okaimono"><b>いちばん安いお店を見る</b><span>'+D.kau.n+'種類</span></a>'+
 '<a class="c2row" href="/kaiten"><b>開店・閉店ニュース</b><span>これから '+D.kai.n+'件</span></a></section>'+
 '<section class="wrap c2sec"><h2>季節のおでかけ</h2><div class="c2more">'+D.more.map(function(m){return '<a href="'+m[1]+'">'+esc(m[0])+'</a>'}).join("")+'</div></section>'+
 '<section class="wrap c2sec c2sns">'+D.sns.map(function(s){return '<a href="'+s[1]+'" target="_blank" rel="noopener">'+esc(s[0])+'</a>'}).join("")+'</section></div>';

/* 写真の列：今の1枚の印 */
var r=$("#c2r"),dots=$$("#c2dots i"),q=0;
r.addEventListener("scroll",function(){if(q)return;q=requestAnimationFrame(function(){q=0;var w=r.firstChild.getBoundingClientRect().width+12,i=Math.round(r.scrollLeft/w);dots.forEach(function(d,k){d.classList.toggle("on",k===i)})})},{passive:true});

/* 地図（近づいたら読む） */
var KC=D.kc||{},map=null,mk=[],box=$("#c2map"),pk=$("#c2pk"),cur="";
function pickCard(x){pk.innerHTML='<a class="c2pc" href="'+link(x)+'">'+(x.im?'<span class="im" style="background-color:'+avg(x.th)+'"><img src="'+img(x)+'" alt="" decoding="async"></span>':'')+
  '<span class="tx"><small>'+esc(x.p)+'・'+left(x.e)+'</small><b>'+esc(x.t)+'</b><em>くわしく見る →</em></span></a>';if(!RM)pk.firstChild.animate([{opacity:0,transform:"translateY(8px)"},{opacity:1,transform:"none"}],{duration:260,easing:"cubic-bezier(.2,.9,.25,1)"})}
function nightStyle(on){box.classList.toggle("nt",on)}
function build(){
  var BB=D.bb;
  map=new maplibregl.Map({container:box,style:"https://tiles.openfreemap.org/styles/positron",bounds:BB,fitBoundsOptions:{padding:24},attributionControl:{compact:true},
    dragRotate:false,pitchWithRotate:false,touchPitch:false,cooperativeGestures:true,localIdeographFontFamily:'"Hiragino Sans","Noto Sans JP",sans-serif'});
  map.touchZoomRotate.disableRotation();
  map.on("error",function(){if(!map.isStyleLoaded()&&$(".c2ml",box))$(".c2ml",box).textContent="地図を出せませんでした（通信を確かめてください）"});
  map.on("style.load",function(){var ly=map.getStyle().layers;ly.forEach(function(l){if(l.type==="symbol"&&l.layout&&l.layout["text-field"]){try{map.setLayoutProperty(l.id,"text-field",["coalesce",["get","name:ja"],["get","name"]])}catch(e){}}});
    $(".c2ml",box)&&$(".c2ml",box).remove()});
  D.pins.forEach(function(x){var el=document.createElement("button");el.type="button";el.className="c2pin";el.style.setProperty("--c",KC[x.k]||"#1D1D1F");el.setAttribute("aria-label",x.t);
    el.addEventListener("click",function(e){e.stopPropagation();$$(".c2pin.on",box).forEach(function(b){b.classList.remove("on")});el.classList.add("on");pickCard(x)});
    var m=new maplibregl.Marker({element:el}).setLngLat([x.ll[1],x.ll[0]]).addTo(map);mk.push([m,x,el])});
  nightStyle(document.documentElement.classList.contains("nt"));
  new MutationObserver(function(){nightStyle(document.documentElement.classList.contains("nt"))}).observe(document.documentElement,{attributes:true,attributeFilter:["class"]});
}
function show(p){cur=p;$$("#c2pf button").forEach(function(b){b.classList.toggle("on",b.dataset.p===p)});
  if(!map)return;var L=D.pins.filter(function(x){return !p||x.p===p});mk.forEach(function(a){a[2].style.display=(!p||a[1].p===p)?"":"none"});
  if(L.length){var b=new maplibregl.LngLatBounds();L.forEach(function(x){b.extend([x.ll[1],x.ll[0]])});map.fitBounds(b,{padding:40,maxZoom:12,duration:RM?0:700})}
  pk.innerHTML=""}
$("#c2pf").addEventListener("click",function(e){var b=e.target.closest("button");if(b)show(b.dataset.p)});
var loaded=false;function load(){if(loaded)return;loaded=true;
  var cs=document.createElement("link");cs.rel="stylesheet";cs.href="/shin/ml/maplibre-gl.css";document.head.appendChild(cs);
  var s=document.createElement("script");s.src="/shin/ml/maplibre-gl.js";s.onload=function(){try{build();if(cur)show(cur)}catch(e){$(".c2ml",box).textContent="地図を出せませんでした"}};
  s.onerror=function(){$(".c2ml",box).textContent="地図を出せませんでした"};document.head.appendChild(s)}
new IntersectionObserver(function(es,o){if(es[0].isIntersecting){o.disconnect();load()}},{rootMargin:"600px 0px"}).observe($("#mapsec"));
S_.onNav(function(a){if(a==="map"){load();$("#mapsec").scrollIntoView({behavior:RM?"auto":"smooth"})}});
S_.ready();
})();
