"""管制室に出す「機械の点検結果」を、点検の記録からそのまま作る（11/9 オーナー「アーチファクトがちゃんと報告になってない」「間違いのないように見れる仕組みにしろ」）。

月が手で数えたり、まとめたりしない。点検の記録（allcheck ブランチ・stats/linkcheck.md・notes/gakushu.json）を読んで、
そのまま JSON にする。朝の点検（9:20）はこの JSON を管制室の morning_report の facts に入れるだけ。

使い方（usagi-fudosan-media で）:
  git fetch origin allcheck
  （投稿の学習も出すとき）管制室 DB の days を直近21日・engine/state を ArtifactData の out_dir で保存しておく
  python3 tools/kanseishitsu/facts.py [--days DIR/days] [--engine DIR/engine/state.json] > /tmp/facts.json
"""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JST = datetime.timezone(datetime.timedelta(hours=9))


def git_show(ref, path):
    try:
        return subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return ""


def allcheck():
    out = {}
    head = git_show("origin/allcheck", "report.md").split("\n", 1)[0]
    m = re.search(r"(\d{4}-\d\d-\d\d \d\d:\d\d)", head)
    out["at"] = m.group(1) if m else ""
    for key, path in (("day", "report.json"), ("night", "night/report.json")):
        raw = git_show("origin/allcheck", path)
        try:
            rows = json.loads(raw) if raw else []
        except ValueError:
            rows = []
        ng = [f'{r["site"]} {r["p"]}：{"／".join(r["prob"])}' for r in rows if r.get("prob")]
        out[key] = {"pages": len(rows), "tsuki": sum(1 for r in rows if r.get("site") == "月"),
                    "akari": sum(1 for r in rows if r.get("site") == "燈"), "ng": ng}
    return out


def linkcheck():
    p = os.path.join(ROOT, "stats", "linkcheck.md")
    if not os.path.exists(p):
        return {}
    t = open(p, encoding="utf-8").read()
    head = t.split("\n", 1)[0]
    m = re.search(r"（(.+?)・(\d+)件）", head)
    bad = [ln[2:].strip() for ln in t.split("\n## 開けない（直す）", 1)[-1].split("\n## ", 1)[0].split("\n") if ln.startswith("- ✗")] if "## 開けない" in t else []
    return {"at": m.group(1) if m else "", "links": int(m.group(2)) if m else 0, "ng": bad}


def linkcheck_life():
    """関東（akari-auto の notes/linkcheck.md）。隣に akari-auto があれば読む。開かない物だけを数える（重い・新しい画面で開く は数えない）。"""
    ak = os.path.join(os.path.dirname(ROOT), "akari-auto")
    if not os.path.isdir(ak):
        return {}
    subprocess.run(["git", "-C", ak, "fetch", "-q", "origin", "main"], capture_output=True)
    try:
        t = subprocess.run(["git", "-C", ak, "show", "origin/main:notes/linkcheck.md"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return {}
    m = re.search(r"確かめた時刻：(\S+ \S+)｜.*?リンク (\d+)本", t)
    bad = []
    sec = t.split("## 直す所", 1)[-1].split("\n## ", 1)[0]
    for ln in sec.split("\n"):
        f = ln[2:].split("｜")
        if not ln.startswith("- ") or len(f) < 3 or not re.search(r"開かない|ページがない|404|見つからない", f[1]):
            continue
        # 載せる前に止めた物（hold）と、楽天が機械を断る 503 は、お客さまの画面では開くので数えない
        if "hold・" in f[0] or ("rakuten" in f[2] and "503" in f[1]):
            continue
        bad.append(f[0] + "：" + f[1])
    return {"at": m.group(1) if m else "", "links": int(m.group(2)) if m else 0, "ng": bad}


def _rows(path):
    import glob
    out = []
    for f in sorted(glob.glob(os.path.join(path, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d = d.get("data", d)
        for p in d.get("posts", []):
            if p.get("reach") is not None and p.get("ch") in ("threads", "twitter"):
                out.append({**p, "day": d.get("date", "")})
    return out


def toko(days_dir, engine_path):
    """投稿の学習（11/9 オーナー「投稿も学習できてるんだろうな？」）。
    ①この7日と前の7日の、1本あたりの閲覧の真ん中　②この7日で、エンジンが「効く」とした型を使った投稿と使わない投稿の真ん中。"""
    import statistics
    if not days_dir or not os.path.isdir(days_dir):
        return {}
    rows = _rows(days_dir)
    if not rows:
        return {}
    from collections import Counter
    cnt = Counter(r["day"] for r in rows if r["ch"] == "threads")
    full = [d for d, c in cnt.items() if c >= 5]   # 数字がまだ入りきっていない日（前日など）は使わない
    last = max(full) if full else max(r["day"] for r in rows)
    rows = [r for r in rows if r["day"] <= last]
    d0 = datetime.date.fromisoformat(last)
    a = (d0 - datetime.timedelta(days=6)).isoformat()
    b = (d0 - datetime.timedelta(days=13)).isoformat()
    up = {}
    if engine_path and os.path.exists(engine_path):
        import ast
        st = json.load(open(engine_path, encoding="utf-8"))
        st = st.get("data", st)
        pol = st.get("policy")
        pol = ast.literal_eval(pol) if isinstance(pol, str) else (pol or {})
        for dim, v in (pol.get("dims") or {}).items():
            up[dim] = set(v.get("up") or [])
    med = lambda xs: round(statistics.median(xs)) if xs else None
    out = {"day": last, "n": len(rows)}
    for ch, nm in (("threads", "Threads"), ("twitter", "X")):
        now = [r["reach"] for r in rows if r["ch"] == ch and r["day"] >= a]
        pre = [r["reach"] for r in rows if r["ch"] == ch and b <= r["day"] < a]
        use, non = [], []
        for r in rows:
            if r["ch"] != ch or r["day"] < a:
                continue
            tg = r.get("tags") or {}
            hit = sum(1 for dim, s in up.items() if tg.get(dim) in s)
            (use if hit >= 2 else non).append(r["reach"])
        out[ch] = {"name": nm, "week": med(now), "prev": med(pre), "n_week": len(now),
                   "kata": med(use), "n_kata": len(use), "other": med(non), "n_other": len(non)}
    return out


def gakushu(days=7):
    """notes/gakushu.json（ミス → 仕組みの帳面）の直近の分。"""
    p = os.path.join(ROOT, "notes", "gakushu.json")
    if not os.path.exists(p):
        return {"rows": [], "made": 0, "open": 0}
    rows = json.load(open(p, encoding="utf-8")).get("rows", [])
    since = (datetime.datetime.now(JST).date() - datetime.timedelta(days=days)).isoformat()
    rows = [r for r in rows if r.get("date", "") >= since]
    made = sum(1 for r in rows if r.get("check"))
    return {"rows": rows[-30:], "made": made, "open": len(rows) - made}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--days")
    ap.add_argument("--engine")
    a = ap.parse_args()
    now = datetime.datetime.now(JST)
    facts = {"made_at": now.strftime("%Y-%m-%dT%H:%M+09:00"), "allcheck": allcheck(), "linkcheck": linkcheck(), "linkcheck_life": linkcheck_life(),
             "gakushu": gakushu(), "toko": toko(a.days, a.engine)}
    json.dump({"date": now.date().isoformat(), "facts": facts}, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
