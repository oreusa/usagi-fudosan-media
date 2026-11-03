# 試し（本番に入れない）：おでかけリストのカードに、ウィキメディアの「自由に使ってよい」写真を付けた見本を作る
# 会場の名前と同じ題の日本語版ウィキペディアの記事の代表写真だけを使う（違う場所の写真を避ける）
import json, re, html, time, urllib.parse, urllib.request
SRC = "links/index.html"; OUT = "links/preview-photo.html"
UA = {"User-Agent": "TownNotePhotoTry/1.0 (https://townnote.pages.dev/)"}
OK = re.compile(r"^(CC BY(-SA)? ?[0-9.]*|CC0|Public domain|PD.*|CC BY(-SA)? [0-9.]+ .*)$", re.I)
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.load(r)
        except Exception as e: time.sleep(2)
    return {}
def page_image(title):
    q = urllib.parse.urlencode({"action":"query","format":"json","titles":title,"prop":"pageimages","piprop":"name","redirects":1})
    for p in get("https://ja.wikipedia.org/w/api.php?"+q).get("query",{}).get("pages",{}).values():
        if "missing" not in p and p.get("pageimage"): return p["pageimage"]
def info(fn):
    q = urllib.parse.urlencode({"action":"query","format":"json","titles":"File:"+fn,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":720})
    for p in get("https://commons.wikimedia.org/w/api.php?"+q).get("query",{}).get("pages",{}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii: return None
        m = ii.get("extmetadata", {}); lic = m.get("LicenseShortName",{}).get("value","")
        if not OK.match(lic.strip()): return {"skip": lic}
        art = re.sub(r"<[^>]+>", "", m.get("Artist",{}).get("value","")).strip()[:40] or "不明"
        return {"src": ii.get("thumburl") or ii["url"], "page": ii.get("descriptionurl"), "lic": lic, "by": html.unescape(art)}
src = open(SRC, encoding="utf-8").read()
cards = re.findall(r'<a class="card"[^>]*>.*?</a>', src)
data, log, seen = {}, [], {}
for c in cards:
    t = html.unescape(re.search(r'<div class="t">(.*?)</div>', c).group(1))
    m = re.search(r'<div class="m">(.*?)</div>', c); m = html.unescape(m.group(1)) if m else ""
    venue = m.split("｜",1)[1].strip() if "｜" in m else ""
    names = [venue] + ([venue.split(" ")[0]] if " " in venue else []) + ([venue.split("・")[0]] if "・" in venue else [])
    got = None
    for n in names:
        if not n: continue
        if n in seen: got = seen[n]; break
        fn = page_image(n); r = info(fn) if fn else None; seen[n] = r if r and "src" in r else None
        if r and "src" in r: got = r; break
        if r: log.append(f"ライセンス外 {n}: {r['skip']}")
    if got: data[re.sub(r"\s+","",t)] = got
    log.append(f"{'○' if got else '－'} {t}｜{venue}")
inj = """<style>
.card .ph{display:block;width:calc(100% + 72px);margin:-14px -56px 12px -16px;height:150px;object-fit:cover;border-radius:7px 7px 0 0;background:#F1F2F4}
.card .cr{position:absolute;left:16px;bottom:8px;right:56px;font-size:9.5px;line-height:1.3;color:#8a8f98;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .phw{position:relative}
</style><script>
(function(){var D=__D__;function go(){document.querySelectorAll("a.card").forEach(function(a){if(a.querySelector(".ph"))return;var t=a.querySelector(".t");if(!t)return;var d=D[t.textContent.replace(/\s+/g,"")];if(!d)return;
var i=document.createElement("img");i.className="ph";i.alt="";i.src=d.src;a.insertBefore(i,a.firstChild);
var c=document.createElement("div");c.className="cr";c.textContent="写真："+d.by+"／"+d.lic+"（ウィキメディア・コモンズ）";a.appendChild(c);});}
document.addEventListener("DOMContentLoaded",function(){go();setTimeout(go,500);setTimeout(go,1500);});})();
</script>""".replace("__D__", json.dumps(data, ensure_ascii=False))
out = src.replace("</body>", inj + "</body>", 1).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"', 1)
open(OUT, "w", encoding="utf-8").write(out)
open("shots/photo_try_log.txt", "w", encoding="utf-8").write(f"写真あり {len(data)} / {len(cards)}\n" + "\n".join(log) + "\n")
print(f"写真あり {len(data)} / {len(cards)}")
