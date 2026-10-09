"""うさぎちゃん不動産 学習エンジン（10/09 司令ツキ）

投稿1本ずつの「特徴」と「反応」から、どの特徴が効くかをベイズで推定し、
翌日の方針（増やす・減らす・試す）と仮説の判定を出す。

使い方:
  python3 learning_engine.py rows.json hypotheses.json out.json [YYYY-MM-DD]
    rows.json       : [{id, ch: "twitter"|"threads", jst: "YYYY-MM-DD HH:MM", reach, clicks, replies,
                        tags: {field, kumitate, first, close, region, grain, city, url, trend, len, cta}}]
    hypotheses.json : [{id, dim, treatment, control, status, ...}]（無ければ []）
    out.json        : {median, arms, policy, hypotheses}

点数の決め方:
  score = log((reach + 1) / (その媒体の中央値 + 1))   0 が「ふつう」、+0.69 で2倍、-0.69 で半分
  X は表示（impressions）、Threads は閲覧（views）。送信から24時間たっていない投稿は使わない。
  事前分布 N(0, 0.5^2)。分散は観測値から（最低0.2）。P(良い)＝ふつうより上である確率。
"""
import json, math, random, statistics, sys, datetime

DIMS = ["field", "kumitate", "first", "close", "region", "grain", "url", "trend", "hour", "lenb"]
DIM_JA = {"field": "分野", "kumitate": "組み立て", "first": "1行目の型", "close": "締め", "region": "地域", "grain": "深さ",
          "url": "URLの位置", "trend": "トレンド便乗", "hour": "時刻", "lenb": "長さ"}
PRIOR_M, PRIOR_V = 0.0, 0.25
MIN_N_DECIDE = 5          # これ未満は「まだ分からない」＝試す対象
EXPLORE_SHARE = 0.2       # 1日12本のうち約2本は、まだ試していない型に使う
NO_DOWN = {"region"}      # 地域は「減らす」にしない。弱いのは掘り方が浅いせいかもしれない（10/09 オーナーの指摘）。代わりに取材の偏りを出す
OSAKA_AREAS = ["大阪市北区", "大阪市都島区", "大阪市福島区", "大阪市此花区", "大阪市中央区", "大阪市西区", "大阪市港区", "大阪市大正区",
               "大阪市天王寺区", "大阪市浪速区", "大阪市西淀川区", "大阪市淀川区", "大阪市東淀川区", "大阪市東成区", "大阪市生野区",
               "大阪市旭区", "大阪市城東区", "大阪市鶴見区", "大阪市阿倍野区", "大阪市住之江区", "大阪市住吉区", "大阪市東住吉区",
               "大阪市平野区", "大阪市西成区", "堺市", "豊中市", "吹田市", "高槻市", "茨木市", "枚方市", "寝屋川市", "東大阪市", "八尾市",
               "岸和田市", "和泉市", "箕面市", "池田市", "守口市", "門真市", "摂津市", "松原市", "羽曳野市", "富田林市", "河内長野市",
               "泉佐野市", "大東市", "交野市", "藤井寺市", "高石市", "泉大津市"]


def lenb(n):
    return "〜120字" if n <= 120 else ("121〜250字" if n <= 250 else "251字〜")


def prepare(rows, now):
    out = []
    for r in rows:
        if r.get("ch") not in ("twitter", "threads"):
            continue
        t = datetime.datetime.strptime(r["jst"], "%Y-%m-%d %H:%M")
        if (now - t).total_seconds() < 24 * 3600:
            continue
        tg = dict(r.get("tags") or {})
        tg["hour"] = f"{t.hour:02d}時"
        tg["lenb"] = lenb(int(tg.get("len") or 0))
        tg["trend"] = "便乗" if tg.get("trend") in (True, "便乗") else "通常"
        out.append({**r, "tags": tg})
    return out


def posterior(xs):
    n = len(xs)
    if n == 0:
        return PRIOR_M, PRIOR_V
    v = max(statistics.pvariance(xs) if n > 1 else 0.5, 0.2)
    pv = 1 / (1 / PRIOR_V + n / v)
    pm = pv * (PRIOR_M / PRIOR_V + sum(xs) / v)
    return pm, pv


def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def run(rows, hyps, today):
    now = datetime.datetime.strptime(today, "%Y-%m-%d") + datetime.timedelta(hours=1)
    rows = prepare(rows, now)
    med = {}
    for ch in ("twitter", "threads"):
        v = [r["reach"] for r in rows if r["ch"] == ch]
        med[ch] = statistics.median(v) if v else 0
    for r in rows:
        r["score"] = math.log((r["reach"] + 1) / (med[r["ch"]] + 1))

    arms = []
    for ch in ("all", "twitter", "threads"):
        sub = [r for r in rows if ch == "all" or r["ch"] == ch]
        for d in DIMS:
            for v in sorted({str(r["tags"].get(d)) for r in sub}):
                grp = [r for r in sub if str(r["tags"].get(d)) == v]
                pm, pv = posterior([r["score"] for r in grp])
                arms.append({"ch": ch, "dim": d, "value": v, "n": len(grp), "mean": round(pm, 3),
                             "sd": round(math.sqrt(pv), 3), "x": round(math.exp(pm), 2),
                             "p_better": round(1 - ncdf((0 - pm) / math.sqrt(pv)), 3),
                             "replies": sum(r["replies"] for r in grp), "clicks": sum(r["clicks"] for r in grp)})

    # 方針：トンプソン抽出を200回まわし、各次元で「1位になった割合」を重みにする
    rnd = random.Random(today)
    policy = {"date": today, "dims": {}, "explore": [], "rules": []}
    for d in ["first", "kumitate", "close", "grain", "region", "lenb", "hour"]:
        cand = [a for a in arms if a["ch"] == "all" and a["dim"] == d and a["value"] not in ("その他", "なし", "None")]
        if not cand:
            continue
        wins = {a["value"]: 0 for a in cand}
        for _ in range(200):
            best = max(cand, key=lambda a: rnd.gauss(a["mean"], a["sd"]))
            wins[best["value"]] += 1
        ranked = sorted(cand, key=lambda a: -a["mean"])
        up = [a["value"] for a in ranked if a["n"] >= MIN_N_DECIDE and a["p_better"] >= 0.8]
        down = [] if d in NO_DOWN else [a["value"] for a in ranked if a["n"] >= MIN_N_DECIDE and a["p_better"] <= 0.2]
        unknown = [a["value"] for a in ranked if a["n"] < MIN_N_DECIDE]
        policy["dims"][d] = {"name": DIM_JA[d], "weights": {k: round(v / 200, 2) for k, v in wins.items()},
                             "up": up, "down": down, "unknown": unknown}
        if unknown and d in ("first", "kumitate", "close"):
            policy["explore"].append({"dim": d, "name": DIM_JA[d], "try": unknown[:2]})
    # 取材の偏り：直近14日の投稿で、府県ごとの本数と、大阪府内でまだ一度も深掘りしていない市区
    since = (now - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
    recent = [r for r in rows if r["jst"][:10] >= since]
    pref = {}
    for r in recent:
        k = str(r["tags"].get("region"))
        pref[k] = pref.get(k, 0) + 1
    cities = {}
    for r in rows:
        c = str(r["tags"].get("city") or "")
        if c:
            cities[c] = cities.get(c, 0) + 1
    deep = {str(r["tags"].get("city")) for r in rows if r["tags"].get("grain") in ("町・駅", "区・市")}
    gaps = [a for a in OSAKA_AREAS if a not in deep]
    top_city = sorted(cities.items(), key=lambda kv: -kv[1])[:5]
    policy["coverage"] = {"prefectures_14d": pref, "top_cities": top_city,
                          "osaka_untouched": gaps[:12], "osaka_untouched_count": len(gaps),
                          "note": "地域は減らさない。同じ市は1週間に2本まで。大阪はまだ扱っていない区・市を、町・駅の単位まで深掘りする"}
    # 媒体ごとの時刻
    for ch in ("twitter", "threads"):
        hs = sorted([a for a in arms if a["ch"] == ch and a["dim"] == "hour" and a["n"] >= 3], key=lambda a: -a["mean"])
        policy["dims"][f"hour_{ch}"] = {"name": f"時刻（{'X' if ch == 'twitter' else 'Threads'}）",
                                        "best": [a["value"] for a in hs[:3]], "worst": [a["value"] for a in hs[-3:]]}

    # 仮説の判定：treatment と control の差の事後確率
    judged = []
    for h in hyps:
        if h.get("status") not in ("testing", None):
            judged.append(h)
            continue
        def grp(val):
            return [r["score"] for r in rows if str(r["tags"].get(h["dim"])) == str(val)
                    and (not h.get("since") or r["jst"][:10] >= h["since"])]
        t, c = grp(h["treatment"]), grp(h["control"])
        mt, vt = posterior(t)
        mc, vc = posterior(c)
        p = 1 - ncdf((0 - (mt - mc)) / math.sqrt(vt + vc))
        h = {**h, "n_t": len(t), "n_c": len(c), "effect_x": round(math.exp(mt - mc), 2), "p": round(p, 3)}
        if len(t) >= 6 and len(c) >= 6 and p >= 0.9:
            h["status"], h["decided"] = "adopted", today
        elif len(t) >= 6 and len(c) >= 6 and p <= 0.1:
            h["status"], h["decided"] = "rejected", today
        else:
            h["status"] = "testing"
        judged.append(h)
    policy["rules"] = [f"{DIM_JA.get(h['dim'], h['dim'])}：{h['treatment']}（{h['effect_x']}倍）" for h in judged if h.get("status") == "adopted"]
    return {"median": med, "n": len(rows), "arms": arms, "policy": policy, "hypotheses": judged}


if __name__ == "__main__":
    rows = json.load(open(sys.argv[1], encoding="utf-8"))
    hyps = json.load(open(sys.argv[2], encoding="utf-8")) if len(sys.argv) > 2 else []
    today = sys.argv[4] if len(sys.argv) > 4 else datetime.date.today().isoformat()
    out = run(rows, hyps, today)
    json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    p = out["policy"]
    print("posts", out["n"], "median", out["median"])
    for d, v in p["dims"].items():
        print(v["name"], "増やす:", v.get("up") or v.get("best"), "減らす:", v.get("down") or v.get("worst"), "未知:", v.get("unknown", []))
    print("試す:", p["explore"])
    for h in out["hypotheses"]:
        print("仮説", h["id"], h["status"], h.get("effect_x"), h.get("p"), h.get("n_t"), h.get("n_c"))
