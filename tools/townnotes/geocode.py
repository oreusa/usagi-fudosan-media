"""TOWN NOTES（仮）の地図用に、おでかけリストのカードの場所を緯度・経度にする。
GitHub Actions で動かす（作業環境からは地図の検索サービスにつなげないため）。
結果: links/townnotes/geo.json {カード名: [lat, lon, "どの検索で取れたか"]}
"""
import json, re, time, urllib.parse, urllib.request, html, os
SRC = 'links/index.html'; OUT = 'links/townnotes/geo.json'
BOX = {'大阪': (34.2, 35.1, 135.0, 135.8), '京都': (34.7, 35.8, 134.8, 136.1), '兵庫': (34.1, 35.7, 134.2, 135.5),
       '奈良': (33.8, 34.8, 135.5, 136.3), '滋賀': (34.7, 35.7, 135.7, 136.5), '和歌山': (33.4, 34.4, 135.0, 136.1)}
UA = {'User-Agent': 'usagi-town-notes-proto/0.1 (github.com/oreusa)'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r: return json.load(r)
def ok(p, lat, lon):
    b = BOX.get(p, (33.4, 35.8, 134.2, 136.5)); return b[0] <= lat <= b[1] and b[2] <= lon <= b[3]
def nomi(q):
    time.sleep(1.1)
    try: r = get('https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=jp&q=' + urllib.parse.quote(q))
    except Exception as e: print('nomi err', q, e); return None
    return (float(r[0]['lat']), float(r[0]['lon'])) if r else None
def gsi(q):
    try: r = get('https://msearch.gsi.go.jp/address-search/AddressSearch?q=' + urllib.parse.quote(q))
    except Exception as e: print('gsi err', q, e); return None
    return (r[0]['geometry']['coordinates'][1], r[0]['geometry']['coordinates'][0]) if r else None
src = open(SRC, encoding='utf-8').read()
old = json.load(open(OUT)) if os.path.exists(OUT) else {}
res = {}
for m in re.finditer(r'<a class="card"([^>]*)>(.*?)</a>', src, re.S):
    attrs, body = m.group(1), m.group(2)
    a = dict(re.findall(r'data-(\w+)="([^"]*)"', attrs))
    t = re.search(r'class="t">(.*?)</div>', body); mm = re.search(r'class="m">(.*?)</div>', body)
    if not t: continue
    title = html.unescape(re.sub('<[^>]+>', '', t.group(1))).strip()
    if title in res: continue
    if title in old and old[title][2] != 'pref': res[title] = old[title]; continue
    pref = a.get('pref', ''); place = html.unescape(a.get('map', ''))
    city, spot = '', ''
    if mm:
        parts = html.unescape(mm.group(1)).split('｜'); city = parts[0].strip(); spot = parts[1].strip() if len(parts) > 1 else ''
    tries = [('place', nomi, place), ('spot', nomi, (spot + ' ' + city).strip()), ('title', nomi, title + ' ' + city), ('city', gsi, city), ('city', nomi, city)]
    got = None
    for kind, fn, q in tries:
        if not q: continue
        r = fn(q)
        if r and ok(pref, *r): got = [round(r[0], 5), round(r[1], 5), kind]; break
    res[title] = got or [None, None, 'none']
    print(title, res[title])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('done', len(res), sum(1 for v in res.values() if v[2] in ('place', 'spot', 'title')), 'exact')
