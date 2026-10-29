// ---- 月のページ（関西おでかけリスト）とつなぐ所 ----
// 地図の本体はページの作りを知らない。ページごとの違いはここだけに書く（燈のページは site-akari.js）
function curPref(){var b=$("#flt button.on");return b&&b.textContent!=="すべて"?b.textContent:""}
function curBlk(){return $(".paper .blk.tb:not(.toff)")||$(".paper .blk.b-now")}
function curTab(){var b=$(".tabs button.on b");return b?b.childNodes[0].textContent:"開催中"}
// ほかのタブの場所（地図に小さな点で出すだけ。押せない）
function others(){var cb=curBlk(),seen={},out=[];list.forEach(function(i){seen[i.k]=1});
 $$(".paper .blk").forEach(function(blk){if(blk===cb)return;$$(".it",blk).forEach(function(w){var tt=$(".card .t",w),k=key(tt&&tt.textContent),g=k&&GEO[k];if(!g||g[0]==null||seen[k])return;seen[k]=1;out.push({k:k,pref:w.getAttribute("data-pref")||"",lat:g[0],lon:g[1]})})});return out}
function items(){var blk=curBlk();if(!blk)return[];var seen={},out=[],soon=blk.classList.contains("b-new");
 $$(".it",blk).forEach(function(w){if(w.style.display==="none")return;var a=$(".card",w);if(!a)return;var tt=$(".t",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k];var d=$(".d",a),dt="",tags=[];if(d)[].forEach.call(d.childNodes,function(n){if(n.nodeType===3)dt+=n.textContent;else if(n.classList&&n.classList.contains("tg"))tags.push(n.textContent)});
  var mp=$(".mp",w);out.push({w:w,a:a,k:k,t:$$(".nwp",tt).map(function(s){return s.textContent}).join(" ")||tt.textContent,pref:w.getAttribute("data-pref")||"",d:dt.replace(/^\s*[｜|]\s*/,"").trim(),tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:soon});});
 return out}
function pickPref(pf){var b=$$("#flt button").filter(function(x){return x.textContent===(pf||"すべて")})[0];if(b)b.click();}
function mount(){var bar=$(".tabs");if(!bar)return;
 // タブの上に「イベント｜新しいお店・施設」の見出し（4つのタブの中身を分かりやすく）
 var tg=$(".tgrp");if(!tg){tg=document.createElement("div");tg.className="tgrp";tg.innerHTML='<span>イベント</span><span>新しいお店・施設</span>'}
 if(bar.previousSibling!==tg)bar.parentNode.insertBefore(tg,bar);
 // 府県ボタンは地図のすぐ上へ（件数は押さないので上のまま）
 var top=$(".tn-top");if(!top){top=document.createElement("div");top.className="tn-top"}
 ["flt","none"].forEach(function(id){var e=document.getElementById(id);if(e&&e.parentNode!==top)top.appendChild(e)});
 if(bar.nextSibling!==top)bar.parentNode.insertBefore(top,bar.nextSibling);
 // 地図は「地図で見る」を押した人だけに出す（リストが主役）
 if(top.nextSibling!==mb)top.parentNode.insertBefore(mb,top.nextSibling);
 if(!FS&&mb.nextSibling!==box)mb.parentNode.insertBefore(box,mb.nextSibling);}
// 上の帯に写すタブ（名前・件数・押す物）
function tabList(){return $$(".tabs button").map(function(b){var bb=b.querySelector("b"),n=bb?bb.childNodes[0].textContent:b.textContent,cn=bb&&bb.querySelector("small,span,i");
 return {el:b,name:n,count:cn?cn.textContent.replace(/[^0-9]/g,""):"",on:b.classList.contains("on"),off:false}})}
function prefList(){return $$("#flt button").map(function(b){return {el:b,name:b.textContent,on:b.classList.contains("on")}})}
function tabCount(){var b=$(".tabs button.on"),m=b&&b.textContent.match(/(\d+)\D*$/);return m?m[1]:""}
var ZONE="#flt,.tabs,.dflt";
// 本番のリストでだけ「地図で見る」が押された数を数える（試作ページ・オーナーは数えない）
function cnt1(k){try{if(/\/townnotes\//.test(location.pathname)||/github\.io$/.test(location.hostname)||localStorage.getItem("usagi_owner")==="1")return;var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true})}catch(e){}}
