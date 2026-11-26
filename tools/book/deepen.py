#!/usr/bin/env python3
"""投稿の2本目の一覧リンクを、その話のお店・催しの1件ページへ付け替える（11/26 関東 akari #1168 と同じ形）。

11/25 オーナー「関西も少ないけど、関東もっと少ないな」「どっちも頑張れ」。
odekake・dekiru の枠で、文に出てくる催し・お店の1件ページ（links/o/<id>.html・links/kaiten/<日付-印>.html）があれば、
一覧（/odekake・/koyo・/illumination・/hatsumode・/ima・/kaiten）へのリンクをそのページに替える。印 ?f= はそのまま。
URL のすぐ前の短い1行（「〜は、こちら。」など）は、行き先に合う1行に替える。

使い方：
  python3 tools/book/deepen.py schedule/D.json          書き換えて、1件ページの本数を出す
  python3 tools/book/deepen.py --check schedule/D.json  書き換えずに、付け替えられる枠を出すだけ（postlink.py も使う）
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
HOST = "https://kansai.townnote.app"
TYPES = ("odekake", "dekiru", "sokuhou")
LIST_URL = re.compile(r"https://kansai\.townnote\.app/(?:odekake|koyo|illumination|hatsumode|ima|kaiten)(?:-[a-z]+)?(?:\.html)?/?(?=[?#\s]|$)")
ONE_URL = re.compile(r"kansai\.townnote\.app/(?:o|kaiten)/[0-9a-z-]+")
LEAD = {"o": "地図と行き方、近くのほかのおでかけは、こちら。", "kaiten": "開く日・場所・地図、近くの新しいお店は、こちら。"}


def norm(s):
    return re.sub(r"\W", "", s or "").lower()


_IDX = None


def index():
    """[(種類, 印, 名前の言葉のリスト)]。名前は1件ページの h1。"""
    global _IDX
    if _IDX is not None:
        return _IDX
    _IDX = []
    for kind in ("o", "kaiten"):
        for f in glob.glob(os.path.join(ROOT, "links", kind, "*.html")):
            try:
                m = re.search(r"<h1[^>]*>([^<]+)", open(f, encoding="utf-8").read())
            except Exception:
                continue
            if not m:
                continue
            toks = [norm(t) for t in re.split(r"[\s　（）()・「」『』｜|]+", m.group(1))]
            toks = [t for t in toks if len(t) >= 2 and not re.fullmatch(r"\d+", t)]
            if toks and len(toks[0]) >= 3:
                _IDX.append((kind, os.path.basename(f)[:-5], toks))
    return _IDX


def find(text):
    """1行目に名前が出てくる1件ページ（種類, 印）。名前の頭の言葉が文にあり、合った字数がいちばん多い1つ。並んだら付けない。"""
    t = norm(text)
    best, score, tie = None, 0, False
    for kind, key, toks in index():
        if toks[0] not in t:
            continue
        if kind == "kaiten" and f"{int(key[4:6])}/{int(key[6:8])}" not in text:  # 開店は日付も同じ時だけ（同じ建物の別の日の改装に付けない）
            continue
        s = sum(len(x) for x in toks if x in t)
        if s > score:
            best, score, tie = (kind, key), s, False
        elif s == score and best and best != (kind, key):
            tie = True
    return None if tie else best


def deepen(item):
    """1枠（schedule の1件か drafts の1件）を付け替える。替えた時は (種類, 印)、替えない時は None。"""
    if item.get("type") not in TYPES:
        return None
    parts = [item.get("threads_text") or ""] + list(item.get("threads_thread") or [])
    if not any(LIST_URL.search(p) for p in parts) or any(ONE_URL.search(p) for p in parts):
        return None
    hit = find(parts[0].split("\n")[0])  # 1行目（その投稿の主役）だけで探す。本文の会場名（例：コラボカフェの入る建物）には付けない
    if not hit:
        return None
    kind, key = hit
    for i, p in enumerate(parts):
        m = LIST_URL.search(p)
        if not m:
            continue
        lines = p.split("\n")
        for j, ln in enumerate(lines):
            if LIST_URL.search(ln):
                lines[j] = LIST_URL.sub(f"{HOST}/{kind}/{key}", ln, count=1)
                if j and 0 < len(lines[j - 1]) <= 40 and "出典" not in lines[j - 1] and "http" not in lines[j - 1]:
                    lines[j - 1] = LEAD[kind]
                break
        parts[i] = "\n".join(lines)
        break
    if len(parts[0]) > 500 or any(len(p) > 500 for p in parts[1:]):
        return None
    item["threads_text"], item["threads_thread"] = parts[0], parts[1:]
    return hit


def deepen_x(item):
    """X の2本目（x_thread）の一覧リンクも、1行目の店・催しの1件ページへ（11/27 門 #1281 が速報の X にも1件ページを求める）。
    「〜を、日付と地図で：URL」の1行は「開く日・場所・地図：URL」に替える。"""
    if item.get("type") not in TYPES:
        return None
    xs = list(item.get("x_thread") or [])
    if not xs or not any(LIST_URL.search(p) for p in xs) or any(ONE_URL.search(p) for p in xs):
        return None
    hit = find((item.get("x_text") or "").split("\n")[0])
    if not hit:
        return None
    kind, key = hit
    for i, p in enumerate(xs):
        if not LIST_URL.search(p):
            continue
        lines = p.split("\n")
        for j, ln in enumerate(lines):
            m = LIST_URL.search(ln)
            if m:
                pre = ln[:m.start()]
                url = LIST_URL.sub(f"{HOST}/{kind}/{key}", ln[m.start():], count=1)
                lines[j] = (("開く日・場所・地図：" if kind == "kaiten" else "地図と行き方：") + url) if pre.endswith("：") and len(pre) <= 30 else pre + url
                break
        xs[i] = "\n".join(lines)
        break
    item["x_thread"] = xs
    return hit


def main(argv):
    check = "--check" in argv
    files = [a for a in argv if not a.startswith("--")]
    for fn in files:
        rows = json.load(open(fn, encoding="utf-8"))
        rows = rows if isinstance(rows, list) else [rows]
        hits = []
        for r in rows:
            rr = dict(r) if check else r
            h = deepen(rr) or deepen_x(rr)
            if h:
                hits.append((r.get("slot"), f"/{h[0]}/{h[1]}"))
        if not check:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
                f.write("\n")
        one = sum(1 for r in rows if any(ONE_URL.search(p or "") for p in [r.get("threads_text")] + list(r.get("threads_thread") or [])))
        for s, u in hits:
            print(("付け替えられる" if check else "付け替えた"), s, u)
        print(f"1件ページのリンク：Threads {one if not check else one}本" + ("（付け替えると +%d）" % len(hits) if check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
