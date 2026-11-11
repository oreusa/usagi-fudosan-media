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
def item(id, name, num, line, ans, why, val=None): items.append({"id": id, "name": name, "num": num, "line": line, "ans": ans, "why": why, "val": val})
def order(to, id, text, why, kind="作る"): orders.append({"to": to, "item": id, "order": text, "why": why, "kind": kind})
# 合格の線は段にする（届いたら次の段へ上がる。遠すぎる線は、毎日「外れ」と出るだけで次の一手を変えない）
def rung(now, ladder): return next((x for x in ladder if x > now), ladder[-1])
hist = prev.get("hist", {})
def ago(id, days=7):
    """days 日より前でいちばん新しい、その項目の数字（無ければ None）"""
    lim = (today - timedelta(days=days)).isoformat()
    xs = [v for d, v in hist.get(id, []) if d <= lim and v is not None]
    return xs[-1] if xs else None

# 1 HP：ページの型（成長の帳面の採点をそのまま使う）
grow, ext0 = sei.get("grow", []), sei.get("ext0", [])
item("hp", "HPのページ", f"外から {sei.get('ext7', '未確認')}人（前の7日 {sei.get('ext_prev7', '未確認')}人）・伸びているページ {len(grow)}", f"前の週の次の段（週{rung(sei.get('ext_prev7', 0) or 0, [50, 100, 150, 300, 600, 1200])}人）を越える。その次は 週{rung(sei.get('ext7', 0) or 0, [50, 100, 150, 300, 600, 1200])}人（最後は 週1200人＝月40件の相談に要る数）", "当たり" if sei.get("ext7", 0) >= rung(sei.get("ext_prev7", 0) or 0, [50, 100, 150, 300, 600, 1200]) else "外れ", sei.get("weak", ""), sei.get("ext7"))
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
item("post", "投稿の型", "・".join(f"{t} {a}人（前 {b}）" for t, (a, b) in sorted(typ.items(), key=lambda x: -x[1][0])) or "印つきの来訪 0", "1つの型で週10人", "当たり" if best and best[1][0] >= 10 else ("計測中" if not typ else "外れ"), "投稿の2本目からHPに来た人", best[1][0] if best else 0)
if best and best[1][0] >= 5: order("投稿の回", "post", f"いちばん来た型「{best[0]}」の枠を1つ増やし、いちばん来なかった型の枠と入れ替える（本数は増やさない）", f"この7日 {best[1][0]}人")
for t in zero: order("投稿の回", "post", f"型「{t}」は2週つづけて0人。題の付け方と行き先を変える。次の週も0ならやめる", "2週0人")
pn, nn = len(pic["p"][1]), len(pic["n"][1])
pa = pic["p"][0] / pn if pn else 0; na = pic["n"][0] / nn if nn else 0
if pn < 5: pans = "計測中"
else: pans = "当たり" if pa > na * 1.3 else ("外れ" if pa < na * 0.8 else "差なし")
item("pic", "画像つき投稿", f"画像つき {pn}本で {pic['p'][0]}人（1本 {pa:.1f}）・文字だけ {nn}本で {pic['n'][0]}人（1本 {na:.1f}）", "画像つきが文字だけの1.3倍", pans, "media/post/index.json の画像を付けた投稿は、印の最後に p", round(pa, 2))
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
item("city", "市ごとの解体補助ページ", f"{n_city}市・外から {ce}人・上位 " + ("・".join(f"{c} {v[0]}人/相談へ{v[1]}" for c, v in top) or "まだ無し"), "外から 週20人", "当たり" if ce >= 20 else ("計測中" if n_city and ce == 0 and not any(r.get("k", "").startswith("表示：市の解体補助") and r.get("day", "") <= d7 for r in rows) else "外れ"), "検索から来る入口。市を足すほど入口が増える", ce)
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
# 11/12 オーナー「meta だるいからなし」→ 再生数の権限は頼まない。取れている数字（いいね・HPに来た人）で判定する
l_now = sum(int(r.get("likes") or 0) for r in rl[:14]); l_old = sum(int(r.get("likes") or 0) for r in rl[14:28])
per = l_now / max(1, len(rl[:14]))
rans = "計測中" if len(rl) < 28 else ("当たり" if (per >= 1 and l_now > l_old) or ig[0] >= 5 else "外れ")
item("reel", "リール（インスタ）", f"この14本のいいね {l_now}（前の14本 {l_old}）・1本あたり {per:.1f}・フォロワー {fol[0] if fol else '未確認'}人・HPへ {ig[0]}人（前 {ig[1]}）", "1本あたり いいね1 で前より上、か HPへ週5人", rans, "再生数は取らない（11/12 オーナー）。声つきの型（11/12〜）を前の型とくらべる", l_now)
if rans == "外れ": order("リールの回", "reel", "いいねが前の14本より下。出だしの1枚（題の言葉と数字）を、いいねの多かった回の形に寄せる。キャプションの最初の行に、HPのその催しのページへの道（プロフィールのリンク）を書く", f"いいね {l_old}→{l_now}")
if tb: order("リールの回", "reel", f"題材は「{tb[0]}」を先に（1本あたりのいいね {tb[1][0] / max(1, tb[1][1]):.1f}）。同じ題材が3本続いたら次の題材へ", "いいねの多かった題材")

# 6 宿・アフィリエイト（押された数は機械・成果は汐が月曜に写す stats/seika.json）
yado = two(lambda k: k.startswith("宿を開く") or k.startswith("泊まり") or "近くの宿" in k)
sk = seika.get("rows", [])
last = sk[-1] if sk else None
item("aff", "宿・アフィリエイト", f"押された {yado[0]}回（前の7日 {yado[1]}）・成果 {last['hassei'] if last else '未確認'}・確定 {last['kakutei'] if last else '未確認'}・入金 {last['nyukin'] if last else '未確認'}", "成果 月1件", ("当たり" if last and int(last.get("hassei") or 0) > 0 else "外れ") if last else "未確認", "クリックは売上ではない。成果は ASP の画面の数字だけ", yado[0])
if not last or (today - date.fromisoformat(last["day"])).days > 8: order("月の朝", "aff", "月曜に汐が写した楽天・A8・バリューコマースの成果（発生・確定・入金）を stats/seika.json に1行入れる。無ければ汐の指示書に1行足す", "成果が未確認のまま", "数字")
if yado[0] < yado[1] * 0.7 and yado[1] >= 10: order("月の朝", "aff", "宿が押される数が落ちた。いちばん見られているおでかけページの「近くの宿」の位置を、カードのすぐ下に戻す", f"{yado[1]}→{yado[0]}")

# 7 申し込みまでの道
st = {s["name"]: s["n"] for s in sei.get("steps", [])}
_n2 = tot(lambda k: k.startswith("申し込み｜次へ｜2")) + tot(lambda k: k == "申し込み｜かんたん｜表示")  # 連絡先を書く所まで来た人（かんたん相談は最初から連絡先が見える）
if st: st = {k2: v2 for k, v in st.items() for k2, v2 in ([("連絡先の画面まで進んだ", max(_n2, v)), (k, v)] if k == "送信した（反響）" else [(k, v)])}
sent = st.get("送信した（反響）", 0); sent_old = ago("lead_sent")
ln = rung(sent, [1, 3, 10, 20, 40])
item("lead", "申し込み（反響）", "・".join(f"{k} {v}" for k, v in st.items()) or "未確認", f"次の段：送信 {ln}件（その先 月40件＝500万円の線）", "当たり" if sent >= 1 and sent > (sent_old or 0) else "外れ", "テストは stats/tests.json で引いた後の数", sent * 100 + st.get("書きはじめた", 0))
hist.setdefault("lead_sent", []).append([today.isoformat(), sent])
# いちばん人が落ちている段を機械が選び、その段だけを直す指令にする（お金にいちばん近いので、毎朝の1番）
names = list(st.keys()); drop = None
for x, y in zip(names, names[1:]):
    if st[x] >= 10:
        rate = st[y] / st[x]
        if drop is None or rate < drop[2]: drop = (x, y, rate)
FIX = {"申し込みページを開いた": "外から来た人がいちばん多いページ（成長の帳面の上位3つ）の、最初の画面の中に「相談する」への道を1つ置く。言葉はそのページの悩み（売る・解体・片付け）に合わせる",
       "書きはじめた": "申し込みページの最初の画面を「選ぶだけの質問1つ」から始める形にする（名前・電話は最後）。開いてすぐ見える所に「無料・しつこい連絡なし・複数の会社をくらべられる」を1行。スマホ幅で、開く→1つ目を押すまでを通しで確かめる",
       "連絡先の画面まで進んだ": "「お家について」（場所・内容）の画面で止まっている。来たページの市の名前を、場所の欄に先に入れておく。内容は書かなくても進めると分かる言葉にする。次へのボタンを、指の届く下に固定する",
       "送信した（反響）": "どの質問でやめたかを測る印（質問ごとの「答えた」）を足す。いちばん落ちる質問を、任意にするか後ろへ回す。送信の直前に「このあと何が起きるか」を3行で書く"}
if drop:
    order("月の朝", "lead", f"「{drop[0]}」{st[drop[0]]}人 →「{drop[1]}」{st[drop[1]]}人（{drop[2] * 100:.0f}%）が、いちばん人が落ちている段。" + FIX.get(drop[1], "この段の画面を、スマホ幅で通しで見て、迷う所を1つ直す") + "。関西と関東の両方", "お金にいちばん近い段。ここが動かないと、来る人を増やしても反響は0のまま")
else:
    order("月の朝", "lead", "申し込みまでの段の数字が10人に届いていない。先に「外から来る人」を増やす指令（市のページ・HPのページ）をやる", "段をくらべる数がまだ無い")

# 8 担当（汐・凪・雫・夜）— 朝の回が stats/tantou.json に、きのう出た物を1行入れる
# 11/12 担当の出来は、燈が毎晩 notes/gpt-runs.md（akari-auto・公開）に書く ○× の行を機械が読む（人が写す手間を無くす）。夜だけは stats/tantou.json
_gr = os.environ.get("GPT_RUNS", os.path.join(ROOT, "..", "akari-auto", "notes", "gpt-runs.md"))
_rows = {r.get("day"): dict(r) for r in tantou.get("rows", [])}
try:
    for l_ in open(_gr, encoding="utf-8"):
        m_ = re.match(r"- (\d{4}-\d\d-\d\d) (.+)", l_)
        if not m_: continue
        r_ = _rows.setdefault(m_.group(1), {"day": m_.group(1)})
        for seg in m_.group(2).split("｜"):
            for who in ("汐", "凪", "雫"):
                if seg.startswith(who): r_.setdefault(who, seg.count("○"))
except Exception: pass
tantou = {"rows": sorted(_rows.values(), key=lambda r: r.get("day", ""))}
WHO = [w for w in ("汐", "凪", "雫", "夜") if any(w in r for r in tantou["rows"])]
tr = [r for r in tantou.get("rows", []) if r.get("day", "") > d7]
if tr:
    miss = {}
    for r in tr:
        for who in WHO:
            if not r.get(who): miss[who] = miss.get(who, 0) + 1
    item("gpt", "担当（" + "・".join(WHO) + "）", f"{len(tr)}日のうち、出なかった日：" + ("・".join(f"{w} {n}日" for w, n in miss.items()) or "なし"), "出なかった日 0", "当たり" if not miss else "外れ", "指示書どおりに毎日の物が出たか", -sum(miss.values()))
    for w, n in miss.items():
        if n >= 2: order("月の朝", "gpt", f"{w}が{n}日出していない。指示書を半分の長さにして、やる事を1つに絞る。次の週も出なければ、その仕事を機械に移す", "出ない指示書は長すぎるか、難しすぎる")
else:
    item("gpt", "担当（汐・凪・雫・夜）", "未確認", "出なかった日 0", "未確認", "朝の回が stats/tantou.json に入れる")
    order("月の朝", "gpt", "きのう 汐・凪・雫・夜 が出した物（行の数・絵・結果の文書）を確かめ、stats/tantou.json の rows に {day, 汐, 凪, 雫, 夜}（出た＝数、出なかった＝0）を1行足す", "担当の出来を測る数字がまだ無い", "数字")

# 9 楽天ROOM
rm = [r for r in sk if "room" in r]
item("room", "楽天ROOM", f"押された {rm[-1]['room'] if rm else '未確認'}・売れた {rm[-1].get('room_uri', '未確認') if rm else '未確認'}", "週に1つ売れる", "未確認" if not rm else ("当たり" if int(rm[-1].get("room_uri") or 0) > 0 else "外れ"), "機械は毎日20件の台本を出している。結果の数字が無い", int(rm[-1].get("room_uri") or 0) if rm else None)
if not rm: order("月の朝", "room", "汐の月曜の回に「ROOM のクリック数・売上件数」を写す1行を足し、stats/seika.json の同じ行に room・room_uri で入れる", "ROOM の結果が未確認のまま", "数字")

# 学び：答えが変わった項目を帳面に足す
pa_ = {i["id"]: i for i in prev.get("items", [])}
for i in items:
    o = pa_.get(i["id"])
    if o and o["ans"] != i["ans"] and i["ans"] not in ("未確認", "計測中"):
        manabi["rows"].append({"day": today.isoformat(), "item": i["name"], "from": o["ans"], "to": i["ans"], "num": i["num"], "did": [x["order"] for x in prev.get("orders", []) if x["item"] == i["id"]][:2]})
# 数字の歩み（30日ぶん）— 段の線と、やった手の答え合わせに使う
for i in items:
    if i.get("val") is not None:
        h = [x for x in hist.setdefault(i["id"], []) if x[0] != today.isoformat()]; h.append([today.isoformat(), i["val"]]); hist[i["id"]] = h[-30:]
hist["lead_sent"] = [x for n, x in enumerate(hist.get("lead_sent", [])) if x[0] != today.isoformat() or n == len(hist["lead_sent"]) - 1][-30:]
# やった手の答え合わせ：回が stats/yatta.json に {day, item, what} を1行足す → 機械が、やる前の数字を控え、7日後に「効いた・効かなかった」を付けて学びに足す
yatta = load(S("yatta.json"), {"about": "やった手の帳面。回が、指令をやったら {day, item, what} を1行足す（item は hp・post・pic・city・reel・aff・lead・gpt・room）。before・after・result は機械が入れる", "rows": []})
now_val = {i["id"]: i.get("val") for i in items}; name_of = {i["id"]: i["name"] for i in items}
for y in yatta["rows"]:
    if "before" not in y:
        xs = [v for d, v in hist.get(y.get("item"), []) if d <= y.get("day", "")]
        y["before"] = xs[-1] if xs else now_val.get(y.get("item"))
    if "result" not in y and y.get("day", "9") <= d7 and now_val.get(y.get("item")) is not None and y.get("before") is not None:
        y["after"] = now_val[y["item"]]
        y["result"] = "効いた" if y["after"] >= y["before"] * 1.2 and y["after"] - y["before"] >= 1 else "効かなかった"
        manabi["rows"].append({"day": today.isoformat(), "item": name_of.get(y["item"], y["item"]), "id": y["item"], "kind": "手の答え", "what": y["what"], "before": y["before"], "after": y["after"], "result": y["result"]})
ng = {}; ok = {}
for m in manabi["rows"]:
    if m.get("kind") == "手の答え": (ok if m["result"] == "効いた" else ng).setdefault(m["id"], []).append(m["what"])
# 指令の並び：お金に近い順。同じ指令が何日続けて出ているか（＝やられていない日数）を数える。月の朝の「作る」は1日1つなので、1番に印
PRI = ["lead", "city", "hp", "post", "pic", "reel", "aff", "gpt", "room"]
old = {(o["to"], o["item"], o["order"][:24]): o.get("days", 1) for o in prev.get("orders", [])}
same_day = prev.get("day") == today.isoformat()
for o in orders:
    d = old.get((o["to"], o["item"], o["order"][:24]))
    o["days"] = (d if same_day else d + 1) if d else 1
    _w = [y["what"] for y in yatta["rows"] if "result" not in y and y.get("item") == o["item"]]
    if _w: o["wait"] = _w[-3:]
    if ng.get(o["item"]): o["ng"] = ng[o["item"]][-3:]
    if ok.get(o["item"]): o["ok"] = ok[o["item"]][-3:]
orders.sort(key=lambda o: (o["kind"] != "作る", PRI.index(o["item"]) if o["item"] in PRI else 99))
_c = [o for o in orders if o["to"] == "月の朝" and o["kind"] == "作る"]
first = next((o for o in _c if len(o.get("wait", [])) < 2), _c[0] if _c else None)  # 同じ所に答え待ちの手が2つあれば、答えが出るまで次の項目を先に（重ねて変えると、どの手が効いたか分からなくなる）
if first: first["first"] = True
def line(o):
    t = ("【きょうの1つ】" if o.get("first") else ("【数字を入れる】" if o["kind"] == "数字" else "")) + o["order"] + f"（理由：{o['why']}）"
    if o["days"] >= 3: t += f" ！{o['days']}日つづけて出ている＝まだやられていない"
    if o.get("wait"): t += "／答え待ちの手（同じ所を重ねて変えない。足りない所だけ足す）：" + "・".join(o["wait"])
    if o.get("ng"): t += "／前に効かなかった手（くり返さない）：" + "・".join(o["ng"])
    if o.get("ok"): t += "／前に効いた手（同じ型を増やす）：" + "・".join(o["ok"])
    return "- " + t
MARK = {"当たり": "◎", "外れ": "×", "未確認": "？", "計測中": "…", "差なし": "△"}
L = [f"# 学習の台帳（{today.isoformat()} 朝）", "", "機械が毎朝作ります。数字が取れない物は「未確認」。直しただけの物は、ここで「当たり」になるまで済みではありません。", "",
     "| | 項目 | 機械が測った数字 | 合格の線 | 答え |", "|---|---|---|---|---|"]
L += [f"| {MARK.get(i['ans'], '')} | {i['name']} | {i['num']} | {i['line']} | {i['ans']} |" for i in items]
L += ["", "## きょうの指令（動く前に、自分あての行を必ず読む）", ""]
for to in ("月の朝", "投稿の回", "リールの回", "燈"):
    xs = [o for o in orders if o["to"] == to]
    if xs: L += [f"### {to}"] + [line(o) for o in xs] + [""]
def mline(m):
    if m.get("kind") == "手の答え": return f"- {m['day']} {m['item']}：やった手「{m['what']}」→ {m['result']}（{m['before']}→{m['after']}）"
    return f"- {m['day']} {m['item']}：{m['from']}→{m['to']}（{m['num']}）。その前に出ていた指令：{'／'.join(m['did']) or '記録なし'}"
wait = [y for y in yatta["rows"] if "result" not in y]
L += ["## 答え待ちの手（やってから7日で、機械が答えを付ける）", ""] + ([f"- {y['day']} {name_of.get(y['item'], y['item'])}：{y['what']}（やる前 {y.get('before')}）" for y in wait] or ["- ありません（指令をやった回が stats/yatta.json に1行足します）"]) + [""]
L += ["## 学び（手の答え・答えが変わった日）", ""] + ([mline(m) for m in manabi["rows"][-12:]] or ["- まだありません"]) + [""]
open(S("gakushu.md"), "w", encoding="utf-8").write("\n".join(L))
json.dump(yatta, open(S("yatta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "items": items, "orders": orders, "sum": {"sent": sent, "seika": (int(last.get("hassei") or 0) if last else None), "cost": 100000}, "hist": hist}, open(S("gakushu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "about": "きょうの指令。to が自分の行を、動く前に読んでそのままやる。やったら stats/yatta.json の rows に {day, item, what} を1行足す（7日後に機械が効いた・効かなかったを付ける）。ng の手はくり返さない", "orders": orders}, open(S("shirei.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manabi, open(S("manabi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L))
