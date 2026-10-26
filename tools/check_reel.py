#!/usr/bin/env python3
"""リールを予約する前の確認（10/26〜。10/24〜26 のリールが無音で出たため）。

使い方: python3 tools/check_reel.py media/2026-10-27/ig.json [...]
ig.json の video（URL）を media/ の手元ファイルに読み替えて、次を確かめる。
  - 動画ファイルがある
  - 音声トラックがあり、音が鳴っている（平均音量が -60dB より大きい。曲つきは約 -43dB、無音は -91dB）
  - 長さが 10 秒以上
  - images が 5 枚あり、ファイルがある
すべて OK なら「OK」、ひとつでもだめなら「NG …」と出して終了コード 1。
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def local(url):
    m = re.search(r"/(media/.+)$", url or "")
    return os.path.join(ROOT, m.group(1)) if m else None


def probe(path):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout.strip() or 0)
    aud = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    vol = None
    if aud:
        err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        m = re.search(r"mean_volume: (-?[\d.]+) dB", err)
        vol = float(m.group(1)) if m else None
    return dur, aud, vol


def check(ig_path):
    ig = json.load(open(ig_path))
    ng = []
    v = local(ig.get("video"))
    if not v or not os.path.exists(v):
        ng.append(f"動画が無い: {ig.get('video')}")
    else:
        dur, aud, vol = probe(v)
        if not aud:
            ng.append("音声トラックが無い")
        elif vol is None or vol < -60:
            ng.append(f"無音（平均 {vol} dB）")
        if dur < 10:
            ng.append(f"短すぎる（{dur:.1f} 秒）")
    imgs = ig.get("images") or []
    if len(imgs) != 5:
        ng.append(f"images が {len(imgs)} 枚")
    for u in imgs:
        p = local(u)
        if not p or not os.path.exists(p):
            ng.append(f"画像が無い: {u}")
    return ng


def main():
    bad = 0
    for p in sys.argv[1:]:
        ng = check(p)
        print(("OK  " if not ng else "NG  ") + p + ("" if not ng else "  " + " / ".join(ng)))
        bad += bool(ng)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
