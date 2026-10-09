"""うさぎちゃん不動産 リールジェネレーター v3（10/09）

HTML と CSS で1枚ずつ組み、Chromium（Playwright）で2倍の解像度に写してから縮小する。
日本語の詰め（palt）・禁則・本物の太字フォントで、文字をくっきりさせるため。
デザインの決まり（燈と相談室で決めたもの）：
  ・背景 #FAF8F5／文字 #222222／強調は深い緑 #1F6F6B を1枚に1か所／注・出典 #6B6B6B
  ・字体は Noto Sans JP だけ（見出し Bold、本文 Medium、大きい数字 Black）。数字も同じ字体
  ・大きさは4段：大きい数字／見出し／本文／注
  ・見出しは全部の枚で同じ高さ（上から470px）。そろえは全枚左。改行は文節の切れ目だけ（BudouX）
  ・キャラクターは入れない。上に小さく名前、右上にページ番号
  ・リールの画面は下と右に操作ボタンが重なるので、下420px・右の端は空けておく
使い方: python3 make_reel3.py <spec.json> <outdir>
"""
import html, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# 字体の組（REEL3_FONT で切り替え）。{太さ: ファイル}。中くらい＝500、太字＝700 以上
FONT_SETS = {
    "noto": {"100 900": "NotoSansJP-VF.ttf"},
    "zenkaku": {"500": "ZenKakuGothicNew-Medium.ttf", "700": "ZenKakuGothicNew-Bold.ttf", "800 900": "ZenKakuGothicNew-Black.ttf"},
    "bizud": {"100 600": "BIZUDPGothic-Regular.ttf", "700 900": "BIZUDPGothic-Bold.ttf"},
    "plex": {"100 600": "IBMPlexSansJP-Medium.ttf", "700 900": "IBMPlexSansJP-Bold.ttf"},
}
FONT_SET = FONT_SETS[os.environ.get("REEL3_FONT", "noto")]
# 太さの組。"iphone" は iPhone の文字（ヒラギノ角ゴ W3/W6）に近い細めの太さ
WEIGHTS = {"std": {"title": 800, "head": 700, "body": 500, "num": 900},
           "iphone": {"title": 650, "head": 600, "body": 400, "num": 700}}[os.environ.get("REEL3_WEIGHT", "std")]
FONT_FACES = "".join(f'@font-face {{ font-family: "NSJP"; src: url("file://{os.path.join(HERE, "fonts", f)}"); font-weight: {w}; }}\n'
                     for w, f in FONT_SET.items())
W, H = 1080, 1920
BG, INK, ACC, SUB, LINE = "#FAF8F5", "#222222", "#1F6F6B", "#6B6B6B", "#E4DFD7"

CSS = f"""
{FONT_FACES}* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {W}px; height: {H}px; background: {BG}; }}
body {{ font-family: "NSJP"; color: {INK}; font-feature-settings: "palt" 1; line-break: strict;
        word-break: keep-all; overflow-wrap: anywhere;
        -webkit-font-smoothing: antialiased; }}
.page {{ position: relative; width: {W}px; height: {H}px; padding: 0 96px; }}
.top {{ position: absolute; left: 96px; right: 96px; top: 150px; display: flex; justify-content: space-between;
        align-items: baseline; font-size: 30px; font-weight: 500; color: {SUB}; letter-spacing: .08em; }}
.top .name {{ color: {INK}; font-weight: 700; letter-spacing: .12em; }}
.series {{ position: absolute; left: 96px; top: 205px; font-size: 30px; font-weight: 500; color: {ACC}; letter-spacing: .04em; }}
.rule-top {{ position: absolute; left: 96px; right: 96px; top: 262px; height: 2px; background: {LINE}; }}
.block {{ position: absolute; left: 96px; right: 96px; top: 470px; bottom: 420px; }}
.kicker {{ font-size: 40px; font-weight: 500; color: {SUB}; letter-spacing: .04em; margin-bottom: 36px; }}
.title {{ font-size: 104px; font-weight: {WEIGHTS['title']}; line-height: 1.28; letter-spacing: .02em; }}
.title em {{ font-style: normal; color: {ACC}; }}
.bar {{ width: 120px; height: 8px; background: {ACC}; margin: 56px 0 48px; border-radius: 4px; }}
.lead {{ font-size: 46px; font-weight: {WEIGHTS['body']}; line-height: 1.6; color: {SUB}; letter-spacing: .04em; }}
h2 {{ font-size: 72px; font-weight: {WEIGHTS['head']}; line-height: 1.3; letter-spacing: .02em; }}
.note {{ font-size: 32px; font-weight: 500; color: {SUB}; line-height: 1.5; margin-top: 20px; }}
.rows {{ margin-top: 56px; border-top: 2px solid {LINE}; }}
.row {{ display: flex; justify-content: space-between; align-items: baseline; padding: 34px 0; border-bottom: 2px solid {LINE}; }}
.row .lab {{ font-size: 48px; font-weight: {WEIGHTS['body']}; letter-spacing: .02em; }}
.row .val {{ font-weight: {WEIGHTS['num']}; color: {INK}; white-space: nowrap; }}
.row .num {{ font-size: 92px; letter-spacing: -.01em; }}
.row .unit {{ font-size: 52px; font-weight: 700; margin-left: 4px; }}
.row.hl .lab {{ font-weight: {WEIGHTS['head']}; }}
.row.hl .val {{ color: {ACC}; }}
.items {{ margin-top: 64px; display: flex; flex-direction: column; gap: 52px; }}
.item {{ display: flex; gap: 32px; align-items: flex-start; }}
.item .no {{ flex: none; width: 64px; height: 64px; border-radius: 50%; border: 3px solid {ACC}; color: {ACC};
             font-size: 34px; font-weight: 700; display: flex; align-items: center; justify-content: center; margin-top: 4px; }}
.item .tx {{ font-size: 52px; font-weight: {WEIGHTS['body']}; line-height: 1.6; letter-spacing: .03em; }}
.item.hl .tx {{ font-weight: {WEIGHTS['head']}; }}
.body {{ font-size: 52px; font-weight: {WEIGHTS['body']}; line-height: 1.6; letter-spacing: .03em; margin-top: 48px; }}
.cta {{ margin-top: 64px; padding: 40px 44px; border-radius: 20px; background: #EEF3F2; }}
.cta .l1 {{ font-size: 44px; font-weight: {WEIGHTS['body']}; line-height: 1.6; }}
.cta .l2 {{ font-size: 52px; font-weight: 700; color: {ACC}; margin-top: 8px; }}
.src {{ position: absolute; left: 96px; right: 200px; bottom: 440px; font-size: 28px; font-weight: 500; color: {SUB}; line-height: 1.55; }}
"""

NUM_RE = re.compile(r"^([0-9０-９,，.．]+)(.*)$")


_BUDOUX = None


def esc(s):
    """文節（BudouX）の切れ目でだけ改行させる。単語の途中で行が割れないように"""
    global _BUDOUX
    if _BUDOUX is None:
        import budoux
        _BUDOUX = budoux.load_default_japanese_parser()
    lines = str(s or "").split("\n")
    return "<br>".join("<wbr>".join(html.escape(c) for c in _BUDOUX.parse(l)) if l else "" for l in lines)


def val_html(v):
    m = NUM_RE.match(str(v))
    if not m:
        return f'<span class="num">{esc(v)}</span>'
    return f'<span class="num">{esc(m.group(1))}</span><span class="unit">{esc(m.group(2))}</span>'


def slide_html(spec, s, i, n):
    head = (f'<div class="top"><span class="name">うさぎちゃん不動産</span><span>{i + 1} / {n}</span></div>'
            f'<div class="series">{esc(spec.get("series", ""))}</div><div class="rule-top"></div>')
    t = s["type"]
    if t == "cover":
        title = esc(s["title"])
        for w in s.get("emph", []):  # 強調語は文節の切れ目（<wbr>）をまたいでも色が付くようにする
            pat = "(?:<wbr>)?".join(re.escape(html.escape(ch)) for ch in w)
            title = re.sub(pat, lambda m: f"<em>{m.group(0)}</em>", title, count=1)
        inner = (f'<div class="kicker">{esc(s.get("kicker"))}</div><div class="title">{title}</div>'
                 f'<div class="bar"></div><div class="lead">{esc(s.get("sub"))}</div>')
    elif t == "bars":
        hl = s.get("hl", len(s["rows"]) - 2 if len(s["rows"]) > 2 else 0)
        rows = "".join(f'<div class="row{" hl" if k == hl else ""}"><span class="lab">{esc(r["label"])}</span>'
                       f'<span class="val">{val_html(r["vtext"])}</span></div>' for k, r in enumerate(s["rows"]))
        inner = f'<h2>{esc(s["head"])}</h2><div class="note">{esc(s.get("note"))}</div><div class="rows">{rows}</div>'
    elif t == "points":
        hl = s.get("hl", 0)
        items = "".join(f'<div class="item{" hl" if k == hl else ""}"><span class="no">{k + 1}</span>'
                        f'<span class="tx">{esc(p)}</span></div>' for k, p in enumerate(s["items"]))
        inner = f'<h2>{esc(s["head"])}</h2><div class="items">{items}</div>'
    elif t == "save":
        cta = s.get("cta", "相談はプロフィールから")
        inner = (f'<h2>{esc(s["head"])}</h2><div class="body">{esc(s.get("body"))}</div>'
                 f'<div class="cta"><div class="l1">{esc(s.get("bridge", "売るか決めていない段階でも大丈夫です"))}</div>'
                 f'<div class="l2">{esc(cta)}</div></div>')
        head += f'<div class="src">出典：{esc(spec.get("source"))}</div>'
    else:
        raise ValueError(t)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="page">{head}<div class="block">{inner}</div></div></body></html>'


def render(spec_path, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    spec = json.load(open(spec_path, encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    n = len(spec["slides"])
    paths = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for i, s in enumerate(spec["slides"]):
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                f.write(slide_html(spec, s, i, n))
            pg.goto("file://" + f.name)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            big = os.path.join(outdir, f"_{i}.png")
            pg.screenshot(path=big)
            os.unlink(f.name)
            out = os.path.join(outdir, f"{spec['name']}-{i + 1}.jpg")
            Image.open(big).convert("RGB").resize((W, H), Image.LANCZOS).save(out, quality=93)
            os.remove(big)
            paths.append(out)
        b.close()
    return spec, paths


def main(spec_path, outdir):
    sys.path.insert(0, HERE)
    import make_reel  # BGM は v2 のものを使う
    spec, paths = render(spec_path, outdir)
    n = len(paths)
    dur, fade = spec.get("seconds_per_slide", 3.6), 0.5
    total = dur * n - fade * (n - 1)
    wav = os.path.join(outdir, f"{spec['name']}-bgm.wav")
    make_reel.make_bgm(wav, total, seed=sum(map(ord, spec["name"])))
    fr = int(round(dur * 30))
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for pth in paths:
        args += ["-i", pth]
    args += ["-i", wav]
    fc = []
    for k in range(n):  # ごくゆっくり寄る（2%）。文字が揺れて見えないよう中心固定
        fc.append(f"[{k}:v]scale=2160:3840,zoompan=z='1+0.02*on/{fr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps=30,setsar=1[z{k}]")
    prev = "[z0]"
    for k in range(1, n):
        out = f"[v{k}]"
        fc.append(f"{prev}[z{k}]xfade=transition=fade:duration={fade}:offset={round(k * (dur - fade), 3)}{out}")
        prev = out
    fc.append(f"{prev}format=yuv420p[vout]")
    mp4 = os.path.join(outdir, f"{spec['name']}.mp4")
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"{n}:a", "-c:v", "libx264", "-preset", "slow",
             "-crf", "18", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", mp4]
    subprocess.run(args, check=True)
    os.remove(wav)
    print("\n".join(paths + [mp4]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
