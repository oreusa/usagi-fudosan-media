/* TOWN NOTES（仮）: おでかけリストに、指で拡大できるイラストの地図とピンを組み込む。
   地図: MapLibre GL で、府県と市区町村の形（links/townnotes/kansai.json、国土数値情報を加工）だけを描く。道路や地図タイルは使わない。
   今のページ（タブ・府県ボタン・カード）をそのまま読み、選んでいるタブと府県のピンだけを立てる。
   場所は /townnotes/geo.json（tools/townnotes/geocode.py が作る）。 */
(function(){
var LIB="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl";
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var PC={"大阪":"#D9775A","京都":"#9C7BB8","兵庫":"#4F86C6","奈良":"#5FA06A","滋賀":"#3FA3B5","和歌山":"#E09A3E"};
var BB={"":[[134.25,33.43],[136.46,35.78]],"大阪":[[135.09,34.27],[135.75,35.05]],"京都":[[134.85,34.70],[136.06,35.78]],"兵庫":[[134.25,34.15],[135.47,35.68]],
 "奈良":[[135.54,33.86],[136.23,34.78]],"滋賀":[[135.76,34.79],[136.46,35.71]],"和歌山":[[135.00,33.43],[136.00,34.39]]};
var key=function(s){return String(s||"").replace(/\s+/g,"")};
var RM=matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---- 見た目（今のサイトに合わせる） ----
var css=`
.tn{margin:0 0 18px}
.tn .hd{display:flex;justify-content:space-between;align-items:flex-end;margin:2px 0 10px}
.tn .hd .e{font-family:Jost,sans-serif;font-size:9.5px;letter-spacing:.36em;color:#A07E66}
.tn .hd .j{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;letter-spacing:.1em;color:#2B2622;margin-top:4px}
.tn .hd .n{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.06em}
.tn .hd .n b{font-family:Jost,sans-serif;font-weight:500;font-size:16px;color:#2B2622;margin:0 2px}
.tn .fr{position:relative;aspect-ratio:1/1.08;background:#FBF8F3;border:1px solid #E2D6CB;overflow:hidden;border-radius:2px}
.tn .mp2{position:absolute;inset:0}
.tn .fr .ld{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:Jost,sans-serif;font-size:10px;letter-spacing:.3em;color:#A39A90}
.tn .bk{position:absolute;left:10px;top:10px;z-index:3;font-family:"Zen Kaku Gothic New",sans-serif;font-size:11.5px;letter-spacing:.06em;color:#2B2622;background:rgba(255,255,255,.94);border:1px solid #D9CFC4;border-radius:16px;padding:6px 12px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .3s;box-shadow:0 2px 8px rgba(43,38,34,.08)}
.tn .bk.on{opacity:1;pointer-events:auto}
.tn .hint{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);z-index:2;font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;letter-spacing:.06em;color:#6E625A;background:rgba(255,255,255,.92);border-radius:12px;padding:4px 10px;pointer-events:none;transition:opacity .6s;white-space:nowrap}
.tn .maplibregl-ctrl-group{border-radius:10px!important;box-shadow:0 2px 8px rgba(43,38,34,.10)!important;border:1px solid #E2D6CB}
.tn .maplibregl-ctrl-group button{width:36px!important;height:36px!important}
.tn .maplibregl-ctrl-attrib{font-size:9px;background:rgba(255,255,255,.75)!important}
.tn .maplibregl-cooperative-gesture-screen{font-family:"Zen Kaku Gothic New",sans-serif;font-size:14px;background:rgba(43,38,34,.45)}
.tn .pop{position:relative;background:#fff;border:1px solid #E2D6CB;border-top:0;border-left:3px solid var(--pc,#2B2622);max-height:0;overflow:hidden;opacity:0;transition:max-height .38s cubic-bezier(.2,.8,.2,1),opacity .25s}
.tn .pop.on{max-height:440px;opacity:1;overflow:auto}
.tn .pop .x{position:absolute;right:4px;top:2px;width:38px;height:38px;background:none;border:0;font-family:Jost,sans-serif;font-size:19px;color:#8C7B6E;cursor:pointer}
.tn .pop .gh{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;letter-spacing:.12em;color:#A07E66;padding:12px 14px 0}
.tn .pi{padding:12px 46px 12px 14px;border-bottom:1px solid #F0EAE3}
.tn .pi:last-child{border-bottom:0}
.tn .pi .d{font-size:11px;color:#8C7B6E;letter-spacing:.04em}
.tn .pi .d i{font-style:normal;font-weight:700;margin-right:6px}
.tn .pi .d u{text-decoration:none;font-size:9.5px;border:1px solid currentColor;padding:0 4px;margin-left:6px}
.tn .pi .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;line-height:1.45;color:#2B2622;margin:3px 0 0}
.tn .pi .ac{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:8px}
.tn .pi .ac a{white-space:nowrap;display:inline-block;font-size:11.5px;letter-spacing:.08em;color:#2B2622;text-decoration:underline;text-decoration-color:#CFC5BA;text-underline-offset:4px;padding:5px 0}
.tn .pi.mini{cursor:pointer;padding:10px 46px 10px 14px;position:relative}
.tn .pi.mini:after{content:"›";position:absolute;right:18px;top:50%;transform:translateY(-50%);font-family:Jost,sans-serif;font-size:18px;color:#B3AAA1}
.tn .pi.mini .t{font-size:13.5px}
.tn .lg{display:none;justify-content:center;gap:16px;margin:8px 0 0;font-size:10px;color:#9C9187;letter-spacing:.06em}
.tn .lg span:before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:#9C9187;margin-right:5px;vertical-align:-1px}
.tn .lg span.s:before{background:#fff;box-shadow:inset 0 0 0 2px #9C9187}
.it.tnf .card{box-shadow:0 0 0 2px var(--pc,#2B2622)!important;transition:box-shadow .3s}
`;
var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);

// ---- 枠を作る ----
var box=document.createElement("div");box.className="tn";
box.innerHTML='<div class="hd"><div><span class="e">MAP</span><span class="j">地図で見る</span></div><div class="n" id="tnn"></div></div>'+
 '<div class="fr"><div class="ld">LOADING MAP</div><div class="mp2" id="tnmap"></div><button class="bk" type="button">← 関西全体</button><div class="hint" id="tnh">2本の指で、広げたり動かしたりできます</div></div>'+
 '<div class="pop" role="dialog"><button class="x" type="button" aria-label="閉じる">×</button><div class="pb"></div></div>'+
 '<div class="lg"><span>開催・オープン</span><span class="s">これからできる</span></div>';
var pop=$(".pop",box),bk=$(".bk",box);

// ---- 今のページの状態を読む ----
function curPref(){var b=$("#flt button.on");return b&&b.textContent!=="すべて"?b.textContent:""}
function curBlk(){return $(".paper .blk.tb:not(.toff)")||$(".paper .blk.b-now")}
function curTab(){var b=$(".tabs button.on b");return b?b.childNodes[0].textContent:"開催中"}
var GEO={};
function items(){var blk=curBlk();if(!blk)return[];var seen={},out=[],soon=blk.classList.contains("b-new");
 $$(".it",blk).forEach(function(w){if(w.style.display==="none")return;var a=$(".card",w);if(!a)return;var tt=$(".t",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k];var d=$(".d",a),dt="",tags=[];if(d)[].forEach.call(d.childNodes,function(n){if(n.nodeType===3)dt+=n.textContent;else if(n.classList&&n.classList.contains("tg"))tags.push(n.textContent)});
  var mp=$(".mp",w);out.push({w:w,a:a,k:k,t:$$(".nwp",tt).map(function(s){return s.textContent}).join(" ")||tt.textContent,pref:w.getAttribute("data-pref")||"",d:dt.replace(/^\s*[｜|]\s*/,"").trim(),tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:soon});});
 return out}

// ---- イラストの地図（リールと同じ「府県の形だけ」の地図。府県と市区町村の形は国土数値情報を軽くしたもの） ----
var FB=["Noto Sans Bold"];
var SOFT={"大阪":"#FBE0D5","京都":"#ECE2F5","兵庫":"#DDEAF8","奈良":"#DEF0DC","滋賀":"#D5EFF2","和歌山":"#FBEACF"};
function mt(o,k){var e=["match",["get",k]];Object.keys(o).forEach(function(p){e.push(p,o[p])});e.push("#EEE");return e}
function style(){return{version:8,glyphs:"https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",sources:{},layers:[{id:"sea",type:"background",paint:{"background-color":"#D3EBF4"}}]}}

// ---- 地図 ----
var map=null,list=[],sel=null,lastSig="",ready=false;
function geo(){return{type:"FeatureCollection",features:list.filter(function(i){return i.lat!=null}).map(function(i,n){return{type:"Feature",id:n,geometry:{type:"Point",coordinates:[i.lon,i.lat]},properties:{k:i.k,pref:i.pref,t:i.t,soon:i.soon?1:0}}})}}
var PL={"大阪":[135.40,34.47],"京都":[135.42,35.32],"兵庫":[134.72,35.12],"奈良":[135.93,34.28],"滋賀":[136.30,35.02],"和歌山":[135.45,33.92]};
// かわいいピン（しずく形）。府県の色ごとに作る
function pinImg(c,soon){var W=56,H=72,cv=document.createElement("canvas");cv.width=W;cv.height=H;var g=cv.getContext("2d"),cx=28,cy=26,r=20;
 function shape(){g.beginPath();g.arc(cx,cy,r,Math.PI*0.80,Math.PI*0.20,false);g.quadraticCurveTo(cx+9,cy+r+8,cx,cy+r+22);g.quadraticCurveTo(cx-9,cy+r+8,cx-r*Math.cos(Math.PI*0.2),cy+r*Math.sin(Math.PI*0.2));g.closePath();}
 g.save();g.shadowColor="rgba(80,60,40,.28)";g.shadowBlur=6;g.shadowOffsetY=3;shape();g.fillStyle=soon?"#fff":c;g.fill();g.restore();
 shape();g.lineWidth=4;g.strokeStyle=soon?c:"#fff";if(soon)g.setLineDash([6,4]);g.stroke();g.setLineDash([]);
 g.beginPath();g.arc(cx,cy,7.5,0,7);g.fillStyle=soon?c:"#fff";g.fill();
 if(!soon){g.beginPath();g.ellipse(cx-8,cy-9,5,3,-.6,0,7);g.fillStyle="rgba(255,255,255,.35)";g.fill();}
 return g.getImageData(0,0,W,H)}
function build(KS){
 map=new maplibregl.Map({container:"tnmap",style:style(),bounds:BB[""],fitBoundsOptions:{padding:14},attributionControl:false,cooperativeGestures:true,dragRotate:false,pitchWithRotate:false,touchPitch:false,
  localIdeographFontFamily:"'Zen Maru Gothic','Zen Kaku Gothic New','Hiragino Maru Gothic ProN',sans-serif",minZoom:6.4,maxZoom:13.5,maxBounds:[[132.9,32.7],[137.8,36.5]],
  locale:{"CooperativeGesturesHandler.WindowsHelpText":"Ctrl を押しながらスクロールで拡大できます","CooperativeGesturesHandler.MacHelpText":"⌘ を押しながらスクロールで拡大できます","CooperativeGesturesHandler.MobileHelpText":"2本の指で、広げたり動かしたりできます","NavigationControl.ZoomIn":"拡大","NavigationControl.ZoomOut":"縮小"}});
 map.touchZoomRotate.disableRotation();
 map.addControl(new maplibregl.NavigationControl({showCompass:false}),"top-right");
 map.addControl(new maplibregl.AttributionControl({compact:true,customAttribution:"出典：国土数値情報（行政区域データ）を加工（スマートニュース メディア研究所）"}),"bottom-right");
 map.on("load",function(){var ld=$(".ld",box);if(ld)ld.remove();
  var at=$(".maplibregl-ctrl-attrib",box);if(at)at.classList.remove("maplibregl-compact-show");
  Object.keys(PC).forEach(function(p){map.addImage("pin-"+p,pinImg(PC[p],0),{pixelRatio:2});map.addImage("pin-"+p+"-s",pinImg(PC[p],1),{pixelRatio:2});});
  map.addSource("nb",{type:"geojson",data:KS.nb});map.addSource("pf",{type:"geojson",data:KS.pref});map.addSource("mu",{type:"geojson",data:KS.muni});map.addSource("ml",{type:"geojson",data:KS.lab});
  map.addSource("pl",{type:"geojson",data:{type:"FeatureCollection",features:Object.keys(PL).map(function(p){return{type:"Feature",geometry:{type:"Point",coordinates:PL[p]},properties:{p:p}}})}});
  // まわりの県は薄く
  map.addLayer({id:"nb",type:"fill",source:"nb",paint:{"fill-color":"#F3EEE6","fill-outline-color":"#E6DDD2"}});
  // 関西はシールのように、影＋白いふち
  map.addLayer({id:"pf-sh",type:"fill",source:"pf",paint:{"fill-color":"#C9B8A6","fill-opacity":.45,"fill-translate":[0,4]}});
  map.addLayer({id:"pf",type:"fill",source:"pf",paint:{"fill-color":mt(SOFT,"p"),"fill-opacity":1}});
  map.addLayer({id:"mu",type:"line",source:"mu",minzoom:7.6,paint:{"line-color":"#FFFFFF","line-width":["interpolate",["linear"],["zoom"],8,.6,12,1.6],"line-opacity":.95}});
  map.addLayer({id:"pf-w",type:"line",source:"pf",layout:{"line-join":"round"},paint:{"line-color":"#FFFFFF","line-width":["interpolate",["linear"],["zoom"],6,3,11,6]}});
  map.addLayer({id:"pf-l",type:"line",source:"pf",layout:{"line-join":"round"},paint:{"line-color":"#5A4E45","line-width":["interpolate",["linear"],["zoom"],6,1.1,11,1.8]}});
  // 市区町村の名前（広げると出る。大阪市などの区は、もう少し広げてから）
  map.addLayer({id:"ml",type:"symbol",source:"ml",minzoom:8.4,filter:["==",["get","c"],""],layout:{"text-field":["get","n"],"text-font":FB,"text-size":["interpolate",["linear"],["zoom"],8.4,10,12,13],"text-padding":4},paint:{"text-color":"#7A6C60","text-halo-color":"rgba(255,255,255,.9)","text-halo-width":1.6}});
  map.addLayer({id:"ml-w",type:"symbol",source:"ml",minzoom:10,filter:["!=",["get","c"],""],layout:{"text-field":["get","n"],"text-font":FB,"text-size":["interpolate",["linear"],["zoom"],10,10.5,13,13.5],"text-padding":3},paint:{"text-color":"#7A6C60","text-halo-color":"rgba(255,255,255,.9)","text-halo-width":1.6}});
  map.addLayer({id:"pl",type:"symbol",source:"pl",maxzoom:8.4,layout:{"text-field":["get","p"],"text-font":FB,"text-size":16,"text-letter-spacing":.3,"text-allow-overlap":true},paint:{"text-color":mt(PC,"p"),"text-halo-color":"rgba(255,255,255,.95)","text-halo-width":2.4}});
  // ピン
  map.addSource("p",{type:"geojson",data:geo(),cluster:true,clusterRadius:36,clusterMaxZoom:11});
  map.addLayer({id:"cl-ring",type:"circle",source:"p",filter:["has","point_count"],paint:{"circle-color":"#FFFFFF","circle-opacity":.55,"circle-radius":["step",["get","point_count"],20,5,24,15,29]}});
  map.addLayer({id:"cl",type:"circle",source:"p",filter:["has","point_count"],paint:{"circle-color":"#FFFDF9","circle-stroke-color":"#E39A7E","circle-stroke-width":2.5,"circle-radius":["step",["get","point_count"],14,5,17,15,21]}});
  map.addLayer({id:"cl-n",type:"symbol",source:"p",filter:["has","point_count"],layout:{"text-field":["get","point_count_abbreviated"],"text-font":FB,"text-size":13.5,"text-allow-overlap":true},paint:{"text-color":"#5A4E45"}});
  map.addLayer({id:"pin-halo",type:"circle",source:"p",filter:["all",["!",["has","point_count"]],["==",["get","k"],""]],paint:{"circle-radius":22,"circle-color":mt(PC,"pref"),"circle-opacity":.22,"circle-translate":[0,-14]}});
  map.addLayer({id:"pin",type:"symbol",source:"p",filter:["!",["has","point_count"]],layout:{"icon-image":["concat","pin-",["get","pref"],["case",["==",["get","soon"],1],"-s",""]],"icon-anchor":"bottom","icon-allow-overlap":true,"icon-size":["interpolate",["linear"],["zoom"],7,.85,12,1.05]}});
  map.addLayer({id:"pin-name",type:"symbol",source:"p",minzoom:10.5,filter:["!",["has","point_count"]],layout:{"text-field":["get","t"],"text-font":FB,"text-size":11.5,"text-offset":[0,.5],"text-anchor":"top","text-max-width":9,"text-optional":true},paint:{"text-color":"#3F3630","text-halo-color":"#fff","text-halo-width":2}});
  map.on("click",onTap);
  ["cl","pin"].forEach(function(l){map.on("mouseenter",l,function(){map.getCanvas().style.cursor="pointer"});map.on("mouseleave",l,function(){map.getCanvas().style.cursor=""})});
  ready=true;lastSig="";sync();window.__tnReady=true;});
 map.on("movestart",function(){var h=$("#tnh");if(h)h.style.opacity=0});
 setTimeout(function(){var h=$("#tnh");if(h)h.style.opacity=0},5000);
 window.__tnMap=map;
}
// 押した所のまわり（指1本分）をまとめて見る。押し間違えにくくする
function onTap(e){var p=e.point,r=22,fs=map.queryRenderedFeatures([[p.x-r,p.y-r],[p.x+r,p.y+r]],{layers:["cl","pin"]});
 if(!fs.length){closePop();return;}
 function d2(f){var q=map.project(f.geometry.coordinates);if(!f.properties.cluster)q.y-=16;return (q.x-p.x)*(q.x-p.x)+(q.y-p.y)*(q.y-p.y)}
 fs.sort(function(a,b){return d2(a)-d2(b)});var f=fs[0];
 if(f.properties.cluster){map.getSource("p").getClusterExpansionZoom(f.properties.cluster_id).then(function(z){map.easeTo({center:f.geometry.coordinates,zoom:Math.min(z+.3,15),duration:RM?0:650})});return;}
 var ks={};fs.forEach(function(x){if(!x.properties.cluster)ks[x.properties.k]=1});
 var near=list.filter(function(i){return ks[i.k]}),it=list.filter(function(i){return i.k===f.properties.k})[0];
 openPin(it,near);}

// ---- ピンを押したとき ----
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function row(it,full){var c=PC[it.pref]||"#2B2622";
 var h='<div class="d"><i style="color:'+c+'">● '+esc(it.pref)+'</i>'+esc(it.d)+it.tags.map(function(t){return '<u style="color:#5E8A4A">'+esc(t)+'</u>'}).join("")+'</div><div class="t">'+esc(it.t)+'</div>';
 if(full)h+='<div class="ac"><a href="'+esc(it.href)+'" target="_blank" rel="noopener" data-k="地図ピン｜'+esc(it.t)+'">くわしく見る →</a>'+(it.map?'<a href="'+esc(it.map)+'" target="_blank" rel="noopener" data-k="地図ピン地図｜'+esc(it.t)+'">行き方 ↗</a>':'')+'<a href="#" class="go2">リストで見る ↓</a></div>';
 return h}
function openPin(it,near){if(!it)return;sel=it;near=(near&&near.length?near:[it]).slice();near.sort(function(a,b){return a===it?-1:b===it?1:0});
 var pb=$(".pb",pop);pop.style.setProperty("--pc",PC[it.pref]||"#2B2622");
 if(near.length>1){pb.innerHTML='<div class="gh">この辺りに '+near.length+' 件</div>'+near.map(function(o,i){return '<div class="pi'+(i?" mini":"")+'" data-i="'+i+'">'+row(o,!i)+'</div>'}).join("");
  $$(".pi.mini",pb).forEach(function(e){e.addEventListener("click",function(){openPin(near[+e.dataset.i],near)})});}
 else pb.innerHTML='<div class="pi">'+row(it,true)+'</div>';
 var g2=$(".go2",pb);if(g2)g2.addEventListener("click",function(e){e.preventDefault();toList(it)});
 pop.classList.add("on");if(ready)map.setFilter("pin-halo",["all",["!",["has","point_count"]],["==",["get","k"],it.k]]);}
function closePop(){pop.classList.remove("on");sel=null;if(ready)map.setFilter("pin-halo",["all",["!",["has","point_count"]],["==",["get","k"],""]]);}
$(".x",pop).addEventListener("click",closePop);
function toList(it){var w=it.w;if(w.classList.contains("cap")){var m=$(".cmore",w.parentNode);if(m)m.click();}
 w.classList.add("tnf");w.style.setProperty("--pc",PC[it.pref]||"#2B2622");w.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(function(){w.classList.remove("tnf")},2200)}

// ---- 府県ボタンと地図をつなぐ ----
function pickPref(pf){var b=$$("#flt button").filter(function(x){return x.textContent===(pf||"すべて")})[0];if(b)b.click();}
bk.addEventListener("click",function(){pickPref("")});
function draw(){list=items();var pf=curPref(),tab=curTab(),n=list.filter(function(i){return i.lat!=null}).length;
 $("#tnn",box).innerHTML=(pf||"関西")+"の"+tab+"<b>"+n+"</b>か所";$(".lg",box).style.display=tab==="もうすぐ"?"flex":"none";bk.classList.toggle("on",!!pf);
 if(ready)map.getSource("p").setData(geo());}
function mount(){var bar=$(".tabs");if(bar&&bar.nextSibling!==box)bar.parentNode.insertBefore(box,bar.nextSibling);}
function sync(){mount();var pf=curPref(),sig=pf+"|"+curTab();if(sig===lastSig)return;var first=!lastSig,pfChanged=first||lastSig.split("|")[0]!==pf;lastSig=sig;closePop();draw();
 if(ready){map.resize();map.setPaintProperty("pf","fill-opacity",pf?["case",["==",["get","p"],pf],1,.45]:1);if(pfChanged)map.fitBounds(BB[pf],{padding:16,duration:(RM||first)?0:900});}}
document.addEventListener("click",function(e){if(e.target.closest("#flt,.tabs,.dflt"))setTimeout(sync,90)});

// ---- 読みこみ ----
function load(){var l=document.createElement("link");l.rel="stylesheet";l.href=LIB+".css";document.head.appendChild(l);
 var s=document.createElement("script");s.src=LIB+".js";s.onload=function(){var f=document.createElement("link");f.rel="stylesheet";f.href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&display=swap";document.head.appendChild(f);Promise.all([fetch("/townnotes/kansai.json").then(function(r){return r.json()}),document.fonts.load('700 12px "Zen Maru Gothic"').catch(function(){})]).then(function(a){build(a[0])});};s.onerror=function(){$(".fr",box).style.display="none"};document.head.appendChild(s);}
fetch("/townnotes/geo.json",{cache:"no-store"}).then(function(r){return r.json()}).catch(function(){return{}}).then(function(g){Object.keys(g).forEach(function(k){if(g[k][0]!=null)GEO[key(k)]=g[k]});mount();draw();load();});
})();
