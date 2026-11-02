"""大阪市24区 地価ランキングのページ（links/chika-osaka.html）を作る。
数字は大阪府「令和8年地価公示」報道資料 p.5 市区町村別対前年平均変動率表（1月1日時点）のまま。
使い方: python3 tools/chika/make.py [--live]   （--live が無いと noindex の見本）
"""
import html, json, sys

SRC = "https://www.pref.osaka.lg.jp/documents/125605/houdour8_1.pdf"
# 区: (住宅地R7, 住宅地R8, 商業地R7, 商業地R8)
D = {
 "都島区": (7.7, 8.5, 9.1, 12.3), "東成区": (7.9, 8.4, 10.1, 11.8), "生野区": (3.7, 4.0, 5.0, 5.5),
 "旭区": (5.7, 5.9, 4.1, 7.8), "城東区": (8.6, 8.9, 9.5, 12.4), "鶴見区": (8.2, 8.8, 9.9, 12.1),
 "阿倍野区": (7.3, 6.9, 8.2, 7.6), "住吉区": (5.4, 5.8, 6.3, 6.7), "住之江区": (3.8, 4.4, 8.1, 8.4),
 "平野区": (2.4, 3.9, 4.1, 5.0), "東住吉区": (4.3, 4.9, 3.9, 4.4), "西成区": (6.1, 7.9, 8.4, 9.3),
 "此花区": (3.2, 4.2, 8.2, 6.1), "港区": (3.5, 5.1, 5.8, 6.4), "大正区": (2.6, 4.0, 6.2, 7.1),
 "西淀川区": (3.3, 4.2, 5.1, 6.8), "淀川区": (7.4, 7.8, 9.7, 10.6), "東淀川区": (7.5, 8.5, 8.3, 9.8),
 "北区": (7.9, 9.2, 13.4, 14.0), "福島区": (7.2, 8.3, 12.5, 15.0), "中央区": (7.7, 8.4, 14.2, 15.5),
 "西区": (8.4, 10.5, 13.9, 15.3), "天王寺区": (6.8, 7.6, 7.2, 7.8), "浪速区": (9.7, 10.9, 14.3, 15.5),
}
AVG = (5.8, 6.5, 11.6, 12.7)
assert len(D) == 24
URL = "https://townnote.pages.dev/chika-osaka"
live = "--live" in sys.argv


def rank(i_now, i_prev):
    rows = sorted(D.items(), key=lambda kv: -kv[1][i_now])
    out, prev_v, prev_r = [], None, 0
    for n, (name, v) in enumerate(rows, 1):
        r = prev_r if v[i_now] == prev_v else n
        prev_v, prev_r = v[i_now], r
        out.append((r, name, v[i_now], v[i_prev]))
    return out


def li(rows, avg_now, avg_prev, mx=None):
    mx = mx or max(r[2] for r in rows)
    h = []
    for r, name, now, prev in rows:
        d = round(now - prev, 1)
        ds = ("+" if d > 0 else "−" if d < 0 else "±") + f"{abs(d):.1f}"
        cls = "up" if d > 0 else "dn" if d < 0 else ""
        top = " top" if r <= 3 else ""
        h.append(
            f'<li class="r{top}"><span class="no">{r}</span><span class="nm">{name}</span>'
            f'<span class="bar"><i style="width:{now / mx * 100:.1f}%"></i></span>'
            f'<span class="v">+{now:.1f}<small>%</small></span>'
            f'<span class="pv">前年 +{prev:.1f}%<b class="{cls}">{ds}pt</b></span></li>')
    return "\n".join(h)


res = rank(1, 0)
com = rank(3, 2)
mx = max(max(v[1], v[3]) for v in D.values())
top3 = "・".join(f"{n} +{v:.1f}%" for _, n, v, _ in res[:3])
desc = (f"大阪市24区の住宅地・商業地の地価の上がり幅を、令和8年地価公示（大阪府発表）の数字でランキングにしました。"
        f"住宅地の1位は{res[0][1]}（+{res[0][2]:.1f}%）、市の平均は+{AVG[1]:.1f}%。前の年との差も見られます。")
faq = [
    ("大阪市で住宅地の地価がいちばん上がった区は？",
     f"令和8年地価公示（1月1日時点）では、{res[0][1]}の+{res[0][2]:.1f}%がいちばん大きく、2位は{res[1][1]}（+{res[1][2]:.1f}%）、3位は{res[2][1]}（+{res[2][2]:.1f}%）でした。"),
    ("大阪市の平均はどれくらい？",
     f"住宅地の平均は+{AVG[1]:.1f}%（前の年は+{AVG[0]:.1f}%）、商業地の平均は+{AVG[3]:.1f}%（前の年は+{AVG[2]:.1f}%）です。24区すべてで住宅地・商業地ともプラスでした。"),
    ("前の年より上がり幅が小さくなった区は？",
     "住宅地で前の年より上がり幅が小さくなったのは、阿倍野区（+7.3%→+6.9%）だけです。商業地では此花区（+8.2%→+6.1%）と阿倍野区（+8.2%→+7.6%）が小さくなりました。"),
    ("この数字で、わが家の値段がわかりますか？",
     "わかりません。区の中の調査地点の平均の上がり幅で、1軒ずつの値段ではありません。家の値段は、場所・広さ・築年数などで大きく変わります。"),
]
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Dataset", "name": "大阪市24区 地価の上がり幅ランキング（令和8年地価公示）", "description": desc,
     "isBasedOn": SRC, "temporalCoverage": "2026-01-01", "spatialCoverage": "大阪市"},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}

E = html.escape
page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>大阪市24区 地価ランキング2026｜住宅地・商業地の上がり幅（令和8年地価公示）</title>
<meta name="description" content="{E(desc)}">
{'' if live else '<meta name="robots" content="noindex">'}{'<link rel="canonical" href="' + URL + '">' if live else ''}
<meta property="og:type" content="article"><meta property="og:url" content="{URL}"><meta property="og:title" content="大阪市24区 地価ランキング2026"><meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="https://townnote.pages.dev/assets/ogp.png"><meta name="twitter:card" content="summary">
<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.head{{text-align:center;margin:0 -16px;padding:30px 16px 26px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px)}}
.head img{{width:60px;height:60px}}
.en{{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:23px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:14px 0 10px;font-feature-settings:"palt"}}
h1 span{{display:block;font-size:14px;letter-spacing:.2em;color:#6B6058;margin-top:4px}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}}
.upd{{font-size:11px;color:#8C7B6E;margin-top:8px}}
.sum{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:22px 0 0}}
.sum div{{background:#F5F5F5;padding:12px 14px}}.sum b{{display:block;font-family:Jost;font-size:22px;font-weight:500;color:#B97A62}}.sum span{{font-size:11px;color:#7A6E66;letter-spacing:.04em}}
.flt{{display:flex;justify-content:center;gap:0 28px;margin:24px 0 8px;padding:10px 0;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4}}
.flt button{{border:none;background:none;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:14px;font-weight:700;letter-spacing:.08em;color:#8C7B6E;border-bottom:1px solid transparent;cursor:pointer}}
.flt button.on{{color:#2B2622;border-bottom-color:#2B2622}}
h2{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:22px 0 4px;padding-left:10px;border-left:3px solid #B97A62}}
.cap{{font-size:11.5px;color:#8C7B6E;margin:0 0 10px;line-height:1.7}}
ol{{list-style:none;margin:0;padding:0}}
.r{{display:grid;grid-template-columns:26px 1fr auto;align-items:center;column-gap:10px;row-gap:5px;padding:11px 2px;border-bottom:1px solid #ECECEC}}
.no{{font-family:Jost;font-size:14px;color:#9C9187;text-align:center;grid-row:1/4}}
.top .no{{color:#fff;background:#B97A62;border-radius:50%;width:24px;height:24px;line-height:24px;font-size:13px}}
.nm{{grid-column:2;grid-row:1;font-weight:700;font-size:14px;letter-spacing:.04em}}
.bar{{grid-column:2/4;grid-row:2;height:6px;background:#F1F2F4;position:relative}}.bar i{{position:absolute;left:0;top:0;bottom:0;background:#D9A48C}}.top .bar i{{background:#B97A62}}
.v{{grid-column:3;grid-row:1;font-family:Jost;font-weight:500;font-size:17px;text-align:right}}.v small{{font-size:11px;margin-left:1px}}
.pv{{grid-column:2/4;grid-row:3;font-size:11px;color:#8C7B6E}}.pv b{{font-weight:500;margin-left:8px}}.pv .up{{color:#6F8A5F}}.pv .dn{{color:#B05A4A}}
.avg{{display:flex;justify-content:space-between;font-size:13px;padding:10px 4px;background:#F5F5F5;margin-top:8px}}.avg b{{font-family:Jost;font-weight:500}}
.pane{{display:none}}.pane.on{{display:block}}
.faq{{margin-top:34px}}.faq details{{background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);margin-bottom:8px;padding:12px 16px}}
.faq summary{{font-weight:700;font-size:14px;line-height:1.6;cursor:pointer}}.faq p{{font-size:13px;line-height:1.9;color:#5E544D;margin:8px 0 0}}
.note{{font-size:12px;line-height:1.9;color:#7A6E66;background:#F5F5F5;padding:14px 16px;margin-top:30px;word-break:break-all}}.note a{{color:#7A6E66}}
.uru{{display:block;text-decoration:none;color:#2B2622;border:1px solid #2B2622;padding:16px;margin-top:30px;text-align:center}}
.uru .k{{font-size:11px;letter-spacing:.2em;color:#8C7B6E}}.uru .t{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.08em;margin:6px 0 4px}}.uru .m{{font-size:12px;color:#6B6058;line-height:1.8}}
.back{{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.ft{{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}}
</style><script src="assets/night.js?v=8"></script><script src="assets/menu.js?v=10" defer></script><script src="assets/v2sub.js?v=8" defer></script></head><body><div class="wrap">
<div class="head"><img src="assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ"><div class="en">OSAKA CITY ─ LAND PRICE</div>
<h1>大阪市24区 地価ランキング<span>2026 住宅地・商業地の上がり幅</span></h1>
<p class="sub">大阪府が発表した令和8年地価公示の数字で、<br>24区を上がり幅の大きい順に並べました。</p>
<div class="upd">2026年1月1日時点の数字（2026年11月1日 作成）</div></div>
<div class="sum"><div><span>住宅地の1位</span><b>{res[0][1]} +{res[0][2]:.1f}%</b></div><div><span>大阪市の平均（住宅地）</span><b>+{AVG[1]:.1f}%</b></div></div>
<nav class="flt"><button class="on" data-p="res">住宅地</button><button data-p="com">商業地</button></nav>
<section class="pane on" id="res"><h2>住宅地の上がり幅</h2><p class="cap">区の中の調査地点の平均。右は前の年（令和7年）と、そこからの差です。</p>
<ol>
{li(res, AVG[1], AVG[0])}
</ol><div class="avg"><span>大阪市の平均</span><b>+{AVG[1]:.1f}%（前年 +{AVG[0]:.1f}%）</b></div></section>
<section class="pane" id="com"><h2>商業地の上がり幅</h2><p class="cap">お店・オフィスの多い場所の調査地点の平均です。</p>
<ol>
{li(com, AVG[3], AVG[2])}
</ol><div class="avg"><span>大阪市の平均</span><b>+{AVG[3]:.1f}%（前年 +{AVG[2]:.1f}%）</b></div></section>
<section class="faq"><h2>よくある質問</h2>
{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}
</section>
<a class="uru" href="uru.html" data-k="お家を売る前に大事なこと"><div class="k">お家を売る・買う前に</div><div class="t">お家を売る前に大事なこと</div><div class="m">売るか、持ち続けるか。<br>迷ったときに読むページです。</div></a>
<p class="note">出典：大阪府「令和8年地価公示 報道資料」p.5 市区町村別対前年平均変動率表（価格時点 2026年1月1日）<br><a href="{SRC}" data-k="出典（大阪府）">{SRC}</a><br>数字は区ごとの調査地点の平均の変動率で、1軒ずつの値段ではありません。</p>
<a class="back" href="fudosan-list">関西不動産リストを見る</a><a class="back" href="chika-kansai" style="margin-top:12px">関西 ぜんぶの街のランキングを見る</a>
<div class="ft">TOWN NOTE</div></div>
<script>document.querySelectorAll(".flt button").forEach(function(b){{b.onclick=function(){{document.querySelectorAll(".flt button,.pane").forEach(function(x){{x.classList.remove("on")}});b.classList.add("on");document.getElementById(b.dataset.p).classList.add("on");}}}});</script>
<script>(function(){{var O=(function(){{try{{return localStorage.getItem("usagi_owner")==="1";}}catch(e){{return false;}}}})();function s(k){{if(O)return;try{{var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}});}}catch(e){{}}}}s("表示：地価ランキング大阪市"+(document.referrer&&!/usagi-odekake|townnote.pages/.test(document.referrer)?"（外から）":""));document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a,.flt button");if(!a)return;s("クリック：地価ランキング大阪市｜"+(a.getAttribute("data-k")||a.textContent.trim()));}},true);}})();</script>
</body></html>
'''
open("links/chika-osaka.html", "w", encoding="utf-8").write(page)
print("ok", "live" if live else "preview(noindex)", res[0], com[0])
