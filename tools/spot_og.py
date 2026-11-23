"""1件ページ（/o/）を LINE・X などに貼ったときの画像（1200×630）を作る。11/4 オーナー「やって」。
左にそのページの地図（tools/spot_map.py の絵）、右に府県・名前・日程・TOWN NOTE。
links/o/img/<id>.jpg に書き、ページの og:image と twitter:card（大きい画像）を差しかえる。
毎朝 link-stats.yml で odekake_spot.py のあとに動く。python3 tools/spot_og.py"""
import glob, os, re, html, io, shutil, subprocess
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import og_kata

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(D, "tools", "fonts")
# 地図の中の字（明朝・ゴシック・Jost）を cairosvg が使えるように、フォントを入れておく
home_fonts = os.path.expanduser("~/.local/share/fonts")
os.makedirs(home_fonts, exist_ok=True)
for f in ("ShipporiMincho-SemiBold.ttf", "ZenKakuGothicNew-Bold.ttf", "ZenKakuGothicNew-Medium.ttf", "Jost-VF.ttf"):
    if not os.path.exists(os.path.join(home_fonts, f)): shutil.copy(os.path.join(FD, f), home_fonts)
subprocess.run(["fc-cache", "-f"], capture_output=True)

MIN = ImageFont.truetype(os.path.join(FD, "ShipporiMincho-SemiBold.ttf"), 56)
MIN_S = ImageFont.truetype(os.path.join(FD, "ShipporiMincho-SemiBold.ttf"), 46)
GO = ImageFont.truetype(os.path.join(FD, "ZenKakuGothicNew-Bold.ttf"), 30)
GO_S = ImageFont.truetype(os.path.join(FD, "ZenKakuGothicNew-Medium.ttf"), 24)
JO = ImageFont.truetype(os.path.join(FD, "Jost-VF.ttf"), 22)
BASE = "https://kansai.townnote.app"


def wrap(d, text, font, width, lines):
    out, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > width:
            out.append(cur); cur = ch
            if len(out) == lines: break
        else: cur += ch
    if len(out) < lines and cur: out.append(cur)
    if len(out) == lines and "".join(out) != text:
        out[-1] = out[-1][:-1] + "…"
    return out


os.makedirs(os.path.join(D, "links/o/img"), exist_ok=True)
keep = set()
n = 0
for f in sorted(glob.glob(os.path.join(D, "links/o/*.html"))):
    h = open(f, encoding="utf-8").read()
    sid = os.path.basename(f)[:-5]
    m = re.search(r'<div class="tmap">(<svg.*?</svg>)', h, re.S)
    name = html.unescape(re.search(r"<h1>(.*?)<span>", h, re.S).group(1))
    en = re.search(r'<div class="en">([A-Z]+) ─', h).group(1)
    pc = re.search(r'--pc:(#[0-9A-Fa-f]{6})', h).group(1)
    when = re.search(r'<span>日程</span><b>(.*?)</b>', h)
    when = html.unescape(when.group(1)) if when else ""
    where = html.unescape(re.search(r'<p class="sub">(.*?)</p>', h, re.S).group(1))
    # 11/23 HP と同じ今の形（og_kata.py：淡いオーロラ・すりガラス・細い字）
    mp = None
    if m:
        svg = m.group(1)
        vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=660, output_height=round(660 * vb[3] / vb[2]))
        mp = Image.open(io.BytesIO(png)).convert("RGB")
    dot = tuple(int(pc[i:i + 2], 16) for i in (1, 3, 5))
    img = og_kata.spot(FD, mp, f"{en} ・ ODEKAKE", dot, name, when, where, "TOWN NOTE", "関西のおでかけ")
    out = os.path.join(D, "links/o/img", sid + ".jpg")
    img.save(out, quality=84, optimize=True, progressive=True)
    keep.add(sid + ".jpg"); n += 1
    url = f"{BASE}/o/img/{sid}.jpg"
    h = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{url}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">', h, count=1)
    h = h.replace('<meta name="twitter:card" content="summary">', f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{url}">', 1)
    open(f, "w", encoding="utf-8").write(h)
for g in glob.glob(os.path.join(D, "links/o/img/*")):
    if os.path.basename(g) not in keep: os.remove(g)
print(n, "og images")
