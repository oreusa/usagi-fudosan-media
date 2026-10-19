"""うさぎちゃん不動産 リールジェネレーター v4（10/17 オーナー決定のノート風デザイン）

HTML と CSS で1枚ずつ組み、Chromium で2倍の解像度に写してから縮小する（v3 と同じ仕組み）。
デザインの決まり（10/17 オーナーが見本と色 A を選んだもの）：
  ・方眼ノートの紙＋上下にベージュの帯。色は A（ベージュ×ブラウン）。背景に粒（ノイズ）は入れない（インスタの再圧縮で崩れるため）
  ・表紙：角を斜めに切った白いカード。ロゴはカードの右下だけ（上には入れない）
  ・2枚目から：上に小さいロゴ＋英字の名前、クリップ付きのカード「01 ◯◯」、チェックの箇条書き、ピンクのヒント枠
  ・ロゴは tools/brand/logo.png をそのままの色で使う（色を変えない）
  ・字体は Zen Kaku Gothic New、英字と番号は Jost。リールの操作ボタンが重なるので、下420px・右の端は空ける
  ・文中の [[ ]] は帯の色の下線、{{ }} はピンクの下線
使い方: python3 make_reel4.py <spec.json> <outdir>
spec の形は tools/specs4/ を参照（cover → item を3〜4枚 → save）
"""
import html, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
ACC, BAND, TIP, LINE, INK, GRID, HL, SUB = "#A07E66", "#EEE5DA", "#F5E6DE", "#D6A99A", "#3A2F28", "#EFE8E0", "#E9D3BE", "#857A70"
FONT = os.path.join(HERE, "fonts")
LOGO = os.path.join(HERE, "brand", "logo.png")
BGM = {"file": os.path.join(HERE, "sound", "bgm", "303PM.mp3"), "credit": "曲：3:03 PM／しゃろう"}  # 10/19 夜オーナー決定「前の曲・音量8%」。曲ファイルは gitignore なので /mnt/project-files/bgm/303PM.mp3 から tools/sound/bgm/ へコピーして使う

CSS = f"""
@font-face {{ font-family: G; src: url("file://{FONT}/ZenKakuGothicNew-Medium.ttf"); font-weight: 500; }}
@font-face {{ font-family: G; src: url("file://{FONT}/ZenKakuGothicNew-Bold.ttf"); font-weight: 700; }}
@font-face {{ font-family: G; src: url("file://{FONT}/ZenKakuGothicNew-Black.ttf"); font-weight: 900; }}
@font-face {{ font-family: J; src: url("file://{FONT}/Jost-VF.ttf"); font-weight: 100 900; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; background: {BAND}; font-family: G; color: {INK}; position: relative; overflow: hidden;
        font-feature-settings: "palt"; line-break: strict; word-break: keep-all; overflow-wrap: anywhere; -webkit-font-smoothing: antialiased; }}
.paper {{ position: absolute; left: 0; right: 0; top: 250px; height: 1300px; background-color: #fff;
          background-image: linear-gradient({GRID} 2px, transparent 2px), linear-gradient(90deg, {GRID} 2px, transparent 2px);
          background-size: 46px 46px; background-position: -2px -2px; }}
.holes {{ position: absolute; left: 30px; top: 310px; display: flex; flex-direction: column; gap: 58px; }}
.holes i {{ display: block; width: 30px; height: 30px; border-radius: 50%; background: #FBFAF8; border: 2px solid {GRID}; }}
.brand {{ position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-family: J; font-size: 30px; font-weight: 500;
          letter-spacing: .3em; color: {ACC}; }}
.brand img {{ height: 84px; vertical-align: middle; margin-right: 18px; }}
.page {{ position: absolute; right: 150px; top: 190px; font-family: J; font-size: 30px; color: {ACC}; letter-spacing: .1em; }}
.next {{ position: absolute; right: 150px; top: 1572px; font-family: J; font-weight: 300; font-size: 58px; color: {ACC}; }}
.next span {{ display: inline-block; width: 70px; height: 2px; background: {ACC}; vertical-align: middle; margin-left: 14px; position: relative; }}
.next span:after {{ content: ""; position: absolute; right: 0; top: -8px; width: 16px; height: 2px; background: {ACC};
                    transform: rotate(35deg); transform-origin: right; }}
.hl {{ background: linear-gradient(transparent 62%, {HL} 62%); }}
.pk {{ background: linear-gradient(transparent 62%, #F1D5CD 62%); }}
.plabel {{ position: absolute; left: 0; right: 0; top: 262px; text-align: center; }}
.plabel span {{ display: inline-block; border: 3px solid {ACC}; color: {ACC}; font-size: 34px; font-weight: 700; padding: 6px 28px;
               letter-spacing: .1em; background: #fff; }}
/* 表紙 */
.cv {{ position: absolute; left: 110px; right: 110px; top: 420px; height: 1000px; background: #fff;
       clip-path: polygon(0 0, calc(100% - 140px) 0, 100% 140px, 100% 100%, 140px 100%, 0 calc(100% - 140px)); }}
.cvin {{ position: absolute; left: 150px; right: 150px; top: 420px; height: 1000px; display: flex; flex-direction: column;
         align-items: center; justify-content: center; text-align: center; }}
.cv-b {{ display: inline-block; background: {ACC}; color: #fff; font-size: 46px; font-weight: 700; padding: 12px 36px;
         letter-spacing: .1em; margin-bottom: 44px; }}
.cv-k {{ font-size: 48px; font-weight: 700; letter-spacing: .08em; }}
.cv-t {{ font-size: 108px; font-weight: 900; letter-spacing: .06em; line-height: 1.3; margin-top: 40px; }}
.cv-c {{ margin-top: 36px; font-size: 60px; font-weight: 700; letter-spacing: .06em; }}
.cv-c b {{ font-family: J; font-weight: 500; font-size: 170px; color: {ACC}; }}
.cv-s {{ margin-top: 26px; font-size: 34px; font-weight: 500; color: {SUB}; letter-spacing: .1em; }}
.cv-logo {{ position: absolute; right: 130px; top: 1250px; height: 150px; }}
/* ポイントの枚 */
.card {{ position: absolute; left: 110px; width: 860px; top: 420px; height: 500px; background: #fff; }}
.card svg {{ position: absolute; inset: 0; }}
.clip {{ position: absolute; left: 50%; top: -62px; transform: translateX(-50%); }}
.cardin {{ position: absolute; left: 110px; width: 860px; top: 420px; height: 500px; text-align: center; padding-top: 80px; }}
.tag {{ display: inline-block; background: {ACC}; color: #fff; font-size: 54px; font-weight: 700; padding: 14px 40px; letter-spacing: .06em; }}
.tag .n {{ font-family: J; font-weight: 300; font-size: 64px; margin-right: 18px; letter-spacing: 0; }}
.desc {{ text-align: left; padding: 0 70px; margin-top: 40px; font-size: 42px; font-weight: 700; line-height: 2.0; letter-spacing: .06em; }}
.mid {{ position: absolute; left: 150px; right: 150px; top: 980px; text-align: center; }}
.h {{ position: relative; display: inline-block; font-size: 56px; font-weight: 700; letter-spacing: .12em; }}
.checks {{ margin-top: 50px; display: flex; flex-direction: column; gap: 34px; text-align: left; }}
.ck {{ display: flex; gap: 22px; align-items: center; font-size: 42px; font-weight: 700; letter-spacing: .05em; }}
.ck b {{ flex: none; width: 38px; height: 38px; background: {TIP}; position: relative; }}
.ck b:after {{ content: ""; position: absolute; left: 8px; top: 2px; width: 12px; height: 24px; border: solid {ACC};
               border-width: 0 5px 5px 0; transform: rotate(45deg); }}
.tip {{ position: absolute; left: 150px; right: 150px; top: 1320px; background: {TIP}; padding: 40px 50px; display: flex; gap: 30px;
        align-items: center; font-size: 40px; font-weight: 700; line-height: 1.8; letter-spacing: .06em; }}
/* 最後の枚 */
.sv {{ position: absolute; left: 150px; right: 150px; top: 430px; }}
.sv h2 {{ font-size: 76px; font-weight: 900; line-height: 1.45; letter-spacing: .06em; }}
.sv .body {{ margin-top: 50px; font-size: 44px; font-weight: 700; line-height: 1.9; letter-spacing: .05em; }}
.sv .cta {{ margin-top: 60px; background: #fff; border: 3px solid {ACC}; padding: 40px 46px; }}
.sv .cta .l1 {{ font-size: 38px; font-weight: 500; line-height: 1.6; }}
.sv .cta .l2 {{ font-size: 50px; font-weight: 900; color: {ACC}; margin-top: 10px; letter-spacing: .04em; }}
.sv .src {{ margin-top: 40px; font-size: 28px; font-weight: 500; color: {SUB}; line-height: 1.6; }}
"""

CLIP = (f'<svg class="clip" width="130" height="90" viewBox="0 0 130 90"><rect x="0" y="52" width="130" height="34" rx="16" fill="{ACC}"/>'
        f'<circle cx="65" cy="30" r="27" fill="{ACC}"/><circle cx="65" cy="30" r="9" fill="#fff"/></svg>')
FRAME = (f'<svg width="860" height="500"><polygon points="1.5,1.5 858.5,1.5 858.5,446 806,498.5 1.5,498.5" fill="none" '
         f'stroke="{ACC}" stroke-width="3"/></svg>')
BULB = (f'<svg width="80" height="110" viewBox="0 0 80 110" style="flex:none"><g stroke="{ACC}" stroke-width="4" fill="none" stroke-linecap="round">'
        f'<line x1="40" y1="4" x2="40" y2="16" stroke="{LINE}"/><line x1="10" y1="12" x2="17" y2="22"/><line x1="70" y1="12" x2="63" y2="22"/>'
        f'<path d="M22 52a18 18 0 1 1 36 0c0 9-8 13-9 22H31c-1-9-9-13-9-22z" stroke="{LINE}"/><line x1="31" y1="84" x2="49" y2="84"/>'
        f'<line x1="33" y1="94" x2="47" y2="94"/></g></svg>')
PEN = (f'<svg width="70" height="120" viewBox="0 0 70 120" style="position:absolute;right:-80px;top:-50px"><g stroke="{ACC}" '
       f'stroke-width="3.5" fill="none" stroke-linecap="round"><path d="M40 20 L14 100 L12 114 L22 104 L48 24 Z"/>'
       f'<line x1="50" y1="2" x2="47" y2="12"/><line x1="60" y1="8" x2="54" y2="16"/><line x1="66" y1="20" x2="57" y2="23"/></g></svg>')
SCRIB = (f'<svg width="360" height="34" viewBox="0 0 360 34" style="position:absolute;left:50%;transform:translateX(-50%);bottom:-34px">'
         f'<path d="M6 24 C60 10 120 12 170 16 S280 8 350 12 M20 28 C90 20 200 26 330 20" stroke="{LINE}" stroke-width="4" '
         f'fill="none" stroke-linecap="round"/></svg>')

_BUDOUX = None


def tx(s):
    """改行（\\n）と文節の切れ目（BudouX）だけで行を割る。[[ ]] と {{ }} は下線（改行をまたいでもよい）"""
    global _BUDOUX
    if _BUDOUX is None:
        import budoux
        _BUDOUX = budoux.load_default_japanese_parser()

    def plain(t):
        return "<br>".join("<wbr>".join(html.escape(c) for c in _BUDOUX.parse(l)) if l else "" for l in t.split("\n"))
    h = ""
    for p in re.split(r"(\[\[.*?\]\]|\{\{.*?\}\})", str(s or ""), flags=re.S):
        if p.startswith("[[") and p.endswith("]]"):
            h += f'<span class="hl">{plain(p[2:-2])}</span>'
        elif p.startswith("{{") and p.endswith("}}"):
            h += f'<span class="pk">{plain(p[2:-2])}</span>'
        elif p:
            h += plain(p)
    return h


def slide_html(spec, s, i, n, credit):
    logo = f"file://{LOGO}"
    t = s["type"]
    if t == "cover":
        body = (f'<div class="brand">USAGI-CHAN REAL ESTATE</div><div class="cv"></div><div class="cvin">'
                + (f'<div class="cv-b">{tx(s["badge"])}</div>' if s.get("badge") else "")
                + f'<div class="cv-k">{tx(s.get("kicker"))}</div><div class="cv-t">{tx(s["title"])}</div>'
                + (f'<div class="cv-c"><b>{html.escape(str(s["count"]))}</b>{tx(s.get("count_text", "つのポイント"))}</div>' if s.get("count") else "")
                + ("" if s.get("badge") else f'<div class="cv-s">{tx(spec.get("series"))}</div>') + '</div>'
                + f'<img class="cv-logo" src="{logo}">')
    else:
        holes = '<div class="holes">' + "<i></i>" * 14 + "</div>"
        body = (f'<div class="paper"></div>{holes}<div class="brand"><img src="{logo}">USAGI-CHAN REAL ESTATE</div>')
        if spec.get("page_label"):
            body += f'<div class="plabel"><span>{tx(spec["page_label"])}</span></div>'
        if t == "item":
            checks = "".join(f'<div class="ck"><b></b><span>{tx(c)}</span></div>' for c in s.get("checks", []))
            body += (f'<div class="card">{FRAME}</div><div class="cardin">{CLIP}<span class="tag"><span class="n">{html.escape(s["n"])}</span>'
                     f'{tx(s["title"])}</span><div class="desc">{tx(s["desc"])}</div></div>'
                     f'<div class="mid"><span class="h">{tx(s.get("check_head", "チェック"))}{PEN}{SCRIB}</span>'
                     f'<div class="checks">{checks}</div></div>'
                     + (f'<div class="tip">{BULB}<div>{tx(s["tip"])}</div></div>' if s.get("tip") else ""))
        elif t == "save":
            src = (("出典：" + tx(spec["source"])) if spec.get("source") else "") + (("<br>" if spec.get("source") else "") + html.escape(credit) if credit else "")  # 自社の案内など出典がない回は「出典：」を出さない
            body += (f'<div class="sv"><h2>{tx(s["head"])}</h2><div class="body">{tx(s.get("body"))}</div>'
                     f'<div class="cta"><div class="l1">{tx(s.get("bridge", "売るか決めていない段階でも大丈夫です"))}</div>'
                     f'<div class="l2">{tx(s.get("cta", "相談はプロフィールから"))}</div></div><div class="src">{src}</div></div>')
        else:
            raise ValueError(t)
    nxt = '<div class="next">Next<span></span></div>' if i < n - 1 else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}{nxt}</body></html>'


def render(spec, outdir, credit):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    n = len(spec["slides"])
    paths = []
    with sync_playwright() as p:
        exe = os.environ.get("REEL_CHROMIUM", "/opt/pw-browsers/chromium")
        b = p.chromium.launch(**({"executable_path": exe} if os.path.exists(exe) else {}))
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
        for i, s in enumerate(spec["slides"]):
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                f.write(slide_html(spec, s, i, n, credit))
            pg.goto("file://" + f.name)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(200)
            big = os.path.join(outdir, f"_{i}.png")
            pg.screenshot(path=big)
            out = os.path.join(outdir, f"{spec['name']}-{i + 1}.jpg")
            Image.open(big).convert("RGB").resize((W, H), Image.LANCZOS).save(out, quality=95)
            os.remove(big)
            os.unlink(f.name)
            paths.append(out)
        b.close()
    return paths


def main(spec_path, outdir, images_only=False):
    spec = json.load(open(spec_path, encoding="utf-8"))
    # 公開する jpg（X・Threads の画像投稿に使う）には曲名を入れない（10/17 オーナー「音楽名まで入ってて変」）。
    # 曲名入りの絵は動画のためだけに一時フォルダで作る
    pub = render(spec, outdir, "")
    if images_only:
        print("\n".join(pub))
        return
    credit = BGM["credit"] if os.path.exists(BGM["file"]) else ""
    tmp = tempfile.mkdtemp()
    paths = render(spec, tmp, credit)
    n = len(paths)
    dur, fade = spec.get("seconds_per_slide", 4.0), 0.4
    total = dur * n - fade * (n - 1)
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for pth in paths:
        args += ["-loop", "1", "-framerate", "30", "-t", f"{dur:.2f}", "-i", pth]
    if credit:
        args += ["-stream_loop", "-1", "-i", BGM["file"]]
    else:
        args += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        print("注意：曲ファイルが無いので無音で作った（tools/sound/bgm/）", file=sys.stderr)
    fc, prev = [], "[0:v]"
    for k in range(1, n):
        off = k * (dur - fade)
        fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={fade}:offset={off:.2f}[x{k}]")
        prev = f"[x{k}]"
    fc.append(f"{prev}format=yuv420p[vout]")
    fc.append(f"[{n}:a]atrim=0:{total:.2f},volume=-21.9dB,afade=t=in:d=0.3,afade=t=out:st={total - 1.2:.2f}:d=1.2[aout]")
    mp4 = os.path.join(outdir, f"{spec['name']}.mp4")
    # 画面がほぼ動かないので、高めの画質でも 10MB 前後に収まる。インスタは投稿時にもう一度圧縮する
    args += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}",
             "-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-crf", "14", "-maxrate", "12M", "-bufsize", "24M",
             "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", mp4]
    subprocess.run(args, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n".join(pub + [mp4]))


if __name__ == "__main__":
    # 使い方：make_reel4.py spec.json outdir [--images-only]（--images-only は jpg だけ作り直し、動画は触らない）
    main(sys.argv[1], sys.argv[2], "--images-only" in sys.argv[3:])
