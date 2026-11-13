#!/usr/bin/env python3
"""関西の機械の予約係（11/13〜。燈の scripts/book.py と同じ形）。

門（gate.py）を通った枠だけを Buffer に予約する。門で × の枠は、何があっても予約しない。
  1. きょうとあすの schedule/D.json を門に通し、state/gate/D.json を書く
  2. BUFFER_API_KEY があり、config.json の machine_booking が true の時だけ：
     ○ の枠のうち、まだ予約していない・いまから lead_min 分以内・5分より先の物を予約する
     （DB の drafts で booked が付いている枠＝人の予約係が入れた枠は飛ばす）
  3. 予約した物の出たか・失敗したか（sent / error）を state/booked/D.json に書く
キーがない時は 1 だけをして終わる（人の予約係は state/gate/D.json の ○ の枠だけを予約する）。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gate  # noqa: E402

ROOT = gate.ROOT
CFG = gate.CFG
JST = timezone(timedelta(hours=9))
URL = "https://api.buffer.com"

CREATE = """mutation($input: CreatePostInput!) { createPost(input: $input) { __typename
  ... on PostActionSuccess { post { id status dueAt } } ... on MutationError { message } } }"""
POSTS = """query($o: OrganizationId!, $ch: [ChannelId!], $s: DateTime, $e: DateTime) {
  posts(first: 50, input: {organizationId: $o, filter: {channelIds: $ch, status: [scheduled, sent, error],
        dueAt: {start: $s, end: $e}}}) { edges { node { id channelService dueAt status } } } }"""


def gql(query, variables):
    key = (os.environ.get("BUFFER_API_KEY") or "").strip()
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "townnote-book"})
    last = None
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
            if data.get("errors"):
                raise RuntimeError("Buffer: " + "; ".join(e.get("message", "") for e in data["errors"])[:300])
            return data["data"]
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2 ** (i + 1))
    raise RuntimeError(f"Buffer に届かない：{last}")


def create(svc, texts, due_utc, topic=None, image=None, alt="", draft=False):
    items = [{"text": t} for t in texts]
    asset = [{"image": {"url": image, "metadata": {"altText": alt or "HPの画面"}}}] if image else None
    meta = {}
    if svc == "twitter":
        meta["twitter"] = {"thread": items} if len(items) > 1 else {}
        if image:
            meta["twitter"]["isAiGenerated"] = True
    else:
        meta["threads"] = {"type": "post", **({"thread": items} if len(items) > 1 else {}),
                           **({"topic": topic} if topic else {})}
    if asset and len(items) > 1:
        items[0]["assets"] = asset
    inp = {"channelId": CFG["channels"][svc], "text": texts[0], "schedulingType": "automatic",
           "mode": "customScheduled", "dueAt": due_utc, "source": "townnote-book"}
    meta = {k: v for k, v in meta.items() if v}
    if meta:
        inp["metadata"] = meta
    if asset:
        inp["assets"] = asset
    if draft:
        inp["saveToDraft"] = True
    res = gql(CREATE, {"input": inp})["createPost"]
    if res["__typename"] != "PostActionSuccess":
        raise RuntimeError(f"{res['__typename']}: {res.get('message', '')}")
    return res["post"]


def load(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def book_day(d, now):
    code, slots = gate.run(d, write=True)
    if slots is None or not CFG.get("machine_booking") or not os.environ.get("BUFFER_API_KEY"):
        return
    if d < CFG.get("machine_from", "9999"):
        return
    # 二重の予約をしない：その日に Buffer にもう入っている（人の予約係が入れた）時刻と媒体は飛ばす
    s0 = datetime.fromisoformat(f"{d}T00:00:00+09:00").astimezone(timezone.utc)
    z = lambda t: t.isoformat().replace("+00:00", "Z")
    have = {(r["channelService"], r["dueAt"][:16]) for r in
            (x["node"] for x in gql(POSTS, {"o": CFG["organizationId"], "ch": list(CFG["channels"].values()),
                                            "s": z(s0), "e": z(s0 + timedelta(days=1))})["posts"]["edges"] or [])}
    rows = {r.get("slot"): r for r in load(os.path.join(ROOT, "schedule", d + ".json"), []) if r.get("date") == d}
    bp = os.path.join(ROOT, "state", "booked", d + ".json")
    booked = load(bp, {})
    for slot, g in slots.items():
        dr = rows.get(slot)
        if not g["ok"] or not dr or (slot in booked and "error" not in booked[slot]) or (dr.get("booked") or {}):
            continue
        due = datetime.fromisoformat(f"{d}T{dr['time']}:00+09:00")
        if not (now + timedelta(minutes=5) < due <= now + timedelta(minutes=CFG.get("lead_min", 720))):
            continue
        due_utc = due.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        rec = {"time": dr["time"], "digest": g["digest"], "at": now.isoformat(timespec="seconds")}
        key = due_utc[:16]
        try:
            th = gate.parts(dr, "threads")
            if ("threads", key) in have:
                rec["threads"] = "もうある"
            else:
                rec["threads"] = create("threads", [t for t in th if t.strip()], due_utc, dr.get("threads_topic"),
                                    dr.get("image_url"), dr.get("image_alt"))["id"]
            xs = [t for t in gate.parts(dr, "x") if t.strip()]
            if g.get("x") and xs and ("twitter", key) in have:
                rec["twitter"] = "もうある"
            elif g.get("x") and xs:
                rec["twitter"] = create("twitter", xs, due_utc, image=dr.get("image_url"), alt=dr.get("image_alt"))["id"]
        except Exception as e:
            rec["error"] = str(e)[:300]  # 次の回（30分後）にもう一度試す。「もうある」で二重にはならない
        booked[slot] = rec
        print(f"予約 {d} {slot} {dr['time']}：{rec}")
    os.makedirs(os.path.dirname(bp), exist_ok=True)
    json.dump(booked, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def after(now):
    """きのう〜あすの予約が出たか・失敗したかを書く（失敗は見回りが朝いちばん上に出す）"""
    if not os.environ.get("BUFFER_API_KEY"):
        return
    s = (now - timedelta(days=1)).replace(hour=0, minute=0).astimezone(timezone.utc)
    e = (now + timedelta(days=1)).replace(hour=23, minute=59).astimezone(timezone.utc)
    z = lambda t: t.isoformat().replace("+00:00", "Z")
    d = gql(POSTS, {"o": CFG["organizationId"], "ch": list(CFG["channels"].values()), "s": z(s), "e": z(e)})
    rows = [x["node"] for x in d["posts"]["edges"] or []]
    out = {"at": now.isoformat(timespec="seconds"), "error": [r for r in rows if r["status"] == "error"],
           "count": {k: sum(r["status"] == k for r in rows) for k in ("scheduled", "sent", "error")}}
    os.makedirs(os.path.join(ROOT, "state"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "state", "buffer_after.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"Buffer：{out['count']}")


def test(now):
    """鍵と形の確かめ：Threads と X に下書き（出ない）を1本ずつ作る。作った下書きは人が消す"""
    due = (now + timedelta(days=2)).replace(hour=4, minute=0, second=0, microsecond=0)
    due_utc = due.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    img = "https://oreusa.github.io/usagi-fudosan-media/media/post/kaitai-ranking.jpg"
    for svc in ("threads", "twitter"):
        texts = ["【予約係の試し】これは出ない下書きです", "2本目の試し https://townnote.pages.dev/?f=th-test-0000a"]
        p = create(svc, texts, due_utc, topic="大阪" if svc == "threads" else None, image=img, alt="試し", draft=True)
        print(f"試しの下書き {svc}: {p}")


if __name__ == "__main__":
    now = datetime.now(JST)
    if "--test" in sys.argv:
        test(now)
        sys.exit(0)
    for d in (now.date(), now.date() + timedelta(days=1)):
        book_day(d.isoformat(), now)
    try:
        after(now)
    except Exception as e:
        print(f"出たかの確かめができない：{e}")
