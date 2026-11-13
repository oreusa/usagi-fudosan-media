# 公式の統計の置き場から、ダウンロードのリンクを探して写す（GitHub の機械で回す。この作業場からは開けないため）
import re, sys, urllib.request, html, urllib.parse
urls = [l.strip() for l in open("tools/seo_data/urls.txt") if l.strip() and not l.startswith("#")]
out = open("tools/seo_data/out/links.txt", "w")
for u in urls:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40)
        b = r.read(); enc = r.headers.get_content_charset() or "utf-8"
        try: s = b.decode(enc)
        except Exception: s = b.decode("cp932", "ignore")
    except Exception as e:
        out.write(f"## {u} ERR {e}\n"); continue
    out.write(f"## {u} {len(s)}\n")
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        h, t = m.group(1), re.sub(r"<[^>]+>|\s+", " ", html.unescape(m.group(2))).strip()
        full = urllib.parse.urljoin(u, html.unescape(h))
        out.write(f"{t[:80]}\t{full}\n")
