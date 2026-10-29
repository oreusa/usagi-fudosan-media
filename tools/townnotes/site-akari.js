// ---- 燈のページ（関東おでかけリスト・akari-auto scripts/page.py）とつなぐ所 ----
// 地図の本体はページの作りを知らない。ページごとの違いはここだけに書く（月のページは site-tsuki.js）
// 燈のページ：都県ボタン .flt button[data-p]、無料だけ .chips .fr、タブ .otab button[data-t]、中身 #odekake .pane[data-t]、カード .card.it
function tabName(b){var s="";[].forEach.call(b.childNodes,function(n){if(n.nodeType===3)s+=n.textContent});return s.trim()}
function curPane(){var b=$(".otab button.on"),t=b?b.dataset.t:"now";return $('#odekake .pane[data-t="'+t+'"]')}
function curPref(){var b=$(".flt button[data-p].on");return b?b.dataset.p:""}
function curTab(){var b=$(".otab button.on");return b?tabName(b):"開催中"}
function freeOnly(){var f=$(".chips .fr");return !!(f&&f.classList.contains("on"))}
// 今のしぼりこみ（都県・無料だけ）に合うカード。「もっと見る」でかくれている物も地図には出す
function okCard(c,pf){if(pf&&c.dataset.pref&&c.dataset.pref!==pf)return false;if(freeOnly()&&c.dataset.free!=="1")return false;return true}
function cardKey(c){var tt=$(".t",c);return key(tt&&tt.textContent)}
function items(){var pane=curPane();if(!pane)return[];var pf=curPref(),seen={},out=[],soon=pane.dataset.t==="soon";
 $$(".card.it",pane).forEach(function(c){if(!okCard(c,pf))return;var k=cardKey(c);if(!k||seen[k])return;seen[k]=1;var g=GEO[k];
  var tt=$(".t",c),go=$("a.go",c),wh=$(".when",c),mp=$("a.mp",c),tags=$$(".tg",c).map(function(e){return e.textContent.replace(/^・/,"")});
  out.push({w:c,a:c,k:k,t:$$(".nwp",tt).map(function(s){return s.textContent}).join(" ")||tt.textContent,pref:c.dataset.pref||"",d:wh?wh.textContent:"",tags:tags,href:go?go.getAttribute("href"):"",map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:soon})});
 return out}
// ほかのタブの場所（地図に小さな点で出すだけ。押せない）
function others(){var cp=curPane(),pf=curPref(),seen={},out=[];list.forEach(function(i){seen[i.k]=1});
 $$("#odekake .pane").forEach(function(p){if(p===cp)return;$$(".card.it",p).forEach(function(c){if(!okCard(c,pf))return;var k=cardKey(c),g=k&&GEO[k];if(!g||g[0]==null||seen[k])return;seen[k]=1;out.push({k:k,pref:c.dataset.pref||"",lat:g[0],lon:g[1]})})});return out}
function pickPref(pf){var b=$('.flt button[data-p="'+(pf||"")+'"]');if(b)b.click()}
// 「地図で見る」は件数の行のすぐ下（おでかけのときだけ出る：ページが data-v で出し入れする）
function mount(){var sec=$("#odekake");if(!sec)return;mb.setAttribute("data-v","odekake");
 if(mb.parentNode!==sec.parentNode||(mb.nextSibling!==sec&&mb.nextSibling!==box))sec.parentNode.insertBefore(mb,sec);
 if(!FS&&mb.nextSibling!==box)sec.parentNode.insertBefore(box,mb.nextSibling)}
// 上の帯に写すタブ（名前・件数・押す物）。0件のタブは出さない
function tabList(){return $$(".otab button").map(function(b){var s=$("small",b);return {el:b,name:tabName(b),count:s?s.textContent.replace(/[^0-9]/g,""):"",on:b.classList.contains("on"),off:b.disabled}})}
function prefList(){return $$(".flt button[data-p]").map(function(b){return {el:b,name:b.textContent,on:b.classList.contains("on")}})}
function tabCount(){var b=$(".otab button.on small");return b?b.textContent.replace(/[^0-9]/g,""):""}
var ZONE=".flt,.otab,.chips[data-v]";
// 押された数は燈のページでは数えない（燈のページの数え方は買う・開くだけ）
function cnt1(k){}
