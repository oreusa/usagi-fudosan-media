"""11/18 オーナー「しっかり仕組みの確認と改善」「そんなミスダメだろ」
関東の公開（akari page.yml）が点検で止まったのに、1時間以上だれも気づかなかった（11/17 にも関東の /kaitai が3日止まっていた）。
→ 公開・毎日の機械が「最後に失敗した」「決めた時間より長く成功していない」を1回で全部見る。
見回り（13:47・18:47・23:47）と朝の回の最初に回す。× が1つでもあれば、その回のうちに直す。

使い方: python3 tools/allcheck/kikai.py   （gh が使える所。Actions では GH_TOKEN を渡す）
× の時は終わりの値が 1。"""
import datetime as dt
import json
import subprocess
import sys

# (リポジトリ, 機械, 何をするか, 成功が空いてよい時間)  ※ GitHub の時刻起動は3〜4時間遅れるので、毎日の物は30時間
KIKAI = [
    ("oreusa/akari-auto", "page.yml", "関東HPを作って公開（1日2回）", 16),
    ("oreusa/akari-auto", "linkcheck.yml", "関東のリンク点検", 30),
    ("oreusa/akari-auto", "ranking.yml", "関東ランキング", 30),
    ("oreusa/akari-auto", "metrics.yml", "関東の数字", 30),
    ("oreusa/usagi-fudosan-media", "link-stats.yml", "関西HPの毎日の作り直し・数字", 30),
    ("oreusa/usagi-fudosan-media", "kaiten-collect.yml", "開店・閉店ニュース集め（6時間ごと）", 10),
    # 11/18 GitHub の30分おきの起動は数時間抜けることがある（11/17 は9時間空いた）。予約は前もって入るので12時間
    ("oreusa/usagi-fudosan-media", "book.yml", "X・Threads の予約", 12),
    ("oreusa/usagi-fudosan-media", "allcheck.yml", "全ページ点検", 30),
    ("oreusa/usagi-fudosan-media", "formcheck.yml", "申し込みの送信テスト", 16),
    ("oreusa/usagi-fudosan-media", "headcheck.yml", "ページの頭の点検", 30),
    ("oreusa/usagi-fudosan-media", "indexnow.yml", "Bing へ送る", 30),
    ("oreusa/usagi-fudosan-media", "post-img.yml", "投稿の絵", 30),
    ("oreusa/usagi-fudosan-media", "metrics.yml", "関西の数字", 16),
    # 関西は点検が公開を止めない（赤になるだけ）。赤のまま出ている＝お客さんに見えている
    # 11/25 オーナー「全部は全部だよ」：関西と関東の違い（ページの種類・中身・無いアドレス・投稿の予定・動画）。赤＝違いがある＝その回に直す（stats/ryouhou.md）
    ("oreusa/usagi-fudosan-media", "ryouhou.yml", "関西と関東の違い（stats/ryouhou.md）", 99999),
    ("oreusa/usagi-fudosan-media", "ngcheck.yml", "関西のページの見せてはいけない言葉", 99999),
]


# 11/26 オーナー「ちゃんと全部仕組みづくり」：上の表に載せ忘れた機械は見られていなかった（ig-post-reel・townnotes-geo）。
# 時刻で動く機械（cron のある .github/workflows）を両方のリポジトリから自分で探し、表に無い物も30時間で見る。
def _kakure():
    import os, re
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    have = {(r, w) for r, w, _, _ in KIKAI}
    out = []
    for repo in ("oreusa/usagi-fudosan-media", "oreusa/akari-auto"):
        d = os.path.join(base, repo.split("/")[1], ".github", "workflows")
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith((".yml", ".yaml")) and (repo, f) not in have:
                if re.search(r"^\s*-\s*cron:", open(os.path.join(d, f), encoding="utf-8").read(), re.M):
                    out.append((repo, f, f"表に無い時刻の機械 {f}", 30))
    return out


KIKAI += _kakure()

def gh(path):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[:200])
    return json.loads(out.stdout)


def t(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


now = dt.datetime.now(dt.timezone.utc)
bad = []
rows = []
for repo, wf, what, hours in KIKAI:
    try:
        runs = gh(f"repos/{repo}/actions/workflows/{wf}/runs?per_page=15&exclude_pull_requests=true")["workflow_runs"]
    except Exception as e:  # 読めない＝見えていない、も × にする
        bad.append(f"× {what}（{repo.split('/')[1]} {wf}）：読めない {e}")
        continue
    runs = [r for r in runs if r.get("head_branch") in ("main", None) or r.get("event") in ("schedule", "workflow_dispatch")]
    done = [r for r in runs if r["status"] == "completed" and r["conclusion"] not in ("cancelled", "skipped")]
    ok = [r for r in done if r["conclusion"] == "success"]
    last = done[0] if done else None
    age = (now - t(ok[0]["updated_at"])).total_seconds() / 3600 if ok else None
    mark = "○"
    why = ""
    if last and last["conclusion"] != "success":
        mark, why = "×", f"最後の回が {last['conclusion']}（{t(last['updated_at']).astimezone(dt.timezone(dt.timedelta(hours=9))):%m/%d %H:%M}）{last['html_url']}"
    elif age is None or age > hours:
        mark, why = "×", f"{hours}時間より長く成功していない（最後の成功 {'なし' if age is None else f'{age:.0f}時間前'}）"
    line = f"{mark} {what}（{repo.split('/')[1]} {wf}）" + (f"：{why}" if why else f"：最後の成功 {age:.0f}時間前")
    rows.append(line)
    if mark == "×":
        bad.append(line)

# 関西HPの公開（Cloudflare Pages）：main の最新の印が success か
try:
    sha = gh("repos/oreusa/usagi-fudosan-media/commits/main")["sha"]
    cr = gh(f"repos/oreusa/usagi-fudosan-media/commits/{sha}/check-runs")["check_runs"]
    cf = [c for c in cr if c["name"] == "Cloudflare Pages"]
    if cf and cf[0]["status"] == "completed" and cf[0]["conclusion"] != "success":
        bad.append(f"× 関西HPの公開（Cloudflare Pages）：main {sha[:7]} が {cf[0]['conclusion']}")
    else:
        rows.append(f"○ 関西HPの公開（Cloudflare Pages）：main {sha[:7]} {cf[0]['status'] if cf else '印なし'}")
except Exception as e:
    bad.append(f"× 関西HPの公開：読めない {e}")

# 11/20：formcheck.yml は「動いた」だけで○になり、中身の「申し込みが送れない」を15時間見逃した（11/19 18時〜）。結果の中身も見る。
try:
    import json, os
    fc = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "stats", "formcheck.json"), encoding="utf-8"))
    for k, s in fc.get("sites", {}).items():
        ng = [r["name"] + "：" + r.get("why", "") for r in s.get("rows", []) if not r.get("ok")]
        if ng:
            bad.append(f"× 申し込みが最後まで送れない（{k}・{fc.get('at')}）：" + "／".join(ng))
        else:
            rows.append(f"○ 申し込みの通し（{k}・{fc.get('at')}）")
except Exception as e:
    bad.append(f"× 申し込みの通し：stats/formcheck.json が読めない {e}")

# 11/26 オーナー「bufferとかその他ツールにも使用制限あるんじゃなかった？」「管理する担当も」：
# GitHub Pages は公開するサイトが1GBまで。関西は出し終わったリール動画で約2GBになっていた（#1260 で消した）。
# main の中身の大きさを数え、900MB を越えたら ×（media/reels の古い mp4 を消す。HP からの参照は無い）。
import os as _os
for _repo, _dir in (("oreusa/usagi-fudosan-media", "usagi-fudosan-media"), ("oreusa/akari-auto", "akari-auto")):
    _path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))), _dir)
    try:
        subprocess.run(["git", "-C", _path, "fetch", "-q", "origin", "main"], timeout=120, check=True)
        out = subprocess.run(["git", "-C", _path, "ls-tree", "-r", "-l", "origin/main"], capture_output=True, text=True, timeout=60).stdout
        tot, big = 0, {}
        for ln in out.splitlines():
            f = ln.split()
            if len(f) >= 5 and f[3].isdigit():
                n = int(f[3]); tot += n
                top = "/".join(ln.split("\t", 1)[1].split("/")[:2])
                big[top] = big.get(top, 0) + n
        top3 = "・".join(f"{k} {v/1e6:.0f}MB" for k, v in sorted(big.items(), key=lambda x: -x[1])[:3])
        line = f"サイトの大きさ（{_dir}・GitHub Pages の上限1GB）：{tot/1e6:.0f}MB（大きい所 {top3}）"
        if tot > 900e6:
            bad.append("× " + line + " → 出し終わった media/reels の mp4 などを消す")
        else:
            rows.append("○ " + line)
    except Exception as e:
        rows.append(f"－ サイトの大きさ（{_dir}）：数えられない {e}")

print("\n".join(rows))
if bad:
    print("\n直すもの：")
    print("\n".join(bad))
    sys.exit(1)
print("\n機械：全部 ○")
