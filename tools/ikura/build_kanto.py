#!/usr/bin/env python3
"""関東 LIFE の「お家はいくらで売れる？」（akari site/ikura.html を月が作る。kau.py と同じ形）。
関東は実際に売れた値段の市区別の表が無いので、令和8年地価公示（akari data/kanto_chika）から目安を出す。
マンション＝kau.py と同じ式（近畿レインズの土地単価→中古マンション㎡単価の関係を、東京カンテイ2025年の都県平均で補正）。
土地・一戸建ての土地の分＝地価公示の住宅地の平均価格×広さ。
関東はアフィリエイトが本来（オーナー 11/9）。ボタンは A8 ざっくりAI査定＋（提携済み 11/13）。人に聞く道は小さく残す。上下に広告（PR）の断り。
使い方：python3 tools/ikura/build_kanto.py [akari-auto のパス]
"""
import csv, glob, json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/"
AK = sys.argv[1] if len(sys.argv) > 1 else R + "../akari-auto/"
src = open(R + "tools/fudosan_list/kau.py", encoding="utf-8").read()
seg = src[src.index("# ---- LIFE の数字"):src.index("# ---- いま開催")]
ns = {"R": R, "AK": AK, "csv": csv, "glob": glob, "json": json, "os": os, "math": math}
exec(compile(seg, "kau.py", "exec"), ns)
price, FM, ADJ, L = ns["price"], ns["FM"], ns["ADJ"], ns["L"]
A8 = "4BGH3I+E2NY4I+5Y9M+5YJRM"  # ざっくりAI査定＋（akari scripts/fudosan_kanto.py A8_ZAKU と同じ）
order = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]
D = {}
for t in L:
    k = (t["p"], t["n"])
    if k not in price:
        continue
    x = price[k] / 10000  # 万円/㎡
    D[t["p"] + "|" + t["n"]] = {"id": t["id"], "l": round(x, 2), "m": round(FM[0] * x ** FM[1] * ns["ADJ"].get(t["p"], 1.0), 2)}
keys = sorted(D, key=lambda k: (order.index(k.split("|")[0]) if k.split("|")[0] in order else 9, k))
data = json.dumps({k: D[k] for k in keys}, ensure_ascii=False, separators=(",", ":"))
n = len(keys)
page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>お家はいくらで売れる？ 関東{n}の市区の地価から目安｜LIFE NOTE</title>
<meta name="description" content="関東{n}の市区町村で、国の地価公示（令和8年）から、マンション・一戸建ての土地・土地の売れそうな値段の目安を30秒で出せます。無料・名前も要りません。">
<link rel="canonical" href="https://lifenote-kanto.pages.dev/ikura">
<link rel="icon" href="/logo-s.png"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 120px}}
.head{{text-align:center;margin:0 -16px;padding:30px 16px 26px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px),#FFFFFF}}
.head img{{width:60px}}
.en{{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:25px;letter-spacing:.14em;color:#231E1B;margin:14px 0 10px;font-feature-settings:"palt"}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}}
.pr{{font-size:11px;color:#8C7B6E;margin:10px 0 0}}
.card{{border:1px solid #D9D9D9;background:#fff;padding:18px 18px 20px;margin-top:22px}}
.q{{font-family:Jost;font-size:9.5px;letter-spacing:.32em;color:#9C8775;margin:0 0 8px}}
.q b{{font-family:"Zen Kaku Gothic New";font-size:14px;letter-spacing:.04em;color:#2B2622;margin-left:6px}}
.step+.step{{margin-top:18px;padding-top:16px;border-top:1px solid #EEE}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
.chips button{{font:inherit;font-size:14px;padding:10px 14px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:#2B2622;cursor:pointer}}
.chips button[aria-pressed=true]{{background:#3A332E;color:#fff;border-color:#3A332E}}
select,input{{font:inherit;font-size:16px;width:100%;box-sizing:border-box;padding:12px;border:1px solid #D9D2CB;border-radius:10px;background:#fff;color:#2B2622}}
.row{{display:flex;gap:8px;align-items:center}}.row span{{white-space:nowrap;font-size:14px}}
.hint{{font-size:12px;color:#8C7B6E;margin:6px 0 0;line-height:1.7}}
.res{{margin-top:22px;border:1px solid #3A332E;padding:20px 18px;display:none;position:relative}}
.res .lb{{font-size:12px;color:#6B6058}}
.res .big{{font-family:"Shippori Mincho",serif;font-weight:700;font-size:32px;margin:6px 0 4px;color:#231E1B}}
.res .big small{{font-size:15px;font-weight:600}}
.res ul{{margin:12px 0 0;padding:0;list-style:none;font-size:13px;line-height:1.9;color:#3A332E}}
.res li:before{{content:"・"}}
.go{{display:block;background:#3A332E;color:#fff;border-radius:12px;padding:16px;margin:18px 0 6px;text-align:center;text-decoration:none;font-weight:700;font-size:15.5px}}
.go small{{display:block;font-weight:500;font-size:11.5px;opacity:.85;margin-top:4px}}
.sm{{font-size:12px;color:#8C7B6E;text-align:center;margin:8px 0 0;line-height:1.8}}.sm a{{color:#6B6058}}
.note{{font-size:11.5px;line-height:1.9;color:#8C7B6E;margin-top:22px}}
</style></head><body><div class="wrap">
<div class="head"><img src="/logo-s.png" alt="LIFE NOTE のロゴ" width="60" height="60"><div class="en">HOW MUCH</div><h1>お家はいくらで売れる？</h1>
<p class="sub">関東{n}の市区町村で、国の地価公示から<br>売れそうな値段の目安を出します。<br>無料・名前も要りません。30秒で終わります。</p><p class="pr">このページには広告（PR）を含みます</p></div>
<div class="card">
<div class="step"><p class="q">01<b>お家の種類</b></p><div class="chips" id="ty"><button type="button" data-v="m" aria-pressed="true">マンション</button><button type="button" data-v="k" aria-pressed="false">一戸建て</button><button type="button" data-v="t" aria-pressed="false">土地</button></div></div>
<div class="step"><p class="q">02<b>お家のある市区町村</b></p><select id="ci" aria-label="市区町村"></select></div>
<div class="step"><p class="q">03<b id="al">専有面積</b></p><div class="row"><input id="ar" type="number" inputmode="decimal" min="10" max="2000" placeholder="例 70"><span>㎡</span></div><p class="hint">分からなければ空のままで大丈夫です（よくある広さで出します）。</p></div>
</div>
<div class="res" id="res" aria-live="polite"><div class="lb" id="rl"></div><div class="big" id="rb"></div><div class="lb" id="rh"></div><ul id="ru"></ul>
<a class="go" id="go" href="https://px.a8.net/svt/ejp?a8mat={A8}" rel="nofollow sponsored noopener" target="_blank" data-k="いくら｜AI査定">このお家の値段を、AIでくわしく見る（無料）<small>ざっくりAI査定＋（広告）・電話ラッシュなし</small></a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat={A8}" alt="" style="position:absolute;width:1px;height:1px;opacity:0">
<p class="sm">人に相談したい方は <a id="hito" href="/moushikomi?lite=1" data-k="いくら｜人に相談">こちら（無料・約1分）</a></p></div>
<p class="note">数字は、国土交通省「令和8年地価公示」の市区町村ごとの住宅地の平均価格（1㎡）から出した目安です。実際に売れた値段ではありません。マンション＝土地の値段と中古マンションの㎡単価の関係（近畿レインズ 2025年度）を当て、都県ごとに東京カンテイ「2025年 中古マンション70㎡換算価格」の平均に合わせて直した値×広さ。土地＝住宅地の平均価格×広さ。一戸建ては土地の分だけを出しています（建物は築年で大きく変わります）。幅は±20％です。査定ではありません。</p>
<p class="pr">このページのリンクの一部は広告（PR）です</p>
</div>
<script>var D={data};
(function(){{var $=function(i){{return document.getElementById(i)}},ty="m",ci=$("ci"),ar=$("ar"),F="direct";try{{F=sessionStorage.getItem("f")||"direct"}}catch(e){{}}
function c(k){{try{{if(localStorage.getItem("usagi_owner")==="1")return;navigator.sendBeacon("/c?f="+encodeURIComponent(F)+"&s=fudosan&k="+encodeURIComponent(String(k).slice(0,40)))}}catch(e){{}}}}
c("表示：いくら"+(document.referrer&&!/lifenote-kanto\\.pages/.test(document.referrer)?"（外から）":""));
var LB={{m:["専有面積","例 70","マンション",70],k:["土地の広さ","例 100","一戸建て",100],t:["土地の広さ","例 100","土地",100]}};
function fill(){{var cur=ci.value;ci.innerHTML='<option value="">市区町村を選んでください</option>';var pp="";Object.keys(D).forEach(function(k){{var p=k.split("|")[0];if(p!==pp){{var g=document.createElement("optgroup");g.label=p;ci.appendChild(g);pp=p}}var o=document.createElement("option");o.value=k;o.textContent=k.split("|")[1];ci.lastChild.appendChild(o)}});if(cur)ci.value=cur}}
function man(n){{return n>=10000?(Math.floor(n/1000)/10)+"億":Math.round(n).toLocaleString()}}
function calc(){{var k=ci.value,r=$("res");$("al").textContent=LB[ty][0];ar.placeholder=LB[ty][1];if(!k){{r.style.display="none";return}}
var x=D[k],a=parseFloat(ar.value),nm=k.split("|")[1],est,u;if(!(a>0))a=LB[ty][3];
if(ty==="m"){{est=x.m*a;u=["1㎡あたりの目安 "+x.m+"万円（中古マンション）","住宅地の平均 1㎡ "+x.l+"万円（地価公示）"];$("rh").textContent="目安の幅（駅からの近さ・築年・階で上下します）"}}
else{{est=x.l*a;u=["住宅地の平均 1㎡ "+x.l+"万円（地価公示）"];$("rh").textContent=ty==="k"?"土地の分の目安（建物の分は築年で変わるので、下のAI査定で確かめられます）":"目安の幅（形・道路・駅からの近さで上下します）"}}
$("rl").textContent=nm+"の"+LB[ty][2]+"（"+Math.round(a)+"㎡）";
$("rb").innerHTML=man(est*0.8)+"〜"+man(est*1.2)+"<small>万円</small>";
$("ru").innerHTML=u.map(function(s){{return"<li>"+s+"</li>"}}).join("");
$("hito").href="/moushikomi?lite=1&want="+encodeURIComponent("査定してほしい")+"&machi="+x.id+"&memo="+encodeURIComponent(nm+"・"+LB[ty][2]+"・"+Math.round(a)+"㎡・目安"+man(est*0.8)+"〜"+man(est*1.2)+"万円");
var first=r.style.display!=="block";r.style.display="block";if(first&&window.__ikU)setTimeout(function(){{r.scrollIntoView({{behavior:"smooth",block:"center"}})}},60);c("いくら｜出した｜"+ty+"｜"+nm)}}
$("ty").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;ty=b.dataset.v;[].forEach.call($("ty").children,function(x){{x.setAttribute("aria-pressed",x===b)}});calc()}});
ci.addEventListener("change",function(){{window.__ikU=1;calc()}});ar.addEventListener("input",calc);
document.addEventListener("click",function(e){{var a=e.target.closest("[data-k]");if(a)c(a.getAttribute("data-k"))}});
fill();try{{var id=new URLSearchParams(location.search).get("machi")||"";Object.keys(D).forEach(function(k){{if(D[k].id===id){{ci.value=k;calc()}}}})}}catch(e){{}}}})();</script>
<script src="/assets/night.js?v=24"></script><script src="/assets/menu.js?v=46"></script><script src="/assets/v2sub.js?v=17"></script>
</body></html>"""
out = AK + "site/ikura.html"
open(out, "w", encoding="utf-8").write(page)
print(out, n, "市区町村")
