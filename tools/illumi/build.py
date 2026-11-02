"""関西イルミネーションのまとめページを作る（検索から人を呼ぶ冬のページ、10/31 オーナー「2やってみて」）。
python3 tools/illumi/build.py → links/illumination.html"""
import datetime, html, json, sys, os, re, urllib.parse, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from data import ITEMS
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
PREFS = ["大阪","京都","兵庫","奈良","滋賀","和歌山"]
PC = {"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"}
WD = "月火水木金土日"
def md(s):
    d = datetime.date.fromisoformat(s); return f"{d.month}/{d.day}（{WD[d.weekday()]}）"
def when(s, e):
    if s and e: return f"{md(s)}〜{md(e)}"
    if s: return f"{md(s)}〜"
    return ""
def state(s, e):
    if not s: return ("発表前", "pre")
    sd = datetime.date.fromisoformat(s); ed = datetime.date.fromisoformat(e) if e else None
    if ed and ed < TODAY: return ("終わりました", "end")
    if sd <= TODAY: return ("開催中", "on")
    return ("これから", "soon")
cards = {p: [] for p in PREFS}; ld = []; evs = {p: [] for p in PREFS}; lds = {p: [] for p in PREFS}
def key(it):
    return (it[3] is None, it[3] or "")
for it in sorted(ITEMS, key=key):
    p, n, m, s, e, free, url, last = it
    lab, cls = state(s, e)
    if cls == "end": continue
    d = when(s, e) if s else f"2026年の日程は発表前（昨年 {last}）"
    tags = f'<span class="st {cls}">{lab}</span>' + ('<span class="fr">無料</span>' if free else '')
    city, spot = m.split("｜")[0], re.sub(r"（.*?）", "", m.split("｜")[-1]).strip()
    q = f"{spot} {city}"
    gm = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)
    cards[p].append(f'<div class="it" data-pref="{p}"><a class="card" data-pref="{p}" data-map="{html.escape(q)}" data-s="{s or ""}" data-e="{e or ""}" href="{url}" target="_blank" rel="noopener"><div class="tg">{tags}</div><div class="d">{html.escape(d)}</div><div class="t">{html.escape(n)}</div><div class="m">{html.escape(m)}</div><div class="go">→</div></a><a class="mp" href="{gm}" target="_blank" rel="noopener" data-k="地図｜{html.escape(n)}">地図</a></div>')
    evs[p].append((n, m, s, e, free))
    if s:
        ev = {"@type":"Event","name":n,"startDate":s,"location":{"@type":"Place","name":m.split("｜")[-1],"address":f"{p}{'府' if p in ('大阪','京都') else '県'}{m.split('｜')[0]}"},"url":url,"eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode"}
        if e: ev["endDate"] = e
        if free: ev["isAccessibleForFree"] = True
        ld.append(ev); lds[p].append(ev)
SLUG = {"大阪":"osaka","京都":"kyoto","兵庫":"hyogo","奈良":"nara","滋賀":"shiga","和歌山":"wakayama"}
def fu(p): return p + ("府" if p in ("大阪","京都") else "県")
BASE = "https://townnote.pages.dev/"
upd = f"{TODAY.year}年{TODAY.month}月{TODAY.day}日"
_mj = os.path.join(os.path.dirname(__file__), "../../links/townnotes/map-illumi.js")
_yj = os.path.join(os.path.dirname(__file__), "../../links/assets/yado.js")
YV = hashlib.sha1(open(_yj, "rb").read()).hexdigest()[:8] if os.path.exists(_yj) else "0"  # 10/31 近くの宿
MV = hashlib.sha1(open(_mj, "rb").read()).hexdigest()[:8] if os.path.exists(_mj) else "0"
def jd(x): return f"{datetime.date.fromisoformat(x).month}/{datetime.date.fromisoformat(x).day}"
def faq(sel):
    """よくある質問（10/31 検索で上に出るため）。データから作るので、書いた事は全部一覧と同じ"""
    it = [x for p in sel for x in evs[p]]
    name = lambda x: x[0]
    qa = []
    fr = [x for x in it if x[4]]
    area = "関西" if len(sel) > 1 else fu(sel[0])
    if fr:
        qa.append((f"{area}で無料で見られるイルミネーションは？", f"無料で見られるのは{len(fr)}か所です。" + "、".join(name(x) for x in fr[:6]) + ("など。" if len(fr) > 6 else "。")))
    xm = [x for x in it if x[2] and x[3] and x[2] <= "2026-12-25" <= x[3]]
    if xm:
        qa.append((f"クリスマス（12月25日）に見られる{area}のイルミネーションは？", f"12月25日に開催しているのは{len(xm)}か所です。" + "、".join(name(x) for x in xm[:6]) + ("など。" if len(xm) > 6 else "。")))
    lg = sorted([x for x in it if x[3] and x[3] >= "2027-02-01"], key=lambda x: x[3], reverse=True)
    if lg:
        qa.append((f"{area}で年明けの2月以降も見られるイルミネーションは？", "、".join(f"{name(x)}（{jd(x[3])}まで）" for x in lg[:5]) + "です。"))
    st = sorted([x for x in it if x[2] and x[2] >= "2026-11-01"], key=lambda x: x[2])
    if st:
        nov = sum(1 for x in st if x[2] < "2026-11-16")
        qa.append((f"{area}のイルミネーションはいつから始まる？", (f"11月から始まる{len(st)}か所のうち、{nov}か所が11月前半に点灯します。" if nov else "") + "早い順に、" + "、".join(f"{name(x)}は{jd(x[2])}から" for x in st[:3]) + "です（日付は各公式の発表）。"))
    pre = [x for x in it if not x[2]]
    if pre:
        qa.append(("日程が「発表前」の所はどうなりますか？", f"{len(pre)}か所は2026年の日程がまだ発表されていません。昨年の期間を目安にのせていて、発表されしだい書き足します。"))
    h = '<section class="faq"><h2 class="fq">よくある質問</h2>' + "".join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in qa) + '</section>'
    j = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q, a in qa]}
    return h, j
def render(sel, fname, title, desc, ogt, en, h1a, h1b, sub, links, crumb):
    secs = ""
    for p in sel:
        secs += f'<section id="{p}" class="ps" style="--c:{PC[p]}"><h2>{fu(p)}のイルミネーション<small>{len(cards[p])}件</small></h2>' + "".join(cards[p]) + '</section>'
    nav = ('<div class="flt" id="flt"><button class="on" data-p="すべて">すべて</button>' + "".join(f'<button data-p="{p}" style="--pc:{PC[p]}">{p}</button>' for p in PREFS) + '</div>') if len(sel) > 1 else ""
    fh, fj = faq(sel)
    url = BASE + fname.replace(".html", "")  # workers.dev は .html を外したアドレスへ転送するので、正しいアドレスはこちら
    l = [x for p in sel for x in lds[p]]
    ldj = [{"@context":"https://schema.org","@type":"ItemList","name":ogt,"itemListElement":[{"@type":"ListItem","position":i+1,"item":ev} for i,ev in enumerate(l)]}, fj,
           {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u.replace(".html","")} for i,(n,u) in enumerate(crumb)]}]
    lds_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ldj)
    mapjs = f'<script src="townnotes/map-illumi.js?v={MV}" defer></script>' if len(sel) > 1 else ""
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:title" content="{ogt}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="https://townnote.pages.dev/assets/ogp.png"><meta name="twitter:card" content="summary">
<meta property="article:modified_time" content="{TODAY.isoformat()}T07:00:00+09:00">
<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
{lds_html}
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.head{{text-align:center;margin:0 -16px;padding:30px 16px 26px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px),#FFFFFF}}
.head img{{width:60px;height:60px}}
.en{{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:23px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:14px 0 10px;font-feature-settings:"palt"}}
h1 span{{display:block;font-size:14px;letter-spacing:.2em;color:#6B6058;margin-top:4px}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}}
.upd{{font-size:11px;color:#8C7B6E;margin-top:8px}}
.flt{{display:flex;flex-wrap:wrap;justify-content:center;gap:0 20px;margin:22px 0 6px;padding:10px 0;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4}}
.flt button{{border:none;background:none;border-radius:0;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer}}
.flt button.on{{color:var(--pc,#2B2622);border-bottom-color:var(--pc,#2B2622)}}
.ps{{scroll-margin-top:12px;margin-top:30px}}
h2{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:0 0 12px;padding-left:10px;border-left:3px solid var(--c);display:flex;align-items:baseline;gap:10px}}
h2 small{{font-family:"Zen Kaku Gothic New";font-size:11px;color:#8C7B6E;letter-spacing:.04em;font-weight:500}}
.card{{display:block;position:relative;text-decoration:none;color:inherit;background:#fff;border-radius:2px;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);padding:14px 40px 14px 16px;margin-bottom:12px}}
.tg{{display:flex;gap:6px;margin-bottom:6px}}
.card .st,.card .fr{{font-size:10.5px;letter-spacing:.06em;padding:1px 7px;border:1px solid;line-height:1.7}}
.card .st.on{{color:#fff;background:var(--c);border-color:var(--c)}}.card .st.soon{{color:var(--c)}}.card .st.pre{{color:#9C9187}}
.card .fr{{color:#6F8A5F}}
.card .d{{font-size:13px;color:var(--c);font-weight:700;letter-spacing:.02em}}
.card .t{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15.5px;line-height:1.5;margin:4px 0 4px;letter-spacing:.04em}}
.card .m{{font-size:12px;color:#7A6E66;line-height:1.6}}
.it{{position:relative;margin-bottom:12px}}.it .card{{margin-bottom:0;padding-bottom:30px}}
.mp{{position:absolute;left:16px;bottom:10px;font-size:11px;letter-spacing:.08em;color:#6B6058;text-decoration:none;border-bottom:1px solid #BFBFBF;line-height:1.4}}
.mp:before{{content:"";display:inline-block;width:8px;height:10px;margin-right:4px;vertical-align:-1px;background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 10'%3E%3Cpath d='M4 0a4 4 0 0 0-4 4c0 3 4 6 4 6s4-3 4-6a4 4 0 0 0-4-4z'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 10'%3E%3Cpath d='M4 0a4 4 0 0 0-4 4c0 3 4 6 4 6s4-3 4-6a4 4 0 0 0-4-4z'/%3E%3C/svg%3E") center/contain no-repeat}}
.go{{position:absolute;right:16px;top:50%;transform:translateY(-50%);font-family:Jost;color:#9C8775}}
.note{{font-size:12px;line-height:1.9;color:#7A6E66;background:#F5F5F5;padding:14px 16px;margin-top:30px}}
.back{{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.tn .lg .o{{display:none}}
.ft{{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}}
.faq{{margin-top:34px}}.faq .fq{{border-left-color:#8C7B6E}}
.faq details{{background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05);margin-bottom:8px;padding:12px 16px}}
.faq summary{{font-weight:700;font-size:14px;line-height:1.6;cursor:pointer}}.faq p{{font-size:13px;line-height:1.9;color:#5E544D;margin:8px 0 0}}
.pl{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:26px}}.pl .plh{{width:100%;text-align:center;font-size:11px;letter-spacing:.2em;color:#8C7B6E}}
.pl a{{font-size:13px;color:var(--pc,#2B2622);text-decoration:none;border:1px solid #D4D4D4;padding:6px 12px;background:#fff}}.pl a[aria-current]{{background:var(--pc);color:#fff;border-color:var(--pc)}}
/* 11/1 オーナー「昔のままのやつも確認しろ」→ カードをおでかけリストと同じ形に（白い角丸・左に府県の色の線・丸い札・ゴシックの題名・丸い矢印） */
html body .it .card,html body .card{{border:1px solid #E2E2E2;border-radius:8px;box-shadow:inset 4px 0 0 var(--c);padding:14px 16px 52px 18px}}
html body .card .tg{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}}
html body .card .st,html body .card .fr{{border:0;border-radius:99px;padding:4px 10px;font-size:11px;font-weight:700;letter-spacing:.04em;line-height:1.2}}
html body .card .st.on{{background:var(--c);color:#fff}}html body .card .st.soon{{background:color-mix(in srgb,var(--c) 12%,#fff);color:color-mix(in srgb,var(--c) 80%,#000)}}html body .card .st.pre{{background:#F1F2F4;color:#6B6058}}
html body .card .fr{{background:#fff;box-shadow:inset 0 0 0 1px #CFCFCF;color:#3A3A3A}}
html body .card .d{{font-size:13px;font-weight:500;color:#6B6058}}
html body .card .t{{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:16.5px;line-height:1.5;letter-spacing:0;color:#1C1C1C;margin:4px 0 6px}}
html body .card .go{{right:12px;top:auto;bottom:10px;transform:none;width:38px;height:38px;border-radius:50%;background:var(--c);color:#fff;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:300}}
html body .it .mp{{left:18px;bottom:21px}}html body .it>.yk{{left:72px;bottom:21px}}
</style><script src="assets/night.js?v=5"></script><script src="assets/menu.js?v=10" defer></script><script src="assets/v2sub.js?v=8" defer></script></head><body><div class="wrap">
<div class="head"><img src="assets/logo-s.png?v=2" width="60" height="60" alt="TOWN NOTE のロゴ"><div class="en">{en}</div>
<h1>{h1a}<span>{h1b}</span></h1>
<p class="sub">{sub}</p>
<div class="upd">{upd} 更新</div></div>
{nav}
{secs}
{fh}
<p class="note">日程は各公式の発表をもとにしています。名前を押すと公式のページ、「地図」を押すと場所が開きます。「発表前」は、2026年の日程がまだ出ていない所です（昨年の期間を目安にのせています）。発表されしだい書き足します。点灯時間や料金は変わることがあるので、お出かけ前にリンク先でご確認ください。</p>
<nav class="pl" aria-label="府県ごとのイルミネーション">{links}</nav>
<a class="back" href="/odekake">関西おでかけリストを見る</a>
<div class="ft">TOWN NOTE</div></div>
<script>(function(){{var t=new Date(Date.now()+9*36e5).toISOString().slice(0,10);document.querySelectorAll(".card").forEach(function(c){{var s=c.dataset.s,e=c.dataset.e,st=c.querySelector(".st");if(!s)return;if(e&&e<t){{(c.closest(".it")||c).remove();return;}}if(s<=t){{st.textContent="開催中";st.className="st on";}}else{{st.textContent="これから";st.className="st soon";}}}});document.querySelectorAll(".ps").forEach(function(x){{x.querySelector("small").textContent=x.querySelectorAll(".card").length+"件";if(!x.querySelector(".card"))x.style.display="none";}});var F=document.getElementById("flt");if(F)F.querySelectorAll("button").forEach(function(b){{b.onclick=function(){{F.querySelectorAll("button").forEach(function(x){{x.classList.remove("on");}});b.classList.add("on");var p=b.dataset.p;document.querySelectorAll(".ps").forEach(function(x){{x.style.display=((p=="すべて"||x.id==p)&&x.querySelector(".card"))?"":"none";}});try{{navigator.sendBeacon("/c",JSON.stringify({{k:"絞り込み：イルミネーション｜"+p}}));}}catch(e){{}}}};}});}})();</script>
<script>(function(){{var O=(function(){{try{{return localStorage.getItem("usagi_owner")==="1";}}catch(e){{return false;}}}})();function s(k){{if(O)return;try{{var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}});}}catch(e){{}}}}s("表示：イルミネーション"+(document.referrer&&!/usagi-odekake|townnote.pages/.test(document.referrer)?"（外から）":""));document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a");if(!a)return;var t=a.querySelector(".t"),n=a.getAttribute("data-k");s("クリック：イルミネーション｜"+(n||(t?t.textContent:a.textContent)));}},true);}})();</script>
{mapjs}<script src="assets/yado.js?v={YV}" defer></script>
</body></html>'''
OUT = os.path.join(os.path.dirname(__file__), "../../links/")
cnt = sum(len(v) for v in cards.values())
def plinks(cur):
    a = [f'<a href="illumination">関西ぜんぶ</a>'] if cur else []
    return '<div class="plh">府県ごとに見る</div>' + "".join(a) + "".join(f'<a href="illumination-{SLUG[p]}" style="--pc:{PC[p]}"{" aria-current=page" if p == cur else ""}>{fu(p)}</a>' for p in PREFS)
pages = {"illumination.html": render(PREFS, "illumination.html",
    "関西イルミネーション2026-2027｜大阪・京都・兵庫・奈良・滋賀・和歌山の日程一覧",
    f"関西6府県のイルミネーション{cnt}か所を、府県ごとに日程・場所・無料かどうかで一覧にしました。御堂筋イルミネーション、神戸イルミナージュ、姫路城イルミネーションなど。{upd}更新。",
    "関西イルミネーション2026-2027 日程一覧", "KANSAI ILLUMINATION", "関西イルミネーション", "2026 - 2027 日程一覧",
    f"大阪・京都・兵庫・奈良・滋賀・和歌山の{cnt}か所を、<br>府県ごとに日程・場所・無料かどうかでまとめました。", plinks(None),
    [("関西おでかけリスト", "odekake"), ("関西イルミネーション2026-2027", "illumination.html")])}
for p in PREFS:
    n = len(cards[p]); nm = "、".join(x[0] for x in evs[p][:3])
    fr = sum(1 for x in evs[p] if x[4])
    pages[f"illumination-{SLUG[p]}.html"] = render([p], f"illumination-{SLUG[p]}.html",
        f"{p}のイルミネーション2026-2027｜日程・場所・無料の{n}か所一覧",
        f"{fu(p)}のイルミネーション{n}か所（無料{fr}か所）を、日程・場所・無料かどうかで一覧にしました。{nm}など。点灯期間は各公式の発表どおり。{upd}更新。",
        f"{p}のイルミネーション2026-2027 日程一覧", f"{SLUG[p].upper()} ILLUMINATION", f"{p}のイルミネーション", "2026 - 2027 日程一覧",
        f"{fu(p)}の{n}か所を、日程・場所・<br>無料かどうかでまとめました。", plinks(p),
        [("関西おでかけリスト", "odekake"), ("関西イルミネーション2026-2027", "illumination.html"), (f"{p}のイルミネーション", f"illumination-{SLUG[p]}.html")])
for f, h in pages.items():
    open(OUT + f, "w").write(h)
sm = "".join(f'<url><loc>{BASE}{f.replace(".html", "")}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n' for f in ["", "odekake", *pages, "tomari.html", "ima.html"])
open(OUT + "sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
print(cnt, {p: len(v) for p, v in cards.items()}, len(pages), "pages")
