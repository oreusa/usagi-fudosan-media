"""11/25 オーナー「全部見直してっていつもお願いしてるのに全部の意味わかってないよね」「改善して仕組みも改善して」「全部は全部だよ」
関西（kansai.townnote.app・usagi）と関東（kanto.townnote.app・akari）を、本番の全部の種類のページ・投稿の予定・動画で並べ、
場所のほかに違う所を × で出す。毎日 ryouhou.yml が回し、stats/ryouhou.md に書く。kikai.py が最後の回の × を拾う。
使い方: python3 tools/allcheck/ryouhou.py   （本番に届く所＝GitHub Actions で）"""
import datetime as dt, json, re, subprocess, sys, urllib.request, collections, os

H = {"kansai": "https://kansai.townnote.app", "kanto": "https://kanto.townnote.app"}
UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
# 片方だけでよい物（理由つき）。足す時は理由を書く
ONLY_OK = {"gyosha": "関西だけの業者の窓口（11/23 決め）", "ranking": "駅の乗降の数字は関西だけ（関東は国の駅の数字が無い）",
           "okaimono": "おかいものは関東が作り、関西からはリンク", "furusato": "ふるさと納税は関東が作り、関西からはリンク",
           "tanka": "おかいもの（関東）", "nesage": "おかいもの（関東）", "kaimawari": "両方にある（関西は shin/）", "privacy": "",
           "tomari": "", "ima": "", "uru": "", "sagasu": "", "hatsumode": ""}
# 11/25 量の違いが「載せる物の数」から来る物（中身の作りは同じ）。× にせず理由を書いて残す。足す時は理由を書く
SOFT = {("kaiten", "字の量"): "開店の数が違う（関西 約100件・関東 約210件）。カードの作りは同じ",
        ("kaiten", "内リンク"): "開店の数が違う（店1件に1リンク）。11/26 関西 101件・関東 210件",
        ("kaiten", "1件へのリンク"): "開店の数が違う（店1件に1リンク）。11/26 関西 101件・関東 210件",
        ("ranking", "字の量"): "関西だけ駅の乗降の数字の欄がある（関東は国の駅の数字が無い）"}
JST_NOW = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(hours=9)
TODAY = JST_NOW.date()
out, bad = [], []


def get(u, tries=2):
    for _ in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30)
            return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, ""
        except Exception:
            pass
    return 0, ""


def kind(path):
    p = path.strip("/")
    if not p: return "top"
    if "/" in p: return p.split("/")[0] + "/"
    return re.sub(r"-.*", "-*", p)


def feat(t):
    b = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", b)
    links = re.findall(r'href="(/[^"#?]*)', t)
    return {"字の量": len(re.sub(r"\s", "", txt)), "内リンク": len(links), "1件へのリンク": len([l for l in links if re.match(r"/(o|kaiten)/", l)]),
            "写真": len(re.findall(r"<img", t)), "題": bool(re.search(r"<title>[^<]{5,}", t)), "説明": bool(re.search(r'name="description" content="[^"]{20,}', t)),
            "canonical": bool(re.search(r'rel="canonical"', t)), "og:image": bool(re.search(r"og:image", t)), "h1": bool(re.search(r"<h1", t)),
            "構造化": ",".join(sorted(set(re.findall(r'"@type"\s*:\s*"(Event|ItemList|BreadcrumbList|Place|LocalBusiness|Store|FAQPage|Article|WebSite|Organization)"', t)))),
            "パンくず": bool(re.search(r"BreadcrumbList|class=\"[^\"]*(crumb|pan)", t)), "数える": bool(re.search(r"data-k=|/c\?|sendBeacon", t)),
            "noindex": bool(re.search(r'name="robots" content="[^"]*noindex', t)),
            # 11/28 owner「毎回それあるな」：関東の開店閉店だけ前の作りのままだった（字や数は同じで見逃した）。使う土台の部品と独自の style の数をくらべる
            "作り": " ".join(sorted(set(re.findall(r'(?:href|src)="/shin/([a-z0-9]+\.(?:css|js))', t)))) + f" style{len(re.findall(r'<style(?![^>]*data-kyu-old)', t))}"}


def mark(a, b, k):
    if isinstance(a, bool) or isinstance(a, str): return a != b
    m = max(a, b)
    return m >= 5 and min(a, b) < m * 0.5  # 半分より少ない


# ---------- 1. ページの種類 ----------
sm = {}
for r, h in H.items():
    st, x = get(h + "/sitemap-all.xml")
    urls = re.findall(r"<loc>([^<]+)</loc>", x)
    by = collections.defaultdict(list)
    for u in urls:
        by[kind(u.replace(h, ""))].append(u)
    sm[r] = by
out.append(f"# 関西と関東の並べ（{TODAY} {dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).strftime('%H:%M')}UTC）\n")
out.append("## 1. ページの種類（sitemap-all）\n")
for k in sorted(set(sm["kansai"]) | set(sm["kanto"])):
    a, b = len(sm["kansai"].get(k, [])), len(sm["kanto"].get(k, []))
    base = k.strip("/-*")
    if (a == 0 or b == 0) and base not in ONLY_OK:
        bad.append(f"ページの種類「{k}」が{'関東' if b == 0 else '関西'}に無い（関西{a}・関東{b}）")
        out.append(f"- × {k}：関西 {a}・関東 {b}")
    else:
        out.append(f"- {k}：関西 {a}・関東 {b}{'（' + ONLY_OK.get(base, '') + '）' if (a == 0 or b == 0) else ''}")

# ---------- 2. 同じ種類のページの中身 ----------
out.append("\n## 2. 同じ種類のページの中身（それぞれ新しい方から3枚の平均）\n")
FIX = ["/", "/odekake", "/kaiten", "/koyo", "/illumination", "/jikka", "/kaitai", "/moushikomi", "/sagasu", "/uru", "/tomari", "/ima", "/hatsumode", "/kaimawari", "/chika-kansai|/chika-kanto"]
pairs = []
for k in sorted(set(sm["kansai"]) & set(sm["kanto"])):
    if k in ("top",): continue
    # 11/25 新しい方から3枚だと、片方だけ特別なページ（関西 illumination-muryo）が混ざって比べにならなかった
    # → 10枚以下の種類は全部の平均。多い種類（o/ など）は新しい方から3枚
    na, nb = sm["kansai"][k], sm["kanto"][k]
    pairs.append((k, na if len(na) <= 10 else na[-3:], nb if len(nb) <= 10 else nb[-3:]))
for p in FIX:
    a, b = (p.split("|") + [p])[:2]
    pairs.append(("固定 " + p, [H["kansai"] + a], [H["kanto"] + b]))
for k, ua, ub in pairs:
    fa, fb = [], []
    for u in ua:
        st, t = get(u)
        if st == 200: fa.append(feat(t))
        elif st: bad.append(f"関西 {u} が {st}")
    for u in ub:
        st, t = get(u)
        if st == 200: fb.append(feat(t))
        elif st: bad.append(f"関東 {u} が {st}")
    if not fa or not fb: continue
    def avg(fs, key):
        v = [f[key] for f in fs]
        if isinstance(v[0], bool): return all(v)
        if isinstance(v[0], str): return v[0]
        return round(sum(v) / len(v))
    diffs, soft = [], []
    kb = k.replace("固定 /", "").strip("/")
    for key in fa[0]:
        a, b = avg(fa, key), avg(fb, key)
        if mark(a, b, key):
            (soft if (kb, key) in SOFT else diffs).append(f"{key} 関西 {a}／関東 {b}" + (f"（{SOFT[(kb, key)]}）" if (kb, key) in SOFT else ""))
    if diffs:
        bad.append(f"「{k}」のページ：" + "・".join(diffs))
        out.append(f"- × {k}：" + "・".join(diffs) + f"（例 {ua[-1]} ／ {ub[-1]}）")
    else:
        out.append(f"- {k}：同じ" + ("（量だけ違う：" + "・".join(soft) + "）" if soft else ""))

# ---------- 3. 無いアドレス ----------
out.append("\n## 3. 無いアドレスが 404 を返すか（200 だと Google に中身の無いページと見られる）\n")
for p in ["/o/zzzz0000", "/kaiten/20260101-zzzz", "/machi/zzzz-99", "/jikka/zzzz-99", "/kaitai-zzzz", "/zzzz-nothing"]:
    sa, _ = get(H["kansai"] + p, 1); sb, _ = get(H["kanto"] + p, 1)
    m = "" if sa == sb == 404 else "× "
    if m: bad.append(f"無いアドレス {p}：関西 {sa}・関東 {sb}（両方 404 が正しい）")
    out.append(f"- {m}{p}：関西 {sa}・関東 {sb}")

# ---------- 4. 投稿の予定（きょう・あす） ----------
out.append("\n## 4. 投稿の予定（usagi schedule/D.json ・ akari schedule/D.json）\n")
def raw(repo, path):
    st, t = get(f"https://raw.githubusercontent.com/oreusa/{repo}/main/{path}")
    return json.loads(t) if st == 200 and t.strip() else None
for d in (TODAY, TODAY + dt.timedelta(days=1)):
    ka, kt = raw("usagi-fudosan-media", f"schedule/{d}.json"), raw("akari-auto", f"schedule/{d}.json")
    def summ(posts, host):
        posts = posts if isinstance(posts, list) else (posts or {}).get("posts", [])
        s = json.dumps(posts, ensure_ascii=False)
        links = re.findall(re.escape(host) + r"(/[^\s\"\\?]*)", s)
        return {"本数": len(posts), "HPへのリンク": len(links), "1件ページへ": len([l for l in links if re.match(r"/(o|kaiten)/", l)])}  # 絵は関東が公開の時に作る（photo_auto.py）ので予定では数えない
    if ka is None or kt is None:
        # 11/26 直し：前は UTC の時で見ていて、朝5時（UTC 20時）に「あす無し」「きょうの関西無し」を×にしていた。日本の時で見る
        if (d > TODAY and JST_NOW.hour < 22) or (d == TODAY and ka is None and kt is not None and JST_NOW.hour < 7):  # あすの予定は夜22時ごろ・関西のきょうは朝6:30ごろに出来る
            out.append(f"- {d}：まだ（関西 {'あり' if ka else 'なし'}・関東 {'あり' if kt else 'なし'}）"); continue
        # 11/25 関西のその日の予定は、その日の朝6:30ごろの回で作る決まり（関東は前の晩22時ごろ）。あすの関西が無いのは正しい
        if d == TODAY + dt.timedelta(days=1) and ka is None and kt is not None:
            out.append(f"- {d}：関西 まだ（その日の朝6:30ごろに作る決まり）・関東 あり"); continue
        bad.append(f"{d} の投稿の予定：関西 {'あり' if ka else 'なし'}・関東 {'あり' if kt else 'なし'}")
        out.append(f"- × {d}：関西 {'あり' if ka else 'なし'}・関東 {'あり' if kt else 'なし'}"); continue
    sa, sb = summ(ka, H["kansai"]), summ(kt, H["kanto"])
    diffs = [f"{k} 関西 {sa[k]}／関東 {sb[k]}" for k in sa if mark(sa[k], sb[k], k)]
    if diffs: bad.append(f"{d} の投稿：" + "・".join(diffs))
    out.append(f"- {'× ' if diffs else ''}{d}：関西 {sa}／関東 {sb}")

# ---------- 5. 動画（インスタ・YouTube・TikTok の元） ----------
out.append("\n## 5. その日の動画のファイル\n")
for d in (TODAY, TODAY + dt.timedelta(days=1)):
    a, b = raw("usagi-fudosan-media", f"ig/reels/{d}.json"), raw("akari-auto", f"reel/yt/{d}.json")
    m = "" if (a and b) or (d > TODAY and JST_NOW.hour < 22) else "× "  # あすの動画は夜までに出来る（日本の時で見る）
    if m: bad.append(f"{d} の動画：関西 {'あり' if a else 'なし'}・関東 {'あり' if b else 'なし'}")
    out.append(f"- {m}{d}：関西 {'あり' if a else 'なし'}・関東 {'あり' if b else 'なし'}")

out.insert(1, f"\n**違い {len(bad)} 件**\n" + "".join(f"- × {x}\n" for x in bad))
os.makedirs("stats", exist_ok=True)
open("stats/ryouhou.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
json.dump({"day": str(TODAY), "bad": bad}, open("stats/ryouhou.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("\n".join(out))
sys.exit(1 if bad else 0)
