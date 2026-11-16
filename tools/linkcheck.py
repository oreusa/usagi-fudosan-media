"""おでかけリストとイルミのページのリンクが開けるかを確かめる（10/31 オーナー「気づいてないだけでもっと深刻なのがあるかも」）。
GitHub Actions（linkcheck.yml）で毎日動かし、stats/linkcheck.md に書く。19:47 のリスト点検がこれを読んで直す。
- 開けない（4xx・5xx・つながらない）物
- 1つのページに、別の催しなのに同じURLが付いている物（10/31 室生寺に壺阪寺のURLが付いていた）"""
import collections, concurrent.futures as cf, glob, html, re, urllib.request, ssl, datetime

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
PAGES = ["links/index.html"] + sorted(glob.glob("links/illumination*.html"))
OK_SAME = {"https://hikari-kyoen.com/core/renaissance",  # 中之島と中央公会堂（同じ催し）
           "https://www.tsubosaka1300.or.jp/news130.html"}  # 壺阪寺・岡寺・室生寺の合同ライトアップ「光の巡礼」
# 11/16 オーナー「HP全部だよね？抜けてないよね？」→ おでかけ・イルミだけでなく、HPの全ページ（不動産・解体・実家・街・泊まり・紅葉・お買い物）の外へのリンクも見る。
# アフィリエイトの入口（バリューコマース・楽天）は押さない（数に入るため）。中の行き先（vc_url・pc）を開いて確かめる。
SKIP = re.compile(r"townnote|pages\.dev|google\.|instagram\.com|threads\.(net|com)|//x\.com|twitter\.com|line\.me|facebook\.com")
KIND = [("不動産", r"fudosan|kaitai|jikka|machi|akiya|chika|gyosha|ranking|uru|ikura|sagasu|shindan|moushikomi|townnotes|town-notes"),
        ("泊まり", r"tomari"), ("紅葉", r"koyo"), ("イルミ", r"illumination"), ("初もうで", r"hatsumode"), ("おでかけ", r"odekake|index|/o/|ima")]


def kind(p):
    for k, r in KIND:
        if re.search(r, p):
            return k
    return "ほか"


def dest(u):
    """アフィリエイトの入口なら中の行き先を返す（入口は押さない）。"""
    import urllib.parse as up
    q = up.parse_qs(up.urlparse(u).query)
    for key in ("vc_url", "pc", "url"):
        if key in q and ("valuecommerce" in u or "afl.rakuten" in u or "a8.net" in u):
            return q[key][0]
    if "valuecommerce" in u or "afl.rakuten" in u or "a8.net" in u:
        return None
    return u


def links_all():
    for p in sorted(glob.glob("links/**/*.html", recursive=True)):
        s = open(p, encoding="utf-8").read()
        for m in re.finditer(r'<a\b[^>]*?href="(https?://[^"]+)"[^>]*>(.*?)</a>', s, re.S):
            u = html.unescape(m.group(1)).split("#")[0]
            if SKIP.search(u):
                continue
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(2))).strip()[:40] or "?"
            yield u, t, p


def cards(p):
    s = open(p, encoding="utf-8").read()
    for m in re.finditer(r'<a class="card[^"]*"[^>]*?href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        t = re.search(r'class="t">(.*?)</div>', m.group(2), re.S)
        yield html.unescape(m.group(1)), re.sub(r"<[^>]+>", "", t.group(1)).strip() if t else "?"


def status(u):
    ctx = ssl.create_default_context()
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(u, method=method, headers={"User-Agent": UA, "Accept-Language": "ja"})
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "GET" or e.code not in (403, 405, 404, 400, 501):
                return e.code
        except Exception as e:
            if method == "GET":
                return type(e).__name__
    return "?"


def main():
    rows, same = [], []
    allc = {}
    for p in PAGES:
        cs = list(cards(p))
        by = collections.defaultdict(set)
        for u, t in cs:
            by[u].add(t)
            allc.setdefault(u, (t, p))
        for u, ts in by.items():
            if len(ts) > 1 and u not in OK_SAME:
                same.append(f"- {p}：{' ／ '.join(sorted(ts))} → {u}")
    nod = 0
    for u, t, p in links_all():
        d = dest(u)
        if d is None:
            nod += 1
            continue
        allc.setdefault(d, (t, p))
    with cf.ThreadPoolExecutor(16) as ex:
        res = dict(zip(allc, ex.map(status, allc)))
    bad = [(u, s) for u, s in res.items() if not (isinstance(s, int) and s < 400) and s != 403]
    cnt = collections.Counter(kind(p) for t, p in allc.values())
    badk = collections.Counter(kind(allc[u][1]) for u, s in bad)
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
    out = [f"# リンクの確かめ（{now} JST・{len(res)}件・HPの全ページ）", "",
           "種類ごと（見た数／開けない数）：" + "・".join(f"{k} {cnt[k]}／{badk[k]}" for k, _ in KIND + [("ほか", "")] if cnt[k]),
           f"行き先の分からないアフィリエイトの入口 {nod}本（押さないので見ていない）", "", "## 開けない（直す）"]
    out += [f"- ✗ [{kind(allc[u][1])}] {allc[u][0]}（{allc[u][1]}）{s} {u}" for u, s in sorted(bad, key=lambda x: (kind(allc[x[0]][1]), allc[x[0]][1]))] or ["- なし"]
    out += ["", "## 別の催しに同じURL（どちらかが違うページかも）"] + (same or ["- なし"])
    out += ["", "※ 403 はサイトが機械を断っているだけのことが多いので、数に入れない。",
            "※ 市や県・観光協会のサイトは、外国（GitHub の機械）からだと 404 や つながらない を返すことがある（10/31 天理市・高槻市・新宮・好古園は WebFetch では開けた）。直す前に WebFetch で開けるか必ず確かめ、開ければそのままにする。"]
    open("stats/linkcheck.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
