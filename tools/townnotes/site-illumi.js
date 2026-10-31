// ---- 月の「関西イルミネーション」ページ（tools/illumi/build.py）とつなぐ所 ----
// ページの作り：府県ボタン #flt button[data-p]、府県ごとの箱 .ps（地図の府県の形が .pf なので別の名前）、カード .it > a.card（.t 名前・.d 日程・.tg の中に 無料）、地図ボタン a.mp
function curPref(){var b=$("#flt button.on");return b&&b.dataset.p!=="すべて"?b.dataset.p:""}
function curTab(){return "イルミネーション"}
function items(){var pf=curPref(),seen={},out=[];
 $$(".ps .it").forEach(function(w){var p=w.getAttribute("data-pref")||"";if(pf&&p!==pf)return;var a=$(".card",w);if(!a)return;var tt=$(".t",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k],d=$(".d",a),mp=$(".mp",w),tags=$$(".fr",a).map(function(e){return e.textContent});
  out.push({w:w,a:a,k:k,t:tt.textContent,pref:p,d:d?d.textContent:"",tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:false})});
 return out}
function others(){return[]}
function pickPref(pf){var b=$('#flt button[data-p="'+(pf||"すべて")+'"]');if(b)b.click()}
// 「地図で見る」は府県ボタンのすぐ下
function mount(){var f=$("#flt");if(!f)return;if(f.nextSibling!==mb)f.parentNode.insertBefore(mb,f.nextSibling);
 if(!FS&&mb.nextSibling!==box)mb.parentNode.insertBefore(box,mb.nextSibling)}
function tabList(){return[]}
function prefList(){return $$("#flt button").map(function(b){return {el:b,name:b.textContent,on:b.classList.contains("on")}})}
function tabCount(){return String(items().length)}
var ZONE="#flt";
function cnt1(k){try{if(localStorage.getItem("usagi_owner")==="1")return;var b=JSON.stringify({k:"イルミネーション｜"+k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true})}catch(e){}}
