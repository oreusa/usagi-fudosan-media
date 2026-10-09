"""背景「白いシルク」を作る（自前で計算。写真素材は使わない）
使い方: python3 make_bg.py out.png [seed]
上からゆるく右へ流れる、幅の違う布のひだ。明るい白〜うすいグレーで、文字の邪魔をしない濃さに抑える。"""
import sys
import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920


def make(path, seed=7):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    shade = np.zeros((H, W))
    for _ in range(7):  # ひだを1本ずつ置く（位置・太さ・濃さ・曲がり方はばらばら）
        x0 = rng.uniform(-200, W + 100)
        lean = rng.uniform(0.18, 0.42)          # 下へ行くほど右へ流れる
        bend = rng.uniform(40, 140) * np.sin(y / rng.uniform(500, 1100) + rng.uniform(0, 6))
        cx = x0 + lean * y + bend
        width = rng.uniform(40, 120)
        depth = rng.uniform(0.35, 1.0)
        d = (x - cx) / width
        shade += depth * np.exp(-d * d) * (1 + 0.6 * np.tanh(d * 2))  # 片側がやわらかく残る影
    shade /= shade.max()
    glow = np.exp(-(((x - W * 0.35) / (W * 0.9)) ** 2 + ((y - H * 0.35) / (H * 0.8)) ** 2))
    val = 251 - 30 * shade ** 1.3 + 4 * glow
    rgb = np.dstack([val - 1.5, val - 0.6, val + 0.8])
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22))
    img.save(path)


if __name__ == "__main__":
    make(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 7)
