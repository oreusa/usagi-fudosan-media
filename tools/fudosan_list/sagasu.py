# !! 11/10 からは tools/fudosan_list/kau.py が /sagasu を作る（予算から住める街）。このファイルを動かすと前の形に戻るので使わない
# 「住む街をさがす」ページ（TOWN links/sagasu.html と LIFE site/sagasu.html）を作る
# 11/9 オーナー「02を押したら検索欄になる…意味わからない」→ 文字を打たずに、府県タブ→街カードで選べるページに
# 街のデータは毎回 towns.json を読むので、地価が変わってもこのページは作り直さなくてよい
import os, sys
R = os.path.dirname(os.path.abspath(__file__)) + "/../../"
AK = sys.argv[1] if len(sys.argv) > 1 else R + "../akari-auto/"
SITES = [
 dict(out=R + "links/sagasu.html", a="assets/", area="関西", n="205", base="https://townnote.pages.dev",
      order=["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"],
      col={"大阪": "#B97A62", "京都": "#8A7495", "兵庫": "#4F6681", "奈良": "#6F8C68", "滋賀": "#5F8F98", "和歌山": "#C4925A"},
      full={"大阪": "大阪府", "京都": "京都府", "兵庫": "兵庫県", "奈良": "奈良県", "滋賀": "滋賀県", "和歌山": "和歌山県"},
      js='<script src="assets/night.js?v=27"></script><script src="assets/menu.js?v=49" defer></script><script src="assets/v2sub.js?v=12" defer></script>',
      logo="assets/logo-s.png?v=2", back="fudosan-list", backn="関西不動産リスト", brand="TOWN NOTE"),
 dict(out=AK + "site/sagasu.html", a="/assets/", area="関東", n="329", base="https://lifenote-kanto.pages.dev",
      order=["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"],
      col={"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A", "栃木": "#D2697E", "群馬": "#9C7BB8"},
      full={"東京": "東京都", "神奈川": "神奈川県", "埼玉": "埼玉県", "千葉": "千葉県", "茨城": "茨城県", "栃木": "栃木県", "群馬": "群馬県"},
      js='<script src="/assets/night.js?v=16"></script><script src="/assets/menu.js?v=34" defer></script><script src="/assets/v2sub.js?v=13" defer></script>',
      logo="/logo-s.png", back="/fudosan-list", backn="関東不動産リスト", brand="LIFE NOTE"),
]
import json
for S in SITES:
    title = f"住む街をさがす【2026年】{S['area']}{S['n']}の街の地価と売り出し中の物件｜{S['brand']}"
    desc = f"{S['area']}{S['n']}の街を、府県ごとに地価の上がり方で並べました。街を選ぶと、街の値段と、いま売り出し中の物件が見られます。"
    tabs = "".join(f'<button type="button" data-p="{p}" style="--c:{S["col"][p]}">{p}</button>' for p in S["order"])
    h = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{S['base']}/sagasu">
<meta property="og:title" content="住む街をさがす｜{S['area']}{S['n']}の街"><meta property="og:description" content="{desc}">
<link rel="icon" href="{S['a']}ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622;padding-bottom:84px}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.s3h{{display:flex;align-items:center;gap:12px;padding:26px 0 0}}.s3h .en{{font-family:Jost,sans-serif;font-size:11.5px;letter-spacing:.32em;color:#9C8775}}.s3h h1{{font-family:"Shippori Mincho",serif;font-size:23px;font-weight:600;letter-spacing:.08em;margin:2px 0 0}}
.ld{{font-family:"Shippori Mincho",serif;font-size:15px;line-height:1.9;margin:14px 0 16px}}
.tb{{position:sticky;top:0;z-index:5;background:#F4F4F6;margin:0 -16px;padding:10px 16px;display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}}.tb::-webkit-scrollbar{{display:none}}
.tb button{{flex:0 0 auto;font:inherit;font-size:14px;font-weight:700;padding:9px 15px;border-radius:99px;border:1.5px solid #DADADA;background:#fff;color:#5E544D;cursor:pointer}}
.tb button.on{{border-color:var(--c);background:var(--c);color:#fff}}
.hd{{display:flex;justify-content:space-between;align-items:baseline;margin:16px 2px 8px;font-size:12.5px;color:#857A70}}.hd b{{font-family:"Shippori Mincho",serif;font-size:17px;color:#2B2622}}
.tl{{display:grid;gap:8px}}
.tc{{display:flex;align-items:center;gap:12px;text-decoration:none;color:#2B2622;background:#fff;border:1px solid #E3E3E3;border-left:4px solid var(--c);border-radius:12px;padding:12px 14px}}
.tc .rk{{flex:0 0 30px;font-family:Jost,sans-serif;font-size:13px;color:#9C8775;text-align:center}}
.tc .nm{{flex:1;min-width:0}}.tc .nm b{{display:block;font-size:16px}}.tc .nm small{{display:block;font-size:12px;color:#857A70;margin-top:2px}}
.tc .pc{{text-align:right;font-family:Jost,sans-serif;font-size:17px;font-weight:500;color:var(--c)}}.tc .pc small{{display:block;font-family:"Zen Kaku Gothic New";font-size:10.5px;color:#9C8775;font-weight:500}}
.tc:after{{content:"→";font-family:Jost;color:#9C8775}}
.nt{{font-size:11.5px;color:#857A70;line-height:1.8;margin:14px 2px 0}}
.back{{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.ft{{text-align:center;font-size:10px;color:#8C7B6E;margin-top:30px}}
</style>{S['js']}</head><body><div class="wrap">
<div class="s3h"><img src="{S['logo']}" width="52" height="52" alt="ロゴ"><div><div class="en">FIND YOUR TOWN</div><h1>住む街をさがす</h1></div></div>
<p class="ld">街を選ぶと、街の値段と、いま売り出し中の物件が見られます。</p>
<div class="tb" id="tb">{tabs}</div>
<div class="hd"><b id="hp"></b><span id="hn"></span></div>
<div class="tl" id="tl"></div>
<p class="nt">並びは、住宅地の地価が1年でどれだけ動いたか（令和8年地価公示・府県の公式の資料）の順です。</p>
<a class="back" href="{S['back']}">{S['backn']}へ戻る</a>
<div class="ft">TOWN NOTE</div></div>
<script>(function(){{
var FULL={json.dumps(S['full'], ensure_ascii=False)},T=[],tb=document.getElementById("tb"),tl=document.getElementById("tl");
function pct(x){{return x==null?"—":(x>0?"+":"")+x.toFixed(1)+"%"}}
function E(s){{return String(s).replace(/[&<>"]/g,function(c){{return{{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]}})}}
function show(p,save){{[].forEach.call(tb.children,function(b){{b.className=b.dataset.p===p?"on":""}});
 var c=tb.querySelector('[data-p="'+p+'"]').style.getPropertyValue("--c"),L=T.filter(function(t){{return t.p===p}}).sort(function(a,b){{return a.rk-b.rk}});
 document.getElementById("hp").textContent=FULL[p];document.getElementById("hn").textContent=L.length+"の街";
 tl.innerHTML=L.map(function(t){{return '<a class="tc" style="--c:'+c+'" href="/machi/'+t.id+'" data-k="住む街をさがす｜'+E(t.n)+'"><span class="rk">'+t.rk+'</span><span class="nm"><b>'+E(t.n)+'</b><small>前の年 '+pct(t.r7)+'・'+E(FULL[p])+'で'+t.rk+'位／'+t.of+'</small></span><span class="pc"><small>地価 1年</small>'+pct(t.r8)+'</span></a>'}}).join("");
 if(save)try{{history.replaceState(null,"","?p="+encodeURIComponent(p))}}catch(e){{}}}}
tb.addEventListener("click",function(e){{var b=e.target.closest("button");if(b){{show(b.dataset.p,1);window.scrollTo(0,tb.offsetTop-0)}}}});
fetch("{S['a']}towns.json").then(function(r){{return r.json()}}).then(function(d){{T=d.towns||d;var q=new URLSearchParams(location.search).get("p");show(FULL[q]?q:tb.children[0].dataset.p)}});
try{{if(localStorage.getItem("usagi_owner")!=="1")navigator.sendBeacon&&navigator.sendBeacon("/c",JSON.stringify({{k:"表示：住む街をさがす"+(document.referrer&&document.referrer.indexOf(location.host)<0?"（外から）":"")}}))}}catch(x){{}}
}})();</script>
</body></html>
"""
    open(S["out"], "w", encoding="utf-8").write(h)
    print("ok", S["out"])
