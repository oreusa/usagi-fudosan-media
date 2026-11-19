"""11/18 月：作業環境からつながらないページを Actions から取って保存する（何でも用）。
使い方: python3 tools/probe/fetch.py 出す所 URL1 URL2 ...（POST は "POST URL 本文"）"""
import os, sys, urllib.request, hashlib, time
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
log = []
for i, u in enumerate(sys.argv[2:]):
    if i and 'duckduckgo' in u: time.sleep(6)   # 11/20 検索は間をあけないと 202 で断られる
    name = hashlib.md5(u.encode()).hexdigest()[:8]
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "ja"}), timeout=60)
        b = r.read(); ct = r.headers.get("Content-Type", "")
        open(os.path.join(out, name), "wb").write(b)
        log.append(f"{name}\t{r.status}\t{len(b)}\t{ct}\t{u}")
    except Exception as e:
        log.append(f"{name}\tERR\t{e}\t\t{u}")
open(os.path.join(out, "log.tsv"), "a").write("\n".join(log) + "\n")
print("\n".join(log))
