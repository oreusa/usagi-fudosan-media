"""リールの 9:16 画像（1080x1920）から、インスタのカルーセル用 4:5 画像（1080x1350）を作る。
インスタのフィードの画像は 4:5 より縦長にできないため、上下の空いた帯を少し落として縮め、左右に帯の色を足す。
使い方: python3 to_feed45.py a-1.jpg a-2.jpg ...  → 同じ場所に a-f1.jpg のように書き出す
"""
import os, re, sys
from PIL import Image

BAND = (0xEE, 0xE5, 0xDA)
TOP, BOTTOM = 110, 1640          # 残す範囲（ブランド名から Next → まで）
OUT_W, OUT_H = 1080, 1350

def convert(path):
    im = Image.open(path).convert("RGB")
    part = im.crop((0, TOP, im.width, BOTTOM))
    s = OUT_H / part.height
    part = part.resize((round(part.width * s), OUT_H), Image.LANCZOS)
    out = Image.new("RGB", (OUT_W, OUT_H), BAND)
    out.paste(part, ((OUT_W - part.width) // 2, 0))
    dst = re.sub(r"-(\d+)\.jpg$", r"-f\1.jpg", path)
    out.save(dst, quality=92)
    return dst

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(convert(p))
