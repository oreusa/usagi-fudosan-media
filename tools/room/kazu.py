"""楽天ROOM の数字（フォロワー・載っている商品の数・コレクションの数）を、公開ページから毎朝1回写す。
11/12 オーナー「一つ一つ完璧な仕組みにしろ」。ROOM は毎日20件の台本を出しているのに、結果の数字がどこにも無かった。
人（GPT）に写させず、機械が読む。読めなかった日は stats/room-fail.txt に理由を残し、台帳が指令に出す。
使い方: python3 tools/room/kazu.py 2026-11-12 [保存してあるHTML]"""
import datetime, html, json, os, re, sys, urllib.request
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DAY = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
URL = "https://room.rakuten.co.jp/ai_usagichan/items"
ABOUT = "楽天ROOM の数字。tools/room/kazu.py が毎朝、公開ページから写す。rows: {day, follower, items, collections}。同じ日は上書き・120日より前は消す"
OUT = os.path.join(ROOT, "stats", "room.json"); FAIL = os.path.join(ROOT, "stats", "room-fail.txt")


def get():
    if len(sys.argv) > 2: return open(sys.argv[2], encoding="utf-8", errors="ignore").read()
    rq = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36", "Accept-Language": "ja"})
    return urllib.request.urlopen(rq, timeout=30).read().decode("utf-8", "ignore")


def num(t, pats):
    for p in pats:
        m = re.search(p, t)
        if m: return int(m.group(1).replace(",", ""))
    return None


def main():
    if not os.path.exists(OUT): json.dump({"about": ABOUT, "rows": []}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)  # 保存の命令が止まらないよう、必ず置く
    try: raw = get()
    except Exception as e:
        open(FAIL, "w", encoding="utf-8").write(f"{DAY} ROOM のページが開けない：{type(e).__name__} {str(e)[:120]}\n"); print("room: 開けない", e); return
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", raw, flags=re.S)))
    fol = num(t, [r"フォロワー\s*([\d,]+)", r"([\d,]+)\s*フォロワー"]) or num(raw, [r'"followers?(?:_?[Cc]ount)?"\s*:\s*(\d+)'])
    itm = num(t, [r"商品\s*([\d,]+)", r"([\d,]+)\s*商品"]) or num(raw, [r'"items?(?:_?[Cc]ount)?"\s*:\s*(\d+)'])
    col = num(t, [r"コレクション\s*([\d,]+)"])
    if fol is None or itm is None:
        i = t.find("フォロワー")
        open(FAIL, "w", encoding="utf-8").write(f"{DAY} ROOM の数字が読めない（フォロワー {fol}・商品 {itm}）。ページの文：{t[max(0, i - 120):i + 160] if i >= 0 else t[:280]}\n"); print("room: 読めない"); return
    d = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"about": ABOUT, "rows": []}
    lim = (datetime.date.fromisoformat(DAY) - datetime.timedelta(days=120)).isoformat()
    d["rows"] = sorted([r for r in d["rows"] if r["day"] != DAY and r["day"] >= lim] + [{"day": DAY, "follower": fol, "items": itm, "collections": col}], key=lambda r: r["day"])
    json.dump(d, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(FAIL, "w").write("")
    print("room:", DAY, "フォロワー", fol, "商品", itm, "コレクション", col)


if __name__ == "__main__":
    main()
