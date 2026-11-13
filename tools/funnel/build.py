"""反響までの道を数える（11/11 経営方針：いちばん大事な数字は反響の数）。
stats/link-30.json（毎朝 link-stats が保存）から、7日と30日の「来た→不動産の道具→申し込みページ→書きはじめ→送信」を
stats/funnel.md と stats/funnel.json に書く。数は自分たち（?owner=1・機械）を外した後の物。それでも調べの回が混ざる日は「未確認」と読む。
使い方：python3 tools/funnel/build.py 2026-11-11"""
import json, os, sys
from datetime import date, timedelta

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
rows = json.load(open(os.path.join(ROOT, "stats", "link-30.json"), encoding="utf-8")).get("by_day", [])
# 11/11 自分たちのテスト（stats/tests.json）を引く。お客さんの数と混ぜない
try:
    TESTS = json.load(open(os.path.join(ROOT, "stats", "tests.json"), encoding="utf-8")).get("rows", [])
except Exception:
    TESTS = []
rows = rows + [{"day": t["day"], "k": t["k"], "n": -int(t.get("n", 0))} for t in TESTS]

STEPS = [
    ("外から来た人", lambda k: k.startswith("表示：") and "（外から）" in k),
    ("不動産の道具を見た", lambda k: k.startswith("表示：") and "（外から）" not in k and any(w in k for w in ("街", "不動産", "実家", "診断", "地価", "売る前"))),
    ("申し込みページを開いた", lambda k: k.startswith("表示：お申し込み")),
    ("書きはじめた", lambda k: k == "申し込み｜書きはじめ"),
    ("送信した（反響）", lambda k: k == "申し込み｜送信"),
]


def count(days):
    since = (today - timedelta(days=days)).isoformat()
    out = [0] * len(STEPS)
    src = {}
    for r in rows:
        if r.get("day", "") <= since:
            continue
        k, n = r.get("k", ""), int(r.get("n", 0) or 0)
        for i, (_, f) in enumerate(STEPS):
            if f(k):
                out[i] += n
        if k.startswith("クリック：") and ("相談" in k or "申し込み" in k or "見積り" in k):
            p = k.split("｜")[0].replace("クリック：", "")
            src[p] = src.get(p, 0) + n
    return out, sorted(src.items(), key=lambda x: -x[1])[:6]


res = {}
lines = [f"# 反響までの道（{today.isoformat()} 朝）", "", "数は自分たちと機械を外した後。調べの回が押した分は分けられないので、送信の数だけは必ずメールと合わせて確かめる。", ""]
for d in (7, 30):
    c, src = count(d)
    res[str(d)] = {STEPS[i][0]: c[i] for i in range(len(STEPS))} | {"申し込みへ押された元": src}
    lines += [f"## この{d}日", "", "| 段 | 数 | 前の段から |", "|---|---|---|"]
    for i, (name, _) in enumerate(STEPS):
        rate = "" if i < 2 or not c[i - 1] else f"{round(100 * c[i] / c[i - 1])}%"
        lines.append(f"| {name} | {c[i]} | {rate} |")
    lines += ["", "申し込み・相談へ押された元：" + ("・".join(f"{p} {n}" for p, n in src) or "なし"), ""]
c7 = res["7"]
weak = "申し込みページを開いた人が書きはじめない" if c7["申し込みページを開いた"] >= 5 and c7["書きはじめた"] * 5 < c7["申し込みページを開いた"] else (
    "申し込みページまで来る人が少ない" if c7["申し込みページを開いた"] < 5 else "書きはじめた人が送信しない")
res["いちばん細い所"] = weak
# 11/13 どの欄で止まるか（moushikomi.html の 欄・止まった・離れた・送信を押した。7日）
_since = (today - timedelta(days=7)).isoformat()
_f = {}
for r in rows:
    k = r.get("k", "")
    if r.get("day", "") > _since and (k.startswith("申し込み｜欄｜") or k.startswith("申し込み｜止まった｜") or k.startswith("申し込み｜離れた｜") or k == "申し込み｜送信を押した"):
        _f[k.replace("申し込み｜", "")] = _f.get(k.replace("申し込み｜", ""), 0) + int(r.get("n", 0) or 0)
res["欄ごと"] = _f
lines += [f"**いちばん細い所（この7日）：{weak}**", ""]
lines += ["どの欄で止まるか（7日・11/13 から測る）：" + ("・".join(f"{k} {n}" for k, n in sorted(_f.items(), key=lambda x: -x[1])[:12]) or "まだ数が無い"), ""]
if TESTS:
    lines += ["引いたテスト：" + "・".join(f'{t["day"][5:]} {t["k"]} {t["n"]}（{t.get("who", "")}）' for t in TESTS), ""]
# 11/11 お金の段階（オーナー：クリックを売上と混ぜない。費用は毎月10万円）
try:
    asp = json.load(open(os.path.join(ROOT, "tools", "asp.json"), encoding="utf-8")).get("asp", [])
except Exception:
    asp = []
lines += ["## お金の段階", "", "毎月の費用：10万円（毎月10日）。成果・確定・入金は ASP の画面の数字だけを書く（無ければ未確認。クリックは売上ではない）。", "",
          "| ASP | 状態 | 使い道 |", "|---|---|---|"]
lines += [f'| {a.get("name", "")} | {a.get("state", "")} | {a.get("use", "")} |' for a in asp]
lines += ["", "| 段 | 数 |", "|---|---|", "| 成果（発生） | 未確認 |", "| 確定 | 未確認 |", "| 入金 | 未確認 |", ""]
open(os.path.join(ROOT, "stats", "funnel.md"), "w", encoding="utf-8").write("\n".join(lines))
json.dump(res, open(os.path.join(ROOT, "stats", "funnel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(lines))
