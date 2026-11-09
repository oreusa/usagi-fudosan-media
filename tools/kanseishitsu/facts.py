"""管制室に出す「機械の点検結果」を、点検の記録からそのまま作る（11/9 オーナー「アーチファクトがちゃんと報告になってない」「間違いのないように見れる仕組みにしろ」）。

月が手で数えたり、まとめたりしない。点検の記録（allcheck ブランチ・stats/linkcheck.md・notes/gakushu.json）を読んで、
そのまま JSON にする。朝の点検（9:20）はこの JSON を管制室の morning_report の facts に入れるだけ。

使い方（usagi-fudosan-media で）:
  git fetch origin allcheck
  python3 tools/kanseishitsu/facts.py > /tmp/facts.json
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
    now = datetime.datetime.now(JST)
    facts = {"made_at": now.strftime("%Y-%m-%dT%H:%M+09:00"), "allcheck": allcheck(), "linkcheck": linkcheck(), "gakushu": gakushu()}
    json.dump({"date": now.date().isoformat(), "facts": facts}, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
