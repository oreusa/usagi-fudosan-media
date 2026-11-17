"""開店・閉店ニュース（/kaiten）を作る。11/17 HP の新しい要素の1つめ（設計図 https://claude.ai/artifact/JmPbw1tcB6f9cDqzZc8uop 、
見本 https://claude.ai/artifact/XJ1fWongLiDBGeJQUq1wvG 。オーナー「月がきめていいよ」）。
元は tools/kaiten/kansai.json（月の毎晩 21:20 の回が「速報の種」から tools/kaiten/add.py で足す）。
形は関西の初詣ページ（links/hatsumode.html）の頭と下のバー・MENU・night.js を借りる。夜の色は night.js が作るので、ここでは書かない。
中身は全部 HTML に書く（Google が読めるように）。「これから／開いた／閉まる」と府県の切り替えは、見る日の日付で JS が分ける。
使い方: python3 tools/kaiten/build.py 2026-11-17"""
import datetime, html, json, os, re, sys, urllib.parse
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
BASE = "https://kansai.townnote.app/"
E = html.escape
DONE_DAYS = 30  # 「開いた」に残す日数
PREFS = ["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"]
KL = {"open": "開店", "pop": "期間限定", "close": "閉店"}
WD = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
items = json.load(open(os.path.join(HERE, "kansai.json"), encoding="utf-8"))["items"]


def day(x):
    return datetime.date.fromisoformat(x["d"])


def bucket(x, t=TODAY):
    n = (day(x) - t).days
    if x["k"] == "close":
        return "close" if n >= 0 else None
    if n >= 0:
        return "soon"
    if x["k"] == "pop" and x.get("end"):
        return "done" if datetime.date.fromisoformat(x["end"]) >= t else None
    return "done" if n >= -DONE_DAYS else None


live = [x for x in items if bucket(x)]
for x in live:
    assert x["p"] in PREFS, "府県の名前がちがう: " + x["n"]
    assert x["u"].startswith("https://"), "公式の発表が無い: " + x["n"]
cnt = {k: sum(bucket(x) == k for x in live) for k in ("soon", "done", "close")}


def card(x):
    q = urllib.parse.quote(re.sub(r"（.*?）", "", x["n"]) + " " + x["pl"].split("・")[0])
    end = f' data-end="{x["end"]}"' if x.get("end") else ""
    return (f'<article class="it" data-d="{x["d"]}" data-k="{x["k"]}" data-p="{x["p"]}"{end}><span class="tag {x["k"]}">{KL[x["k"]]}</span>'
            f'<h3 class="nm">{E(x["n"])}</h3><p class="pt">{E(x["pt"])}</p><dl><dt>場所</dt><dd>{E(x["p"])}・{E(x["pl"])}</dd>'
            + (f'<dt>時間</dt><dd>{E(x["tm"])}</dd>' if x.get("tm") else "") + "</dl>"
            f'<div class="ln"><a class="src" href="{E(x["u"])}" target="_blank" rel="noopener" data-k="公式の発表｜{E(x["n"])}">公式の発表 ↗</a>'
            f'<a href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener" data-k="地図｜{E(x["n"])}">地図</a></div></article>')


# 日付ごとにまとめる（日付がまだの物は fuzzy の言葉でまとめる）。並びは日付の順。JS が見る日に合わせて並べ替え・隠す
groups = {}
for x in sorted(live, key=lambda x: (x["d"], x["k"] != "close", x["n"])):
    groups.setdefault(x.get("fuzzy") or x["d"], {"d": x["d"], "f": x.get("fuzzy"), "a": []})["a"].append(x)
days_html = ""
for key, g in groups.items():
    d = datetime.date.fromisoformat(g["d"])
    md = (g["f"].replace("12月", "12.").replace("月", ".") if g["f"] else f"{d.month}.{d.day:02d}")
    days_html += (f'<section class="day" data-d="{g["d"]}"' + (' data-f="1"' if g["f"] else "") + f'><div class="dt"><div class="md">{E(md)}</div>'
                  f'<div class="wd">{"" if g["f"] else WD[d.weekday()]}</div><span class="left"></span></div><div class="items">'
                  + "".join(card(x) for x in g["a"]) + "</div></section>")

N = len(live)
s = open(os.path.join(ROOT, "links", "hatsumode.html"), encoding="utf-8").read()
title = f"関西の開店・閉店ニュース｜新しいお店・閉まるお店を公式の発表で（{TODAY.month}月{TODAY.day}日）"
desc = (f"関西6府県で、これから開くお店{cnt['soon']}件・この{DONE_DAYS}日に開いたお店{cnt['done']}件・閉まるお店{cnt['close']}件。"
        f"各社の公式の発表だけを毎日たしかめて足しています。日付・場所・時間と、公式の発表と地図へすぐ行けます。")
ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関西の開店・閉店ニュース",
       "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["n"], "url": x["u"]} for i, x in enumerate(sorted(live, key=lambda x: x["d"]))]},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "関西おでかけリスト", "item": BASE + "odekake"},
          {"@type": "ListItem", "position": 2, "name": "関西の開店・閉店ニュース", "item": BASE + "kaiten"}]}]
s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
CSS = ("<style>"
       ".cnt{display:grid;grid-template-columns:repeat(3,1fr);margin:18px 0 0;border-top:1px solid #E6E0D9;border-bottom:1px solid #E6E0D9}"
       ".cnt div{text-align:center;padding:12px 4px 11px;border-left:1px solid #E6E0D9}.cnt div:first-child{border-left:0}"
       ".cnt small{display:block;font-size:10.5px;letter-spacing:.12em;color:#8C7B6E}"
       ".cnt b{display:block;font-family:'Shippori Mincho',serif;font-weight:600;font-size:24px;color:#231E1B;margin-top:2px;font-variant-numeric:tabular-nums}"
       ".kbar{position:sticky;top:0;z-index:5;background:#fff;margin:10px -16px 0;padding:10px 16px 8px;border-bottom:1px solid #E6E0D9}"
       ".seg{display:grid;grid-template-columns:repeat(3,1fr);background:#F1EEEA;border-radius:10px;padding:3px}"
       ".seg button{font:700 13px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.06em;border:0;background:transparent;color:#8C7B6E;padding:8px 0;border-radius:8px;cursor:pointer}"
       ".seg button[aria-pressed=true]{background:#fff;color:#2B2622;box-shadow:0 1px 2px rgba(0,0,0,.08)}"
       ".kpref{display:flex;gap:0 16px;overflow-x:auto;scrollbar-width:none;margin-top:8px}.kpref::-webkit-scrollbar{display:none}"
       ".kpref button{flex:none;font:700 13px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.06em;border:0;background:none;color:#8C7B6E;padding:6px 0;border-bottom:1.5px solid transparent;cursor:pointer}"
       ".kpref button[aria-pressed=true]{color:#2B2622;border-bottom-color:#2B2622}"
       ".day{display:grid;grid-template-columns:62px 1fr;gap:0 14px;padding:18px 0 4px;border-bottom:1px solid #E6E0D9}"
       ".dt{position:sticky;top:96px;align-self:start}"
       ".dt .md{font-family:Jost,sans-serif;font-size:22px;letter-spacing:.02em;color:#231E1B;line-height:1.1;font-variant-numeric:tabular-nums}"
       ".dt .wd{font-family:Jost,sans-serif;font-size:10px;letter-spacing:.3em;color:#8C7B6E;margin-top:4px}"
       ".dt .left{display:inline-block;font-size:10.5px;font-weight:700;color:#6B6058;margin-top:6px}.dt .left.today{color:#3E6B57}"
       ".items{display:grid;gap:14px;min-width:0;padding-bottom:12px}.it{min-width:0}.it+.it{border-top:1px dashed #E6E0D9;padding-top:14px}"
       ".tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;border-radius:5px;padding:1px 7px;margin-bottom:4px}"
       ".tag.open{color:#3E6B57;background:#E8F0EB}.tag.close{color:#9A4B3C;background:#F5E6E2}.tag.pop{color:#7A5A2E;background:#F3ECE0}"
       ".nm{font-family:'Shippori Mincho',serif;font-weight:600;font-size:16.5px;line-height:1.6;letter-spacing:.03em;color:#231E1B;margin:0;word-break:auto-phrase}"
       ".pt{font-size:13.5px;line-height:1.85;color:#2B2622;margin:4px 0 0}"
       ".it dl{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;margin:8px 0 0;font-size:12.5px;line-height:1.75}"
       ".it dt{color:#8C7B6E;letter-spacing:.06em}.it dd{margin:0;color:#6B6058;min-width:0;overflow-wrap:anywhere}"
       ".ln{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}"
       ".ln a{font-size:12.5px;font-weight:700;color:#2B2622;text-decoration:none;border:1px solid #E6E0D9;border-radius:99px;padding:6px 12px}.ln a.src{background:#F7F5F2}"
       ".day[hidden],.it[hidden]{display:none}.kempty{font-size:13px;color:#6B6058;text-align:center;padding:36px 0;display:none}"
       ".kfol{margin-top:18px;text-align:center}.kfol p{font-size:13px;line-height:1.9;color:#6B6058;margin:0 0 10px}"
       ".kfol a{display:inline-block;margin:0 4px 8px;font-size:13px;font-weight:700;text-decoration:none;border-radius:99px;padding:9px 16px;background:#2B2622;color:#fff}"
       ".kfol a+a{background:#fff;color:#2B2622;box-shadow:inset 0 0 0 1px #2B2622}"
       "</style>")
s = s.replace("</head>", CSS + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
    s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + "関西の開店・閉店ニュース", s, count=1)
s = s.replace(BASE + 'hatsumode"', BASE + 'kaiten"')
s = re.sub(r'<body data-kind="[^"]*">', '<body data-kind="開店・閉店ニュース">', s, count=1)
s = re.sub(r'<div class="en">[^<]*</div>', '<div class="en">KANSAI NEW SHOPS</div>', s, count=1)
s = re.sub(r"<h1>.*?</h1>", "<h1>関西の開店・閉店ニュース<span>新しいお店・閉まるお店を公式の発表で</span></h1>", s, count=1, flags=re.S)
s = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">お店や施設の公式の発表だけを、毎日たしかめて足しています。<br>日付と街で、近くの新しいお店がすぐ分かります。</p>', s, count=1, flags=re.S)
s = re.sub(r'<div class="upd">.*?</div>', f'<div class="upd">{TODAY.year}年{TODAY.month}月{TODAY.day}日 更新・{N}件</div>', s, count=1, flags=re.S)
s = re.sub(r'<div class="flt" id="flt">.*?</div>', "", s, count=1, flags=re.S)
TOP = ('<div class="cnt" aria-label="件数"><div><small>これから開く</small><b id="n-soon">%d</b></div><div><small>この%d日に開いた</small><b id="n-done">%d</b></div>'
       '<div><small>閉まる</small><b id="n-close">%d</b></div></div>' % (cnt["soon"], DONE_DAYS, cnt["done"], cnt["close"])
       + '<div class="kbar"><div class="seg" role="group" aria-label="見るもの"><button type="button" data-v="soon" aria-pressed="true">これから</button>'
       '<button type="button" data-v="done" aria-pressed="false">開いた</button><button type="button" data-v="close" aria-pressed="false">閉まる</button></div>'
       '<div class="kpref" role="group" aria-label="府県"><button type="button" data-p="" aria-pressed="true">すべて</button>'
       + "".join(f'<button type="button" data-p="{p}" aria-pressed="false">{p}</button>' for p in PREFS) + "</div></div>"
       f'<main id="klist">{days_html}<p class="kempty" id="kempty">この条件のお店は、いまはありません。</p></main>')
a = s.index('<section id="'); b = s.index('<section class="faq">'); e = s.index("</section>", b) + len("</section>")
s = s[:a] + TOP + s[e:]
s = re.sub(r'<p class="note">.*?</p>', '<p class="note">日付・時間・内容は、各社の公式の発表をもとにしています。変わることがあるので、出かける前に「公式の発表」で確かめてください。閉店のセールの日数や値引きの中身は、発表に書かれた物だけを載せています。</p>'
           '<div class="kfol"><p>新しいお店の速報は、毎日 X にも出しています。</p><a href="https://x.com/fudosan_ai_si" target="_blank" rel="noopener" data-k="速報｜Xで毎日見る">X で毎日見る</a>'
           '<a href="https://www.threads.com/@fudousan_ai_si" target="_blank" rel="noopener" data-k="速報｜Threadsで見る">Threads で見る</a></div>', s, count=1, flags=re.S)
s = re.sub(r'<nav class="also".*?</nav>', '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/odekake" data-k="あわせて：おでかけリスト">関西おでかけリスト</a><a href="/ima" data-k="あわせて：いま行ける">いま行けるおでかけ</a><a href="/ranking" data-k="あわせて：まちランキング">関西まちランキング</a></nav>', s, count=1, flags=re.S)


def _sc(m):
    a = m.group(1)
    if "ld+json" in a or "night.js" in a or "menu.js" in a or "v2sub.js" in a:
        return m.group(0)
    return ""


s = re.sub(r"<script([^>]*)>(.*?)</script>", _sc, s, flags=re.S)
JS = ('<script>(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1";}catch(e){}'
      'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
      'c("表示：開店・閉店ニュース"+(document.referrer&&!/townnote\\.(pages|app)/.test(document.referrer)?"（外から）":""));'
      'document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("[data-k]"):null;if(a)c("クリック：開店・閉店ニュース｜"+a.getAttribute("data-k"));});'
      'var T=new Date();T=new Date(T.getTime()+(T.getTimezoneOffset()+540)*6e4);T=T.getFullYear()+"-"+("0"+(T.getMonth()+1)).slice(-2)+"-"+("0"+T.getDate()).slice(-2);'
      'function dd(a){return Math.round((new Date(a+"T00:00:00")-new Date(T+"T00:00:00"))/864e5)}'
      'function bk(x){var n=dd(x.dataset.d),k=x.dataset.k;if(k==="close")return n>=0?"close":"";if(n>=0)return "soon";if(k==="pop"&&x.dataset.end)return dd(x.dataset.end)>=0?"done":"";return n>=-%d?"done":""}'
      'var view="soon",pref="",L=document.getElementById("klist"),D=[].slice.call(L.querySelectorAll(".day"));'
      'function go(){var c={soon:0,done:0,close:0},any=false;D.forEach(function(s){var sh=0;s.querySelectorAll(".it").forEach(function(x){var b=bk(x);if(b)c[b]++;var on=b===view&&(!pref||x.dataset.p===pref);x.hidden=!on;if(on)sh++});s.hidden=!sh;if(sh)any=true;'
      'var n=dd(s.dataset.d),l=s.querySelector(".left");l.textContent=s.dataset.f?"日付はまだ":n===0?"きょう":n>0?"あと"+n+"日":(-n)+"日前";l.className="left"+(n===0?" today":"")});'
      '["soon","done","close"].forEach(function(k){document.getElementById("n-"+k).textContent=c[k]});document.getElementById("kempty").style.display=any?"none":"block";'
      'D.slice().sort(function(a,b){return view==="done"?(a.dataset.d<b.dataset.d?1:-1):(a.dataset.d<b.dataset.d?-1:1)}).forEach(function(s){L.insertBefore(s,document.getElementById("kempty"))})}'
      'document.querySelectorAll(".seg button").forEach(function(b){b.onclick=function(){view=b.dataset.v;document.querySelectorAll(".seg button").forEach(function(x){x.setAttribute("aria-pressed",x===b)});go();c("開店・閉店｜"+b.textContent)}});'
      'document.querySelectorAll(".kpref button").forEach(function(b){b.onclick=function(){pref=b.dataset.p;document.querySelectorAll(".kpref button").forEach(function(x){x.setAttribute("aria-pressed",x===b)});go();c("開店・閉店｜府県 "+(pref||"すべて"))}});'
      'go();})();</script>') % DONE_DAYS
s = s.replace("</body>", JS + "</body>", 1)
s = re.sub(r"/\*.*?\*/", lambda m: "" if "初詣" in m.group(0) else m.group(0), s, flags=re.S)
assert "初詣" not in s, "初詣の言葉が残っている: " + s[max(0, s.index("初詣") - 80):s.index("初詣") + 60]
assert "html.night .it" not in s, "ページ側に夜の色を書かない"
open(os.path.join(ROOT, "links", "kaiten.html"), "w", encoding="utf-8").write(s)
# サイトマップに無ければ足す（日付は tools/sitemap_dates.py が中身の変わった日にする）
for sm in ("sitemap.xml", "sitemap-all.xml"):
    p = os.path.join(ROOT, "links", sm)
    if os.path.exists(p):
        x = open(p, encoding="utf-8").read()
        if f"{BASE}kaiten<" not in x:
            open(p, "w", encoding="utf-8").write(x.replace("</urlset>", f"<url><loc>{BASE}kaiten</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>", 1))
print("kaiten", N, cnt)
