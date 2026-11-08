"""府県ごとのおでかけリスト（/odekake-osaka など6ページ）を links/index.html から作る。
11/4 オーナー「Google 検索何とか上がりそう？」→ 「大阪 イベント 今週末」のような府県の検索に合わせたページ。
中身はおでかけリストと同じ（その府県のカードだけ残す）。毎朝 link-stats.yml で odekake_ld.py のあとに作り直す。
python3 tools/odekake_pref.py [YYYY-MM-DD]"""
import re, json, html, sys, datetime
SRC = "links/index.html"
TODAY = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
PREFS = [("大阪", "osaka", "大阪府"), ("京都", "kyoto", "京都府"), ("兵庫", "hyogo", "兵庫県"),
         ("奈良", "nara", "奈良県"), ("滋賀", "shiga", "滋賀県"), ("和歌山", "wakayama", "和歌山県")]
s = open(SRC, encoding="utf-8").read()
d = datetime.date.fromisoformat(TODAY)
upd = f"{d.year}年{d.month}月{d.day}日更新"
CARD = re.compile(r'<a class="card"[^>]*>.*?</a>\n?', re.S)


def name(c):
    t = re.search(r'class="t">(.*?)</div>', c, re.S)
    return html.unescape(re.sub("<[^>]+>", "", t.group(1))).strip() if t else ""


sm_add = []
for p, slug, fu in PREFS:
    keep = lambda m: m.group(0) if f'data-pref="{p}"' in m.group(0) else ""
    out = CARD.sub(keep, s)
    cards = [c for c in CARD.findall(out)]
    now = [c for c in cards if re.search(r'data-e="(\d{4}-\d\d-\d\d)"', c) and re.search(r'data-e="([^"]+)"', c).group(1) >= TODAY]
    free = sum(1 for c in now if 'data-tag="無料' in c)
    names = "、".join(dict.fromkeys(name(c) for c in now if name(c)))
    names = names[:70].rsplit("、", 1)[0] if len(names) > 70 else names
    title = f"{p}のおでかけ・イベント一覧｜開催中・今週末・これから（{fu}）｜TOWN NOTE"
    desc = f"{fu}で開催中・これからのイベントとおでかけ先{len(now)}件（入場無料{free}件）を、日程・場所・公式ページつきで一覧にしました。{names}など。{upd}。"
    out = re.sub(r"<title>.*?</title>", lambda _: f"<title>{html.escape(title)}</title>", out, count=1, flags=re.S)
    out = re.sub(r'<meta name="description" content="[^"]*">', lambda _: f'<meta name="description" content="{html.escape(desc)}">', out, count=1)
    out = out.replace('<link rel="canonical" href="https://townnote.pages.dev/odekake">', f'<link rel="canonical" href="https://townnote.pages.dev/odekake-{slug}">', 1)
    out = re.sub(r'(<meta property="og:(?:title|description)" content=")[^"]*', lambda m: m.group(1) + html.escape(title if "title" in m.group(0) else desc), out)
    out = out.replace("<h1>関西おでかけリスト</h1>", f"<h1>{p}おでかけリスト</h1>", 1)
    # 11/6 府県ページの見られた数を、関西のリストと分けて数える
    out = out.replace('c("表示：おでかけリスト");', f'c("表示：{p}おでかけリスト"+(document.referrer&&document.referrer.indexOf(location.host)<0?"（外から）":""));', 1)
    # 検索用のイベント情報も、その府県の物だけにする
    m = re.search(r'<script type="application/ld\+json" id="ev-ld">(.*?)</script>', out, re.S)
    if m:
        ld = json.loads(m.group(1).replace("<\\/", "</"))
        items = [x for x in ld.get("itemListElement", []) if x["item"]["location"].get("address", "").startswith(fu)]
        for i, x in enumerate(items): x["position"] = i + 1
        ld["itemListElement"] = items; ld["name"] = f"{p}のおでかけリスト 開催中・これからのイベント"
        tag = '<script type="application/ld+json" id="ev-ld">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
        out = out[:m.start()] + tag + out[m.end():]
    # ほかの府県のページへの入口（一番下の注意書きの前）。関西すべてのリストに置いた入口（<!--pn-->）は消してから付ける
    out = re.sub(r'<!--pn-->.*?<!--/pn-->', '', out, flags=re.S)
    nav = '<nav class="prefnav" aria-label="府県ごとに見る"><div class="plh">府県ごとに見る</div>' + \
          '<a href="/odekake">関西すべて</a>' + "".join(
              f'<a href="/odekake-{sl}"{" aria-current=page" if sl == slug else ""}>{q}</a>' for q, sl, _ in PREFS) + "</nav>"
    css = "<style>.prefnav{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:28px 0 8px}.prefnav .plh{width:100%;text-align:center;font-size:12px;letter-spacing:.2em;color:#8a8f98;margin-bottom:4px}.prefnav a{font-size:13px;padding:6px 12px;border:1px solid #DCDFE4;border-radius:99px;color:#3a3330;text-decoration:none;background:#fff}.prefnav a[aria-current]{background:#2B2622;color:#fff;border-color:#2B2622}</style>"
    css += "<style>#flt{display:none!important}</style>"  # 府県の切り替えは下の「府県ごとに見る」で
    out = out.replace("</head>", css + "</head>", 1)
    # 終わったおでかけは府県が書いていないので、府県のページでは見せない（形は崩さず隠すだけ）
    out = out.replace("</head>", '<style>.wk[style*="b9ada2"],.past,.past+*{display:none!important}</style></head>', 1)
    out = out.replace("出かける前に、必ず公式ページで", nav + "出かける前に、必ず公式ページで", 1) if "出かける前に、必ず公式ページで" in out else out.replace("</body>", nav + "</body>", 1)
    open(f"links/odekake-{slug}.html", "w", encoding="utf-8").write(out)
    sm_add.append(f"https://townnote.pages.dev/odekake-{slug}")
    print(slug, len(cards), "cards,", len(now), "now")

# サイトの地図に足す（無ければ）
sm = open("links/sitemap.xml", encoding="utf-8").read()
for u in sm_add:
    if f"<loc>{u}</loc>" not in sm:
        sm = sm.replace("<url><loc>https://townnote.pages.dev/odekake</loc>",
                        f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n<url><loc>https://townnote.pages.dev/odekake</loc>", 1) \
            if "<url><loc>https://townnote.pages.dev/odekake</loc>" in sm else sm.replace("</urlset>", f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>")
    sm = re.sub(rf"(<loc>{re.escape(u)}</loc><lastmod>)[^<]*", rf"\g<1>{TODAY}", sm)
open("links/sitemap.xml", "w", encoding="utf-8").write(sm)
