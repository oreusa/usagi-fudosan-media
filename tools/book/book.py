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


def create(svc, texts, due_utc, topic=None, image=None, alt="", draft=False, video=None):
    items = [{"text": t} for t in texts]
    asset = [{"image": {"url": image, "metadata": {"altText": alt or "HPの画面"}}}] if image else None
    if video:
        asset = [{"video": {"url": video}}]
    meta = {}
    if svc == "twitter":
        meta["twitter"] = {"thread": items} if len(items) > 1 else {}
        if image or video:
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
            if not g.get("th", True):
                rec["threads"] = "X だけの枠"
            elif ("threads", key) in have:
                rec["threads"] = "もうある"
            else:
                # 11/27 オーナー「投稿ヤバくない？」：Threads が 11/20 から落ちた（X は横ばい）。11/28〜30 は半分の枠を絵なしでくらべる（関東 akari scripts/book.py と同じ式）
                _noimg = "2026-11-28" <= d <= "2026-11-30" and (datetime.fromisoformat(d).toordinal() + int(dr["time"][:2])) % 2 == 1
                rec["threads"] = create("threads", [t for t in th if t.strip()], due_utc, dr.get("threads_topic"),
                                    None if _noimg else dr.get("image_url"), dr.get("image_alt"))["id"]
                if dr.get("image_url"): rec["threads_img"] = 0 if _noimg else 1
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


# ---- 11/17 オーナー「リール動画をxにも投稿、朝2つアカウントに」「Threadsはどうする？動画載せる？」「これからそうしよう、フォロワー集め」
# 毎朝インスタに出すおでかけリール（ig/reels/D.json）の同じ動画を、X はリールと同じ時刻、Threads は 10:30 に出す。
# 動画（media/reels/…mp4）ができてから・出る150分前から予約。予約の後に動画を作り直したら、出る10分より前なら古い予約を消して入れ直す。
REEL_SNS = (("twitter", None), ("threads", "10:30"))
REEL_LEAD = 150
REEL_LIST = "https://kansai.townnote.app/links/"
DELETE = 'mutation($i:DeletePostInput!){deletePost(input:$i){__typename}}'


def x_weight(t):
    """X の数え方：URL は23、半角は1、日本語などは2。上限280"""
    import re
    n = 0
    for part in re.split(r"(https?://\S+)", t):
        if part.startswith("http"):
            n += 23
        else:
            n += sum(1 if ord(c) < 0x1100 else 2 for c in part)
    return n


def reel_texts(spec, svc, d):
    """リールの台本（公式の文で答え合わせ済み）から X・Threads の文を作る。X はリンクなし・タグ2つまで。"""
    tx = spec.get("text") or {}
    place = (tx.get("place") or "").split("｜")
    name = place[0].strip()
    city = place[1].strip() if len(place) > 1 else ""
    head = f"{name}（{city}）" if city else name
    title = "。".join(t for t in (tx.get("title") or []) if t)
    info = [f"・{a} {b}" for a, b in (tx.get("info") or []) if a and b]
    note = "出かける前に、公式ページで確かめてください。"
    if svc == "twitter":
        tags = "#関西おでかけ #" + name.replace(" ", "").replace("　", "")
        rows = list(info)
        while True:
            t = "\n".join([head, title, ""] + rows + ["", note, "", tags])
            if x_weight(t) <= 280 or not rows:
                return [t] if x_weight(t) <= 280 else []
            rows.pop()
    body = "\n".join([head, title, ""] + ([tx["map_caption"]] if tx.get("map_caption") else []) + info
                     + ["", note, "", CFG.get("last_line", "")]).strip()
    out = [body]
    if spec.get("source"):
        out.append("出典：公式ページ\n" + spec["source"])
    out.append("日付と地図でさがせる、関西おでかけリスト\n" + REEL_LIST + "?f=th-reel-" + d[5:7] + d[8:10])
    return out


def book_reel_sns(d, now):
    sp = os.path.join(ROOT, "ig", "reels", d + ".json")
    spec = load(sp, None)
    hold = os.path.join(ROOT, "ig", "reels-hold")
    # 11/23 インスタと同じ門：STOP があっても、その日の OK-<日> があれば出す（11/20〜23 は STOP のせいで X・Threads だけ出ていなかった）
    if not spec or (os.path.exists(os.path.join(hold, "STOP")) and not os.path.exists(os.path.join(hold, "OK-" + d))):
        return
    url = spec.get("video_url") or ""
    mp4 = os.path.join(ROOT, "media", "reels", url.rsplit("/", 1)[-1]) if url else ""
    if not mp4 or not os.path.exists(mp4) or os.path.exists(os.path.join(ROOT, "stats", "reel-fail", d + ".txt")):
        return  # 動画がまだ（作っている・止まっている）。インスタと同じ物しか出さない
    bp = os.path.join(ROOT, "state", "booked", d + ".json")
    booked = load(bp, {})
    changed = False
    for svc, hhmm in REEL_SNS:
        due = datetime.fromisoformat(f"{d}T{hhmm or spec.get('time') or '07:30'}:00+09:00")
        mins = (due - now).total_seconds() / 60
        key = "reel_" + svc
        rec = booked.get(key) or {}
        if rec.get("id") and rec.get("url") != url and mins > 10:  # 動画を作り直した → 古い予約を消して入れ直す
            try:
                r = gql(DELETE, {"i": {"id": rec["id"]}}).get("deletePost") or {}
                if "Error" in str(r.get("__typename", "")):
                    raise RuntimeError(r.get("__typename"))
            except Exception as e:
                rec["error"] = "古い予約を消せない：" + str(e)[:200]
                booked[key], changed = rec, True
                continue
            rec = {"replaced": rec["id"]}
        if rec.get("id") or rec.get("tries", 0) >= 3 or not (5 < mins <= REEL_LEAD):
            continue
        texts = reel_texts(spec, svc, d)
        if not texts:
            rec["error"] = "文が X の280に入らない"
            booked[key], changed = rec, True
            continue
        rec["tries"] = rec.get("tries", 0) + 1
        try:
            p = create(svc, texts, due.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                       topic=spec.get("tab") if svc == "threads" else None, video=url)
            rec.update({"id": p["id"], "url": url, "time": due.strftime("%H:%M"), "texts": texts,
                        "at": now.isoformat(timespec="seconds")})
            rec.pop("error", None)
        except Exception as e:
            rec["error"] = str(e)[:300]
        booked[key], changed = rec, True
        print(f"リール {svc} {d}：{rec}")
    if changed:
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
        texts = ["【予約係の試し】これは出ない下書きです", "2本目の試し https://kansai.townnote.app/?f=th-test-0000a"]
        p = create(svc, texts, due_utc, topic="大阪" if svc == "threads" else None, image=img, alt="試し", draft=True)
        print(f"試しの下書き {svc}: {p}")


if __name__ == "__main__":
    now = datetime.now(JST)
    if "--reel-text" in sys.argv:  # 文だけ見る：python3 tools/book/book.py --reel-text 2026-11-18
        d = sys.argv[-1]
        sp = load(os.path.join(ROOT, "ig", "reels", d + ".json"), {})
        for svc, _ in REEL_SNS:
            for t in reel_texts(sp, svc, d):
                print(f"--- {svc} ({x_weight(t) if svc == 'twitter' else len(t)})\n{t}")
        sys.exit(0)
    if "--test" in sys.argv:
        test(now)
        sys.exit(0)
    for d in (now.date(), now.date() + timedelta(days=1)):
        book_day(d.isoformat(), now)
        if CFG.get("machine_booking") and os.environ.get("BUFFER_API_KEY"):
            try:
                book_reel_sns(d.isoformat(), now)
            except Exception as e:
                print(f"リールの X・Threads 予約×：{e}")
    try:
        after(now)
    except Exception as e:
        print(f"出たかの確かめができない：{e}")
