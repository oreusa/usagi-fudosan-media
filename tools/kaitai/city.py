"""市ごとの「解体の補助金」ページ（links/kaitai-<市>.html）を作る。11/11 月（オーナー「全て作り替えてくれ」。物差しは500万円＝入口の数）。
「◯◯市 解体 補助金」で探す人の入口。中身は、公式ページで確かめた市の補助（正本は tools/fudosan_list/towns.py の J_CITY）＋
補助を引いた目安＋費用の計算＋無料の見積り相談。形は /kaitai（build.py が先に作る）を借りる。
市を足す時：J_CITY に公式で確かめた行を足し、下の CITY に（ローマ字・府県・上限の万円・割合）を足す。
使い方: python3 tools/kaitai/city.py 2026-11-11   （build.py のあとに動かす）"""
import ast, datetime, html, json, os, re, sys
from fractions import Fraction
from urllib.parse import quote

TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
BASE = "https://townnote.pages.dev/"
E = html.escape
# 市：(ローマ字, 府県, 上限の万円（表を出さない市は None）, 割合（定額・上限だけの市は None）)
CITY = {
    "寝屋川市": ("neyagawa", "大阪府", 50, "4/5"), "大東市": ("daito", "大阪府", 80, "4/5"), "堺市": ("sakai", "大阪府", None, None),
    "大阪市": ("osaka", "大阪府", 70, "1/3"), "東大阪市": ("higashiosaka", "大阪府", 50, None), "神戸市": ("kobe", "兵庫県", None, None),
    "奈良市": ("nara", "奈良県", 30, "1/2"), "姫路市": ("himeji", "兵庫県", 50, "1/3"), "尼崎市": ("amagasaki", "兵庫県", 50, "2/3"),
    "和歌山市": ("wakayama", "和歌山県", 50, "2/3"), "豊中市": ("toyonaka", "大阪府", 40, None), "高槻市": ("takatsuki", "大阪府", 40, None),
    "枚方市": ("hirakata", "大阪府", 20, None), "八尾市": ("yao", "大阪府", 40, None), "加古川市": ("kakogawa", "兵庫県", 25, "1/5"),
    "宇治市": ("uji", "京都府", 30, "1/3"), "橿原市": ("kashihara", "奈良県", 50, "4/5"),
    "和泉市": ("izumi", "大阪府", 20, "4/5"),
    "茨木市": ("ibaraki", "大阪府", 40, None), "岸和田市": ("kishiwada", "大阪府", None, None), "富田林市": ("tondabayashi", "大阪府", 30, None), "松原市": ("matsubara", "大阪府", 40, None), "伊丹市": ("itami", "兵庫県", 60, None), "草津市": ("kusatsu", "滋賀県", 50, "4/5"), "生駒市": ("ikoma", "奈良県", 50, None), "河内長野市": ("kawachinagano", "大阪府", 25, "1/2"), "泉佐野市": ("izumisano", "大阪府", 130, None), "羽曳野市": ("habikino", "大阪府", 20, "1/2"), "摂津市": ("settsu", "大阪府", 40, None),
}
END = ("受付停止", "受付終了")


def load():
    t = open(os.path.join(ROOT, "tools", "fudosan_list", "towns.py"), encoding="utf-8").read()
    a = t.index("J_CITY = ["); J = ast.literal_eval(t[a + 9:t.index("\n]\n", a) + 2])
    ns = {}; exec(re.search(r"^J_DATE = .*$", t, re.M).group(0), ns)
    return J, ns["J_DATE"]


def cut(tx, n=88):
    """説明文に入れる時、文の途中で切らない（11/12 関東の説明が途中で切れていた）。"""
    if len(tx) <= n: return tx
    t = tx[:n]; i = t.rfind("。")
    if i < 30: i = t.rfind("）")
    return t[:i + 1] if i >= 30 else t.rstrip("、・（(") + "…"


def man(v):
    v = round(v)
    return f"{v}万円"


def page(base, city, rows, date, others):
    slug, pref, cap, ratio = CITY[city]
    kai = [r for r in rows if "解体" in r[0]]; etc = [r for r in rows if "解体" not in r[0]]
    h0, tx0, st0, u0 = kai[0]
    ended = st0 in END
    s = base
    card = lambda h, tx, st, u: (f'<div class="kt-hj"><b>{E(h)}</b>' + (f'<em class="{"x" if st in END else ""}">{st}</em>' if st else "") + f'<p>{E(tx)}</p>'
                                 f'<a href="{E(u)}" target="_blank" rel="noopener" data-k="市の補助｜公式ページ｜{E(city)}">{E(city)}の公式ページで確かめる</a></div>')
    sec = (f'<section id="shi" class="ps" style="--c:#4F7BA8"><h2>{E(city)}の解体の補助</h2><p class="kt-tr"><span>公式ページで確認 {re.sub(r"^\d+年", "", date)}</span><span>受付の状況を毎週見直し</span><span>関西{len(others)}市を掲載</span></p>'
           + "".join(card(*r) for r in kai)
           + ('<h3 class="kt-h">ほかの制度</h3>' + "".join(card(*r) for r in etc) if etc else "")
           + '<p class="kt-n">受付・条件・上限は変わります。交付が決まる前に契約や工事を始めると、対象外になる市が多いので、見積りの前に公式ページでご確認ください。</p></section>')
    if cap and not ended:
        fr = Fraction(ratio) if ratio else None
        tr = ""
        for t in (20, 30, 40):
            lo, hi = 3 * t, 5 * t
            sl, sh = (min(cap, lo * fr), min(cap, hi * fr)) if fr else (min(cap, lo), min(cap, hi))
            sub = man(sl) if round(sl) == round(sh) else f"{round(sl)}万〜{man(sh)}"
            tr += f"<tr><th>{t}坪<small>解体 {lo}万〜{hi}万円</small></th><td>{sub}</td><td><b>{round(lo - sl)}万〜{man(hi - sh)}</b></td></tr>"
        how = (f"補助は「費用の{ratio}・上限{cap}万円」で計算しています。" if ratio else f"補助は「上限{cap}万円」で計算しています。")
        sec += (f'<section id="hiku" class="ps" style="--c:#4F7BA8"><h2>補助が出た時の目安</h2><p class="rk-sub">木造の家・条件に合った時</p>'
                '<div class="kt-w"><table class="kt"><thead><tr><th>広さ</th><th>補助の目安</th><th>自分で払う目安</th></tr></thead><tbody>' + tr + '</tbody></table></div>'
                f'<p class="kt-n">{how}解体の目安は全国の相場（木造1坪3万〜5万円）です。対象になるか・いくら出るかは、市の審査で決まります。</p></section>')
    elif ended:
        sec += (f'<section id="hiku" class="ps" style="--c:#4F7BA8"><h2>今年度の受付について</h2><p class="kt-n" style="font-size:13.5px;color:inherit">{E(city)}の今年度の受付は、'
                f'{"止まっています" if st0 == "受付停止" else "終わっています"}。来年度の受付は、市の公式ページでご確認ください。見積りは、受付が始まる前に取っておくと、申し込みが早く進みます。</p></section>')
    steps = [("市の窓口で、対象かどうかを確かめる", "建った年・空き家の期間・所得などの条件があります。"), ("解体の見積りを取る", "申請に見積書が要る市が多いです。2〜3社でくらべると安心です。"),
             ("市に申請して、交付の決定を待つ", "決定の前に契約や工事を始めると、対象外になります。"), ("決定のあとで、契約・工事", "工事の前後の写真が要る市もあります。"),
             ("工事が終わったら報告して、補助を受け取る", "報告の期限があります。")]
    jun = ('<section id="tejun" class="ps" style="--c:#4F7BA8"><h2>補助を使う時の順番</h2><ol class="kt-st">' + "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in steps)
           + f'</ol><p class="kt-n">順番や書類は市ごとに違います。{E(city)}の手続きは、上の公式ページでご確認ください。</p>'
           + f'<a class="kt-b" href="/moushikomi?lite=1&amp;want=%E8%A7%A3%E4%BD%93%E3%81%AE%E8%A6%8B%E7%A9%8D%E3%82%8A&amp;memo={quote(city + " 申請に使う見積り")}" data-k="見積りを相談｜順番の下">申請に使う見積りを、無料で頼む</a><p class="kt-n" style="text-align:center">無料・書くのは4つだけ・見積りだけでも大丈夫です</p></section>')
    same = [c for c in others if CITY[c][1] == pref and c != city]; rest = [c for c in others if CITY[c][1] != pref]
    _rk = sorted([CITY[c][2] for c in others if CITY[c][2]], reverse=True)
    _pos = (f'{E(city)}の上限{cap}万円は、関西{len(_rk)}市の中で{_rk.index(cap) + 1}位です。' if cap else '')
    oth = ('<section id="hoka" class="ps" style="--c:#4F7BA8"><h2>ほかの市の補助</h2>'
           f'<p style="margin:0 0 12px;font-size:13.5px">{_pos}<a href="/kaitai-ranking" data-k="市の補助｜補助ランキング｜{E(city)}" style="font-weight:700">上限の高い順に見る（補助金ランキング）</a></p><p class="kt-ci">'
           + "".join(f'<a href="/kaitai-{CITY[c][0]}" data-k="市の補助｜ほかの市｜{E(c)}">{E(c)}</a>' for c in same + rest) + '</p></section>')
    a = s.index('<section id="keisan"'); k1 = s.index('<section id="kaitai"'); h1 = s.index('<section id="hojo"')
    f1 = s.index('<section class="faq">'); f2 = s.index("</section>", f1) + len("</section>")
    hj_end = s.index("</section>", h1) + len("</section>")
    while s[hj_end:hj_end + 11] == "<!--/hojo-->": hj_end += 11
    q2 = ("いまは受付中です。締め切りと残りの予算は、市の公式ページでご確認ください。" if st0 == "受付中" else
          f"今年度の受付は{'止まっています' if st0 == '受付停止' else '終わっています'}。来年度の受付は、市の公式ページでご確認ください。" if ended else
          "受付の時期と残りの予算は、市の公式ページでご確認ください。予算に達すると、途中で終わる事があります。")
    faq = [(f"{city}の解体の補助は、いくらですか？", f"{h0}：{tx0}"), (f"{city}の解体の補助は、いつまで申し込めますか？", q2),
           ("補助が決まる前に、解体の契約をしてもいいですか？", "多くの市で、交付が決まる前に契約や工事を始めると対象外になります。見積りを取る所までにして、先に市へ申請してください。"),
           ("見積りだけでも頼めますか？", "はい。無料で、見積りだけでも大丈夫です。関西（大阪・京都・兵庫・奈良・滋賀・和歌山）のお家が対象です。")]
    fq = '<section class="faq"><h2>よくある質問</h2>' + "".join(f"<details><summary>{E(q)}</summary><p>{E(x)}</p></details>" for q, x in faq) + "</section>"
    s = s[:a] + sec + s[a:k1] + jun + s[k1:h1].replace("<!--hojo-->", "") + oth + fq + s[f2:]
    title = f"{city}の解体の補助金 2026年度｜" + (f"上限{cap}万円・" if cap else "") + "条件と受付の状況、費用の目安"
    desc = f"{pref}{city}の{h0}：{cut(tx0)} 木造30坪の解体は90万〜150万円が目安（全国）。市の公式ページを{date}に確認。無料の見積り相談もできます。"
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in faq]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "関西不動産リスト", "item": BASE + "fudosan-list"},
              {"@type": "ListItem", "position": 2, "name": "解体・片付けの費用", "item": BASE + "kaitai"},
              {"@type": "ListItem", "position": 3, "name": f"{city}の解体の補助金", "item": BASE + "kaitai-" + slug}]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", '<style>.kt-tr{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}.kt-tr span{font-size:11.5px;padding:4px 10px;border:1px solid #A9BFD8;border-radius:99px;color:#2F5F8F;background:#F1F6FB;font-weight:700}.kt-tr span::before{content:"✓ "}.kt-big{display:flex;align-items:baseline;gap:12px;margin:2px 0 10px}.kt-big b{font-size:30px;letter-spacing:.02em;line-height:1.2}.kt-big b small{font-size:15px;margin-left:2px}.kt-big b i{font-style:normal;font-size:13px;font-weight:500;margin-right:6px}.kt-big span{font-size:12px;padding:3px 10px;border-radius:99px;background:#E6F2E8;color:#2F6B3F;font-weight:700}.kt-big span.x{background:#EEE;color:#777}.kt td a,.kt-hj>a{display:inline-block;padding:8px 0}.kt-ci{display:flex;flex-wrap:wrap;gap:8px;margin:0}.kt-ci a{font-size:13px;padding:7px 12px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:inherit;text-decoration:none}.kt th small{display:block;font-weight:500;font-size:11px;color:#8A7F76;white-space:nowrap;margin-top:2px}</style>'
                  + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
    # 11/12 最初の画面で、いちばん知りたい数字（上限・受付の状況）を大きく見せる
    if cap:
        s = re.sub(r'(<section id="shi"[^>]*><h2>[^<]*</h2>)', lambda m: m.group(1) + f'<p class="kt-big"><b><i>上限</i>{cap}<small>万円</small></b>' + (f'<span class="{"x" if st0 in END else ""}">{st0}</span>' if st0 else "") + '</p>', s, count=1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
    for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
        s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(f"{city}の解体の補助金 2026年度"), s, count=1)
    s = s.replace(BASE + 'kaitai"', BASE + f'kaitai-{slug}"')
    s = re.sub(r"<h1>.*?</h1>", f"<h1>{E(city)}の解体の補助金<span>いくら出るか・条件・受付の状況</span></h1>", s, count=1, flags=re.S)
    s = re.sub(r'<p class="sub">.*?</p>', f'<p class="sub">{pref}{E(city)}の、家の解体に使える補助を、<br>市の公式ページで確かめてまとめました。</p>', s, count=1, flags=re.S)
    s = re.sub(r'<nav class="also".*?</nav>', '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/kaitai" data-k="あわせて：解体・片付けの費用">解体・片付けの費用（関西）</a>'
               + (f'<a href="/machi/{MID[city]}" data-k="あわせて：この市の地価｜{E(city)}">{E(city)}の地価・土地の相場</a><a href="/jikka/{MID[city]}" data-k="あわせて：この市の実家ノート｜{E(city)}">{E(city)}の実家・空き家（売れた相場）</a>' if city in MID and os.path.exists(os.path.join(ROOT, "links", "jikka", MID[city] + ".html")) else (f'<a href="/machi/{MID[city]}" data-k="あわせて：この市の地価｜{E(city)}">{E(city)}の地価・土地の相場</a>' if city in MID else ""))
               + '<a href="/jikka/" data-k="あわせて：実家・空き家ノート">実家・空き家ノート</a><a href="/uru" data-k="あわせて：家を売りたい">家を売りたい</a></nav>', s, count=1, flags=re.S)
    s = s.replace('c("表示：解体・片付けの費用"+', f'c("表示：市の解体補助 {city}"+', 1).replace('c("クリック：解体・片付けの費用｜"+', f'c("クリック：市の解体補助｜{city}｜"+', 1)
    s = s.replace('"&memo="+encodeURIComponent(l+" "+v)', f'"&memo="+encodeURIComponent("{city} "+l+" "+v)', 1)
    for bad in ('id="hojo"', 'id="katazuke"x'):
        assert bad not in s, bad
    assert s.count("<h1>") == 1 and f"kaitai-{slug}" in s
    return s


def ranking(base, have, J, J_DATE):
    """/kaitai-ranking：関西の市ごとの解体補助の上限を、高い順に1枚で（11/12 月。当たり型＝地元の順位＋数字 を、お金のページへつなぐ）。"""
    rows = dict(J); s = base
    items = []
    for c in have:
        slug, pref, cap, ratio = CITY[c]
        if not cap: continue
        st = [r for r in rows[c] if "解体" in r[0]][0][2]
        items.append((cap, c, slug, pref, ratio, st))
    items.sort(key=lambda x: (-x[0], x[1]))
    tr = ""; rank = 0; prev = None
    for i, (cap, c, slug, pref, ratio, st) in enumerate(items, 1):
        if cap != prev: rank = i; prev = cap
        tr += (f'<tr data-p="{pref}"><th>{rank}位</th><td><a href="/kaitai-{slug}" data-k="補助ランキング｜{E(c)}">{E(c)}</a><small style="display:block;font-size:11px;color:#8A7F76">{pref}'
               + (f'・{st}' if st in END else "") + f'</small></td><td><b>{cap}万円</b>' + (f'<small style="display:block;font-size:11px;color:#8A7F76">費用の{ratio}まで</small>' if ratio else "") + '</td></tr>')
    top = items[0]
    sec = (f'<section id="rank" class="ps" style="--c:#4F7BA8"><h2>解体の補助金 上限ランキング（関西 {len(items)}市）</h2><p class="rk-sub">市の公式ページで確かめた上限額・高い順</p>'
           '<div class="kt-f"><button type="button" class="on" data-p="">すべて</button>' + "".join(f'<button type="button" data-p="{q}">{q[:-1]}</button>' for q in dict.fromkeys(x[3] for x in items)) + '</div>'
           '<div class="kt-w"><table class="kt"><thead><tr><th>順位</th><th>市</th><th>上限</th></tr></thead><tbody>' + tr + '</tbody></table></div>'
           '<p class="kt-n">上限は、いちばん多く出る場合の額です。建った年・空き家の期間・所得・場所などの条件で変わります。市の名前を押すと、条件と受付の状況、公式ページへ進めます。'
           '載っていない市は、公式ページで確かめられた順に足しています。</p>'
           + (lambda nc: ('<p class="kt-n">上限が1つの額で決まらない市（広さなどで変わる）：' + "・".join(f'<a href="/kaitai-{CITY[c][0]}" data-k="補助ランキング｜{E(c)}">{E(c)}</a>' for c in nc) + '。額は市のページでご確認ください。</p>') if nc else "")([c for c in have if not CITY[c][2]])
           + '</section>')
    a = s.index('<section id="keisan"')
    s = s[:a] + sec + s[a:]
    title = f"解体の補助金 上限ランキング 関西{len(items)}市｜1位は{top[1]}の{top[0]}万円【2026年度】"
    desc = f"大阪・兵庫・京都・奈良・滋賀・和歌山の{len(items)}市の、家の解体に使える補助金の上限額を高い順にまとめました。1位は{top[1]}の上限{top[0]}万円。市の公式ページで確かめた額だけを載せています。"
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関西の解体補助金 上限ランキング", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": f"{c} 上限{cap}万円", "url": BASE + "kaitai-" + slug} for i, (cap, c, slug, pref, ratio, st) in enumerate(items, 1)]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
    s = s.replace("</head>", '<style>.kt-f{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}.kt-f button{font:inherit;font-size:13px;padding:8px 14px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:inherit;cursor:pointer}.kt-f button.on{background:#2B2622;color:#fff;border-color:#2B2622}.kt td a{display:inline-block;padding:9px 0;font-weight:700}</style><script>document.addEventListener("DOMContentLoaded",function(){var f=document.querySelector(".kt-f");if(!f)return;f.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var p=b.getAttribute("data-p");[].forEach.call(f.querySelectorAll("button"),function(x){x.classList.toggle("on",x===b)});[].forEach.call(document.querySelectorAll("#rank tbody tr"),function(r){r.style.display=(!p||r.getAttribute("data-p")===p)?"":"none"})})});</script></head>', 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
    for prop in ('<meta name="description" content="', '<meta property="og:description" content="'):
        s = re.sub("(" + re.escape(prop) + ')[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(f"解体の補助金 上限ランキング 関西{len(items)}市"), s, count=1)
    s = s.replace(BASE + 'kaitai"', BASE + 'kaitai-ranking"')
    s = re.sub(r"<h1>.*?</h1>", "<h1>解体の補助金 上限ランキング<span>関西の市ごとに、いくらまで出るか</span></h1>", s, count=1, flags=re.S)
    s = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">家の解体に使える補助の上限を、<br>市の公式ページで確かめて、高い順にならべました。</p>', s, count=1, flags=re.S)
    s = s.replace('c("表示：解体・片付けの費用"+', 'c("表示：解体補助ランキング"+', 1).replace('c("クリック：解体・片付けの費用｜"+', 'c("クリック：解体補助ランキング｜"+', 1)
    assert s.count("<h1>") == 1 and "kaitai-ranking" in s
    return s, len(items), top


# 11/12 作り替え：市の補助ページ → 同じ市の街ページ・実家ページへの道（中のリンクを同じ市でつなぐ）。街ページの題から 市の名前 → id を作る
MID = {}
for _f in sorted(os.listdir(os.path.join(ROOT, "links", "machi"))):
    _m = re.search(r"<title>(.+?)の地価", open(os.path.join(ROOT, "links", "machi", _f), encoding="utf-8").read(3000))
    if _m: MID.setdefault(_m.group(1), _f[:-5])
def main():
    J, J_DATE = load()
    base = open(os.path.join(ROOT, "links", "kaitai.html"), encoding="utf-8").read()
    have = [c for c, rows in J if c in CITY and any("解体" in r[0] for r in rows)]
    miss = [c for c, rows in J if c not in CITY and any("解体" in r[0] for r in rows)]
    assert not miss, f"CITY に無い市: {miss}"
    for c, rows in J:
        if c in have:
            open(os.path.join(ROOT, "links", f"kaitai-{CITY[c][0]}.html"), "w", encoding="utf-8").write(page(base, c, rows, J_DATE.get(c, "2026年11月10日"), have))
    rk, n, top = ranking(base, have, J, J_DATE)
    open(os.path.join(ROOT, "links", "kaitai-ranking.html"), "w", encoding="utf-8").write(rk)
    # /kaitai の「解体の補助がある市」に、市ごとのページへの道を足す
    row = ('<style>.kt-ci{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}.kt-ci a{font-size:13px;padding:7px 12px;border:1px solid #D9D2CB;border-radius:99px;background:#fff;color:inherit;text-decoration:none}</style>'
           '<p class="kt-ci">' + "".join(f'<a href="/kaitai-{CITY[c][0]}" data-k="費用｜市ごとのページ｜{E(c)}">{E(c)}</a>' for c in have) + "</p>")
    k = '<p class="rk-sub">公式ページで確かめられた市だけ・順に足します</p>'
    if k in base and 'class="kt-ci"' not in base:
        open(os.path.join(ROOT, "links", "kaitai.html"), "w", encoding="utf-8").write(base.replace(k, k + row, 1))
    b2 = open(os.path.join(ROOT, "links", "kaitai.html"), encoding="utf-8").read()
    if "/kaitai-ranking" not in b2 and '<p class="kt-ci">' in b2:
        open(os.path.join(ROOT, "links", "kaitai.html"), "w", encoding="utf-8").write(b2.replace('<p class="kt-ci">', '<p style="margin:0 0 12px"><a href="/kaitai-ranking" data-k="費用｜補助ランキング" style="font-weight:700">上限の高い順に見る（補助金ランキング）</a></p><p class="kt-ci">', 1))
    # サイトマップ
    p = os.path.join(ROOT, "links", "sitemap.xml"); sm = open(p, encoding="utf-8").read()
    for loc in [f"{BASE}kaitai-{CITY[c][0]}" for c in have] + [BASE + "kaitai-ranking"]:
        if f"<loc>{loc}</loc>" not in sm:
            sm = sm.replace("</urlset>", f"<url><loc>{loc}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n</urlset>")
    open(p, "w", encoding="utf-8").write(sm)
    print("kaitai city", len(have), "市")


if __name__ == "__main__":
    main()
