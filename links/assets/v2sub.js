/* 11/1 オーナー「統一してるんだからちゃんと見ろよ」→ トップ以外のページにも、トップと同じ下のバー（右端に MENU）を出す。
   開催中・これから・地図はトップへ移動して開く（v2.js が ?v2t= を読む）。 */
(function(){
var st=document.createElement("style");st.textContent=":root{--ink:#1C1C1C;--acc:#3A2F28}#v2bar{position:fixed;left:10px;right:10px;bottom:calc(10px + env(safe-area-inset-bottom));z-index:9980;display:flex;align-items:stretch;background:rgba(255,255,255,.97);border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.14);overflow:hidden;transform:translateY(140%);transition:transform .3s;max-width:460px;margin:0 auto}#v2bar.on{transform:none}#v2bar button,#v2bar a{flex:1;text-decoration:none;border:0;background:none;padding:10px 2px 9px;font-family:\"Zen Kaku Gothic New\",sans-serif;font-size:11px;font-weight:700;color:var(--ink);letter-spacing:.02em;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px}#v2bar a svg,#v2bar button svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}#v2bar a.cur{color:var(--acc)}#v2bar a.cur span{border-bottom:2px solid var(--acc)}#v2bar button.mn{flex:0 0 72px;background:var(--acc);color:#fff;font-family:Jost,sans-serif;letter-spacing:.14em;font-size:10.5px}#v2bar button.mn{justify-content:center;gap:7px}#v2bar button.mn i{display:block;width:18px;height:1.5px;background:#fff;box-shadow:0 -5px 0 #fff,0 5px 0 #fff;margin:5px 0 3px}html.v2bar-on #umenu{opacity:0;pointer-events:none;transition:opacity .25s}html.v2bar-on #umenu{display:none!important}html[style*=\"overflow: hidden\"] #v2bar{display:none}html.v2bar-on #utheme{right:12px}body{padding-bottom:84px}";document.head.appendChild(st);
var I={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',up:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
function goF(){
/* 11/1 オーナー「バーの中身も不動産リストで、完全別項目で分けろよ」→ 不動産リスト用の下のバー。
   上のタブ（地価・人口…）と同じ物は並べない。街で探す・ランキング・新着・売る前に。 */
var F={q:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>',rk:'<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V5M16 20v-7M22 20H2"/></svg>',nw:'<svg viewBox="0 0 24 24"><path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4 6.7 19.4l1.2-6L3.4 9.3l6-.7z"/></svg>',ur:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
var here=/\/fudosan-list/.test(location.pathname),rk=/\/chika-osaka/.test(location.pathname);
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
bar.innerHTML='<a data-m="q">'+F.q+'<span>街で探す</span></a><a data-h="/chika-osaka"'+(rk?' class="cur"':'')+'>'+F.rk+'<span>ランキング</span></a><a data-m="new">'+F.nw+'<span>新着</span></a><a data-h="/uru.html">'+F.ur+'<span>売る前に</span></a><button class="mn" type="button"><i></i>MENU</button>';
bar.querySelectorAll("a").forEach(function(a){a.setAttribute("data-k","下のバー｜"+a.textContent);
 if(a.dataset.h){a.href=a.dataset.h;return;}
 if(here&&window.FQ){a.href="#";a.onclick=function(e){e.preventDefault();window.FQ.open(a.dataset.m);};}
 else a.href="/fudosan-list?fq="+a.dataset.m;});
bar.querySelector(".mn").onclick=function(){var m=document.getElementById("umenu");if(m)m.click();};
document.body.appendChild(bar);bar.classList.add("on");document.documentElement.classList.add("v2bar-on");
window.V2BAR=bar;
}
function go(){
if(/\/(fudosan-list|chika-osaka)/.test(location.pathname))return goF();
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
var inn=/\/tomari/.test(location.pathname);
bar.innerHTML='<a data-h="/?v2t=0">'+I.now+'<span>開催中</span></a><a data-h="/?v2t=1">'+I.up+'<span>これから</span></a><a data-h="/?v2t=map">'+I.map+'<span>地図</span></a><a data-h="/tomari.html"'+(inn?' class="cur"':'')+'>'+I.inn+'<span>泊まり</span></a><button class="mn" type="button"><i></i>MENU</button>';
bar.querySelectorAll("a").forEach(function(a){a.href=a.dataset.h;a.setAttribute("data-k","下のバー｜"+a.textContent);});
bar.querySelector(".mn").onclick=function(){var m=document.getElementById("umenu");if(m)m.click();};
document.body.appendChild(bar);bar.classList.add("on");document.documentElement.classList.add("v2bar-on");
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go();
})();
