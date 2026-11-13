"""関東の市区ごとの「解体の補助金」ページ（akari-auto site/kaitai-<市区>.html）を作る。11/11 月（関西の city.py と同じ型。物差しは入口の数）。
元は tools/kaitai/kanto_hojo.tsv（月が公式ページで確かめた行だけ）と、to_life.py が作った akari-auto/site/kaitai.html。
市区を足す時：kanto_hojo.tsv に行を足し、下の SLUG に（ローマ字・都県）を足す。
使い方：python3 tools/kaitai/to_life.py ../akari-auto のあとに  python3 tools/kaitai/city_life.py ../akari-auto"""
import html, json, os, re, sys
from urllib.parse import quote
def cut(tx, n=88):
    """説明文に入れる時、文の途中で切らない（関西の city.py と同じ）。"""
    if len(tx) <= n: return tx
    t = tx[:n]; i = t.rfind("。")
    if i < 30: i = t.rfind("）")
    return t[:i + 1] if i >= 30 else t.rstrip("、・（(") + "…"

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
AK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "akari-auto")
BASE = "https://lifenote-kanto.pages.dev/"; E = html.escape
SLUG = {"横浜市": ("yokohama", "神奈川県"), "川崎市": ("kawasaki", "神奈川県"), "八王子市": ("hachioji", "東京都"), "千葉市": ("chiba", "千葉県"),
        "町田市": ("machida", "東京都"), "足立区": ("adachi", "東京都"), "葛飾区": ("katsushika", "東京都"),
        "江戸川区": ("edogawa", "東京都"), "相模原市": ("sagamihara", "神奈川県"), "船橋市": ("funabashi", "千葉県"), "横須賀市": ("yokosuka", "神奈川県"), "大田区": ("ota", "東京都"), "江東区": ("koto", "東京都"), "練馬区": ("nerima", "東京都"), "板橋区": ("itabashi", "東京都"), "川口市": ("kawaguchi", "埼玉県"), "さいたま市": ("saitama", "埼玉県"), "杉並区": ("suginami", "東京都"), "松戸市": ("matsudo", "千葉県"), "市川市": ("ichikawa", "千葉県"), "北区": ("kita", "東京都"), "品川区": ("shinagawa", "東京都"), "中野区": ("nakano", "東京都"), "墨田区": ("sumida", "東京都"), "荒川区": ("arakawa", "東京都"), "目黒区": ("meguro", "東京都"), "文京区": ("bunkyo", "東京都"), "台東区": ("taito", "東京都"), "越谷市": ("koshigaya", "埼玉県"), "新宿区": ("shinjuku", "東京都")}
END = ("受付停止", "受付終了")

FV_CSS = ('.head{padding:18px 16px 16px!important}.head img{width:44px;height:44px}.head .en{margin-top:6px}'
          '.fv{margin:12px auto 0;max-width:340px}.fv .n{display:flex;justify-content:center;align-items:baseline;gap:10px;flex-wrap:wrap}.fv .n b{font-size:34px;line-height:1.1}.fv .n b.t{font-size:20px;line-height:1.5}'
          '.fv .n b i{font-style:normal;font-size:13px;font-weight:500;margin-right:6px}.fv .n b small{font-size:16px;margin-left:2px}'
          '.fv .n span{font-size:12px;padding:3px 10px;border-radius:99px;background:#E6F2E8;color:#2F6B3F;font-weight:700}.fv .n span.x{background:#EEE;color:#777}'
          '.fv .d{font-size:12px;line-height:1.7;color:#6B6058;margin:6px 0 12px}.fv .bt{display:flex;gap:8px}.fv .bt a{flex:1;text-align:center;font-weight:700;font-size:14px;line-height:1.4;padding:13px 6px;border-radius:2px;text-decoration:none}'
          '.fv .bt a.k{background:#2B2622;color:#fff}.fv .bt a.w{border:1px solid #2B2622;color:#2B2622;background:#fff}'
          '.toc{display:flex;gap:8px;overflow-x:auto;margin:0 -16px;padding:10px 16px;background:#fff;border-top:1px solid #EEE9E4;border-bottom:1px solid #EEE9E4;white-space:nowrap;-webkit-overflow-scrolling:touch}'
          '.toc a{font-size:12.5px;padding:8px 12px;border:1px solid #D9D2CB;border-radius:99px;color:inherit;text-decoration:none;flex:none}')
TOC = (("shi", "補助の中身"), ("hiku", "自分で払う目安"), ("keisan", "30秒で計算"), ("tejun", "使う順番"), ("kaitai", "解体の費用"), ("hoka", "ほかの市区"))


def first_view(s, city, word, cap, st, ended, tx, date):
    """11/13 最初の画面に、上限・受付の状況・締め切り・ボタン2つ・目次を入れる（オーナーOK。ロゴ・英字・題・後ろの絵は残す）。"""
    E_ = html.escape
    num = (f'<b><i>{word}</i>{cap}<small>万円</small></b>' if cap else '<b class="t">広さなどで決まる額</b>')
    stt = (f'<span class="{"x" if ended else ""}">{E_(st)}</span>' if st else "")
    m = re.search(r"受付は([^（(。、]{2,22}?まで)", tx or "")
    dl = (f'受付は{E_(m.group(1))}・' if (m and not ended) else "")
    md = re.sub(r"^\d+年", "", date)
    want = quote("解体の見積り")
    b1 = "来年度に向けて見積りを頼む" if ended else "見積りを無料で頼む"
    fv = (f'<div class="fv"><div class="n">{num}{stt}</div><div class="d">{dl}市の公式ページで{md}に確認</div><div class="bt">'
          f'<a class="k" href="/moushikomi?lite=1&amp;want={want}&amp;memo={quote(city + " 最初の画面")}" data-k="見積りを相談｜最初の画面">{b1}</a>'
          '<a class="w" href="#keisan" data-k="最初の画面｜30秒で目安">30秒で目安を出す</a></div></div>')
    s, n = re.subn(r'<p class="sub">.*?</p>', lambda _m: fv, s, count=1, flags=re.S)
    assert n == 1, city
    toc = '<nav class="toc" aria-label="このページの目次">' + "".join(f'<a href="#{i}" data-k="目次｜{t}">{t}</a>' for i, t in TOC if f'<section id="{i}"' in s) + '</nav>'
    s = s.replace('<section id="shi"', toc + '<section id="shi"', 1)
    return s.replace("</head>", "<style>" + FV_CSS + "</style></head>", 1)


rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "kanto_hojo.tsv"), encoding="utf-8") if l.strip() and not l.startswith("#")]
rows = [r for r in rows if len(r) == 5 and r[0] in SLUG]
base = open(os.path.join(AK, "site", "kaitai.html"), encoding="utf-8").read()
for city, tx, st, u, d in rows:
    slug, pref = SLUG[city]; ended = st in END; s = base
    sec = (f'<section id="shi" class="ps" style="--c:#4F7BA8"><h2>{E(city)}の解体の補助</h2><p class="kt-tr"><span>公式ページで確認 {re.sub(r"^\d+年", "", d)}</span><span>受付の状況を毎週見直し</span><span>関東{len(rows)}市区を掲載</span></p>'
           f'<div class="kt-hj"><b>解体の補助</b>' + (f'<em class="{"x" if ended else ""}">{E(st)}</em>' if st else "") + f'<p>{E(tx)}</p>'
           f'<a href="{E(u)}" target="_blank" rel="noopener" data-k="市の補助｜公式ページ｜{E(city)}">{E(city)}の公式ページで確かめる</a></div>'
           '<p class="kt-n">受付・条件・上限は変わります。交付が決まる前に契約や工事を始めると、対象外になる市区が多いので、見積りの前に公式ページでご確認ください。</p></section>')
    if ended:
        sec += (f'<section id="hiku" class="ps" style="--c:#4F7BA8"><h2>今年度の受付について</h2><p class="kt-n" style="font-size:13.5px;color:inherit">{E(city)}の今年度の受付は、'
                f'{"止まっています" if st == "受付停止" else "終わっています"}。来年度の受付は、市の公式ページでご確認ください。見積りは、受付が始まる前に取っておくと、申し込みが早く進みます。</p></section>')
    steps = [("市の窓口で、対象かどうかを確かめる", "建った年・場所・所得などの条件があります。"), ("解体の見積りを取る", "申請に見積書が要る市区が多いです。2〜3社でくらべると安心です。"),
             ("市に申請して、交付の決定を待つ", "決定の前に契約や工事を始めると、対象外になります。"), ("決定のあとで、契約・工事", "工事の前後の写真が要る市区もあります。"),
             ("工事が終わったら報告して、補助を受け取る", "報告の期限があります。")]
    jun = ('<section id="tejun" class="ps" style="--c:#4F7BA8"><h2>補助を使う時の順番</h2><ol class="kt-st">' + "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in steps)
           + f'</ol><p class="kt-n">順番や書類は市区ごとに違います。{E(city)}の手続きは、上の公式ページでご確認ください。</p>'
           + f'<a class="kt-b" href="/moushikomi?lite=1&amp;want=%E8%A7%A3%E4%BD%93%E3%81%AE%E8%A6%8B%E7%A9%8D%E3%82%8A&amp;memo={quote(city + " 申請に使う見積り")}" data-k="見積りを相談｜順番の下">申請に使う見積りを、無料で頼む</a><p class="kt-n" style="text-align:center">無料・書くのは4つだけ・見積りだけでも大丈夫です</p></section>')
    oth = ('<section id="hoka" class="ps" style="--c:#4F7BA8"><h2>ほかの市区の補助</h2>'
           f'<p style="margin:0 0 12px;font-size:13.5px"><a href="/kaitai-ranking" data-k="市の補助｜補助ランキング｜{E(city)}" style="font-weight:700">上限の高い順に見る（補助金ランキング）</a></p><p class="kt-ci">'
           + "".join(f'<a href="/kaitai-{SLUG[c][0]}" data-k="市の補助｜ほかの市｜{E(c)}">{E(c)}</a>' for c, *_ in rows if c != city) + '</p></section>')
    q2 = ("いまは受付中です。締め切りと残りの予算は、市の公式ページでご確認ください。" if st == "受付中" else
          f"今年度の受付は{'止まっています' if st == '受付停止' else '終わっています'}。来年度の受付は、市の公式ページでご確認ください。" if ended else
          "受付の時期と残りの予算は、市の公式ページでご確認ください。予算に達すると、途中で終わる事があります。")
    faq = [(f"{city}の解体の補助は、いくらですか？", tx), (f"{city}の解体の補助は、いつまで申し込めますか？", q2),
           ("補助が決まる前に、解体の契約をしてもいいですか？", "多くの市区で、交付が決まる前に契約や工事を始めると対象外になります。見積りを取る所までにして、先に市へ申請してください。"),
           ("見積りだけでも頼めますか？", "はい。無料で、見積りだけでも大丈夫です。関東（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）のお家が対象です。")]
    fq = '<section class="faq"><h2>よくある質問</h2>' + "".join(f"<details><summary>{E(q)}</summary><p>{E(x)}</p></details>" for q, x in faq) + "</section>"
    a = s.index('<section id="keisan"'); k1 = s.index('<section id="kaitai"'); h1 = s.index('<section id="hojo"'); hj_end = s.index("</section>", h1) + len("</section>")
    f1 = s.index('<section class="faq">'); f2 = s.index("</section>", f1) + len("</section>")
    s = s[:a] + sec + s[a:k1] + jun + s[k1:h1] + s[hj_end:f1] + oth + fq + s[f2:]
    # 11/12 関西の題と同じく、金額を題に入れる（本文の「上限・最大◯万円」のいちばん大きい数。500万円より大きい物・見つからない物は入れない）
    _cap = max([int(x.replace(",", "")) for x in re.findall(r"(?:上限|最大)[はが]?\s*([\d,]+)万円", tx) + re.findall(r"[（(][^）)]*?は\s*([\d,]+)万円[）)]", tx) if int(x.replace(",", "")) <= 500] or [0])
    title = f"{city}の解体の補助金 2026年度｜" + (f"最大{_cap}万円・" if _cap else "") + "条件と受付の状況、費用の目安"
    desc = f"{pref}{city}の解体の補助：{cut(tx)} 木造30坪の解体は90万〜150万円が目安（全国）。市の公式ページを{d}に確認。無料の見積り相談もできます。"
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "解体・片付けの費用", "item": BASE + "kaitai"},
              {"@type": "ListItem", "position": 2, "name": f"{city}の解体の補助金", "item": BASE + "kaitai-" + slug}]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", '<style>.kt-tr{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}.kt-tr span{font-size:11.5px;padding:4px 10px;border:1px solid #A9BFD8;border-radius:99px;color:#2F5F8F;background:#F1F6FB;font-weight:700}.kt-tr span::before{content:"✓ "}.kt-big{display:flex;align-items:baseline;gap:12px;margin:2px 0 10px}.kt-big b{font-size:30px;letter-spacing:.02em;line-height:1.2}.kt-big b small{font-size:15px;margin-left:2px}.kt-big b i{font-style:normal;font-size:13px;font-weight:500;margin-right:6px}.kt-big span{font-size:12px;padding:3px 10px;border-radius:99px;background:#E6F2E8;color:#2F6B3F;font-weight:700}.kt-big span.x{background:#EEE;color:#777}.kt td a,.kt-hj>a{display:inline-block;padding:8px 0}.kt-ci{display:flex;flex-wrap:wrap;gap:8px;margin:0}.kt-ci a{font-size:13px;padding:7px 12px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:inherit;text-decoration:none}</style>'
                  + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
    for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
        s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(f"{city}の解体の補助金 2026年度"), s, count=1)
    s = s.replace(BASE + 'kaitai"', BASE + f'kaitai-{slug}"')
    s = re.sub(r"<h1>.*?</h1>", f"<h1>{E(city)}の解体の補助金<span>いくら出るか・条件・受付の状況</span></h1>", s, count=1, flags=re.S)
    s = re.sub(r'<p class="sub">.*?</p>', f'<p class="sub">{pref}{E(city)}の、家の解体に使える補助を、<br>市の公式ページで確かめてまとめました。</p>', s, count=1, flags=re.S)
    s = first_view(s, city, "最大", _cap, st, ended, tx, d)
    n1 = s.count('c("表示：解体・片付けの費用"+'); s = s.replace('c("表示：解体・片付けの費用"+', f'c("表示：市の解体補助 {city}"+', 1).replace('c("クリック：解体・片付けの費用｜"+', f'c("クリック：市の解体補助｜{city}｜"+', 1)
    s = s.replace('"&memo="+encodeURIComponent(l+" "+v)', f'"&memo="+encodeURIComponent("{city} "+l+" "+v)', 1)
    assert n1 == 1 and 'id="hojo"' not in s, city
    open(os.path.join(AK, "site", f"kaitai-{slug}.html"), "w", encoding="utf-8").write(s)
    print("作った", f"site/kaitai-{slug}.html")
# 費用ページの補助の段から、市区ごとのページへ道を付ける
k = base
for city, *_ in rows:
    k = k.replace(f'<div class="kt-hj"><b>{E(city)}</b>', f'<div class="kt-hj"><b><a href="/kaitai-{SLUG[city][0]}" data-k="費用｜市ごとのページ｜{E(city)}" style="color:inherit">{E(city)}</a></b>', 1)
open(os.path.join(AK, "site", "kaitai.html"), "w", encoding="utf-8").write(k)
# 11/12 月：関東の「解体の補助金 上限ランキング」（関西の city.py ranking と同じ型。金額は本文の「上限・最大◯万円」のいちばん大きい数）

def rank_view(s, name, cap, n, word, unit):
    """11/13 ランキングの最初の画面：1位と数、ボタン2つ、目次（市のページと同じ形）。"""
    fv = (f'<div class="fv"><div class="n"><b class="t"><i>1位</i>{html.escape(name)}　{word}{cap}<small>万円</small></b></div>'
          f'<div class="d">{n}{unit}を、公式ページで確かめた額の高い順にならべました</div><div class="bt">'
          '<a class="k" href="#rank" data-k="最初の画面｜ランキングを見る">ランキングを見る</a><a class="w" href="#keisan" data-k="最初の画面｜30秒で目安">30秒で目安を出す</a></div></div>')
    s, k = re.subn(r'<p class="sub">.*?</p>', lambda _m: fv, s, count=1, flags=re.S)
    assert k == 1
    toc = '<nav class="toc" aria-label="このページの目次">' + "".join(f'<a href="#{i}" data-k="目次｜{t}">{t}</a>' for i, t in (("rank", "ランキング"), ("keisan", "30秒で計算"), ("kaitai", "解体の費用"), ("hojo", "補助の中身"), ("katazuke", "片付けの費用"), ("junban", "順番")) if f'<section id="{i}"' in s) + '</nav>'
    s = s.replace('<section id="rank"', toc + '<section id="rank"', 1)
    return s.replace("</head>", "<style>" + FV_CSS + "</style></head>", 1)

def _capof(tx):
    return max([int(x.replace(",", "")) for x in re.findall(r"(?:上限|最大)[はが]?\s*([\d,]+)万円", tx) + re.findall(r"[（(][^）)]*?は\s*([\d,]+)万円[）)]", tx) if int(x.replace(",", "")) <= 500] or [0])
items = sorted([(_capof(tx), city, SLUG[city][0], SLUG[city][1], st) for city, tx, st, u, d in rows if _capof(tx)], key=lambda x: (-x[0], x[1]))
if len(items) >= 5:
    tr = ""; rank = 0; prev = None
    for i, (cap, c, slug, pref, st) in enumerate(items, 1):
        if cap != prev: rank = i; prev = cap
        tr += (f'<tr data-p="{pref}"><th>{rank}位</th><td><a href="/kaitai-{slug}" data-k="補助ランキング｜{E(c)}">{E(c)}</a><small style="display:block;font-size:11px;color:#8A7F76">{pref}'
               + (f'・{st}' if st in END else "") + f'</small></td><td><b>最大{cap}万円</b></td></tr>')
    top = items[0]; s = k
    sec = (f'<section id="rank" class="ps" style="--c:#4F7BA8"><h2>解体の補助金 上限ランキング（関東 {len(items)}市区）</h2><p class="rk-sub">市区の公式ページで確かめた、いちばん多く出る場合の額・高い順</p>'
           '<div class="kt-f"><button type="button" class="on" data-p="">すべて</button>' + "".join(f'<button type="button" data-p="{q}">{q[:-1]}</button>' for q in dict.fromkeys(x[3] for x in items)) + '</div>'
           '<div class="kt-w"><table class="kt"><thead><tr><th>順位</th><th>市区</th><th>上限</th></tr></thead><tbody>' + tr + '</tbody></table></div>'
           '<p class="kt-n">額は、いちばん多く出る場合です。建った年・場所（地区）・所得などの条件で変わり、対象の地区が決まっている市区もあります。名前を押すと、条件と受付の状況、公式ページへ進めます。'
           '載っていない市区は、公式ページで確かめられた順に足しています。</p></section>')
    a = s.index('<section id="keisan"'); s = s[:a] + sec + s[a:]
    title = f"解体の補助金 上限ランキング 関東{len(items)}市区｜1位は{top[1]}の最大{top[0]}万円【2026年度】"
    desc = f"東京・神奈川・埼玉・千葉の{len(items)}市区の、家の解体に使える補助金の上限額を高い順にまとめました。1位は{top[1]}の最大{top[0]}万円。市区の公式ページで確かめた額だけを載せています。"
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "関東の解体補助金 上限ランキング", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": f"{c} 最大{cap}万円", "url": BASE + "kaitai-" + slug} for i, (cap, c, slug, pref, st) in enumerate(items, 1)]}
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>', 1)
    s = s.replace("</head>", '<style>.kt-f{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}.kt-f button{font:inherit;font-size:13px;padding:8px 14px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:inherit;cursor:pointer}.kt-f button.on{background:#2B2622;color:#fff;border-color:#2B2622}.kt td a{display:inline-block;padding:9px 0;font-weight:700}</style><script>document.addEventListener("DOMContentLoaded",function(){var f=document.querySelector(".kt-f");if(!f)return;f.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var p=b.getAttribute("data-p");[].forEach.call(f.querySelectorAll("button"),function(x){x.classList.toggle("on",x===b)});[].forEach.call(document.querySelectorAll("#rank tbody tr"),function(r){r.style.display=(!p||r.getAttribute("data-p")===p)?"":"none"})})});</script></head>', 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
    for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
        s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(f"解体の補助金 上限ランキング 関東{len(items)}市区"), s, count=1)
    s = s.replace(BASE + 'kaitai"', BASE + 'kaitai-ranking"')
    s = re.sub(r"<h1>.*?</h1>", "<h1>解体の補助金 上限ランキング<span>関東の市区ごとに、いくらまで出るか</span></h1>", s, count=1, flags=re.S)
    s = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">家の解体に使える補助の上限を、<br>市区の公式ページで確かめて、高い順にならべました。</p>', s, count=1, flags=re.S)
    s = s.replace('c("表示：解体・片付けの費用"+', 'c("表示：解体補助ランキング"+', 1).replace('c("クリック：解体・片付けの費用｜"+', 'c("クリック：解体補助ランキング｜"+', 1)
    assert s.count("<h1>") == 1
    s = rank_view(s, top[1], top[0], len(items), "最大", "市区")
    open(os.path.join(AK, "site", "kaitai-ranking.html"), "w", encoding="utf-8").write(s)
    # 費用ページから入れる道
    k2 = open(os.path.join(AK, "site", "kaitai.html"), encoding="utf-8").read(); h = k2.find('<section id="hojo"')
    if "/kaitai-ranking" not in k2 and h >= 0:
        e = k2.index("</h2>", h) + 5
        k2 = k2[:e] + '<p style="margin:0 0 12px"><a href="/kaitai-ranking" data-k="費用｜補助ランキング" style="font-weight:700">上限の高い順に見る（補助金ランキング）</a></p>' + k2[e:]
        open(os.path.join(AK, "site", "kaitai.html"), "w", encoding="utf-8").write(k2)
    print("作った site/kaitai-ranking.html", len(items), "市区", top[1], top[0])
