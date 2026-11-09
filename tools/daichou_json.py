"""台帳 notes/daichou.md を管制室の daichou/latest の形（JSON）にする。
11/9 オーナー「記録してないのは月の管理体制にかなり問題がある」→ 管制室に台帳を出し、確かめた日が14日より古い行は黄、「未確認」は赤。
使い方: python3 tools/daichou_json.py [notes/daichou.md] > daichou.json（標準エラーに「未確認◯・古い◯」）"""
import datetime, json, re, sys

src = sys.argv[1] if len(sys.argv) > 1 else "notes/daichou.md"
today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()


def iso(s):
    m = re.search(r"(\d{1,2})/(\d{1,2})", s or "")
    if not m:
        return ""
    y = today.year - (1 if int(m.group(1)) > today.month + 1 else 0)
    return f"{y}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


secs, cur = {}, None
for line in open(src, encoding="utf-8"):
    h = re.match(r"##\s*(\d)\.", line)
    if h:
        cur = h.group(1)
        secs[cur] = []
    elif cur and line.startswith("|") and not re.match(r"\|\s*-", line):
        secs[cur].append([c.strip().replace("**", "") for c in line.strip().strip("|").split("|")])
for k in secs:
    secs[k] = secs[k][1:]  # 見出しの行を外す

acc = [{"kind": r[0], "name": r[1], "who": r[2], "id": r[3] if r[3] != "—" else "", "state": r[4],
        "checked": iso(r[5]) or ("未確認" if "未確認" in r[5] else ""), "checked_label": r[5]} for r in secs.get("1", []) if len(r) >= 6]
pro = [{"kind": r[0], "name": r[1], "who": r[2], "state": r[3] + ("・報酬 " + r[4] if r[4] and r[4] != "—" else ""),
        "checked": "未確認" if "未確認" in r[4] else today.isoformat(), "checked_label": ""} for r in secs.get("2", []) if len(r) >= 5]
tasks = [{"what": r[0], "who": r[1], "state": r[2], "due": r[3] if r[3] != "—" else ""} for r in secs.get("3", []) if len(r) >= 4]


def age(c):
    try:
        return (today - datetime.date.fromisoformat(c)).days
    except Exception:
        return None


red = sum(1 for r in acc + pro if "未確認" in (r["checked"] + r["state"]))
yel = sum(1 for r in acc + pro if "未確認" not in (r["checked"] + r["state"]) and (age(r["checked"]) is None or age(r["checked"]) > 14))
print(json.dumps({"date": today.isoformat(), "accounts": acc, "programs": pro, "tasks": tasks, "red": red, "yellow": yel}, ensure_ascii=False, indent=1))
print(f"台帳：未確認{red}・古い{yel}", file=sys.stderr)
