"""11/17 月：開店・閉店の公式の元（チェーンの新店ページ・商業施設・PR TIMES）の中身を、Actions から取って保存する（作業環境からはつながらないため）。
読み方（パーサー）を書く前に、本物の HTML を見るための道具。tools/kaiten/probe/ に保存する。"""
import os, re, sys, time, urllib.request
URLS = {
 "lawson-kinki": "https://www.lawson.co.jp/newstore/kinki.html",
 "lawson-kantou": "https://www.lawson.co.jp/newstore/kantou.html",
 "daiso": "https://www.daiso-sangyo.co.jp/infolist/shop",
 "daiso-1": "https://www.daiso-sangyo.co.jp/info/shop/51233",
 "prtimes-news": "https://prtimes.jp/sitemap-news.xml",
 "prtimes-rdf": "https://prtimes.jp/index.rdf",
 "lumine": "https://www.lumine.ne.jp/newshop/",
 "lumine-est": "https://www.lumine.ne.jp/est/newshop/",
 "lalaport-expo": "https://mitsui-shopping-park.com/lalaport/expocity/news/",
 "parco-shinsaibashi": "https://shinsaibashi.parco.jp/shopnews/",
 "cando": "https://www.cando-web.co.jp/news/",
 "tsuruha": "https://www.tsuruha.co.jp/news/open/",
 "sundrug": "https://www.sundrug.co.jp/news/category/estate",
 "sushiro": "https://www.akindo-sushiro.co.jp/news/?category=3",
 "saizeriya": "https://www.saizeriya.co.jp/shop-news/",
 "komeda": "https://fc.komeda.co.jp/information/",
 "decohome": "https://www.nitori.co.jp/decohome/news/shop.html",
 "ok": "https://ok-corporation.jp/news/new-shop/",
 "donki": "https://www.donki.com/backnumber/index.php?p=1&page=1",
 "aeonmall-future": "https://www.aeonmall.com/open_renewal/search",
 "hankyu-shopnews": "https://www.hankyu-dept.co.jp/honten/shopnews/",
 "mapfan-27": "https://mapfan.com/future-info/facility/27/upcoming/spots",
 "kurasushi": "https://www.kurasushi.co.jp/news/",
 "workman": "https://www.workman.co.jp/news/",
 "seria": "https://www.seria-group.com/news/",
 "mandai": "https://www.mandai-net.co.jp/news/",
 "lopia": "https://lopia.jp/news/",
 "atpress-robots": "https://www.atpress.ne.jp/robots.txt",
}
# 11/17 PR TIMES の発表の中身（住所・時間の書き方）を見る
for i, u in enumerate(["https://prtimes.jp/main/html/rd/p/000001216.000014225.html", "https://prtimes.jp/main/html/rd/p/000001230.000034930.html",
                       "https://prtimes.jp/main/html/rd/p/000000053.000053965.html", "https://prtimes.jp/main/html/rd/p/000000444.000022024.html",
                       "https://prtimes.jp/main/html/rd/p/000000288.000040849.html", "https://prtimes.jp/main/html/rd/p/000000012.000135197.html",
                       "https://www.mandai-net.co.jp/news/", "https://www.sundrug.co.jp/news/post-24634"]):
    URLS[f"rel{i}"] = u
URLS = {k: v for k, v in URLS.items() if k.startswith("rel") or k in ("prtimes-news",)}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe")
os.makedirs(out, exist_ok=True)
for k, u in URLS.items():
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; TownNoteBot/1.0)"}), timeout=25)
        b = r.read()[:4000000]
        cs = (re.search(rb'charset=["\']?([\w-]+)', b[:3000]) or [None, b"utf-8"])[1].decode()
        t = b.decode(cs if cs.lower() not in ("shift_jis", "sjis", "x-sjis") else "cp932", "replace")
        open(os.path.join(out, k + ".html"), "w", encoding="utf-8").write(t)
        print(k, r.status, len(b))
    except Exception as e:
        print(k, "ERR", str(e)[:120])
    time.sleep(1.5)
