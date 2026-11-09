# HPのページ型ごとの学び（11/9 オーナー「学習エンジンはしっかり改良・どんどん良くしないと人が来ない」）
# stats/link-30.json の「表示：◯◯（外から）」を、ページ型ごとに この7日／前の7日 でくらべる。
# 増やす型＝外から来ていて伸びている型（同じ型のページを増やす）、直す型＝外から0か減っている型（題・中身・リンクを直す）
import json, os, sys, datetime
R = os.path.dirname(os.path.abspath(__file__)) + "/../"
TYPES = [("入口", ["表示：TOWN NOTE 入口"]), ("おでかけ", ["表示：おでかけリスト", "表示：大阪おでかけリスト", "表示：京都おでかけリスト", "表示：兵庫おでかけリスト", "表示：奈良おでかけリスト", "表示：滋賀おでかけリスト", "表示：和歌山おでかけリスト"]),
         ("1件ページ", ["表示：1件ページ"]), ("イルミ", ["表示：イルミネーション"]), ("紅葉", ["表示：紅葉ライトアップ"]),
         ("不動産リスト", ["表示：不動産リスト"]), ("地価ランキング", ["表示：地価ランキング"]), ("街ページ", ["表示：街ページ"]),
         ("困りごと", ["表示：業者さまページ"]), ("住む街", ["表示：住む街をさがす"])]


def main(today=None):
    d = json.load(open(R + "stats/link-30.json", encoding="utf-8"))
    today = today or max(r["day"] for r in d["by_day"])
    t = datetime.date.fromisoformat(today)
    a0, b0 = (t - datetime.timedelta(days=6)).isoformat(), (t - datetime.timedelta(days=13)).isoformat()
    out = []
    for name, keys in TYPES:
        ext = [k + "（外から）" for k in keys]
        now = sum(r["n"] for r in d["by_day"] if r["k"] in ext and r["day"] >= a0)
        prev = sum(r["n"] for r in d["by_day"] if r["k"] in ext and b0 <= r["day"] < a0)
        allv = sum(r["n"] for r in d["by_day"] if (r["k"] in keys or r["k"] in ext) and r["day"] >= a0)
        out.append({"type": name, "ext7": now, "ext_prev7": prev, "views7": allv})
    up = [o["type"] for o in sorted(out, key=lambda o: -o["ext7"]) if o["ext7"] > 0 and o["ext7"] >= o["ext_prev7"]][:3]
    fix = [o["type"] for o in out if o["views7"] > 0 and (o["ext7"] == 0 or o["ext7"] < o["ext_prev7"])]
    line = f"HPの学び（この7日・外から）：増やす型 {'・'.join(up) or 'なし'}／直す型 {'・'.join(fix) or 'なし'}"
    return {"day": today, "types": out, "up": up, "fix": fix, "line": line}


if __name__ == "__main__":
    r = main(sys.argv[1] if len(sys.argv) > 1 else None)
    json.dump(r, open(R + "stats/hp-learning.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(r["line"])
