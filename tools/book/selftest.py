#!/usr/bin/env python3
"""門（gate.py）の自分の点検。11/13 に実際に出てしまった間違いを、門が × にするかを確かめる。"""
import json, os, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gate

D = "2026-11-14"
LAST = gate.CFG["last_line"]
def post(slot, time, typ, head, url, img="", x=""):
    return {"date": D, "slot": slot, "time": time, "type": typ, "threads_topic": "大阪",
            "threads_text": f"{head}\n本文\n{url}\n{LAST}", "threads_thread": [], "x_text": x, "x_thread": [],
            "image_url": img}
ok = [post("n1", "07:00", "rank", "【京阪本線｜大阪府内の駅で1位】", "https://townnote.pages.dev/ranking?f=th-rank-1114ap#r30",
           x="【京阪本線】 https://townnote.pages.dev/ranking?f=x-rank-1114a#r30"),
      post("S1", "08:00", "jikka", "【実家が摂津市なら｜昨年度の平均は2,173万円】", "https://townnote.pages.dev/jikka/settsu?f=th-jikka-1114b"),
      post("n2", "09:00", "odekake", "【11/15から｜紅葉】", "https://townnote.pages.dev/koyo-osaka?f=th-odekake-1114c",
           x="【11/15から】 https://townnote.pages.dev/koyo-osaka?f=x-odekake-1114c"),
      post("n3", "12:00", "dekiru", "【ルクア サウス、28店舗が開業】", "https://townnote.pages.dev/odekake-osaka?f=th-dekiru-1114d1"),
      post("n8", "13:00", "rank", "【南海本線｜府内で2位】", "https://townnote.pages.dev/ranking?f=th-rank-1114e#r31",
           x="【南海本線】 https://townnote.pages.dev/ranking?f=x-rank-1114e#r31"),
      post("n7", "21:00", "hitoeki", "【ひと駅しらべ その22｜南草津駅】", "https://townnote.pages.dev/machi/shiga-03?f=th-hitoeki-1114f1",
           x="【ひと駅しらべ】 https://townnote.pages.dev/machi/shiga-03?f=x-hitoeki-1114f"),
      post("n5", "15:00", "odekake", "【今週末だけ｜夜の紅葉】", "https://townnote.pages.dev/koyo-osaka?f=th-odekake-1114g"),
      post("n6", "18:00", "dekiru", "【11/20開店｜草津駅前】", "https://townnote.pages.dev/odekake-shiga?f=th-dekiru-1114h")]
for p_ in ok: p_.update(x_text="", x_thread=[])  # 11/14〜 Threads の枠は X に出さない（X は x07〜x21 の別枠）
def xpost(h, text):
    return {"date": D, "slot": "x" + h, "time": h + ":00", "type": "sokuhou", "threads_text": "", "threads_thread": [],
            "x_text": text, "x_thread": [], "image_url": ""}
ok += [xpost(h, f"【{h}時｜草津市】駅前に新しい店が11/20開店\n草津駅から歩いて3分\n#草津市 #草津駅") for h in ("07", "09", "12", "15", "18", "21")]
CASES = [  # (直す枠, 直し方, × に入るはずの言葉)
    ("S1", lambda p: p.update(threads_text=p["threads_text"].replace("/jikka/settsu", "/kaitai-settsu")), "売れた値段"),
    ("n3", lambda p: p.update(threads_text=p["threads_text"].replace("/odekake-osaka", "/machi/osaka-19")), "開業"),
    ("n8", lambda p: p.update(threads_text=p["threads_text"] + "\nお名前なしでも大丈夫"), "名前なしでも"),
    ("n7", lambda p: p.update(threads_text=p["threads_text"].replace(LAST, "毎朝7時と夜8時に、関西の街の数字を出しています。")), "最後の行"),
    ("x09", lambda p: p.update(x_text=""), "x_text が空"),
    ("x12", lambda p: p.update(x_text=p["x_text"] + "\nhttps://townnote.pages.dev/?f=x-sokuhou-1114a"), "リンクがある"),
    ("x15", lambda p: p.update(x_text=p["x_text"] + " #関西 #開店"), "ハッシュタグ"),
    ("x18", lambda p: p.update(threads_text="Threads の文"), "X だけ"),
    ("x21", lambda p: p.update(type="jikka"), "型が"),
    ("n1", lambda p: p.update(time="20:00"), "時刻"),
    ("n2", lambda p: p.update(threads_text=p["threads_text"].replace("f=th-odekake-1114c", "f=x-odekake-1113c")), "印"),
    ("n3", lambda p: p.update(threads_text=p["threads_text"].replace("townnote.pages.dev", "oreusa.github.io")), "お客さんに見せない"),
    ("n7", lambda p: p.update(image_url="https://x/media/post/nai-e.jpg"), "リポジトリに無い"),
    ("n1", lambda p: p.update(threads_text=p["threads_text"].replace("https://townnote.pages.dev/ranking?f=th-rank-1114ap#r30", "4位より下は、下のリンクで見られます")), "下のリンク"),
]
tmp = tempfile.mkdtemp(); real = gate.ROOT
os.makedirs(os.path.join(tmp, "schedule")); os.makedirs(os.path.join(tmp, "media", "post"))
gate.ROOT = tmp
def run(rows):
    json.dump(rows, open(os.path.join(tmp, "schedule", D + ".json"), "w"), ensure_ascii=False)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return gate.run(D)
fail = 0
code, out = run(ok)
if code != 0:
    fail += 1; print("× 正しい枠が通らない：", {k: v["bad"] for k, v in out.items() if v["bad"]})
for slot, fix, word in CASES:
    rows = json.loads(json.dumps(ok)); fix(next(r for r in rows if r["slot"] == slot))
    code, out = run(rows)
    if code == 0 or not any(word in b for b in out[slot]["bad"]):
        fail += 1; print(f"× {slot} の「{word}」を止められない：{out[slot]['bad']}")
code, out = run(ok[:-1])
if code == 0: fail += 1; print("× 抜けた枠を止められない")
shutil.rmtree(tmp); gate.ROOT = real
print("門の自分の点検：" + ("全部○" if not fail else f"× {fail}件")); sys.exit(1 if fail else 0)
