#!/usr/bin/env python3
"""投稿の見出しとリンク先・絵が合っているかの機械の点検（11/13 オーナー「なんか変じゃない？」）。

11/13 12:00 の関西の投稿で、店の開業（ルクア サウス）の話なのに、リンクは大阪市北区の土地相場、
絵も土地相場のページだった。8:00 の実家の投稿（売れた値段の話）も、絵が解体の補助のページだった。
決まりの文（DB rules/content）は直したが、文だけでは忘れるので、予約の前にこれで止める。

使い方：python3 tools/allcheck/postlink.py 下書き.json …
  下書き.json は DB drafts の1件（threads_text・x_text・threads_thread・image_url・type）か、その配列。
  1件でも × があれば終わりのコードは 1。予約しない。
"""
import json
import re
import sys

# 型ごとに、リンクしてよいページの頭（townnote.pages.dev の後ろ）
OK = {
    "rank": ("/ranking",),
    "kata": ("/ranking", "/illumination", "/kaitai-", "/machi/"),
    "hitoeki": ("/machi/",),
    "jikka": ("/jikka/", "/machi/", "/kaitai-"),
    "kaitai": ("/kaitai-", "/hojo"),
    "hojo": ("/hojo", "/kaitai-"),
    "odekake": ("/koyo", "/illumination", "/hatsumode", "/odekake", "/o/", "/ima"),
    "dekiru": ("/odekake", "/ima", "/koyo", "/illumination", "/hatsumode", "/o/", "/machi/"),
}

# 見出し（1行目）の言葉 → 行き先はこのどれかでないといけない
WORDS = [
    (r"開業|オープン|店舗|売り場|商業施設|新店", ("/odekake", "/ima", "/o/"), "店・施設の開業の話"),
    (r"売れた|成約|中古一戸建て|平均は", ("/jikka/", "/machi/"), "売れた値段の話"),
    (r"紅葉|もみじ", ("/koyo", "/odekake", "/o/"), "紅葉の話"),
    (r"イルミ|ライトアップ", ("/illumination", "/koyo", "/odekake", "/o/"), "イルミ・ライトアップの話"),
    (r"解体|補助金|空き家", ("/kaitai-", "/hojo", "/jikka/"), "解体・補助の話"),
]

# 絵の名前（media/post/<名前>.jpg）の頭 → 合うページの頭
PIC = [
    ("odekake-odekake-", "/odekake"), ("odekake-koyo", "/koyo"), ("odekake-illumination", "/illumination"),
    ("odekake-hatsumode", "/hatsumode"), ("rank-", "/ranking"), ("machi-", "/machi/"),
    ("jikka-", "/jikka/"), ("kaitai-ranking", "/kaitai-ranking"), ("kaitai-", "/kaitai-"),
]

LINK_RE = re.compile(r"https://townnote\.pages\.dev(/[^\s?#]*)")


def texts_of(d):
    out = [d.get("threads_text") or "", d.get("x_text") or ""]
    for k in ("threads_thread", "x_thread"):
        v = d.get(k) or []
        out += v if isinstance(v, list) else [str(v)]
    return [t for t in out if isinstance(t, str)]


def head_of(d):
    t = (d.get("threads_text") or d.get("x_text") or "").strip()
    return t.splitlines()[0] if t else ""


def check(d):
    bad = []
    links = []
    for t in texts_of(d):
        links += LINK_RE.findall(t)
    links = list(dict.fromkeys(links))
    head = head_of(d)
    typ = d.get("type") or ""
    if typ in OK:
        for p in links:
            if not p.startswith(OK[typ]):
                bad.append(f"型 {typ} なのにリンク先が {p}")
    for pat, ok, what in WORDS:
        if re.search(pat, head) and links and not any(p.startswith(ok) for p in links):
            bad.append(f"見出しは{what}なのに、リンク先が {', '.join(links)}（{' / '.join(ok)} のどれかへ）")
            break
    img = d.get("image_url") or ""
    m = re.search(r"/media/post/([a-z0-9-]+)\.jpg", img)
    if m and links:
        name = m.group(1)
        for pre, page in PIC:
            if name.startswith(pre):
                if not any(p.startswith(page) for p in links):
                    bad.append(f"絵 {name} はページ {page} の絵なのに、リンク先は {', '.join(links)}")
                break
    return head, links, bad


def main(paths):
    n_bad = 0
    for f in paths:
        data = json.load(open(f, encoding="utf-8"))
        rows = data if isinstance(data, list) else [data]
        for d in rows:
            head, links, bad = check(d)
            mark = "×" if bad else "○"
            print(f"{mark} {d.get('id') or d.get('slot') or f}｜{head[:40]}｜{' '.join(links) or 'リンクなし'}")
            for b in bad:
                print("   → " + b)
            n_bad += bool(bad)
    print(f"× {n_bad} 件")
    return 1 if n_bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
