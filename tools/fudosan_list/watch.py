"""関西不動産リストの新着さがし（11/16 オーナー「不動産は？仕組みできてる？」→ 中身を足すのが人の手だった）。
毎朝 link-stats.yml で動く。国・府県・鉄道・レインズの「お知らせ」のページを開き、前の日に無かったリンクのうち
不動産リストに合う言葉（空き家・解体・補助・相続・地価・人口・新駅・開業など）を含む物を stats/fudosan-shinchaku.md に書く。
足すのは機械ではなく、月曜と木曜の 19:47 の回（kanri/teiki/odekake-list-1947.md）。公式ページで確かめてから
tools/fudosan_list/facts.json に足して make.py を回す。足した・見送ったら stats/fudosan-watch.json の done に URL を入れる。"""
import concurrent.futures as cf, datetime, html, json, os, re, ssl, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "stats/fudosan-watch.json")
OUT = os.path.join(ROOT, "stats/fudosan-shinchaku.md")
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
# (名前, お知らせのページ, リストの種類の目安)
PAGES = [
    ("国土交通省 報道発表", "https://www.mlit.go.jp/report/press/index.html", "seido"),
    ("国土交通省 近畿地方整備局", "https://www.kkr.mlit.go.jp/", "dekiru"),
    ("法務省（相続登記）", "https://www.moj.go.jp/", "seido"),
    ("国税庁", "https://www.nta.go.jp/", "seido"),
    ("総務省統計局", "https://www.stat.go.jp/", "jinko"),
    ("近畿レインズ", "https://www.kinkireins.or.jp/", "chika"),
    ("大阪府", "https://www.pref.osaka.lg.jp/", "seido"),
    ("京都府", "https://www.pref.kyoto.jp/", "seido"),
    ("兵庫県", "https://web.pref.hyogo.lg.jp/", "seido"),
    ("奈良県", "https://www.pref.nara.lg.jp/", "seido"),
    ("滋賀県", "https://www.pref.shiga.lg.jp/", "seido"),
    ("和歌山県", "https://www.pref.wakayama.lg.jp/", "seido"),
    ("大阪市", "https://www.city.osaka.lg.jp/", "seido"),
    ("京都市", "https://www.city.kyoto.lg.jp/", "seido"),
    ("神戸市", "https://www.city.kobe.lg.jp/", "seido"),
    ("堺市", "https://www.city.sakai.lg.jp/", "seido"),
    ("JR西日本 ニュースリリース", "https://www.westjr.co.jp/press/", "dekiru"),
    ("近鉄 ニュース", "https://www.kintetsu.co.jp/news/", "dekiru"),
    ("南海 ニュース", "https://www.nankai.co.jp/", "dekiru"),
    ("阪急阪神HD ニュース", "https://www.hankyu-hanshin.co.jp/", "dekiru"),
    ("京阪HD ニュース", "https://www.keihan-holdings.co.jp/", "dekiru"),
    ("Osaka Metro ニュース", "https://www.osakametro.co.jp/", "dekiru"),
]
WORDS = re.compile(r"空き家|空家|解体|除却|補助|助成|相続|登記|地価|路線価|基準地|公示|人口|国勢調査|移住|定住|耐震|住宅|マンション|中古|成約|不動産|固定資産|土地|新駅|開業|延伸|再開発|まちづくり|宅地|リフォーム|子育て世帯")
NOT = re.compile(r"採用|入札|職員|募集|議会|選挙|プレゼント|キャンペーン|運休|遅延|工事のお知らせ|お詫び")


def get(u):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "ja"})
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            b = r.read(3_000_000)
            cs = r.headers.get_content_charset() or (re.search(rb'charset=["\']?([\w-]+)', b[:3000]) or [None, b"utf-8"])[1].decode()
            return b.decode(cs, "replace")
    except Exception as e:
        return "ERR " + type(e).__name__


def links(base, s):
    out = {}
    for m in re.finditer(r'<a\b[^>]*?href="([^"#]+)"[^>]*>(.*?)</a>', s, re.S | re.I):
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
        if 6 <= len(t) <= 140:
            out[urllib.parse.urljoin(base, html.unescape(m.group(1)))] = t
    return out


def main():
    db = json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else {"seen": {}, "done": [], "new": []}
    with cf.ThreadPoolExecutor(8) as ex:
        res = dict(zip([p[1] for p in PAGES], ex.map(get, [p[1] for p in PAGES])))
    today = (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
    bad, first = [], []
    for name, u, cat in PAGES:
        s = res[u]
        if s.startswith("ERR "):
            bad.append(f"- {name} {u}（{s[4:]}）")
            continue
        ls = links(u, s)
        seen = set(db["seen"].get(u, []))
        if not seen:
            first.append(name)
        k = 0
        for lu, t in ls.items():
                if not seen and k >= 5:  # はじめて見たページは、今出ている物から5件だけ候補に
                    break
                if lu in seen or lu in db["done"] or any(n["url"] == lu for n in db["new"]):
                    continue
                if WORDS.search(t) and not NOT.search(t):
                    db["new"].append({"date": today, "src": name, "cat": cat, "t": t, "url": lu}); k += 1
        db["seen"][u] = sorted(seen | set(ls))[-3000:]
    # 30日たった新着は消す（見送り扱い）
    lim = (datetime.date.fromisoformat(today) - datetime.timedelta(days=30)).isoformat()
    db["new"] = [n for n in db["new"] if n["date"] >= lim and n["url"] not in db["done"]]
    json.dump(db, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    out = [f"# 不動産リストの新着の候補（{today}・{len(PAGES)}ページを見た）", "",
           "月曜と木曜の 19:47 の回が、上から公式ページで確かめ、合う物を tools/fudosan_list/facts.json に足して make.py を回す。",
           "足した物・合わない物は stats/fudosan-watch.json の done に URL を入れる（次から出ない）。", "",
           f"## 候補（{len(db['new'])}件）"]
    out += [f"- {n['date']}｜{n['src']}｜[{n['cat']}] {n['t']}｜{n['url']}" for n in sorted(db["new"], key=lambda n: n["date"], reverse=True)] or ["- なし"]
    if first:
        out += ["", "## 今日はじめて見たページ（今出ている物から5件まで候補に入れた。明日からは新しい物だけ）", "- " + "・".join(first)]
    out += ["", "## 開けなかったページ（続けば PAGES のアドレスを直す）"] + (bad or ["- なし"])
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out[:12]))


if __name__ == "__main__":
    main()
