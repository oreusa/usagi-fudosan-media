"""表紙（入口）用の小さなデータ links/assets/cover.json を作る。
11/10 オーナー「見やすさと操作性と技術で勝負」→ 表紙は毎回リスト全体を読まず、これ1つ（数KB）だけ読む。
中身：府県ごとの おでかけ開催中の数と3件・住宅地の上がり幅・上がった街・戸建の売れた平均（近畿レインズ）。"""
import json, os, re, datetime
from bs4 import BeautifulSoup
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = os.path.join(R, "links")
PREF = ["大阪", "京都", "兵庫", "奈良", "滋賀", "和歌山"]
today = (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")

# 11/10 夜 #165：表紙の「きょう◯件」と一覧の「きょう」の件数がちがった（休館日を見ていなかった）→ when.js の openOn と同じ数え方
HOL = {"2026-11-03", "2026-11-23", "2027-01-01", "2027-01-11", "2027-02-11", "2027-02-23", "2027-03-21", "2027-03-22"}
def open_on(days, d):
    if not days:
        return True
    w = (datetime.date.fromisoformat(d).weekday() + 1) % 7  # 0=日〜6=土
    if days.startswith("wd:"):
        return ("h" in days[3:] and d in HOL) or str(w) in days[3:]
    if days == "sat":
        return w == 6
    if days == "sun":
        return w == 0
    if days == "we":
        return w in (0, 6) or d in HOL
    return d in days.split(",")
soup = BeautifulSoup(open(os.path.join(L, "index.html"), encoding="utf-8").read(), "html.parser")
od = {p: [] for p in PREF}; up = 0
cur = ""
paper = soup.select_one(".paper")
for a in paper.select(".wk, a.card"):
    if "wk" in (a.get("class") or []):
        cur = a.get_text(); continue
    e, s, p = a.get("data-e") or "", a.get("data-s") or "", a.get("data-pref") or ""
    t = a.select_one(".t")
    if (e and e < today) or not t or p not in od: continue
    if not cur.startswith("これから"): continue
    if s and s > today: up += 1; continue
    if not open_on(a.get("data-days") or "", today): continue
    m = a.select_one(".m")
    od[p].append({"t": t.get_text(strip=True), "m": m.get_text(strip=True) if m else "", "h": a.get("href"), "f": "無料" in (a.get("data-tag") or "")})
towns = json.load(open(os.path.join(L, "assets", "towns.json"), encoding="utf-8"))
sold = json.load(open(os.path.join(L, "assets", "gyosha-sold.json"), encoding="utf-8"))
out = {"at": today, "up": up, "p": {}}
for p in PREF:
    tw = [t for t in towns if t["p"] == p]
    r = [t.get("r8") or 0 for t in tw]
    n = s_ = 0
    for t in tw:
        k = (sold.get(t["n"]) or {}).get("k")
        if k: n += k[0]; s_ += k[0] * k[1]
    top = sorted(tw, key=lambda t: -(t.get("r8") or 0))[:3]
    out["p"][p] = {"od": len(od[p]), "free": sum(1 for x in od[p] if x["f"]), "odL": [{"t": x["t"], "h": x["h"]} for x in od[p][:3]],
                   "tw": len(tw), "upT": sum(1 for x in r if x > 0), "avg": round(sum(r) / len(r), 1) if r else 0,
                   "top": [{"n": t["n"], "r": t.get("r8") or 0, "id": t["id"]} for t in top],
                   "kN": n, "kAvg": round(s_ / n) if n else 0}
json.dump(out, open(os.path.join(L, "assets", "cover.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("cover.json", sum(v["od"] for v in out["p"].values()), "件", os.path.getsize(os.path.join(L, "assets", "cover.json")), "bytes")
