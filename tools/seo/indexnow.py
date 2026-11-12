"""Bing など（IndexNow）へ、変わったページのアドレスを知らせる。11/12 月：Google に載っているのが 関西8枚・関東1枚 と分かった。
Google は人の手（Search Console）でしか頼めないが、Bing・Copilot・ChatGPT の検索はここへ送るだけで見に来る。
はじめての日は全部、次の日からは sitemap の lastmod がきょうの物だけ（月曜は lastmod の無い物も）。結果は stats/indexnow.json。
鍵は公開してよい物（links/<鍵>.txt と同じ文字。持ち主の証明に使うだけ）。"""
import json, os, re, sys, urllib.request, datetime
KEY = "e38dec9c8189c4506a483aa2fd97fcfb"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "stats", "indexnow.json")
day = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
SITES = [("kansai", "townnote.pages.dev"), ("kanto", "lifenote-kanto.pages.dev")]
try: st = json.load(open(OUT, encoding="utf-8"))
except Exception: st = {"about": "IndexNow（Bing など）へ送った数。rows: {day, site, n, code}。code 200/202 が成功", "rows": []}
monday = datetime.date.fromisoformat(day).weekday() == 0
for site, host in SITES:
    row = {"day": day, "site": site, "n": 0, "code": None}
    try:
        req = urllib.request.Request(f"https://{host}/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"})
        xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        ent = re.findall(r"<url>\s*<loc>([^<]+)</loc>(?:\s*<lastmod>([^<]*)</lastmod>)?", xml)
        first = not any(r.get("site") == site and r.get("code") in (200, 202) and r.get("n", 0) > 50 for r in st["rows"])
        urls = [u for u, lm in ent if first or lm == day or (monday and not lm)]
        urls = [u for u in urls if u.startswith(f"https://{host}/")][:10000]
        row["all"] = len(ent)
        if urls:
            body = json.dumps({"host": host, "key": KEY, "keyLocation": f"https://{host}/{KEY}.txt", "urlList": urls}).encode()
            r = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
            try: row["code"] = urllib.request.urlopen(r, timeout=30).status
            except urllib.error.HTTPError as e: row["code"] = e.code; row["err"] = e.read().decode("utf-8", "ignore")[:200]
            row["n"] = len(urls)
        else: row["code"] = 0
    except Exception as e: row["err"] = str(e)[:200]
    st["rows"] = [r for r in st["rows"] if not (r.get("day") == day and r.get("site") == site)] + [row]
    print(row)
st["rows"] = st["rows"][-120:]
json.dump(st, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
