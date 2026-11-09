# サイトマップの lastmod を「中身が本当に変わった日」にする（11/9 毎日すべて今日の日付だと Google が日付を信じなくなる）
# ページの中身（数え用のスクリプトは除く）の指紋を stats/sitemap-dates.json に残し、指紋が変わった日だけ日付を進める
import hashlib, json, os, re, sys
from datetime import datetime, timedelta, timezone
TODAY = sys.argv[1] if len(sys.argv) > 1 else (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d")
R = os.path.dirname(os.path.abspath(__file__)) + "/../"
SM, DB = R + "links/sitemap.xml", R + "stats/sitemap-dates.json"
SPECIAL = {"": "town-notes.html", "odekake": "index.html"}
try:
    db = json.load(open(DB, encoding="utf-8"))
except Exception:
    db = {}

def fp(path):
    f = R + "links/" + SPECIAL.get(path, path.removesuffix(".html") + ".html")
    if not os.path.exists(f):
        return None
    h = open(f, encoding="utf-8", errors="ignore").read()
    h = re.sub(r"<script>\(function\(\)\{.*?sendBeacon.*?</script>", "", h, flags=re.S)  # 数え用
    return hashlib.sha1(h.encode()).hexdigest()[:16]

sm = open(SM, encoding="utf-8").read()
def fix(m):
    loc = m.group(1); path = loc.split("pages.dev/", 1)[1] if "pages.dev/" in loc else ""
    h = fp(path)
    old = db.get(path)
    if h is None:
        return m.group(0)
    if not old or old[0] != h:
        db[path] = [h, TODAY if old else (m.group(2) if m.group(2) and m.group(2) < TODAY else TODAY)]
    return f"<url><loc>{loc}</loc><lastmod>{db[path][1]}</lastmod></url>"
sm2 = re.sub(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]*)</lastmod>)?</url>", fix, sm)
open(SM, "w", encoding="utf-8").write(sm2)
json.dump(db, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
ds = re.findall(r"<lastmod>([^<]+)</lastmod>", sm2)
print("sitemap:", len(ds), "urls,", sum(d == TODAY for d in ds), "changed today")
