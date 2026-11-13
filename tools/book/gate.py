#!/usr/bin/env python3
"""関西の投稿の「門」（11/13 オーナー「甘い。もっと本格的に作らないと」）。

予約の前に、その日の下書きを全部ここに通す。× が1つでもある枠は予約しない。
人（Claude）が「点検を忘れた」「読み落とした」で変な投稿が出ないように、
決まりの文ではなく機械で止める。燈（関東）の scripts/check.py と同じ考え方。

使い方：
  python3 tools/book/gate.py 2026-11-14          … schedule/2026-11-14.json を調べる
  python3 tools/book/gate.py 2026-11-14 --write  … 結果を state/gate/2026-11-14.json に書く（機械の予約係・投稿担当はこれを読む）
schedule/D.json は DB drafts の date==D の文書をそのまま並べた配列（会議・06:23 の回が書く）。
終わりのコード：× 0 なら 0、× があれば 1、ファイルが無ければ 2。
"""
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "allcheck"))
import postlink  # noqa: E402

CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"), encoding="utf-8"))
NG = json.load(open(os.path.join(ROOT, "tools", "allcheck", "ngwords.json"), encoding="utf-8"))
NG_W = [(re.compile(rx), why) for rx, why in NG["words"]]
NG_ALLOW = NG.get("allow", [])

LINK_RE = re.compile(r"https?://[^\s　）)」]+")
TOWN_RE = re.compile(r"https://townnote\.pages\.dev(/[^\s?#]*)?(\?[^\s#]*)?")
MARK_RE = re.compile(r"^(th|x|ig)-([a-z0-9]+)-(\d{4})([a-z]+\d*)$")


def table_for(d):
    """その日の枠の表（config.json の tables のうち、from <= d <= to に当たる物。無ければ base）"""
    for t in CFG["tables"]:
        if t.get("from", "0000") <= d <= t.get("to", "9999"):
            return t
    return CFG["base"]


def x_len(text):
    """X の数え方：URL は23、全角は2、半角は1（Buffer は280まで）"""
    n = 0
    rest = LINK_RE.sub(lambda m: "\0", text)
    n += 23 * rest.count("\0")
    for ch in rest.replace("\0", ""):
        n += 2 if unicodedata.east_asian_width(ch) in "WFA" else 1
    return n


def parts(d, svc):
    if svc == "threads":
        return [d.get("threads_text") or ""] + list(d.get("threads_thread") or [])
    return [d.get("x_text") or ""] + list(d.get("x_thread") or [])


def ng_words(text):
    t = text
    for a in NG_ALLOW:
        t = t.replace(a, "")
    out = []
    for rx, why in NG_W:
        m = rx.search(t)
        if m:
            out.append(f"使わない言葉（{why}）：…{t[max(0, m.start() - 10):m.end() + 10]}…")
    return out


def check_one(dr, d, tab, seen_heads):
    bad, warn = [], []
    slot = dr.get("slot") or "?"
    want = tab["slots"].get(slot)
    if dr.get("date") != d:
        bad.append(f"date が {dr.get('date')}（{d} ではない）")
    if not want:
        bad.append(f"枠 {slot} はこの日の表に無い（表：{', '.join(tab['slots'])}）")
    else:
        if dr.get("time") != want["time"]:
            bad.append(f"時刻が {dr.get('time')}（表では {want['time']}）")
        if want.get("type") and dr.get("type") not in want["type"]:
            bad.append(f"型が {dr.get('type')}（表では {' か '.join(want['type'])}）")
    th = parts(dr, "threads")
    # 11/13 owner「X も利用しろ」：X だけの枠（th:false）は Threads を見ない。本文にリンクを入れない（link:false）
    th_on = not (want and want.get("th") is False)
    if not th_on:
        if any(t.strip() for t in th):
            bad.append("この枠は X だけなのに Threads の文がある（Threads は別の枠に）")
        th = [""]
    elif not th[0].strip():
        bad.append("Threads の1本目が空")
    if th_on and not (dr.get("threads_topic") or "").strip():
        bad.append("Threads のトピック（threads_topic）が無い")
    for i, t in enumerate(th):
        if len(t) > 500:
            bad.append(f"Threads の{i + 1}本目が {len(t)} 字（500まで）")
    xs = parts(dr, "x")
    want_x = bool(want and want.get("x"))
    if want_x and not xs[0].strip():
        bad.append("この枠は X にも出す日なのに x_text が空")
    for i, t in enumerate(xs):
        if t.strip() and x_len(t) > 280:
            bad.append(f"X の{i + 1}本目が {x_len(t)}（全角2・URL23 で280まで）")
    # 見出しとリンク先・絵（postlink.py と同じ点検）
    _, links, pl_bad = postlink.check(dr)
    bad += pl_bad
    # 1本目の最後の行（決まりの1行）
    line = tab.get("last_line_override") or CFG.get("last_line")
    if want and line and th_on:
        body = th[0].rstrip()
        last = body.splitlines()[-1] if body else ""
        for old in CFG.get("old_last_lines", []):
            if old in th[0] and old != line:
                bad.append(f"古い最後の行「{old}」が残っている")
        if last != line:
            bad.append(f"1本目の最後の行が「{last[:30]}」（決まりは「{line}」）")
    # リンクの印と行き先
    mmdd = d[5:7] + d[8:10]
    for svc, ps in (("threads", th), ("x", xs)):
        pre = "th" if svc == "threads" else "x"
        for t in ps:
            for m in LINK_RE.finditer(t):
                u = m.group(0)
                if "github.io" in u or "oreusa" in u or "workers.dev" in u:
                    bad.append(f"お客さんに見せないアドレス {u[:60]}（HPは https://townnote.pages.dev/）")
            for m in TOWN_RE.finditer(t):
                q = m.group(2) or ""
                f = re.search(r"[?&]f=([^&#\s]+)", q)
                if not f:
                    bad.append(f"{svc} のHPのリンクに印（?f=）が無い：{m.group(0)[:60]}")
                    continue
                mk = MARK_RE.match(f.group(1))
                if not mk:
                    bad.append(f"印の形が違う：{f.group(1)}（媒体-型-MMDD枠）")
                    continue
                if mk.group(1) != pre:
                    bad.append(f"{svc} の文なのに印が {mk.group(1)}-（{pre}- にする）")
                if mk.group(3) != mmdd:
                    bad.append(f"印の日付が {mk.group(3)}（{mmdd} にする）")
    if want and want.get("link", True) and not links:
        bad.append("HP（townnote.pages.dev）へのリンクが無い")
    if want and want.get("link") is False and LINK_RE.search(xs[0]):
        bad.append("X の1本目にリンクがある（この枠は本文にリンクを入れない。要るなら返信の2本目に）")
    if want and want.get("x") and xs[0].strip():
        tags = re.findall(r"#\S+", xs[0])
        if len(tags) > 2:
            bad.append(f"X のハッシュタグが {len(tags)} 個（2つまで：市の名前と駅の名前）")
    # 使わない言葉
    for t in th + xs:
        bad += ng_words(t)
    # 絵：ファイルが本当にあるか
    img = dr.get("image_url") or ""
    m = re.search(r"/media/post/([A-Za-z0-9_-]+)\.jpg", img)
    if img and not m:
        bad.append(f"絵のアドレスの形が違う：{img[:60]}")
    elif m and not os.path.exists(os.path.join(ROOT, "media", "post", m.group(1) + ".jpg")):
        bad.append(f"絵 media/post/{m.group(1)}.jpg がリポジトリに無い")
    if not img:
        warn.append("絵が無い（文字だけで出る）")
    # 11/13 owner「訳分からん投稿」：「下のリンク」「こちら。」と書いたのに、その本にも次の本にもリンクが無い
    for svc, ps in (("Threads", th), ("X", xs)):
        for i, t in enumerate(ps):
            if re.search(r"下のリンク|リンクで見られ|リンクから見られ|は、こちら。", t):
                nxt = ps[i + 1] if i + 1 < len(ps) else ""
                if not (LINK_RE.search(t) or LINK_RE.search(nxt)):
                    bad.append(f"{svc} の{i + 1}本目に「下のリンク・こちら」と書いたのにリンクが無い")
    # 同じ日に同じ見出し
    first = th[0] if th[0].strip() else xs[0]
    head = first.strip().splitlines()[0] if first.strip() else ""
    if head and head in seen_heads:
        bad.append(f"同じ見出しが {seen_heads[head]} にもある")
    seen_heads.setdefault(head, slot)
    return head, bad, warn


def digest(dr):
    keep = {k: dr.get(k) for k in ("slot", "time", "threads_text", "threads_thread", "x_text", "x_thread",
                                    "image_url", "threads_topic")}
    return hashlib.sha256(json.dumps(keep, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def run(d, write=False):
    fp = os.path.join(ROOT, "schedule", d + ".json")
    if not os.path.exists(fp):
        print(f"schedule/{d}.json がありません")
        return 2, None
    data = json.load(open(fp, encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("posts", [])
    rows = [r for r in rows if r.get("date") == d]
    tab = table_for(d)
    seen, out, n_bad = {}, {}, 0
    for dr in sorted(rows, key=lambda r: r.get("time") or ""):
        head, bad, warn = check_one(dr, d, tab, seen)
        slot = dr.get("slot") or "?"
        out[slot] = {"ok": not bad, "time": dr.get("time"), "head": head[:60], "bad": bad, "warn": warn,
                     "digest": digest(dr), "x": bool(tab["slots"].get(slot, {}).get("x")),
                     "th": tab["slots"].get(slot, {}).get("th") is not False}
        n_bad += bool(bad)
        print(f"{'○' if not bad else '×'} {slot} {dr.get('time')}｜{head[:40]}")
        for b in bad:
            print("   × " + b)
        for w in warn:
            print("   △ " + w)
    for slot, w in tab["slots"].items():
        if slot not in out:
            n_bad += 1
            out[slot] = {"ok": False, "time": w["time"], "head": "", "bad": ["下書きが無い（抜け）"], "warn": [],
                         "digest": "", "x": bool(w.get("x")), "th": w.get("th") is not False}
            print(f"× {slot} {w['time']}｜下書きが無い（抜け）")
    print(f"× {n_bad} 枠（全部で {len(out)} 枠）")
    if write:
        os.makedirs(os.path.join(ROOT, "state", "gate"), exist_ok=True)
        json.dump({"date": d, "bad": n_bad, "slots": out}, open(os.path.join(ROOT, "state", "gate", d + ".json"), "w",
                  encoding="utf-8"), ensure_ascii=False, indent=1)
    return (1 if n_bad else 0), out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    date.fromisoformat(args[0])
    sys.exit(run(args[0], "--write" in sys.argv)[0])
