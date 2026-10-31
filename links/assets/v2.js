(function(){
var T=new Date(Date.now()+9*36e5).toISOString().slice(0,10),WD=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
function fd(s){var d=new Date(s+"T00:00:00Z");return (d.getUTCMonth()+1)+"."+String(d.getUTCDate()).padStart(2,"0")+" "+WD[d.getUTCDay()];}
document.querySelectorAll(".paper .it .card").forEach(function(c){
  if(c.querySelector(".v2c"))return;var d=c.querySelector(".d"),bd=c.querySelector(".bd")||c;if(!d)return;
  var pref=c.dataset.pref||"",s=c.dataset.s,e=c.dataset.e,free=!!d.querySelector(".tg.f");
  var st=s&&s>T?"これから":(e?"開催中":"");
  var h='';if(pref)h+='<span class="p" data-p="'+pref+'">'+pref+'</span>';if(st)h+='<span'+(st==="開催中"?' class="on"':'')+'>'+st+'</span>';if(free)h+='<span class="f">無料</span>';
  var cx=document.createElement("div");cx.className="v2c";cx.innerHTML=h;
  var dt=document.createElement("div");dt.className="v2d";
  dt.textContent=s&&s>T?fd(s)+(e&&e!==s?" — "+fd(e):""):(e?fd(e)+" まで":d.textContent.replace(pref,"").replace("無料","").trim());
  bd.insertBefore(dt,bd.firstChild);bd.insertBefore(cx,dt);
});
document.addEventListener("click",function(ev){var p=ev.target.closest&&ev.target.closest(".v2c span.p");if(!p)return;ev.preventDefault();ev.stopPropagation();
  var b=[].find.call(document.querySelectorAll("#flt button"),function(x){return x.textContent.trim()===p.dataset.p});if(b){b.click();var f=document.getElementById("flt");scrollTo({top:f.getBoundingClientRect().top+scrollY-70,behavior:"smooth"});}},true);
/* 一覧の見出し */
var tabs=document.querySelector(".blk.b-now .tabs");
function head(){var on=tabs&&tabs.querySelector("button.on");if(!on)return;var en=on.childNodes[0].textContent.trim(),jp=on.querySelector("b").childNodes[0].textContent.trim(),n=on.querySelector("i").textContent;
  var h=document.querySelector(".v2h");if(!h){h=document.createElement("div");h.className="v2h";var m=document.querySelector(".tnbtn")||document.querySelector(".paper .it");m.parentNode.insertBefore(h,m);}
  h.innerHTML='<span>'+jp+'のおでかけ</span><small>'+en+'</small><b>'+n+'件</b>';}
setTimeout(head,300);if(tabs)tabs.addEventListener("click",function(){setTimeout(head,50)});
/* 下のボタン列 */
var I={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',up:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
bar.innerHTML='<button data-t="0" class="cur">'+I.now+'<span>開催中</span></button><button data-t="1">'+I.up+'<span>これから</span></button><button data-a="map">'+I.map+'<span>地図</span></button><button data-a="inn">'+I.inn+'<span>泊まり</span></button><button class="mn" data-a="menu"><i></i>MENU</button>';
document.body.appendChild(bar);
function syncBar(){var on=tabs&&[].indexOf.call(tabs.children,tabs.querySelector("button.on"));bar.querySelectorAll("button[data-t]").forEach(function(b){b.classList.toggle("cur",+b.dataset.t===on)});}
bar.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.dataset.t){tabs.children[+b.dataset.t].click();syncBar();head();var t=document.querySelector(".blk.b-now");scrollTo({top:t.getBoundingClientRect().top+scrollY-10,behavior:"smooth"});}
  else if(b.dataset.a==="map"){var m=document.querySelector(".tnbtn");if(m)m.click();}
  else if(b.dataset.a==="inn")location.href="/tomari.html";
  else document.getElementById("umenu").click();});
var tk=0;addEventListener("scroll",function(){if(tk)return;tk=1;requestAnimationFrame(function(){tk=0;var o=scrollY>500;bar.classList.toggle("on",o);document.documentElement.classList.toggle("v2bar-on",o);});},{passive:true});
})();
