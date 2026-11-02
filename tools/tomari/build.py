"""泊まりで行くおでかけ（10/31 オーナー「三本線…旅行先とかのあれも色々作れる」）。
遠くのおでかけ（近くの宿がある物）と、楽天トラベルの評価の高い宿3軒を1ページに。
python3 tools/tomari/build.py → links/tomari.html
元：links/index.html と links/illumination.html のカード ＋ links/kansai-yado.json（毎朝 link-stats.yml が燈から取る）。"""
import datetime, html, json, os, re, sys, urllib.parse
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)).date()
PREFS = ["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"]
PC = {"大阪": "#B97A62", "京都": "#8A7495", "兵庫": "#4F6681", "奈良": "#6F8C68", "滋賀": "#5F8F98", "和歌山": "#C4925A"}
WD = "月火水木金土日"
E = html.escape
yado = json.load(open(os.path.join(R, "links/kansai-yado.json")))
Y = {re.sub(r"\s+", "", k): v for k, v in yado.items() if v}
# 宿の名前のうしろの「<淡路島>」「 ^」は楽天の付け足し（燈の kansai_yado.py でも消す）
for v in Y.values():
    for h in v:
        h["n"] = re.sub(r"\s*(<[^<>]*>|\^)\s*$", "", h.get("n", "")).strip()

def txt(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

cards = {}
for page in ("links/index.html", "links/illumination.html"):
    s = open(os.path.join(R, page), encoding="utf-8").read()
    for m in re.finditer(r'<a class="card"([^>]*)>(.*?)</a>', s, re.S):
        a, body = m.group(1), m.group(2)
        g = lambda k: (re.search(k + r'="([^"]*)"', a) or [None, ""])[1]
        t = txt((re.search(r'<div class="t">(.*?)</div>', body, re.S) or [None, ""])[1])
        k = re.sub(r"\s+", "", t)
        if not t or k not in Y or k in cards:
            continue
        cards[k] = dict(t=t, p=g("data-pref"), s=g("data-s"), e=g("data-e"), map=html.unescape(g("data-map")), href=html.unescape(g("href")),
                        d=txt((re.search(r'<div class="d">(.*?)</div>', body, re.S) or [None, ""])[1]),
                        m=txt((re.search(r'<div class="m">(.*?)</div>', body, re.S) or [None, ""])[1]), free="無料" in body)

def md(x):
    d = datetime.date.fromisoformat(x); return f"{d.month}/{d.day}（{WD[d.weekday()]}）"

items = {p: [] for p in PREFS}
T = TODAY.isoformat()
for k, c in cards.items():
    if c["p"] not in items or (c["e"] and c["e"] < T):
        continue
    c["on"] = (not c["s"]) or c["s"] <= T
    c["k"] = k
    items[c["p"]].append(c)
for p in PREFS:
    items[p].sort(key=lambda c: (0, c["e"] or "9") if c["on"] else (1, c["s"]))
n_all = sum(len(v) for v in items.values())
n_inn = sum(len(Y[c["k"]][:3]) for v in items.values() for c in v)

def hotel(c, h, i):
    km = "すぐそば" if h.get("km", 9) < 0.1 else f"ここから{h['km']}km"
    rv = f"★{h['r']:.2f}".rstrip("0").rstrip(".") if h.get("r") else ""
    rc = f"（{h['rc']:,}件）" if h.get("rc") else ""
    pr = f"{int(h['min']):,}円〜" if h.get("min") else ""
    return (f'<li><a href="{E(h["u"])}" target="_blank" rel="noopener sponsored" data-k="宿｜{E(c["t"])}｜{E(h["n"])}">'
            f'<span class="hn">{E(h["n"])}</span><span class="hm"><b>{rv}</b>{rc}・{km}</span><span class="hp"><span class="hy">{pr}</span><span class="hv">空室を見る</span></span></a></li>')

secs = []
for p in PREFS:
    if not items[p]:
        continue
    rows = []
    for c in items[p]:
        tag = f'<span class="st {"on" if c["on"] else "soon"}">{"開催中" if c["on"] else "これから"}</span>' + ('<span class="fr">無料</span>' if c["free"] else "")
        gm = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(c["map"] or c["t"])
        hs = "".join(hotel(c, h, i) for i, h in enumerate(Y[c["k"]][:3]))
        rows.append(f'<article class="it" data-s="{E(c["s"])}" data-e="{E(c["e"])}"><a class="card" href="{E(c["href"])}" target="_blank" rel="noopener" data-k="公式｜{E(c["t"])}">'
                    f'<div class="tg">{tag}</div><div class="d">{E(c["d"])}</div><div class="t">{E(c["t"])}</div><div class="m">{E(c["m"])}</div><div class="go">公式 →</div></a>'
                    f'<div class="inn"><div class="ih"><span>近くの宿</span><a class="mp" href="{E(gm)}" target="_blank" rel="noopener" data-k="地図｜{E(c["t"])}">地図</a></div><ul>{hs}</ul></div></article>')
    secs.append(f'<section class="ps" id="p-{p}" data-p="{p}" style="--c:{PC[p]}"><h2>{p}<small>{len(items[p])}か所</small></h2>{"".join(rows)}</section>')

btns = '<button class="on" data-p="すべて">すべて</button>' + "".join(f'<button data-p="{p}" style="--pc:{PC[p]}">{p}</button>' for p in PREFS if items[p])
upd = f"{TODAY.year}年{TODAY.month}月{TODAY.day}日"
BASE = "https://townnote.pages.dev/"
# 地図（tools/townnotes/build.py が作る map-tomari.js）。中身が変わったら ?v= も変わる
import hashlib
_mj = os.path.join(R, "links/townnotes/map-tomari.js")
MAPJS = f'<script src="townnotes/map-tomari.js?v={hashlib.sha1(open(_mj, "rb").read()).hexdigest()[:8]}" defer></script>' if os.path.exists(_mj) else ""
out = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>泊まりで行く関西のおでかけ｜近くの宿つき</title><meta name="description" content="関西の少し遠いおでかけ{n_all}か所と、近くの評価の高い宿をまとめました。大阪・京都・兵庫・奈良・滋賀・和歌山。">
<link rel="canonical" href="{BASE}tomari"><meta property="og:title" content="泊まりで行く関西のおでかけ"><meta property="og:image" content="{BASE}assets/ogp.png">
<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.head{{text-align:center;margin:0 -16px;padding:30px 16px 24px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px),#FFFFFF}}
.head img{{width:60px;height:60px}}
.en{{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:24px;line-height:1.5;letter-spacing:.12em;color:#231E1B;margin:14px 0 10px;font-feature-settings:"palt"}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}}
.cnt{{display:flex;justify-content:center;gap:18px;margin-top:14px;font-size:12px;color:#6B6058}}.cnt b{{font-family:"Shippori Mincho",serif;font-size:20px;color:#2B2622;margin:0 2px}}
.flt{{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.96);display:flex;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;gap:0 16px;margin:20px -16px 0;padding:10px 64px 10px 16px;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4}}
.flt::-webkit-scrollbar{{display:none}}.flt button{{flex:none;border:none;background:none;padding:6px 0;font-family:"Zen Kaku Gothic New";font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer}}
.flt button.on{{color:var(--pc,#2B2622);border-bottom-color:var(--pc,#2B2622)}}
.wk{{display:flex;justify-content:center;margin:12px 0 0}}
.wk button{{font-family:"Zen Kaku Gothic New";font-size:12px;letter-spacing:.04em;color:#5B5450;background:#fff;border:1px solid #D4D4D4;border-radius:99px;padding:7px 14px;cursor:pointer}}
.wk button[aria-pressed=true]{{background:#2B2622;border-color:#2B2622;color:#fff}}
.pr{{font-size:11px;line-height:1.8;color:#8C7B6E;text-align:center;margin:10px 0 0}}
.ps{{scroll-margin-top:60px;margin-top:28px}}
h2{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:0 0 12px;padding-left:10px;border-left:3px solid var(--c);display:flex;align-items:baseline;gap:10px}}
h2 small{{font-family:"Zen Kaku Gothic New";font-size:11px;color:#8C7B6E;letter-spacing:.04em;font-weight:500}}
.it{{margin-bottom:16px;background:#fff;border:1px solid #E6E6E6}}
.card{{display:block;position:relative;text-decoration:none;color:inherit;padding:14px 64px 12px 16px}}
.tg{{display:flex;gap:6px;margin-bottom:6px}}
.st,.fr{{font-size:10.5px;letter-spacing:.06em;padding:1px 7px;border:1px solid;line-height:1.7}}
.st.on{{color:#fff;background:var(--c);border-color:var(--c)}}.st.soon{{color:var(--c)}}.fr{{color:#6F8A5F}}
.d{{font-size:13px;color:var(--c);font-weight:700;letter-spacing:.02em}}
.t{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;line-height:1.5;margin:4px 0}}
.m{{font-size:12px;color:#7A6E66;line-height:1.6}}
.go{{position:absolute;right:14px;top:16px;font-size:11px;letter-spacing:.06em;color:#6B6058;border-bottom:1px solid #BDBDBD;padding-bottom:1px}}
.inn{{border-top:1px dashed #DCDCDC;margin:0 16px;padding:10px 0 6px}}
.ih{{display:flex;justify-content:space-between;align-items:center;font-size:11px;letter-spacing:.14em;color:#8C7B6E;margin-bottom:2px}}
.ih .mp{{font-size:11px;letter-spacing:.08em;color:#6B6058;text-decoration:none;border-bottom:1px solid #BDBDBD;padding:4px 0 1px}}
.inn ul{{list-style:none;margin:0;padding:0}}
.inn li{{border-top:1px solid #F0F0F0}}.inn li:first-child{{border-top:0}}
.inn li a{{display:grid;grid-template-columns:1fr auto;column-gap:10px;padding:10px 0;text-decoration:none;color:#2B2622;min-height:44px;box-sizing:border-box}}
.hn{{font-size:13.5px;font-weight:700;line-height:1.45;grid-column:1}}
.hm{{grid-column:1;font-size:11px;color:#857A70;margin-top:2px}}.hm b{{color:#B5532F;font-weight:700}}
.hp{{grid-column:2;grid-row:1/3;align-self:center;display:flex;flex-direction:column;align-items:flex-end;gap:5px;white-space:nowrap}}
.hy{{font-family:Jost;font-size:13px;color:#2B2622}}
.hv{{font-size:11px;font-weight:700;color:#B5532F;border:1px solid #B5532F;border-radius:999px;padding:3px 10px;line-height:1.4}}
.hv:after{{content:" →"}}
.none{{display:none;text-align:center;font-size:13px;color:#8C7B6E;padding:40px 0}}
.note{{font-size:12px;line-height:1.9;color:#7A6E66;background:#F5F5F5;padding:14px 16px;margin-top:30px}}
.back{{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.ft{{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}}
</style><script src="assets/night.js?v=5"></script><script src="assets/menu.js?v=10" defer></script><script src="assets/v2sub.js?v=8" defer></script></head><body><div class="wrap">
<div class="head"><img src="assets/logo-s.png?v=2" width="60" height="60" alt="ロゴ"><div class="en">STAY &amp; GO</div>
<h1>泊まりで行くおでかけ</h1><p class="sub">関西の少し遠いおでかけと、<br>近くの評価の高い宿をまとめました。</p>
<div class="cnt"><span>おでかけ<b>{n_all}</b>か所</span><span>宿<b>{n_inn}</b>軒</span></div><div class="upd" style="font-size:11px;color:#8C7B6E;margin-top:6px">{upd} 更新</div></div>
<div class="flt" id="flt">{btns}</div>
<div class="wk"><button type="button" id="wk" aria-pressed="false">この週末に開いている所だけ</button></div>
<p class="pr">宿は楽天トラベルの評価3.5以上・口コミ10件以上から、近い順に3軒。<br>値段は1泊の最安の目安で、日や人数で変わります。宿のリンクは広告（PR）です。</p>
{"".join(secs)}
<div class="none" id="none">この週末に開いている所はありません。</div>
<div class="note">おでかけの日にちや時間は、出かける前に必ず公式ページで確かめてください。宿の空きや値段は楽天トラベルでご確認ください。</div>
<a class="back" href="/odekake">関西おでかけリストへ戻る</a>
<div class="ft">ぴょんと街しらべ│関西おでかけリスト</div></div>
<script>(function(){{
var B=document.querySelectorAll("#flt button"),S=document.querySelectorAll(".ps"),wk=document.getElementById("wk"),P="すべて",W=false;
function we(){{var n=new Date(Date.now()+9*36e5),d=n.getUTCDay(),sat=new Date(n);sat.setUTCDate(n.getUTCDate()+((6-d+7)%7));if(d===0)sat.setUTCDate(n.getUTCDate()-1);var sun=new Date(sat);sun.setUTCDate(sat.getUTCDate()+1);return [sat.toISOString().slice(0,10),sun.toISOString().slice(0,10)];}}
var WE=we();
var TD=new Date(Date.now()+9*36e5).toISOString().slice(0,10);/* 11/2 終わった日を過ぎたら、作り直し前でも出さない */
function draw(){{var any=0;S.forEach(function(s){{var on=P==="すべて"||s.dataset.p===P,c=0;s.querySelectorAll(".it").forEach(function(it){{var a=it.dataset.s||"0000",e=it.dataset.e||"9999",ok=e>=TD&&(!W||(a<=WE[1]&&e>=WE[0]));it.hidden=!ok;if(ok)c++;}});var h=s.querySelector("h2 small");if(h)h.textContent=c+"か所";s.hidden=!on||!c;if(on&&c)any++;}});document.getElementById("none").style.display=any?"none":"block";}}
B.forEach(function(b){{b.addEventListener("click",function(){{B.forEach(function(x){{x.classList.toggle("on",x===b)}});P=b.dataset.p;draw();ck("泊まり｜絞り込み："+P);var t=document.querySelector(".flt").getBoundingClientRect().top+scrollY;if(scrollY>t)scrollTo({{top:t,behavior:"smooth"}});}});}});
wk.addEventListener("click",function(){{W=!W;wk.setAttribute("aria-pressed",W);draw();ck("泊まり｜この週末");}});
function ck(k){{try{{if(localStorage.getItem("usagi_owner")==="1")return;}}catch(e){{}}try{{var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}});}}catch(e){{}}}}
document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a[data-k]");if(a)ck(a.dataset.k.indexOf("宿｜")===0?a.dataset.k:"泊まり｜"+a.dataset.k);}},true);
draw();ck("表示：泊まりで行くおでかけ");
}})();</script>{MAPJS}</body></html>
'''
open(os.path.join(R, "links/tomari.html"), "w", encoding="utf-8").write(out)
print("ok", n_all, n_inn)
