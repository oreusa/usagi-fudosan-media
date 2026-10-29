/* TOWN NOTES（仮）: おでかけリストに、押すだけで寄っていく地図を組み込む（関西 → 府県 → 市・区）。
   指2本の操作はなし。府県・市区町村の形は links/townnotes/kansai.json（国土数値情報を加工）、場所は geo.json。
   今のページ（タブ・府県ボタン・カード）をそのまま読み、選んでいるタブのカードだけをピンにする。 */
(function(){
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var NS="http://www.w3.org/2000/svg";
var PREFS=["兵庫","京都","滋賀","大阪","奈良","和歌山"];
var PC={"大阪":"#D9775A","京都":"#9C7BB8","兵庫":"#4F86C6","奈良":"#5FA06A","滋賀":"#3FA3B5","和歌山":"#E09A3E"};      // ピン・文字
var FILL={"大阪":"#F7D9CC","京都":"#E6DBF1","兵庫":"#D6E4F5","奈良":"#D8ECD4","滋賀":"#D0EBEF","和歌山":"#F8E4C4"};    // 府県の面
var DEEP={"大阪":"#F0BFA9","京都":"#D3C1E6","兵庫":"#B9D0EE","奈良":"#BCDDB5","滋賀":"#AEDCE3","和歌山":"#F1CF98"};    // 選んだ市・区
var EN={"大阪":"OSAKA","京都":"KYOTO","兵庫":"HYOGO","奈良":"NARA","滋賀":"SHIGA","和歌山":"WAKAYAMA"};
var key=function(s){return String(s||"").replace(/\s+/g,"")};
var RM=matchMedia("(prefers-reduced-motion: reduce)").matches;
// 経度・緯度 → 地図の座標（関西あたりで形がゆがまないよう、経度に cos(34.7°) をかける）
function P(lon,lat){return [(lon-134)*82.2,(36-lat)*100]}

// ---- 見た目 ----
var css=`
.tn{margin:0 0 18px}
.tn-top{padding:6px 0 0}.tn-top .flt{margin:0 0 12px;gap:0 13px;flex-wrap:nowrap}
.tn .hd{display:flex;justify-content:space-between;align-items:flex-end;margin:2px 0 10px}
.tn .hd .e{font-family:Jost,sans-serif;font-size:9.5px;letter-spacing:.36em;color:#A07E66}
.tn .hd .j{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;letter-spacing:.1em;color:#2B2622;margin-top:4px}
.tn .hd .n{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.06em}
.tn .hd .n b{font-family:Jost,sans-serif;font-weight:500;font-size:16px;color:#2B2622;margin:0 2px}
.tn .fr{position:relative;aspect-ratio:1/1.12;background:#FDFCFA;overflow:hidden;user-select:none;-webkit-user-select:none}
.tn .fr:before{content:"";position:absolute;inset:8px;border:1px solid rgba(43,38,34,.28);pointer-events:none;z-index:3}
.tn .fr:after{content:"";position:absolute;inset:0;background:url(/townnotes/grain.png);opacity:.05;mix-blend-mode:multiply;pointer-events:none;z-index:4}
.tn svg.m{position:absolute;inset:0;width:100%;height:100%;display:block}
.tn .pf{stroke:#FDFCFA;stroke-linejoin:round;cursor:pointer;transition:fill .5s,opacity .5s}
.tn .mu{fill:transparent;stroke:#FDFCFA;stroke-linejoin:round;cursor:pointer;transition:fill .4s,opacity .4s}
.tn .lbs{position:absolute;inset:0;pointer-events:none;z-index:2}
.tn .lb{position:absolute;white-space:nowrap;transform:translate(-50%,-50%);text-shadow:0 0 2px #FDFCFA,0 0 3px #FDFCFA,0 0 6px rgba(253,252,250,.9)}
.tn .lb.p{text-align:center;font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.16em;line-height:1.2}
.tn .lb.p small{display:block;font-family:Jost,sans-serif;font-weight:400;font-size:8.5px;letter-spacing:.32em;margin-top:3px}
.tn .lb.m{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:11px;letter-spacing:.06em;color:#5C524A}
.tn .lb.m b{font-family:Jost,sans-serif;font-weight:500;font-size:10px;color:#fff;background:var(--c);border-radius:8px;padding:0 5px;margin-left:4px;text-shadow:none}
.tn .lb.w{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:500;font-size:10px;letter-spacing:.06em;color:#9C8F84}
.tn .lb.t.fl{transform:translate(calc(-100% - 12px),-50%)}
.tn .lb.t{transform:translate(12px,-50%);font-family:"Shippori Mincho",serif;font-weight:600;font-size:12px;color:#2B2622}
.tn .lb.hide{visibility:hidden}
.tn .hit{fill:transparent;cursor:pointer}
.tn .sel-r{fill:none;opacity:.5}
.tn .crumb{position:absolute;left:18px;top:16px;z-index:5;display:flex;align-items:center;gap:6px;font-family:"Shippori Mincho",serif;font-weight:600;font-size:13px;letter-spacing:.08em;color:#2B2622}
.tn .crumb button{font:inherit;color:#8C7B6E;background:none;border:0;padding:6px 0;cursor:pointer;text-decoration:underline;text-decoration-color:#D9CFC4;text-underline-offset:4px}
.tn .crumb i{font-style:normal;font-family:Jost,sans-serif;color:#B3AAA1;font-weight:300}
.tn .cen{position:absolute;right:18px;top:20px;z-index:5;font-family:Jost,sans-serif;font-size:9px;letter-spacing:.34em;color:#A39A90;transition:color .4s}
.tn .hint{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;bottom:14px;background:rgba(255,255,255,.88);border-radius:99px;padding:5px 12px;z-index:5;text-align:center;font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;letter-spacing:.08em;color:#8C7B6E;pointer-events:none}
.tn .hint:before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;background:#D9775A;margin-right:7px;vertical-align:1px}
.tn .cr{position:absolute;right:16px;bottom:4px;z-index:5;font-size:7.5px;color:#C2B9B0;pointer-events:none}
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

// ---- 枠 ----
var box=document.createElement("div");box.className="tn";
box.innerHTML='<div class="hd"><div><span class="e">MAP</span><span class="j">地図で見る</span></div><div class="n" id="tnn"></div></div>'+
 '<div class="fr"><svg class="m" preserveAspectRatio="xMidYMid meet"><g class="g-pf"></g><g class="g-mu"></g><g class="g-pin"></g></svg><div class="lbs"></div>'+
 '<div class="crumb"></div><div class="cen">KANSAI</div><div class="hint"></div><div class="cr">地図：国土数値情報（行政区域）を加工</div></div>'+
 '<div class="pop" role="dialog"><button class="x" type="button" aria-label="閉じる">×</button><div class="pb"></div></div>'+
 '<div class="lg"><span>開催・オープン</span><span class="s">これからできる</span></div>';
var svg=$("svg.m",box),G={pf:$(".g-pf",svg),mu:$(".g-mu",svg),pin:$(".g-pin",svg)},LBS=$(".lbs",box),pop=$(".pop",box);

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

// ---- 形のデータ ----
var PF={},MU=[],GR={},HOME=null;
var LP={"大阪":[135.43,34.52],"京都":[135.45,35.30],"兵庫":[134.78,35.12],"奈良":[135.88,34.30],"滋賀":[136.20,35.05],"和歌山":[135.50,33.98]};
function ring2d(r){return r.map(function(c,i){var q=P(c[0],c[1]);return (i?"L":"M")+q[0].toFixed(2)+" "+q[1].toFixed(2)}).join("")+"Z"}
function geom2d(g){var ps=g.type==="Polygon"?[g.coordinates]:g.coordinates;return ps.map(function(p){return p.map(ring2d).join("")}).join("")}
function gbb(g){var b=[1e9,1e9,-1e9,-1e9],ps=g.type==="Polygon"?[g.coordinates]:g.coordinates;ps.forEach(function(p){p[0].forEach(function(c){var q=P(c[0],c[1]);b[0]=Math.min(b[0],q[0]);b[1]=Math.min(b[1],q[1]);b[2]=Math.max(b[2],q[0]);b[3]=Math.max(b[3],q[1])})});return b}
// 点が形の中にあるか（ピンがどの市・区にあるかを決める）
function inRing(x,y,r){var c=false;for(var i=0,j=r.length-1;i<r.length;j=i++){var a=r[i],b=r[j];if(((a[1]>y)!==(b[1]>y))&&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]))c=!c}return c}
function inGeom(lon,lat,g){var ps=g.type==="Polygon"?[g.coordinates]:g.coordinates;return ps.some(function(p){return inRing(lon,lat,p[0])&&!p.slice(1).some(function(h){return inRing(lon,lat,h)})})}
function el(t,a,par){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);if(par)par.appendChild(e);return e}
function setup(KS){
 KS.pref.features.forEach(function(f){var p=f.properties.p;PF[p]={bb:gbb(f.geometry),path:el("path",{d:geom2d(f.geometry),"class":"pf",fill:FILL[p]},G.pf)};
  PF[p].path.addEventListener("click",function(){if(state.pref!==p)pickPref(p)})});
 KS.muni.features.forEach(function(f){var pr=f.properties,m={p:pr.p,n:pr.n,c:pr.c,g:f.geometry,bb:gbb(f.geometry)};m.id=m.p+"|"+m.c+"|"+m.n;
  m.path=el("path",{d:geom2d(f.geometry),"class":"mu"},G.mu);m.path.addEventListener("click",function(ev){if(state.pref===m.p){ev.stopPropagation();goMuni(m.grp)}});MU.push(m)});
 // 大阪市・京都市・神戸市・堺市などは、区をまとめて「市」として寄る
 MU.forEach(function(m){var gid=m.p+"|"+(m.c||m.n);var g=GR[gid];if(!g){g=GR[gid]={id:gid,p:m.p,n:m.c||m.n,city:!!m.c,mus:[],bb:[1e9,1e9,-1e9,-1e9]}}g.mus.push(m);m.grp=g;g.bb=[Math.min(g.bb[0],m.bb[0]),Math.min(g.bb[1],m.bb[1]),Math.max(g.bb[2],m.bb[2]),Math.max(g.bb[3],m.bb[3])]});
 var b=[1e9,1e9,-1e9,-1e9];PREFS.forEach(function(p){var x=PF[p].bb;b=[Math.min(b[0],x[0]),Math.min(b[1],x[1]),Math.max(b[2],x[2]),Math.max(b[3],x[3])]});HOME=b;
}

// ---- 見ている範囲（なめらかに寄る） ----
var vb=[0,0,100,100],anim=0;
function aspect(){var r=$(".fr",box).getBoundingClientRect();return r.width?r.height/r.width:1.12}
function fit(b,pad){var w=b[2]-b[0],h=b[3]-b[1],A=aspect();pad=pad||.12;var W=w*(1+pad*2),H=h*(1+pad*2)+h*.16;if(H/W>A)W=H/A;else H=W*A;var cx=(b[0]+b[2])/2,cy=(b[1]+b[3])/2;return [cx-W/2,cy-H/2,W,H]}
function fly(to){var from=vb.slice(),t0=performance.now(),D=RM?1:650;cancelAnimationFrame(anim);
 (function f(n){var k=Math.min(1,(n-t0)/D),e=1-Math.pow(1-k,3);vb=from.map(function(v,i){return v+(to[i]-v)*e});apply();if(k<1)anim=requestAnimationFrame(f)})(t0)}
function px(){var r=svg.getBoundingClientRect();return vb[2]/(r.width||360)}  // 画面の1pxが地図の何単位か
function apply(){svg.setAttribute("viewBox",vb.join(" "));var u=px(),lv=level();
 PREFS.forEach(function(p){PF[p].path.setAttribute("stroke-width",(lv===1?2.4:1.6)*u)});
 MU.forEach(function(m){m.path.setAttribute("stroke-width",(lv===3?1.3:.9)*u)});
 // 文字は HTML で重ねる（小さくてもきれいに出る）。重なる文字は、大事な方だけ出す
 var r=svg.getBoundingClientRect(),placed=[];
 LB.forEach(function(l){var x=(l.x-vb[0])/vb[2]*r.width,y=(l.y-vb[1])/vb[3]*r.height;l.e.style.left=x+"px";l.e.style.top=y+"px";l.e.classList.remove("hide")});
 LB.slice().sort(function(a,b){return b.pri-a.pri}).forEach(function(l){l.e.classList.remove("fl");var b=l.e.getBoundingClientRect();if(l.e.classList.contains("t")&&b.right>r.right-16){l.e.classList.add("fl");b=l.e.getBoundingClientRect()}if(b.right<r.left||b.left>r.right||b.bottom<r.top+40||b.top>r.bottom-30){l.e.classList.add("hide");return}
  if(placed.some(function(o){return b.left<o.right+2&&b.right>o.left-2&&b.top<o.bottom+1&&b.bottom>o.top-1})){l.e.classList.add("hide");return}placed.push(b)});
 $$(".pinx",G.pin).forEach(function(g){var r=+g.dataset.r,d=g.querySelector(".dot");d.setAttribute("r",r*u);d.setAttribute("stroke-width",(r>4?2:1.2)*u);g.querySelector(".hit").setAttribute("r",(lv===1?0:18)*u);var s=g.querySelector(".sel-r");if(s){s.setAttribute("r",(r+7)*u);s.setAttribute("stroke-width",1.5*u)}});
}

// ---- 状態：関西（1）→ 府県（2）→ 市・区（3） ----
var LB=[];function addL(x,y,cls,html,pri,c){var e=document.createElement("div");e.className="lb "+cls;e.innerHTML=html;if(c)e.style.setProperty("--c",c);LBS.appendChild(e);LB.push({e:e,x:x,y:y,pri:pri});return e}
var state={pref:"",muni:null},list=[],lastSig="",ready=false,sel=null;
function level(){return state.muni?3:state.pref?2:1}
function goMuni(g){state.muni=g;sel=null;pop.classList.remove("on");render();fly(fit(g.bb,g.city?.04:.22))}
function goPref(){state.muni=null;sel=null;pop.classList.remove("on");render();fly(state.pref?fit(PF[state.pref].bb,.03):fit(HOME,.02))}
function pickPref(pf){var b=$$("#flt button").filter(function(x){return x.textContent===(pf||"すべて")})[0];if(b)b.click();}
function muniOf(it){if(it._m!==undefined)return it._m;it._m=null;for(var i=0;i<MU.length;i++){var m=MU[i];if(m.p===it.pref&&inGeom(it.lon,it.lat,m.g)){it._m=m;break}}
 if(!it._m){var q=P(it.lon,it.lat),best=1e9;MU.forEach(function(m){if(m.p!==it.pref)return;var cx=(m.bb[0]+m.bb[2])/2,cy=(m.bb[1]+m.bb[3])/2,d=(cx-q[0])*(cx-q[0])+(cy-q[1])*(cy-q[1]);if(d<best){best=d;it._m=m}})}return it._m}

function render(){var lv=level(),pf=state.pref,m=state.muni,pins=list.filter(function(i){return i.lat!=null});
 PREFS.forEach(function(p){var on=!pf||p===pf;PF[p].path.setAttribute("fill",on?FILL[p]:"#F1ECE5");});
 var cnt={};pins.forEach(function(i){if(i.pref!==pf)return;var mm=muniOf(i);if(mm){cnt[mm.grp.id]=(cnt[mm.grp.id]||0)+1}});
 var LIGHT=function(p){return {"大阪":"#FBEEE8","京都":"#F4EFF8","兵庫":"#EEF3FA","奈良":"#EEF6EC","滋賀":"#EAF6F8","和歌山":"#FCF3E4"}[p]};
 if(lv===3)PF[pf].path.setAttribute("fill",LIGHT(pf));
 MU.forEach(function(x){var inP=x.p===pf;x.path.style.opacity=inP?1:0;x.path.style.pointerEvents=inP?"auto":"none";x.path.style.fill=m&&x.grp===m?FILL[x.p]:"transparent"});
 LBS.innerHTML="";LB=[];
 if(lv===1)PREFS.forEach(function(p){var c=LP[p],q=P(c[0],c[1]),n=pins.filter(function(i){return i.pref===p}).length;addL(q[0],q[1],"p",p+(n?"<small>"+n+" SPOTS</small>":""),9).style.color=PC[p]});
 if(lv===2)Object.keys(GR).forEach(function(id){var g=GR[id];if(g.p!==pf||!cnt[id])return;var cx=(g.bb[0]+g.bb[2])/2,cy=(g.bb[1]+g.bb[3])/2;addL(cx,cy,"m",esc(g.n)+"<b>"+cnt[id]+"</b>",cnt[id],PC[pf])});
 if(lv===3&&m.city)m.mus.forEach(function(x){var cx=(x.bb[0]+x.bb[2])/2,cy=(x.bb[1]+x.bb[3])/2;addL(cx,cy,"w",esc(x.n),0)});
 G.pin.innerHTML="";
 pins.forEach(function(it){if(pf&&it.pref!==pf)return;var q=P(it.lon,it.lat),c=PC[it.pref]||"#2B2622",inM=lv===3&&muniOf(it)&&muniOf(it).grp===m,r=lv===1?2.6:lv===2?5:(inM?7:3.5);
  var g=el("g",{"class":"pinx"},G.pin);g.dataset.r=r;
  if(sel&&sel.k===it.k)el("circle",{"class":"sel-r",cx:q[0],cy:q[1],stroke:c},g);
  el("circle",{"class":"dot",cx:q[0],cy:q[1],fill:it.soon?"#fff":c,stroke:it.soon?c:"#fff"},g);
  var h=el("circle",{"class":"hit",cx:q[0],cy:q[1]},g);h.addEventListener("click",function(ev){ev.stopPropagation();tapPin(it)});
  });
 var cr=$(".crumb",box);cr.innerHTML="";
 function cb(txt,fn){var b=document.createElement("button");b.type="button";b.textContent=txt;b.onclick=fn;cr.appendChild(b)}
 function sep(){var i=document.createElement("i");i.textContent="›";cr.appendChild(i)}
 function cur(txt){var s=document.createElement("span");s.textContent=txt;cr.appendChild(s)}
 if(lv===1)cur("関西");else{cb("関西",function(){pickPref("")});sep();if(lv===2)cur(pf);else{cb(pf,function(){goPref()});sep();cur(m.n)}}
 var ce=$(".cen",box);ce.textContent=pf?EN[pf]:"KANSAI";ce.style.color=pf?PC[pf]:"";
 $(".hint",box).textContent=lv===1?"府県を押すと、近づきます":lv===2?"市や区を押すと、もっと近づきます":"ピンを押すと、くわしく見られます";
 $("#tnn",box).innerHTML=(lv===3?m.n:pf||"関西")+"の"+curTab()+"<b>"+(lv===3?(cnt[m.id]||0):pins.filter(function(i){return !pf||i.pref===pf}).length)+"</b>か所";
 apply();}

// ---- ピンを押したとき（指1本分のまわりのピンも一緒に出す） ----
function tapPin(it){var lv=level();if(lv===1){pickPref(it.pref);return}
 var u=px(),q=P(it.lon,it.lat),near=list.filter(function(o){if(o.lat==null||(state.pref&&o.pref!==state.pref))return false;var z=P(o.lon,o.lat);return Math.hypot(z[0]-q[0],z[1]-q[1])<20*u});
 if(lv===2&&near.length>2){var mm=muniOf(it);if(mm){goMuni(mm.grp);return}}
 openPin(it,near)}
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
 pop.classList.add("on");render();}
function closePop(){pop.classList.remove("on");if(sel){sel=null;if(ready)render()}}
$(".x",pop).addEventListener("click",closePop);
function toList(it){var w=it.w;if(w.classList.contains("cap")){var m=$(".cmore",w.parentNode);if(m)m.click();}
 w.classList.add("tnf");w.style.setProperty("--pc",PC[it.pref]||"#2B2622");w.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(function(){w.classList.remove("tnf")},2200)}

// ---- 今のページとつなぐ ----
function mount(){var bar=$(".tabs");if(!bar)return;
 // 府県ボタンは地図のすぐ上へ（件数は押さないので上のまま）
 var top=$(".tn-top");if(!top){top=document.createElement("div");top.className="tn-top"}
 ["flt","none"].forEach(function(id){var e=document.getElementById(id);if(e&&e.parentNode!==top)top.appendChild(e)});
 if(bar.nextSibling!==top)bar.parentNode.insertBefore(top,bar.nextSibling);
 if(top.nextSibling!==box)top.parentNode.insertBefore(box,top.nextSibling);}
function sync(){mount();if(!ready)return;var pf=curPref(),sig=pf+"|"+curTab();if(sig===lastSig)return;var first=!lastSig,pfChanged=first||lastSig.split("|")[0]!==pf;lastSig=sig;
 list=items();$(".lg",box).style.display=curTab()==="もうすぐ"?"flex":"none";sel=null;pop.classList.remove("on");
 if(pfChanged){state.pref=pf;state.muni=null;if(first){vb=fit(HOME,.02);render()}else goPref()}else render();}
document.addEventListener("click",function(e){if(e.target.closest("#flt,.tabs,.dflt"))setTimeout(sync,90)});
addEventListener("resize",function(){if(ready)apply()});
mount();
Promise.all([fetch("/townnotes/geo.json",{cache:"no-store"}).then(function(r){return r.json()}).catch(function(){return{}}),fetch("/townnotes/kansai.json").then(function(r){return r.json()})]).then(function(a){
 Object.keys(a[0]).forEach(function(k){if(a[0][k][0]!=null)GEO[key(k)]=a[0][k]});setup(a[1]);ready=true;lastSig="";sync();window.__tnReady=true;
}).catch(function(e){console.error(e);$(".fr",box).style.display="none"});
})();
