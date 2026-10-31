"""関西イルミネーションのまとめページを作る（検索から人を呼ぶ冬のページ、10/31 オーナー「2やってみて」）。
python3 tools/illumi/build.py → links/illumination.html"""
import datetime, html, json, sys, os
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
cards = {p: [] for p in PREFS}; ld = []
def key(it):
    return (it[3] is None, it[3] or "")
for it in sorted(ITEMS, key=key):
    p, n, m, s, e, free, url, last = it
    lab, cls = state(s, e)
    if cls == "end": continue
    d = when(s, e) if s else f"2026年の日程は発表前（昨年 {last}）"
    tags = f'<span class="st {cls}">{lab}</span>' + ('<span class="fr">無料</span>' if free else '')
    cards[p].append(f'<a class="card" data-s="{s or ""}" data-e="{e or ""}" href="{url}" target="_blank" rel="noopener"><div class="tg">{tags}</div><div class="d">{html.escape(d)}</div><div class="t">{html.escape(n)}</div><div class="m">{html.escape(m)}</div><div class="go">→</div></a>')
    if s:
        ev = {"@type":"Event","name":n,"startDate":s,"location":{"@type":"Place","name":m.split("｜")[-1],"address":f"{p}{'府' if p in ('大阪','京都') else '県'}{m.split('｜')[0]}"},"url":url,"eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode"}
        if e: ev["endDate"] = e
        if free: ev["isAccessibleForFree"] = True
        ld.append(ev)
nav = '<button class="on" data-p="すべて">すべて</button>' + "".join(f'<button data-p="{p}" style="--pc:{PC[p]}">{p}</button>' for p in PREFS)
secs = ""
for p in PREFS:
    secs += f'<section id="{p}" class="pf" style="--c:{PC[p]}"><h2>{p}{"府" if p in ("大阪","京都") else "県"}<small>{len(cards[p])}件</small></h2>' + "".join(cards[p]) + '</section>'
cnt = sum(len(v) for v in cards.values())
upd = f"{TODAY.year}年{TODAY.month}月{TODAY.day}日"
TITLE = "関西イルミネーション2026-2027｜大阪・京都・兵庫・奈良・滋賀・和歌山の日程一覧"
DESC = f"関西6府県のイルミネーション{cnt}か所を、府県ごとに日程・場所・無料かどうかで一覧にしました。御堂筋イルミネーション、神戸イルミナージュ、姫路城イルミネーションなど。{upd}更新。"
URL = "https://usagi-odekake.usagi-fudosan.workers.dev/illumination.html"
page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}</title><meta name="description" content="{DESC}"><link rel="canonical" href="{URL}">
<meta property="og:type" content="article"><meta property="og:url" content="{URL}"><meta property="og:title" content="関西イルミネーション2026-2027 日程一覧"><meta property="og:description" content="{DESC}">
<meta property="og:image" content="https://usagi-odekake.usagi-fudosan.workers.dev/assets/ogp.png"><meta name="twitter:card" content="summary">
<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="assets/ogp.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"ItemList","name":"関西イルミネーション2026-2027","itemListElement":[{"@type":"ListItem","position":i+1,"item":ev} for i,ev in enumerate(ld)]},ensure_ascii=False)}</script>
<style>
body{{margin:0;background:#FDFCFA;font-family:"Zen Kaku Gothic New";color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.head{{text-align:center;margin:0 -16px;padding:30px 16px 26px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px),#FDFCFA}}
.head img{{width:60px;height:60px}}
.en{{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:23px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:14px 0 10px;font-feature-settings:"palt"}}
h1 span{{display:block;font-size:14px;letter-spacing:.2em;color:#6B6058;margin-top:4px}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}}
.upd{{font-size:11px;color:#8C7B6E;margin-top:8px}}
.flt{{display:flex;flex-wrap:wrap;justify-content:center;gap:0 20px;margin:22px 0 6px;padding:10px 0;border-top:1px solid #DDD3C8;border-bottom:1px solid #DDD3C8}}
.flt button{{border:none;background:none;border-radius:0;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer}}
.flt button.on{{color:var(--pc,#2B2622);border-bottom-color:var(--pc,#2B2622)}}
.pf{{scroll-margin-top:12px;margin-top:30px}}
h2{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:0 0 12px;padding-left:10px;border-left:3px solid var(--c);display:flex;align-items:baseline;gap:10px}}
h2 small{{font-family:"Zen Kaku Gothic New";font-size:11px;color:#8C7B6E;letter-spacing:.04em;font-weight:500}}
.card{{display:block;position:relative;text-decoration:none;color:inherit;background:#fff;border-radius:2px;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);padding:14px 40px 14px 16px;margin-bottom:12px}}
.tg{{display:flex;gap:6px;margin-bottom:6px}}
.st,.fr{{font-size:10.5px;letter-spacing:.06em;padding:1px 7px;border:1px solid;line-height:1.7}}
.st.on{{color:#fff;background:var(--c);border-color:var(--c)}}.st.soon{{color:var(--c)}}.st.pre{{color:#9C9187}}
.fr{{color:#6F8A5F}}
.d{{font-size:13px;color:var(--c);font-weight:700;letter-spacing:.02em}}
.t{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15.5px;line-height:1.5;margin:4px 0 4px;letter-spacing:.04em}}
.m{{font-size:12px;color:#7A6E66;line-height:1.6}}
.go{{position:absolute;right:16px;top:50%;transform:translateY(-50%);font-family:Jost;color:#9C8775}}
.note{{font-size:12px;line-height:1.9;color:#7A6E66;background:#F7F2EC;padding:14px 16px;margin-top:30px}}
.back{{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.ft{{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}}
</style></head><body><div class="wrap">
<div class="head"><img src="assets/logo-s.png" width="60" height="60" alt="うさぎ│TOWN NOTES のロゴ"><div class="en">KANSAI ILLUMINATION</div>
<h1>関西イルミネーション<span>2026 - 2027 日程一覧</span></h1>
<p class="sub">大阪・京都・兵庫・奈良・滋賀・和歌山の{cnt}か所を、<br>府県ごとに日程・場所・無料かどうかでまとめました。</p>
<div class="upd">{upd} 更新</div></div>
<div class="flt" id="flt">{nav}</div>
{secs}
<p class="note">日程はウォーカープラスと各公式の発表をもとにしています。「発表前」は、2026年の日程がまだ出ていない所です（昨年の期間を目安にのせています）。発表されしだい書き足します。点灯時間や料金は変わることがあるので、お出かけ前にリンク先でご確認ください。</p>
<a class="back" href="./">関西おでかけリストを見る</a>
<div class="ft">うさぎ│TOWN NOTES</div></div>
<script>(function(){{var t=new Date(Date.now()+9*36e5).toISOString().slice(0,10);document.querySelectorAll(".card").forEach(function(c){{var s=c.dataset.s,e=c.dataset.e,st=c.querySelector(".st");if(!s)return;if(e&&e<t){{c.remove();return;}}if(s<=t){{st.textContent="開催中";st.className="st on";}}else{{st.textContent="これから";st.className="st soon";}}}});document.querySelectorAll(".pf").forEach(function(x){{x.querySelector("small").textContent=x.querySelectorAll(".card").length+"件";}});var F=document.getElementById("flt");F.querySelectorAll("button").forEach(function(b){{b.onclick=function(){{F.querySelectorAll("button").forEach(function(x){{x.classList.remove("on");}});b.classList.add("on");var p=b.dataset.p;document.querySelectorAll(".pf").forEach(function(x){{x.style.display=(p=="すべて"||x.id==p)?"":"none";}});try{{navigator.sendBeacon("/c",JSON.stringify({{k:"絞り込み：イルミネーション｜"+p}}));}}catch(e){{}}}};}});}})();</script>
<script>(function(){{var O=(function(){{try{{return localStorage.getItem("usagi_owner")==="1";}}catch(e){{return false;}}}})();function s(k){{if(O)return;try{{var b=JSON.stringify({{k:k}});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{{method:"POST",body:b,keepalive:true}});}}catch(e){{}}}}s("表示：イルミネーション"+(document.referrer&&!/usagi-odekake/.test(document.referrer)?"（外から）":""));document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a");if(!a)return;var t=a.querySelector(".t");s("クリック：イルミネーション｜"+(t?t.textContent:a.textContent));}},true);}})();</script>
</body></html>'''
open(os.path.join(os.path.dirname(__file__), "../../links/illumination.html"), "w").write(page)
print(cnt, {p: len(v) for p, v in cards.items()})
