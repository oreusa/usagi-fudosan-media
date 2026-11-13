#!/usr/bin/env python3
"""決まりの見回り（11/13 オーナー「各々の仕組みがあるのにそれから間違ってないか、改善するところはないかも見回りのひとつだろ」）。

台帳の MIMAWARI は「毎日の仕事が動いたか」を見る。こちらは「仕組みが、その目的とオーナーの決まりのとおりか」を見る。
仕組みごとに 目的・決まり・機械で確かめる事 を1行ずつ持ち、毎朝 link-stats（08:30）で回して stats/kimari.json に書く。
台帳（gakushu.py）は × の行を「止まっている物」のすぐ下に出し、朝の回はオーナーへの報告の上の方に写す。
オーナーに言われた決まりを1つ覚えたら、ここに1行足す（文の決まりだけで終わらせない）。
使い方：python3 tools/allcheck/kimari.py 2026-11-14
"""
import glob
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JST = timezone(timedelta(hours=9))
AK = "https://raw.githubusercontent.com/oreusa/akari-auto/main/"


def R(*p):
    return os.path.join(ROOT, *p)


def load(p, d=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def akari(path):
    """関東（燈）のファイル。読めない時は None（網の都合＝× にはしない）"""
    try:
        with urllib.request.urlopen(urllib.request.Request(AK + path, headers={"User-Agent": "townnote-kimari"}), timeout=20) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return None


def html_texts(pattern):
    for f in sorted(glob.glob(R(pattern), recursive=True)):
        yield f, open(f, encoding="utf-8", errors="ignore").read()


ROWS = []


def rule(name, purpose, kimari, ok, detail, te):
    """ok は True（○）・False（×）・None（確かめられない）"""
    ROWS.append({"name": name, "purpose": purpose, "kimari": kimari, "ok": ok, "detail": detail, "te": te})


def main(day):
    today = date.fromisoformat(day)
    now = datetime.now(JST)

    # 1 関西の申し込み＝反響（オーナーへの相談）を取る場所
    bad = [os.path.relpath(f, R("links")) for f, t in html_texts("links/**/*.html")
           if re.search(r"px\.a8\.net|ieul\.jp|sumai-step|home4u|lifull.*satei", t)]
    rule("関西の申し込み（反響）", "関西のお家の相談をオーナーに届ける", "関西のページに売却・査定のアフィリエイト（A8・一括査定）を出さない（11/13 オーナー「関西は反響とるんじゃなかったか？」）",
         not bad, f"売却系のアフィリエイトがあるページ {len(bad)}枚" + (f"（{', '.join(bad[:5])}）" if bad else ""), "そのページから外す。関西の売却の道は /moushikomi だけ")

    # 2 申し込みはお名前を必ずもらう
    mo = open(R("links", "moushikomi.html"), encoding="utf-8").read()
    nm_req = bool(re.search(r'id="nm"[^>]*required', mo))
    ng_hits = [os.path.relpath(f, ROOT) for f, t in html_texts("links/**/*.html")
               if "/shindan" not in f and re.search(r"名前なしでも|お名前は要りません|名前は要りません",
                                                     re.sub(r'<a [^>]*href="/jikka/shindan[^"]*"[^>]*>.*?</a>', "", t, flags=re.S))]  # 3問診断は申し込みではない（名前の要らない診断）
    rule("申し込みの形", "名前のある相談だけを受ける", "申し込みは必ずお名前（名字だけでも）をもらう。名前なしの入口は作らない（11/12 オーナー）",
         nm_req and not ng_hits, ("お名前の欄が必須" if nm_req else "お名前の欄が必須でない") + (f"・名前なしの言葉 {len(ng_hits)}枚（{', '.join(ng_hits[:3])}）" if ng_hits else ""),
         "links/moushikomi.html の nm に required。言葉はページから外す")

    # 3 関西と関東の投稿は同じ型・同じ本数（関東は＋PR1本）
    cfg = load(R("tools", "book", "config.json"), {})
    tab = next((t for t in cfg.get("tables", []) if t.get("from", "0") <= day <= t.get("to", "9")), cfg.get("base", {}))
    kansai_n = len([k for k, v in tab.get("slots", {}).items() if v.get("th") is not False])  # X だけの枠（x07〜）は別に数える
    ks = akari(f"schedule/{day}.json")
    if ks is None:
        rule("投稿の本数（関西と関東）", "両方で同じ型を回して、くらべて学ぶ", "関東は関西と同じ型・同じ本数＋PR1本（11/13 オーナー「一緒で、ってお願いしたはず」）", None, "関東の予定表が読めない", "akari schedule/きょう.json を見る")
    else:
        try:
            kp = json.loads(ks).get("posts", [])
        except Exception:
            kp = []
        rule("投稿の本数（関西と関東）", "両方で同じ型を回して、くらべて学ぶ", "関東は関西と同じ型・同じ本数＋PR1本（11/13 オーナー「一緒で、ってお願いしたはず」）",
             len(kp) == kansai_n + 1, f"関西 {kansai_n}本・関東 {len(kp)}本（線：関東＝関西＋1）", "少ない側の予定表を直す。本数を変える時は両方同時（config.json と akari docs/nightly-prompt.md）")

    # 4 関西の門：予約の前に全部の枠を機械で通す
    g = load(R("state", "gate", day + ".json"))
    if day < "2026-11-14":
        gok, gd = None, "門は 11/14 から"
    elif now.date() == today and now.hour < 7:
        gok, gd = None, "まだ 06:23 の回の前"
    elif g is None:
        gok, gd = False, "きょうの門の結果が無い（06:23 の回が schedule/きょう.json を書いていない）"
    else:
        gok, gd = g.get("bad", 1) == 0, f"× {g.get('bad')} 枠"
    rule("関西の門（予約の前の点検）", "変な投稿を出さない", "門で ○ の枠だけを予約する（11/13 オーナー「甘い」「ガチれ」）", gok, gd,
         "06:23 の回（投稿スレッド）が動いたか。× の枠は drafts を直して schedule/D.json を書き直す")

    # 4b X の速報（11/13 owner「X も利用しろ、人口はめちゃくちゃ多い」）
    xs = {k: v for k, v in tab.get("slots", {}).items() if v.get("th") is False}
    if xs and g is not None:
        xok = sum(1 for k in xs if (g.get("slots", {}).get(k) or {}).get("ok"))
        rule("X の速報（関西）", "X の人の多さを入口にする", "X は Threads と別に1日8本（開店・閉店・新駅・工事の速報が主役・本文にリンクなし）", xok == len(xs),
             f"○ {xok}／{len(xs)} 枠", "06:23 の回で速報を10件集める。足りない日は路線の順位・催しで埋める")

    # 5 機械の予約：失敗0・二重0
    bk = load(R("state", "booked", day + ".json"), {})
    errs = [s for s, r in bk.items() if "error" in r]
    ba = load(R("state", "buffer_after.json"), {})
    berr = len(ba.get("error", []))
    rule("関西の機械の予約", "決まった時刻に必ず出す", "予約の失敗は30分後にやり直し、失敗のまま残さない", not errs and not berr,
         f"予約の失敗 {len(errs)}枠{('（' + ', '.join(errs) + '）') if errs else ''}・Buffer の失敗 {berr}本", "state/booked/きょう.json の error を読み、文か絵を直す")

    # 6 投稿の数字の機械
    tk = load(R("stats", "toukou.json"), {})
    at = (tk.get("machine") or {}).get("at", "")
    fresh = bool(at) and (now - datetime.fromisoformat(at)).total_seconds() < 26 * 3600
    rule("投稿の数字（機械）", "どの型が見られたかを毎日学ぶ", "数字は機械が毎日取る（Claude の手で取らない）", fresh, f"最後に取った時 {at or '無い'}",
         "Actions の metrics.yml を見る")

    # 7 ROOM：毎日たくさん載せる
    rd = akari("notes/room-daihon.md")
    if rd is None:
        rule("楽天ROOM（台本）", "夜（GPT）が毎日たくさん載せる", "台本は毎日・40件より多く（11/13 オーナー「100倍楽天roomやれ」）", None, "台本が読めない", "akari page.yml を見る")
    else:
        up = re.search(r"更新：(\d{4}-\d\d-\d\d)", rd)
        n = re.search(r"件数：(\d+)件", rd)
        okr = bool(up and up.group(1) >= (today - timedelta(days=1)).isoformat() and n and int(n.group(1)) >= 40)
        rule("楽天ROOM（台本）", "夜（GPT）が毎日たくさん載せる", "台本は毎日・40件より多く（11/13 オーナー「100倍楽天roomやれ」）", okr,
             f"台本の日付 {up.group(1) if up else '無い'}・{n.group(1) if n else '?'}件", "akari scripts/room_auto.py と page.yml を見る")

    # 8 広告の断り：アフィリエイトのあるページは上下に「広告（PR）」
    miss = []
    for f, t in html_texts("links/**/*.html"):
        if re.search(r"hb\.afl\.rakuten|px\.a8\.net|ck\.jp\.ap\.valuecommerce|af\.moshimo", t) and "広告" not in t and "PR" not in t:
            miss.append(os.path.relpath(f, R("links")))
    rule("広告の断り（関西）", "ステマにしない", "アフィリエイトのあるページには「広告（PR）」の断りを入れる（カードごとの印はつけない）", not miss,
         f"断りの無いページ {len(miss)}枚" + (f"（{', '.join(miss[:5])}）" if miss else ""), "ページの上か下に1行足す")

    # 9 お客さんのページに中の名前を出さない（ngcheck と同じ言葉）
    ng = load(R("tools", "allcheck", "ngwords.json"), {"words": []})
    W = [(re.compile(rx), why) for rx, why in ng["words"]]
    hit = []
    for f, t in html_texts("links/**/*.html"):
        if re.search(r"mihon|preview|-try\.html|_mihon|okaimono-live|otoku|/googl", f):
            continue
        body = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<!--.*?-->|<[^>]+>", " ", t, flags=re.S)
        for a in ng.get("allow", []):
            body = body.replace(a, "")
        for rx, why in W:
            if rx.search(body):
                hit.append(f"{os.path.relpath(f, R('links'))}（{why}）")
                break
    rule("お客さんの画面の言葉", "中の事情を見せない", "中の名前・使わない言葉をお客さんのページに出さない", not hit, f"{len(hit)}枚" + (f"（{', '.join(hit[:3])}）" if hit else ""),
         "tools/allcheck/ngcheck.py links で場所を出して直す")

    out = {"day": day, "at": now.isoformat(timespec="seconds"), "bad": sum(1 for r in ROWS if r["ok"] is False), "rows": ROWS}
    json.dump(out, open(R("stats", "kimari.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in ROWS:
        print(("○" if r["ok"] else "×" if r["ok"] is False else "？") + f" {r['name']}｜{r['detail']}")
    print(f"決まりと違う物 {out['bad']} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else datetime.now(JST).date().isoformat()))
