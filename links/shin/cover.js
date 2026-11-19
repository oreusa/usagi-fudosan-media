/* 新しいHP：表紙（/）。役目＝関西のおでかけ・家と土地・おかいもの・開店閉店へ、1タップで入れる入口。
   こだわり＝一番上の府県の地図（いま開催中の数）。押すとその府県のおでかけへ。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,TD=S_.TD,dd=S_.dd,D=S_.data;
var PC={"大阪":"#D9775A","京都":"#9C7BB8","兵庫":"#4F86C6","奈良":"#5FA06A","滋賀":"#3FA3B5","和歌山":"#E09A3E"},FL={"大阪":"#F7D9CC","京都":"#E6DBF1","兵庫":"#D6E4F5","奈良":"#D8ECD4","滋賀":"#D0EBEF","和歌山":"#F8E4C4"};
var LB={"兵庫":[62,105],"京都":[122,78],"滋賀":[176,92],"大阪":[118,165],"奈良":[156,178],"和歌山":[118,215]},SL={"大阪":"osaka","京都":"kyoto","兵庫":"hyogo","奈良":"nara","滋賀":"shiga","和歌山":"wakayama"};
function avg(b){try{var h=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)}),hd=h[0]|h[1]<<8|h[2]<<16,l=(hd&63)/63,p=((hd>>6)&63)/31.5-1,q=((hd>>12)&63)/31.5-1,bb=l-2/3*p,r=(3*l-bb+q)/2,g=r-q;
  var f=function(v){return Math.round(255*Math.max(0,Math.min(1,v)))};return "rgb("+f(r)+","+f(g)+","+f(bb)+")"}catch(e){return ""}}
var DT=dd(TD),tot=0;Object.keys(D.pc).forEach(function(p){tot+=D.pc[p]});
S_.main.innerHTML='<div class="wrap"><section class="hero"><h1 class="h1t">関西のおでかけと、家と土地</h1><p class="h1p">大阪・京都・兵庫・奈良・滋賀・和歌山を、公式の発表と数字で</p>'+
 '<p class="dl">'+(DT.getUTCMonth()+1)+'月'+DT.getUTCDate()+'日（'+"日月火水木金土"[DT.getUTCDay()]+'）<span>いま開催中 <b data-n="'+tot+'">0</b>件</span></p></section>'+
 '<div class="cmap" id="cmap"><svg viewBox="10 15 200 250" role="img" aria-label="府県の地図。押すとその府県のおでかけへ"><g class="nb">'+D.map.nb.map(function(d){return '<path d="'+d+'"/>'}).join("")+'</g>'+
  Object.keys(D.map.pref).map(function(p){return '<a href="/odekake-'+SL[p]+'" aria-label="'+p+'のおでかけ '+(D.pc[p]||0)+'件"><path class="pf" d="'+D.map.pref[p]+'" style="--f:'+FL[p]+';--c:'+PC[p]+'"/></a>'}).join("")+
  Object.keys(LB).map(function(p){return '<g class="cl" transform="translate('+LB[p][0]+' '+LB[p][1]+')"><text class="pl" style="fill:'+PC[p]+'">'+p+'</text><text class="pn" y="11">'+(D.pc[p]||0)+'件</text></g>'}).join("")+'</svg>'+
  '<p class="cmh">府県を押すと、その府県のおでかけへ</p></div>'+
 '<div class="sec"><h2>いま開催中</h2><a class="sm" href="/odekake">すべて見る</a></div><div class="crow">'+D.top.map(function(x){return '<a class="cd" href="'+(x.o?"/o/"+x.o:"/odekake")+'"><div class="im" style="background-color:'+(x.th?avg(x.th):"var(--chip)")+'"><img alt="" loading="lazy" src="/assets/ph/'+x.im+'"></div><div class="lb"><span>'+esc(x.p)+'</span></div><h4>'+esc(x.t)+'</h4><div class="dt">'+S_.md(x.e)+'まで</div></a>'}).join("")+'</div>'+
 '<div class="sec"><h2>見る</h2></div><div class="cgo">'+D.go.map(function(g){return '<a href="'+g.u+'"><span class="ci">'+(S_.IC[g.ic]||"")+'</span><span class="ct"><b>'+esc(g.t)+'</b><small>'+esc(g.s)+'</small></span><span class="cn"><b>'+esc(g.n)+'</b><small>'+esc(g.nu)+'</small></span></a>'}).join("")+'</div>'+
 '<nav class="also2" aria-label="ほかのページ"><small>季節と、ほかのページ</small>'+D.more.map(function(a){return '<a href="'+a[1]+'">'+esc(a[0])+'<i>→</i></a>'}).join("")+'</nav>'+
 '<div class="cfl"><small>インスタ・Threads・X で、毎日おしらせしています</small><div>'+D.sns.map(function(s){return '<a href="'+s[1]+'" target="_blank" rel="noopener">'+esc(s[0])+'</a>'}).join("")+'</div></div></div>';
S_.counts(S_.main);
var ims=$$("img",S_.main);ims.forEach(function(im){if(im.complete)im.classList.add("ld");else im.onload=function(){im.classList.add("ld")}});
S_.onNav(function(a){if(a==="map")scrollTo({top:$("#cmap").getBoundingClientRect().top+scrollY-60,behavior:"smooth"})});
S_.ready();
})();
