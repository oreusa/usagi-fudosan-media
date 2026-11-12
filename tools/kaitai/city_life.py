"""関東の市区ごとの「解体の補助金」ページ（akari-auto site/kaitai-<市区>.html）を作る。11/11 月（関西の city.py と同じ型。物差しは入口の数）。
元は tools/kaitai/kanto_hojo.tsv（月が公式ページで確かめた行だけ）と、to_life.py が作った akari-auto/site/kaitai.html。
市区を足す時：kanto_hojo.tsv に行を足し、下の SLUG に（ローマ字・都県）を足す。
使い方：python3 tools/kaitai/to_life.py ../akari-auto のあとに  python3 tools/kaitai/city_life.py ../akari-auto"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
AK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "akari-auto")
BASE = "https://lifenote-kanto.pages.dev/"; E = html.escape
SLUG = {"横浜市": ("yokohama", "神奈川県"), "川崎市": ("kawasaki", "神奈川県"), "八王子市": ("hachioji", "東京都"), "千葉市": ("chiba", "千葉県"),
        "町田市": ("machida", "東京都"), "足立区": ("adachi", "東京都"), "葛飾区": ("katsushika", "東京都"),
        "江戸川区": ("edogawa", "東京都"), "相模原市": ("sagamihara", "神奈川県"), "船橋市": ("funabashi", "千葉県"), "横須賀市": ("yokosuka", "神奈川県"), "大田区": ("ota", "東京都"), "江東区": ("koto", "東京都"), "練馬区": ("nerima", "東京都")}
END = ("受付停止", "受付終了")
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "kanto_hojo.tsv"), encoding="utf-8") if l.strip() and not l.startswith("#")]
rows = [r for r in rows if len(r) == 5 and r[0] in SLUG]
base = open(os.path.join(AK, "site", "kaitai.html"), encoding="utf-8").read()
for city, tx, st, u, d in rows:
    slug, pref = SLUG[city]; ended = st in END; s = base
    sec = (f'<section id="shi" class="ps" style="--c:#4F7BA8"><h2>{E(city)}の解体の補助</h2><p class="rk-sub">市の公式ページを {E(d)} に確かめました</p>'
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
           + f'</ol><p class="kt-n">順番や書類は市区ごとに違います。{E(city)}の手続きは、上の公式ページでご確認ください。</p></section>')
    oth = ('<section id="hoka" class="ps" style="--c:#4F7BA8"><h2>ほかの市区の補助</h2><p class="kt-ci">'
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
    title = f"{city}の解体の補助金 2026年度｜条件と受付の状況、費用の目安"
    desc = f"{pref}{city}の解体の補助：{tx[:88]} 木造30坪の解体は90万〜150万円が目安（全国）。市の公式ページを{d}に確認。無料の見積り相談もできます。"
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "解体・片付けの費用", "item": BASE + "kaitai"},
              {"@type": "ListItem", "position": 2, "name": f"{city}の解体の補助金", "item": BASE + "kaitai-" + slug}]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", '<style>.kt-ci{display:flex;flex-wrap:wrap;gap:8px;margin:0}.kt-ci a{font-size:13px;padding:7px 12px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:inherit;text-decoration:none}</style>'
                  + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
    for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
        s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(f"{city}の解体の補助金 2026年度"), s, count=1)
    s = s.replace(BASE + 'kaitai"', BASE + f'kaitai-{slug}"')
    s = re.sub(r"<h1>.*?</h1>", f"<h1>{E(city)}の解体の補助金<span>いくら出るか・条件・受付の状況</span></h1>", s, count=1, flags=re.S)
    s = re.sub(r'<p class="sub">.*?</p>', f'<p class="sub">{pref}{E(city)}の、家の解体に使える補助を、<br>市の公式ページで確かめてまとめました。</p>', s, count=1, flags=re.S)
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
