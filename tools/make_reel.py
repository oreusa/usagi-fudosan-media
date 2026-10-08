"""うさぎちゃん不動産 リール見本ジェネレーター（1080x1920 / Pillow + ffmpeg）
使い方: python3 make_reel.py <spec.json> <outdir>
spec: {"name":..., "field":"sell|money|home", "series":..., "slides":[{...}], "source":...}
"""
import json, sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
M = 96               # 端からの余白（80px以上）
SAFE_TR = 150        # 右上の空ける四方
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_BL = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
FIELDS = {
    "sell":  {"main": (139, 94, 60),  "bg": (247, 240, 232), "soft": (234, 220, 204), "label": "売却・相場"},
    "money": {"main": (214, 112, 132), "bg": (252, 241, 243), "soft": (246, 214, 221), "label": "お金の制度"},
    "home":  {"main": (95, 135, 90),  "bg": (240, 245, 238), "soft": (214, 228, 210), "label": "住まい"},
}
INK = (40, 34, 30)
SUB = (110, 100, 92)

def f(path, size): return ImageFont.truetype(path, size, index=0)

def wrap(draw, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if draw.textlength(line + ch, font=font) > maxw and line and ch not in "、。，．％%）」』！？ー":
                out.append(line); line = ch
            else:
                line += ch
        out.append(line)
    return out

def bunny(draw, x, y, s, col):
    """オリジナルの図形マーク：丸い顔と2本の耳（既存キャラクターに似せない単純な形）"""
    ew, eh = int(s * 0.26), int(s * 0.62)
    draw.rounded_rectangle([x + int(s*0.18), y, x + int(s*0.18) + ew, y + eh], radius=ew // 2, fill=col)
    draw.rounded_rectangle([x + int(s*0.56), y + int(s*0.06), x + int(s*0.56) + ew, y + int(s*0.06) + eh], radius=ew // 2, fill=col)
    draw.ellipse([x, y + int(s*0.42), x + s, y + int(s*0.42) + int(s*0.86)], fill=col)
    e = max(4, s // 14)
    cy = y + int(s*0.42) + int(s*0.40)
    draw.ellipse([x + int(s*0.30) - e, cy - e, x + int(s*0.30) + e, cy + e], fill=(255, 255, 255))
    draw.ellipse([x + int(s*0.70) - e, cy - e, x + int(s*0.70) + e, cy + e], fill=(255, 255, 255))

def frame(spec, i, n):
    fld = FIELDS[spec["field"]]
    im = Image.new("RGB", (W, H), fld["bg"])
    d = ImageDraw.Draw(im)
    # 上の帯（シリーズ名）— 右上150pxは空ける
    d.rectangle([0, 0, W, 300], fill=fld["main"])
    d.rectangle([W - SAFE_TR, 0, W, SAFE_TR], fill=fld["main"])
    d.text((M, 150), spec["series"], font=f(FONT_B, 46), fill=(255, 255, 255), anchor="lm")
    # ページ番号（右下側）
    d.text((M, 236), fld["label"] + "　｜　関西　｜　" + f"{i+1}/{n}", font=f(FONT_R, 34), fill=(255, 255, 255), anchor="lm")
    # 下：マークと名前
    bunny(d, M, H - 470, 110, fld["main"])
    d.text((M + 140, H - 380), "うさぎちゃん不動産", font=f(FONT_B, 40), fill=INK, anchor="lm")
    return im, d, fld

def body(d, spec, s, fld, y):
    maxw = W - 2 * M
    if s["type"] == "cover":
        d.text((M, y), s.get("kicker", ""), font=f(FONT_B, 50), fill=fld["main"]); y += 120
        for line in s["title"].split("\n"):
            d.text((M, y), line, font=f(FONT_BL, 118), fill=INK); y += 165
        y += 30
        d.rectangle([M, y, M + 180, y + 14], fill=fld["main"]); y += 80
        for line in wrap(d, s.get("sub", ""), f(FONT_R, 50), maxw):
            d.text((M, y), line, font=f(FONT_R, 50), fill=SUB); y += 76
    elif s["type"] == "bars":
        d.text((M, y), s["head"], font=f(FONT_BL, 80), fill=INK); y += 130
        d.text((M, y), s.get("note", ""), font=f(FONT_R, 40), fill=SUB); y += 120
        vmax = max(r["v"] for r in s["rows"])
        for r in s["rows"]:
            d.text((M, y), r["label"], font=f(FONT_B, 52), fill=INK)
            d.text((W - M, y - 6), r["vtext"], font=f(FONT_BL, 64), fill=INK, anchor="ra")
            by = y + 92
            bw = int(maxw * r["v"] / vmax)
            d.rounded_rectangle([M, by, M + maxw, by + 40], radius=20, fill=fld["soft"])
            d.rounded_rectangle([M, by, M + bw, by + 40], radius=20, fill=fld["main"])
            y += 200
    elif s["type"] == "points":
        d.text((M, y), s["head"], font=f(FONT_BL, 88), fill=INK); y += 170
        for p in s["items"]:
            d.ellipse([M, y + 24, M + 34, y + 58], fill=fld["main"])
            for ln in wrap(d, p, f(FONT_B, 60), maxw - 64):
                d.text((M + 64, y), ln, font=f(FONT_B, 60), fill=INK); y += 88
            y += 56
    elif s["type"] == "save":
        for line in s["head"].split("\n"):
            d.text((M, y), line, font=f(FONT_BL, 96), fill=INK); y += 140
        y += 50
        for ln in wrap(d, s.get("body", ""), f(FONT_B, 54), maxw):
            d.text((M, y), ln, font=f(FONT_B, 54), fill=INK); y += 82
        y += 60
        src = wrap(d, spec["source"], f(FONT_R, 36), maxw - 80)
        hbox = 120 + len(src) * 54
        d.rounded_rectangle([M, y, W - M, y + hbox], radius=28, fill=fld["soft"])
        yy = y + 40
        d.text((M + 40, yy), "出典", font=f(FONT_B, 38), fill=fld["main"]); yy += 64
        for ln in src:
            d.text((M + 40, yy), ln, font=f(FONT_R, 36), fill=SUB); yy += 54
        y += hbox
    return y

def draw_slide(spec, s, i, n):
    im, d, fld = frame(spec, i, n)
    top, bottom = 380, H - 520
    scratch = ImageDraw.Draw(Image.new("RGB", (W, H)))
    h = body(scratch, spec, s, fld, 0)
    y0 = top + max(0, (bottom - top - h) // 2)
    body(d, spec, s, fld, y0)
    return im

def main(spec_path, outdir):
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    n = len(spec["slides"])
    paths = []
    for i, s in enumerate(spec["slides"]):
        im = draw_slide(spec, s, i, n)
        p = os.path.join(outdir, f"{spec['name']}-{i+1}.jpg")
        im.save(p, quality=90); paths.append(p)
    dur, fade = spec.get("seconds_per_slide", 3.2), 0.4
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for p in paths:
        args += ["-loop", "1", "-t", str(dur), "-i", p]
    args += ["-f", "lavfi", "-t", str(dur * n - fade * (n - 1)), "-i", "anullsrc=r=44100:cl=stereo"]
    fc, prev = [], "[0:v]"
    for k in range(1, n):
        off = round(k * (dur - fade), 3)
        out = f"[v{k}]"
        fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={fade}:offset={off}{out}")
        prev = out
    fc.append(f"{prev}format=yuv420p,fps=30[vout]")
    mp4 = os.path.join(outdir, f"{spec['name']}.mp4")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n}:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "128k",
             "-shortest", "-movflags", "+faststart", mp4]
    subprocess.run(args, check=True)
    print("\n".join(paths + [mp4]))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
