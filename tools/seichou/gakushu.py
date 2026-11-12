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
# 作る機械が止まっていないか（11/12 /kaitai の作り直しが点検で止まり、link-stats ごと止まって数字が1日入らなかった）
try: _bf = [l.strip() for l in open(S("build-fail.txt"), encoding="utf-8") if l.strip()]
except Exception: _bf = []
if _bf: order("月の朝", "hp", "【きょうの1つより先】ページを作る機械が止まっている：" + "／".join(_bf) + "。手元で同じ命令を回して原因を直す（止まったページは古いまま出ている）", "止まった仕組みはその日に直す")
item("hp", "HPのページ", f"外から {sei.get('ext7', '未確認')}人（前の7日 {sei.get('ext_prev7', '未確認')}人）・伸びているページ {len(grow)}", f"前の週の次の段（週{rung(sei.get('ext_prev7', 0) or 0, [50, 100, 150, 300, 600, 1200])}人）を越える。その次は 週{rung(sei.get('ext7', 0) or 0, [50, 100, 150, 300, 600, 1200])}人（最後は 週1200人＝月40件の相談に要る数）", "当たり" if sei.get("ext7", 0) >= rung(sei.get("ext_prev7", 0) or 0, [50, 100, 150, 300, 600, 1200]) else "外れ", sei.get("weak", ""), sei.get("ext7"))
# 足した型の答え合わせ（tools/seichou/tashita.json）。7日で答え。答え待ちが2つある間は、新しく足さない（どれが効いたか分からなくなる）
_ts = load(os.path.join(ROOT, "tools", "seichou", "tashita.json"), {}).get("rows", [])
_tw, _ta, _tx = [], [], []
for _r in _ts:
    _age = (today - date.fromisoformat(_r["day"])).days
    _e = sum(int(r.get("n", 0) or 0) for r in rows if r.get("day", "") > _r["day"] and r.get("k", "") == "表示：" + _r["name"] + "（外から）")
    (_tw if _age < 7 else (_ta if _e >= 3 else _tx)).append((_r, _e, _age))
if _ts:
    item("kata-tasu", "足した型のページ", "・".join(f"{r['name']} 外から{e}人（{a}日目）" for r, e, a in _tw + _ta + _tx), "足して7日で 外から3人", "当たり" if _ta else ("外れ" if _tx and not _tw else "計測中"), "伸びた型をまねて足し、効いた作りだけ増やす", sum(e for _, e, _ in _tw + _ta + _tx))
    for r, e, a in _ta[:1]: order("月の朝", "kata-tasu", f"足したページ「{r['name']}」に外から {e}人。同じ作り（同じ表から、探す言葉で切り出す）をもう1つ足し、tools/seichou/tashita.json に1行", "当たり：まねた作りが効いた")
    for r, e, a in _tx[:1]: order("月の朝", "kata-tasu", f"足したページ「{r['name']}」は7日で外から {e}人。この作りはもう足さない。別の伸びている型（{'・'.join(grow[:3])}）から、ちがう切り出し方で1つ足す", "外れ：作りを変える")
if grow and len(_tw) < 2: order("月の朝", "hp", f"伸びているページ「{grow[0]}」と同じ型のページを1つ足し、tools/seichou/tashita.json に1行（答え待ち {len(_tw)}）", "外から来る人が前の週より増えた型")
# 1件ページの中身（11/12：題はもう探す人の言葉。足りないのは時間・料金・駐車場＝公式から1日5件足す。tools/odekake_more.json）
_mr = load(os.path.join(ROOT, "tools", "odekake_more.json"), {}).get("rows", {})
_sp = []
try:
    for _f in sorted(os.listdir(os.path.join(ROOT, "links", "o"))):
        _h = open(os.path.join(ROOT, "links", "o", _f), encoding="utf-8").read()
        _m = re.search(r"<h1>(.*?)<span>", _h)
        if _m: _sp.append((re.sub(r"\s+", "", _m.group(1)), _m.group(1), "<span>時間</span>" in _h or "<span>料金</span>" in _h))
except Exception: pass
if _sp:
    _done = [x for x in _sp if x[2]]; _seen = {re.sub(r"\s+", "", k) for k in _mr}
    _todo = [x for x in _sp if x[0] not in _seen]
    _hot = sorted(_todo, key=lambda x: (0 if re.search("イルミ|ライトアップ|紅葉|初詣|光", x[1]) else 1, -tot(lambda k, n=x[1]: k == "表示：1件ページ｜" + n)))[:5]
    _lastm = max([v.get("day", "") for v in _mr.values()] or [""])
    _gm = (today - date.fromisoformat(_lastm)).days if _lastm else 99
    _e1 = (sei.get("pages", {}).get("1件ページ", {}) or {}).get("e7", 0)
    item("spot-more", "1件ページの中身（時間・料金・駐車場）", f"{len(_sp)}件のうち 時間か料金つき {len(_done)}件・まだ調べていない {len(_todo)}件・最後に足した日 {_lastm[5:] or 'なし'}・外から {_e1}人/週", "1日5件足す・外から 週10人", "当たり" if _e1 >= 10 else ("外れ" if _gm >= 2 and _todo else "計測中"), "題は探す人の言葉になっている。足りないのは、探す人が知りたい中身", len(_done))
    if _todo: order("月の朝", "spot-more", "1件ページに、公式ページの通りの 時間・料金・駐車場 を足す（tools/odekake_more.json）。きょうの5件：" + "・".join(x[1] for x in _hot) + "。公式に無ければ nashi:true で残す", "中では見られているのに外から0。題は直っている" + ("。！" + str(_gm) + "日 足していない" if _gm >= 2 else ""))
if ext0 and ext0[0] != "1件ページ": order("月の朝", "hp", f"「{ext0[0]}」の題と説明文を、探す人の言葉に直す", "中では見られているのに外から0")
elif len(ext0) > 1: order("月の朝", "hp", f"「{ext0[1]}」の題と説明文を、探す人の言葉に直す", "中では見られているのに外から0")
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

# 3b 投稿そのものの数字（閲覧・フォロワー）。11/12：投稿の点検の回（20:33）が Buffer の数字を stats/toukou.json に毎晩足す
#   rows: {day, svc: "threads"|"x", slot: "07:00", type: "kaitai", pic: true|false, views, likes}／followers: {day, threads, x}
tk = load(S("toukou.json"), {}); trows = tk.get("rows", []); tfol = tk.get("followers", [])
import statistics as _st
_med = lambda xs: int(_st.median(xs)) if xs else 0
for svc, nm in (("threads", "Threads"), ("x", "X")):
    now_ = [r for r in trows if r.get("svc") == svc and r.get("day", "") > d7]; old_ = [r for r in trows if r.get("svc") == svc and d14 < r.get("day", "") <= d7]
    if not now_:
        item("view-" + svc, f"投稿の閲覧（{nm}）", "未確認", "1本の中央値が前の7日より上", "未確認", "stats/toukou.json に行が無い")
        continue
    bs = {}
    for r in now_: bs.setdefault(r.get("slot", ""), []).append(int(r.get("views") or 0))
    sm = sorted(((k, _med(v)) for k, v in bs.items() if len(v) >= 3), key=lambda x: -x[1])
    mn, mo = _med([int(r.get("views") or 0) for r in now_]), _med([int(r.get("views") or 0) for r in old_])
    f_now = [f.get(svc) for f in tfol if f.get("day", "") > d7 and f.get(svc) is not None]; f_old = [f.get(svc) for f in tfol if f.get("day", "") <= d7 and f.get(svc) is not None]
    fd = (f_now[-1] - (f_old[-1] if f_old else f_now[0])) if f_now else None
    item("view-" + svc, f"投稿の閲覧（{nm}）", f"1本の中央値 {mn}（前の7日 {mo if old_ else '未確認'}）・フォロワー {f_now[-1] if f_now else '未確認'}人（7日で {('+' if fd >= 0 else '') + str(fd) if fd is not None else '未確認'}）・強い枠 " + ("・".join(f"{k} {v}" for k, v in sm[:2]) or "まだ数が足りない") + (f"・弱い枠 {sm[-1][0]} {sm[-1][1]}" if len(sm) >= 3 else ""), "1本の中央値が前の7日より上", "計測中" if not old_ else ("当たり" if mn > mo else "外れ"), "見られないと、HPにも来ない", mn)
    if len(sm) >= 3 and sm[-1][1] * 3 < sm[0][1]: order("投稿の回", "view-" + svc, f"{nm} の {sm[-1][0]} の枠（中央値 {sm[-1][1]}）をやめ、その1本を {sm[0][0]} の前後30分（中央値 {sm[0][1]}）に移す。本数は増やさない", "弱い枠は強い枠の3分の1より下")
    top3 = sorted(now_, key=lambda r: -int(r.get("views") or 0))[:3]
    if old_ and mn <= mo and top3: order("投稿の回", "view-" + svc, f"{nm} の中央値が前の週より下。いちばん見られた3本（" + "／".join(f"{r.get('day', '')[5:]} {r.get('slot', '')} {r.get('type', '')} {r.get('views')}" for r in top3) + "）の1行目の作りを、あすの同じ枠で別の街・別の数字で作る", f"中央値 {mo}→{mn}")
    # 大当たり（14日の中央値の10倍より上）は「形」ごと増やす。11/12：学習エンジン（毎晩の回）の仕事をここに移した
    all14 = [r for r in trows if r.get("svc") == svc and r.get("day", "") > d14]; m14 = _med([int(r.get("views") or 0) for r in all14])
    big = sorted([r for r in all14 if m14 and int(r.get("views") or 0) >= m14 * 10], key=lambda r: -int(r.get("views") or 0))[:3]
    if big: order("投稿の回", "view-" + svc, f"{nm} の大当たり（ふつうの10倍より上）：" + "／".join(f"{r.get('day', '')[5:]} {r.get('slot', '')}「{r.get('type', '')}」{r.get('views')}" for r in big) + "。この題の形（何の順位か・数字の出し方・1行目）を、別の路線・別の街で今週3本作る。同じ街・同じ数字はくり返さない", f"ふつうは {m14}")
if not trows: order("投稿の回", "view-threads", "投稿の点検の回（20:33）で、きょう出た投稿の閲覧・いいねとフォロワー数を Buffer から取り、stats/toukou.json に足す（形はファイルの about のとおり）", "投稿の閲覧が未確認のまま", "数字")

# 3b2 惹きつける型（11/12 オーナー「人を惹きつけることはファブルなら可能じゃない？投稿の仕方とかも」）
#   それまでは1本ずつの題で数えていたので「どの型が人を集めるか」を機械が覚えられなかった。題を型に分け、型ごとの中央値で、あすの枠の割り当てを機械が決める
import re as _r2
KATA = [("駅・路線の順位", r"駅|線|乗|rank"), ("日付つきの催し", r"^\d+/\d+|^あす|^あした|^今夜|odekake|見頃|まで｜"), ("できる・開く（新駅・開業・完成）", r"開通|完成|オープン|新駅|開業|202[7-9]年|新規|新しい"),
        ("市ごとの地価・家の値段", r"住宅地|地価|土地|㎡|の家、|基準"), ("人口・世帯の増え方", r"人口|世帯|人は|[+＋]\d+人|国勢"), ("ひと駅しらべ", r"hitoeki|→"),
        ("実家・お金の知識", r"jikka|kaitai|親の|名義|金利|フラット"), ("防犯・火事の数字", r"詐欺|盗|侵入|火"), ("街の豆知識・クイズ", r"読|村｜|町の名|どこ？|市｜「"), ("HPの紹介・お礼", r"TOWN NOT|いつも見て|続き")]
def kata(t):
    for nm_, pat in KATA:
        if _r2.search(pat, t or ""): return nm_
    return "そのほか"
_kt = {}
for r in trows:
    if r.get("svc") == "threads" and r.get("day", "") > d14 and r.get("views") is not None: _kt.setdefault(r.get("kata") or kata(r.get("head") or r.get("type", "")), []).append(int(r["views"]))
if _kt:
    _all = _med([v for vs in _kt.values() for v in vs])
    _ks = sorted(((k, _med(v), len(v), max(v)) for k, v in _kt.items()), key=lambda x: -x[1])
    _good = [x for x in _ks if x[2] >= 3 and x[1] >= _all * 2]; _bad = [x for x in _ks if x[2] >= 3 and x[1] * 2 <= _all]
    item("kata", "惹きつける型（Threads・14日）", "・".join(f"{k} {m}（{n}本・最高{mx}）" for k, m, n, mx in _ks) + f"／全部の中央値 {_all}", "いちばん強い型を、強い枠（朝7時・夜8時）に毎日置く", "当たり" if _good else "計測中", "型は題から機械が分ける。3本より少ない型は判断しない", _good[0][1] if _good else 0)
    if _good: order("投稿の回", "kata", f"あすの朝7時は「{_good[0][0]}」（中央値 {_good[0][1]}・ふつうは {_all}）で作る。まだ出していない路線・市・駅を選び、1行目に「その場所の名前＋順位か数字」を入れる。" + (f"夜8時は「{_good[1][0]}」（中央値 {_good[1][1]}）。" if len(_good) > 1 else "") + "同じ場所・同じ数字はくり返さない", "強い型はふつうの2倍より上")
    for k, m, n, mx in _bad[:3]: order("投稿の回", "kata", f"「{k}」の型は中央値 {m}（{n}本）で、ふつう（{_all}）の半分より下。あすからこの型の枠を「{_good[0][0] if _good else _ks[0][0]}」に替える。出すなら週1本まで、1行目を地名＋数字に変えて", "弱い型に枠を使わない")

# 3c 検索で打たれた言葉（Search Console）。11/12 owner「GPTの使い道を増やして欲しい」→ 汐が毎朝写す → 月の朝が stats/kensaku.json へ → 機械が「題に入れる言葉」を選ぶ
ks = load(S("kensaku.json"), {}).get("rows", [])
for site, nm in (("kansai", "関西"), ("kanto", "関東")):
    kr = sorted([r for r in ks if r.get("site") == site], key=lambda r: r.get("day", ""))
    if not kr:
        item("search-" + site, f"検索（{nm}）", "未確認", "クリックが前の週より上", "未確認", "stats/kensaku.json に行が無い")
        continue
    cur_, prev_ = kr[-1], ([r for r in kr if r.get("day", "") <= (date.fromisoformat(kr[-1]["day"]) - timedelta(days=7)).isoformat()] or [None])[-1]
    item("search-" + site, f"検索（{nm}）", f"7日でクリック {cur_.get('clicks')}・表示 {cur_.get('imps')}・平均 {cur_.get('pos')}位（{cur_.get('day')}）" + (f"・前の週 クリック {prev_.get('clicks')}" if prev_ else ""), "クリックが前の週より上", "計測中" if not prev_ else ("当たり" if (cur_.get("clicks") or 0) > (prev_.get("clicks") or 0) else "外れ"), "検索から来る人が、いちばん相談に近い", cur_.get("clicks"))
    # 11/12 はじめて数字が入った：関西 表示8・関東 表示0。題を直す前に「Googleに載っているか」が先。載った枚数は汐が帳面に【登録】で写す → rows の idx / noidx
    if (cur_.get("imps") or 0) < 50:
        _ix = cur_.get("idx")
        order("月の朝", "search-" + site, f"{nm}：Google の表示が7日で {cur_.get('imps')} 回しか無い（題より前に、載っていない）。" + (f"載っているページ {_ix} 枚・載っていない {cur_.get('noidx')} 枚。" + (f"サイトマップが「{cur_.get('map')}」のまま＝Google がページの一覧を受け取れていない。Search Console で /sitemap-all.xml を送り直し、汐が毎朝10ページずつ登録をリクエストする" if "取得" in str(cur_.get("map", "")) else "載っていない理由のいちばん多い物から直す（重複・リンクが無い）") if _ix is not None else "汐の帳面の【登録】の行（載っている枚数・載っていない理由）を stats/kensaku.json の idx・noidx・why に入れ、理由のいちばん多い物から直す"), "検索から人が来ない元の原因")
    ws = cur_.get("words", [])
    near = sorted([w for w in ws if (w.get("i") or 0) >= 10 and 5 <= (w.get("p") or 99) <= 20], key=lambda w: -(w.get("i") or 0))[:3]
    seen0 = sorted([w for w in ws if (w.get("i") or 0) >= 20 and not (w.get("c") or 0) and (w.get("p") or 99) < 10], key=lambda w: -(w.get("i") or 0))[:2]
    if near: order("月の朝", "search-" + site, f"{nm}：あと少しで1ページ目の言葉（" + "／".join(f"「{w['w']}」表示{w['i']}・{w['p']}位" for w in near) + "）。その言葉で出ているページの題と最初の見出しに、その言葉をそのまま入れ、答え（数字）をページのいちばん上に置く", "5〜20位は、題を直すと上がりやすい")
    if seen0: order("月の朝", "search-" + site, f"{nm}：見られているのに押されない言葉（" + "／".join(f"「{w['w']}」表示{w['i']}・クリック0" for w in seen0) + "）。そのページの題と説明文を「◯◯はいくら」「◯◯の順位」のように答えが分かる形に直す", "10位より上なのにクリック0")
if not ks: order("月の朝", "search-kansai", "Drive の「検索の帳面」（汐が毎朝写す）に【検索】【言葉】【ページ】の行があれば、stats/kensaku.json の rows に足す（形は about のとおり）。「見られない」の行なら、オーナーに Search Console の権限の事を1行で伝える", "検索の数字が未確認のまま", "数字")

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
# 5b 絵本を開く型（11/12〜）と前の型のくらべ。ig/posts/*.json（出した記録）の spec から、絵本の型で出したリールを見分ける
import glob as _g
eh_urls = set()
for pp in _g.glob(os.path.join(ROOT, "ig/posts/*.json")):
    try:
        pj = json.load(open(pp)); sp = json.load(open(os.path.join(ROOT, pj.get("spec", ""))))
        if (sp.get("kata") == "ehon" or "ehon" in sp.get("video_url", "")) and pj.get("permalink"): eh_urls.add(pj["permalink"].rstrip("/"))
    except Exception: pass
eh = [r for r in rl if r.get("url", "").rstrip("/") in eh_urls]; old = [r for r in rl if r.get("url", "").rstrip("/") not in eh_urls][:14]
ea = sum(int(r.get("likes") or 0) for r in eh) / max(1, len(eh)); oa = sum(int(r.get("likes") or 0) for r in old) / max(1, len(old))
eans = "計測中" if len(eh) < 6 else ("当たり" if ea > oa else "外れ")
item("reel-ehon", "リールの絵本の型", f"絵本の型 {len(eh)}本・1本あたり いいね {ea:.1f}（前の型の直近14本 {oa:.1f}）", "6本たまったら、前の型より上か", eans, "11/12 オーナー「リールは絵本を開く型」。6本で答えを出す", round(ea * 10))
if eans == "外れ": order("リールの回", "reel-ehon", "絵本の型のいいねが前の型より下。表紙の題（1コマ目）を、いいねの多かった回の言葉に寄せ、絵（motif・scene）を変えて3本ためす。型をやめる・戻すはオーナーに聞く", f"いいね 絵本 {ea:.1f}・前 {oa:.1f}")
if eans == "当たり": order("リールの回", "reel-ehon", "絵本の型が前の型より上。このまま続け、いいねの多かった絵（motif・scene）を先に使う", f"いいね 絵本 {ea:.1f}・前 {oa:.1f}")
if tb: order("リールの回", "reel", f"題材は「{tb[0]}」を先に（1本あたりのいいね {tb[1][0] / max(1, tb[1][1]):.1f}）。同じ題材が3本続いたら次の題材へ", "いいねの多かった題材")

# 6 宿・アフィリエイト（押された数は機械・成果は汐が月曜に写す stats/seika.json）
yado = two(lambda k: k.startswith("宿を開く") or k.startswith("泊まり") or "近くの宿" in k)
sk = seika.get("rows", [])
last = sk[-1] if sk else None
# 11/12 楽天の成果は燈と同じIDなので、燈が毎朝書く notes/sales-board.md（akari-auto・公開）の「- M/D 朝：成果N」を機械が読む
_sbp = os.environ.get("SALES_BOARD", os.path.join(ROOT, "..", "akari-auto", "notes", "sales-board.md")); _sb7 = {}
try:
    for l_ in open(_sbp, encoding="utf-8"):
        m_ = re.match(r"- (\d+)/(\d+) 朝：成果(\d+)", l_)
        if m_:
            dd = date(today.year, int(m_.group(1)), int(m_.group(2)))
            if dd > today: dd = date(today.year - 1, dd.month, dd.day)
            if dd.isoformat() > d7: _sb7[dd.isoformat()] = int(m_.group(3))
except Exception: pass
if _sb7 and not (last and (today - date.fromisoformat(last["day"])).days <= 8):
    last = {"day": max(_sb7), "hassei": sum(_sb7.values()), "kakutei": "未確認", "nyukin": "未確認"}
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

# 7b 未来予想（11/12 オーナー「未来予想もして収益化本格的に」）。機械が毎朝「このままだと30日で相談が何件か」を出し、7日後に自分の予想を答え合わせして、外れた分だけ次の予想を直す
yo = load(S("yosou.json"), {"about": "未来予想の帳面。機械が毎朝1行足し、7日たった行に答え（actual）と外れ具合（err）を付ける。bias は、これまでの 答え÷予想 の真ん中の値で、次の予想に掛ける", "rows": []})
_e7, _ep = sei.get("ext7") or 0, sei.get("ext_prev7") or 0
_op, _wr, _cn = st.get("申し込みページを開いた", 0), st.get("書きはじめた", 0), st.get("連絡先の画面まで進んだ", 0)
for r_ in yo["rows"]:
    if "actual" not in r_ and r_.get("for", "9") <= today.isoformat():
        r_["actual"] = {"ext7": _e7, "sent": sent}; r_["err"] = round(_e7 / r_["pred"]["ext7"], 2) if r_["pred"].get("ext7") else None
        manabi["rows"].append({"day": today.isoformat(), "kind": "手の答え", "item": "未来予想", "what": f"{r_['day']} の予想（外から 週{r_['pred']['ext7']}人・相談 {r_['pred']['sent30']}件/30日）", "result": "当たり" if r_["err"] and 0.7 <= r_["err"] <= 1.3 else "外れ（予想の掛け算を直した）", "before": r_["pred"]["ext7"], "after": _e7})
_errs = sorted(r_["err"] for r_ in yo["rows"] if r_.get("err"))
bias = _errs[len(_errs) // 2] if _errs else 1.0
_tr = min(2.0, max(0.5, _e7 / _ep)) if _ep else 1.0
p_ext = round(_e7 * _tr * bias)                      # 来週 外から来る人
r_op = min(1.0, _op / _e7) if _e7 else 0             # 外から → 申し込みを開く
r_wr = _wr / _op if _op else 0                       # 開く → 書きはじめる
r_sd = (sent / _wr) if _wr and sent else None        # 書きはじめる → 送信（まだ0件なら未確認）
SD0 = 0.5                                            # 送信の率がまだ測れない間の仮の値（書きはじめた人の半分）。1件でも送信が出たら実測に替わる
def sim(ext, op, wr, sd=None): return ext * 30 / 7 * op * wr * (sd if sd is not None else (r_sd if r_sd is not None else SD0))
now30 = sim(p_ext, r_op, r_wr)
# 市を足す仕組み（tools/kaitai/chou.json＝Drive「関西の解体補助金帳」の写し。朝の回がそろえる）
_ch = load(os.path.join(ROOT, "tools", "kaitai", "chou.json"), {}).get("rows", [])
if _ch:
    _mt = [r for r in _ch if r["state"] == "待ち"]; _mo = [r for r in _ch if r["state"] == "持ち越し"]; _pg = [r for r in _ch if r["state"] == "ページ"]
    _last_pg = max([r["day"] for r in _pg] or [""]); _last_any = max(r["day"] for r in _ch)
    _gap = (today - date.fromisoformat(_last_pg)).days if _last_pg else 99; _gap_c = (today - date.fromisoformat(_last_any)).days
    _old = [r for r in _mt if (today - date.fromisoformat(r["day"])).days >= 1]
    item("city-tasu", "市を足す仕組み（汐の写し→月が確かめる→ページ）", f"ページにした {len(_pg)}市（最後 {_last_pg[5:]}）・待ち {len(_mt)}市・持ち越し {len(_mo)}市・帳が最後に動いた日 {_last_any[5:]}", "待ちを次の日に残さない・2日つづけて0市にしない", "外れ" if _old or _gap >= 2 or _gap_c >= 2 else "当たり", "入口の数は、毎日足さないと増えない", len(_pg))
    if _old: order("月の朝", "city-tasu", "帳で待っている市を、きょう全部ページにする：" + "・".join(r["city"] for r in _old[:10]) + "（公式で確かめ、tools/kaitai/chou.json の state を直す）", "待ちが1日を越えた")
    elif _gap_c >= 2: order("月の朝", "city-tasu", f"汐の写しが {_gap_c}日 止まっている。月が帳の順番の次の3市を自分で公式から確かめてページにし、オーナーに汐の回が動いているかを1行で聞く", "写しが止まると入口が増えない")
    elif _gap >= 2: order("月の朝", "city-tasu", f"{_gap}日 新しい市が出ていない。持ち越しの市（" + "・".join(r["city"] for r in _mo[:5]) + "）を、PDF・別の公式ページから確かめ直して出す", "2日つづけて0市")
    if len(_mo) >= 5: order("月の朝", "city-tasu", f"持ち越しが {len(_mo)}市たまっている。機械で開けない市は、凪の【確かめ】「合う」を待って出す形に切り替える", "確かめきれない市が溜まっている")
LEV = [("外から来る人を2倍にする（市のページ・検索・投稿の2本目）", sim(p_ext * 2, r_op, r_wr), "city"),
       ("書きはじめる人を、開いた人の3割にする（申し込みページの最初の画面）", sim(p_ext, r_op, max(r_wr, 0.3)), "lead"),
       ("家のページから申し込みを開く人を増やす（開く率を1.5倍）", sim(p_ext, min(1.0, r_op * 1.5), r_wr), "michi")]
LEV.sort(key=lambda x: -x[1]); top = LEV[0]
need = round(40 / (30 / 7 * r_op * r_wr * (r_sd if r_sd is not None else SD0))) if r_op and r_wr else None
item("yosou", "未来予想（30日）", f"このままだと 相談 {now30:.1f}件/30日（紹介料の見込み 約{now30 * 1:.0f}万円・毎月の出費 10万円）。来週 外から {p_ext}人の予想。いちばん効く手：{top[0]} → {top[1]:.1f}件" + ("。送信の率は未確認（仮に半分）" if r_sd is None else ""), f"30日で {rung(now30, [1, 3, 10, 20, 40])}件（月40件に要る 外から来る人：週{need if need else '未確認'}人）", "当たり" if now30 >= 10 else "外れ", f"予想の当たり具合：これまで {len(_errs)}回 答え合わせ・掛け算 {bias}", round(now30, 1))
order("月の朝", "yosou", f"未来予想でいちばん効く手は「{top[0]}」（30日の相談 {now30:.1f}件 → {top[1]:.1f}件）。きょうの1つは、この手に当たる指令（{top[2]}）から選ぶ。2番目は「{LEV[1][0]}」→ {LEV[1][1]:.1f}件", "同じ手間なら、相談がいちばん増える所から", "数字")
if not any(r_["day"] == today.isoformat() for r_ in yo["rows"]):
    yo["rows"].append({"day": today.isoformat(), "for": (today + timedelta(days=7)).isoformat(), "pred": {"ext7": p_ext, "sent30": round(now30, 1), "top": top[0]}, "rates": {"open": round(r_op, 2), "write": round(r_wr, 2), "send": r_sd}})
yo["bias"] = bias; yo["rows"] = yo["rows"][-120:]
json.dump(yo, open(S("yosou.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

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
_yoru = [r["day"] for r in tantou["rows"] if "夜" in r]
if not _yoru or (today - date.fromisoformat(max(_yoru))).days > 2:
    order("月の朝", "gpt", "Drive の「夜の結果 きのうの日付」に【道】【止まった所】【ミス帳】の3行があるかを見て、stats/tantou.json の rows に {day, 夜: 行の数（無ければ0）, 夜_naoshi: その行から直した数} を1行足す", "夜（テスター）の出来を測る数字が無い", "数字")
tr = [r for r in tantou.get("rows", []) if r.get("day", "") > d7]
if tr:
    miss = {}
    for r in tr:
        for who in WHO:
            if who == "夜" and (not _yoru or r.get("day", "") < min(_yoru)): continue  # 夜は、数え始めた日より前を「出なかった」にしない
            if not r.get(who): miss[who] = miss.get(who, 0) + 1
    item("gpt", "担当（" + "・".join(WHO) + "）", f"{len(tr)}日のうち、出なかった日：" + ("・".join(f"{w} {n}日" for w, n in miss.items()) or "なし") + (f"・夜の指摘から直した {sum(int(r.get('夜_naoshi') or 0) for r in tr)}件" if any("夜_naoshi" in r for r in tr) else ""), "出なかった日 0", "当たり" if not miss else "外れ", "指示書どおりに毎日の物が出たか", -sum(miss.values()))
    for w, n in miss.items():
        if n >= 2: order("月の朝", "gpt", f"{w}が{n}日出していない。指示書を半分の長さにして、やる事を1つに絞る。次の週も出なければ、その仕事を機械に移す", "出ない指示書は長すぎるか、難しすぎる")
else:
    item("gpt", "担当（汐・凪・雫・夜）", "未確認", "出なかった日 0", "未確認", "朝の回が stats/tantou.json に入れる")
    order("月の朝", "gpt", "きのう 汐・凪・雫・夜 が出した物（行の数・絵・結果の文書）を確かめ、stats/tantou.json の rows に {day, 汐, 凪, 雫, 夜}（出た＝数、出なかった＝0）を1行足す", "担当の出来を測る数字がまだ無い", "数字")

# 9 楽天ROOM
# 11/12 作り替え：人に写させず、機械が公開ページから毎朝写す（tools/room/kazu.py → stats/room.json）。売れた数は楽天の成果（燈と同じID・sales-board）
rm = load(S("room.json"), {}).get("rows", [])
try: _rf = open(S("room-fail.txt"), encoding="utf-8").read().strip()
except Exception: _rf = ""
if rm:
    _r0 = rm[-1]; _r7 = next((r for r in reversed(rm) if r["day"] <= d7), None); _r1 = rm[-2] if len(rm) > 1 else None
    _df = _r0["follower"] - _r7["follower"] if _r7 else None; _di = _r0["items"] - _r1["items"] if _r1 else None
    _uri = sum(_sb7.values()) if _sb7 else None
    _stale = (today - date.fromisoformat(_r0["day"])).days >= 2
    item("room", "楽天ROOM", f"フォロワー {_r0['follower']}（7日で {'未確認' if _df is None else ('+' if _df >= 0 else '') + str(_df)}）・載っている商品 {_r0['items']}（きのうから {'未確認' if _di is None else ('+' if _di >= 0 else '') + str(_di)}）・楽天の成果 7日 {'未確認' if _uri is None else _uri}件", "商品が毎日ふえる・フォロワー 週+10・週に1つ売れる", "外れ" if _stale or (_di is not None and _di <= 0) else ("当たり" if (_uri or 0) > 0 or (_df or 0) >= 10 else ("計測中" if _df is None else "外れ")), "台本を出しても、載っていなければ0。載っても、見る人（フォロワー）が増えなければ売れない", _r0["follower"])
    if _stale or _rf: order("月の朝", "room", "ROOM の数字が写せていない：" + (_rf or "stats/room.json が2日止まっている") + "。tools/room/kazu.py を直す", "見張りが止まっている", "数字")
    elif _di is not None and _di <= 0: order("月の朝", "room", f"ROOM の商品がきのうから増えていない（{_r0['items']}件）。雫・凪の報告（燈への報告の【雫】の行）で、載せた番号と止まった文言を見て、台本か指示書の止まる所を直す", "台本を出しても載っていない")
    elif _df is not None and _df < 10 and not (_uri or 0): order("月の朝", "room", f"ROOM のフォロワーが7日で {_df:+d}。台本の題材を、いま売れる季節の物（akari の room-daihon の上位）に寄せ、コレクションの名前を探す言葉にする。1つだけ変えて7日見る", "載っているのに見る人が増えていない")
else:
    item("room", "楽天ROOM", "未確認" + ("（" + _rf[:80] + "）" if _rf else ""), "商品が毎日ふえる・フォロワー 週+10・週に1つ売れる", "未確認", "機械が毎朝、公開ページから写す")
    order("月の朝", "room", "ROOM の数字が写せていない：" + (_rf or "stats/room.json がまだ無い") + "。tools/room/kazu.py を直す", "ROOM の結果が未確認のまま", "数字")

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
# 11/12 owner「なんでそれが抜けてるのか理解できない。大問題だろ」：関東の街ページ329枚に申し込みへの道が無かった（見られた1195→申し込み0）。人の目ではなく、機械が毎日「家のページなのに申し込みへ行けないページ」を数える
def _michi(root):
    import re as _re
    bad = []
    for d, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".html"): continue
            rel = os.path.relpath(os.path.join(d, f), root)
            if not _re.match(r"(machi/|jikka/[^/]+\.html|kaitai|ranking|chika|uru|fudosan-list)", rel) or rel == "jikka/index.html": continue
            s = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
            if 'http-equiv="refresh"' in s: continue
            if "moushikomi" not in _re.sub(r"<nav.*?</nav>", "", s, flags=_re.S): bad.append(rel)
    return sorted(bad)
_bad = _michi(os.path.join(ROOT, "links"))
item("michi", "申し込みへの道", f"家のページで道が無い {len(_bad)}枚" + (f"（例 {_bad[0]}）" if _bad else ""), "合格の線：0枚", "当たり" if not _bad else "外れ", "家・土地のページは、どれも申し込みへ1回で行ける事", val=len(_bad))
if _bad: order("月の朝", "michi", f"申し込みへの道が無い家のページが {len(_bad)}枚（{'・'.join(_bad[:3])}）。そのページを作る機械に、街の名前入りの「いくらで売れるか無料で聞く」を足す", "見られても反響にならない")
# 申し込みが本番で送れるか（tools/formcheck/check.js が毎朝と直した時に通す。stats/formcheck.json）
fc = load(S("formcheck.json"), {})
if fc:
    _ng = [f"{'関西' if k == 'kansai' else '関東'}「{r['name']}」{r['why']}" for k, v in (fc.get("sites") or {}).items() for r in v.get("rows", []) if not r.get("ok")]
    _old_fc = fc.get("at", "")[:10] < (today - __import__("datetime").timedelta(days=1)).isoformat()
    item("form", "申し込みが送れるか", f"{fc.get('at', '')} に本番で通した：関西・関東 各3つの道のうち、だめ {len(_ng)}" + (f"（{_ng[0]}）" if _ng else "") + ("・確かめが2日止まっている" if _old_fc else ""), "だめ 0・毎日確かめている", "外れ" if _ng or _old_fc else "当たり", "壊れていても、相談0のままでは気づけない", len(_ng))
    if _ng: order("月の朝", "form", "申し込みが本番で最後まで送れない：" + "／".join(_ng[:3]) + "。ほかの何より先に直し、formcheck.yml を動かして「だめ 0」を確かめる", "反響の出口が壊れている")
    if _old_fc and not _ng: order("月の朝", "form", "申し込みの通し確かめ（formcheck.yml）が2日止まっている。Actions を見て動かす", "見張りが止まっている")
else:
    item("form", "申し込みが送れるか", "未確認（stats/formcheck.json が無い）", "だめ 0・毎日確かめている", "未確認", "壊れていても、相談0のままでは気づけない")
PRI = ["form", "yosou", "lead", "michi", "search-kansai", "search-kanto", "city-tasu", "city", "hp", "kata-tasu", "spot-more", "post", "kata", "view-threads", "view-x", "pic", "reel", "reel-ehon", "aff", "gpt", "room"]
old = {(o["to"], o["item"], o["order"][:24]): o.get("days", 1) for o in prev.get("orders", [])}
same_day = prev.get("day") == today.isoformat()
for o in orders:
    d = old.get((o["to"], o["item"], o["order"][:24]))
    o["days"] = (d if same_day else d + 1) if d else 1
    _w = [y["what"] for y in yatta["rows"] if "result" not in y and y.get("item") == o["item"]]
    if _w: o["wait"] = _w[-3:]
    if ng.get(o["item"]): o["ng"] = ng[o["item"]][-3:]
    if ok.get(o["item"]): o["ok"] = ok[o["item"]][-3:]
# 指令をやったかの見張り（11/12 オーナー「お前の優先はそれだろ」「一つ一つ完璧な仕組みにしろ」）。
# 指令が出ているのに、その項目に手（yatta.json の行）が無い日数を数える。きのうの【きょうの1つ】に手が無ければ「外れ」。月が指令をやらずに他の事をした日が、台帳と管制室に出る
import datetime as _dt
# 同じ項目に指令が2つ以上ある時は、行の order（指令の最初の24字）が合う手だけを数える（order の無い古い行は、その項目の1つ目の指令の手とみなす）
def _last(o):
    sib = [x for x in orders if x["item"] == o["item"] and x["to"] == o["to"]]
    return max([y.get("day", "") for y in yatta["rows"] if y.get("item") == o["item"] and (len(sib) < 2 or y.get("order", "")[:24] == o["order"][:24] or ("order" not in y and sib[0] is o))] or [""])
for o in orders:
    lt = _last(o); st = (today - _dt.timedelta(days=o["days"] - 1)).isoformat()
    o["idle"] = o["days"] if lt < st else max(0, (today - _dt.date.fromisoformat(lt)).days)   # 指令が出てから手が無い日数（手を打った日からは数え直す）
orders.sort(key=lambda o: (o["kind"] != "作る", PRI.index(o["item"]) if o["item"] in PRI else 99))
_c = [o for o in orders if o["to"] == "月の朝" and o["kind"] == "作る"]
first = next((o for o in _c if len(o.get("wait", [])) < 2), _c[0] if _c else None)  # 同じ所に答え待ちの手が2つあれば、答えが出るまで次の項目を先に（重ねて変えると、どの手が効いたか分からなくなる）
if first: first["first"] = True
_m = [o for o in orders if o["to"] == "月の朝"]
_late = [o for o in _m if o.get("idle", 0) >= 3]
_pf = prev.get("first_item"); _pd = prev.get("day", "")
_did = (not _pf) or same_day or any(y.get("item") == _pf and y.get("day", "") >= _pd for y in yatta["rows"])
items.insert(0, {"id": "jikkou", "name": "指令をやったか（月）", "num": f"月あての指令 {len(_m)}本・3日以上 手が無い {len(_late)}本" + (f"（{'・'.join(sorted(set(o['item'] for o in _late)))}）" if _late else "") + f"・きのうの【きょうの1つ】{'やった' if _did else 'やっていない'}",
              "line": "きのうの1つをやった・3日以上 手が無い指令 0本", "ans": "当たり" if _did and not _late else "外れ", "why": "仕組みを作っても、月が指令どおりに動かなければ意味がない（11/12 オーナー）", "val": len(_late)})

def line(o):
    t = ("【きょうの1つ】" if o.get("first") else ("【数字を入れる】" if o["kind"] == "数字" else "")) + o["order"] + f"（理由：{o['why']}）"
    if o.get("idle", 0) >= 3: t += f" ！{o['idle']}日 手が無い＝まだやられていない（やったら stats/yatta.json に1行）"
    elif o["days"] >= 3: t += f"（{o['days']}日目。手は打ってある）"
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
json.dump({"day": today.isoformat(), "first_item": (first or {}).get("item"), "items": items, "orders": orders, "sum": {"sent": sent, "seika": (int(last.get("hassei") or 0) if last else None), "cost": 100000}, "hist": hist}, open(S("gakushu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "about": "きょうの指令。to が自分の行を、動く前に読んでそのままやる。やったら stats/yatta.json の rows に {day, item, what} を1行足す（同じ item の指令が2つ以上ある時は order に指令の最初の24字も書く。書かないと「手が無い」と数えられる）（7日後に機械が効いた・効かなかったを付ける）。ng の手はくり返さない", "orders": orders}, open(S("shirei.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manabi, open(S("manabi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L))
