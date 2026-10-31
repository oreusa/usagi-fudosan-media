// ---- 燈の「関東イルミネーション」ページ（akari-auto scripts/illumi.py）とつなぐ所 ----
// ページの作り：都県ボタン .tabs button[data-f]（すべては空）、都県ごとの箱 .ps（地図の形が .pf なので別の名前）、カード li.it > .cw > a.cd（.nm 名前・.dt 日程・.fr 無料）と a.mp（地図）
function curPref(){var b=$(".tabs button.on");return b?b.dataset.f||"":""}
function curTab(){return "イルミネーション"}
function items(){var pf=curPref(),seen={},out=[];
 $$(".ps .it").forEach(function(w){var p=w.getAttribute("data-p")||"";if(pf&&p!==pf)return;var a=$(".cd",w);if(!a)return;var tt=$(".nm",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k],d=$(".dt",a),mp=$(".mp",w),tags=$$(".fr",a).map(function(e){return e.textContent});
  out.push({w:w,a:a,k:k,t:tt.textContent,pref:p,d:d?d.textContent:"",tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:false})});
 return out}
function others(){return[]}
function pickPref(pf){var b=$('.tabs button[data-f="'+(pf||"")+'"]');if(b)b.click()}
// 「地図で見る」は都県ボタンのすぐ下
function mount(){var f=$(".tabs");if(!f)return;if(f.nextSibling!==mb)f.parentNode.insertBefore(mb,f.nextSibling);
 if(!FS&&mb.nextSibling!==box)mb.parentNode.insertBefore(box,mb.nextSibling)}
function tabList(){return[]}
function prefList(){return $$(".tabs button").map(function(b){return {el:b,name:b.textContent,on:b.classList.contains("on")}})}
function tabCount(){return String(items().length)}
var ZONE=".tabs";
// 燈のページでは押された数を数えない
function cnt1(k){}
