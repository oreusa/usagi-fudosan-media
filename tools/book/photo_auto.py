# 関西の投稿の写真の表紙を機械で作る（11/19 オーナー「投稿に使う写真も劇的に変えれる」「関西は？」）。関東 akari scripts/photo_auto.py と同じ考え。
# book.yml で門と予約の前に動く。今日の schedule/D.json の odekake の枠（まだ予約していない物）を tools/post_img/photo-pick.json の写真と照らし、
# 合えば tools/post_img/photo.js で写真の表紙を作り、その枠の image_url を raw.githubusercontent の絵に替える（Pages を待たずに Buffer が取れる）。
# 写真は photo-pick.json に月が目で見て入れた物だけ（催しそのもの・季節が合う・幅900px以上・cr あり）。合わない枠は今の絵のまま。
# 使い方：python3 tools/book/photo_auto.py [--need]
import json, os, re, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JST = timezone(timedelta(hours=9))
RAW = "https://raw.githubusercontent.com/oreusa/usagi-fudosan-media/main/media/post/"
WD = "月火水木金土日"


def load(p, d):
    try:
        with open(os.path.join(R, p), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return d


def in_season(pk, day):
    md = day[5:]
    a, b = pk.get("from", "01-01"), pk.get("to", "12-31")
    return a <= md <= b if a <= b else (md >= a or md <= b)


def first_line(r):
    return ((r.get("threads_text") or r.get("x_text") or "").strip().split("\n") or [""])[0]


def pick_for(r, day, picks):
    t = first_line(r) + " " + (r.get("x_text") or "").split("\n")[0]
    for pk in picks:
        if all(w in t for w in pk["all"]) and (not pk.get("any") or any(w in t for w in pk["any"])) and in_season(pk, day):
            return pk
    return None


def date_bits(t, day):
    """1行目の最初の日付（M/D）と、その後の「まで」「から」"""
    m = re.search(r"(\d{1,2})/(\d{1,2})(?:（[^）]*）)?(〜\d{1,2}(?:/\d{1,2})?(?:（[^）]*）)?)?", t)
    if not m:
        return None, None, ""
    mo, d = int(m.group(1)), int(m.group(2))
    rest = t[m.end():m.end() + 6]
    unit = "まで" if "まで" in rest else "から" if ("から" in rest or m.group(3)) else ""
    try:
        wd = WD[datetime(int(day[:4]) + (1 if mo < int(day[5:7]) else 0), mo, d).weekday()]
    except ValueError:
        return None, None, ""
    return f"{mo}.{d:02d}", unit, f"{mo}/{d}（{wd}）{unit}"


def specs_for(r, day, pk):
    big, unit, when = date_bits(first_line(r) + " " + (r.get("x_text") or ""), day)
    base = {"name": f"photo-{day[5:].replace('-', '')}-{r['slot']}", "im": pk["file"], "cr": pk["cr"], "pos": pk.get("pos", "50% 50%"),
            "pill": (pk.get("area", "") + ("　" + when if when else "")).strip(), "big": big, "unit": unit, "en": pk.get("en", ""), "nowrap": True}
    cap = pk.get("cap", "")
    return [dict(base, head=pk["head"], cap=cap), dict(base, head=pk["head"], cap=cap, hs=60)]


def main():
    now = datetime.now(JST)
    day = now.date().isoformat()
    sp = os.path.join(R, "schedule", day + ".json")
    rows = load(f"schedule/{day}.json", []) or []
    picks = (load("tools/post_img/photo-pick.json", {}) or {}).get("items") or []
    booked = load(f"state/booked/{day}.json", {}) or {}
    todo = []
    for r in rows:
        if r.get("date") != day or r.get("type") != "odekake" or "card-photo-" in str(r.get("image_url", "")):
            continue
        b = booked.get(r.get("slot")) or {}
        if (b and "error" not in b) or r.get("booked"):
            continue
        try:
            due = datetime.fromisoformat(f"{day}T{r['time']}:00+09:00")
        except (KeyError, ValueError):
            continue
        if due <= now + timedelta(minutes=10):
            continue
        pk = pick_for(r, day, picks)
        if pk:
            todo.append((r, specs_for(r, day, pk)))
    if "--need" in sys.argv:
        print("yes" if todo else "no")
        return 0
    n = 0
    for r, tries in todo:
        for s in tries:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump([s], f, ensure_ascii=False)
            p = subprocess.run(["node", os.path.join(R, "tools", "post_img", "photo.js"), f.name], capture_output=True, text=True, timeout=120)
            out = os.path.join(R, "media", "post", f"card-{s['name']}.jpg")
            if "作った 1 枚" in p.stdout and os.path.exists(out):
                r["image_url"] = RAW + f"card-{s['name']}.jpg?v={int(time.time()) % 100000000:x}"
                r["image_alt"] = re.sub(r"<[^>]+>", "", s["head"].replace("<br>", "　")) + "（写真：" + s["cr"] + "）"
                print(f"写真の表紙：{r['slot']} {s['im']}")
                n += 1
                break
            print(f"写真の表紙×：{r['slot']} {p.stdout.strip()[-120:]} {p.stderr.strip()[-200:]}")
    if n:
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
