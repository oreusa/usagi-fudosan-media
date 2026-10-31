/* 10/31 オーナー「三本線を作って項目を選べるように」「分かりやすく、使いやすく、細かいところまで」
   全ページ共通のメニュー。右上の三本線 → 右から出る紙。昼と夜の切り替えもここ（night.js）。
   ページを足すときは L に1行足すだけ。押された数は /c に「メニュー｜名前」で数える。 */
(function(){
  var P=location.pathname.replace(/^\/townnotes\//,"/"),here=
    /^\/(index\.html)?$/.test(P)?"list":/^\/illumination/.test(P)?"illumi":/^\/tomari/.test(P)?"tomari":/^\/(fudosan|uru|gyosha)/.test(P)?"fudosan":"";
  var L=[
    ["LIST","list","/","関西おでかけリスト","開催中・これからのおでかけ"],
    ["MAP","map","/#map","地図で見る","関西の地図から、近くのおでかけを"],
    ["ILLUMINATION","illumi","/illumination.html","イルミネーション日程","2026-2027　府県ごとの日程と無料の所"],
    ["STAY","tomari","/tomari.html","泊まりで行くおでかけ","遠くのおでかけと、近くの宿"],
    ["-","CONTACT"],
    ["REAL ESTATE","fudosan","/fudosan.html","不動産のご相談","売却・査定、売る前に大事なこと"],
    ["LISTING","listing","https://ig.me/m/fudousan_ai_si","おでかけ掲載","新しいお店やイベントのご紹介"]
  ];
  var css=
  "#umenu{position:fixed;top:12px;right:12px;z-index:9990;width:42px;height:42px;border-radius:50%;border:1px solid #DADADA;background:rgba(255,255,255,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:0;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.07);-webkit-tap-highlight-color:transparent}"+
  "#umenu i{display:block;width:16px;height:1.5px;background:#3A3330;border-radius:1px}"+
  "#umenu:active{transform:scale(.94)}"+
  "html[style*=\"overflow: hidden\"] #umenu{display:none}"+
  "#umask{position:fixed;inset:0;z-index:9991;background:rgba(30,26,24,.32);opacity:0;pointer-events:none;transition:opacity .25s}"+
  "#umask.on{opacity:1;pointer-events:auto}"+
  "#upan{position:fixed;top:0;right:0;bottom:0;z-index:9992;width:min(86vw,360px);background:#fff;transform:translateX(102%);transition:transform .28s cubic-bezier(.2,.7,.2,1);display:flex;flex-direction:column;box-shadow:-8px 0 30px rgba(0,0,0,.08);font-family:'Zen Kaku Gothic New',sans-serif;color:#2B2622}"+
  "#upan.on{transform:none}"+
  "#upan .uh{display:flex;align-items:center;gap:10px;padding:16px 14px 14px 20px;border-bottom:1px solid #EDEDED}"+
  "#upan .uh img{width:34px;height:34px}"+
  "#upan .uh b{flex:1;font-family:Jost,sans-serif;font-weight:400;font-size:10.5px;letter-spacing:.32em;color:#8C7B6E}"+
  "#upan .ux{width:42px;height:42px;border:0;background:none;font-size:24px;line-height:1;color:#3A3330;cursor:pointer;border-radius:50%}"+
  "#upan .ux:active{background:#F3F3F3}"+
  "#upan nav{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:6px 0 10px}"+
  "#upan .ug{font-family:Jost,sans-serif;font-size:9.5px;letter-spacing:.34em;color:#A09488;padding:18px 20px 6px}"+
  "#upan a.ui{display:block;position:relative;text-decoration:none;color:#2B2622;padding:13px 44px 13px 20px;border-top:1px solid #F1F1F1}"+
  "#upan a.ui:first-of-type{border-top:0}"+
  "#upan a.ui:active{background:#F7F7F7}"+
  "#upan a.ui small{display:block;font-family:Jost,sans-serif;font-size:9px;letter-spacing:.3em;color:#9C8775}"+
  "#upan a.ui span{display:block;font-family:'Shippori Mincho',serif;font-weight:600;font-size:16.5px;letter-spacing:.08em;margin-top:3px}"+
  "#upan a.ui em{display:block;font-style:normal;font-size:11.5px;color:#857A70;margin-top:3px;letter-spacing:.02em}"+
  "#upan a.ui:after{content:'\\2192';position:absolute;right:20px;top:50%;transform:translateY(-50%);font-family:Jost,sans-serif;color:#9C8775}"+
  "#upan a.ui.cur{background:#F7F7F7}"+
  "#upan a.ui.cur:before{content:'';position:absolute;left:0;top:12px;bottom:12px;width:3px;background:#2B2622}"+
  "#upan a.ui.cur:after{content:'いまのページ';font-family:'Zen Kaku Gothic New',sans-serif;font-size:10px;color:#8C7B6E}"+
  "#upan .ut{display:flex;align-items:center;justify-content:space-between;margin:8px 20px 0;padding:14px 0;border-top:1px solid #EDEDED;font-size:13.5px}"+
  "#upan .ut em{display:block;font-style:normal;font-size:11px;color:#8C7B6E;margin-top:2px}"+
  "#upan .sw{position:relative;width:50px;height:30px;border-radius:99px;border:0;background:#D9D9D9;cursor:pointer;flex:none;transition:background .2s}"+
  "#upan .sw:after{content:'';position:absolute;top:3px;left:3px;width:24px;height:24px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.2);transition:transform .2s}"+
  "#upan .sw[aria-checked=true]{background:#2B2622}"+
  "#upan .sw[aria-checked=true]:after{transform:translateX(20px)}"+
  "#upan .us{display:flex;gap:22px;justify-content:center;padding:14px 20px calc(18px + env(safe-area-inset-bottom));border-top:1px solid #EDEDED}"+
  "#upan .us a{font-family:Jost,sans-serif;font-size:13px;letter-spacing:.06em;color:#2B2622;text-decoration:none;border-bottom:1px solid #2B2622;padding:6px 0 2px}"+
  "html.umenu-open,html.umenu-open body{overflow:hidden}"+
  "@media (prefers-reduced-motion:reduce){#upan,#umask{transition:none}}";
  function ck(k){try{if(localStorage.getItem("usagi_owner")==="1")return;}catch(e){}try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function openMap(){var n=0;(function t(){var b=document.querySelector(".tnbtn");if(b){b.click();return;}if(++n<40)setTimeout(t,100);})();}
  function build(){
    var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
    var btn=document.createElement("button");btn.id="umenu";btn.type="button";btn.setAttribute("aria-label","メニューを開く");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","upan");btn.innerHTML="<i></i><i></i><i></i>";
    var mask=document.createElement("div");mask.id="umask";
    var pan=document.createElement("div");pan.id="upan";pan.setAttribute("role","dialog");pan.setAttribute("aria-modal","true");pan.setAttribute("aria-label","メニュー");pan.setAttribute("aria-hidden","true");
    var h='<div class="uh"><img src="/assets/logo-s.png?v=2" alt=""><b>USAGI TOWN NOTES</b><button class="ux" type="button" aria-label="メニューを閉じる">×</button></div><nav><div class="ug">KANSAI ODEKAKE</div>';
    L.forEach(function(x){
      if(x[0]==="-"){h+='<div class="ug">'+x[1]+'</div>';return;}
      var cur=x[1]===here,ext=/^https?:/.test(x[2]);
      h+='<a class="ui'+(cur?" cur":"")+'" data-k="'+x[1]+'" href="'+x[2]+'"'+(ext?' target="_blank" rel="noopener"':"")+(cur?' aria-current="page"':"")+'><small>'+x[0]+'</small><span>'+esc(x[3])+'</span><em>'+esc(x[4])+'</em></a>';
    });
    h+='<div class="ut"><div>夜の見た目<em>暗い背景で、目にやさしく</em></div><button class="sw" type="button" role="switch" aria-label="夜の見た目"></button></div></nav>'+
      '<div class="us"><a href="https://www.instagram.com/fudousan_ai_si/" target="_blank" rel="noopener">Instagram</a><a href="https://www.threads.com/@fudousan_ai_si" target="_blank" rel="noopener">Threads</a><a href="https://x.com/fudosan_ai_si" target="_blank" rel="noopener">X</a></div>';
    pan.innerHTML=h;
    document.body.appendChild(btn);document.body.appendChild(mask);document.body.appendChild(pan);
    var sw=pan.querySelector(".sw"),last=null;
    function syncSw(){var n=window.usagiTheme&&window.usagiTheme.get()==="night";sw.setAttribute("aria-checked",n?"true":"false");}
    syncSw();document.addEventListener("usagi-theme",syncSw);
    function open(){last=document.activeElement;document.documentElement.classList.add("umenu-open");mask.classList.add("on");pan.classList.add("on");pan.setAttribute("aria-hidden","false");btn.setAttribute("aria-expanded","true");setTimeout(function(){pan.querySelector(".ux").focus();},50);ck("メニュー｜開く");}
    function close(){document.documentElement.classList.remove("umenu-open");mask.classList.remove("on");pan.classList.remove("on");pan.setAttribute("aria-hidden","true");btn.setAttribute("aria-expanded","false");if(last&&last.focus)last.focus();}
    btn.addEventListener("click",open);mask.addEventListener("click",close);pan.querySelector(".ux").addEventListener("click",close);
    document.addEventListener("keydown",function(e){if(e.key==="Escape"&&pan.classList.contains("on"))close();});
    /* 右へなでて閉じる */
    var sx=null;pan.addEventListener("touchstart",function(e){sx=e.touches[0].clientX;},{passive:true});
    pan.addEventListener("touchend",function(e){if(sx!==null&&e.changedTouches[0].clientX-sx>70)close();sx=null;},{passive:true});
    sw.addEventListener("click",function(){if(!window.usagiTheme)return;var v=window.usagiTheme.get()==="night"?"day":"night";window.usagiTheme.set(v);ck("メニュー｜"+(v==="night"?"夜":"昼"));});
    pan.querySelectorAll("a.ui").forEach(function(a){a.addEventListener("click",function(e){
      var k=a.getAttribute("data-k");ck("メニュー｜"+a.querySelector("span").textContent);
      if(k===here&&k!=="map"){e.preventDefault();close();window.scrollTo({top:0,behavior:"smooth"});return;}
      if(k==="map"&&here==="list"){e.preventDefault();close();setTimeout(openMap,280);}
    });});
    if(here==="list"&&location.hash==="#map"){try{history.replaceState(null,"",location.pathname+location.search);}catch(e){}openMap();}
  }
  if(document.body)build();else document.addEventListener("DOMContentLoaded",build);
})();
