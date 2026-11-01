"""TOWN NOTE の入口ページ（links/town-notes.html）を作る。
11/1 12:54 オーナー「TOWNNOTEを作れ。項目は2種類。1番最初の入口だ」「最初の入口はかなり手を入れろ」
→ 関西おでかけリスト と 関西不動産リスト の2つの入口。上に関西の絵地図、まんなかに「あなたの街」を両方まとめて探せる窓。
  数（開催中・これから・街・数字）はページを開いた時に両方のリストから読むので、手で直さなくても毎日合う。
使い方: python3 tools/townnotes_top/make.py [--live]
"""
import html, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
live = "--live" in sys.argv
E = html.escape
BASE = "https://townnote.pages.dev"
K = json.load(open(os.path.join(ROOT, "links/townnotes/kansai.json"), encoding="utf-8"))
PC = {"大阪": "#B97A62", "京都": "#8A7495", "兵庫": "#4F6681", "奈良": "#6F8C68", "滋賀": "#5F8F98", "和歌山": "#C4925A"}
FILL = {"大阪": "#F7D9CC", "京都": "#E6DBF1", "兵庫": "#D6E4F5", "奈良": "#D8ECD4", "滋賀": "#D0EBEF", "和歌山": "#F8E4C4"}
LP = {"大阪": [135.47, 34.62], "京都": [135.45, 35.30], "兵庫": [134.78, 35.12], "奈良": [135.88, 34.30], "滋賀": [136.18, 35.20], "和歌山": [135.50, 33.98]}
ID = {"大阪": "osaka", "京都": "kyoto", "兵庫": "hyogo", "奈良": "nara", "滋賀": "shiga", "和歌山": "wakayama"}
EN = {"大阪": "OSAKA", "京都": "KYOTO", "兵庫": "HYOGO", "奈良": "NARA", "滋賀": "SHIGA", "和歌山": "WAKAYAMA"}


def rings(g):
    return g["coordinates"] if g["type"] == "Polygon" else [r for p in g["coordinates"] for r in p]


xs = [x for f in K["pref"]["features"] for r in rings(f["geometry"]) for x, _ in r]
ys = [y for f in K["pref"]["features"] for r in rings(f["geometry"]) for _, y in r]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
k = math.cos(math.radians((y0 + y1) / 2))
S = 600 / ((x1 - x0) * k)
W, H = 600, (y1 - y0) * S


def P(lon, lat):
    return ((lon - x0) * k * S, (y1 - lat) * S)


paths = []
for f in K["pref"]["features"]:
    pf = f["properties"]["p"]
    d = "".join("M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in (P(*q) for q in r)) + "Z" for r in rings(f["geometry"]))
    paths.append(f'<path d="{d}" fill="{FILL[pf]}" data-p="{pf}"/>')
labels = []
for pf, (lo, la) in LP.items():
    x, y = P(lo, la)
    labels.append(f'<g transform="translate({x:.0f},{y:.0f})"><text class="jp" fill="{PC[pf]}">{pf}</text><text class="en" y="17">{EN[pf]}</text></g>')
SVG = (f'<svg class="kmap" viewBox="-10 -10 {W + 20:.0f} {H + 20:.0f}" role="img" aria-label="関西6府県の地図">'
       f'<g class="pf" stroke="#fff" stroke-width="2.4" stroke-linejoin="round">{"".join(paths)}</g>'
       f'<g class="lb">{"".join(labels)}</g></svg>')

desc = "関西の不動産屋が、街を調査して見つけたことを、ノートにまとめています。イベントや新しいお店・施設の「関西おでかけリスト」と、地価・人口・できる物を公式の数字で見る「関西不動産リスト」。"
ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "TOWN NOTE", "url": f"{BASE}/", "description": desc}

CHIPS = ["梅田", "吹田", "京都市", "宇治", "神戸", "西宮", "奈良市", "生駒", "大津", "草津", "和歌山市", "白浜"]

page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TOWN NOTE（タウンノート）｜関西おでかけリスト・関西不動産リスト</title>
<meta name="description" content="{E(desc)}">{'' if live else '<meta name="robots" content="noindex">'}{f'<link rel="canonical" href="{BASE}/">' if live else ''}
<meta property="og:type" content="website"><meta property="og:url" content="{BASE}/"><meta property="og:title" content="TOWN NOTE"><meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{BASE}/assets/ogp.png"><meta name="twitter:card" content="summary">
<link rel="icon" href="/assets/ogp.png"><link rel="apple-touch-icon" href="/assets/ogp.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New",sans-serif;color:#2B2622;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:460px;margin:0 auto;padding:0 16px 30px;overflow:hidden}}
.head{{position:relative;text-align:center;margin:0 -16px;padding:34px 16px 6px;background:radial-gradient(circle at 10% 14%,rgba(242,214,194,.55) 0 84px,transparent 85px),radial-gradient(circle at 92% 8%,rgba(205,224,236,.6) 0 60px,transparent 61px),radial-gradient(circle at 4% 62%,rgba(236,214,222,.45) 0 40px,transparent 41px)}}
.head img{{width:74px;height:74px}}
.brand{{font-family:Jost;font-weight:300;font-size:10.5px;letter-spacing:.5em;color:#8C7B6E;margin:12px 0 0;padding-left:.5em}}
h1{{font-family:Jost;font-weight:300;font-size:40px;letter-spacing:.16em;line-height:1.1;margin:16px 0 0;padding-left:.16em;color:#231E1B}}
.kana{{font-size:11px;font-weight:500;letter-spacing:.5em;padding-left:.5em;color:#8C7B6E;margin:8px 0 0}}
.cp{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:19px;letter-spacing:.14em;margin:16px 0 0;color:#2B2622}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:12px 0 0;text-wrap:balance}}
.kmap{{display:block;width:100%;height:auto;margin:18px 0 0}}
.kmap .lb text{{text-anchor:middle;paint-order:stroke;stroke:#fff;stroke-width:5px;stroke-linejoin:round}}
.kmap .jp{{font-family:"Shippori Mincho",serif;font-weight:700;font-size:22px;letter-spacing:.12em}}
.kmap .en{{font-family:Jost;font-size:9.5px;letter-spacing:.3em;fill:#9C8775}}
.kmap .pf path{{cursor:pointer;transition:opacity .2s}}.kmap.sel .pf path{{opacity:.35}}.kmap.sel .pf path.on{{opacity:1}}
.pp{{margin:8px 0 0;background:#fff;border:1px solid #ECECEC;border-top:3px solid var(--pc,#D6CCC1);padding:14px 16px;text-align:left}}.pp[hidden]{{display:none}}
.pp h3{{margin:0;font-family:"Shippori Mincho",serif;font-weight:700;font-size:18px;letter-spacing:.1em;color:var(--pc)}}.pp h3 small{{font-family:Jost;font-weight:400;font-size:9.5px;letter-spacing:.3em;color:#9C8775;margin-left:8px}}
.pp .g{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0 0}}.pp .g a{{display:block;text-decoration:none;color:#2B2622;background:#F1F2F4;padding:10px 12px}}
.pp .g span{{display:block;font-size:11px;color:#7A6E66}}.pp .g b{{display:block;font-family:Jost;font-weight:500;font-size:20px;color:var(--pc)}}.pp .g em{{display:block;font-style:normal;font-size:11.5px;color:#5C5048;line-height:1.5;margin-top:2px}}
.mapcap{{text-align:center;font-family:Jost;font-size:10px;letter-spacing:.34em;color:#9C8775;margin:4px 0 0}}
/* あなたの街 */
.find{{margin:28px 0 0;padding:20px 16px 16px;background:#F1F2F4}}
.find h2{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.12em;margin:0;text-align:center}}
.find h2 small{{display:block;font-family:Jost;font-weight:400;font-size:10px;letter-spacing:.34em;color:#9C8775;margin-bottom:6px}}
.find p{{font-size:12px;color:#6B6058;text-align:center;margin:8px 0 12px;line-height:1.8}}
.fi{{display:block;width:100%;box-sizing:border-box;font-size:16px;padding:13px 16px;border:1px solid #D6CCC1;border-radius:12px;background:#fff;color:#2B2622;font-family:inherit;outline:none}}.fi:focus{{border-color:#8C7B6E}}
.chips{{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 0;justify-content:center}}
.chips button{{border:1px solid #D6CCC1;background:#fff;border-radius:999px;padding:6px 12px;font-family:inherit;font-size:12.5px;font-weight:700;color:#5C5048;cursor:pointer}}
.res{{margin-top:12px}}.res:empty{{display:none}}
.res .sec{{font-family:Jost;font-size:10px;letter-spacing:.3em;color:#9C8775;margin:14px 2px 8px}}
.res a{{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;background:#fff;text-decoration:none;color:#2B2622;padding:12px 14px;margin:0 0 8px;border-left:3px solid var(--pc)}}
.res a i{{font-style:normal;font-size:11px;font-weight:700;color:var(--pc);border:1px solid var(--pc);border-radius:999px;padding:1px 8px}}
.res a b{{font-size:14px;line-height:1.5}}.res a b small{{display:block;font-size:11px;font-weight:500;color:#8C7B6E}}
.res a em{{font-style:normal;font-family:Jost;font-weight:500;font-size:16px}}
.res .none{{font-size:12.5px;color:#7A6E66;text-align:center;padding:6px 0}}
/* 2つのリスト */
.lists{{margin:34px 0 0}}
.lists>h2{{text-align:center;font-family:Jost;font-weight:400;font-size:10.5px;letter-spacing:.42em;color:#8C7B6E;margin:0 0 16px}}
.ls{{position:relative;display:block;text-decoration:none;color:#2B2622;background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05),0 10px 26px rgba(43,38,34,.07);padding:22px 20px 18px;margin:0 0 18px;overflow:hidden}}
.ls:before{{content:"";position:absolute;right:-46px;top:-46px;width:150px;height:150px;border-radius:50%;background:var(--bg)}}
.ls .no{{position:relative;font-family:Jost;font-weight:300;font-size:30px;color:var(--ac);line-height:1}}
.ls .no small{{font-size:10px;letter-spacing:.3em;margin-right:8px;vertical-align:middle;color:#9C8775}}
.ls .en{{position:relative;font-family:Jost;font-size:10px;letter-spacing:.3em;color:#9C8775;margin-top:10px}}
.ls h3{{position:relative;font-family:"Shippori Mincho",serif;font-weight:600;font-size:23px;letter-spacing:.12em;margin:6px 0 0}}
.ls p{{position:relative;font-size:12.5px;line-height:1.9;color:#6B6058;margin:6px 0 0}}
.ls .st{{position:relative;display:flex;gap:0 18px;margin:14px 0 0;padding:12px 0 0;border-top:1px solid #ECECEC}}
.ls .st span{{font-size:11px;color:#7A6E66}}.ls .st b{{display:block;font-family:Jost;font-weight:500;font-size:22px;color:var(--ac);line-height:1.3}}
.ls .pv{{position:relative;margin:12px 0 0;font-size:12.5px;line-height:1.7;color:#2B2622}}.ls .pv:empty{{display:none}}
.ls .pv div{{padding:7px 0;border-top:1px dashed #E4E4E4;display:flex;gap:8px}}.ls .pv div i{{font-style:normal;font-size:10.5px;font-weight:700;color:var(--c);flex:none;margin-top:1px}}
.ls .go{{position:relative;display:flex;justify-content:space-between;align-items:center;margin:14px 0 0;padding:12px 16px;background:var(--ac);color:#fff;font-weight:700;font-size:14px;letter-spacing:.08em}}
.ls .go span{{font-family:Jost}}
/* 約束 */
.prom{{margin:30px 0 0;text-align:center}}
.prom h2{{font-family:Jost;font-weight:400;font-size:10.5px;letter-spacing:.42em;color:#8C7B6E;margin:0 0 14px}}
.prom ol{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}}
.prom li{{background:#F1F2F4;padding:14px 4px 12px;font-size:11.5px;line-height:1.6;color:#5C5048}}.prom li b{{display:block;font-family:"Shippori Mincho",serif;font-size:15px;color:#2B2622;margin-bottom:4px;letter-spacing:.06em}}
.cos{{margin:30px 0 0;border:1px solid #D6CCC1}}
.cos a{{display:block;position:relative;text-decoration:none;color:#2B2622;padding:16px 44px 15px 18px;border-top:1px solid #ECECEC}}.cos a:first-child{{border-top:0}}
.cos a small{{display:block;font-family:Jost;font-size:9.5px;letter-spacing:.3em;color:#9C8775}}.cos a b{{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.08em;margin-top:4px}}.cos a span{{display:block;font-size:11.5px;color:#857A70;margin-top:3px}}
.cos a:after{{content:"→";position:absolute;right:18px;top:50%;transform:translateY(-50%);font-family:Jost;color:#9C8775}}
.sns{{margin:30px 0 0;text-align:center}}.sns h2{{font-family:Jost;font-weight:400;font-size:10.5px;letter-spacing:.42em;color:#8C7B6E;margin:0 0 12px}}
.sns a{{display:inline-block;margin:0 10px;color:#2B2622;text-decoration:none;font-family:Jost;font-size:14px;letter-spacing:.06em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.ft{{text-align:center;font-size:10.5px;letter-spacing:.06em;color:#8C7B6E;margin-top:30px}}
</style><script src="/assets/night.js?v=5"></script><script src="/assets/menu.js?v=9" defer></script><script src="/assets/v2sub.js?v=7" defer></script></head><body><div class="wrap">
<header class="head"><img src="/assets/logo-s.png?v=2" width="74" height="74" alt="TOWN NOTE のロゴ">
<h1>TOWN NOTE</h1><div class="kana">タウンノート</div>
<p class="sub">関西の不動産屋が、街を調査して見つけたことを、<br>公式の情報つきで、このノートに書きとめています。</p>
<div class="nofilt">{SVG}</div><div class="mapcap">府県を押すと、その府県の数が出ます</div><div class="pp" id="pp" hidden></div></header>

<section class="find"><h2><small>YOUR TOWN</small>あなたの街を探す</h2>
<p>街の名前を入れると、その街の<b>おでかけ</b>と<b>地価</b>が<br>まとめて出ます。</p>
<input class="fi" id="q" type="search" placeholder="例：吹田、西宮、草津" enterkeyhint="search" aria-label="街の名前">
<div class="chips">{"".join(f'<button type="button">{c}</button>' for c in CHIPS)}</div>
<div class="res" id="res"></div></section>

<section class="lists"><h2>IN THIS NOTE　─　このノートの中身</h2>
<a class="ls" href="/odekake" data-k="入口｜関西おでかけリスト" style="--ac:#B97A62;--bg:#FBEEE8;--c:#B97A62"><div class="no"><small>PAGE</small>01</div><div class="en">KANSAI ODEKAKE</div><h3>関西おでかけリスト</h3>
<p>イベント・新しいお店や施設を、公式ページつきで。<br>今週末に行ける所も、地図でも探せます。</p>
<div class="st"><div><span>開催中</span><b id="o1">―</b></div><div><span>これから</span><b id="o2">―</b></div><div><span>入場無料</span><b id="o3">―</b></div></div>
<div class="pv" id="opv"></div><div class="go">おでかけリストを開く<span>→</span></div></a>
<a class="ls" href="/fudosan-list" data-k="入口｜関西不動産リスト" style="--ac:#4F6681;--bg:#EEF3FA;--c:#4F6681"><div class="no"><small>PAGE</small>02</div><div class="en">KANSAI REAL ESTATE</div><h3>関西不動産リスト</h3>
<p>地価・人口・できる物・制度を、公式の数字で。<br>あなたの街が、1年でどう動いたかがわかります。</p>
<div class="st"><div><span>関西の街</span><b id="f1">―</b></div><div><span>上がった街</span><b id="f2">―</b></div><div><span>調べた数字</span><b id="f3">―</b></div></div>
<div class="pv" id="fpv"></div><div class="go">不動産リストを開く<span>→</span></div></a></section>

<section class="prom"><h2>NOTE RULES　─　書きかたの約束</h2><ol><li><b>公式だけ</b>公式ページ・<br>公式の数字だけ</li><li><b>6府県</b>どの府県も<br>同じように</li><li><b>毎日ふえる</b>見つけたら、<br>その日に足します</li></ol></section>

<nav class="cos"><a href="/fudosan.html" data-k="入口｜不動産のご相談"><small>REAL ESTATE</small><b>不動産のご相談</b><span>売却・査定、お家を売る前に大事なこと</span></a><a href="https://ig.me/m/fudousan_ai_si" data-k="入口｜おでかけ掲載"><small>LISTING</small><b>おでかけ掲載</b><span>新しいお店や、毎年のイベントのご紹介</span></a></nav>
<div class="sns"><h2>FOLLOW</h2><a href="https://www.instagram.com/fudousan_ai_si/">Instagram</a><a href="https://www.threads.com/@fudousan_ai_si">Threads</a><a href="https://x.com/fudosan_ai_si">X</a></div>
<div class="ft">ぴょんと街しらべ│TOWN NOTE</div></div>
<script>(function(){{
var PC={json.dumps(PC, ensure_ascii=False)};
try{{var oq=new URLSearchParams(location.search).get("owner");if(oq==="1")localStorage.setItem("usagi_owner","1");if(oq==="0")localStorage.removeItem("usagi_owner");if(oq!==null)history.replaceState(null,"",location.pathname+location.hash);}}catch(e){{}}
var O=(function(){{try{{return localStorage.getItem("usagi_owner")==="1";}}catch(e){{return false;}}}})();function c(k){{if(O)return;try{{var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}});}}catch(e){{}}}}
function esc(s){{return String(s).replace(/[&<>"]/g,function(x){{return{{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[x]}})}}
function pct(v){{return (v>0?"+":v<0?"−":"±")+Math.abs(v).toFixed(1)+"%"}}
var today=new Date(Date.now()+9*36e5).toISOString().slice(0,10);
// おでかけ：今のリストを読んで、開催中・これからを数える（終わった物は数えない）
var OD=[],TW=[],FA=0;
var pO=fetch("/odekake").then(function(r){{return r.text()}}).then(function(t){{var d=new DOMParser().parseFromString(t,"text/html");
 d.querySelectorAll(".paper a.card").forEach(function(a){{var e=a.getAttribute("data-e")||"",s=a.getAttribute("data-s")||"",tt=a.querySelector(".t"),m=a.querySelector(".m");if(e&&e<today)return;if(!tt)return;
  OD.push({{t:tt.textContent.trim(),m:m?m.textContent.trim():"",p:a.getAttribute("data-pref")||"",h:a.getAttribute("href"),f:/無料/.test(a.getAttribute("data-tag")||""),now:!!(s&&s<=today&&(!e||e>=today)),up:!!(s&&s>today)}});}});
 var n1=OD.filter(function(x){{return x.now}}).length,n2=OD.filter(function(x){{return x.up}}).length;document.getElementById("o1").innerHTML=n1+'<small style="font-size:12px">件</small>';document.getElementById("o2").innerHTML=n2+'<small style="font-size:12px">件</small>';
 var n3=OD.filter(function(x){{return x.f}}).length;document.getElementById("o3").innerHTML=n3+'<small style="font-size:12px">件</small>';
 var pv=OD.filter(function(x){{return x.now}}).slice(0,3);document.getElementById("opv").innerHTML=pv.map(function(x){{return '<div><i style="color:'+(PC[x.p]||"#8C7B6E")+'">'+esc(x.p)+'</i>'+esc(x.t)+'</div>'}}).join("");}}).catch(function(){{}});
var pF=fetch("/assets/towns.json").then(function(r){{return r.json()}}).then(function(d){{TW=d;document.getElementById("f1").textContent=d.length;document.getElementById("f2").textContent=d.filter(function(t){{return t.r8>0}}).length;
 var top=d.slice().sort(function(a,b){{return b.r8-a.r8}});var pv=[top[0]].concat(["京都","兵庫","奈良","滋賀","和歌山"].map(function(p){{return top.filter(function(t){{return t.p===p}})[0]}})).slice(0,3);
 document.getElementById("fpv").innerHTML=pv.map(function(t){{return '<div><i style="color:'+PC[t.p]+'">'+t.p+'</i>'+esc(t.n)+'　住宅地 '+pct(t.r8)+'（'+t.p+'で1位）</div>'}}).join("");}}).catch(function(){{}});
fetch("/fudosan-list").then(function(r){{return r.text()}}).then(function(t){{var m=t.match(/class="card"/g);document.getElementById("f3").innerHTML=(m?m.length:0)+'<small style="font-size:12px">件</small>';}}).catch(function(){{}});
// 地図：府県を押すと、その府県のおでかけと街の数
var ID={json.dumps(ID, ensure_ascii=False)},EN={json.dumps(EN, ensure_ascii=False)},svg=document.querySelector(".kmap"),pp=document.getElementById("pp");
svg.querySelectorAll(".pf path").forEach(function(el){{el.addEventListener("click",function(){{var p=el.getAttribute("data-p");Promise.all([pO,pF]).then(function(){{
 svg.classList.add("sel");svg.querySelectorAll(".pf path").forEach(function(x){{x.classList.toggle("on",x.getAttribute("data-p")===p)}});
 var od=OD.filter(function(x){{return x.p===p}}),nw=od.filter(function(x){{return x.now}}),tw=TW.filter(function(x){{return x.p===p}}),up=tw.filter(function(x){{return x.r8>0}}),tp=tw.slice().sort(function(a,b){{return b.r8-a.r8}})[0];
 pp.style.setProperty("--pc",PC[p]);pp.hidden=false;
 pp.innerHTML='<h3>'+p+'<small>'+EN[p]+'</small></h3><div class="g"><a href="/odekake" data-k="入口の地図｜おでかけ｜'+p+'"><span>おでかけ（開催中）</span><b>'+nw.length+'<small style="font-size:12px">件</small></b><em>'+(nw[0]?esc(nw[0].t):"これから足します")+'</em></a><a href="/chika-kansai#'+ID[p]+'" data-k="入口の地図｜地価｜'+p+'"><span>上がった街</span><b>'+up.length+'<small style="font-size:12px">／'+tw.length+'</small></b><em>'+(tp?"1位 "+esc(tp.n)+" "+pct(tp.r8):"")+'</em></a></div>';
 c("入口の地図："+p);}});}});}});
// あなたの街：おでかけと地価をまとめて
var q=document.getElementById("q"),res=document.getElementById("res"),tq;
function find(v){{v=v.replace(/\\s/g,"");if(!v){{res.innerHTML="";return;}}var vv=v.replace(/(市|区|町|村|駅)$/,"");
 var tw=TW.filter(function(t){{return t.n.indexOf(vv)>=0||t.s.indexOf(vv)>=0}}).slice(0,6);
 var od=OD.filter(function(x){{return (x.t+x.m).replace(/\\s/g,"").indexOf(vv)>=0}}).slice(0,6);
 var h="";if(tw.length)h+='<div class="sec">LAND PRICE　街の地価</div>'+tw.map(function(t){{return '<a href="/machi/'+t.id+'" style="--pc:'+PC[t.p]+'" data-k="入口の検索｜地価｜'+esc(t.n)+'"><i>'+t.p+'</i><b>'+esc(t.n)+'<small>住宅地 1年の動き・'+t.p+'で'+t.rk+'位／'+t.of+'</small></b><em style="color:'+(t.r8>0?PC[t.p]:"#7A6E66")+'">'+pct(t.r8)+'</em></a>'}}).join("");
 if(od.length)h+='<div class="sec">ODEKAKE　おでかけ</div>'+od.map(function(x){{return '<a href="'+esc(x.h)+'" style="--pc:'+(PC[x.p]||"#8C7B6E")+'" data-k="入口の検索｜おでかけ｜'+esc(x.t.slice(0,20))+'"><i>'+esc(x.p)+'</i><b>'+esc(x.t)+'<small>'+esc(x.m.split("｜")[0])+(x.now?"・開催中":x.up?"・これから":"")+'</small></b><em style="color:#9C8775">→</em></a>'}}).join("");
 res.innerHTML=h||'<div class="none">「'+esc(v)+'」はまだありません。調べて、リストに足していきます。</div>';}}
q.oninput=function(){{Promise.all([pO,pF]).then(function(){{find(q.value)}});clearTimeout(tq);tq=setTimeout(function(){{if(q.value.trim())c("入口で探す："+q.value.trim())}},1500);}};
document.querySelectorAll(".chips button").forEach(function(b){{b.onclick=function(){{q.value=b.textContent;Promise.all([pO,pF]).then(function(){{find(b.textContent)}});c("入口で探す："+b.textContent);}}}});
c("表示：TOWN NOTE 入口"+(document.referrer&&!/usagi-odekake|townnote.pages/.test(document.referrer)?"（外から）":""));
document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a");if(!a)return;c("クリック：TOWN NOTE 入口｜"+(a.getAttribute("data-k")||a.textContent.trim().slice(0,30)));}},true);
}})();</script></body></html>'''
open(os.path.join(ROOT, "links/town-notes.html"), "w", encoding="utf-8").write(page)
print("ok", len(page))
