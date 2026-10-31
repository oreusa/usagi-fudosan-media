// ---- 月の「泊まりで行くおでかけ」ページ（tools/tomari/build.py → links/tomari.html）とつなぐ所 ----
// ページの作り：府県ボタン #flt button[data-p]、週末だけ #wk、府県ごとの箱 section.ps[data-p]、カード article.it > a.card（.t 名前・.d 日程・.tg の .fr 無料）、近くの宿 .inn（a.mp 地図・ul li a 宿）
function curPref(){var b=$("#flt button.on");return b&&b.dataset.p!=="すべて"?b.dataset.p:""}
function curTab(){var w=$("#wk");return w&&w.getAttribute("aria-pressed")==="true"?"この週末":"泊まりで行く"}
function items(){var pf=curPref(),seen={},out=[];
 $$(".ps .it").forEach(function(w){if(w.hidden)return;var s=w.closest(".ps"),p=s?s.dataset.p:"";if(pf&&p!==pf)return;var a=$(".card",w);if(!a)return;var tt=$(".t",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k],d=$(".d",a),mp=$(".inn .mp",w),tags=$$(".fr",a).map(function(e){return e.textContent});
  out.push({w:w,a:a,k:k,t:tt.textContent,pref:p,d:d?d.textContent:"",tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:false})});
 return out}
function others(){return[]}
function pickPref(pf){var b=$('#flt button[data-p="'+(pf||"すべて")+'"]');if(b)b.click()}
// 「地図で見る」は「この週末」ボタンのすぐ下
function mount(){var f=$(".wk")||$("#flt");if(!f)return;if(f.nextSibling!==mb)f.parentNode.insertBefore(mb,f.nextSibling);
 if(!FS&&mb.nextSibling!==box)mb.parentNode.insertBefore(box,mb.nextSibling)}
function tabList(){return[]}
function prefList(){return $$("#flt button").map(function(b){return {el:b,name:b.textContent,on:b.classList.contains("on")}})}
function tabCount(){return String(items().length)}
var ZONE="#flt,.wk";
// 地図のカードにも近くの宿3軒（押した数は、ページの「宿｜…」の数え方にそのまま入る）
function extraRow(it){var L=$$(".inn li a",it.w);if(!L.length)return"";
 return '<div class="yd"><b>近くの宿</b>'+L.slice(0,3).map(function(a){var n=$(".hn",a),m=$(".hm",a),p=$(".hp",a);
  return '<a href="'+esc(a.getAttribute("href"))+'" target="_blank" rel="noopener sponsored" '+(a.dataset.y?'data-y="'+esc(a.dataset.y)+'"':'data-k="'+esc(a.dataset.k||"")+'"')+'><span>'+esc(n?n.textContent:"")+'</span><em>'+esc((m&&$("b",m)?$("b",m).textContent:"")+(p&&p.textContent?"・"+p.textContent:""))+'</em></a>'}).join("")+'</div>'}
function cnt1(k){try{if(localStorage.getItem("usagi_owner")==="1")return;var b=JSON.stringify({k:"泊まり｜"+k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true})}catch(e){}}
