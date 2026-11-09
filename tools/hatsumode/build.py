"""関西の初詣ページ（/hatsumode）を作る。11/9 オーナー OK（見本 → 「ok」「初詣は紅葉ではなくない？」→ 絵は鳥居 HATSUMODE）。
形は関西の紅葉ページ（links/koyo.html、毎朝 tools/illumi/build.py が作る）を借りて、中身だけ入れ替える。データは data.tsv（公式ページだけ）。
使い方: python3 tools/hatsumode/build.py 2026-11-09"""
import datetime, html, json, os, re, sys, urllib.parse
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
BASE = "https://townnote.pages.dev/"
PREFS = ["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"]
s = open(os.path.join(ROOT, "links", "koyo.html"), encoding="utf-8").read()
PC = dict(re.findall(r'data-p="(\S+?)" style="--pc:(#[0-9A-Fa-f]+)"', s))
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "data.tsv"), encoding="utf-8") if l.strip() and not l.startswith("#")]
fu = lambda p: p + ("府" if p in ("大阪", "京都") else "県")
secs = ""; places = []
for p in PREFS:
    rs = [r for r in rows if r[0] == p]
    if not rs: continue
    cs = ""
    for _, n, city, tm, tr, yr, url in rs:
        tag = '<span class="st on">2027年の案内</span>' if yr == "2027年" else f'<span class="st pre">{"昨年" if yr == "昨年" else "例年"}の案内</span>'
        kv = f'<div class="kv"><span>時間</span>{html.escape(tm)}</div>' + (f'<div class="kv"><span>車・混雑</span>{html.escape(tr)}</div>' if tr not in ("", "—") else "")
        q = f"{n} {city}"; gm = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)
        cs += (f'<div class="it" data-pref="{p}"><a class="card" data-pref="{p}" data-map="{html.escape(q)}" href="{url}" target="_blank" rel="noopener">'
               f'<div class="tg">{tag}</div><div class="t">{html.escape(n)}</div><div class="m">{html.escape(city)}</div>{kv}<div class="go">→</div></a>'
               f'<a class="mp" href="{gm}" target="_blank" rel="noopener" data-k="地図｜{html.escape(n)}">地図</a></div>')
        places.append((p, n, city, tm, yr, url))
    secs += f'<section id="{p}" class="ps" style="--c:{PC.get(p, "#999")}"><h2>{fu(p)}の初詣<small>{len(rs)}か所</small></h2>{cs}</section>'
N = len(places); n27 = sum(1 for x in places if x[4] == "2027年")
names = "、".join(x[1] for x in places[:4])
title = f"関西の初詣2027｜大晦日・三が日の時間と交通規制（{N}か所）"
desc = f"関西6府県の初詣{N}か所の、大晦日と三が日の参拝時間・交通規制・駐車場を、各神社の公式ページからまとめました。{names}など。{TODAY.month}月{TODAY.day}日更新。"
# よくある質問（一覧と同じ事だけ）
qa = []
yo = [x for x in places if re.search(r"夜通し|24時間|終夜", x[3])]
if yo: qa.append(("大晦日の夜中にお参りできる関西の神社は？", "、".join(f"{x[1]}（{x[3].split('。')[0]}）" for x in yo) + "です。各神社の公式ページの案内です。"))
qa.append(("2027年の時間はもう決まっていますか？", (f"{n27}か所は2027年の案内が出ています。" if n27 else "") + "ほかは昨年・例年の案内です。新しい案内が出たら書き換えます。お出かけ前に公式ページをご確認ください。"))
faq = '<section class="faq"><h2 class="fq">よくある質問</h2>' + "".join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in qa) + "</section>"
ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関西の初詣2027", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Place", "name": x[1], "address": fu(x[0]) + x[2], "url": x[5]}} for i, x in enumerate(places)]},
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "関西おでかけリスト", "item": BASE + "odekake"}, {"@type": "ListItem", "position": 2, "name": "関西の初詣2027", "item": BASE + "hatsumode"}]}]
s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
s = s.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
s = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", s, count=1)
s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc), s, count=1)
s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc), s, count=1)
s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + "関西の初詣2027 大晦日・三が日の時間と交通規制", s, count=1)
s = s.replace(BASE + "koyo\"", BASE + "hatsumode\"")
s = re.sub(r'<div class="en">[^<]*</div>', '<div class="en">KANSAI HATSUMODE</div>', s, count=1)
s = re.sub(r"<h1>.*?</h1>", "<h1>関西の初詣<span>2027 大晦日・三が日の時間と交通規制</span></h1>", s, count=1, flags=re.S)
s = re.sub(r'<p class="sub">.*?</p>', f'<p class="sub">関西6府県の{N}か所の、大晦日と<br>三が日の時間・交通規制をまとめました。</p>', s, count=1, flags=re.S)
s = re.sub(r'<nav class="sw".*?</nav>', "", s, count=1, flags=re.S)
s = re.sub(r'<div class="tnb">.*?</div>', "", s, count=1, flags=re.S)
a = s.index('<section id="'); b = s.index('<section class="faq">'); e = s.index("</section>", b) + len("</section>")
s = s[:a] + secs + faq + s[e:]
s = re.sub(r'<p class="note">.*?</p>', '<p class="note">時間・交通規制・駐車場は、各神社の公式ページの案内をのせています。2027年の案内が出ていない所は、昨年・例年の内容です。名前を押すと公式のページ、「地図」を押すと場所が開きます。お出かけ前にリンク先でご確認ください。</p>', s, count=1, flags=re.S)
s = re.sub(r'<nav class="also".*?</nav>', '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/illumination" data-k="あわせて：関西イルミネーション">関西イルミネーション</a><a href="/tomari" data-k="あわせて：泊まりで行くおでかけ">泊まりで行くおでかけ</a><a href="/odekake" data-k="あわせて：関西おでかけリスト">関西おでかけリスト</a></nav>', s, count=1, flags=re.S)
s = s.replace("v2sub.js?v=12", "v2sub.js?v=12").replace("紅葉ライトアップ", "初詣")
open(os.path.join(ROOT, "links", "hatsumode.html"), "w", encoding="utf-8").write(s)
print("hatsumode", N, "places")
