"""開店・閉店ニュースに1件ずつ足す（月の毎晩 21:20 の回が「速報の種」の新しい行から使う）。
同じ公式の発表（u）と同じ名前（n）の物は足さない。日付が過ぎた閉店・30日より前の開店は足さない。
使い方: python3 tools/kaiten/add.py kansai '{"d":"2026-11-20","k":"open","p":"大阪","n":"店の名前","pt":"新しい点","pl":"場所","tm":"時間","u":"https://..."}' [もう1件 ...]
足したら python3 tools/kaiten/build.py を回す（毎朝 08:30 の link-stats でも作り直す）。"""
import datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
area, rows = sys.argv[1], sys.argv[2:]
PREFS = {"kansai": {"大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"}}[area]
p = os.path.join(HERE, area + ".json")
j = json.load(open(p, encoding="utf-8"))
have = {(x["u"], x["n"]) for x in j["items"]}
today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date()
added = 0
for r in rows:
    x = json.loads(r)
    for k in ("d", "k", "p", "n", "pt", "pl", "u"):
        assert x.get(k), f"{k} が無い: {r}"
    assert x["k"] in ("open", "pop", "close"), x["k"]
    assert x["p"] in PREFS, "府県: " + x["p"]
    assert x["u"].startswith("https://"), "公式の発表のURL: " + x["u"]
    d = datetime.date.fromisoformat(x["d"])
    if (x["u"], x["n"]) in have or (x["k"] == "close" and d < today) or (d - today).days < -30:
        print("足さない:", x["n"]); continue
    x.setdefault("tm", ""); x["added"] = today.isoformat()
    j["items"].append(x); have.add((x["u"], x["n"])); added += 1
json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("足した", added, "件・全部", len(j["items"]), "件")
