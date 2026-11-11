"""学習の台帳（11/11 オーナー「直して欲しいんじゃない。学習して成長し考えることが出来るシステムを」）。
取り組みの全部を1枚に並べ、項目ごとに ①機械が測った数字 ②合格の線 ③答え（当たり・外れ・未確認）④機械が出す指令 を毎朝作る。
- stats/gakushu.md   人が読む1枚（管制室にも同じ物）
- stats/shirei.json  きょうの指令。月の朝の回・投稿の回・リールの回・燈は、動く前に必ずこれを読み、自分あての指令をそのままやる
- stats/manabi.json  学びの帳面。答えが変わった日（当たり→外れ など）に機械が1行足す。次の回はこれを読み、同じ外れをくり返さない
数字が取れない項目は「未確認」と書き、「取れるようにする」を指令の一番上に出す（計画を実績と書かない）。
使い方：python3 tools/seichou/gakushu.py 2026-11-12"""
import json, os, re, sys
from datetime import date, timedelta
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
S = lambda *p: os.path.join(ROOT, "stats", *p)
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
def load(p, d):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return d
rows = load(S("link-30.json"), {}).get("by_day", [])
sei = load(S("seichou.json"), {}); reels = load(S("reels.json"), {}); seika = load(S("seika.json"), {}); tantou = load(S("tantou.json"), {})
prev = load(S("gakushu.json"), {}); manabi = load(S("manabi.json"), {"about": "学びの帳面。機械が、答えの変わった日に1行足す。消さない", "rows": []})
d7 = (today - timedelta(days=7)).isoformat(); d14 = (today - timedelta(days=14)).isoformat()
def tot(f, a=d7, b="9999"): return sum(int(r.get("n", 0) or 0) for r in rows if a < r.get("day", "") <= b and f(r.get("k", "")))
def two(f): return tot(f), tot(f, d14, d7)
items, orders = [], []
def item(id, name, num, line, ans, why): items.append({"id": id, "name": name, "num": num, "line": line, "ans": ans, "why": why})
def order(to, id, text, why): orders.append({"to": to, "item": id, "order": text, "why": why})

# 1 HP：ページの型（成長の帳面の採点をそのまま使う）
grow, ext0 = sei.get("grow", []), sei.get("ext0", [])
item("hp", "HPのページ", f"外から {sei.get('ext7', '未確認')}人（前の7日 {sei.get('ext_prev7', '未確認')}人）・伸びているページ {len(grow)}", "外から 週150人", "当たり" if sei.get("ext7", 0) >= 150 else "外れ", sei.get("weak", ""))
if grow: order("月の朝", "hp", f"伸びているページ「{grow[0]}」と同じ型のページを1つ足す", "外から来る人が前の週より増えた型")
if ext0: order("月の朝", "hp", f"「{ext0[0]}」の題と説明文を、探す人の言葉に直す", "中では見られているのに外から0")
if sei.get("play"): order("月の朝", "hp", sei["play"], "いちばん弱い所：" + sei.get("weak", ""))

# 2 投稿の型（?f=媒体-型-日付と枠）と、3 画像つき（枠の最後に p）
typ, pic = {}, {"p": [0, set()], "n": [0, set()]}
for r in rows:
    k, n, day = r.get("k", ""), int(r.get("n", 0) or 0), r.get("day", "")
    if not k.startswith("来訪：SNS｜"): continue
    f = k.split("｜", 1)[1]; parts = f.split("-")
    if len(parts) < 3: continue
    t = typ.setdefault(parts[1], [0, 0])
    if day > d7: t[0] += n
    elif day > d14: t[1] += n
    if day > d7:
        g = pic["p" if parts[2].endswith("p") else "n"]; g[0] += n; g[1].add(f)
best = max(typ.items(), key=lambda x: x[1][0], default=None)
zero = [t for t, (a, b) in typ.items() if a == 0 and b == 0]
item("post", "投稿の型", "・".join(f"{t} {a}人（前 {b}）" for t, (a, b) in sorted(typ.items(), key=lambda x: -x[1][0])) or "印つきの来訪 0", "1つの型で週10人", "当たり" if best and best[1][0] >= 10 else ("計測中" if not typ else "外れ"), "投稿の2本目からHPに来た人")
if best and best[1][0] >= 5: order("投稿の回", "post", f"いちばん来た型「{best[0]}」の枠を1つ増やし、いちばん来なかった型の枠と入れ替える（本数は増やさない）", f"この7日 {best[1][0]}人")
for t in zero: order("投稿の回", "post", f"型「{t}」は2週つづけて0人。題の付け方と行き先を変える。次の週も0ならやめる", "2週0人")
pn, nn = len(pic["p"][1]), len(pic["n"][1])
pa = pic["p"][0] / pn if pn else 0; na = pic["n"][0] / nn if nn else 0
if pn < 5: pans = "計測中"
else: pans = "当たり" if pa > na * 1.3 else ("外れ" if pa < na * 0.8 else "差なし")
item("pic", "画像つき投稿", f"画像つき {pn}本で {pic['p'][0]}人（1本 {pa:.1f}）・文字だけ {nn}本で {pic['n'][0]}人（1本 {na:.1f}）", "画像つきが文字だけの1.3倍", pans, "media/post/index.json の画像を付けた投稿は、印の最後に p")
order("投稿の回", "pic", {"当たり": "全部の枠に画像を付ける", "外れ": "画像をやめ、画像の枠を「いちばん来た型」に回す", "差なし": "画像は朝7時だけ残す（作る手間を減らす）"}.get(pans, "朝7時と夜8時の投稿の1本目に、送り先のページと同じ行の画像（media/post/index.json の url）を付け、2本目のリンクの印の最後に p を付ける。ほかの枠は文字だけのまま（くらべるため）"), "画像あり・なしをくらべる")

# 4 市ごとの補助ページ
city = {}
for r in rows:
    k, n, day = r.get("k", ""), int(r.get("n", 0) or 0), r.get("day", "")
    if day <= d7: continue
    m = re.match(r"表示：市の解体補助 (.+?)（外から）$", k)
    if m: city.setdefault(m.group(1), [0, 0])[0] += n
    m = re.match(r"クリック：市の解体補助｜(.+?)｜", k)
    if m: city.setdefault(m.group(1), [0, 0])[1] += n
ce = tot(lambda k: k.startswith("表示：市の解体補助") and k.endswith("（外から）"))
top = sorted(city.items(), key=lambda x: (-x[1][0], -x[1][1]))[:3]
n_city = len([f for f in os.listdir(os.path.join(ROOT, "links")) if re.match(r"kaitai-.+\.html$", f)])
item("city", "市ごとの解体補助ページ", f"{n_city}市・外から {ce}人・上位 " + ("・".join(f"{c} {v[0]}人/相談へ{v[1]}" for c, v in top) or "まだ無し"), "外から 週20人", "当たり" if ce >= 20 else ("計測中" if n_city and ce == 0 and not any(r.get("k", "").startswith("表示：市の解体補助") and r.get("day", "") <= d7 for r in rows) else "外れ"), "検索から来る入口。市を足すほど入口が増える")
if ce >= 20: order("月の朝", "city", f"市を1日3つ足す（汐の帳面の順。いちばん来た「{top[0][0]}」と同じ府県を先に）。関東も同じ型で作る", "当たり：入口が効いている")
elif top and top[0][1][0] > 0: order("月の朝", "city", f"いちばん来た「{top[0][0]}」のページの題・見出しの形を、ほかの市のページにも揃える。市は1日1つ足す", "来ている市と来ない市の差を型にする")
else: order("月の朝", "city", "市は1日1つ足す。7日たっても外から0なら、題を「◯◯市 解体 補助金 2026 いくら」の形に変える", "まだ数が無い")

# 5 リール（インスタ）
rl = reels.get("reels", []) if isinstance(reels, dict) else []
rec = [r for r in rl if r.get("at", "")[:10] > d7[:10]] if rl and len(rl[0].get("at", "")) > 6 else rl[:14]
rec = rl[:14]
views = [r["views"] for r in rec if r.get("views") is not None]
likes = sum(int(r.get("likes") or 0) for r in rec)
THEME = {"紅葉": ("紅葉", "もみじ", "赤", "色づ"), "光": ("光", "イルミ", "灯", "ライト"), "催し": ("フェス", "市", "展", "祭"), "花・自然": ("バラ", "コスモス", "ススキ", "花")}
th = {}
for r in rl[:40]:
    for name, ws in THEME.items():
        if any(w in r.get("title", "") for w in ws):
            t = th.setdefault(name, [0, 0]); t[0] += int(r.get("likes") or 0); t[1] += 1; break
tb = max(th.items(), key=lambda x: x[1][0] / max(1, x[1][1]), default=None)
fol = list((reels.get("followers") or {}).values())[-1:] if isinstance(reels, dict) else []
ig = two(lambda k: k.startswith("来訪：SNS｜ig"))
item("reel", "リール（インスタ）", f"再生 {'未確認' if not views else sum(views)}・この14本のいいね {likes}・フォロワー {fol[0] if fol else '未確認'}人・HPへ {ig[0]}人（前 {ig[1]}）", "1本の再生 300回・HPへ週5人", "未確認" if not views else ("当たり" if sum(views) / len(views) >= 300 else "外れ"), "声つきの型（11/12〜）を前の型とくらべる")
if not views: order("月の朝", "reel", "再生数の権限（instagram_manage_insights）が無い。オーナーへの「今やること」に、権限を付け直す手順とURLを出す", "再生が見えないと、型の当たり外れが分からない")
if tb: order("リールの回", "reel", f"題材は「{tb[0]}」を先に（1本あたりのいいね {tb[1][0] / max(1, tb[1][1]):.1f}）。同じ題材が3本続いたら次の題材へ", "いいねの多かった題材")

# 6 宿・アフィリエイト（押された数は機械・成果は汐が月曜に写す stats/seika.json）
yado = two(lambda k: k.startswith("宿を開く") or k.startswith("泊まり") or "近くの宿" in k)
sk = seika.get("rows", [])
last = sk[-1] if sk else None
item("aff", "宿・アフィリエイト", f"押された {yado[0]}回（前の7日 {yado[1]}）・成果 {last['hassei'] if last else '未確認'}・確定 {last['kakutei'] if last else '未確認'}・入金 {last['nyukin'] if last else '未確認'}", "成果 月1件", ("当たり" if last and int(last.get("hassei") or 0) > 0 else "外れ") if last else "未確認", "クリックは売上ではない。成果は ASP の画面の数字だけ")
if not last or (today - date.fromisoformat(last["day"])).days > 8: order("月の朝", "aff", "月曜に汐が写した楽天・A8・バリューコマースの成果（発生・確定・入金）を stats/seika.json に1行入れる。無ければ汐の指示書に1行足す", "成果が未確認のまま")
if yado[0] < yado[1] * 0.7 and yado[1] >= 10: order("月の朝", "aff", "宿が押される数が落ちた。いちばん見られているおでかけページの「近くの宿」の位置を、カードのすぐ下に戻す", f"{yado[1]}→{yado[0]}")

# 7 申し込みまでの道
st = {s["name"]: s["n"] for s in sei.get("steps", [])}
item("lead", "申し込み（反響）", "・".join(f"{k} {v}" for k, v in st.items()) or "未確認", "反響 月40件（500万円の線）", "当たり" if st.get("送信した（反響）", 0) >= 10 else "外れ", "テストは stats/tests.json で引いた後の数")

# 8 担当（汐・凪・雫・夜）— 朝の回が stats/tantou.json に、きのう出た物を1行入れる
tr = [r for r in tantou.get("rows", []) if r.get("day", "") > d7]
if tr:
    miss = {}
    for r in tr:
        for who in ("汐", "凪", "雫", "夜"):
            if not r.get(who): miss[who] = miss.get(who, 0) + 1
    item("gpt", "担当（汐・凪・雫・夜）", f"{len(tr)}日のうち、出なかった日：" + ("・".join(f"{w} {n}日" for w, n in miss.items()) or "なし"), "出なかった日 0", "当たり" if not miss else "外れ", "指示書どおりに毎日の物が出たか")
    for w, n in miss.items():
        if n >= 2: order("月の朝", "gpt", f"{w}が{n}日出していない。指示書を半分の長さにして、やる事を1つに絞る。次の週も出なければ、その仕事を機械に移す", "出ない指示書は長すぎるか、難しすぎる")
else:
    item("gpt", "担当（汐・凪・雫・夜）", "未確認", "出なかった日 0", "未確認", "朝の回が stats/tantou.json に入れる")
    order("月の朝", "gpt", "きのう 汐・凪・雫・夜 が出した物（行の数・絵・結果の文書）を確かめ、stats/tantou.json の rows に {day, 汐, 凪, 雫, 夜}（出た＝数、出なかった＝0）を1行足す", "担当の出来を測る数字がまだ無い")

# 9 楽天ROOM
rm = [r for r in sk if "room" in r]
item("room", "楽天ROOM", f"押された {rm[-1]['room'] if rm else '未確認'}・売れた {rm[-1].get('room_uri', '未確認') if rm else '未確認'}", "週に1つ売れる", "未確認" if not rm else ("当たり" if int(rm[-1].get("room_uri") or 0) > 0 else "外れ"), "機械は毎日20件の台本を出している。結果の数字が無い")
if not rm: order("月の朝", "room", "汐の月曜の回に「ROOM のクリック数・売上件数」を写す1行を足し、stats/seika.json の同じ行に room・room_uri で入れる", "ROOM の結果が未確認のまま")

# 学び：答えが変わった項目を帳面に足す
pa_ = {i["id"]: i for i in prev.get("items", [])}
for i in items:
    o = pa_.get(i["id"])
    if o and o["ans"] != i["ans"] and i["ans"] not in ("未確認", "計測中"):
        manabi["rows"].append({"day": today.isoformat(), "item": i["name"], "from": o["ans"], "to": i["ans"], "num": i["num"], "did": [x["order"] for x in prev.get("orders", []) if x["item"] == i["id"]][:2]})
MARK = {"当たり": "◎", "外れ": "×", "未確認": "？", "計測中": "…", "差なし": "△"}
L = [f"# 学習の台帳（{today.isoformat()} 朝）", "", "機械が毎朝作ります。数字が取れない物は「未確認」。直しただけの物は、ここで「当たり」になるまで済みではありません。", "",
     "| | 項目 | 機械が測った数字 | 合格の線 | 答え |", "|---|---|---|---|---|"]
L += [f"| {MARK.get(i['ans'], '')} | {i['name']} | {i['num']} | {i['line']} | {i['ans']} |" for i in items]
L += ["", "## きょうの指令（動く前に、自分あての行を必ず読む）", ""]
for to in ("月の朝", "投稿の回", "リールの回", "燈"):
    xs = [o for o in orders if o["to"] == to]
    if xs: L += [f"### {to}"] + [f"- {o['order']}（理由：{o['why']}）" for o in xs] + [""]
L += ["## 学び（答えが変わった日）", ""] + ([f"- {m['day']} {m['item']}：{m['from']}→{m['to']}（{m['num']}）。その前にやった事：{'／'.join(m['did']) or '記録なし'}" for m in manabi["rows"][-12:]] or ["- まだありません（答えが変わった日に、機械が1行足します）"]) + [""]
open(S("gakushu.md"), "w", encoding="utf-8").write("\n".join(L))
json.dump({"day": today.isoformat(), "items": items, "orders": orders}, open(S("gakushu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "about": "きょうの指令。to が自分の行を、動く前に読んでそのままやる。やったら PR の題か報告に item の名前を書く", "orders": orders}, open(S("shirei.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manabi, open(S("manabi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L))
