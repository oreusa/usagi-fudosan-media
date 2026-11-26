"""11/26 オーナー「全部仕組みづくり」「もっとよくしていこう仕組みも全て」
GPT（夜・雫・汐）の予定が、今日決めた回だけ動いたかを数える。月が目で数えると抜けを見落とす。
使い方: python3 tools/allcheck/gpt_kaisu.py <燈への報告を download した text のファイル> [YYYY-MM-DD]
× がある時は終わりの値が 1。予定の正は夜の指示書 ■1（予定を変えたらこの YOTEI も同じ日に直す）。"""
import datetime as dt
import re
import sys

# (名前, 報告の頭, 決まった時刻)
YOTEI = [
    ("夜 うさぎの回", "【夜 この回】", ["07:00", "10:30", "13:30", "16:30", "19:30"]),
    ("夜 HP中身", "【夜 HP中身】", ["09:00", "12:00", "15:00", "21:00"]),
    ("雫 ROOM", "【雫開始】", ["06:40", "07:25", "12:30", "17:30"]),
    ("汐", "【汐】", ["07:45"]),
]
YOYUU = 75  # 回が始まってから報告が出るまで待つ分

text = open(sys.argv[1], encoding="utf-8-sig").read()
jst = dt.timezone(dt.timedelta(hours=9))
now = dt.datetime.now(jst)
day = sys.argv[2] if len(sys.argv) > 2 else now.date().isoformat()
bad, rows = [], []
for name, head, times in YOTEI:
    lines = [l for l in text.splitlines() if l.startswith(head) and day in l]
    due = [t for t in times if now >= dt.datetime.fromisoformat(f"{day}T{t}:00+09:00") + dt.timedelta(minutes=YOYUU)]
    got = len(lines)
    # 回の時刻と報告の時刻はずれる（汐 7:45 の回が 8:05 に書く等）ので、数でくらべる
    if got < len(due):
        bad.append(f"× {name}：{len(due)}回のはずが報告{got}行（{day}・決まった時刻 {'・'.join(due)}）")
    else:
        rows.append(f"○ {name}：{len(due)}回のはず・報告{got}行")
print("\n".join(rows))
if bad:
    print("\n来ていない回：")
    print("\n".join(bad))
    sys.exit(1)
print("\nGPT の回：全部 ○")
