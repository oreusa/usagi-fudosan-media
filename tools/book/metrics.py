#!/usr/bin/env python3
"""関西の投稿の数字係（11/13〜。燈の scripts/metrics.py と同じ考え）。

きょう・きのう・おとといに出た関西の X・Threads の投稿の数字（閲覧・いいね）を Buffer から取り、
stats/toukou.json の rows に上書きで足す（同じ day・svc・slot は上書き。新しい数字が0で前が大きい時は前を残す）。
kata_count[D] も数え直す。台帳（tools/seichou/gakushu.py）が毎朝これを読む。
それまでは夜 20:33 の Claude の回が手で取っていた（数字を取り忘れる・型の分け方がぶれる）。
使い方：BUFFER_API_KEY を入れて python3 tools/book/metrics.py
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import book  # noqa: E402

ROOT = book.ROOT
JST = book.JST
P = os.path.join(ROOT, "stats", "toukou.json")

Q = """query($o: OrganizationId!, $ch: [ChannelId!], $s: DateTime, $e: DateTime, $after: String) {
  posts(first: 50, after: $after, input: {organizationId: $o,
        filter: {channelIds: $ch, status: [sent], dueAt: {start: $s, end: $e}}}) {
    edges { node { id channelService dueAt sentAt text assets { type } metrics { type value } } }
    pageInfo { hasNextPage endCursor } } }"""


def _kata_fn():
    """台帳と同じ型の分け方を使う（gakushu.py の KATA と kata() をそのまま読む）"""
    src = open(os.path.join(ROOT, "tools", "seichou", "gakushu.py"), encoding="utf-8").read()
    a = src.index("KATA = [")
    b = src.index("_kt = {}")
    ns = {"_r2": re, "re": re}
    exec(src[a:b], ns)
    return ns["kata"]


kata = _kata_fn()


def sched_type(day, hhmm):
    try:
        rows = json.load(open(os.path.join(ROOT, "schedule", day + ".json"), encoding="utf-8"))
    except Exception:
        return ""
    for r in rows:
        if r.get("time") == hhmm:
            return r.get("type") or ""
    return ""


def fetch(day):
    s = datetime.fromisoformat(f"{day}T00:00:00+09:00").astimezone(timezone.utc)
    e = s + timedelta(days=1)
    z = lambda t: t.isoformat().replace("+00:00", "Z")
    out, after = [], None
    while True:
        d = book.gql(Q, {"o": book.CFG["organizationId"], "ch": list(book.CFG["channels"].values()),
                         "s": z(s), "e": z(e), "after": after})["posts"]
        for x in d["edges"] or []:
            n = x["node"]
            due = datetime.fromisoformat(n["dueAt"].replace("Z", "+00:00")).astimezone(JST)
            m = {k["type"]: k["value"] for k in (n.get("metrics") or [])}
            svc = "x" if n["channelService"] == "twitter" else n["channelService"]
            head = ((n.get("text") or "").strip().splitlines() or [""])[0]
            views = m.get("views") if svc == "threads" else m.get("impressions", m.get("views"))
            likes = m.get("likes", m.get("reactions", 0))
            hhmm = due.strftime("%H:%M")
            typ = sched_type(day, hhmm)
            out.append({"day": day, "svc": svc, "slot": hhmm, "type": typ, "head": head,
                        "kata": kata(head) if head else kata(typ), "pic": bool(n.get("assets")),
                        "views": int(views or 0), "likes": int(likes or 0), "_types": sorted(m)})
        if not d["pageInfo"]["hasNextPage"]:
            break
        after = d["pageInfo"]["endCursor"]
    return out


def main():
    if not os.environ.get("BUFFER_API_KEY"):
        print("BUFFER_API_KEY が無いので何もしません")
        return 0
    data = json.load(open(P, encoding="utf-8"))
    rows = data.get("rows", [])
    idx = {(r.get("day"), r.get("svc"), r.get("slot")): i for i, r in enumerate(rows)}
    today = datetime.now(JST).date()
    days = [(today - timedelta(days=b)).isoformat() for b in (0, 1, 2)]
    seen_types = set()
    for day in days:
        new = fetch(day)
        for r in new:
            seen_types.update(r.pop("_types"))
            k = (r["day"], r["svc"], r["slot"])
            if k in idx:
                old = rows[idx[k]]
                if r["views"] == 0 and int(old.get("views") or 0) > 0:
                    r["views"], r["likes"] = old["views"], old.get("likes", 0)
                if not r["type"]:
                    r["type"] = old.get("type", "")
                rows[idx[k]] = {**old, **r}
            else:
                idx[k] = len(rows)
                rows.append(r)
        kc = {"Threads": {}, "X": {}}
        for r in rows:
            if r.get("day") == day:
                b = kc["Threads" if r["svc"] == "threads" else "X"]
                b[r.get("kata") or "そのほか"] = b.get(r.get("kata") or "そのほか", 0) + 1
        data.setdefault("kata_count", {})[day] = kc
        print(f"{day}：{len(new)}本 Threads 閲覧 {sum(r['views'] for r in new if r['svc'] == 'threads')}・X {sum(r['views'] for r in new if r['svc'] == 'x')}")
    # 型の無い行（10/29〜 手で取った頃の行など）にも、台帳と同じ分け方で型を付ける（型が None だと学びの数に入らない）
    for r in rows:
        if not r.get("kata"):
            r["kata"] = kata(r.get("head") or r.get("type") or "")
    for day in {r.get("day") for r in rows}:
        kc = {"Threads": {}, "X": {}}
        for r in rows:
            if r.get("day") == day:
                b = kc["Threads" if r["svc"] == "threads" else "X"]
                b[r["kata"]] = b.get(r["kata"], 0) + 1
        data.setdefault("kata_count", {})[day] = kc
    lim = (today - timedelta(days=60)).isoformat()
    data["rows"] = sorted([r for r in rows if r.get("day", "") >= lim], key=lambda r: (r["day"], r.get("slot", ""), r["svc"]))
    data["kata_count"] = {k: v for k, v in data.get("kata_count", {}).items() if k >= lim}
    data["machine"] = {"at": datetime.now(JST).isoformat(timespec="seconds"), "by": "tools/book/metrics.py", "metric_types": sorted(seen_types)}
    json.dump(data, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
