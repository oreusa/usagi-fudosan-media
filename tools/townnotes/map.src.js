/* TOWN NOTES（仮）: おでかけリストに、リールと同じ関西の地図とピンを組み込む。
   今のページ（タブ・府県ボタン・カード）をそのまま読み、選んでいるタブと府県のピンだけを立てる。
   地図の形は tools/outing_reel/paths.json（mapsvg.com, CC BY 4.0）、場所は /townnotes/geo.json。 */
(function(){
var PATHS=__PATHS__;
var NS="http://www.w3.org/2000/svg",$=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"};
var PID={"大阪":"osaka","京都":"kyoto","兵庫":"hyogo","奈良":"nara","滋賀":"shiga","和歌山":"wakayama"};
var EN={"大阪":"OSAKA","京都":"KYOTO","兵庫":"HYOGO","奈良":"NARA","滋賀":"SHIGA","和歌山":"WAKAYAMA"};
// 府県名を置く位置（府県の形の中で、ピンとかぶりにくい所）
var LBL={"大阪":[.30,.62],"京都":[.42,.22],"兵庫":[.36,.30],"奈良":[.62,.62],"滋賀":[.50,.20],"和歌山":[.50,.62]};
var HOME=[200.5,251,60,60],BASE=60;
function X(lon){return 19.72*lon-2438.3}function Y(lat){return 255.75+(35.67-lat)*23.36}
var key=function(s){return String(s||"").replace(/\s+/g,"")};

// ---- 見た目 ----
var css=`
.tn{margin:0 0 18px}
.tn .hd{display:flex;justify-content:space-between;align-items:flex-end;margin:2px 0 10px}
.tn .hd .e{font-family:Jost,sans-serif;font-size:9.5px;letter-spacing:.36em;color:#A07E66}
.tn .hd .j{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;letter-spacing:.1em;color:#2B2622;margin-top:4px}
.tn .hd .n{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.06em}
.tn .hd .n b{font-family:Jost,sans-serif;font-weight:500;font-size:16px;color:#2B2622;margin:0 2px}
.tn .fr{position:relative;aspect-ratio:1/0.94;background:#FDFCFA;border:1px solid #E2D6CB;overflow:hidden;touch-action:manipulation}
.tn svg.m{position:absolute;inset:0;width:100%;height:100%;display:block}
.tn .mo{fill:#F4F0EA;stroke:#E6DDD2;stroke-width:1px;vector-effect:non-scaling-stroke}
.tn .mk{stroke:#2B2622;stroke-width:1.1px;vector-effect:non-scaling-stroke;stroke-linejoin:round;cursor:pointer;transition:fill .45s,stroke-opacity .45s}
.tn .mk.dim{stroke-opacity:.35}
.tn .lb{position:absolute;transform:translate(-50%,-50%);font-family:"Shippori Mincho",serif;font-weight:600;font-size:12px;letter-spacing:.18em;pointer-events:none;white-space:nowrap;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 6px #fff;transition:opacity .3s}
.tn .lb small{display:block;font-family:Jost,sans-serif;font-weight:400;font-size:8px;letter-spacing:.3em;text-align:center;margin-top:1px;opacity:.8}
.tn .pin{cursor:pointer}
.tn .pin .sh{fill:rgba(43,38,34,.20)}
.tn .pin .hit{fill:transparent}
.tn .pin .dot{stroke:#fff;stroke-width:1.6px;vector-effect:non-scaling-stroke}
.tn .pin.soon .dot{stroke-width:2px;stroke-dasharray:2.4 1.5}
.tn .pin .rg{fill:none;stroke-width:1.2px;vector-effect:non-scaling-stroke;opacity:0;transform-box:fill-box;transform-origin:center}
.tn .pin.sel .rg{animation:tnrp 1.8s ease-out infinite}
@keyframes tnrp{0%{opacity:.75;transform:scale(1)}100%{opacity:0;transform:scale(3.4)}}
.tn .pin .dw{transform-box:fill-box;transform-origin:center bottom}
.tn .cn{position:absolute;top:9px;font-family:Jost,sans-serif;font-size:8.5px;letter-spacing:.32em;color:#A39A90;pointer-events:none}
.tn .cn.a{left:11px}.tn .cn.b{right:11px;transition:color .3s}
.tn .bk{position:absolute;left:8px;bottom:8px;z-index:3;font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;letter-spacing:.06em;color:#2B2622;background:#fff;border:1px solid #CFC5BA;padding:5px 10px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .3s}
.tn .bk.on{opacity:1;pointer-events:auto}
.tn .cr{position:absolute;right:8px;bottom:5px;font-size:8px;color:#B3AAA1;pointer-events:none}
.tn .pop{position:relative;background:#fff;border:1px solid #E2D6CB;border-top:0;border-left:3px solid var(--pc,#2B2622);max-height:0;overflow:hidden;opacity:0;transition:max-height .38s cubic-bezier(.2,.8,.2,1),opacity .25s}
.tn .pop.on{max-height:420px;opacity:1;overflow:auto}
.tn .pop:before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--pc,#2B2622);opacity:.25}
.tn .pop .x{position:absolute;right:4px;top:2px;width:34px;height:34px;background:none;border:0;font-family:Jost,sans-serif;font-size:18px;color:#8C7B6E;cursor:pointer}
.tn .pop .gh{font-family:Jost,sans-serif;font-size:9px;letter-spacing:.3em;color:#A07E66;padding:12px 14px 0}
.tn .pi{padding:12px 44px 12px 14px;border-bottom:1px solid #F0EAE3}
.tn .pi:last-child{border-bottom:0}
.tn .pi .d{font-size:11px;color:#8C7B6E;letter-spacing:.04em}
.tn .pi .d i{font-style:normal;font-weight:700;margin-right:6px}
.tn .pi .d u{text-decoration:none;font-size:9.5px;border:1px solid currentColor;padding:0 4px;margin-left:6px}
.tn .pi .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;line-height:1.45;color:#2B2622;margin:3px 0 0}
.tn .pi .ac{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:8px}
.tn .pi .ac a{white-space:nowrap;display:inline-block;font-size:11.5px;letter-spacing:.08em;color:#2B2622;text-decoration:underline;text-decoration-color:#CFC5BA;text-underline-offset:4px;padding:4px 0}
.tn .pi.mini{cursor:pointer;padding:10px 44px 10px 14px}
.tn .pi.mini .t{font-size:13.5px}
.tn .lg{display:flex;justify-content:center;gap:14px;margin:8px 0 0;font-size:10px;color:#9C9187;letter-spacing:.06em}
.tn .lg span:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:#9C9187;margin-right:5px;vertical-align:0}
.tn .lg span.s:before{background:#fff;border:1px dashed #9C9187;width:6px;height:6px}
.it.tnf .card{box-shadow:0 0 0 2px var(--pc,#2B2622)!important;transition:box-shadow .3s}
`;
var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);

// ---- 地図を作る ----
var box=document.createElement("div");box.className="tn";
box.innerHTML='<div class="hd"><div><span class="e">MAP</span><span class="j">地図で見る</span></div><div class="n" id="tnn"></div></div>'+
 '<div class="fr"><svg class="m" viewBox="'+HOME.join(" ")+'" preserveAspectRatio="xMidYMid slice"><g class="base"></g><g class="pins"></g></svg><div class="lbs"></div>'+
 '<span class="cn a">KANSAI</span><span class="cn b">ALL</span><button class="bk" type="button">← 関西全体</button><span class="cr">地図：mapsvg.com（CC BY 4.0）</span>'+
 '</div><div class="pop" role="dialog"><button class="x" type="button" aria-label="閉じる">×</button><div class="pb"></div></div>'+
 '<div class="lg" style="display:none"><span>開催・オープン</span><span class="s">これからできる</span></div>';
var svg=$("svg.m",box),base=$(".base",svg),pins=$(".pins",svg),lbs=$(".lbs",box),pop=$(".pop",box),bk=$(".bk",box),cnb=$(".cn.b",box);
Object.keys(PATHS).forEach(function(k){if(Object.values(PID).indexOf(k)<0){var p=document.createElementNS(NS,"path");p.setAttribute("class","mo");p.setAttribute("d",PATHS[k]);base.appendChild(p);}});
Object.keys(PID).forEach(function(pf){var p=document.createElementNS(NS,"path");p.setAttribute("class","mk");p.id="tn_"+PID[pf];p.setAttribute("d",PATHS[PID[pf]]);p.dataset.pref=pf;
 p.addEventListener("click",function(){pickPref(pf)});base.appendChild(p);
 var l=document.createElement("div");l.className="lb";l.dataset.pref=pf;l.style.color=PC[pf];l.innerHTML=pf+"<small>"+EN[pf]+"</small>";lbs.appendChild(l);});

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

// ---- 表示する範囲 ----
var vb=HOME.slice(),anim=0;
function target(pf){if(!pf)return HOME;var bb=$("#tn_"+PID[pf]).getBBox(),s=Math.max(bb.width,bb.height/0.94)*1.16;return [bb.x+bb.width/2-s/2,bb.y+bb.height/2-s*0.94/2,s,s*0.94]}
function fly(to){var from=vb.slice(),t0=performance.now(),D=matchMedia("(prefers-reduced-motion: reduce)").matches?1:720;cancelAnimationFrame(anim);
 (function f(n){var k=Math.min(1,(n-t0)/D),e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;vb=from.map(function(v,i){return v+(to[i]-v)*e});place();if(k<1)anim=requestAnimationFrame(f);else labels()})(t0)}
function place(){svg.setAttribute("viewBox",vb.join(" "));var r=vb[2]/BASE;$$(".pin",pins).forEach(function(g){g.setAttribute("transform","translate("+g.dataset.x+" "+g.dataset.y+") scale("+r+")")});labels()}
function labels(){var m=svg.getScreenCTM(),fr=$(".fr",box).getBoundingClientRect(),pf=curPref();if(!m)return;
 $$(".lb",lbs).forEach(function(l){var p=l.dataset.pref,bb=$("#tn_"+PID[p]).getBBox(),pt=svg.createSVGPoint(),o=LBL[p];pt.x=bb.x+bb.width*o[0];pt.y=bb.y+bb.height*o[1];var q=pt.matrixTransform(m);
  l.style.left=(q.x-fr.left)+"px";l.style.top=(q.y-fr.top)+"px";l.style.opacity=pf?0:1;});}

// ---- ピン ----
var list=[],sel=null,lastSig="";
function draw(drop){list=items();var pf=curPref(),tab=curTab();pins.innerHTML="";var n=0,shown=0;
 list.slice().sort(function(a,b){return (b.lat||0)-(a.lat||0)}).forEach(function(it){if(it.lat==null)return;shown++;
  var g=document.createElementNS(NS,"g");g.setAttribute("class","pin"+(it.soon?" soon":"")+(sel&&sel.k===it.k?" sel":""));g.dataset.x=X(it.lon);g.dataset.y=Y(it.lat);g.dataset.k=it.k;
  var c=PC[it.pref]||"#2B2622";
  g.innerHTML='<ellipse class="sh" cx="0" cy=".55" rx=".75" ry=".24"/><circle class="rg" r=".8" stroke="'+c+'"/><g class="dw"><circle class="dot" r=".8" style="fill:'+(it.soon?"#fff":c)+';stroke:'+(it.soon?c:"#fff")+'"/></g><circle class="hit" r="1.9"/>';
  g.addEventListener("click",function(e){e.stopPropagation();openPin(it)});pins.appendChild(g);
  if(drop&&!matchMedia("(prefers-reduced-motion: reduce)").matches){var dw=$(".dw",g),dl=Math.min(n++*22,560);
   dw.animate([{transform:"translateY(-5px)",opacity:0},{transform:"translateY(0)",opacity:1,offset:.62},{transform:"translateY(-.7px) scaleY(.92)",offset:.8},{transform:"none",opacity:1}],{duration:480,delay:dl,easing:"ease-out",fill:"backwards"});}});
 $("#tnn",box).innerHTML=(pf||"関西")+"の"+tab+"<b>"+shown+"</b>か所";
 $(".lg",box).style.display=tab==="もうすぐ"?"flex":"none";
 $$(".mk",base).forEach(function(p){var on=p.dataset.pref===pf;p.style.fill=hexA(PC[p.dataset.pref],pf?(on?.13:.03):.07);p.classList.toggle("dim",!!pf&&!on)});
 cnb.textContent=pf?EN[pf]:"ALL";cnb.style.color=pf?PC[pf]:"";bk.classList.toggle("on",!!pf);
 place()}
function hexA(h,a){var n=parseInt(h.slice(1),16);return "rgba("+(n>>16)+","+(n>>8&255)+","+(n&255)+","+a+")"}

// ---- ピンを押したとき：近くのピンもまとめて出す ----
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function row(it,full){var c=PC[it.pref]||"#2B2622";
 var h='<div class="d"><i style="color:'+c+'">● '+esc(it.pref)+'</i>'+esc(it.d)+it.tags.map(function(t){return '<u style="color:#5E8A4A">'+esc(t)+'</u>'}).join("")+'</div><div class="t">'+esc(it.t)+'</div>';
 if(full)h+='<div class="ac"><a href="'+esc(it.href)+'" target="_blank" rel="noopener" data-k="地図ピン｜'+esc(it.t)+'">くわしく見る →</a>'+(it.map?'<a href="'+esc(it.map)+'" target="_blank" rel="noopener" data-k="地図ピン地図｜'+esc(it.t)+'">行き方 ↗</a>':'')+'<a href="#" class="go2">リストで見る ↓</a></div>';
 return h}
function openPin(it){sel=it;var r=vb[2]/BASE*1.5,near=list.filter(function(o){return o.lat!=null&&Math.hypot(X(o.lon)-X(it.lon),Y(o.lat)-Y(it.lat))<r});
 near.sort(function(a,b){return a===it?-1:b===it?1:0});var pb=$(".pb",pop);pop.style.setProperty("--pc",PC[it.pref]||"#2B2622");
 if(near.length>1){pb.innerHTML='<div class="gh">この辺りに '+near.length+' 件</div>'+near.map(function(o,i){return '<div class="pi'+(i?" mini":"")+'" data-i="'+i+'">'+row(o,!i)+'</div>'}).join("");
  $$(".pi.mini",pb).forEach(function(e){e.addEventListener("click",function(){openPin(near[+e.dataset.i])})});}
 else pb.innerHTML='<div class="pi">'+row(it,true)+'</div>';
 var g2=$(".go2",pb);if(g2)g2.addEventListener("click",function(e){e.preventDefault();toList(it)});
 pop.classList.add("on");$$(".pin",pins).forEach(function(g){g.classList.toggle("sel",g.dataset.k===it.k)});}
function closePop(){pop.classList.remove("on");sel=null;$$(".pin.sel",pins).forEach(function(g){g.classList.remove("sel")})}
$(".x",pop).addEventListener("click",closePop);
svg.addEventListener("click",function(e){if(!e.target.closest(".pin")&&!e.target.closest(".mk"))closePop()});
function toList(it){var w=it.w;if(w.classList.contains("cap")){var m=$(".cmore",w.parentNode);if(m)m.click();}
 w.classList.add("tnf");w.style.setProperty("--pc",PC[it.pref]||"#2B2622");w.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(function(){w.classList.remove("tnf")},2200)}

// ---- 府県を押す＝上の府県ボタンを押すのと同じ ----
function pickPref(pf){var b=$$("#flt button").filter(function(x){return x.textContent===(pf||"すべて")})[0];if(b)b.click();}
bk.addEventListener("click",function(){pickPref("")});

// ---- 地図をタブの下に置く。タブ・府県が変わったら描き直す ----
function mount(){var bar=$(".tabs");if(bar&&bar.nextSibling!==box)bar.parentNode.insertBefore(box,bar.nextSibling);}
function sync(){mount();var pf=curPref(),sig=pf+"|"+curTab();if(sig===lastSig)return;var pfChanged=lastSig.split("|")[0]!==pf||!lastSig;lastSig=sig;closePop();draw(true);if(pfChanged)fly(target(pf));}
document.addEventListener("click",function(e){if(e.target.closest("#flt,.tabs,.dflt"))setTimeout(sync,90)});
addEventListener("resize",labels);
fetch("/townnotes/geo.json",{cache:"no-store"}).then(function(r){return r.json()}).catch(function(){return{}}).then(function(g){Object.keys(g).forEach(function(k){if(g[k][0]!=null)GEO[key(k)]=g[k]});mount();lastSig="";sync();});
})();
