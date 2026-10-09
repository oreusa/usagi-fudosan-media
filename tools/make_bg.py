"""背景「白いシルク」を作る（自前で計算。写真・動画素材は使わない）
  静止画: python3 make_bg.py out.png [seed]
  動画  : python3 make_bg.py out.mp4 [seed] [秒数]
上からゆるく右へ流れる、幅の違う布のひだ。動画ではひだが風でゆっくり揺れる。
明るい白〜うすいグレーで、文字の邪魔をしない濃さに抑える。"""
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
SW, SH = 270, 480  # 動画は1/4で計算して拡大する（ひだはぼかすので見た目は同じ）


def _folds(seed):
    rng = np.random.default_rng(seed)
    return [dict(x0=rng.uniform(-200, W + 100), lean=rng.uniform(0.18, 0.42), bamp=rng.uniform(40, 140),
                 bper=rng.uniform(500, 1100), bph=rng.uniform(0, 6), width=rng.uniform(40, 120),
                 depth=rng.uniform(0.35, 1.0), sway=rng.uniform(25, 60), sper=rng.uniform(5.0, 9.0),
                 sph=rng.uniform(0, 6)) for _ in range(7)]


def _field(folds, t, w, h):
    s = W / w
    y, x = np.mgrid[0:h, 0:w].astype(float) * s
    shade = np.zeros((h, w))
    for f in folds:
        sway = f["sway"] * np.sin(2 * np.pi * t / f["sper"] + f["sph"] + y / 900)  # 下ほど遅れて揺れる
        cx = f["x0"] + f["lean"] * y + f["bamp"] * np.sin(y / f["bper"] + f["bph"] + 0.25 * t) + sway
        d = (x - cx) / f["width"]
        shade += f["depth"] * np.exp(-d * d) * (1 + 0.6 * np.tanh(d * 2))
    return shade, x, y


def _color(shade, x, y, norm):
    shade = np.clip(shade / norm, 0, 1)
    glow = np.exp(-(((x - W * 0.35) / (W * 0.9)) ** 2 + ((y - H * 0.35) / (H * 0.8)) ** 2))
    val = 251 - 30 * shade ** 1.3 + 4 * glow
    return np.clip(np.dstack([val - 1.5, val - 0.6, val + 0.8]), 0, 255).astype(np.uint8)


def make_still(path, seed=7):
    folds = _folds(seed)
    shade, x, y = _field(folds, 0.0, W, H)
    Image.fromarray(_color(shade, x, y, shade.max())).filter(ImageFilter.GaussianBlur(22)).save(path)


def make_video(path, seed=7, seconds=13.0, fps=30):
    folds = _folds(seed)
    norm = max(_field(folds, t, SW, SH)[0].max() for t in np.linspace(0, 9, 10))  # 明るさが時間で揺れないよう固定
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}",
                          "-r", str(fps), "-i", "-", "-vf", f"scale={W}:{H}:flags=bicubic,gblur=sigma=6",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", path],
                         stdin=subprocess.PIPE)
    for k in range(int(round(seconds * fps))):
        shade, x, y = _field(folds, k / fps, SW, SH)
        img = Image.fromarray(_color(shade, x, y, norm)).filter(ImageFilter.GaussianBlur(5))
        p.stdin.write(img.tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    out = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    if out.endswith(".mp4"):
        make_video(out, seed, float(sys.argv[3]) if len(sys.argv) > 3 else 13.0)
    else:
        make_still(out, seed)
