"""インスタのリールの数字をとる（stats/reels.json・stats/reels.md）。11/11 月。
それまでリールの再生の数を測っていなかった（オーナー「全て作り替えてくれ」）。
ig-post-reel.yml の最後に動く。6時間に1回だけ。フォロワーの数も毎日1行残す。
見る物：再生・届いた人・平均で見た秒・保存・シェア・いいね・コメント（直近30本）。"""
import json, os, sys, time, urllib.request, urllib.parse, datetime as dt

GV = os.environ.get("GV", "v23.0"); PT = os.environ["PT"]
JST = dt.timezone(dt.timedelta(hours=9))
OUT = "stats/reels.json"


def call(path, **q):
    q["access_token"] = PT
    try:
        with urllib.request.urlopen(f"https://graph.facebook.com/{GV}/{path}?" + urllib.parse.urlencode(q), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return {"error": json.loads(e.read().decode() or "{}").get("error", {"code": e.code})}
        except Exception:
            return {"error": {"code": e.code}}
    except Exception as e:
        return {"error": {"message": str(e)[:120]}}


def main():
    now = dt.datetime.now(JST)
    old = {}
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except Exception:
        pass
    if old.get("at") and "--force" not in sys.argv:
        if (now - dt.datetime.fromisoformat(old["at"])).total_seconds() < 6 * 3600:
            print("reel stats: 6時間たっていない"); return
    ig = json.load(open("ig/setup.json"))["ig_user_id"]
    me = call(ig, fields="followers_count,media_count")
    med = call(f"{ig}/media", fields="id,caption,permalink,timestamp,media_product_type,like_count,comments_count", limit="30")
    if "error" in med:
        print("reel stats ×", med["error"]); return
    rows = []; err = None
    for m in med.get("data", []):
        if m.get("media_product_type") != "REELS":
            continue
        ins = call(f"{m['id']}/insights", metric="views,reach,saved,shares,total_interactions,ig_reels_avg_watch_time")
        v = {}
        if "error" in ins:
            err = ins["error"]
        for x in ins.get("data", []):
            v[x["name"]] = (x.get("values") or [{}])[0].get("value")
        t = dt.datetime.strptime(m["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).astimezone(JST)
        cap = [l for l in (m.get("caption") or "").split("\n") if l.strip()]
        rows.append({"at": t.strftime("%Y-%m-%d %H:%M"), "title": (cap[1] if len(cap) > 1 else (cap or [""])[0])[:40], "url": m.get("permalink"),
                     "views": v.get("views"), "reach": v.get("reach"), "avg_sec": round((v.get("ig_reels_avg_watch_time") or 0) / 1000, 1) if v.get("ig_reels_avg_watch_time") is not None else None,
                     "saved": v.get("saved"), "shares": v.get("shares"), "likes": m.get("like_count"), "comments": m.get("comments_count")})
        time.sleep(0.3)
    fol = dict(old.get("followers") or {})
    if me.get("followers_count") is not None:
        fol[now.date().isoformat()] = me["followers_count"]
    out = {"at": now.isoformat(timespec="minutes"), "followers": dict(sorted(fol.items())[-120:]), "media_count": me.get("media_count"), "reels": rows}
    if err:
        out["error"] = {k: err.get(k) for k in ("code", "message") if err.get(k)}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    vs = [r["views"] for r in rows if r["views"] is not None]
    L = ["# リールの数字（インスタ・関西）", "", f"更新：{now.strftime('%Y-%m-%d %H:%M')}（機械が6時間に1回とる。tools/reel_stats.py）", ""]
    fk = sorted(fol.items())
    if fk:
        L.append(f"- フォロワー：{fk[-1][1]}人" + (f"（{fk[0][0]} は {fk[0][1]}人）" if len(fk) > 1 else ""))
    if vs:
        s = sorted(vs)
        L.append(f"- 直近{len(vs)}本の再生：まん中 {s[len(s)//2]}・いちばん多い {s[-1]}・いちばん少ない {s[0]}")
    if err:
        L.append(f"- とれなかった数字がある：{err.get('message', err)}")
    L += ["", "| 出した時刻 | 中身 | 再生 | 届いた人 | 平均で見た秒 | 保存 | シェア | いいね |", "|---|---|---|---|---|---|---|---|"]
    f = lambda x: "—" if x is None else str(x)
    for r in rows:
        L.append(f"| {r['at'][5:]} | {r['title']} | {f(r['views'])} | {f(r['reach'])} | {f(r['avg_sec'])} | {f(r['saved'])} | {f(r['shares'])} | {f(r['likes'])} |")
    open("stats/reels.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("reel stats", len(rows), "本", "フォロワー", me.get("followers_count"), "エラー" if err else "")


if __name__ == "__main__":
    main()
