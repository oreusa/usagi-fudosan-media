"""関西の「ふるさと納税 寄付1万円でどれだけもらえるか」ページ（links/furusato.html）を作る。
11/27 owner「できること全部やろう」。関東 LIFE の /furusato（akari scripts/furusato.py）と同じ中身を関西にも（関東と関西は同じに）。
品と値段は燈が毎回楽天のAPIで取り直す akari data/furusato.json をそのまま使う（数字を書き写さない＝まちがえない）。
形は開店ニュース（links/kaiten.html）の1店のページを借りる。12/31 を過ぎたら「来年の分」と書き換える。
使い方: python3 tools/furusato/build.py 2026-11-27 [furusato.json のパス（なければ ../akari-auto/data/furusato.json）]"""
import datetime, html, json, os, re, sys

TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
SRC = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "..", "akari-auto", "data", "furusato.json")
BASE = "https://kansai.townnote.app/"
E = html.escape

d = json.load(open(SRC, encoding="utf-8"))
cats = [c for c in d["cats"] if c.get("top")]
if not cats:
    sys.exit("furusato: 品が0件（akari data/furusato.json）")
at = d.get("at", "")[:16]
end = datetime.date(TODAY.year, 12, 31)
left = (end - TODAY).days
UNIT = {"kg": "kg", "m": "m", "L": "L"}


def card(r, i, unit, avg):
    per = f'{r["per"]:,.1f}'.rstrip("0").rstrip(".")
    up = round((r["per"] / avg - 1) * 100) if avg else 0
    st = f'★{r["av"]:.2f}（{r["rc"]:,}件）' if r.get("rc") else ""
    return (f'<li class="fz"><a href="{E(r["url"])}" target="_blank" rel="noopener sponsored" data-k="ふるさと｜{E(r["shop"])}">'
            f'<span class="no">{i}</span>'
            + (f'<img src="{E(r["img"])}" alt="" width="88" height="88" loading="lazy" decoding="async">' if r.get("img") else "<span></span>")
            + f'<span class="tx"><b>{E(r["shop"])}</b><span class="nm">{E(r["name"])}</span>'
            f'<span class="nu"><em>{per}{UNIT.get(unit, unit)}</em> / 寄付1万円'
            + (f'<i>平均より{up}%多い</i>' if up >= 10 else "") + "</span>"
            f'<span class="mt">寄付 {r["price"]:,}円・{E(r["amt"])}{("・" + st) if st else ""}</span></span></a></li>')


secs = ""
for c in cats:
    secs += (f'<section class="sp-sec" id="{c["key"]}"><h2>{E(c["title"])}<small>寄付1万円あたり 平均 {c["avg"]:,.1f}{UNIT.get(c["unit"], c["unit"])}</small></h2>'
             '<ol class="fzl">' + "".join(card(r, i + 1, c["unit"], c["avg"]) for i, r in enumerate(c["top"])) + "</ol></section>")
N = sum(len(c["top"]) for c in cats)
names = "・".join(c["title"] for c in cats)
title = f"ふるさと納税 {TODAY.year}年の締め切り前に｜寄付1万円でいちばん多くもらえる{names}"
desc = (f"ふるさと納税の{names}を、楽天の返礼品から「寄付1万円あたりの量」でくらべました（口コミ30件以上・★4以上）。"
        f"{TODAY.year}年分は12月31日まで。{TODAY.month}月{TODAY.day}日更新。")[:150]
tab = "".join(f'<a href="#{c["key"]}">{E(c["title"])}</a>' for c in cats)
body = ('<nav class="sp-bc" aria-label="現在地"><a href="/">TOWN NOTE</a> › ふるさと納税</nav>'
        '<div class="fzh"><p class="en">FURUSATO NOZEI</p>'
        f'<h1>ふるさと納税、寄付1万円で<br>いちばん多くもらえるのは？</h1>'
        f'<p class="lead">お米・トイレットペーパー・水を、楽天の返礼品から「寄付1万円あたりの量」で並べました。口コミ30件以上・★4以上の品だけです。</p>'
        + (f'<p class="dl"><b>{TODAY.year}年分の締め切り 12月31日</b><span>あと{left}日</span></p>' if left >= 0 else "")
        + f'<nav class="fzt" aria-label="種類">{tab}</nav></div>'
        + secs +
        '<section class="sp-sec"><h2>はじめての人へ</h2><dl class="sp-dl">'
        '<dt>いくらまで</dt><dd>自己負担2,000円で済む上限は、年収と家族で変わります。楽天ふるさと納税の「控除上限額シミュレーター」で先に確かめると安心です。</dd>'
        '<dt>手続き</dt><dd>会社員で寄付先が5つまでなら「ワンストップ特例」の申請書を寄付先に送れば、確定申告はいりません（翌年1月10日必着）。</dd>'
        '<dt>締め切り</dt><dd>その年の分は12月31日の寄付まで。年末はお米・トイレットペーパーなどの人気の品が品切れになりやすいので、早めがおすすめです。</dd>'
        '</dl></section>'
        f'<p class="sp-chk">品・寄付の金額・口コミは、楽天の返礼品のデータ（{E(at)} 取得）です。量は品の名前から読んだもので、選べる品・定期便はくらべていません。寄付の前に楽天のページでご確認ください。'
        'このページのリンクは広告（楽天アフィリエイト）です。紹介料をいただくことがあります。</p>'
        '<p class="sp-more"><a href="/kaiten" data-k="ふるさと｜開店ニュース">関西の開店・閉店ニュースも見る →</a></p>')
CSS = ("<style>"
       ".fzh{margin:18px 0 0}.fzh .en{font:500 11px Jost,sans-serif;letter-spacing:.24em;color:#8C7B6E;margin:0}"
       ".fzh h1{font-family:'Shippori Mincho',serif;font-weight:600;font-size:23px;line-height:1.55;color:#231E1B;margin:6px 0 0;text-wrap:balance}"
       ".fzh .lead{font-size:14px;line-height:1.9;color:#2B2622;margin:12px 0 0}"
       ".fzh .dl{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:14px 0 0;border:1px solid #E6E0D9;border-radius:14px;padding:12px 14px}"
       ".fzh .dl b{font-size:14px;color:#231E1B}.fzh .dl span{margin-left:auto;font-size:12.5px;font-weight:700;color:#fff;background:#7A5230;border-radius:99px;padding:5px 12px}"
       ".fzt{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 0}.fzt a{font-size:13px;font-weight:700;color:#2B2622;border:1px solid #2B2622;border-radius:99px;padding:7px 14px;text-decoration:none}"
       ".sp-sec h2 small{display:block;font:500 11.5px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.02em;color:#8C7B6E;margin-top:2px}"
       ".fzl{list-style:none;margin:0;padding:0}.fz{border-bottom:1px solid #EFEAE4}"
       ".fz a{display:grid;grid-template-columns:22px 72px 1fr;gap:10px;align-items:start;padding:12px 0;text-decoration:none;color:inherit}"
       ".fz .no{font:500 16px Jost,sans-serif;color:#7A5230;padding-top:2px}.fz img{width:72px;height:72px;object-fit:cover;border-radius:10px;background:#F1EEEA}"
       ".fz .tx{min-width:0;display:flex;flex-direction:column;gap:3px}.fz b{font-size:12px;color:#8C7B6E}"
       ".fz .nm{font-size:13px;line-height:1.6;color:#231E1B;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
       ".fz .nu{font-size:12px;color:#6B6058}.fz .nu em{font:600 18px Jost,sans-serif;font-style:normal;color:#231E1B;margin-right:2px}"
       ".fz .nu i{font-style:normal;font-weight:700;color:#3E6B57;margin-left:8px}.fz .mt{font-size:11.5px;color:#8C7B6E}"
       "</style>")

src = open(os.path.join(ROOT, "tools", "kaiten", "build.py"), encoding="utf-8").read()
ns = {}
exec(re.search(r"^SCSS = \(.*?\"</style>\"\)", src, re.M | re.S).group(0), ns)
t = open(os.path.join(ROOT, "links", "kaiten.html"), encoding="utf-8").read()
url = BASE + "furusato"
ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "ふるさと納税 寄付1万円あたりの量でくらべた返礼品",
       "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": r["name"][:60], "url": r["plain"]} for i, r in enumerate([r for c in cats for r in c["top"]])]},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "TOWN NOTE", "item": BASE},
          {"@type": "ListItem", "position": 2, "name": "ふるさと納税", "item": url}]}]
t = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", t, count=1)
for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
    t = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), t, count=1)
t = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E("ふるさと納税 寄付1万円でいちばん多くもらえる品"), t, count=1)
t = t.replace(f'"{BASE}kaiten"', f'"{url}"')
t = re.sub(r'<script type="application/ld\+json">.*?</script>', "", t, flags=re.S)
t = t.replace("</head>", ns["SCSS"] + CSS + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
a = t.index('<div class="head">'); b = t.index("</main>") + len("</main>")
t = t[:a] + body + t[b:]
t = re.sub(r'<p class="note">.*?</p>', "", t, count=1, flags=re.S)
t = re.sub(r'<nav class="also".*?</nav>', "", t, count=1, flags=re.S)
t = t.replace('<a class="back" href="/odekake">関西おでかけリストを見る</a>', '<a class="back" href="/">TOWN NOTE の入口へ戻る</a>', 1)
j0 = t.index('<script>(function(){var O'); j1 = t.index("</script>", j0) + len("</script>")
SJS = ('<script>(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1";}catch(e){}'
       'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
       'c("表示：ふるさと納税"+(document.referrer&&!/townnote\\.(pages|app)/.test(document.referrer)?"（外から）":""));'
       'document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("[data-k]"):null;if(a)c("クリック："+a.getAttribute("data-k"));});'
       '})();</script>')
t = t[:j0] + SJS + t[j1:]
open(os.path.join(ROOT, "links", "furusato.html"), "w", encoding="utf-8").write(t)
for sm in ("sitemap.xml", "sitemap-all.xml"):
    p = os.path.join(ROOT, "links", sm)
    if os.path.exists(p):
        x = open(p, encoding="utf-8").read()
        if f"<loc>{url}</loc>" not in x:
            open(p, "w", encoding="utf-8").write(x.replace("</urlset>", f"<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url></urlset>", 1))
print("furusato", N, "品")
