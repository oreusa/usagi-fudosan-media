/* 10/31 オーナー「夜と昼の切り替えにしたら？」
   夜（18時〜翌6時・日本時間）は暗い見た目。右上のボタンで（地図を開いている間は隠す）昼／夜を切り替え（選んだ方を覚える）。
   色は全部のページで手で決めているので、ページ全体を反転して暗くし、写真・ロゴ・地図の色は元に戻す。 */
(function(){
  var K="usagi_theme",d=document.documentElement;
  function pick(){try{var v=localStorage.getItem(K);if(v==="day"||v==="night")return v;}catch(e){}
    var h=new Date(Date.now()+9*36e5).getUTCHours();return (h>=18||h<6)?"night":"day";}
  function set(v){d.classList.toggle("night",v==="night");if(b)b.setAttribute("aria-label",v==="night"?"昼の見た目にする":"夜の見た目にする");if(b)b.innerHTML=v==="night"?SUN:MOON;}
  var css="html.night{background:#fff;filter:invert(.8) hue-rotate(180deg)}"+
    "html.night img,html.night video,html.night picture,html.night svg image,html.night .nofilt,html.night .tnbtn .mm{filter:invert(1) hue-rotate(180deg)}"+
    "html.night .head img{background:#fff;border-radius:50%}"+
    "#daynight{position:fixed;top:12px;right:12px;z-index:9999;width:38px;height:38px;border-radius:50%;border:1px solid #DADADA;background:#fff;color:#5B5450;display:flex;align-items:center;justify-content:center;padding:0;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06)}"+
    "#daynight svg{width:18px;height:18px}"+
    "html[style*=\"overflow: hidden\"] #daynight{display:none}";
  var MOON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>';
  var SUN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var st=document.createElement("style");st.textContent=css;(document.head||d).appendChild(st);
  var b=null;set(pick());
  function btn(){b=document.createElement("button");b.id="daynight";b.type="button";document.body.appendChild(b);set(pick());
    b.addEventListener("click",function(){var v=d.classList.contains("night")?"day":"night";try{localStorage.setItem(K,v);}catch(e){}set(v);});}
  if(document.body)btn();else document.addEventListener("DOMContentLoaded",btn);
})();
