#!/usr/bin/env python3
"""「いくらで売れる？」の道具（関西 TOWN・11/13 見本）。
近畿レインズ 2025年度 年刊市況レポートの「実際に売れた」数字（tools/fudosan_list/reins/*.csv）だけで、
街・種類・広さから目安の幅を出し、そのまま相談（/moushikomi?lite=1）へつなぐ。
関西は反響（オーナーへの相談）の場所なので、売却のアフィリエイトは置かない。
使い方：python3 tools/ikura/build.py           … links/ikura-mihon.html（noindex の見本）
        python3 tools/ikura/build.py --live    … links/ikura.html（公開。オーナーの OK の後だけ）
"""
import csv, json, os, sys, html
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RE = os.path.join(R, "tools", "fudosan_list", "reins")
LIVE = "--live" in sys.argv
PF = {"大阪府": "大阪", "京都府": "京都", "兵庫県": "兵庫", "奈良県": "奈良", "滋賀県": "滋賀", "和歌山県": "和歌山"}
towns = json.load(open(os.path.join(R, "links", "assets", "towns.json"), encoding="utf-8"))
towns = towns.get("towns", towns) if isinstance(towns, dict) else towns
tid = {(t["p"], t["n"]): t["id"] for t in towns}

def rows(fn):
    for r in csv.DictReader(open(os.path.join(RE, fn), encoding="utf-8")):
        if r["府県"] not in PF or not r["市区町村"]:
            continue
        name = r["市区町村"]
        big = r["地域見出し"]
        if big and big.endswith("市") and not name.startswith(big):  # 大阪市 都島区 → 大阪市都島区
            name = big + name
        yield PF[r["府県"]], name, r

D = {}
for p, n, r in rows("mansion_2025.csv"):
    if int(r["件数"]) >= 10:
        D.setdefault(p + "|" + n, {})["m"] = [int(r["件数"]), float(r["㎡単価万円"]), int(r["価格万円"]), float(r["専有面積"]), float(r["築年"])]
for p, n, r in rows("kodate_2025.csv"):
    if int(r["件数"]) >= 10:
        D.setdefault(p + "|" + n, {})["k"] = [int(r["件数"]), int(r["価格万円"]), float(r["土地面積"]), float(r["建物面積"]), float(r["築年"])]
for p, n, r in rows("tochi_2025.csv"):
    if int(r["件数"]) >= 10:
        D.setdefault(p + "|" + n, {})["t"] = [int(r["件数"]), float(r["㎡単価万円"]), int(r["価格万円"]), float(r["土地面積"])]
for k in D:
    p, n = k.split("|")
    D[k]["id"] = tid.get((p, n), "")
order = ["大阪", "兵庫", "京都", "奈良", "滋賀", "和歌山"]
keys = sorted(D, key=lambda k: (order.index(k.split("|")[0]), k))
data = json.dumps({k: D[k] for k in keys}, ensure_ascii=False, separators=(",", ":"))

robots = "" if LIVE else '<meta name="robots" content="noindex">'
page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}
<title>お家はいくらで売れる？ 関西の街の実際に売れた値段で目安｜TOWN NOTE</title>
<meta name="description" content="関西{len(keys)}の市区で、2025年度に実際に売れた中古マンション・中古一戸建て・土地の値段（近畿レインズ）から、お家の目安を30秒で出せます。無料・名前も要りません。">
<link rel="canonical" href="https://townnote.pages.dev/ikura">
<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 120px}}
.head{{text-align:center;margin:0 -16px;padding:30px 16px 26px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px),#FFFFFF}}
.head img{{width:60px}}
.en{{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:25px;letter-spacing:.14em;color:#231E1B;margin:14px 0 10px;font-feature-settings:"palt"}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}}
.card{{border:1px solid #D9D9D9;background:#fff;padding:18px 18px 20px;margin-top:22px}}
.q{{font-family:Jost;font-size:9.5px;letter-spacing:.32em;color:#9C8775;margin:0 0 8px}}
.q b{{font-family:"Zen Kaku Gothic New";font-size:14px;letter-spacing:.04em;color:#2B2622;margin-left:6px}}
.step+.step{{margin-top:18px;padding-top:16px;border-top:1px solid #EEE}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
.chips button{{font:inherit;font-size:14px;padding:10px 14px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:#2B2622;cursor:pointer}}
.chips button[aria-pressed=true]{{background:#3A332E;color:#fff;border-color:#3A332E}}
select,input{{font:inherit;font-size:16px;width:100%;box-sizing:border-box;padding:12px 12px;border:1px solid #D9D2CB;border-radius:10px;background:#fff;color:#2B2622}}
.row{{display:flex;gap:8px;align-items:center}}.row span{{white-space:nowrap;font-size:14px}}
.hint{{font-size:12px;color:#8C7B6E;margin:6px 0 0;line-height:1.7}}
.res{{margin-top:22px;border:1px solid #3A332E;padding:20px 18px;display:none}}
.res .lb{{font-size:12px;color:#6B6058}}
.res .big{{font-family:"Shippori Mincho",serif;font-weight:700;font-size:32px;letter-spacing:.02em;margin:6px 0 4px;color:#231E1B}}
.res .big small{{font-size:15px;font-weight:600}}
.res ul{{margin:12px 0 0;padding:0;list-style:none;font-size:13px;line-height:1.9;color:#3A332E}}
.res li:before{{content:"・"}}
.go{{display:block;background:#3A332E;color:#fff;border-radius:12px;padding:16px;margin:18px 0 6px;text-align:center;text-decoration:none;font-weight:700;font-size:15.5px}}
.go small{{display:block;font-weight:500;font-size:11.5px;opacity:.85;margin-top:4px}}
.note{{font-size:11.5px;line-height:1.9;color:#8C7B6E;margin-top:22px}}
.note a{{color:#8C7B6E}}
</style></head><body><div class="wrap">
<div class="head"><img src="assets/logo-s.png?v=2" alt="ロゴ" width="60" height="60"><div class="en">HOW MUCH</div><h1>お家はいくらで売れる？</h1>
<p class="sub">関西{len(keys)}の市区で、去年<b>実際に売れた値段</b>から目安を出します。<br>無料・名前も要りません。30秒で終わります。</p></div>
<div class="card">
<div class="step"><p class="q">01<b>お家の種類</b></p><div class="chips" id="ty"><button type="button" data-v="m" aria-pressed="true">マンション</button><button type="button" data-v="k" aria-pressed="false">一戸建て</button><button type="button" data-v="t" aria-pressed="false">土地</button></div></div>
<div class="step"><p class="q">02<b>お家のある市区</b></p><select id="ci" aria-label="市区"></select><p class="hint" id="cn"></p></div>
<div class="step"><p class="q">03<b id="al">専有面積</b></p><div class="row"><input id="ar" type="number" inputmode="decimal" min="10" max="2000" placeholder="例 70"><span>㎡</span></div><p class="hint" id="ah">分からなければ空のままで大丈夫です（この街の平均で出します）。</p></div>
</div>
<div class="res" id="res" aria-live="polite"><div class="lb" id="rl"></div><div class="big" id="rb"></div><div class="lb">目安の幅（実際の値段は、お家の状態・駅からの近さ・築年で上下します）</div><ul id="ru"></ul>
<a class="go" id="go" href="/moushikomi?lite=1" data-k="いくら｜正確な値段を聞く">このお家の正確な値段を聞く（無料）<small>売るか決めていなくても大丈夫です。メールだけなら、お電話はしません</small></a></div>
<p class="note">数字は、近畿レインズ「2025年度 年刊市況レポート」の市区町村別の成約（実際に売れた）データです（10件以上売れた市区だけ）。目安の出し方：マンション＝その市区の㎡単価×広さ、一戸建て＝その市区で売れた一戸建ての土地1㎡あたりの値段×土地の広さ、土地＝その市区の㎡単価×広さ。幅は±15％です。査定ではありません。</p>
</div>
<script>var D={data};
(function(){{var $=function(i){{return document.getElementById(i)}},ty="m",ci=$("ci"),ar=$("ar");
function c(k){{try{{if(localStorage.getItem("usagi_owner")==="1")return;var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}});}}catch(e){{}}}}
c("表示：いくら"+(document.referrer&&!/townnote\\.pages/.test(document.referrer)?"（外から）":""));
var LB={{m:["専有面積","例 70","マンション"],k:["土地の広さ","例 100","一戸建て"],t:["土地の広さ","例 120","土地"]}};
function fill(){{var cur=ci.value;ci.innerHTML='<option value="">市区を選んでください</option>';var pp="";Object.keys(D).forEach(function(k){{if(!D[k][ty])return;var p=k.split("|")[0];if(p!==pp){{var g=document.createElement("optgroup");g.label=p;ci.appendChild(g);pp=p;}}var o=document.createElement("option");o.value=k;o.textContent=k.split("|")[1];ci.lastChild.appendChild(o);}});if(cur&&D[cur]&&D[cur][ty])ci.value=cur;}}
function man(n){{return n>=10000?(Math.floor(n/1000)/10)+"億":Math.round(n).toLocaleString()}}
function calc(){{var k=ci.value,r=$("res");$("al").textContent=LB[ty][0];ar.placeholder=LB[ty][1];if(!k){{r.style.display="none";$("cn").textContent="";return}}
var x=D[k][ty],a=parseFloat(ar.value),est,u=[],nm=k.split("|")[1];
if(ty==="m"){{if(!(a>0))a=x[3];est=x[1]*a;u=["この市区で売れたマンション "+x[0]+"件","平均 "+man(x[2])+"万円（平均 "+x[3]+"㎡・築 "+Math.round(x[4])+"年）","1㎡あたり "+x[1]+"万円"]}}
else if(ty==="k"){{if(!(a>0))a=x[2];est=x[1]/x[2]*a;u=["この市区で売れた一戸建て "+x[0]+"件","平均 "+man(x[1])+"万円（土地 "+x[2]+"㎡・建物 "+x[3]+"㎡・築 "+Math.round(x[4])+"年）"]}}
else{{if(!(a>0))a=x[3];est=x[1]*a;u=["この市区で売れた土地 "+x[0]+"件","平均 "+man(x[2])+"万円（平均 "+x[3]+"㎡）","1㎡あたり "+x[1]+"万円"]}}
$("cn").textContent="2025年度に"+LB[ty][2]+"が "+x[0]+"件 売れた市区です";
$("rl").textContent=nm+"の"+LB[ty][2]+"（"+Math.round(a)+"㎡）";
$("rb").innerHTML=man(est*0.85)+"〜"+man(est*1.15)+"<small>万円</small>";
$("ru").innerHTML=u.map(function(s){{return"<li>"+s+"</li>"}}).join("");
var memo=nm+"・"+LB[ty][2]+"・"+Math.round(a)+"㎡・目安"+man(est*0.85)+"〜"+man(est*1.15)+"万円";
$("go").href="/moushikomi?lite=1&want="+encodeURIComponent("査定してほしい")+(D[k].id?"&machi="+D[k].id:"")+"&memo="+encodeURIComponent(memo);
var first=r.style.display!=="block";r.style.display="block";if(first&&window.__ikU)setTimeout(function(){{r.scrollIntoView({{behavior:"smooth",block:"center"}})}},60);c("いくら｜出した｜"+ty+"｜"+nm)}}
$("ty").addEventListener("click",function(e){{var b=e.target.closest("button");if(!b)return;ty=b.dataset.v;[].forEach.call($("ty").children,function(x){{x.setAttribute("aria-pressed",x===b)}});fill();calc()}});
ci.addEventListener("change",function(){{window.__ikU=1;calc()}});ar.addEventListener("input",calc);
document.addEventListener("click",function(e){{var a=e.target.closest("[data-k]");if(a)c("クリック："+a.getAttribute("data-k"))}});
try{{var id=new URLSearchParams(location.search).get("machi")||sessionStorage.getItem("tn_machi")||"";if(id)Object.keys(D).forEach(function(k){{if(D[k].id===id)ci.dataset.want=k}})}}catch(e){{}}
fill();if(ci.dataset.want&&D[ci.dataset.want][ty]){{ci.value=ci.dataset.want;calc()}}}})();</script>
<script src="assets/night.js?v=29"></script><script src="assets/menu.js?v=49"></script><script src="assets/v2sub.js?v=12"></script>
</body></html>"""
out = os.path.join(R, "links", "ikura.html" if LIVE else "ikura-mihon.html")
open(out, "w", encoding="utf-8").write(page)
print(out, len(keys), "市区", sum(1 for k in keys if "m" in D[k]), sum(1 for k in keys if "k" in D[k]), sum(1 for k in keys if "t" in D[k]), "id", sum(1 for k in keys if D[k]["id"]))
