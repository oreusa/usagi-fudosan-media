"""11/18 月：兵庫観光navi 写真・動画ライブラリ（https://hyogo-tourism.jp/photo/）の写真の一覧を作る。
規約 https://hyogo-tourism.jp/photo/terms.html ：兵庫の魅力発信・観光振興に使える／申請不要（ダウンロードで同意）／©表記はそのまま／
HP に使ったらページのアドレスを photo@hyogo-tourism.jp に知らせるよう努める／作り終えたら作業中のデータは消す。
使い方:
  python3 tools/photo/hyogo.py list <保存先>            → 保存先/catalog.json（id・題・カテゴリ・エリア・向き・大きさ）
  python3 tools/photo/hyogo.py get <保存先> 572 936 ...  → 保存先/h572.jpg（幅 PW）"""
import io, json, os, re, sys, time, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (TownNote; +https://kansai.townnote.app/)"}
B = "https://hyogo-tourism.jp/photo/"
def get(u):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except Exception:
            if i == 2: raise
            time.sleep(3)
def tx(s): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()
cmd, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
if cmd == "list":
    ids = []
    for n in range(1, 60):
        h = get(B + (f"index_{n}.html" if n > 1 else "index.html")).decode("utf-8", "ignore")
        got = re.findall(r'href="detail_(\d+)\.html"', h)
        new = [i for i in dict.fromkeys(got) if i not in ids]
        if not new: break
        ids += new; time.sleep(0.4)
    cat = []
    for i in ids:
        try:
            h = get(B + f"detail_{i}.html").decode("utf-8", "ignore")
            dl = dict((tx(a), tx(b)) for a, b in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", h, re.S))
            t = tx(re.search(r"<h2>(.*?)</h2>", h, re.S).group(1))
            txt = tx((re.search(r'<div id="text"[^>]*>(.*?)</div>', h, re.S) or [None, ""])[1] or "")
            cat.append({"id": i, "t": t, "text": txt, "cat": dl.get("カテゴリ", ""), "area": dl.get("エリア", ""), "muki": dl.get("向き", ""), "size": dl.get("写真サイズ", ""), "copy": "©" in h[h.find('id="detail"'):h.find('id="cart"')]})
        except Exception as e: print("ERR", i, e)
        time.sleep(0.3)
    json.dump(cat, open(os.path.join(out, "catalog.json"), "w"), ensure_ascii=False, indent=1)
    print(len(ids), "件")
else:
    from PIL import Image
    pw = int(os.environ.get("PW", "960"))
    for i in sys.argv[3:]:
        try:
            im = Image.open(io.BytesIO(get(B.replace("/photo/", "") + f"/lsc/api/photo/?src={i}"))).convert("RGB")
            print(i, im.size)
            if im.width > pw: im = im.resize((pw, round(im.height * pw / im.width)), Image.LANCZOS)
            im.save(os.path.join(out, f"h{i}.jpg"), quality=82)
        except Exception as e: print("ERR", i, e)
        time.sleep(0.4)
