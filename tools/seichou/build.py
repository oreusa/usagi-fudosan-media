"""成長の帳面（stats/seichou.md）を作る。11/11 オーナー「誰も真似出来ない、追いつけない仕組み。勝つ方法は技術と追いつけない成長」。
毎朝、①全ページを採点（外から来た人・前の週とのくらべ・相談へ押された数）②週の実験の答え合わせ ③いちばん弱い所と次の一手 を自動で書く。
月・燈・夜は、毎回この帳面を最初に読み、「次の一手」から1つだけやる。新しい事を始める時は tools/seichou/jikken.json に1行足す。
元：stats/link-30.json（毎朝 link-stats が保存。自分たちと機械は外した後の数）と stats/funnel.json。
使い方：python3 tools/seichou/build.py 2026-11-11"""
import json, os, sys
from datetime import date, timedelta
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
rows = json.load(open(os.path.join(ROOT, "stats", "link-30.json"), encoding="utf-8")).get("by_day", [])
try: funnel = json.load(open(os.path.join(ROOT, "stats", "funnel.json"), encoding="utf-8"))
except Exception: funnel = {}
jk = json.load(open(os.path.join(HERE, "jikken.json"), encoding="utf-8"))
d7 = (today - timedelta(days=7)).isoformat(); d14 = (today - timedelta(days=14)).isoformat()
have = sorted({r["day"] for r in rows}); first = have[0] if have else today.isoformat()
ASK = ("相談", "申し込み", "見積り")

# ① ページの採点
pg = {}
def P(n): return pg.setdefault(n, {"v7": 0, "e7": 0, "e_prev": 0, "ask7": 0, "v30": 0})
for r in rows:
    k, n, day = r.get("k", ""), int(r.get("n", 0) or 0), r.get("day", "")
    if k.startswith("表示："):
        ext = k.endswith("（外から）"); name = k[3:].replace("（外から）", "")
        p = P(name); p["v30"] += n
        if day > d7:
            p["v7"] += n; p["e7"] += n if ext else 0
        elif day > d14 and ext: p["e_prev"] += n
    elif k.startswith("クリック：") and day > d7 and any(w in k for w in ASK):
        P(k[5:].split("｜")[0])["ask7"] += n
def mark(p):
    if p["v7"] == 0: return "動いていない"
    if p["e7"] >= 3 and p["e7"] > p["e_prev"]: return "伸びている"
    if p["e7"] < p["e_prev"]: return "落ちた"
    if p["e7"] == 0: return "外から0"
    return "横ばい"
tbl = sorted(pg.items(), key=lambda x: (-x[1]["e7"], -x[1]["v7"]))
L = [f"# 成長の帳面（{today.isoformat()} 朝）", "",
     "毎朝、機械が作り直します。月・燈・夜は毎回これを最初に読み、「次の一手」から1つだけやります。",
     "数は自分たちと機械を外した後の物です。調べの回が押した分は分けられないので、小さい数は「未確認」と読みます。", ""]

# ② 週の実験の答え合わせ
L += ["## 週の実験（答え合わせ）", "", "| 実験 | 合格の線 | 今の数 | 結果 |", "|---|---|---|---|"]
# 投稿の型：?f= の印ごとに、HPへ来た人
sns = {}
for r in rows:
    k, n, day = r.get("k", ""), int(r.get("n", 0) or 0), r.get("day", "")
    if k.startswith("来訪：SNS｜"):
        t = sns.setdefault("-".join(k.split("｜", 1)[1].split("-")[:2]), [0, 0])  # th-rank-1111a → th-rank
        if day > d7: t[0] += n
        elif day > d14: t[1] += n
def smark(a, b): return "伸びている" if a >= 5 and a > b * 1.3 else ("落ちた" if b >= 5 and a < b * 0.7 else ("0" if a == 0 else "横ばい"))
SNS_ROWS = [f"| {f}{'' if '-' in f else '（型なし）'} | {a} | {b} | {smark(a, b)} |" for f, (a, b) in sorted(sns.items(), key=lambda x: -x[1][0]) if a or b] or ["| （まだありません） | 0 | 0 | |"]
res = []
for it in jk["items"]:
    s = date.fromisoformat(it["start"]); e = s + timedelta(days=it["days"])
    got = sum(int(r.get("n", 0) or 0) for r in rows if s.isoformat() <= r.get("day", "") < e.isoformat() and any(r.get("k", "").startswith(k) for k in it["keys"]))
    left = (e - today).days
    st = "合格" if got >= it["pass"] else (f"計測中（あと{left}日）" if left > 0 else "不合格")
    res.append({"id": it["id"], "got": got, "pass": it["pass"], "status": st})
    L.append(f"| {it['what']} | {it['days']}日で{it['pass']} | {got} | {st} |")
L += ["", "- 合格：同じ型をもう1つ増やす（次の実験を1行足す）。", "- 不合格：理由を1行書いて、直すかやめるかを日曜の会議で決める。直すなら新しい実験として1行足す。", "- 計測中の実験が4つある時は、新しい実験を足さない（どれが効いたか分からなくなるため）。", ""]

# ③ いちばん弱い所と次の一手
f7 = funnel.get("7", {})
ext7 = sum(p["e7"] for p in pg.values()); extp = sum(p["e_prev"] for p in pg.values())
steps = [("外から来た人", ext7), ("申し込みページを開いた", f7.get("申し込みページを開いた", 0)), ("書きはじめた", f7.get("書きはじめた", 0)), ("送信した（反響）", f7.get("送信した（反響）", 0))]
PLAY = {"来る人が少ない": "外から人が来ているページの型（下の表で「伸びている」）をもう1つ作る。伸びる時間の投稿（朝7時・夜8時）の2本目を、そのページに向ける。",
        "申し込みまで来ない": "見られているのに相談へ押されないページ（下の表で、見た数が多く「相談へ」が0）に、そのページの言葉で相談の入口を1つ足す。",
        "書きはじめない": "申し込みの最初の問いを軽くする（選ぶだけ・名前は後）。夜の調べ（指示97）の結果を読んでから1つだけ変える。",
        "送信しない": "入力の数を減らす。どの問いで止まったか（申し込み｜次へ｜n）を見て、止まった問いを1つ直す。"}
if ext7 < 150: weak = "来る人が少ない"
elif steps[1][1] * 20 < ext7: weak = "申し込みまで来ない"
elif steps[2][1] * 5 < steps[1][1]: weak = "書きはじめない"
else: weak = "送信しない"
L += ["## いちばん弱い所と次の一手", "", "| 段 | この7日 |", "|---|---|"] + [f"| {n} | {v} |" for n, v in steps]
L += ["", f"外から来た人は、前の7日は {extp} でした。", "", f"**いちばん弱い所：{weak}**", "", f"次の一手：{PLAY[weak]}", "",
      "（1週間に外から150人より少ない間は、後ろの段を直しても数が小さすぎて効いたか分かりません。まず来る人を増やします。）", ""]
grow = [n for n, p in tbl if mark(p) == "伸びている"]
dead = [n for n, p in tbl if p["v7"] >= 20 and p["e7"] == 0]
noask = [n for n, p in tbl if p["v7"] >= 30 and p["ask7"] == 0 and any(w in n for w in ("街", "不動産", "実家", "地価", "売る前", "診断", "ランキング", "解体"))]
L += ["## 機械が見つけた事", "",
      "- 伸びている（同じ型を増やす）：" + ("・".join(grow) or "なし"),
      "- 中では見られているのに、外から0（題・説明・投稿からの道を直す）：" + ("・".join(dead[:8]) or "なし"),
      "- 不動産の道具なのに、相談へ押されていない（相談の入口を足す）：" + ("・".join(noask[:8]) or "なし"), ""]
L += ["## ページの採点（この7日）", "", "| ページ | 見た数 | 外から | 前の7日の外から | 相談へ | 印 |", "|---|---|---|---|---|---|"]
for n, p in tbl:
    if p["v7"] == 0 and p["v30"] < 5: continue
    L.append(f"| {n} | {p['v7']} | {p['e7']} | {p['e_prev']} | {p['ask7']} | {mark(p)} |")
L += ["", f"数え始めた日：{first}（それより前は数がありません）", "",
      "## 投稿の型（投稿からHPに来た人）", "",
      "投稿の2本目のリンクに付けた印（?f=媒体-型-日付と枠。例 th-rank-1111a・x-kaitai-1111b）を、媒体と型でまとめて、機械が数えます。印が媒体だけ（th・x）の物は「型なし」です。", "",
      "| 印 | この7日 | 前の7日 | 印 |", "|---|---|---|---|"] + SNS_ROWS + ["",
      "- 決まり：投稿からHPへのリンクには必ず「媒体-型-日付と枠」の印を付ける（型は th-rank／th-jikka／th-kaitai／th-odekake／th-hitoeki、X は x-、インスタは ig-）。",
      "- 月曜：いちばん多い型の枠を1つ増やし、2週つづけて0の型は、題と行き先を変えるか、やめる。増やした・やめたを1行で台帳へ。", ""]
open(os.path.join(ROOT, "stats", "seichou.md"), "w", encoding="utf-8").write("\n".join(L))
json.dump({"day": today.isoformat(), "weak": weak, "ext7": ext7, "ext_prev7": extp, "experiments": res, "grow": grow, "ext0": dead, "no_ask": noask, "sns": {f: {"d7": a, "prev7": b} for f, (a, b) in sns.items()},
           "pages": {n: p | {"mark": mark(p)} for n, p in tbl}}, open(os.path.join(ROOT, "stats", "seichou.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L[:60]))
