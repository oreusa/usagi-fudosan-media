"""おでかけリストとイルミのページのリンクが開けるかを確かめる（10/31 オーナー「気づいてないだけでもっと深刻なのがあるかも」）。
GitHub Actions（linkcheck.yml）で毎日動かし、stats/linkcheck.md に書く。19:47 のリスト点検がこれを読んで直す。
- 開けない（4xx・5xx・つながらない）物
- 1つのページに、別の催しなのに同じURLが付いている物（10/31 室生寺に壺阪寺のURLが付いていた）"""
import collections, concurrent.futures as cf, glob, html, re, urllib.request, ssl, datetime

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
PAGES = ["links/index.html"] + sorted(glob.glob("links/illumination*.html"))
OK_SAME = {"https://www.hikari-kyoen.com/renaissance/index.html"}  # 同じ催しのまとめページ（御堂筋と中央公会堂）


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
    with cf.ThreadPoolExecutor(12) as ex:
        res = dict(zip(allc, ex.map(status, allc)))
    bad = [(u, s) for u, s in res.items() if not (isinstance(s, int) and s < 400) and s != 403]
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
    out = [f"# リンクの確かめ（{now} JST・{len(res)}件）", "", "## 開けない（直す）"]
    out += [f"- ✗ {allc[u][0]}（{allc[u][1]}）{s} {u}" for u, s in sorted(bad, key=lambda x: allc[x[0]][1])] or ["- なし"]
    out += ["", "## 別の催しに同じURL（どちらかが違うページかも）"] + (same or ["- なし"])
    out += ["", "※ 403 はサイトが機械を断っているだけのことが多いので、数に入れない。"]
    open("stats/linkcheck.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
