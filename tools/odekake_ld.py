"""おでかけリスト（links/index.html）のカードから、検索用の催しの情報（Event の構造化データ）を作って head に入れる。
11/2 オーナーOK「全部ok」→ 検索結果に日付が出やすくするため。毎朝 link-stats.yml で作り直す（終わった物は外す）。
python3 tools/odekake_ld.py [YYYY-MM-DD]"""
import re, json, html, sys, datetime
P = "links/index.html"
TODAY = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
FU = {"大阪": "大阪府", "京都": "京都府", "兵庫": "兵庫県", "奈良": "奈良県", "滋賀": "滋賀県", "和歌山": "和歌山県"}
s = open(P, encoding="utf-8").read()
evs, seen = [], set()
for m in re.finditer(r'<a class="card"([^>]*)>(.*?)</a>', s, re.S):
    a = dict(re.findall(r'(data-\w+|href)="([^"]*)"', m.group(1)))
    st, en = a.get("data-s", ""), a.get("data-e", "")
    if not re.fullmatch(r"\d{4}-\d\d-\d\d", st): continue
    if en and en < TODAY: continue
    t = re.search(r'class="t">(.*?)</div>', m.group(2), re.S); mm = re.search(r'class="m">(.*?)</div>', m.group(2), re.S)
    if not t: continue
    name = html.unescape(re.sub("<[^>]+>", "", t.group(1))).strip()
    if name in seen: continue
    seen.add(name)
    city, place = "", ""
    if mm:
        parts = html.unescape(re.sub("<[^>]+>", "", mm.group(1))).split("｜"); city = parts[0].strip(); place = parts[-1].strip()
    ev = {"@type": "Event", "name": name, "startDate": st, "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
          "eventStatus": "https://schema.org/EventScheduled",
          "location": {"@type": "Place", "name": place or city, "address": FU.get(a.get("data-pref", ""), "") + city}, "url": html.unescape(a.get("href", ""))}
    if re.fullmatch(r"\d{4}-\d\d-\d\d", en): ev["endDate"] = en
    if "無料" in a.get("data-tag", ""): ev["isAccessibleForFree"] = True
    evs.append(ev)
ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "関西おでかけリスト 開催中・これからのイベント",
      "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": e} for i, e in enumerate(evs)]}
tag = '<script type="application/ld+json" id="ev-ld">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
if 'id="ev-ld"' in s:
    s2 = re.sub(r'<script type="application/ld\+json" id="ev-ld">.*?</script>', lambda _: tag, s, count=1, flags=re.S)
else:
    s2 = s.replace("</head>", tag + "</head>", 1)
if s2 != s: open(P, "w", encoding="utf-8").write(s2)
print(len(evs), "events")
